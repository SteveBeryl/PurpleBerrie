import ctypes
import time
import tkinter as tk
from tkinter import ttk

# ---------- Windows API (for monitoring and writing) ----------
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002

def caesar(text: str, shift: int = 1) -> str:
    s = shift % 26
    out = []
    for ch in text:
        code = ord(ch)
        if 65 <= code <= 90: out.append(chr((code - 65 + s) % 26 + 65))
        elif 97 <= code <= 122: out.append(chr((code - 97 + s) % 26 + 97))
        else: out.append(ch)
    return "".join(out)

def set_clipboard_win32(text: str):
    """Fallback write method using Win32."""
    for _ in range(5):
        if not user32.OpenClipboard(None):
            time.sleep(0.1)
            continue
        try:
            user32.EmptyClipboard()
            data = (text + "\0").encode("utf-16-le")
            h = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
            if not h: continue
            ptr = kernel32.GlobalLock(h)
            if not ptr:
                kernel32.GlobalFree(h)
                continue
            ctypes.memmove(ptr, data, len(data))
            kernel32.GlobalUnlock(h)
            if user32.SetClipboardData(CF_UNICODETEXT, h):
                return True
        finally:
            user32.CloseClipboard()
    return False

class CipherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cipher Tool")
        self.root.geometry("600x500")
        self.root.minsize(500, 400)
        
        # Configure styles
        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("Status.TLabel", font=("Segoe UI", 11, "bold"))
        
        self.is_enabled = tk.BooleanVar(value=True)
        
        # --- Top Header ---
        header_frame = tk.Frame(root, bg="#f0f0f0", pady=10)
        header_frame.pack(fill="x")
        
        ttk.Label(header_frame, text="Clipboard Cipher Control", font=("Segoe UI", 14, "bold"), background="#f0f0f0").pack()

        # --- Control Panel ---
        self.control_frame = ttk.Frame(root, padding=15)
        self.control_frame.pack(fill="x")
        
        self.status_label = ttk.Label(
            self.control_frame, 
            text="● MONITORING ACTIVE", 
            foreground="#2d8a2d", # Dark Green
            style="Status.TLabel"
        )
        self.status_label.pack(side="left")
        
        self.toggle_btn = tk.Button(
            self.control_frame, 
            text="PAUSE MONITORING", 
            command=self.toggle_monitoring,
            font=("Segoe UI", 10, "bold"),
            bg="#e1e1e1",
            padx=10,
            pady=5,
            relief="flat",
            activebackground="#cccccc"
        )
        self.toggle_btn.pack(side="right")
        
        # --- Log Container ---
        log_container = ttk.Frame(root, padding=(15, 0, 15, 15))
        log_container.pack(fill="both", expand=True)
        
        ttk.Label(log_container, text="Activity Log", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=5)
        
        # Scrollbar for the log
        scrollbar = ttk.Scrollbar(log_container)
        scrollbar.pack(side="right", fill="y")
        
        self.log_box = tk.Text(
            log_container, 
            height=15, 
            state="disabled", 
            font=("Consolas", 11),
            bg="#ffffff",
            fg="#333333",
            padx=10,
            pady=10,
            relief="solid",
            borderwidth=1,
            yscrollcommand=scrollbar.set
        )
        self.log_box.pack(fill="both", expand=True)
        scrollbar.config(command=self.log_box.yview)
        
        # Tag colors for the log
        self.log_box.tag_configure("info", foreground="#666666")
        self.log_box.tag_configure("success", foreground="#007acc", font=("Consolas", 11, "bold"))
        self.log_box.tag_configure("action", foreground="#2d8a2d")
        self.log_box.tag_configure("error", foreground="#cc0000")
        self.log_box.tag_configure("timestamp", foreground="#999999")

        self.last_seq = user32.GetClipboardSequenceNumber()
        self.ignore_next = False
        
        self.log("Application started. Auto-encryption is active.", "info")
        self.monitor()

    def toggle_monitoring(self):
        if self.is_enabled.get():
            self.is_enabled.set(False)
            self.toggle_btn.config(text="START MONITORING", bg="#d9fdd3") # Light Green background when paused
            self.status_label.config(text="○ MONITORING PAUSED", foreground="#cc0000")
            self.log("Monitoring paused by user.", "error")
        else:
            self.is_enabled.set(True)
            self.toggle_btn.config(text="PAUSE MONITORING", bg="#e1e1e1")
            self.status_label.config(text="● MONITORING ACTIVE", foreground="#2d8a2d")
            self.log("Monitoring resumed.", "info")
            self.last_seq = user32.GetClipboardSequenceNumber()

    def log(self, message, tag="info"):
        self.log_box.config(state="normal")
        timestamp = time.strftime('%H:%M:%S')
        self.log_box.insert("end", f"[{timestamp}] ", "timestamp")
        self.log_box.insert("end", f"{message}\n", tag)
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def monitor(self):
        if self.is_enabled.get():
            curr_seq = user32.GetClipboardSequenceNumber()
            if curr_seq != self.last_seq:
                self.last_seq = curr_seq
                
                if self.ignore_next:
                    self.ignore_next = False
                else:
                    # Brief wait for clipboard stability
                    time.sleep(0.1)
                    
                    content = None
                    for attempt in range(5):
                        try:
                            content = self.root.clipboard_get()
                            break
                        except tk.TclError:
                            time.sleep(0.1)
                    
                    if content:
                        preview = (content[:25] + "..") if len(content) > 25 else content
                        self.log(f"DETECTED: '{preview}'", "success")
                        encrypted = caesar(content, 1)
                        
                        self.ignore_next = True
                        try:
                            self.root.clipboard_clear()
                            self.root.clipboard_append(encrypted)
                            self.root.update() 
                            self.log("ACTION: Encrypted & copied to clipboard.", "action")
                            self.last_seq = user32.GetClipboardSequenceNumber()
                        except tk.TclError:
                            if set_clipboard_win32(encrypted):
                                self.log("ACTION: Encrypted & copied (Win32 mode).", "action")
                                self.last_seq = user32.GetClipboardSequenceNumber()
                            else:
                                self.ignore_next = False
                                self.log("ERROR: Could not write back to clipboard.", "error")
                    else:
                        # Some formats like images trigger a change but have no text
                        pass
        
        self.root.after(200, self.monitor)

if __name__ == "__main__":
    root = tk.Tk()
    app = CipherApp(root)
    root.mainloop()


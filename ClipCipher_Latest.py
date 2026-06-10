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
        self.root.title("ClipCipher V3")
        self.root.geometry("600x520")
        self.root.minsize(500, 450)
        self.root.configure(bg="#ffffff")
        
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#ffffff")
        style.configure("TLabel", background="#ffffff", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#1a1a1a")
        style.configure("Status.TLabel", font=("Segoe UI", 11, "bold"))
        
        self.is_enabled = tk.BooleanVar(value=True)
        
        # --- Top Header ---
        header_frame = tk.Frame(root, bg="#f8f9fa", pady=15, highlightthickness=1, highlightbackground="#e9ecef")
        header_frame.pack(fill="x")
        ttk.Label(header_frame, text="ClipCipher V3", style="Header.TLabel", background="#f8f9fa").pack()

        # --- Control Panel ---
        self.control_panel = tk.Frame(root, bg="#ffffff", padx=20, pady=20)
        self.control_panel.pack(fill="x")
        
        self.status_indicator = tk.Label(
            self.control_panel, 
            text="●", 
            font=("Segoe UI", 14), 
            fg="#28a745", 
            bg="#ffffff"
        )
        self.status_indicator.pack(side="left")
        
        self.status_text = tk.Label(
            self.control_panel, 
            text="MONITORING ACTIVE", 
            font=("Segoe UI", 11, "bold"), 
            fg="#1a1a1a", 
            bg="#ffffff",
            padx=10
        )
        self.status_text.pack(side="left")
        
        self.toggle_btn = tk.Button(
            self.control_panel, 
            text="PAUSE", 
            command=self.toggle_monitoring,
            font=("Segoe UI", 10, "bold"),
            bg="#007bff",
            fg="white",
            padx=20,
            pady=8,
            relief="flat",
            activebackground="#0056b3",
            activeforeground="white",
            cursor="hand2"
        )
        self.toggle_btn.pack(side="right")
        
        # --- Log Container ---
        log_container = tk.Frame(root, bg="#ffffff")
        log_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        log_header = tk.Frame(log_container, bg="#ffffff")
        log_header.pack(fill="x", pady=(0, 10))
        tk.Label(log_header, text="ACTIVITY LOG", font=("Segoe UI", 9, "bold"), fg="#6c757d", bg="#ffffff").pack(side="left")
        
        # Log Box with custom styling
        self.log_box = tk.Text(
            log_container, 
            state="disabled", 
            font=("Consolas", 10),
            bg="#f8f9fa",
            fg="#212529",
            padx=15,
            pady=15,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#dee2e6",
            wrap="word",
            cursor="arrow"
        )
        self.log_box.pack(side="left", fill="both", expand=True)
        
        # Custom scrollbar
        scrollbar = ttk.Scrollbar(log_container, orient="vertical", command=self.log_box.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_box.configure(yscrollcommand=scrollbar.set)
        
        # Tag colors for the log
        self.log_box.tag_configure("info", foreground="#6c757d")
        self.log_box.tag_configure("success", foreground="#007bff", font=("Consolas", 10, "bold"))
        self.log_box.tag_configure("action", foreground="#28a745")
        self.log_box.tag_configure("error", foreground="#dc3545")
        self.log_box.tag_configure("timestamp", foreground="#adb5bd")

        self.last_seq = user32.GetClipboardSequenceNumber()
        self.ignore_next = False
        
        self.log("Ready. Auto-encryption is active.", "info")
        self.monitor()

    def toggle_monitoring(self):
        if self.is_enabled.get():
            self.is_enabled.set(False)
            self.toggle_btn.config(text="RESUME", bg="#28a745", activebackground="#218838")
            self.status_indicator.config(fg="#dc3545")
            self.status_text.config(text="MONITORING PAUSED")
            self.log_box.config(bg="#fff5f5") # Light red background when paused
            self.log("Monitoring paused.", "error")
        else:
            self.is_enabled.set(True)
            self.toggle_btn.config(text="PAUSE", bg="#007bff", activebackground="#0056b3")
            self.status_indicator.config(fg="#28a745")
            self.status_text.config(text="MONITORING ACTIVE")
            self.log_box.config(bg="#f8f9fa")
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
                            self.log("ACTION: Encrypted & copied.", "action")
                            self.last_seq = user32.GetClipboardSequenceNumber()
                        except tk.TclError:
                            if set_clipboard_win32(encrypted):
                                self.log("ACTION: Encrypted (Win32 Fallback).", "action")
                                self.last_seq = user32.GetClipboardSequenceNumber()
                            else:
                                self.ignore_next = False
                                self.log("ERROR: Write failed.", "error")
        
        self.root.after(200, self.monitor)

if __name__ == "__main__":
    root = tk.Tk()
    app = CipherApp(root)
    root.mainloop()

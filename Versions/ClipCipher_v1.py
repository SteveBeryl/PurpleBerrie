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
        self.root.title("Cipher Tool V1")
        self.root.geometry("500x450")
        
        self.is_enabled = tk.BooleanVar(value=True)
        
        # --- Control Panel ---
        self.control_frame = ttk.Frame(root, padding=10)
        self.control_frame.pack(fill="x")
        
        self.status_label = ttk.Label(
            self.control_frame, 
            text="STATUS: MONITORING ACTIVE", 
            foreground="darkgreen", 
            font=("Segoe UI", 10, "bold")
        )
        self.status_label.pack(side="left", padx=5)
        
        self.toggle_btn = ttk.Button(
            self.control_frame, 
            text="DISABLE", 
            command=self.toggle_monitoring
        )
        self.toggle_btn.pack(side="right", padx=5)
        
        # --- Log Box ---
        self.log_box = tk.Text(root, height=15, state="disabled", font=("Consolas", 9))
        self.log_box.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.last_seq = user32.GetClipboardSequenceNumber()
        self.ignore_next = False
        
        self.log("Ready. Auto-encryption is ENABLED.")
        self.monitor()

    def toggle_monitoring(self):
        if self.is_enabled.get():
            self.is_enabled.set(False)
            self.toggle_btn.config(text="ENABLE")
            self.status_label.config(text="STATUS: PAUSED", foreground="red")
            self.log(">>> Monitoring PAUSED.")
        else:
            self.is_enabled.set(True)
            self.toggle_btn.config(text="DISABLE")
            self.status_label.config(text="STATUS: MONITORING ACTIVE", foreground="darkgreen")
            self.log(">>> Monitoring RESUMED.")
            # Update sequence so we don't immediately trigger on old content
            self.last_seq = user32.GetClipboardSequenceNumber()

    def log(self, message):
        self.log_box.config(state="normal")
        self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
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
                    self.log(f"--- Change Detected (Seq {curr_seq}) ---")
                    
                    content = None
                    for attempt in range(5):
                        try:
                            content = self.root.clipboard_get()
                            break
                        except tk.TclError:
                            time.sleep(0.1)
                    
                    if content:
                        self.log(f"   Read: '{content[:20]}...'")
                        encrypted = caesar(content, 1)
                        
                        self.ignore_next = True
                        try:
                            self.root.clipboard_clear()
                            self.root.clipboard_append(encrypted)
                            self.root.update() 
                            self.log("   Action: Encrypted.")
                            self.last_seq = user32.GetClipboardSequenceNumber()
                        except tk.TclError:
                            if set_clipboard_win32(encrypted):
                                self.log("   Action: Encrypted (Win32 Fallback).")
                                self.last_seq = user32.GetClipboardSequenceNumber()
                            else:
                                self.ignore_next = False
                                self.log("   [Fail] Could not write back.")
                    else:
                        self.log("   [Fail] Could not read text.")
        
        self.root.after(200, self.monitor)

if __name__ == "__main__":
    root = tk.Tk()
    app = CipherApp(root)
    root.mainloop()


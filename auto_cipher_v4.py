import ctypes
import ctypes.wintypes as w
import time
import threading
import tkinter as tk
from tkinter import ttk

# ---------- Windows API Setup ----------
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

def get_clipboard_text_resilient():
    """Attempt to read clipboard with retries and better handle management."""
    for _ in range(5): # 5 attempts
        if not user32.OpenClipboard(None):
            time.sleep(0.05)
            continue
        try:
            h = user32.GetClipboardData(CF_UNICODETEXT)
            if not h:
                return None
            
            ptr = kernel32.GlobalLock(h)
            if not ptr:
                # If lock fails, don't try to unlock later
                time.sleep(0.05)
                continue
            
            try:
                return ctypes.wstring_at(ptr)
            finally:
                kernel32.GlobalUnlock(h)
        finally:
            user32.CloseClipboard()
    return None

def set_clipboard_text_resilient(text: str):
    """Attempt to write to clipboard with retries."""
    for _ in range(5):
        if not user32.OpenClipboard(None):
            time.sleep(0.05)
            continue
        try:
            user32.EmptyClipboard()
            data = (text + "\0").encode("utf-16-le")
            h = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
            if not h: return False
            
            ptr = kernel32.GlobalLock(h)
            if not ptr:
                kernel32.GlobalFree(h)
                continue
                
            ctypes.memmove(ptr, data, len(data))
            kernel32.GlobalUnlock(h)
            
            if user32.SetClipboardData(CF_UNICODETEXT, h):
                return True
            else:
                kernel32.GlobalFree(h)
        finally:
            user32.CloseClipboard()
    return False

class CipherV4:
    def __init__(self, root):
        self.root = root
        self.root.title("Cipher V4 (Resilient)")
        self.root.geometry("450x350")
        
        ttk.Label(root, text="Status: Active & Monitoring", foreground="green", font=("Segoe UI", 10, "bold")).pack(pady=10)
        
        self.log_box = tk.Text(root, height=12, state="disabled", font=("Consolas", 9))
        self.log_box.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.last_seq = user32.GetClipboardSequenceNumber()
        self.ignore_next = False
        
        self.log("Ready. Copy text to encrypt.")
        self.monitor()

    def log(self, message):
        self.log_box.config(state="normal")
        self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def monitor(self):
        curr_seq = user32.GetClipboardSequenceNumber()
        if curr_seq != self.last_seq:
            self.last_seq = curr_seq
            
            if self.ignore_next:
                self.ignore_next = False
            else:
                # Give the other app a tiny bit of time to finish its clipboard operation
                time.sleep(0.05) 
                
                content = get_clipboard_text_resilient()
                if content:
                    self.log(f"Detected: {content[:30]}...")
                    encrypted = caesar(content, 1)
                    
                    self.ignore_next = True
                    if set_clipboard_text_resilient(encrypted):
                        self.log(f"Success: -> {encrypted[:30]}...")
                        self.last_seq = user32.GetClipboardSequenceNumber()
                    else:
                        self.ignore_next = False
                        self.log("Error: Could not write result.")
                else:
                    self.log("Note: Clipboard changed but could not be read as text.")
        
        self.root.after(100, self.monitor)

if __name__ == "__main__":
    root = tk.Tk()
    app = CipherV4(root)
    root.mainloop()

import ctypes
import ctypes.wintypes as w
import time
import tkinter as tk
from tkinter import ttk

# ---------- Windows API Setup ----------
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002

def get_last_error():
    return kernel32.GetLastError()

def caesar(text: str, shift: int = 1) -> str:
    s = shift % 26
    out = []
    for ch in text:
        code = ord(ch)
        if 65 <= code <= 90: out.append(chr((code - 65 + s) % 26 + 65))
        elif 97 <= code <= 122: out.append(chr((code - 97 + s) % 26 + 97))
        else: out.append(ch)
    return "".join(out)

def get_clipboard_text():
    if not user32.OpenClipboard(None):
        return f"ERROR_OPEN_{get_last_error()}"
    try:
        h = user32.GetClipboardData(CF_UNICODETEXT)
        if not h:
            return f"ERROR_DATA_{get_last_error()}"
        ptr = kernel32.GlobalLock(h)
        if not ptr:
            return f"ERROR_LOCK_{get_last_error()}"
        try:
            return ctypes.wstring_at(ptr)
        finally:
            kernel32.GlobalUnlock(h)
    finally:
        user32.CloseClipboard()

def set_clipboard_text(text: str):
    if not user32.OpenClipboard(None):
        return False, f"OPEN_{get_last_error()}"
    try:
        user32.EmptyClipboard()
        data = (text + "\0").encode("utf-16-le")
        h = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        if not h: return False, f"ALLOC_{get_last_error()}"
        ptr = kernel32.GlobalLock(h)
        if not ptr: return False, f"LOCK_{get_last_error()}"
        ctypes.memmove(ptr, data, len(data))
        kernel32.GlobalUnlock(h)
        res = user32.SetClipboardData(CF_UNICODETEXT, h)
        return bool(res), f"SET_{get_last_error()}"
    finally:
        user32.CloseClipboard()

class DiagnosticCipher:
    def __init__(self, root):
        self.root = root
        self.root.title("Cipher Diagnostics")
        self.root.geometry("500x400")
        
        ttk.Label(root, text="Diagnostic Mode (High Sensitivity)", foreground="red").pack(pady=5)
        
        self.log_box = tk.Text(root, height=15, state="disabled", font=("Consolas", 9))
        self.log_box.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.last_text = ""
        self.last_seq = user32.GetClipboardSequenceNumber()
        
        self.log(f"Started. Initial Sequence: {self.last_seq}")
        self.check_loop()

    def log(self, message):
        self.log_box.config(state="normal")
        self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def check_loop(self):
        # 1. Check Sequence Number (Lowest level change detection)
        current_seq = user32.GetClipboardSequenceNumber()
        if current_seq != self.last_seq:
            self.log(f"Change Detected! Seq: {self.last_seq} -> {current_seq}")
            self.last_seq = current_seq
            
            content = get_clipboard_text()
            if "ERROR_" in str(content):
                self.log(f"   Read Failed: {content}")
            else:
                self.log(f"   Content: '{content}'")
                if content and not content.endswith(" [ENC]"): # Simple loop prevention
                    enc = caesar(content, 1) + " [ENC]"
                    success, err = set_clipboard_text(enc)
                    if success:
                        self.log(f"   Updated -> '{enc}'")
                        self.last_seq = user32.GetClipboardSequenceNumber() # Update to new seq
                    else:
                        self.log(f"   Write Failed: {err}")
        
        self.root.after(100, self.check_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = DiagnosticCipher(root)
    root.mainloop()

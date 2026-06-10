import ctypes
import ctypes.wintypes as w
import time
import tkinter as tk
from tkinter import ttk

# ---------- Windows API Setup ----------
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

CF_TEXT = 1
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002

def get_last_err():
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

class CipherV6:
    def __init__(self, root):
        self.root = root
        self.root.title("Cipher V6 (Format Analyzer)")
        self.root.geometry("550x450")
        
        ttk.Label(root, text="V6: Analyzing All Clipboard Formats", foreground="blue", font=("Segoe UI", 10, "bold")).pack(pady=5)
        
        self.log_box = tk.Text(root, height=18, state="disabled", font=("Consolas", 9))
        self.log_box.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.last_seq = user32.GetClipboardSequenceNumber()
        self.ignore_next = False
        
        self.log(f"Started. Initial Sequence: {self.last_seq}")
        self.monitor()

    def log(self, message):
        self.log_box.config(state="normal")
        self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def list_formats(self):
        formats = []
        if not user32.OpenClipboard(None):
            return None
        try:
            f = user32.EnumClipboardFormats(0)
            while f != 0:
                formats.append(f)
                f = user32.EnumClipboardFormats(f)
        finally:
            user32.CloseClipboard()
        return formats

    def get_text_aggressive(self):
        """Tries to read text and logs exactly what happens."""
        if not user32.OpenClipboard(None):
            self.log(f"   [Fail] Could not open clipboard (Err {get_last_err()})")
            return None
        
        try:
            # 1. List formats
            fmts = []
            f = user32.EnumClipboardFormats(0)
            while f != 0:
                fmts.append(f)
                f = user32.EnumClipboardFormats(f)
            self.log(f"   Formats available: {fmts}")

            # 2. Prefer Unicode
            target = None
            if CF_UNICODETEXT in fmts: target = CF_UNICODETEXT
            elif CF_TEXT in fmts: target = CF_TEXT
            
            if target is None:
                self.log("   [Fail] No text formats found in list.")
                return None

            h = user32.GetClipboardData(target)
            if not h:
                self.log(f"   [Fail] GetClipboardData({target}) returned null (Err {get_last_err()})")
                return None
            
            ptr = kernel32.GlobalLock(h)
            if not ptr:
                self.log(f"   [Fail] GlobalLock failed (Err {get_last_err()})")
                return None
            
            try:
                if target == CF_UNICODETEXT:
                    return ctypes.wstring_at(ptr)
                else:
                    return ctypes.string_at(ptr).decode('ansi', errors='ignore')
            finally:
                kernel32.GlobalUnlock(h)
        finally:
            user32.CloseClipboard()

    def set_text_resilient(self, text):
        if not user32.OpenClipboard(None): return False
        try:
            user32.EmptyClipboard()
            data = (text + "\0").encode("utf-16-le")
            h = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
            if not h: return False
            ptr = kernel32.GlobalLock(h)
            if not ptr:
                kernel32.GlobalFree(h)
                return False
            ctypes.memmove(ptr, data, len(data))
            kernel32.GlobalUnlock(h)
            return bool(user32.SetClipboardData(CF_UNICODETEXT, h))
        finally:
            user32.CloseClipboard()

    def monitor(self):
        curr_seq = user32.GetClipboardSequenceNumber()
        if curr_seq != self.last_seq:
            self.last_seq = curr_seq
            
            if self.ignore_next:
                self.ignore_next = False
            else:
                self.log(f"--- Change Detected (Seq {curr_seq}) ---")
                time.sleep(0.15) # Brief wait
                
                content = self.get_text_aggressive()
                if content:
                    self.log(f"   Read success: '{content[:15]}...'")
                    encrypted = caesar(content, 1)
                    
                    self.ignore_next = True
                    if self.set_text_resilient(encrypted):
                        self.log(f"   Action: Encrypted and Copied.")
                        self.last_seq = user32.GetClipboardSequenceNumber()
                    else:
                        self.ignore_next = False
                        self.log("   [Fail] Write failed.")
        
        self.root.after(100, self.monitor)

if __name__ == "__main__":
    root = tk.Tk()
    app = CipherV6(root)
    root.mainloop()

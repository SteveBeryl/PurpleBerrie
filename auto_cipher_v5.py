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

class CipherV5:
    def __init__(self, root):
        self.root = root
        self.root.title("Cipher V5 (Deep Diag)")
        self.root.geometry("500x400")
        
        ttk.Label(root, text="V5: Monitoring with Deep Diagnostics", foreground="purple", font=("Segoe UI", 10, "bold")).pack(pady=5)
        
        self.log_box = tk.Text(root, height=15, state="disabled", font=("Consolas", 9))
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

    def get_text_verbose(self):
        """Attempts to read clipboard and logs EVERY step failure."""
        for attempt in range(1, 11): # 10 attempts
            if not user32.OpenClipboard(None):
                if attempt == 10: self.log(f"   [Fail] OpenClipboard error {get_last_err()}")
                time.sleep(0.1)
                continue
            
            try:
                # Check what formats are actually there
                has_uni = user32.IsClipboardFormatAvailable(CF_UNICODETEXT)
                has_txt = user32.IsClipboardFormatAvailable(CF_TEXT)
                
                if not (has_uni or has_txt):
                    if attempt == 10: self.log("   [Fail] No text formats available on clipboard.")
                    return None

                h = user32.GetClipboardData(CF_UNICODETEXT if has_uni else CF_TEXT)
                if not h:
                    if attempt == 10: self.log(f"   [Fail] GetClipboardData null, err {get_last_err()}")
                    return None
                
                ptr = kernel32.GlobalLock(h)
                if not ptr:
                    if attempt == 10: self.log(f"   [Fail] GlobalLock failed, err {get_last_err()}")
                    return None
                
                try:
                    if has_uni:
                        return ctypes.wstring_at(ptr)
                    else:
                        return ctypes.string_at(ptr).decode('ansi', errors='ignore')
                finally:
                    kernel32.GlobalUnlock(h)
            finally:
                user32.CloseClipboard()
                
            break # If we got here without returning, something is wrong, but we opened it
        return None

    def set_text_resilient(self, text):
        for _ in range(5):
            if not user32.OpenClipboard(None):
                time.sleep(0.1)
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

    def monitor(self):
        curr_seq = user32.GetClipboardSequenceNumber()
        if curr_seq != self.last_seq:
            self.last_seq = curr_seq
            
            if self.ignore_next:
                self.ignore_next = False
            else:
                self.log(f"Change Detected (Seq {curr_seq})")
                time.sleep(0.2) # Longer wait for the source app to settle
                
                content = self.get_text_verbose()
                if content:
                    self.log(f"   Read: '{content[:20]}...'")
                    encrypted = caesar(content, 1)
                    
                    self.ignore_next = True
                    if self.set_text_resilient(encrypted):
                        self.log(f"   Encrypted -> '{encrypted[:20]}...'")
                        self.last_seq = user32.GetClipboardSequenceNumber()
                    else:
                        self.ignore_next = False
                        self.log("   [Fail] Could not write back.")
        
        self.root.after(100, self.monitor)

if __name__ == "__main__":
    root = tk.Tk()
    app = CipherV5(root)
    root.mainloop()

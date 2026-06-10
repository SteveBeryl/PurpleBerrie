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

class CipherV7:
    def __init__(self, root):
        self.root = root
        self.root.title("Cipher V7 (Ultra-Resilient)")
        self.root.geometry("550x450")
        
        ttk.Label(root, text="V7: Ultra-Resilient Clipboard Access", foreground="darkgreen", font=("Segoe UI", 10, "bold")).pack(pady=5)
        
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

    def get_text_ultra_resilient(self):
        """Extremely aggressive read strategy with retries and format switching."""
        # 1. Wait for source app to settle (longer wait)
        time.sleep(0.3)
        
        for attempt in range(1, 8): # 7 attempts
            if not user32.OpenClipboard(None):
                time.sleep(0.1 * attempt)
                continue
            
            try:
                # Prioritize Unicode (13) then ANSI (1)
                target = None
                if user32.IsClipboardFormatAvailable(CF_UNICODETEXT): target = CF_UNICODETEXT
                elif user32.IsClipboardFormatAvailable(CF_TEXT): target = CF_TEXT
                
                if target is None:
                    # Maybe it hasn't appeared yet? Retry.
                    time.sleep(0.05)
                    continue

                h = user32.GetClipboardData(target)
                if not h:
                    time.sleep(0.05)
                    continue
                
                ptr = kernel32.GlobalLock(h)
                if not ptr:
                    err = get_last_err()
                    # Err 6 is Invalid Handle - this is what we're fighting
                    if attempt < 7:
                        time.sleep(0.1)
                        continue
                    else:
                        self.log(f"   [Fail] GlobalLock(fmt={target}) failed repeatedly (Err {err})")
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
            
            break
        return None

    def set_text_ultra_resilient(self, text):
        for _ in range(5):
            if not user32.OpenClipboard(None):
                time.sleep(0.1)
                continue
            try:
                user32.EmptyClipboard()
                data = (text + "\0").encode("utf-16-le")
                size = len(data)
                h = kernel32.GlobalAlloc(GMEM_MOVEABLE, size)
                if not h: continue
                
                ptr = kernel32.GlobalLock(h)
                if not ptr:
                    kernel32.GlobalFree(h)
                    continue
                    
                ctypes.memmove(ptr, data, size)
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
                self.log(f"--- Change Detected (Seq {curr_seq}) ---")
                
                content = self.get_text_ultra_resilient()
                if content:
                    self.log(f"   Read success: '{content[:15]}...'")
                    encrypted = caesar(content, 1)
                    
                    self.ignore_next = True
                    if self.set_text_ultra_resilient(encrypted):
                        self.log(f"   Action: Encrypted and Copied.")
                        # Update our last_seq to the one WE just caused
                        self.last_seq = user32.GetClipboardSequenceNumber()
                    else:
                        self.ignore_next = False
                        self.log("   [Fail] Write failed.")
                else:
                    self.log("   [Fail] Could not read text after 7 attempts.")
        
        self.root.after(100, self.monitor)

if __name__ == "__main__":
    root = tk.Tk()
    app = CipherV7(root)
    root.mainloop()

import ctypes
import time
import threading
import tkinter as tk
from tkinter import ttk

# ---------- Caesar cipher ----------
def caesar(text: str, shift: int = 1) -> str:
    s = shift % 26
    out = []
    for ch in text:
        code = ord(ch)
        if 65 <= code <= 90: # A-Z
            out.append(chr((code - 65 + s) % 26 + 65))
        elif 97 <= code <= 122: # a-z
            out.append(chr((code - 97 + s) % 26 + 97))
        else:
            out.append(ch)
    return "".join(out)

# ---------- Windows clipboard helpers ----------
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002

def get_clipboard_text() -> str:
    if not user32.OpenClipboard(None):
        return ""
    try:
        h = user32.GetClipboardData(CF_UNICODETEXT)
        if not h:
            return ""
        ptr = kernel32.GlobalLock(h)
        if not ptr:
            return ""
        try:
            return ctypes.wstring_at(ptr)
        finally:
            kernel32.GlobalUnlock(h)
    finally:
        user32.CloseClipboard()

def set_clipboard_text(text: str) -> bool:
    if not user32.OpenClipboard(None):
        return False
    try:
        user32.EmptyClipboard()
        data = (text + "\0").encode("utf-16-le")
        h = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        if not h:
            return False
        ptr = kernel32.GlobalLock(h)
        if not ptr:
            return False
        ctypes.memmove(ptr, data, len(data))
        kernel32.GlobalUnlock(h)
        return user32.SetClipboardData(CF_UNICODETEXT, h) != 0
    finally:
        user32.CloseClipboard()

class CipherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Always-On Cipher")
        self.root.geometry("400x300")
        
        self.label = ttk.Label(root, text="Status: Running", foreground="green")
        self.label.pack(pady=10)
        
        self.log_label = ttk.Label(root, text="Activity Log:")
        self.log_label.pack(anchor="w", padx=10)
        
        self.log_box = tk.Text(root, height=10, state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.last_seen = get_clipboard_text()
        self.running = True
        
        # Start polling thread
        self.thread = threading.Thread(target=self.poll_clipboard, daemon=True)
        self.thread.start()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def log(self, message):
        self.log_box.config(state="normal")
        self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def poll_clipboard(self):
        while self.running:
            try:
                current = get_clipboard_text()
                # Only encrypt if there's new text AND it wasn't just set by us
                if current and current != self.last_seen:
                    encrypted = caesar(current, 1)
                    if set_clipboard_text(encrypted):
                        self.last_seen = encrypted
                        self.root.after(0, self.log, f"Encrypted: {current} -> {encrypted}")
                    else:
                        self.last_seen = current
                else:
                    self.last_seen = current
            except Exception as e:
                self.root.after(0, self.log, f"Error: {e}")
            
            time.sleep(0.5) # Poll every 0.5s

    def on_close(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CipherGUI(root)
    root.mainloop()

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
WM_CLIPBOARDUPDATE = 0x031D

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

# ---------- Clipboard Helpers ----------
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
        self.root.title("Cipher (Event-Driven)")
        self.root.geometry("450x350")
        
        self.status_label = ttk.Label(root, text="Status: Listening for clipboard changes...", foreground="blue")
        self.status_label.pack(pady=10)
        
        self.log_box = tk.Text(root, height=12, state="disabled", font=("Consolas", 9))
        self.log_box.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.last_text = get_clipboard_text()
        self.ignore_next = False
        
        # We need a window handle (HWND) to register for clipboard events
        # Tkinter's root.winfo_id() gives the HWND on Windows
        self.hwnd = root.winfo_id()
        
        # Register for clipboard updates
        if user32.AddClipboardFormatListener(self.hwnd):
            self.log("System: Registered clipboard listener.")
        else:
            self.log("Error: Failed to register listener.")

        # Bind the clipboard update event (Windows message)
        # Note: Tkinter doesn't natively expose WM_CLIPBOARDUPDATE easily
        # So we'll use a hidden thread to monitor the clipboard with the listener
        # OR we can use a more reliable polling if listeners are tricky in Tk
        # Let's try the listener with a custom message handler if possible, 
        # but for simplicity and reliability, I'll use a high-frequency check
        # combined with the listener logic.
        
        self.poll_active = True
        self.thread = threading.Thread(target=self.event_loop, daemon=True)
        self.thread.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def log(self, message):
        self.log_box.config(state="normal")
        self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def event_loop(self):
        """
        Since catching Win32 messages in Tkinter is complex, we use 
        a high-speed check that only triggers when the clipboard 
        content actually changes.
        """
        while self.poll_active:
            try:
                current = get_clipboard_text()
                
                if current and current != self.last_text:
                    if self.ignore_next:
                        # This was likely the update we just made
                        self.ignore_next = False
                        self.last_text = current
                    else:
                        # Real user copy detected!
                        encrypted = caesar(current, 1)
                        self.root.after(0, self.log, f"Detected: '{current}'")
                        
                        self.ignore_next = True # Don't trigger on our own write
                        if set_clipboard_text(encrypted):
                            self.last_text = encrypted
                            self.root.after(0, self.log, f"Result: '{encrypted}' (copied)")
                        else:
                            self.ignore_next = False
                            self.root.after(0, self.log, "Error: Failed to write to clipboard")
                
                elif not current and self.last_text:
                    self.last_text = ""
                    
            except Exception as e:
                self.root.after(0, self.log, f"Internal Error: {e}")
            
            time.sleep(0.1) # Fast check (10 times per second)

    def on_close(self):
        self.poll_active = False
        user32.RemoveClipboardFormatListener(self.hwnd)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CipherGUI(root)
    root.mainloop()

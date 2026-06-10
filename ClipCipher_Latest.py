import ctypes
# Enable high-DPI awareness
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

import time
import tkinter as tk
from tkinter import ttk
import codecs
import base64
from pynput import keyboard
import threading

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

def rot13(text: str) -> str:
    return codecs.encode(text, 'rot_13')

def atbash(text: str) -> str:
    res = []
    for ch in text:
        if 'a' <= ch <= 'z': res.append(chr(ord('z') - (ord(ch) - ord('a'))))
        elif 'A' <= ch <= 'Z': res.append(chr(ord('Z') - (ord(ch) - ord('A'))))
        else: res.append(ch)
    return "".join(res)

def affine(text: str, a=5, b=8) -> str:
    res = []
    for ch in text:
        if ch.isalpha():
            start = ord('A') if ch.isupper() else ord('a')
            res.append(chr(((a * (ord(ch) - start) + b) % 26) + start))
        else: res.append(ch)
    return "".join(res)

def bacon(text: str) -> str:
    dict_bacon = {
        'A': 'aaaaa', 'B': 'aaaab', 'C': 'aaaba', 'D': 'aaabb', 'E': 'aabaa',
        'F': 'aabab', 'G': 'aabba', 'H': 'aabbb', 'I': 'abaaa', 'J': 'abaab',
        'K': 'ababa', 'L': 'ababb', 'M': 'abbaa', 'N': 'abbab', 'O': 'abbba',
        'P': 'abbbb', 'Q': 'baaaa', 'R': 'baaab', 'S': 'baaba', 'T': 'baabb',
        'U': 'babaa', 'V': 'babab', 'W': 'babba', 'X': 'babbb', 'Y': 'bbaaa', 'Z': 'bbaab'
    }
    res = []
    for ch in text.upper():
        if ch in dict_bacon: res.append(dict_bacon[ch])
        else: res.append(ch)
    return "".join(res)

def beaufort(text: str, key: str = "KEY") -> str:
    res = []
    key = key.upper()
    for i, ch in enumerate(text.upper()):
        if ch.isalpha():
            shift = (ord(key[i % len(key)]) - ord(ch)) % 26
            res.append(chr(shift + ord('A')))
        else: res.append(ch)
    return "".join(res)

def playfair(text: str, key: str = "KEY") -> str:
    # Minimal implementation for example
    return "PlayfairNotImpl"

def base64_enc(text: str) -> str:
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')

def reverse_str(text: str) -> str:
    return text[::-1]

CIPHER_MAP = {
    "Affine": affine,
    "Atbash": atbash,
    "Base64": base64_enc,
    "Beaufort": beaufort,
    "Bacon": bacon,
    "Caesar": caesar,
    "Playfair": playfair,
    "Reverse": reverse_str,
    "ROT13": rot13
}

def set_clipboard_win32(text: str):
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
        self.root.title("PurpleBerrie")
        self.root.iconbitmap("PurpleBerrie.ico")
        self.root.geometry("320x450")
        self.root.resizable(False, False)
        
        # Consistent Font Setup
        self.FONT_MAIN = ("Segoe UI", 11)
        self.FONT_BOLD = ("Segoe UI", 11, "bold")
        self.root.option_add("*Font", self.FONT_MAIN)
        self.root.configure(bg="#f8f7ff")
        
        # Colors
        self.PRIMARY = "#6f42c1"    # Deep Purple
        self.SECONDARY = "#e2d9f3"  # Light Purple
        self.TEXT = "#212529"       # Dark Grey/Black
        self.SUCCESS = "#28a745"    # Green
        self.ERROR = "#dc3545"      # Red
        self.BG_LOG = "#ffffff"     # White

        self.is_enabled = tk.BooleanVar(value=True)
        self.last_seq = user32.GetClipboardSequenceNumber()
        self.ignore_next = False
        
        # --- Aesthetic Header ---
        header = tk.Frame(root, bg=self.PRIMARY, pady=12)
        header.pack(fill="x")
        tk.Label(
            header, text="PurpleBerrie", font=("Segoe UI", 16, "bold"), 
            fg="white", bg=self.PRIMARY
        ).pack()

        # --- Selection Frame ---
        select_frame = tk.Frame(root, bg="#f8f7ff", padx=15, pady=10)
        select_frame.pack(fill="x")
        tk.Label(select_frame, text="Method:", bg="#f8f7ff", font=self.FONT_MAIN).pack(side="left")
        self.method_var = tk.StringVar(value="Affine")
        self.method_dropdown = ttk.Combobox(
            select_frame, textvariable=self.method_var, 
            values=sorted(list(CIPHER_MAP.keys())), state="readonly", font=self.FONT_MAIN
        )
        self.method_dropdown.pack(side="right", fill="x", expand=True)

        # --- Status & Control Card ---
        card = tk.Frame(root, bg="#ffffff", padx=15, pady=15, highlightthickness=1, highlightbackground=self.SECONDARY)
        card.pack(fill="x", padx=15, pady=15)
        
        self.switch_btn = tk.Button(
            card, text="ON", command=self.toggle_monitoring,
            font=self.FONT_BOLD, bg="#55ff55", fg="black",
            width=6, relief="raised", cursor="hand2"
        )
        self.switch_btn.pack(side="right")
        
        self.status_label = tk.Label(
            card, text="ACTIVATED", font=self.FONT_BOLD, 
            fg=self.SUCCESS, bg="#ffffff"
        )
        self.status_label.pack(side="left")
        
        # --- Log Section ---
        log_frame = tk.Frame(root, bg="#f8f7ff", padx=15)
        log_frame.pack(fill="both", expand=True)
        
        tk.Label(log_frame, text="ACTIVITY", font=self.FONT_BOLD, 
                 fg=self.PRIMARY, bg="#f8f7ff").pack(anchor="w", pady=(0, 5))
        
        self.log_box = tk.Text(
            log_frame, state="disabled", font=("Consolas", 10),
            bg=self.BG_LOG, fg=self.TEXT, padx=8, pady=8,
            relief="flat", highlightthickness=1, highlightbackground=self.SECONDARY,
            wrap="word", height=8
        )
        self.log_box.pack(fill="both", expand=True, pady=(0, 15))

        self.log_box.tag_configure("msg", foreground=self.TEXT, font=self.FONT_MAIN)
        self.log_box.tag_configure("highlight", foreground=self.PRIMARY, font=self.FONT_BOLD)
        self.log_box.tag_configure("time", foreground="#9b8bb1", font=self.FONT_MAIN)

        self.log("App ready", "msg")
        
        # Hotkey setup
        self.hotkey_listener = keyboard.GlobalHotKeys({'<ctrl>+<alt>+b': self.toggle_monitoring})
        self.hotkey_listener.start()
        
        self.monitor()

    def toggle_monitoring(self):
        if self.is_enabled.get():
            self.is_enabled.set(False)
            self.switch_btn.config(text="OFF", bg="#ff5555")
            self.status_label.config(text="DEACTIVATED", fg=self.ERROR)
            self.log("Monitoring paused", "msg")
        else:
            self.is_enabled.set(True)
            self.switch_btn.config(text="ON", bg="#55ff55")
            self.status_label.config(text="ACTIVATED", fg=self.SUCCESS)
            self.log("Monitoring resumed", "msg")
            self.last_seq = user32.GetClipboardSequenceNumber()

    def log(self, message, tag="msg"):
        self.log_box.config(state="normal")
        timestamp = time.strftime('%H:%M')
        self.log_box.insert("end", f"{timestamp} ", "time")
        self.log_box.insert("end", f"{message}\n", tag)
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def monitor(self):
        if self.is_enabled.get():
            curr_seq = user32.GetClipboardSequenceNumber()
            if curr_seq != self.last_seq:
                self.last_seq = curr_seq
                if not self.ignore_next:
                    time.sleep(0.1)
                    try:
                        content = self.root.clipboard_get()
                        if content:
                            self.log("Copy detected", "highlight")
                            cipher_func = CIPHER_MAP.get(self.method_var.get(), caesar)
                            encrypted = cipher_func(content)
                            self.ignore_next = True
                            try:
                                self.root.clipboard_clear()
                                self.root.clipboard_append(encrypted)
                                self.root.update()
                                self.log(f"Encrypted ({self.method_var.get()})", "msg")
                                self.last_seq = user32.GetClipboardSequenceNumber()
                            except:
                                if set_clipboard_win32(encrypted):
                                    self.log(f"Encrypted ({self.method_var.get()}) (win32)", "msg")
                                    self.last_seq = user32.GetClipboardSequenceNumber()
                    except tk.TclError:
                        pass
                else:
                    self.ignore_next = False
        self.root.after(200, self.monitor)

if __name__ == "__main__":
    root = tk.Tk()
    app = CipherApp(root)
    root.mainloop()

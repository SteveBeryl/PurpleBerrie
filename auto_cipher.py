import ctypes
import ctypes.wintypes as w
import time
import threading

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

def main():
    print("Auto-Cipher is running... (Shift: 1)")
    print("Every time you copy text, it will be immediately encrypted.")
    
    last_seen = get_clipboard_text()
    
    while True:
        try:
            current = get_clipboard_text()
            if current and current != last_seen:
                # Encrypt
                encrypted = caesar(current, 1)
                # Set back to clipboard
                if set_clipboard_text(encrypted):
                    last_seen = encrypted
                    print(f"Encrypted: {current!r} -> {encrypted!r}")
                else:
                    last_seen = current
            else:
                last_seen = current
        except Exception as e:
            print(f"Error: {e}")
            
        time.sleep(0.3)

if __name__ == "__main__":
    main()

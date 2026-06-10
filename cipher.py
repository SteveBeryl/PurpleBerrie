import sys
import ctypes
import ctypes.wintypes as w


def caesar(text: str, shift: int) -> str:
    s = shift % 26
    out = []
    for ch in text:
        code = ord(ch)
        if 65 <= code <= 90:           # A-Z
            out.append(chr((code - 65 + s) % 26 + 65))
        elif 97 <= code <= 122:        # a-z
            out.append(chr((code - 97 + s) % 26 + 97))
        else:
            out.append(ch)
    return "".join(out)


def get_clipboard_text() -> str:
    CF_UNICODETEXT = 13
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    user32.OpenClipboard.argtypes = [w.HWND]
    user32.OpenClipboard.restype = w.BOOL
    user32.CloseClipboard.argtypes = []
    user32.CloseClipboard.restype = w.BOOL
    user32.GetClipboardData.argtypes = [w.UINT]
    user32.GetClipboardData.restype = w.HANDLE
    user32.EmptyClipboard.argtypes = []
    user32.EmptyClipboard.restype = w.BOOL
    user32.SetClipboardData.argtypes = [w.UINT, w.HANDLE]
    user32.SetClipboardData.restype = w.HANDLE
    kernel32.GlobalLock.argtypes = [w.HGLOBAL]
    kernel32.GlobalLock.restype = w.LPVOID
    kernel32.GlobalUnlock.argtypes = [w.HGLOBAL]
    kernel32.GlobalUnlock.restype = w.BOOL
    kernel32.GlobalAlloc.argtypes = [w.UINT, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = w.HGLOBAL
    kernel32.GlobalFree.argtypes = [w.HGLOBAL]
    kernel32.GlobalFree.restype = w.HGLOBAL

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
    CF_UNICODETEXT = 13
    GMEM_MOVEABLE = 0x0002

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    user32.OpenClipboard.argtypes = [w.HWND]
    user32.OpenClipboard.restype = w.BOOL
    user32.CloseClipboard.argtypes = []
    user32.CloseClipboard.restype = w.BOOL
    user32.EmptyClipboard.argtypes = []
    user32.EmptyClipboard.restype = w.BOOL
    user32.SetClipboardData.argtypes = [w.UINT, w.HANDLE]
    user32.SetClipboardData.restype = w.HANDLE
    kernel32.GlobalAlloc.argtypes = [w.UINT, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = w.HGLOBAL
    kernel32.GlobalLock.argtypes = [w.HGLOBAL]
    kernel32.GlobalLock.restype = w.LPVOID
    kernel32.GlobalUnlock.argtypes = [w.HGLOBAL]
    kernel32.GlobalUnlock.restype = w.BOOL

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


def ask_shift(prompt: str) -> int | None:
    """Popup dialog (InputBox) to ask the user for a shift value."""
    MB_OKCANCEL = 0x1
    IDOK = 1

    ctypes.windll.user32.MessageBoxW.argtypes = [w.HWND, w.LPCWSTR, w.LPCWSTR, w.UINT]
    ctypes.windll.user32.MessageBoxW.restype = w.INT

    # Use PowerShell's InputBox via a tiny script -- simpler than hosting a Win32 form.
    # We use the MSHTML InputBox through VBScript-like approach via PowerShell here.
    import subprocess
    ps = (
        "Add-Type -AssemblyName Microsoft.VisualBasic; "
        f"$r = [Microsoft.VisualBasic.Interaction]::InputBox('{prompt}','Cipher','1'); "
        "Write-Output $r"
    )
    try:
        out = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", ps],
            capture_output=True, text=True, timeout=60
        )
        val = out.stdout.strip()
        if not val:
            return None
        return int(val)
    except Exception:
        return None


def main():
    plaintext = get_clipboard_text()
    if not plaintext:
        ctypes.windll.user32.MessageBoxW(
            None, "Clipboard is empty. Copy some text first.", "Cipher", 0x40
        )
        return

    shift = ask_shift("Enter the Caesar shift (integer, e.g. 1, 3, -2):")
    if shift is None:
        ctypes.windll.user32.MessageBoxW(
            None, "Cancelled or invalid input.", "Cipher", 0x40
        )
        return

    encoded = caesar(plaintext, shift)
    ok = set_clipboard_text(encoded)
    if ok:
        ctypes.windll.user32.MessageBoxW(
            None, f"Copied {len(encoded)} encrypted character(s) to the clipboard.",
            "Cipher", 0x40
        )
    else:
        ctypes.windll.user32.MessageBoxW(
            None, "Failed to write to clipboard.", "Cipher", 0x10
        )


if __name__ == "__main__":
    main()

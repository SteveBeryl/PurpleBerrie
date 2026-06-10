import ctypes
import ctypes.wintypes as w
import threading
import time
import tkinter as tk
from tkinter import ttk
import queue

# ---------- Caesar cipher ----------
def caesar(text: str, shift: int) -> str:
    s = shift % 26
    out = []
    for ch in text:
        code = ord(ch)
        if 65 <= code <= 90:
            out.append(chr((code - 65 + s) % 26 + 65))
        elif 97 <= code <= 122:
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


# ---------- Global hotkey (Win32 RegisterHotKey) ----------
# Hotkey IDs
HK_ENCRYPT = 1     # Ctrl+Shift+C
HK_TOGGLE = 2      # Ctrl+Shift+X  (toggle listening)
MOD_CONTROL  = 0x0002
MOD_SHIFT    = 0x0004
MOD_NOREPEAT = 0x4000
VK_C = 0x43
VK_X = 0x58

WM_HOTKEY = 0x0312

class HotkeyListener(threading.Thread):
    """Runs a hidden message-only window to receive WM_HOTKEY messages."""
    def __init__(self, on_hotkey):
        super().__init__(daemon=True)
        self.on_hotkey = on_hotkey
        self._stop = threading.Event()
        self.hwnd = None

    def stop(self):
        self._stop.set()
        if self.hwnd:
            user32.PostMessageW(self.hwnd, 0x0010, 0, 0)  # WM_CLOSE

    def run(self):
        # Register window class
        WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_long, w.HWND, w.UINT, w.WPARAM, w.LPARAM)

        def wndproc(hwnd, msg, wp, lp):
            if msg == WM_HOTKEY:
                self.on_hotkey(int(wp))
            elif msg == 0x0010:  # WM_CLOSE
                user32.DestroyWindow(hwnd)
                return 0
            return user32.DefWindowProcW(hwnd, msg, wp, lp)

        self._wndproc = WNDPROC(wndproc)  # keep ref alive

        wc = user32.WNDCLASSEXW()
        wc.cbSize = ctypes.sizeof(wc)
        wc.lpfnWndProc = self._wndproc
        wc.hInstance = kernel32.GetModuleHandleW(None)
        wc.lpszClassName = "CipherHotkeyWnd"

        if not user32.RegisterClassExW(ctypes.byref(wc)):
            return

        # HWND_MESSAGE = -3 -> message-only window (no taskbar icon)
        self.hwnd = user32.CreateWindowExW(
            0, wc.lpszClassName, "CipherHotkey",
            0, 0, 0, 0, 0,
            -3, None, wc.hInstance, None
        )
        if not self.hwnd:
            return

        # Register hotkeys
        user32.RegisterHotKey(self.hwnd, HK_ENCRYPT, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, VK_C)
        user32.RegisterHotKey(self.hwnd, HK_TOGGLE,  MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, VK_X)

        # Pump messages
        msg = w.MSG()
        while not self._stop.is_set():
            res = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if res == 0 or res == -1:
                break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        user32.UnregisterHotKey(self.hwnd, HK_ENCRYPT)
        user32.UnregisterHotKey(self.hwnd, HK_TOGGLE)
        user32.DestroyWindow(self.hwnd)


# ---------- Clipboard poller (fallback) ----------
class ClipboardDaemon(threading.Thread):
    def __init__(self, get_shift, is_enabled, on_event):
        super().__init__(daemon=True)
        self.get_shift = get_shift
        self.is_enabled = is_enabled
        self.on_event = on_event
        self._stop = threading.Event()
        self._last_seen = None

    def stop(self):
        self._stop.set()

    def set_last_seen(self, text):
        self._last_seen = text

    def run(self):
        self._last_seen = get_clipboard_text()
        self.on_event("baseline", self._last_seen, 0)
        while not self._stop.is_set():
            time.sleep(0.5)
            if not self.is_enabled():
                continue
            try:
                current = get_clipboard_text()
            except Exception as e:
                self.on_event("error", repr(e), 0)
                continue
            if current == self._last_seen:
                continue
            self._last_seen = current
            if not current:
                self.on_event("empty", "", 0)
                continue
            shift = self.get_shift()
            try:
                encoded = caesar(current, shift)
                set_clipboard_text(encoded)
                self._last_seen = encoded
                self.on_event("encrypted", (current, encoded), shift)
            except Exception as e:
                self.on_event("error", repr(e), 0)


# ---------- GUI ----------
class CipherApp:
    def __init__(self, root):
        self.root = root
        root.title("Cipher Auto-Encrypt")
        root.geometry("620x460")
        root.minsize(500, 340)

        self.enabled = tk.BooleanVar(value=False)
        self.shift = tk.IntVar(value=1)

        # --- Top control panel ---
        top = ttk.Frame(root, padding=10)
        top.pack(fill="x")

        self.toggle = ttk.Checkbutton(
            top, text="Listen & auto-encrypt clipboard",
            variable=self.enabled, command=self._on_toggle,
        )
        self.toggle.pack(anchor="w")

        row = ttk.Frame(top)
        row.pack(fill="x", pady=(8, 0))
        ttk.Label(row, text="Shift:").pack(side="left")
        ttk.Spinbox(row, from_=-25, to=25, textvariable=self.shift, width=6).pack(side="left", padx=6)
        ttk.Button(row, text="Encrypt NOW", command=self.encrypt_now).pack(side="left", padx=(12, 0))
        ttk.Button(row, text="Clear log", command=self._clear_log).pack(side="left", padx=(6, 0))

        # --- Global hotkey help ---
        help_frame = ttk.LabelFrame(root, text="Global hotkeys (work in ANY app)", padding=8)
        help_frame.pack(fill="x", padx=10, pady=(0, 6))
        ttk.Label(help_frame,
                  text="Ctrl + Shift + C  =  Encrypt the current clipboard RIGHT NOW\n"
                       "Ctrl + Shift + X  =  Toggle auto-listen on/off",
                  justify="left", foreground="#036").pack(anchor="w")

        # --- Status line ---
        self.status_var = tk.StringVar(value="Idle. Use Ctrl+Shift+C to encrypt, or tick the checkbox.")
        self.status = ttk.Label(root, textvariable=self.status_var, foreground="#555",
                                padding=(10, 4), anchor="w")
        self.status.pack(fill="x")

        # --- Log box ---
        log_frame = ttk.Frame(root, padding=(10, 0, 10, 10))
        log_frame.pack(fill="both", expand=True)
        ttk.Label(log_frame, text="Activity log:").pack(anchor="w")
        self.log = tk.Text(log_frame, height=12, wrap="word", state="disabled",
                           font=("Consolas", 9))
        self.log.pack(fill="both", expand=True, pady=(4, 0))
        sb = ttk.Scrollbar(self.log, command=self.log.yview)
        self.log.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        # --- Daemon ---
        self.daemon = ClipboardDaemon(
            get_shift=lambda: int(self.shift.get()),
            is_enabled=lambda: bool(self.enabled.get()),
            on_event=self._on_event_threaded,
        )
        self.daemon.start()

        # --- Global hotkey listener ---
        self.hotkey = HotkeyListener(self._on_hotkey_threaded)
        self.hotkey.start()

        self._log("App started. Use Ctrl+Shift+C in any app to encrypt current clipboard.")
        self._log("Tip: tick 'Listen & auto-encrypt' for automatic mode, OR use the hotkey manually.")

        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _on_toggle(self):
        if self.enabled.get():
            self._log(">>> Listening STARTED. Copy text anywhere with Ctrl+C.")
            self.status_var.set("Listening... copy text with Ctrl+C to auto-encrypt.")
        else:
            self._log(">>> Listening PAUSED.")
            self.status_var.set("Paused. Use Ctrl+Shift+C to encrypt, or re-enable listening.")

    def encrypt_now(self):
        text = get_clipboard_text()
        if not text:
            self._log("[manual] Clipboard is empty.")
            return
        shift = int(self.shift.get())
        encoded = caesar(text, shift)
        ok = set_clipboard_text(encoded)
        if ok:
            self.daemon.set_last_seen(encoded)
            self._log_event("manual", text, encoded, shift)
        else:
            self._log("[manual] Failed to write to clipboard.")

    def _on_hotkey_threaded(self, hk_id):
        if hk_id == HK_ENCRYPT:
            self.root.after(0, self.encrypt_now)
        elif hk_id == HK_TOGGLE:
            self.root.after(0, self._hotkey_toggle)

    def _hotkey_toggle(self):
        self.enabled.set(not self.enabled.get())
        self._on_toggle()

    def _on_event_threaded(self, kind, payload, shift):
        self.root.after(0, self._on_event, kind, payload, shift)

    def _on_event(self, kind, payload, shift):
        if kind == "baseline":
            preview = (payload[:60] + "...") if payload and len(payload) > 60 else (payload or "(empty)")
            self._log(f"[baseline] {preview!r}")
        elif kind == "empty":
            self._log("[empty] Clipboard was cleared.")
        elif kind == "error":
            self._log(f"[ERROR] {payload}")
            self.status_var.set("Error reading clipboard -- see log.")
        elif kind == "encrypted":
            orig, enc = payload
            self._log_event("auto", orig, enc, shift)
        else:
            self._log(f"[{kind}] {payload!r}")

    def _log_event(self, mode, orig, enc, shift):
        po = (orig[:60] + "...") if len(orig) > 60 else orig
        pe = (enc[:60] + "...") if len(enc) > 60 else enc
        self._log(f"[{mode}] shift={shift}")
        self._log(f"   in : {po!r}")
        self._log(f"   out: {pe!r}")
        self.status_var.set(f"Last: shift {shift}  ->  {pe!r}")

    def _log(self, msg):
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n")
        line_count = int(self.log.index("end-1c").split(".")[0])
        if line_count > 500:
            self.log.delete("1.0", "200.0")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def on_close(self):
        self.daemon.stop()
        self.hotkey.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    CipherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

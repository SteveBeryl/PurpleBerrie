# Cipher Auto-Encrypt Tool

This Windows utility provides seamless, real-time clipboard encryption. It continuously monitors for new text and instantly applies a Caesar cipher shift of 1. Built with a resilient hybrid engine (Tkinter/Win32), it features a user-friendly GUI with an activity log and a toggle button to easily enable or pause monitoring as needed.

## Features
- **Always-On Monitoring:** Automatically detects clipboard changes.
- **GUI Control:** Toggle monitoring on/off with a single click.
- **Resilient Engine:** Uses a hybrid high-level (Tkinter) and low-level (Win32) approach to ensure compatibility and stability on Windows.
- **Activity Log:** Real-time feedback on encryption tasks.

## How to Use
1. Run `cipher-v1.exe` (or run `cipher_v1.py` if you have Python installed).
2. Ensure the status shows **MONITORING ACTIVE**.
3. Copy any text (e.g., "test").
4. The text is immediately replaced on your clipboard with the encrypted version (e.g., "uftu").
5. Paste anywhere!

## Development
This project is written in Python 3.13.

### Requirements
- Python 3.x
- `pyinstaller` (for building the .exe)

### Building the Executable
To generate a standalone `.exe` file:
```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --noconsole --name cipher-v1 cipher_v1.py
```

## License
MIT

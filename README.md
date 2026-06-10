# Cipher Auto-Encrypt Tool

This Windows utility provides seamless, real-time clipboard encryption. It continuously monitors for new text and instantly applies a Caesar cipher shift of 1.

## Available Versions

### **Version 2 (Current)**
- **Enhanced UI:** Color-coded logs, modern fonts, and improved layout.
- **Detailed Feedback:** Real-time visibility of detection and encryption actions.
- **Toggle Control:** Easily pause or resume monitoring with a single button.

### **Version 1 (Legacy)**
- **Original UI:** Simple, clean interface using standard Tkinter elements.
- **Reliable Logic:** Uses the same resilient hybrid engine as V2.

## Features
- **Always-On Monitoring:** Automatically detects clipboard changes.
- **GUI Control:** Toggle monitoring on/off with a single click.
- **Resilient Engine:** Uses a hybrid high-level (Tkinter) and low-level (Win32) approach to ensure compatibility and stability on Windows.

## How to Use
1. Run `cipher-v2.exe` for the enhanced UI, or `cipher-v1.exe` for the legacy look.
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
```bash
pip install pyinstaller
# To build V1
pyinstaller --noconfirm --onefile --noconsole --name cipher-v1 cipher_v1.py
# To build V2
pyinstaller --noconfirm --onefile --noconsole --name cipher-v2 cipher_v2.py
```

## License
MIT

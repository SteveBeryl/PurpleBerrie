# Cipher Auto-Encrypt Tool

This Windows utility provides seamless, real-time clipboard encryption. It continuously monitors for new text and instantly applies a Caesar cipher shift of 1.

## Available Versions

### **Version 3 (Latest)**
- **Refined UI:** Professional, high-contrast interface with improved visual hierarchy.
- **Enhanced Legibility:** Optimized font weights and clearer activity log layout.
- **Dynamic Feedback:** Real-time visibility of clipboard changes with color-coded status.

### **Version 2**
- **Original Enhanced UI:** Color-coded logs and improved layout.
- **Reliable Logic:** Uses the same resilient hybrid engine.

### **Version 1 (Legacy)**
- **Classic UI:** Simple, clean interface using standard Tkinter elements.

## Features
- **Always-On Monitoring:** Automatically detects clipboard changes.
- **GUI Control:** Toggle monitoring on/off with a single click.
- **Resilient Engine:** Uses a hybrid high-level (Tkinter) and low-level (Win32) approach for maximum stability on Windows.

## How to Use
1. Run `ClipCipher_Latest.exe` for the most up-to-date experience.
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
# To build Latest (V3)
pyinstaller ClipCipher_Latest.spec
```

## License
MIT

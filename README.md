# PurpleBerrie

This Windows utility provides seamless, real-time clipboard encryption. It continuously monitors for new text and instantly applies a selected encryption method.

## Available Versions

### **Version 4 (Latest)**
- **App Name:** Renamed to **PurpleBerrie**.
- **Enhanced Status Labels:** Now displays **ACTIVATED** and **DEACTIVATED** states.
- **High-Quality Branding:** Uses a new, high-quality, transparent icon (cropped from Beryl Poster).
- **Multi-Algorithm Support:** Choose between Caesar, ROT13, Atbash, Base64, and Reverse.
- **Dynamic Method Selection:** Select the desired encryption on the fly from the UI menu.

### **Version 3**
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
- **Encryption Selection:** Pick your preferred algorithm in real-time.
- **Resilient Engine:** Uses a hybrid high-level (Tkinter) and low-level (Win32) approach for maximum stability on Windows.

## How to Use
1. Run `PurpleBerrie.exe` for the most up-to-date experience.
2. Select the desired encryption algorithm from the dropdown menu.
3. Ensure the status shows **ACTIVATED**.
4. Copy any text.
5. The text is immediately replaced on your clipboard with the encrypted version.
6. Paste anywhere!

## Development
This project is written in Python 3.13.

### Requirements
- Python 3.x
- `pyinstaller` (for building the .exe)

## License
MIT

## Last Updated
June 10, 2026

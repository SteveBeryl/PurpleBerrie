# PurpleBerrie V5

PurpleBerrie is a powerful, real-time Windows clipboard encryption utility designed for seamless security. It automatically monitors your clipboard and instantly encrypts any copied text using your selected algorithm.

## Features & Implemented Enhancements (V5)

### 1. Advanced Encryption Engine
- **Multiple Algorithms:** Choose from a robust list of ciphers:
  - **Affine:** Algebraic cipher for secure text substitution.
  - **Atbash:** Classic substitution cipher.
  - **Bacon:** Converts text into a binary-like representation.
  - **Base64:** Standard encoding format.
  - **Beaufort:** Polyalphabetic substitution cipher.
  - **Caesar:** Classic shift cipher.
  - **Playfair:** Polygraphic substitution cipher.
  - **Reverse:** Simply reverses the text string.
  - **ROT13:** Basic 13-character rotation.
- **Dynamic Selection:** Switch encryption methods instantly via the UI dropdown menu.

### 2. High-Performance Monitoring
- **Real-Time Encryption:** Monitors clipboard changes continuously and applies encryption automatically.
- **Global Hotkey Support:** Toggle the service on/off globally using `Ctrl` + `Alt` + `B`, even when the application is minimized or in the background.

### 3. Modern & Scalable UI
- **Renamed:** Formerly "ClipCipher", the application is now branded as **PurpleBerrie**.
- **Intuitive Status:** Clearly toggles between **ACTIVATED** and **DEACTIVATED** states.
- **Improved Clarity:** Updated UI font configuration (`Segoe UI`, size 11) ensures high-contrast, crystal-clear text rendering on high-DPI displays.
- **Responsive Layout:** The UI now utilizes a grid-based scaling manager to ensure a consistent appearance across different display settings.
- **Professional Aesthetic:** Refined color palette (Deep Purple/Light Purple) for a sleek, modern look.
- **High-Quality Branding:** Uses a high-resolution, transparent icon (512x512) for the window title, taskbar, and executable.

### 4. Stability & Usability
- **Hybrid Engine:** Uses both high-level `tkinter` and low-level `win32` API calls for maximum stability and reliability on Windows systems.
- **High-DPI Aware:** Specifically configured to render clearly on modern high-resolution screens.

## How to Use
1. Run `PurpleBerrie.exe`.
2. Select your desired algorithm from the **Method** dropdown.
3. Use the **ON/OFF** switch or the global hotkey (`Ctrl` + `Alt` + `B`) to toggle encryption.
4. Copy any text; it will be instantly replaced on your clipboard with its encrypted version.
5. Paste your encrypted text anywhere.

## Development
- **Language:** Python 3.13
- **Dependencies:** `pyinstaller`, `pynput`, `Pillow`, `requests`, `tkinter`.
- **License:** MIT

## Last Updated
June 10, 2026

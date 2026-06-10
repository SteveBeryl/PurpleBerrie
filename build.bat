@echo off
setlocal
cd /d "%~dp0"

python -m pip install --upgrade pip >nul
python -m pip install --upgrade pyinstaller >nul

echo === Building cipher.exe (one-shot popup) ===
python -m PyInstaller --noconfirm --onefile --noconsole --name cipher cipher.py

echo === Building cipher-daemon.exe (background listener) ===
python -m PyInstaller --noconfirm --onefile --noconsole --name cipher-daemon cipher_daemon.py

if exist dist\cipher.exe (
    echo.
    echo ONE-SHOT:    dist\cipher.exe
) else (
    echo ONE-SHOT BUILD FAILED
)
if exist dist\cipher-daemon.exe (
    echo LISTENER:    dist\cipher-daemon.exe
) else (
    echo LISTENER BUILD FAILED
)
pause

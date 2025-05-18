@echo off
echo Building Step Paster for Windows...

REM Install PyInstaller if not already installed
pip install pyinstaller

REM Build the executable
pyinstaller --onefile --name step_paster ^
  --hidden-import pyperclip ^
  --hidden-import pyautogui ^
  --hidden-import keyboard ^
  --hidden-import pynput ^
  --collect-all keyboard ^
  --collect-all pyautogui ^
  --collect-all pyperclip ^
  --collect-all pynput ^
  main.py

echo Build complete! Check the 'dist' folder for your executable.
pause
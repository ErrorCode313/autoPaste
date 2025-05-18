#!/bin/bash
echo "Building Step Paster for macOS..."

# Install PyInstaller if not already installed
pip install pyinstaller

# Build the executable
pyinstaller --onefile --name step_paster \
  --hidden-import pyperclip \
  --hidden-import pyautogui \
  --hidden-import pynput \
  --collect-all pyautogui \
  --collect-all pyperclip \
  --collect-all pynput \
  main.py

echo "Build complete! Check the 'dist' folder for your executable."
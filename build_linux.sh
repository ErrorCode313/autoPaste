#!/bin/bash
echo "Building Step Paster for Linux..."

# Install required system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-tk python3-dev scrot xclip

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
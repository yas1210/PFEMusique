#!/bin/bash
set -e

PYTHON="$(dirname "$0")/../.venv/bin/python"

if [ ! -f "$PYTHON" ]; then
  echo "ERROR: Virtual environment Python not found at $PYTHON"
  echo "Run this script from the project root, or activate your venv first."
  exit 1
fi

echo "Installing PyInstaller if needed..."
"$PYTHON" -m pip install --upgrade pyinstaller

echo "Building MusicMove executable..."
"$PYTHON" -m PyInstaller --clean --noconfirm MPipophoneOS.spec

if [ $? -ne 0 ]; then
  echo "ERROR: PyInstaller build failed."
  exit 1
fi

echo ""
echo "Build complete."
echo "Executable produced at dist/MPipophone"
read -p "Press Enter to continue..."
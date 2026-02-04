#!/bin/bash

set -e

REPO_URL="https://github.com/j341nono/SignalSurfer.git"
REPO_DIR="SignalSurfer"

if ! command -v uv &> /dev/null
then
    echo "'uv' is not installed. Please install it first."
    echo "Installation guide: https://astral.sh/docs/uv#installation"
    exit 1
fi

if [ -d "$REPO_DIR" ]; then
    echo "Removing existing '$REPO_DIR' directory..."
    rm -rf "$REPO_DIR"
fi

echo "Cloning SignalSurfer..."
git clone "$REPO_URL"

cd "$REPO_DIR"

echo "Creating virtual environment (.venv) and installing dependencies..."
uv venv
source .venv/bin/activate
uv add pyinstaller

echo "Building the app..."
.venv/bin/python -m PyInstaller --onefile --windowed --name="WiFi Signal Visualizer" --icon assets/app.icns --noconfirm src/__main__.py

deactivate
cd ..
rm -rf "$REPO_DIR"


echo "Build complete! The app is in the 'dist' folder."

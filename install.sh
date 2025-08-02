#!/bin/bash

set -e

REPO_URL="https://github.com/j341nono/SignalSurfer.git"
REPO_DIR="SignalSurfer"

# uvコマンドがインストールされているか確認
if ! command -v uv &> /dev/null
then
    echo "❌ 'uv' is not installed. Please install it first."
    echo "Installation guide: https://astral.sh/docs/uv#installation"
    exit 1
fi

echo "Cloning SignalSurfer..."
git clone "$REPO_URL"
cd "$REPO_DIR"

echo "Creating virtual environment (.venv)..."
uv venv

echo "Installing dependencies with uv sync..."
uv sync

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Building the app..."
pyinstaller --onefile --windowed --name="WiFi Signal Visualizer" --icon=app.icns main.py

echo "✅ Build complete! You can find the app in the 'dist' folder."
# Signal Surfer

**Signal Surfer** is a macOS desktop application that visualizes your current Wi-Fi signal strength using dynamic animations.

---

## Features

- Real-time detection of Wi-Fi signal strength using macOS's CoreWLAN framework
- Visual feedback with animations that vary depending on signal strength levels
- Lightweight UI application packaged with PyInstaller

---

## Installation

### For a quick and easy installation
run the following command in your terminal:

```bash
curl -sL https://raw.githubusercontent.com/j341nono/SignalSurfer/main/install.sh | bash
```

### manually

Alternatively, you can clone the repository and build the app manually:

Clone the repository and build the app:

```bash
git clone git@github.com:j341nono/SignalSurfer.git
cd SignalSurfer

# (Optional) Create and activate virtual environment
source .venv/bin/activate

# Build the app
pyinstaller --onefile --windowed --name="WiFi Signal Visualizer" --icon=app.icns main.py
```
Requires Python 3.8+ and pyinstaller installed in your environment.

## Usage
After building, navigate to the dist/ directory:

- cd dist/
- Double-click on WiFi Signal Visualizer to launch the app.
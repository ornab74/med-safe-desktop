#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$HOME/med-safe-desktop}"
VENV_DIR="$APP_DIR/venv"
REPO_URL="${REPO_URL:-https://github.com/ornab74/humoid-gui-gemma-4.git}"

if ! command -v git >/dev/null 2>&1; then
    echo "Git is required. Install Xcode Command Line Tools or Homebrew first."
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is required. Install it from python.org or Homebrew first."
    exit 1
fi

echo "Cloning or updating repository..."
mkdir -p "$APP_DIR"

if [ -d "$APP_DIR/.git" ]; then
    git -C "$APP_DIR" pull --ff-only
else
    git clone "$REPO_URL" "$APP_DIR"
fi

echo "Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"

echo "Installing Python dependencies..."
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip

if [ -f "$APP_DIR/requirements.txt" ]; then
    pip install -r "$APP_DIR/requirements.txt"
elif [ -f "$APP_DIR/requirements.in" ]; then
    pip install -r "$APP_DIR/requirements.in"
else
    echo "No requirements file found in $APP_DIR"
fi

echo
echo "macOS setup complete."
echo
echo "If tkinter is missing, install Python from python.org or add a Tk-enabled Python build."
echo "Optional for local speech output: brew install espeak"
echo
echo "To run it manually:"
echo "cd \"$APP_DIR\""
echo "source venv/bin/activate"
echo "python -u main.py"

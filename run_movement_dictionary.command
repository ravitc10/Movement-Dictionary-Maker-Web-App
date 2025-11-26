#!/bin/bash

# Change to the folder this script lives in
cd "$(dirname "$0")"

echo "Starting Movement Dictionary app..."

# Check for Python 3
if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: Python 3 is not installed."
  echo "Please install Python 3.10 or 3.11 from python.org, then run this again."
  read -n 1 -s -r -p "Press any key to exit..."
  exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment (.venv)..."
  python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
# shellcheck disable=SC1091
source .venv/bin/activate

# Install dependencies the first time
if [ ! -f ".deps_installed" ]; then
  echo "Installing dependencies (this may take a few minutes)..."
  pip install --upgrade pip
  pip install -r requirements.txt
  # Create a marker file so we don't reinstall every time
  touch .deps_installed
fi

echo "Running app.py..."
python app.py

# Keep window open if the app crashes
echo
echo "Flask app stopped. You can close this window."
read -n 1 -s -r -p "Press any key to exit..."

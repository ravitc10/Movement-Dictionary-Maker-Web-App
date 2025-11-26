@echo off
setlocal

REM Change to the folder this script lives in
cd /d "%~dp0"

echo Starting Movement Dictionary app...

REM Check for Python
where python >nul 2>nul
if errorlevel 1 (
  echo Error: Python is not installed or not on PATH.
  echo Please install Python 3.10 or 3.11 from https://www.python.org/downloads/
  echo and make sure "Add Python to PATH" is checked during install.
  pause
  exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
  echo Creating virtual environment (.venv)...
  python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies the first time
if not exist ".deps_installed" (
  echo Installing dependencies (this may take a few minutes)...
  pip install --upgrade pip
  pip install -r requirements.txt
  type nul > .deps_installed
)

echo Running app.py...
python app.py

echo.
echo Flask app stopped. You can close this window.
pause

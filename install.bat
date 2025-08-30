@echo off
echo Installing Snapchat Score Tracker Dependencies...
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo.
echo Installing Python packages...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install some packages
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo Installation complete!
echo.
echo Next steps:
echo 1. Install ChromeDriver if not already installed
echo 2. Run the application with: python main.py
echo   or double-click run.bat
echo.
pause
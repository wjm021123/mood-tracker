@echo off
cd /d "%~dp0"

echo Checking Python...
py --version

echo Upgrading pip...
py -m pip install --upgrade pip

echo Installing dependencies...
py -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo Launching Mood Tracker...
py -m streamlit run app.py

pause
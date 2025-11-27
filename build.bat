@echo off
REM Build script for Windows executable
REM Run this from a Windows machine with Python installed

echo ==========================================
echo DjVu to PDF Converter - Windows Build
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Checking for bin directory...
if not exist "bin\" (
    echo WARNING: bin\ directory not found!
    echo.
    echo Please create a bin\ directory and add these Windows executables:
    echo   - djvused.exe
    echo   - ddjvu.exe
    echo   - djvu2hocr.exe
    echo   - tiffsplit.exe
    echo   - pdfbeads (Ruby script/executable)
    echo.
    echo See BUILD_WINDOWS.md for details.
    echo.
    pause
)

echo.
echo [3/4] Building executable with PyInstaller...
pyinstaller build_windows.spec
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo [4/4] Build complete!
echo.
echo Your executable is ready: dist\djvu2pdf.exe
echo.
echo You can now distribute this single .exe file.
echo It contains all dependencies and requires no installation!
echo.
pause

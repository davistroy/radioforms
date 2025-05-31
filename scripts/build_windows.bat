@echo off
REM Build script for Windows executable
REM Requires Python 3.10+ with PyInstaller

echo ====================================================
echo Building RadioForms for Windows
echo ====================================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists, create if not
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Install PyInstaller if not present
pip install pyinstaller
if %errorlevel% neq 0 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "RadioForms-Windows.exe" del "RadioForms-Windows.exe"

REM Run tests before building
echo Running tests...
python test_comprehensive_suite.py
if %errorlevel% neq 0 (
    echo WARNING: Some tests failed. Continue anyway? (y/n)
    set /p continue=
    if /i not "%continue%"=="y" (
        echo Build cancelled by user
        pause
        exit /b 1
    )
)

REM Build executable
echo Building executable...
pyinstaller radioforms.spec
if %errorlevel% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

REM Move executable to root directory
if exist "dist\RadioForms-Windows.exe" (
    move "dist\RadioForms-Windows.exe" "RadioForms-Windows.exe"
    echo.
    echo ====================================================
    echo Build completed successfully!
    echo Executable: RadioForms-Windows.exe
    echo ====================================================
) else (
    echo ERROR: Executable not found in dist directory
    exit /b 1
)

REM Test the executable
echo Testing executable...
"RadioForms-Windows.exe" --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Executable test passed
) else (
    echo ⚠ Executable test failed - manual testing required
)

REM File size information
for %%I in ("RadioForms-Windows.exe") do echo File size: %%~zI bytes

echo.
echo Build complete! Test the executable before distribution.
pause
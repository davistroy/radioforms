@echo off
REM RadioForms Release Build Script for Windows
REM Simple, reliable build process following MANDATORY.md principles

echo 🚀 Building RadioForms Release...

REM Check if we're in the right directory
if not exist "package.json" (
    echo ❌ Error: Must run from project root directory
    exit /b 1
)

REM Check for npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: npm is required but not installed
    exit /b 1
)

REM Check for cargo
cargo --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Rust/Cargo is required but not installed
    exit /b 1
)

echo ✅ Environment checks passed

REM Install dependencies if needed
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install
)

echo 🔨 Starting build process...

REM Check for Windows code signing credentials
set HAVE_WINDOWS_SIGNING=false
if defined TAURI_SIGNING_PRIVATE_KEY if defined TAURI_SIGNING_PRIVATE_KEY_PASSWORD (
    set HAVE_WINDOWS_SIGNING=true
    echo 🔐 Windows code signing credentials found
)

echo 🖥️  Building for Windows platform

REM Build based on signing availability
if "%HAVE_WINDOWS_SIGNING%"=="true" (
    echo 🔐 Building signed Windows release...
    npm run tauri build
) else (
    echo ⚠️  Building unsigned release ^(no code signing credentials^)
    echo    This is fine for development and internal use
    npm run tauri build --no-bundle
)

REM Check build results
if %ERRORLEVEL% equ 0 (
    echo ✅ Build completed successfully!
    echo.
    echo 📁 Build outputs located in:
    echo    src-tauri\target\release\
    echo.
    echo 🎉 RadioForms build complete!
    echo    Ready for deployment and testing
) else (
    echo ❌ Build failed!
    echo    Check the error messages above
    exit /b 1
)
#!/bin/bash
# Build script for macOS application bundle
# Requires Python 3.10+ with PyInstaller

set -e  # Exit on any error

echo "===================================================="
echo "Building RadioForms for macOS"
echo "===================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.10+ using Homebrew or python.org"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ "$(printf '%s\n' "3.10" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.10" ]]; then
    echo "ERROR: Python 3.10 or newer is required. Found: $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements-dev.txt

# Install PyInstaller if not present
pip install pyinstaller

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist
rm -f RadioForms-macOS
rm -rf RadioForms.app

# Run tests before building
echo "Running tests..."
if ! python test_comprehensive_suite.py; then
    echo "WARNING: Some tests failed. Continue anyway? (y/n)"
    read -r continue
    if [[ ! "$continue" =~ ^[Yy]$ ]]; then
        echo "Build cancelled by user"
        exit 1
    fi
fi

# Build application bundle
echo "Building application bundle..."
pyinstaller radioforms.spec

# Check if build was successful
if [ -f "dist/RadioForms-macOS" ]; then
    mv "dist/RadioForms-macOS" "RadioForms-macOS"
    echo ""
    echo "===================================================="
    echo "Build completed successfully!"
    echo "Executable: RadioForms-macOS"
    echo "===================================================="
elif [ -d "dist/RadioForms.app" ]; then
    mv "dist/RadioForms.app" "RadioForms.app"
    echo ""
    echo "===================================================="
    echo "Build completed successfully!"
    echo "Application Bundle: RadioForms.app"
    echo "===================================================="
else
    echo "ERROR: Build output not found in dist directory"
    exit 1
fi

# Test the executable
echo "Testing executable..."
if [ -f "RadioForms-macOS" ]; then
    if ./RadioForms-macOS --version >/dev/null 2>&1; then
        echo "✓ Executable test passed"
    else
        echo "⚠ Executable test failed - manual testing required"
    fi
    
    # File size information
    echo "File size: $(du -h RadioForms-macOS | cut -f1)"
fi

if [ -d "RadioForms.app" ]; then
    echo "App bundle size: $(du -sh RadioForms.app | cut -f1)"
    
    # Test app bundle
    if open -W RadioForms.app --args --version >/dev/null 2>&1; then
        echo "✓ App bundle test passed"
    else
        echo "⚠ App bundle test failed - manual testing required"
    fi
fi

# Code signing information (if certificates are available)
if command -v codesign &> /dev/null; then
    echo ""
    echo "Note: For distribution, you should code sign the application:"
    if [ -f "RadioForms-macOS" ]; then
        echo "codesign --force --deep --sign \"Developer ID Application: Your Name\" RadioForms-macOS"
    fi
    if [ -d "RadioForms.app" ]; then
        echo "codesign --force --deep --sign \"Developer ID Application: Your Name\" RadioForms.app"
    fi
fi

# Notarization information
echo ""
echo "Note: For macOS 10.15+ distribution, you should also notarize the application:"
echo "xcrun notarytool submit --apple-id your-email --password app-password --team-id TEAM_ID RadioForms.zip"

echo ""
echo "Build complete! Test the application before distribution."
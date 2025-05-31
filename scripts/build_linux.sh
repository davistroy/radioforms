#!/bin/bash
# Build script for Linux AppImage
# Requires Python 3.10+ with PyInstaller

set -e  # Exit on any error

echo "===================================================="
echo "Building RadioForms for Linux"
echo "===================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.10+ using your package manager"
    echo "Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "CentOS/RHEL: sudo yum install python3 python3-venv python3-pip"
    echo "Fedora: sudo dnf install python3 python3-venv python3-pip"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ "$(printf '%s\n' "3.10" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.10" ]]; then
    echo "ERROR: Python 3.10 or newer is required. Found: $PYTHON_VERSION"
    exit 1
fi

# Check for required system libraries
echo "Checking system dependencies..."
MISSING_DEPS=()

# Check for GUI libraries (required for PySide6)
if ! ldconfig -p | grep -q libX11; then
    MISSING_DEPS+=("libX11-dev")
fi

if ! ldconfig -p | grep -q libGL; then
    MISSING_DEPS+=("libgl1-mesa-dev")
fi

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo "WARNING: Missing system dependencies: ${MISSING_DEPS[*]}"
    echo "Install with:"
    echo "Ubuntu/Debian: sudo apt install ${MISSING_DEPS[*]}"
    echo "CentOS/RHEL: sudo yum install mesa-libGL-devel libX11-devel"
    echo "Continue anyway? (y/n)"
    read -r continue
    if [[ ! "$continue" =~ ^[Yy]$ ]]; then
        echo "Build cancelled by user"
        exit 1
    fi
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
rm -f RadioForms-Linux RadioForms-Linux.AppImage

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

# Build executable
echo "Building executable..."
pyinstaller radioforms.spec

# Check if build was successful
if [ -f "dist/RadioForms-Linux" ]; then
    mv "dist/RadioForms-Linux" "RadioForms-Linux"
    chmod +x "RadioForms-Linux"
    echo ""
    echo "===================================================="
    echo "Build completed successfully!"
    echo "Executable: RadioForms-Linux"
    echo "===================================================="
else
    echo "ERROR: Executable not found in dist directory"
    exit 1
fi

# Test the executable
echo "Testing executable..."
if ./RadioForms-Linux --version >/dev/null 2>&1; then
    echo "✓ Executable test passed"
else
    echo "⚠ Executable test failed - manual testing required"
fi

# File size information
echo "File size: $(du -h RadioForms-Linux | cut -f1)"

# Try to create AppImage if tools are available
if command -v wget &> /dev/null && command -v chmod &> /dev/null; then
    echo ""
    echo "Creating AppImage..."
    
    # Download AppImage tool if not present
    if [ ! -f "appimagetool-x86_64.AppImage" ]; then
        echo "Downloading AppImage tool..."
        wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
        chmod +x appimagetool-x86_64.AppImage
    fi
    
    # Create AppDir structure
    mkdir -p RadioForms.AppDir/usr/bin
    mkdir -p RadioForms.AppDir/usr/share/applications
    mkdir -p RadioForms.AppDir/usr/share/icons/hicolor/256x256/apps
    
    # Copy executable
    cp RadioForms-Linux RadioForms.AppDir/usr/bin/radioforms
    
    # Create desktop file
    cat > RadioForms.AppDir/usr/share/applications/radioforms.desktop << EOF
[Desktop Entry]
Type=Application
Name=RadioForms
Comment=FEMA ICS Forms Management
Exec=radioforms
Icon=radioforms
Categories=Office;Utility;
EOF
    
    # Create AppRun
    cat > RadioForms.AppDir/AppRun << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
exec "${HERE}/usr/bin/radioforms" "$@"
EOF
    chmod +x RadioForms.AppDir/AppRun
    
    # Copy desktop file to root
    cp RadioForms.AppDir/usr/share/applications/radioforms.desktop RadioForms.AppDir/
    
    # Create icon (if available) or use placeholder
    if [ -f "resources/radioforms.png" ]; then
        cp resources/radioforms.png RadioForms.AppDir/usr/share/icons/hicolor/256x256/apps/radioforms.png
        cp resources/radioforms.png RadioForms.AppDir/radioforms.png
    else
        # Create simple placeholder icon
        echo "No icon file found, using placeholder"
        touch RadioForms.AppDir/radioforms.png
    fi
    
    # Build AppImage
    if ./appimagetool-x86_64.AppImage RadioForms.AppDir RadioForms-Linux.AppImage >/dev/null 2>&1; then
        echo "✓ AppImage created successfully: RadioForms-Linux.AppImage"
        echo "AppImage size: $(du -h RadioForms-Linux.AppImage | cut -f1)"
        
        # Test AppImage
        if ./RadioForms-Linux.AppImage --version >/dev/null 2>&1; then
            echo "✓ AppImage test passed"
        else
            echo "⚠ AppImage test failed - manual testing required"
        fi
    else
        echo "⚠ AppImage creation failed, but executable is available"
    fi
    
    # Clean up
    rm -rf RadioForms.AppDir
else
    echo ""
    echo "Note: wget not available, skipping AppImage creation"
    echo "You can create an AppImage manually using AppImageTool"
fi

# Distribution information
echo ""
echo "Distribution notes:"
echo "- Test on clean systems before distributing"
echo "- Verify all dependencies are included"
echo "- Check that executable works without Python installed"
echo "- Consider creating .deb/.rpm packages for easier installation"

echo ""
echo "Build complete! Test the executable before distribution."
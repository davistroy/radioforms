#!/bin/bash
# RadioForms Release Build Script
# Simple, reliable build process following MANDATORY.md principles

set -e  # Exit on any error

echo "🚀 Building RadioForms Release..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# Check for Node.js and npm
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is required but not installed"
    exit 1
fi

# Check for Rust and Cargo
if ! command -v cargo &> /dev/null; then
    echo "❌ Error: Rust/Cargo is required but not installed"
    exit 1
fi

echo "✅ Environment checks passed"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "🔨 Starting build process..."

# Check for code signing credentials
HAVE_WINDOWS_SIGNING=false
HAVE_MACOS_SIGNING=false

if [[ -n "$TAURI_SIGNING_PRIVATE_KEY" && -n "$TAURI_SIGNING_PRIVATE_KEY_PASSWORD" ]]; then
    HAVE_WINDOWS_SIGNING=true
    echo "🔐 Windows code signing credentials found"
fi

if [[ -n "$APPLE_CERTIFICATE_IDENTITY" && -n "$APPLE_ID" && -n "$APPLE_PASSWORD" ]]; then
    HAVE_MACOS_SIGNING=true
    echo "🔐 macOS code signing credentials found"
fi

# Platform detection
PLATFORM="unknown"
case "$(uname -s)" in
    Linux*)     PLATFORM="linux";;
    Darwin*)    PLATFORM="macos";;
    CYGWIN*|MINGW*|MSYS*) PLATFORM="windows";;
esac

echo "🖥️  Building for platform: $PLATFORM"

# Build strategy based on platform and signing availability
if [[ "$PLATFORM" == "windows" && "$HAVE_WINDOWS_SIGNING" == true ]]; then
    echo "🔐 Building signed Windows release..."
    npm run tauri build
elif [[ "$PLATFORM" == "macos" && "$HAVE_MACOS_SIGNING" == true ]]; then
    echo "🔐 Building signed macOS release..."
    npm run tauri build
elif [[ "$PLATFORM" == "linux" ]]; then
    echo "🐧 Building Linux AppImage (no signing required)..."
    npm run tauri build
else
    echo "⚠️  Building unsigned release (no code signing credentials)"
    echo "   This is fine for development and internal use"
    npm run tauri build --no-bundle
fi

# Check build results
if [ $? -eq 0 ]; then
    echo "✅ Build completed successfully!"
    echo ""
    echo "📁 Build outputs located in:"
    echo "   src-tauri/target/release/"
    echo ""
    
    # List the actual output files
    if [ -d "src-tauri/target/release" ]; then
        echo "📦 Generated files:"
        find src-tauri/target/release -name "radioforms*" -type f -exec ls -lh {} \;
    fi
    
    echo ""
    echo "🎉 RadioForms build complete!"
    echo "   Ready for deployment and testing"
else
    echo "❌ Build failed!"
    echo "   Check the error messages above"
    exit 1
fi
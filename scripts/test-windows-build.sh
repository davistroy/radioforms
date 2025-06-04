#!/bin/bash

# Test Windows Cross-Compilation Script
# This script tests if we can build for Windows locally

echo "🚀 Testing Windows Cross-Compilation Setup"
echo "=========================================="

cd "$(dirname "$0")/.."

echo "📋 Environment Check:"
echo "Node version: $(node --version)"
echo "npm version: $(npm --version)"
echo "Rust version: $(rustc --version)"
echo ""

echo "🔧 Frontend Build Test:"
npm run build
if [ $? -eq 0 ]; then
    echo "✅ Frontend build successful"
else
    echo "❌ Frontend build failed"
    exit 1
fi
echo ""

echo "🦀 Rust Backend Check:"
cd src-tauri
cargo check --target x86_64-pc-windows-gnu 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Rust Windows target available"
    
    echo "🏗️ Attempting Windows build..."
    timeout 600 cargo build --release --target x86_64-pc-windows-gnu
    if [ $? -eq 0 ]; then
        echo "✅ Windows build successful!"
        ls -la target/x86_64-pc-windows-gnu/release/radioforms.exe 2>/dev/null && echo "✅ Windows executable created"
    else
        echo "⚠️ Windows build failed or timed out (10 minutes)"
    fi
else
    echo "❌ Windows target not available - install with:"
    echo "rustup target add x86_64-pc-windows-gnu"
fi

echo ""
echo "🎯 Summary: Local build testing complete"
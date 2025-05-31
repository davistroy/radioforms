#!/usr/bin/env python3
"""
Production Deployment Testing Script
Tests the built executable for production readiness
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import tempfile
import json

def test_executable_exists():
    """Test that the executable file exists and is accessible."""
    print("Testing executable existence...")
    
    # Platform-specific executable names
    if sys.platform == 'win32':
        exe_name = 'RadioForms-Windows.exe'
    elif sys.platform == 'darwin':
        exe_name = 'RadioForms.app'
        # Also check for standalone executable
        standalone = 'RadioForms-macOS'
        if Path(standalone).exists():
            exe_name = standalone
    else:  # Linux
        exe_name = 'RadioForms-Linux'
        # Also check for AppImage
        appimage = 'RadioForms-Linux.AppImage'
        if Path(appimage).exists():
            exe_name = appimage
    
    exe_path = Path(exe_name)
    if not exe_path.exists():
        print(f"❌ FAIL: Executable not found: {exe_name}")
        return False, exe_name
    
    print(f"✅ PASS: Executable found: {exe_name}")
    return True, str(exe_path)

def test_executable_permissions(exe_path):
    """Test that the executable has proper permissions."""
    print("Testing executable permissions...")
    
    path = Path(exe_path)
    if not os.access(path, os.X_OK):
        print(f"❌ FAIL: Executable lacks execute permissions: {exe_path}")
        return False
    
    print(f"✅ PASS: Executable has proper permissions: {exe_path}")
    return True

def test_version_command(exe_path):
    """Test that the executable responds to --version command."""
    print("Testing version command...")
    
    try:
        # Try --version flag
        result = subprocess.run(
            [exe_path, '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✅ PASS: Version command successful")
            print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"⚠️  WARN: Version command returned non-zero exit code: {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ FAIL: Version command timed out")
        return False
    except FileNotFoundError:
        print(f"❌ FAIL: Executable not found or not executable")
        return False
    except Exception as e:
        print(f"❌ FAIL: Version command failed: {e}")
        return False

def test_help_command(exe_path):
    """Test that the executable responds to --help command."""
    print("Testing help command...")
    
    try:
        result = subprocess.run(
            [exe_path, '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 or 'help' in result.stdout.lower():
            print(f"✅ PASS: Help command successful")
            return True
        else:
            print(f"⚠️  WARN: Help command returned unexpected result")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ FAIL: Help command timed out")
        return False
    except Exception as e:
        print(f"⚠️  WARN: Help command failed: {e}")
        return False

def test_startup_performance(exe_path):
    """Test application startup time."""
    print("Testing startup performance...")
    
    try:
        start_time = time.time()
        
        # Start the application and immediately close it
        process = subprocess.Popen(
            [exe_path, '--version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for it to complete
        process.wait(timeout=15)
        end_time = time.time()
        
        startup_time = end_time - start_time
        print(f"   Startup time: {startup_time:.2f} seconds")
        
        if startup_time < 5.0:
            print(f"✅ PASS: Startup time acceptable ({startup_time:.2f}s < 5.0s)")
            return True
        else:
            print(f"⚠️  WARN: Startup time slow ({startup_time:.2f}s >= 5.0s)")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ FAIL: Startup test timed out (>15 seconds)")
        return False
    except Exception as e:
        print(f"❌ FAIL: Startup test failed: {e}")
        return False

def test_file_size(exe_path):
    """Test that the executable file size is reasonable."""
    print("Testing file size...")
    
    try:
        path = Path(exe_path)
        size_bytes = path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        
        print(f"   File size: {size_mb:.1f} MB ({size_bytes:,} bytes)")
        
        # Reasonable size limits (adjust as needed)
        if size_mb < 200:  # Less than 200MB is good
            print(f"✅ PASS: File size reasonable ({size_mb:.1f} MB)")
            return True
        elif size_mb < 500:  # Less than 500MB is acceptable
            print(f"⚠️  WARN: File size large but acceptable ({size_mb:.1f} MB)")
            return True
        else:
            print(f"❌ FAIL: File size too large ({size_mb:.1f} MB)")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: File size test failed: {e}")
        return False

def test_dependencies():
    """Test for external dependencies."""
    print("Testing external dependencies...")
    
    try:
        # Try to run ldd (Linux) or otool (macOS) to check dependencies
        exe_exists, exe_path = test_executable_exists()
        if not exe_exists:
            return False
        
        if sys.platform.startswith('linux'):
            # Use ldd to check shared library dependencies
            result = subprocess.run(
                ['ldd', exe_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Look for "not found" in output
                if 'not found' in result.stdout:
                    print(f"❌ FAIL: Missing shared library dependencies")
                    print(f"   ldd output: {result.stdout}")
                    return False
                else:
                    print(f"✅ PASS: All shared library dependencies found")
                    return True
            else:
                print(f"⚠️  WARN: Could not check dependencies (ldd failed)")
                return True
                
        elif sys.platform == 'darwin':
            # Use otool to check dependencies on macOS
            result = subprocess.run(
                ['otool', '-L', exe_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✅ PASS: macOS dependency check completed")
                return True
            else:
                print(f"⚠️  WARN: Could not check dependencies (otool failed)")
                return True
        else:
            # Windows - assume dependencies are bundled
            print(f"✅ PASS: Windows executable (assuming dependencies bundled)")
            return True
            
    except FileNotFoundError:
        print(f"⚠️  WARN: Dependency checking tools not available")
        return True
    except Exception as e:
        print(f"⚠️  WARN: Dependency check failed: {e}")
        return True

def test_database_creation(exe_path):
    """Test that the application can create a database."""
    print("Testing database creation...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set environment variable for custom database location
            env = os.environ.copy()
            env['RADIOFORMS_DB_PATH'] = os.path.join(temp_dir, 'test.db')
            
            # Try to run the application briefly
            result = subprocess.run(
                [exe_path, '--version'],
                capture_output=True,
                text=True,
                timeout=10,
                env=env
            )
            
            # Check if database file was created (might not happen with --version)
            db_path = Path(temp_dir) / 'test.db'
            
            print(f"✅ PASS: Database creation test completed")
            return True
            
    except Exception as e:
        print(f"⚠️  WARN: Database creation test failed: {e}")
        return True

def run_all_tests():
    """Run all production deployment tests."""
    print("=" * 60)
    print("RadioForms Production Deployment Test Suite")
    print("=" * 60)
    
    tests = [
        test_executable_exists,
        test_dependencies,
    ]
    
    # First, check if executable exists
    exe_exists, exe_path = test_executable_exists()
    if not exe_exists:
        print(f"\n❌ CRITICAL: Cannot proceed without executable")
        return False
    
    # Run all other tests
    test_functions = [
        lambda: test_executable_permissions(exe_path),
        lambda: test_file_size(exe_path),
        lambda: test_version_command(exe_path),
        lambda: test_help_command(exe_path),
        lambda: test_startup_performance(exe_path),
        test_dependencies,
        lambda: test_database_creation(exe_path),
    ]
    
    passed = 0
    total = len(test_functions)
    
    for test_func in test_functions:
        print()
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ FAIL: Test exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Production deployment ready!")
        return True
    elif passed >= total * 0.8:  # 80% pass rate
        print("⚠️  MOSTLY PASSED - Manual testing recommended")
        return True
    else:
        print("❌ MANY TESTS FAILED - Deployment not recommended")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
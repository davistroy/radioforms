#!/usr/bin/env python3
"""Basic functionality test without GUI.

This test verifies the application structure works correctly
without requiring a display or GUI environment.
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing module imports...")
    
    try:
        import src.main
        print("✅ src.main imported successfully")
        
        import src.app.application
        print("✅ src.app.application imported successfully")
        
        import src.ui.main_window
        print("✅ src.ui.main_window imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_application_without_gui():
    """Test application functionality without GUI."""
    print("\nTesting application logic...")
    
    try:
        from src.app.application import Application
        
        # Create application instance
        app = Application(database_path=Path("test.db"), debug=True)
        print("✅ Application instance created")
        
        # Test that it handles no GUI gracefully
        # This should return 0 and not crash
        exit_code = app.run()
        print(f"✅ Application run completed with exit code: {exit_code}")
        
        return exit_code == 0
    except Exception as e:
        print(f"❌ Application error: {e}")
        return False

def test_logging_setup():
    """Test logging configuration."""
    print("\nTesting logging setup...")
    
    try:
        from src.main import setup_logging
        
        setup_logging("DEBUG")
        logger = logging.getLogger("test")
        logger.info("Test log message")
        print("✅ Logging setup working")
        
        return True
    except Exception as e:
        print(f"❌ Logging error: {e}")
        return False

def main():
    """Run all tests."""
    print("RadioForms Basic Functionality Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_logging_setup,
        test_application_without_gui,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Application structure is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
Test script for UX enhancements.

This script validates the UX enhancement functionality including:
- Notification system
- Validation feedback
- Progress indicators
- Keyboard shortcuts
- Auto-save functionality
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, 'src')

def test_ux_imports():
    """Test if UX enhancement imports work."""
    try:
        from ui.ux_enhancements import (
            UXNotificationWidget, UXValidationFeedback, UXProgressIndicator,
            UXKeyboardShortcuts, UXAutoSave, UXEnhancementManager,
            NotificationType, ValidationLevel
        )
        print("✅ UX enhancements imports successful")
        return True
    except ImportError as e:
        print(f"❌ UX enhancements import failed: {e}")
        return False

def test_notification_types():
    """Test notification type enumeration."""
    try:
        from ui.ux_enhancements import NotificationType
        
        # Test all notification types
        types = [
            NotificationType.INFO,
            NotificationType.SUCCESS,
            NotificationType.WARNING,
            NotificationType.ERROR
        ]
        
        print("✅ Notification types available:")
        for ntype in types:
            print(f"   - {ntype.value}")
        
        return True
    except Exception as e:
        print(f"❌ Notification types test failed: {e}")
        return False

def test_validation_levels():
    """Test validation level enumeration."""
    try:
        from ui.ux_enhancements import ValidationLevel
        
        # Test all validation levels
        levels = [
            ValidationLevel.NONE,
            ValidationLevel.ERROR,
            ValidationLevel.WARNING,
            ValidationLevel.SUCCESS,
            ValidationLevel.INFO
        ]
        
        print("✅ Validation levels available:")
        for level in levels:
            print(f"   - {level.value}")
        
        return True
    except Exception as e:
        print(f"❌ Validation levels test failed: {e}")
        return False

def test_auto_save_logic():
    """Test auto-save logic without GUI."""
    try:
        from ui.ux_enhancements import UXAutoSave
        
        # Track save calls
        save_count = 0
        def mock_save():
            nonlocal save_count
            save_count += 1
            print(f"   Mock save called (count: {save_count})")
        
        # Create auto-save with 1-second interval for testing
        auto_save = UXAutoSave(mock_save, interval_seconds=1)
        
        print("✅ Auto-save functionality:")
        print(f"   - Interval: {auto_save.interval_seconds}s")
        print(f"   - Enabled: {auto_save.is_enabled}")
        print(f"   - Has changes: {auto_save.has_changes}")
        
        # Test change tracking
        auto_save.mark_changed()
        print(f"   - After mark_changed(): {auto_save.has_changes}")
        
        auto_save.mark_saved()
        print(f"   - After mark_saved(): {auto_save.has_changes}")
        
        # Test enable/disable
        auto_save.set_enabled(False)
        print(f"   - After disable: {auto_save.is_enabled}")
        
        auto_save.set_enabled(True)
        print(f"   - After enable: {auto_save.is_enabled}")
        
        return True
    except Exception as e:
        print(f"❌ Auto-save test failed: {e}")
        return False

def test_keyboard_shortcuts():
    """Test keyboard shortcuts without GUI."""
    try:
        from ui.ux_enhancements import UXKeyboardShortcuts
        
        # Mock widget for testing
        class MockWidget:
            pass
        
        mock_widget = MockWidget()
        shortcuts = UXKeyboardShortcuts(mock_widget)
        
        print("✅ Keyboard shortcuts functionality:")
        
        # Test getting help
        help_list = shortcuts.get_shortcuts_help()
        print(f"   - Default shortcuts: {len(help_list)}")
        
        for shortcut in help_list[:5]:  # Show first 5
            print(f"     {shortcut['keys']}: {shortcut['description']}")
        
        if len(help_list) > 5:
            print(f"     ... and {len(help_list) - 5} more")
        
        return True
    except Exception as e:
        print(f"❌ Keyboard shortcuts test failed: {e}")
        return False

def test_ux_enhancement_manager():
    """Test UX enhancement manager without GUI."""
    try:
        from ui.ux_enhancements import UXEnhancementManager, NotificationType, ValidationLevel
        
        # Mock main window
        class MockMainWindow:
            def geometry(self):
                class MockRect:
                    def x(self): return 0
                    def y(self): return 0
                    def width(self): return 800
                    def height(self): return 600
                return MockRect()
        
        mock_window = MockMainWindow()
        manager = UXEnhancementManager(mock_window)
        
        print("✅ UX Enhancement Manager:")
        print(f"   - Notifications list: {len(manager.notifications)}")
        print(f"   - Validation widgets: {len(manager.validation_widgets)}")
        
        # Test notification (will be logged since no GUI)
        manager.show_notification("Test notification", NotificationType.INFO)
        print("   - Test notification sent")
        
        return True
    except Exception as e:
        print(f"❌ UX enhancement manager test failed: {e}")
        return False

def main():
    """Main test execution."""
    print("UX Enhancements Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_ux_imports),
        ("Notification Types", test_notification_types),
        ("Validation Levels", test_validation_levels),
        ("Auto-save Logic", test_auto_save_logic),
        ("Keyboard Shortcuts", test_keyboard_shortcuts),
        ("UX Manager", test_ux_enhancement_manager)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            failed += 1
    
    print(f"\n📊 Test Results")
    print("=" * 50)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")
    
    if failed == 0:
        print("\n✅ All UX enhancement tests passed!")
        print("\nUX enhancements are ready for integration with the main application.")
        sys.exit(0)
    else:
        print(f"\n❌ {failed} test(s) failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
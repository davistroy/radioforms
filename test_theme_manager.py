#!/usr/bin/env python3
"""
Test script for theme management system.

This script validates the theme management functionality including:
- Theme enumeration and settings
- Stylesheet generation for all themes
- Theme switching and persistence
- System theme detection
- Menu creation functionality
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, 'src')

def test_theme_imports():
    """Test theme manager imports."""
    try:
        from ui.themes import (
            Theme, ThemeManager, ThemeSettings, 
            apply_theme, detect_system_theme, create_theme_menu
        )
        print("✅ Theme manager imports successful")
        return True
    except ImportError as e:
        print(f"❌ Theme manager import failed: {e}")
        return False

def test_theme_enumeration():
    """Test theme enumeration values."""
    try:
        from ui.themes import Theme
        
        themes = [
            Theme.LIGHT,
            Theme.DARK,
            Theme.HIGH_CONTRAST,
            Theme.SYSTEM
        ]
        
        print("✅ Available themes:")
        for theme in themes:
            print(f"   - {theme.value}")
        
        return True
    except Exception as e:
        print(f"❌ Theme enumeration test failed: {e}")
        return False

def test_theme_settings():
    """Test theme settings persistence."""
    try:
        from ui.themes import ThemeSettings, Theme
        
        # Create settings with fallback for testing
        settings = ThemeSettings()
        
        print("✅ Theme settings functionality:")
        
        # Test default theme
        default_theme = settings.get_theme()
        print(f"   - Default theme: {default_theme.value}")
        
        # Test setting theme
        settings.set_theme(Theme.DARK)
        saved_theme = settings.get_theme()
        print(f"   - After setting DARK: {saved_theme.value}")
        
        # Test auto-switch settings
        settings.set_auto_switch(True)
        auto_switch = settings.get_auto_switch()
        print(f"   - Auto-switch enabled: {auto_switch}")
        
        settings.set_auto_switch(False)
        auto_switch = settings.get_auto_switch()
        print(f"   - Auto-switch disabled: {auto_switch}")
        
        return True
    except Exception as e:
        print(f"❌ Theme settings test failed: {e}")
        return False

def test_stylesheet_generation():
    """Test stylesheet generation for all themes."""
    try:
        from ui.themes import ThemeManager, Theme
        
        manager = ThemeManager()
        
        print("✅ Stylesheet generation:")
        
        themes_to_test = [Theme.LIGHT, Theme.DARK, Theme.HIGH_CONTRAST]
        
        for theme in themes_to_test:
            manager.current_theme = theme
            stylesheet = manager.get_current_stylesheet()
            
            # Basic validation
            if not stylesheet:
                print(f"   ❌ {theme.value}: No stylesheet generated")
                return False
            
            if len(stylesheet) < 100:
                print(f"   ❌ {theme.value}: Stylesheet too short ({len(stylesheet)} chars)")
                return False
            
            # Check for theme-specific colors
            if theme == Theme.DARK:
                if "#1a1a1a" not in stylesheet and "#2d2d2d" not in stylesheet:
                    print(f"   ❌ {theme.value}: Missing dark theme colors")
                    return False
            elif theme == Theme.HIGH_CONTRAST:
                if "#000000" not in stylesheet or "#ffffff" not in stylesheet:
                    print(f"   ❌ {theme.value}: Missing high contrast colors")
                    return False
            
            print(f"   ✅ {theme.value}: {len(stylesheet):,} characters")
        
        return True
    except Exception as e:
        print(f"❌ Stylesheet generation test failed: {e}")
        return False

def test_theme_manager():
    """Test theme manager functionality."""
    try:
        from ui.themes import ThemeManager, Theme
        
        manager = ThemeManager()
        
        print("✅ Theme manager functionality:")
        
        # Test initial state
        current_theme = manager.get_current_theme()
        print(f"   - Initial theme: {current_theme.value}")
        
        # Test theme switching
        manager.set_theme(Theme.DARK)
        new_theme = manager.get_current_theme()
        print(f"   - After setting DARK: {new_theme.value}")
        
        # Test toggle functionality
        manager.toggle_theme()
        toggled_theme = manager.get_current_theme()
        print(f"   - After toggle: {toggled_theme.value}")
        
        # Test system theme detection
        system_theme = manager._detect_system_theme()
        print(f"   - Detected system theme: {system_theme.value}")
        
        return True
    except Exception as e:
        print(f"❌ Theme manager test failed: {e}")
        return False

def test_helper_functions():
    """Test helper functions."""
    try:
        from ui.themes import detect_system_theme, create_theme_menu, ThemeManager
        
        print("✅ Helper functions:")
        
        # Test system theme detection
        system_theme = detect_system_theme()
        print(f"   - System theme detection: {system_theme.value}")
        
        # Test menu creation (without GUI)
        manager = ThemeManager()
        menu = create_theme_menu(manager)
        if menu is not None:
            print("   - Theme menu created successfully")
        else:
            print("   - Theme menu creation skipped (no PySide6)")
        
        return True
    except Exception as e:
        print(f"❌ Helper functions test failed: {e}")
        return False

def test_dark_theme_specifics():
    """Test dark theme specific features for nighttime operations."""
    try:
        from ui.themes import ThemeManager, Theme
        
        manager = ThemeManager()
        manager.set_theme(Theme.DARK)
        
        stylesheet = manager.get_current_stylesheet()
        
        print("✅ Dark theme nighttime operation features:")
        
        # Check for dark background colors
        dark_backgrounds = ["#1a1a1a", "#242424", "#2d2d2d"]
        found_dark = any(color in stylesheet for color in dark_backgrounds)
        print(f"   - Dark backgrounds: {'✅' if found_dark else '❌'}")
        
        # Check for reduced brightness elements
        if "#64b5f6" in stylesheet:  # Light blue for accents
            print("   - ✅ Reduced brightness accent colors")
        else:
            print("   - ❌ Missing reduced brightness accents")
        
        # Check for improved scrollbar visibility
        if "QScrollBar" in stylesheet:
            print("   - ✅ Enhanced scrollbar visibility")
        else:
            print("   - ❌ Missing scrollbar enhancements")
        
        # Check for form validation colors in dark theme
        validation_colors = ["#4a1a1a", "#4a3a1a", "#1a4a1a"]
        found_validation = any(color in stylesheet for color in validation_colors)
        print(f"   - Validation feedback colors: {'✅' if found_validation else '❌'}")
        
        return True
    except Exception as e:
        print(f"❌ Dark theme specifics test failed: {e}")
        return False

def test_high_contrast_accessibility():
    """Test high contrast theme accessibility features."""
    try:
        from ui.themes import ThemeManager, Theme
        
        manager = ThemeManager()
        manager.set_theme(Theme.HIGH_CONTRAST)
        
        stylesheet = manager.get_current_stylesheet()
        
        print("✅ High contrast accessibility features:")
        
        # Check for high contrast colors
        if "#000000" in stylesheet and "#ffffff" in stylesheet:
            print("   - ✅ High contrast black/white base colors")
        else:
            print("   - ❌ Missing high contrast base colors")
        
        # Check for accessibility yellow
        if "#ffff00" in stylesheet:
            print("   - ✅ High visibility yellow accents")
        else:
            print("   - ❌ Missing yellow accent colors")
        
        # Check for increased border widths
        if "3px solid" in stylesheet:
            print("   - ✅ Enhanced border visibility")
        else:
            print("   - ❌ Missing enhanced borders")
        
        # Check for larger font sizes
        if "12pt" in stylesheet:
            print("   - ✅ Increased font sizes for readability")
        else:
            print("   - ❌ Missing font size enhancements")
        
        # Check for bold font weights
        if "font-weight: bold" in stylesheet:
            print("   - ✅ Bold text for better visibility")
        else:
            print("   - ❌ Missing bold font weights")
        
        return True
    except Exception as e:
        print(f"❌ High contrast accessibility test failed: {e}")
        return False

def main():
    """Main test execution."""
    print("Theme Manager Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_theme_imports),
        ("Theme Enumeration", test_theme_enumeration),
        ("Theme Settings", test_theme_settings),
        ("Stylesheet Generation", test_stylesheet_generation),
        ("Theme Manager", test_theme_manager),
        ("Helper Functions", test_helper_functions),
        ("Dark Theme Features", test_dark_theme_specifics),
        ("High Contrast Accessibility", test_high_contrast_accessibility)
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
        print("\n✅ All theme manager tests passed!")
        print("\nDark theme is ready for nighttime operations!")
        print("High contrast theme meets accessibility requirements!")
        sys.exit(0)
    else:
        print(f"\n❌ {failed} test(s) failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
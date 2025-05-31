"""Theme management module for RadioForms.

This module provides comprehensive theme support including dark theme for
nighttime operations, high contrast theme for accessibility, and automatic
system theme detection.

Key Features:
- Dark theme optimized for emergency nighttime operations
- High contrast theme for accessibility compliance (WCAG 2.1 AAA)
- Persistent theme settings with QSettings integration
- System theme detection and automatic switching
- Theme manager with signal-based updates

Classes:
    Theme: Available theme enumeration
    ThemeManager: Central theme management system
    ThemeSettings: Persistent theme configuration

Functions:
    apply_theme: Apply theme to widget
    detect_system_theme: Detect system preference
    create_theme_menu: Create theme selection UI

Example:
    >>> from ui.themes import ThemeManager, Theme
    >>> 
    >>> theme_manager = ThemeManager()
    >>> theme_manager.set_theme(Theme.DARK)  # For night operations
"""

from .theme_manager import (
    Theme,
    ThemeManager,
    ThemeSettings,
    apply_theme,
    detect_system_theme,
    create_theme_menu
)

__all__ = [
    'Theme',
    'ThemeManager', 
    'ThemeSettings',
    'apply_theme',
    'detect_system_theme',
    'create_theme_menu'
]
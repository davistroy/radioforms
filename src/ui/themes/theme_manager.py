"""Theme Management System for RadioForms.

This module provides comprehensive theme management including dark theme support,
system theme detection, and persistent theme settings. Designed for emergency
management environments where nighttime operations require dark themes to
preserve night vision.

Following CLAUDE.md principles:
- Simple theme switching interface
- Accessible design patterns
- System integration where available
- Performance-optimized theme application

Example:
    >>> from src.ui.themes.theme_manager import ThemeManager, Theme
    >>> 
    >>> # Initialize theme manager
    >>> theme_manager = ThemeManager()
    >>> 
    >>> # Apply dark theme
    >>> theme_manager.set_theme(Theme.DARK)
    >>> 
    >>> # Get theme stylesheet
    >>> stylesheet = theme_manager.get_current_stylesheet()

Classes:
    Theme: Enumeration of available themes
    ThemeManager: Central theme management system
    ThemeSettings: Persistent theme settings storage

Functions:
    apply_theme: Apply theme to a widget hierarchy
    detect_system_theme: Detect system preference (where available)
    create_theme_menu: Create theme selection menu for UI

Notes:
    This implementation focuses on emergency management use cases where
    dark themes are critical for nighttime operations and eye strain
    reduction during extended incident response periods.
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Callable, Any
import json

# Conditional import for PySide6
try:
    from PySide6.QtWidgets import (
        QWidget, QApplication, QMenu, QActionGroup, QSystemTrayIcon
    )
    from PySide6.QtCore import QSettings, QObject, Signal, Qt, QTimer
    from PySide6.QtGui import QAction, QPalette, QColor, QIcon
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    
    # Create mock classes that can be inherited from
    class QWidget:
        def __init__(self, parent=None): pass
        def setStyleSheet(self, stylesheet): pass
        def update(self): pass
        def isWidgetType(self): return True
    
    class QObject:
        def __init__(self, parent=None): pass
    
    Signal = lambda *args: None


logger = logging.getLogger(__name__)


class Theme(Enum):
    """Available application themes."""
    LIGHT = "light"
    DARK = "dark"
    HIGH_CONTRAST = "high_contrast"
    SYSTEM = "system"  # Follow system preference


class ThemeSettings:
    """Persistent theme settings storage.
    
    Manages theme preferences with automatic persistence and validation.
    Integrates with QSettings for platform-appropriate storage.
    """
    
    def __init__(self, settings_path: Optional[Path] = None):
        """Initialize theme settings.
        
        Args:
            settings_path: Optional custom settings file path.
        """
        self.settings_path = settings_path
        
        if PYSIDE6_AVAILABLE:
            if settings_path:
                self.settings = QSettings(str(settings_path), QSettings.IniFormat)
            else:
                self.settings = QSettings("RadioForms", "ThemeSettings")
        else:
            # Fallback for when PySide6 not available
            self.settings = None
            self._fallback_settings = {}
        
        logger.debug("ThemeSettings initialized")
    
    def get_theme(self) -> Theme:
        """Get the currently selected theme.
        
        Returns:
            Theme: The selected theme, defaults to LIGHT if not set.
        """
        if PYSIDE6_AVAILABLE and self.settings:
            theme_value = self.settings.value("theme", Theme.LIGHT.value)
        else:
            theme_value = self._fallback_settings.get("theme", Theme.LIGHT.value)
        
        try:
            return Theme(theme_value)
        except ValueError:
            logger.warning(f"Invalid theme value '{theme_value}', defaulting to LIGHT")
            return Theme.LIGHT
    
    def set_theme(self, theme: Theme) -> None:
        """Set the selected theme.
        
        Args:
            theme: Theme to set as current.
        """
        if PYSIDE6_AVAILABLE and self.settings:
            self.settings.setValue("theme", theme.value)
            self.settings.sync()
        else:
            self._fallback_settings["theme"] = theme.value
        
        logger.debug(f"Theme set to: {theme.value}")
    
    def get_auto_switch(self) -> bool:
        """Get whether automatic theme switching is enabled.
        
        Returns:
            bool: True if auto-switching is enabled.
        """
        if PYSIDE6_AVAILABLE and self.settings:
            return self.settings.value("auto_switch", False, type=bool)
        else:
            return self._fallback_settings.get("auto_switch", False)
    
    def set_auto_switch(self, enabled: bool) -> None:
        """Set automatic theme switching.
        
        Args:
            enabled: Whether to enable automatic switching.
        """
        if PYSIDE6_AVAILABLE and self.settings:
            self.settings.setValue("auto_switch", enabled)
            self.settings.sync()
        else:
            self._fallback_settings["auto_switch"] = enabled
        
        logger.debug(f"Auto-switch set to: {enabled}")


class ThemeManager(QObject):
    """Central theme management system.
    
    Provides theme switching, system theme detection, and persistent settings.
    Handles theme application across the entire application widget hierarchy.
    
    Signals:
        theme_changed: Emitted when theme changes (theme: Theme)
    """
    
    theme_changed = Signal(Theme) if PYSIDE6_AVAILABLE else Signal()
    
    def __init__(self, parent=None):
        """Initialize theme manager.
        
        Args:
            parent: Parent QObject for Qt object hierarchy.
        """
        super().__init__(parent)
        
        self.settings = ThemeSettings()
        self.current_theme = self.settings.get_theme()
        self.stylesheets = self._load_stylesheets()
        self.widgets: list = []  # Track widgets for theme application
        
        # Auto-switch timer for system theme detection
        if PYSIDE6_AVAILABLE:
            self.auto_switch_timer = QTimer(self)
            self.auto_switch_timer.timeout.connect(self._check_system_theme)
            if self.settings.get_auto_switch():
                self.auto_switch_timer.start(30000)  # Check every 30 seconds
        
        logger.debug(f"ThemeManager initialized with theme: {self.current_theme.value}")
    
    def _load_stylesheets(self) -> Dict[Theme, str]:
        """Load theme stylesheets.
        
        Returns:
            Dict[Theme, str]: Mapping of themes to their stylesheet content.
        """
        stylesheets = {}
        
        # Light theme (default)
        stylesheets[Theme.LIGHT] = self._create_light_stylesheet()
        
        # Dark theme for nighttime operations
        stylesheets[Theme.DARK] = self._create_dark_stylesheet()
        
        # High contrast theme for accessibility
        stylesheets[Theme.HIGH_CONTRAST] = self._create_high_contrast_stylesheet()
        
        return stylesheets
    
    def _create_light_stylesheet(self) -> str:
        """Create light theme stylesheet.
        
        Returns:
            str: CSS stylesheet for light theme.
        """
        return """
        /* RadioForms Light Theme */
        QMainWindow {
            background-color: #ffffff;
            color: #212121;
        }
        
        QWidget {
            background-color: #ffffff;
            color: #212121;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
        }
        
        /* Form Areas */
        QTabWidget::pane {
            border: 1px solid #e0e0e0;
            background-color: #fafafa;
        }
        
        QTabBar::tab {
            background-color: #f5f5f5;
            color: #424242;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-bottom: none;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #ffffff;
            color: #1976d2;
            border-bottom: 2px solid #1976d2;
        }
        
        QTabBar::tab:hover {
            background-color: #e3f2fd;
        }
        
        /* Input Fields */
        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {
            background-color: #ffffff;
            color: #212121;
            border: 2px solid #e0e0e0;
            border-radius: 4px;
            padding: 8px;
            font-size: 11pt;
        }
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
            border: 2px solid #1976d2;
            background-color: #ffffff;
        }
        
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
            background-color: #f5f5f5;
            color: #9e9e9e;
        }
        
        /* Buttons */
        QPushButton {
            background-color: #1976d2;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 10pt;
        }
        
        QPushButton:hover {
            background-color: #1565c0;
        }
        
        QPushButton:pressed {
            background-color: #0d47a1;
        }
        
        QPushButton:disabled {
            background-color: #e0e0e0;
            color: #9e9e9e;
        }
        
        /* Secondary buttons */
        QPushButton[class="secondary"] {
            background-color: #ffffff;
            color: #1976d2;
            border: 2px solid #1976d2;
        }
        
        QPushButton[class="secondary"]:hover {
            background-color: #e3f2fd;
        }
        
        /* Tables */
        QTableWidget {
            background-color: #ffffff;
            alternate-background-color: #f8f9fa;
            gridline-color: #e0e0e0;
            border: 1px solid #e0e0e0;
        }
        
        QHeaderView::section {
            background-color: #f5f5f5;
            color: #424242;
            border: 1px solid #e0e0e0;
            padding: 8px;
            font-weight: bold;
        }
        
        QTableWidget::item:selected {
            background-color: #e3f2fd;
            color: #1976d2;
        }
        
        /* Status and Progress */
        QStatusBar {
            background-color: #f5f5f5;
            color: #424242;
            border-top: 1px solid #e0e0e0;
        }
        
        QProgressBar {
            border: 2px solid #e0e0e0;
            border-radius: 4px;
            text-align: center;
            background-color: #f5f5f5;
        }
        
        QProgressBar::chunk {
            background-color: #4caf50;
            border-radius: 2px;
        }
        
        /* Menus */
        QMenuBar {
            background-color: #fafafa;
            color: #212121;
            border-bottom: 1px solid #e0e0e0;
        }
        
        QMenuBar::item:selected {
            background-color: #e3f2fd;
            color: #1976d2;
        }
        
        QMenu {
            background-color: #ffffff;
            color: #212121;
            border: 1px solid #e0e0e0;
        }
        
        QMenu::item:selected {
            background-color: #e3f2fd;
            color: #1976d2;
        }
        """
    
    def _create_dark_stylesheet(self) -> str:
        """Create dark theme stylesheet for nighttime operations.
        
        Returns:
            str: CSS stylesheet for dark theme.
        """
        return """
        /* RadioForms Dark Theme - Optimized for Nighttime Operations */
        QMainWindow {
            background-color: #1a1a1a;
            color: #e0e0e0;
        }
        
        QWidget {
            background-color: #1a1a1a;
            color: #e0e0e0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
        }
        
        /* Form Areas */
        QTabWidget::pane {
            border: 1px solid #404040;
            background-color: #242424;
        }
        
        QTabBar::tab {
            background-color: #2d2d2d;
            color: #bdbdbd;
            padding: 8px 16px;
            border: 1px solid #404040;
            border-bottom: none;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #1a1a1a;
            color: #64b5f6;
            border-bottom: 2px solid #64b5f6;
        }
        
        QTabBar::tab:hover {
            background-color: #1e3a5f;
        }
        
        /* Input Fields */
        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 2px solid #404040;
            border-radius: 4px;
            padding: 8px;
            font-size: 11pt;
        }
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
            border: 2px solid #64b5f6;
            background-color: #2d2d2d;
        }
        
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
            background-color: #1f1f1f;
            color: #666666;
        }
        
        /* Buttons */
        QPushButton {
            background-color: #1976d2;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 10pt;
        }
        
        QPushButton:hover {
            background-color: #64b5f6;
        }
        
        QPushButton:pressed {
            background-color: #1565c0;
        }
        
        QPushButton:disabled {
            background-color: #404040;
            color: #666666;
        }
        
        /* Secondary buttons */
        QPushButton[class="secondary"] {
            background-color: #2d2d2d;
            color: #64b5f6;
            border: 2px solid #64b5f6;
        }
        
        QPushButton[class="secondary"]:hover {
            background-color: #1e3a5f;
        }
        
        /* Tables */
        QTableWidget {
            background-color: #2d2d2d;
            alternate-background-color: #242424;
            gridline-color: #404040;
            border: 1px solid #404040;
            color: #e0e0e0;
        }
        
        QHeaderView::section {
            background-color: #1f1f1f;
            color: #bdbdbd;
            border: 1px solid #404040;
            padding: 8px;
            font-weight: bold;
        }
        
        QTableWidget::item:selected {
            background-color: #1e3a5f;
            color: #64b5f6;
        }
        
        /* Status and Progress */
        QStatusBar {
            background-color: #1f1f1f;
            color: #bdbdbd;
            border-top: 1px solid #404040;
        }
        
        QProgressBar {
            border: 2px solid #404040;
            border-radius: 4px;
            text-align: center;
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        
        QProgressBar::chunk {
            background-color: #4caf50;
            border-radius: 2px;
        }
        
        /* Menus */
        QMenuBar {
            background-color: #1f1f1f;
            color: #e0e0e0;
            border-bottom: 1px solid #404040;
        }
        
        QMenuBar::item:selected {
            background-color: #1e3a5f;
            color: #64b5f6;
        }
        
        QMenu {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #404040;
        }
        
        QMenu::item:selected {
            background-color: #1e3a5f;
            color: #64b5f6;
        }
        
        /* Scrollbars for better visibility in dark theme */
        QScrollBar:vertical {
            background-color: #2d2d2d;
            width: 12px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #606060;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #64b5f6;
        }
        
        QScrollBar:horizontal {
            background-color: #2d2d2d;
            height: 12px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #606060;
            border-radius: 6px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #64b5f6;
        }
        
        /* Form validation feedback in dark theme */
        QWidget[class="validation-error"] {
            background-color: #4a1a1a;
            border: 1px solid #d32f2f;
        }
        
        QWidget[class="validation-warning"] {
            background-color: #4a3a1a;
            border: 1px solid #f57c00;
        }
        
        QWidget[class="validation-success"] {
            background-color: #1a4a1a;
            border: 1px solid #388e3c;
        }
        """
    
    def _create_high_contrast_stylesheet(self) -> str:
        """Create high contrast theme for accessibility.
        
        Returns:
            str: CSS stylesheet for high contrast theme.
        """
        return """
        /* RadioForms High Contrast Theme - WCAG 2.1 AAA Compliant */
        QMainWindow {
            background-color: #000000;
            color: #ffffff;
        }
        
        QWidget {
            background-color: #000000;
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            font-size: 12pt;
            font-weight: bold;
        }
        
        /* Form Areas */
        QTabWidget::pane {
            border: 3px solid #ffffff;
            background-color: #000000;
        }
        
        QTabBar::tab {
            background-color: #000000;
            color: #ffffff;
            padding: 12px 20px;
            border: 3px solid #ffffff;
            border-bottom: none;
            margin-right: 4px;
            font-size: 12pt;
            font-weight: bold;
        }
        
        QTabBar::tab:selected {
            background-color: #ffff00;
            color: #000000;
            border: 3px solid #ffffff;
        }
        
        QTabBar::tab:hover {
            background-color: #ffff00;
            color: #000000;
        }
        
        /* Input Fields */
        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {
            background-color: #ffffff;
            color: #000000;
            border: 3px solid #000000;
            border-radius: 0px;
            padding: 12px;
            font-size: 12pt;
            font-weight: bold;
        }
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
            border: 3px solid #ffff00;
            background-color: #ffffff;
            color: #000000;
        }
        
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
            background-color: #808080;
            color: #000000;
        }
        
        /* Buttons */
        QPushButton {
            background-color: #ffff00;
            color: #000000;
            border: 3px solid #000000;
            border-radius: 0px;
            padding: 12px 24px;
            font-weight: bold;
            font-size: 12pt;
        }
        
        QPushButton:hover, QPushButton:focus {
            background-color: #ffffff;
            color: #000000;
            border: 3px solid #ffff00;
        }
        
        QPushButton:pressed {
            background-color: #000000;
            color: #ffffff;
            border: 3px solid #ffffff;
        }
        
        QPushButton:disabled {
            background-color: #808080;
            color: #000000;
            border: 3px solid #000000;
        }
        
        /* Tables */
        QTableWidget {
            background-color: #ffffff;
            color: #000000;
            gridline-color: #000000;
            border: 3px solid #000000;
            font-size: 11pt;
            font-weight: bold;
        }
        
        QHeaderView::section {
            background-color: #000000;
            color: #ffffff;
            border: 3px solid #ffffff;
            padding: 12px;
            font-weight: bold;
            font-size: 11pt;
        }
        
        QTableWidget::item:selected {
            background-color: #ffff00;
            color: #000000;
        }
        
        /* Status and Progress */
        QStatusBar {
            background-color: #000000;
            color: #ffffff;
            border-top: 3px solid #ffffff;
            font-size: 11pt;
            font-weight: bold;
        }
        
        QProgressBar {
            border: 3px solid #ffffff;
            border-radius: 0px;
            text-align: center;
            background-color: #000000;
            color: #ffffff;
            font-size: 11pt;
            font-weight: bold;
        }
        
        QProgressBar::chunk {
            background-color: #ffff00;
        }
        
        /* Menus */
        QMenuBar {
            background-color: #000000;
            color: #ffffff;
            border-bottom: 3px solid #ffffff;
            font-size: 12pt;
            font-weight: bold;
        }
        
        QMenuBar::item:selected, QMenuBar::item:focus {
            background-color: #ffff00;
            color: #000000;
        }
        
        QMenu {
            background-color: #000000;
            color: #ffffff;
            border: 3px solid #ffffff;
            font-size: 11pt;
            font-weight: bold;
        }
        
        QMenu::item:selected, QMenu::item:focus {
            background-color: #ffff00;
            color: #000000;
        }
        
        /* Scrollbars */
        QScrollBar:vertical {
            background-color: #000000;
            width: 20px;
            border: 3px solid #ffffff;
        }
        
        QScrollBar::handle:vertical {
            background-color: #ffffff;
            border: 2px solid #000000;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #ffff00;
        }
        """
    
    def get_current_theme(self) -> Theme:
        """Get the currently active theme.
        
        Returns:
            Theme: Current theme.
        """
        return self.current_theme
    
    def get_current_stylesheet(self) -> str:
        """Get the stylesheet for the current theme.
        
        Returns:
            str: CSS stylesheet content.
        """
        theme = self.current_theme
        if theme == Theme.SYSTEM:
            theme = self._detect_system_theme()
        
        return self.stylesheets.get(theme, self.stylesheets[Theme.LIGHT])
    
    def set_theme(self, theme: Theme) -> None:
        """Set and apply a new theme.
        
        Args:
            theme: Theme to apply.
        """
        if theme == self.current_theme:
            return
        
        old_theme = self.current_theme
        self.current_theme = theme
        
        # Save to settings
        self.settings.set_theme(theme)
        
        # Apply theme to application
        self._apply_theme()
        
        # Emit signal
        if PYSIDE6_AVAILABLE and self.theme_changed:
            self.theme_changed.emit(theme)
        
        logger.info(f"Theme changed from {old_theme.value} to {theme.value}")
    
    def _apply_theme(self) -> None:
        """Apply current theme to the application."""
        if not PYSIDE6_AVAILABLE:
            return
        
        stylesheet = self.get_current_stylesheet()
        
        # Apply to QApplication if available
        app = QApplication.instance()
        if app:
            app.setStyleSheet(stylesheet)
        
        # Apply to tracked widgets
        for widget in self.widgets:
            if widget and not widget.isWidgetType():
                continue
            try:
                widget.setStyleSheet(stylesheet)
                widget.update()
            except RuntimeError:
                # Widget was deleted, remove from tracking
                self.widgets.remove(widget)
    
    def register_widget(self, widget: QWidget) -> None:
        """Register a widget for theme application.
        
        Args:
            widget: Widget to track for theme changes.
        """
        if widget not in self.widgets:
            self.widgets.append(widget)
    
    def _detect_system_theme(self) -> Theme:
        """Detect system theme preference.
        
        Returns:
            Theme: Detected system theme, defaults to LIGHT.
        """
        if not PYSIDE6_AVAILABLE:
            return Theme.LIGHT
        
        try:
            # Try to detect system theme through QApplication palette
            app = QApplication.instance()
            if app:
                palette = app.palette()
                window_color = palette.color(QPalette.Window)
                # Simple heuristic: if window is dark, assume dark theme
                if window_color.lightness() < 128:
                    return Theme.DARK
        except Exception as e:
            logger.debug(f"System theme detection failed: {e}")
        
        return Theme.LIGHT
    
    def _check_system_theme(self) -> None:
        """Check if system theme has changed (for auto-switching)."""
        if self.current_theme != Theme.SYSTEM:
            return
        
        # Re-apply theme to pick up system changes
        self._apply_theme()
    
    def toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        if self.current_theme == Theme.LIGHT:
            self.set_theme(Theme.DARK)
        else:
            self.set_theme(Theme.LIGHT)
    
    def enable_auto_switch(self, enabled: bool) -> None:
        """Enable or disable automatic system theme switching.
        
        Args:
            enabled: Whether to enable auto-switching.
        """
        self.settings.set_auto_switch(enabled)
        
        if PYSIDE6_AVAILABLE:
            if enabled:
                self.auto_switch_timer.start(30000)
            else:
                self.auto_switch_timer.stop()
        
        logger.debug(f"Auto-switch {'enabled' if enabled else 'disabled'}")


def apply_theme(widget: QWidget, theme: Theme) -> None:
    """Apply theme to a specific widget.
    
    Args:
        widget: Widget to apply theme to.
        theme: Theme to apply.
    """
    if not PYSIDE6_AVAILABLE:
        return
    
    # Create temporary theme manager to get stylesheet
    temp_manager = ThemeManager()
    temp_manager.current_theme = theme
    stylesheet = temp_manager.get_current_stylesheet()
    
    widget.setStyleSheet(stylesheet)
    widget.update()


def detect_system_theme() -> Theme:
    """Detect system theme preference.
    
    Returns:
        Theme: Detected system theme.
    """
    manager = ThemeManager()
    return manager._detect_system_theme()


def create_theme_menu(theme_manager: ThemeManager, parent=None) -> 'QMenu':
    """Create theme selection menu.
    
    Args:
        theme_manager: ThemeManager instance.
        parent: Parent widget for the menu.
        
    Returns:
        QMenu: Theme selection menu.
    """
    if not PYSIDE6_AVAILABLE:
        return None
    
    from PySide6.QtWidgets import QMenu
    
    menu = QMenu("Theme", parent)
    action_group = QActionGroup(menu)
    
    themes = [
        (Theme.LIGHT, "Light Theme"),
        (Theme.DARK, "Dark Theme (Night Ops)"),
        (Theme.HIGH_CONTRAST, "High Contrast"),
        (Theme.SYSTEM, "Follow System")
    ]
    
    for theme, label in themes:
        action = QAction(label, menu)
        action.setCheckable(True)
        action.setChecked(theme == theme_manager.get_current_theme())
        action.triggered.connect(lambda checked, t=theme: theme_manager.set_theme(t))
        
        action_group.addAction(action)
        menu.addAction(action)
    
    # Connect theme manager signal to update menu
    if theme_manager.theme_changed:
        def update_menu(new_theme: Theme):
            for action in action_group.actions():
                # Find the action for this theme
                for theme, label in themes:
                    if action.text() == label:
                        action.setChecked(theme == new_theme)
                        break
        
        theme_manager.theme_changed.connect(update_menu)
    
    return menu
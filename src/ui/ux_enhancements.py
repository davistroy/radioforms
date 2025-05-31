"""User Experience Enhancements for RadioForms.

This module provides enhanced user experience features including:
- Improved error messages and validation feedback
- Better visual feedback for operations
- Keyboard shortcuts and accessibility
- Auto-save functionality
- Progress indicators and notifications

Following CLAUDE.md principles of simple, user-focused design.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from enum import Enum

# Conditional import for PySide6
try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QMessageBox, QProgressBar, QSystemTrayIcon, QStatusBar,
        QToolTip, QGraphicsEffect, QGraphicsDropShadowEffect,
        QFrame, QSizePolicy, QApplication
    )
    from PySide6.QtCore import (
        Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve,
        QRect, QEvent, QObject, QSettings
    )
    from PySide6.QtGui import (
        QIcon, QPixmap, QPalette, QColor, QFont, QKeySequence,
        QShortcut, QPainter, QLinearGradient
    )
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    QWidget = QLabel = QPushButton = QMessageBox = object
    QTimer = QRect = Signal = Qt = QShortcut = QKeySequence = object


logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of user notifications."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class ValidationLevel(Enum):
    """Validation feedback levels."""
    NONE = "none"
    ERROR = "error"
    WARNING = "warning"
    SUCCESS = "success"
    INFO = "info"


class UXNotificationWidget(QWidget):
    """Enhanced notification widget with animations and better styling.
    
    Provides slide-in notifications with auto-dismiss, different types,
    and smooth animations for better user feedback.
    """
    
    dismissed = Signal() if PYSIDE6_AVAILABLE else None
    
    def __init__(self, message: str, notification_type: NotificationType = NotificationType.INFO, 
                 auto_dismiss: int = 5000, parent=None):
        """Initialize notification widget.
        
        Args:
            message: Notification message text.
            notification_type: Type of notification for styling.
            auto_dismiss: Auto-dismiss timeout in milliseconds (0 = manual only).
            parent: Parent widget.
        """
        super().__init__(parent)
        
        if not PYSIDE6_AVAILABLE:
            return
        
        self.message = message
        self.notification_type = notification_type
        self.auto_dismiss = auto_dismiss
        
        self._setup_ui()
        self._setup_styling()
        self._setup_animations()
        
        # Auto-dismiss timer
        if auto_dismiss > 0:
            QTimer.singleShot(auto_dismiss, self._start_hide_animation)
    
    def _setup_ui(self):
        """Set up the notification UI."""
        self.setFixedHeight(60)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)
        
        # Icon label (could be enhanced with actual icons)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        layout.addWidget(self.icon_label)
        
        # Message label
        self.message_label = QLabel(self.message)
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label, 1)
        
        # Close button
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(24, 24)
        self.close_button.clicked.connect(self._start_hide_animation)
        layout.addWidget(self.close_button)
    
    def _setup_styling(self):
        """Apply styling based on notification type."""
        colors = {
            NotificationType.INFO: ("#e3f2fd", "#1976d2", "#0d47a1"),
            NotificationType.SUCCESS: ("#e8f5e8", "#4caf50", "#2e7d32"),
            NotificationType.WARNING: ("#fff3e0", "#ff9800", "#ef6c00"),
            NotificationType.ERROR: ("#ffebee", "#f44336", "#c62828")
        }
        
        bg_color, border_color, text_color = colors.get(
            self.notification_type, colors[NotificationType.INFO]
        )
        
        style = f"""
        UXNotificationWidget {{
            background-color: {bg_color};
            border: 2px solid {border_color};
            border-radius: 8px;
            color: {text_color};
        }}
        QLabel {{
            color: {text_color};
            font-weight: bold;
        }}
        QPushButton {{
            background-color: transparent;
            border: none;
            color: {text_color};
            font-weight: bold;
            font-size: 16px;
        }}
        QPushButton:hover {{
            background-color: rgba(0, 0, 0, 0.1);
            border-radius: 12px;
        }}
        """
        
        self.setStyleSheet(style)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)
    
    def _setup_animations(self):
        """Set up slide animations."""
        self.show_animation = QPropertyAnimation(self, b"geometry")
        self.show_animation.setDuration(300)
        self.show_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.hide_animation = QPropertyAnimation(self, b"geometry")
        self.hide_animation.setDuration(300)
        self.hide_animation.setEasingCurve(QEasingCurve.InCubic)
        self.hide_animation.finished.connect(self._on_hide_finished)
    
    def show_notification(self, parent_rect: QRect):
        """Show notification with slide animation.
        
        Args:
            parent_rect: Parent widget rectangle for positioning.
        """
        # Position at top of parent
        target_rect = QRect(
            parent_rect.x() + 10,
            parent_rect.y() + 10,
            parent_rect.width() - 20,
            60
        )
        
        # Start above parent (hidden)
        start_rect = QRect(
            target_rect.x(),
            parent_rect.y() - 60,
            target_rect.width(),
            60
        )
        
        self.setGeometry(start_rect)
        self.show()
        
        # Animate to target position
        self.show_animation.setStartValue(start_rect)
        self.show_animation.setEndValue(target_rect)
        self.show_animation.start()
    
    def _start_hide_animation(self):
        """Start hide animation."""
        current_rect = self.geometry()
        target_rect = QRect(
            current_rect.x(),
            current_rect.y() - 70,
            current_rect.width(),
            60
        )
        
        self.hide_animation.setStartValue(current_rect)
        self.hide_animation.setEndValue(target_rect)
        self.hide_animation.start()
    
    def _on_hide_finished(self):
        """Handle hide animation completion."""
        self.hide()
        if self.dismissed:
            self.dismissed.emit()


class UXValidationFeedback(QWidget):
    """Enhanced validation feedback widget with visual indicators."""
    
    def __init__(self, parent=None):
        """Initialize validation feedback widget."""
        super().__init__(parent)
        
        if not PYSIDE6_AVAILABLE:
            return
        
        self._setup_ui()
        self._current_level = ValidationLevel.NONE
    
    def _setup_ui(self):
        """Set up the validation feedback UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Status indicator
        self.indicator = QLabel()
        self.indicator.setFixedSize(12, 12)
        layout.addWidget(self.indicator)
        
        # Message label
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label, 1)
        
        self.hide()
    
    def set_validation_state(self, level: ValidationLevel, message: str = ""):
        """Set validation state with visual feedback.
        
        Args:
            level: Validation level for styling.
            message: Validation message to display.
        """
        self._current_level = level
        
        if level == ValidationLevel.NONE:
            self.hide()
            return
        
        # Update message
        self.message_label.setText(message)
        
        # Update styling based on level
        colors = {
            ValidationLevel.ERROR: ("#f44336", "#ffebee"),
            ValidationLevel.WARNING: ("#ff9800", "#fff3e0"),
            ValidationLevel.SUCCESS: ("#4caf50", "#e8f5e8"),
            ValidationLevel.INFO: ("#2196f3", "#e3f2fd")
        }
        
        if level in colors:
            color, bg_color = colors[level]
            
            # Style the indicator
            self.indicator.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    border-radius: 6px;
                }}
            """)
            
            # Style the widget
            self.setStyleSheet(f"""
                UXValidationFeedback {{
                    background-color: {bg_color};
                    border: 1px solid {color};
                    border-radius: 4px;
                }}
                QLabel {{
                    color: {color};
                    font-size: 11px;
                }}
            """)
        
        self.show()
    
    def clear_validation(self):
        """Clear validation state."""
        self.set_validation_state(ValidationLevel.NONE)


class UXProgressIndicator(QWidget):
    """Enhanced progress indicator with better visual feedback."""
    
    def __init__(self, parent=None):
        """Initialize progress indicator."""
        super().__init__(parent)
        
        if not PYSIDE6_AVAILABLE:
            return
        
        self._setup_ui()
        self._operation_text = ""
    
    def _setup_ui(self):
        """Set up the progress indicator UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Operation label
        self.operation_label = QLabel()
        self.operation_label.setAlignment(Qt.AlignCenter)
        self.operation_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.operation_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        self.hide()
    
    def start_operation(self, operation_text: str, total_steps: int = 0):
        """Start progress indication for an operation.
        
        Args:
            operation_text: Description of the operation.
            total_steps: Total number of steps (0 for indeterminate).
        """
        self._operation_text = operation_text
        self.operation_label.setText(operation_text)
        
        if total_steps > 0:
            self.progress_bar.setRange(0, total_steps)
            self.progress_bar.setValue(0)
        else:
            self.progress_bar.setRange(0, 0)  # Indeterminate
        
        self.status_label.setText("Starting...")
        self.show()
    
    def update_progress(self, current_step: int, status_text: str = ""):
        """Update progress indication.
        
        Args:
            current_step: Current step number.
            status_text: Optional status description.
        """
        self.progress_bar.setValue(current_step)
        
        if status_text:
            self.status_label.setText(status_text)
        else:
            total = self.progress_bar.maximum()
            if total > 0:
                percentage = int((current_step / total) * 100)
                self.status_label.setText(f"Step {current_step} of {total} ({percentage}%)")
    
    def finish_operation(self, success: bool = True, message: str = ""):
        """Finish progress indication.
        
        Args:
            success: Whether operation completed successfully.
            message: Optional completion message.
        """
        if success:
            self.progress_bar.setValue(self.progress_bar.maximum())
            self.status_label.setText(message or "Completed successfully")
            self.status_label.setStyleSheet("color: #27ae60; font-size: 11px; font-weight: bold;")
        else:
            self.status_label.setText(message or "Operation failed")
            self.status_label.setStyleSheet("color: #e74c3c; font-size: 11px; font-weight: bold;")
        
        # Auto-hide after delay
        QTimer.singleShot(2000, self.hide)


class UXKeyboardShortcuts:
    """Enhanced keyboard shortcuts manager."""
    
    def __init__(self, parent_widget: QWidget):
        """Initialize keyboard shortcuts manager.
        
        Args:
            parent_widget: Parent widget to attach shortcuts to.
        """
        self.parent = parent_widget
        self.shortcuts: Dict[str, QShortcut] = {}
        
        if PYSIDE6_AVAILABLE:
            self._setup_default_shortcuts()
    
    def _setup_default_shortcuts(self):
        """Set up default keyboard shortcuts."""
        # Form operations
        self.add_shortcut("Ctrl+N", "new_form", "Create new form")
        self.add_shortcut("Ctrl+S", "save_form", "Save current form")
        self.add_shortcut("Ctrl+Shift+S", "save_as_form", "Save form as...")
        self.add_shortcut("Ctrl+O", "open_form", "Open form")
        
        # Edit operations
        self.add_shortcut("Ctrl+Z", "undo", "Undo last action")
        self.add_shortcut("Ctrl+Y", "redo", "Redo action")
        self.add_shortcut("Ctrl+A", "select_all", "Select all text")
        
        # Import/Export
        self.add_shortcut("Ctrl+I", "import_form", "Import form from file")
        self.add_shortcut("Ctrl+E", "export_form", "Export form to file")
        self.add_shortcut("Ctrl+P", "print_form", "Print/PDF form")
        
        # Navigation
        self.add_shortcut("Ctrl+Tab", "next_tab", "Next form tab")
        self.add_shortcut("Ctrl+Shift+Tab", "prev_tab", "Previous form tab")
        self.add_shortcut("F1", "help", "Show help")
        self.add_shortcut("Escape", "cancel", "Cancel current operation")
    
    def add_shortcut(self, key_sequence: str, action_name: str, 
                    description: str, callback: Optional[Callable] = None):
        """Add a keyboard shortcut.
        
        Args:
            key_sequence: Key sequence string (e.g., "Ctrl+S").
            action_name: Unique action name.
            description: Human-readable description.
            callback: Optional callback function.
        """
        if not PYSIDE6_AVAILABLE:
            return
        
        shortcut = QShortcut(QKeySequence(key_sequence), self.parent)
        shortcut.setContext(Qt.WindowShortcut)
        
        if callback:
            shortcut.activated.connect(callback)
        
        # Store with metadata
        self.shortcuts[action_name] = {
            'shortcut': shortcut,
            'key_sequence': key_sequence,
            'description': description
        }
        
        logger.debug(f"Added keyboard shortcut: {key_sequence} -> {action_name}")
    
    def connect_shortcut(self, action_name: str, callback: Callable):
        """Connect a callback to an existing shortcut.
        
        Args:
            action_name: Action name to connect.
            callback: Callback function.
        """
        if action_name in self.shortcuts:
            shortcut_info = self.shortcuts[action_name]
            shortcut_info['shortcut'].activated.connect(callback)
            logger.debug(f"Connected callback to shortcut: {action_name}")
    
    def get_shortcuts_help(self) -> List[Dict[str, str]]:
        """Get list of all shortcuts for help display.
        
        Returns:
            List of dictionaries with shortcut information.
        """
        help_list = []
        for action_name, info in self.shortcuts.items():
            help_list.append({
                'action': action_name,
                'keys': info['key_sequence'],
                'description': info['description']
            })
        
        return sorted(help_list, key=lambda x: x['keys'])


class UXAutoSave:
    """Enhanced auto-save functionality."""
    
    def __init__(self, save_callback: Callable, interval_seconds: int = 30):
        """Initialize auto-save functionality.
        
        Args:
            save_callback: Function to call for saving.
            interval_seconds: Auto-save interval in seconds.
        """
        self.save_callback = save_callback
        self.interval_seconds = interval_seconds
        self.is_enabled = True
        self.has_changes = False
        
        if PYSIDE6_AVAILABLE:
            self.timer = QTimer()
            self.timer.timeout.connect(self._auto_save)
            self.timer.start(interval_seconds * 1000)
            
            logger.debug(f"Auto-save initialized with {interval_seconds}s interval")
    
    def mark_changed(self):
        """Mark that changes have been made."""
        self.has_changes = True
    
    def mark_saved(self):
        """Mark that changes have been saved."""
        self.has_changes = False
    
    def set_enabled(self, enabled: bool):
        """Enable or disable auto-save.
        
        Args:
            enabled: Whether auto-save should be enabled.
        """
        self.is_enabled = enabled
        logger.debug(f"Auto-save {'enabled' if enabled else 'disabled'}")
    
    def set_interval(self, seconds: int):
        """Set auto-save interval.
        
        Args:
            seconds: New interval in seconds.
        """
        self.interval_seconds = seconds
        if PYSIDE6_AVAILABLE and hasattr(self, 'timer'):
            self.timer.setInterval(seconds * 1000)
        
        logger.debug(f"Auto-save interval set to {seconds}s")
    
    def _auto_save(self):
        """Perform auto-save if changes exist."""
        if self.is_enabled and self.has_changes:
            try:
                self.save_callback()
                self.mark_saved()
                logger.debug("Auto-save completed")
            except Exception as e:
                logger.error(f"Auto-save failed: {e}")


class UXEnhancementManager:
    """Central manager for all UX enhancements."""
    
    def __init__(self, main_window):
        """Initialize UX enhancement manager.
        
        Args:
            main_window: Main application window.
        """
        self.main_window = main_window
        self.notifications: List[UXNotificationWidget] = []
        self.validation_widgets: Dict[str, UXValidationFeedback] = {}
        
        if PYSIDE6_AVAILABLE:
            self.shortcuts = UXKeyboardShortcuts(main_window)
            self.progress = UXProgressIndicator(main_window)
            self.auto_save = None  # Will be initialized when needed
        
        logger.debug("UX Enhancement Manager initialized")
    
    def show_notification(self, message: str, notification_type: NotificationType = NotificationType.INFO,
                         auto_dismiss: int = 5000):
        """Show a notification to the user.
        
        Args:
            message: Notification message.
            notification_type: Type of notification.
            auto_dismiss: Auto-dismiss timeout in milliseconds.
        """
        if not PYSIDE6_AVAILABLE:
            logger.info(f"Notification: {message}")
            return
        
        notification = UXNotificationWidget(message, notification_type, auto_dismiss, self.main_window)
        notification.dismissed.connect(lambda: self._remove_notification(notification))
        
        # Position and show notification
        parent_rect = self.main_window.geometry()
        notification.show_notification(parent_rect)
        
        self.notifications.append(notification)
    
    def _remove_notification(self, notification: UXNotificationWidget):
        """Remove notification from tracking list."""
        if notification in self.notifications:
            self.notifications.remove(notification)
            notification.deleteLater()
    
    def add_validation_feedback(self, field_name: str, parent_widget: QWidget) -> UXValidationFeedback:
        """Add validation feedback widget for a field.
        
        Args:
            field_name: Unique field identifier.
            parent_widget: Parent widget to attach to.
            
        Returns:
            Validation feedback widget.
        """
        if not PYSIDE6_AVAILABLE:
            return None
        
        feedback_widget = UXValidationFeedback(parent_widget)
        self.validation_widgets[field_name] = feedback_widget
        
        return feedback_widget
    
    def set_field_validation(self, field_name: str, level: ValidationLevel, message: str = ""):
        """Set validation state for a field.
        
        Args:
            field_name: Field identifier.
            level: Validation level.
            message: Validation message.
        """
        if field_name in self.validation_widgets:
            self.validation_widgets[field_name].set_validation_state(level, message)
    
    def clear_all_validation(self):
        """Clear all validation feedback."""
        for widget in self.validation_widgets.values():
            widget.clear_validation()
    
    def setup_auto_save(self, save_callback: Callable, interval_seconds: int = 30):
        """Set up auto-save functionality.
        
        Args:
            save_callback: Function to call for saving.
            interval_seconds: Auto-save interval in seconds.
        """
        if PYSIDE6_AVAILABLE:
            self.auto_save = UXAutoSave(save_callback, interval_seconds)
    
    def show_progress(self, operation_text: str, total_steps: int = 0):
        """Show progress indicator.
        
        Args:
            operation_text: Description of operation.
            total_steps: Total number of steps.
        """
        if PYSIDE6_AVAILABLE:
            self.progress.start_operation(operation_text, total_steps)
    
    def update_progress(self, current_step: int, status_text: str = ""):
        """Update progress indicator.
        
        Args:
            current_step: Current step number.
            status_text: Optional status text.
        """
        if PYSIDE6_AVAILABLE:
            self.progress.update_progress(current_step, status_text)
    
    def finish_progress(self, success: bool = True, message: str = ""):
        """Finish progress indication.
        
        Args:
            success: Whether operation was successful.
            message: Optional completion message.
        """
        if PYSIDE6_AVAILABLE:
            self.progress.finish_operation(success, message)
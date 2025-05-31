"""Text field templates for the RadioForms template system.

This module provides text input field templates including single-line
and multi-line text fields with validation and formatting options.

Classes:
    TextFieldTemplate: Single-line text input field
    TextAreaFieldTemplate: Multi-line text input field

Notes:
    These templates follow CLAUDE.md principles for simplicity and
    explicit configuration over complex behavior.
"""

from dataclasses import dataclass
from typing import Optional, Any
import logging

# Import base classes
from ..base.field_template import FieldTemplate, ValidationResult, MaxLengthRule

# Import Qt classes with fallback for testing
try:
    from PySide6.QtWidgets import QLineEdit, QTextEdit, QPlainTextEdit
    from PySide6.QtCore import QObject, Signal
    PYSIDE6_AVAILABLE = True
except ImportError:
    # Mock classes for testing without PySide6
    class QLineEdit:
        def __init__(self):
            self._text = ""
        def text(self):
            return self._text
        def setText(self, text):
            self._text = text
        def setPlaceholderText(self, text):
            pass
        def setMaxLength(self, length):
            pass
        def setEnabled(self, enabled):
            pass
        def setVisible(self, visible):
            pass
        def setReadOnly(self, read_only):
            pass
        def setInputMask(self, mask):
            pass
        def clear(self):
            self._text = ""
    
    class QTextEdit:
        def __init__(self):
            self._text = ""
        def toPlainText(self):
            return self._text
        def setPlainText(self, text):
            self._text = text
        def setPlaceholderText(self, text):
            pass
        def setEnabled(self, enabled):
            pass
        def setVisible(self, visible):
            pass
        def setReadOnly(self, read_only):
            pass
        def setMinimumHeight(self, height):
            pass
        def setMaximumHeight(self, height):
            pass
        def clear(self):
            self._text = ""
    
    class QPlainTextEdit:
        def __init__(self):
            self._text = ""
        def toPlainText(self):
            return self._text
        def setPlainText(self, text):
            self._text = text
        def setPlaceholderText(self, text):
            pass
        def setEnabled(self, enabled):
            pass
        def setVisible(self, visible):
            pass
        def setReadOnly(self, read_only):
            pass
        def setMinimumHeight(self, height):
            pass
        def setMaximumHeight(self, height):
            pass
        def clear(self):
            self._text = ""
    
    PYSIDE6_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class TextFieldTemplate(FieldTemplate):
    """Single-line text input field template.
    
    Provides a simple text input field with validation and formatting
    options suitable for names, IDs, and short text entries.
    
    Attributes:
        max_length: Maximum number of characters allowed
        placeholder: Placeholder text to show when empty
        mask: Input mask for formatted input (e.g., phone numbers)
        read_only: Whether field is read-only
    
    Example:
        >>> field = TextFieldTemplate(
        ...     field_id="incident_name",
        ...     label="Incident Name",
        ...     max_length=100,
        ...     placeholder="Enter incident name",
        ...     required=True
        ... )
        >>> widget = field.create_widget()
        >>> field.set_value("Mountain Fire 2025")
    """
    
    max_length: Optional[int] = None
    placeholder: Optional[str] = None
    mask: Optional[str] = None
    read_only: bool = False
    
    def __post_init__(self):
        """Initialize text field template."""
        super().__post_init__()
        
        # Add max length validation rule if specified
        if self.max_length and not any(
            isinstance(rule, MaxLengthRule) for rule in self.validation_rules
        ):
            self.validation_rules.append(MaxLengthRule(self.max_length, self.label))
    
    def create_widget(self) -> QLineEdit:
        """Create QLineEdit widget for text input.
        
        Returns:
            QLineEdit: Configured text input widget
        """
        widget = QLineEdit()
        
        # Configure placeholder text
        if self.placeholder:
            widget.setPlaceholderText(self.placeholder)
        
        # Configure maximum length
        if self.max_length:
            widget.setMaxLength(self.max_length)
        
        # Configure input mask if specified
        if self.mask and PYSIDE6_AVAILABLE:
            widget.setInputMask(self.mask)
        
        # Configure read-only state
        widget.setReadOnly(self.read_only)
        
        # Set initial value
        if self.default_value is not None:
            widget.setText(str(self.default_value))
        
        # Configure enabled/visible state
        widget.setEnabled(self.enabled)
        widget.setVisible(self.visible)
        
        # Connect value changed signal if PySide6 is available
        if PYSIDE6_AVAILABLE:
            widget.textChanged.connect(self._notify_value_changed)
        
        self.widget = widget
        logger.debug(f"Created text field widget for {self.field_id}")
        
        return widget
    
    def get_value(self) -> str:
        """Get current text value from the widget.
        
        Returns:
            str: Current text value
        """
        if hasattr(self, 'widget') and self.widget:
            return self.widget.text()
        elif self.default_value is not None:
            return str(self.default_value)
        else:
            return ""
    
    def set_value(self, value: Any) -> None:
        """Set text value in the widget.
        
        Args:
            value: Value to set (will be converted to string)
        """
        text_value = str(value) if value is not None else ""
        
        if hasattr(self, 'widget') and self.widget:
            self.widget.setText(text_value)
        else:
            # Store as default value if widget not created yet
            self.default_value = text_value
        
        logger.debug(f"Set value for {self.field_id}: {text_value}")


@dataclass
class TextAreaFieldTemplate(FieldTemplate):
    """Multi-line text input field template.
    
    Provides a text area for longer text entries such as descriptions,
    messages, and detailed information.
    
    Attributes:
        max_length: Maximum number of characters allowed
        placeholder: Placeholder text to show when empty
        min_rows: Minimum number of visible rows
        max_rows: Maximum number of visible rows
        word_wrap: Whether to wrap words at widget boundaries
        read_only: Whether field is read-only
        plain_text: Whether to use plain text (no rich formatting)
    
    Example:
        >>> field = TextAreaFieldTemplate(
        ...     field_id="message",
        ...     label="Message Content",
        ...     max_length=1000,
        ...     min_rows=3,
        ...     placeholder="Enter message content",
        ...     required=True
        ... )
        >>> widget = field.create_widget()
        >>> field.set_value("This is a multi-line message...")
    """
    
    max_length: Optional[int] = None
    placeholder: Optional[str] = None
    min_rows: int = 3
    max_rows: Optional[int] = None
    word_wrap: bool = True
    read_only: bool = False
    plain_text: bool = True
    
    def __post_init__(self):
        """Initialize text area field template."""
        super().__post_init__()
        
        # Add max length validation rule if specified
        if self.max_length and not any(
            isinstance(rule, MaxLengthRule) for rule in self.validation_rules
        ):
            self.validation_rules.append(MaxLengthRule(self.max_length, self.label))
    
    def create_widget(self):
        """Create text area widget for multi-line input.
        
        Returns:
            QTextEdit or QPlainTextEdit: Configured text area widget
        """
        # Use QPlainTextEdit for plain text, QTextEdit for rich text
        if self.plain_text:
            widget = QPlainTextEdit()
        else:
            widget = QTextEdit()
        
        # Configure placeholder text
        if self.placeholder:
            widget.setPlaceholderText(self.placeholder)
        
        # Configure minimum size based on rows
        if PYSIDE6_AVAILABLE and hasattr(widget, 'fontMetrics'):
            font_height = widget.fontMetrics().height()
            min_height = font_height * self.min_rows + 10  # Add padding
            widget.setMinimumHeight(min_height)
            
            if self.max_rows:
                max_height = font_height * self.max_rows + 10
                widget.setMaximumHeight(max_height)
        
        # Configure word wrap
        if PYSIDE6_AVAILABLE and hasattr(widget, 'setWordWrapMode'):
            if self.word_wrap:
                from PySide6.QtGui import QTextOption
                widget.setWordWrapMode(QTextOption.WordWrap)
            else:
                widget.setWordWrapMode(QTextOption.NoWrap)
        
        # Configure read-only state
        widget.setReadOnly(self.read_only)
        
        # Set initial value
        if self.default_value is not None:
            widget.setPlainText(str(self.default_value))
        
        # Configure enabled/visible state
        widget.setEnabled(self.enabled)
        widget.setVisible(self.visible)
        
        # Connect value changed signal if PySide6 is available
        if PYSIDE6_AVAILABLE:
            widget.textChanged.connect(self._notify_value_changed)
        
        self.widget = widget
        logger.debug(f"Created text area widget for {self.field_id}")
        
        return widget
    
    def get_value(self) -> str:
        """Get current text value from the widget.
        
        Returns:
            str: Current text value
        """
        if hasattr(self, 'widget') and self.widget:
            return self.widget.toPlainText()
        elif self.default_value is not None:
            return str(self.default_value)
        else:
            return ""
    
    def set_value(self, value: Any) -> None:
        """Set text value in the widget.
        
        Args:
            value: Value to set (will be converted to string)
        """
        text_value = str(value) if value is not None else ""
        
        if hasattr(self, 'widget') and self.widget:
            self.widget.setPlainText(text_value)
        else:
            # Store as default value if widget not created yet
            self.default_value = text_value
        
        logger.debug(f"Set value for {self.field_id}: {text_value[:50]}...")
    
    def validate(self) -> ValidationResult:
        """Validate text area content with character count checking.
        
        Returns:
            ValidationResult: Validation result with character count info
        """
        result = super().validate()
        
        # Add character count information for user feedback
        if result.is_valid and self.max_length:
            current_length = len(self.get_value())
            if current_length > self.max_length * 0.9:  # Warn at 90% capacity
                remaining = self.max_length - current_length
                result.message = f"Valid ({remaining} characters remaining)"
        
        return result
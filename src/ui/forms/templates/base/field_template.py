"""Base field template classes for the RadioForms template system.

This module provides the foundational classes for all field templates,
following CLAUDE.md principles of simplicity and explicit design.

Classes:
    ValidationResult: Result of field validation
    ValidationRule: Abstract base for validation rules
    FieldTemplate: Abstract base class for all field types

Functions:
    combine_validation_results: Combine multiple validation results

Notes:
    All field templates must inherit from FieldTemplate and implement
    the abstract methods for widget creation and value management.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Optional, Union
import logging

# Import Qt classes with fallback for testing
try:
    from PySide6.QtWidgets import QWidget
    from PySide6.QtCore import QObject, Signal
    PYSIDE6_AVAILABLE = True
except ImportError:
    # Mock classes for testing without PySide6
    class QWidget:
        pass
    class QObject:
        pass
    def Signal():
        return lambda: None
    PYSIDE6_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of field validation operation.
    
    Encapsulates whether validation passed and provides detailed
    error messages for user feedback.
    
    Attributes:
        is_valid: True if validation passed
        message: Human-readable validation message
        field_id: ID of the field that was validated
        error_code: Optional machine-readable error code
    
    Example:
        >>> result = ValidationResult(False, "Field is required", "name_field")
        >>> if not result.is_valid:
        ...     print(f"Validation error: {result.message}")
    """
    
    is_valid: bool
    message: str = ""
    field_id: Optional[str] = None
    error_code: Optional[str] = None
    
    @classmethod
    def success(cls, message: str = "Valid") -> 'ValidationResult':
        """Create successful validation result."""
        return cls(is_valid=True, message=message)
    
    @classmethod
    def error(cls, message: str, field_id: Optional[str] = None, 
             error_code: Optional[str] = None) -> 'ValidationResult':
        """Create failed validation result."""
        return cls(
            is_valid=False, 
            message=message, 
            field_id=field_id, 
            error_code=error_code
        )
    
    @classmethod
    def combine(cls, results: List['ValidationResult']) -> 'ValidationResult':
        """Combine multiple validation results.
        
        Args:
            results: List of validation results to combine
            
        Returns:
            Combined result - fails if any input failed
        """
        if not results:
            return cls.success("No validation performed")
        
        failed_results = [r for r in results if not r.is_valid]
        
        if not failed_results:
            return cls.success("All validations passed")
        
        # Combine error messages
        messages = [r.message for r in failed_results if r.message]
        combined_message = "; ".join(messages)
        
        return cls.error(combined_message)


class ValidationRule(ABC):
    """Abstract base class for field validation rules.
    
    Validation rules encapsulate specific validation logic that can
    be applied to field values. Rules are composable and reusable.
    
    Example:
        >>> class RequiredRule(ValidationRule):
        ...     def validate(self, value):
        ...         if not value:
        ...             return ValidationResult.error("Field is required")
        ...         return ValidationResult.success()
    """
    
    @abstractmethod
    def validate(self, value: Any) -> ValidationResult:
        """Validate a field value.
        
        Args:
            value: The value to validate
            
        Returns:
            ValidationResult indicating success or failure
        """
        pass


class RequiredRule(ValidationRule):
    """Validation rule for required fields."""
    
    def __init__(self, field_label: str = "Field"):
        self.field_label = field_label
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate that value is not empty."""
        if value is None:
            return ValidationResult.error(f"{self.field_label} is required")
        
        if isinstance(value, str) and not value.strip():
            return ValidationResult.error(f"{self.field_label} is required")
        
        if hasattr(value, '__len__') and len(value) == 0:
            return ValidationResult.error(f"{self.field_label} is required")
        
        return ValidationResult.success()


class MaxLengthRule(ValidationRule):
    """Validation rule for maximum string length."""
    
    def __init__(self, max_length: int, field_label: str = "Field"):
        self.max_length = max_length
        self.field_label = field_label
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate that string value doesn't exceed maximum length."""
        if value is None:
            return ValidationResult.success()
        
        str_value = str(value)
        if len(str_value) > self.max_length:
            return ValidationResult.error(
                f"{self.field_label} must be {self.max_length} characters or less"
            )
        
        return ValidationResult.success()


@dataclass
class FieldTemplate(ABC):
    """Abstract base class for all field templates.
    
    Field templates define the structure and behavior of form fields,
    including widget creation, validation, and value management.
    
    All concrete field types must inherit from this class and implement
    the abstract methods.
    
    Attributes:
        field_id: Unique identifier for this field
        label: Human-readable field label
        required: Whether this field is required
        validation_rules: List of validation rules to apply
        help_text: Optional help text for users
        default_value: Default value for the field
        enabled: Whether the field is enabled for editing
        visible: Whether the field is visible
    
    Example:
        >>> class MyFieldTemplate(FieldTemplate):
        ...     def create_widget(self):
        ...         return QLineEdit()
        ...     def get_value(self):
        ...         return self.widget.text()
        ...     def set_value(self, value):
        ...         self.widget.setText(str(value))
    """
    
    field_id: str
    label: str
    required: bool = False
    validation_rules: List[ValidationRule] = field(default_factory=list)
    help_text: Optional[str] = None
    default_value: Any = None
    enabled: bool = True
    visible: bool = True
    
    def __post_init__(self):
        """Initialize field template after creation."""
        self.widget: Optional[QWidget] = None
        self._value_changed_callbacks: List = []
        
        # Add required validation rule if field is required
        if self.required and not any(isinstance(rule, RequiredRule) for rule in self.validation_rules):
            self.validation_rules.insert(0, RequiredRule(self.label))
        
        logger.debug(f"Created field template: {self.field_id}")
    
    @abstractmethod
    def create_widget(self) -> QWidget:
        """Create the Qt widget for this field.
        
        Returns:
            QWidget: The widget for user interaction
            
        Notes:
            This method must be implemented by all concrete field types.
            The widget should be properly configured with signals connected.
        """
        pass
    
    @abstractmethod
    def get_value(self) -> Any:
        """Get the current value from the field widget.
        
        Returns:
            The current field value in appropriate Python type
            
        Notes:
            This method must handle the case where the widget hasn't
            been created yet by returning the default value.
        """
        pass
    
    @abstractmethod
    def set_value(self, value: Any) -> None:
        """Set the field widget to the specified value.
        
        Args:
            value: The value to set
            
        Notes:
            This method must handle type conversion and widget updates.
            Should be safe to call even if widget hasn't been created.
        """
        pass
    
    def validate(self) -> ValidationResult:
        """Validate the current field value.
        
        Returns:
            ValidationResult indicating success or failure
        """
        current_value = self.get_value()
        
        # Apply all validation rules
        results = []
        for rule in self.validation_rules:
            try:
                result = rule.validate(current_value)
                result.field_id = self.field_id  # Add field context
                results.append(result)
            except Exception as e:
                logger.error(f"Validation rule failed for {self.field_id}: {e}")
                results.append(ValidationResult.error(
                    f"Validation error in {self.label}",
                    field_id=self.field_id,
                    error_code="VALIDATION_EXCEPTION"
                ))
        
        return ValidationResult.combine(results)
    
    def reset(self) -> None:
        """Reset field to default value."""
        if self.default_value is not None:
            self.set_value(self.default_value)
        else:
            # Reset to empty/default state
            if hasattr(self, 'widget') and self.widget:
                if hasattr(self.widget, 'clear'):
                    self.widget.clear()
                elif hasattr(self.widget, 'setText'):
                    self.widget.setText("")
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the field."""
        self.enabled = enabled
        if hasattr(self, 'widget') and self.widget:
            self.widget.setEnabled(enabled)
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the field."""
        self.visible = visible
        if hasattr(self, 'widget') and self.widget:
            self.widget.setVisible(visible)
    
    def add_value_changed_callback(self, callback) -> None:
        """Add callback to be called when field value changes."""
        self._value_changed_callbacks.append(callback)
    
    def _notify_value_changed(self) -> None:
        """Notify all callbacks that value has changed."""
        for callback in self._value_changed_callbacks:
            try:
                callback(self.field_id, self.get_value())
            except Exception as e:
                logger.warning(f"Value changed callback failed for {self.field_id}: {e}")
    
    def to_dict(self) -> dict:
        """Convert field template to dictionary representation."""
        return {
            'field_id': self.field_id,
            'label': self.label,
            'value': self.get_value(),
            'required': self.required,
            'enabled': self.enabled,
            'visible': self.visible,
            'help_text': self.help_text
        }
    
    def from_dict(self, data: dict) -> None:
        """Load field template from dictionary representation."""
        if 'value' in data:
            self.set_value(data['value'])
        if 'enabled' in data:
            self.set_enabled(data['enabled'])
        if 'visible' in data:
            self.set_visible(data['visible'])


def combine_validation_results(results: List[ValidationResult]) -> ValidationResult:
    """Utility function to combine multiple validation results."""
    return ValidationResult.combine(results)
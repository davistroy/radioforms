"""Section template base classes for the RadioForms template system.

This module provides the foundational classes for form sections,
which group related fields together with consistent layout and validation.

Classes:
    LayoutType: Enumeration of available layout types
    SectionTemplate: Abstract base class for form sections

Functions:
    create_section_layout: Factory function for layout creation

Notes:
    Sections provide logical grouping of fields and coordinate validation
    across multiple fields within the section.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
import logging

# Import field template and Qt classes
from .field_template import FieldTemplate, ValidationResult

# Import Qt classes with fallback for testing
try:
    from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                                   QGridLayout, QGroupBox, QFormLayout)
    from PySide6.QtCore import QObject, Signal
    PYSIDE6_AVAILABLE = True
except ImportError:
    # Mock classes for testing without PySide6
    class QWidget:
        pass
    class QVBoxLayout:
        pass
    class QHBoxLayout:
        pass
    class QGridLayout:
        pass
    class QGroupBox:
        pass
    class QFormLayout:
        pass
    class QObject:
        pass
    def Signal():
        return lambda: None
    PYSIDE6_AVAILABLE = False

logger = logging.getLogger(__name__)


class LayoutType(Enum):
    """Types of layouts available for sections.
    
    Different layout types provide different arrangements of fields
    within a section, optimized for different use cases.
    """
    
    SINGLE_COLUMN = "single_column"      # Vertical stacking of fields
    TWO_COLUMN = "two_column"            # Side-by-side field arrangement
    FORM_LAYOUT = "form_layout"          # Label-field pairs in form layout
    GRID_LAYOUT = "grid_layout"          # Custom grid arrangement
    HORIZONTAL = "horizontal"            # Horizontal field arrangement


@dataclass
class SectionTemplate(ABC):
    """Abstract base class for form sections.
    
    Sections group related fields together and provide consistent
    layout, validation, and interaction patterns.
    
    Attributes:
        section_id: Unique identifier for this section
        title: Human-readable section title
        fields: List of field templates in this section
        layout: Layout type for field arrangement
        collapsible: Whether section can be collapsed
        collapsed: Whether section starts collapsed
        required: Whether this section is required
        visible: Whether section is visible
        help_text: Optional help text for the section
    
    Example:
        >>> class MySection(SectionTemplate):
        ...     def create_section_widget(self):
        ...         group_box = QGroupBox(self.title)
        ...         layout = QVBoxLayout(group_box)
        ...         for field in self.fields:
        ...             layout.addWidget(field.create_widget())
        ...         return group_box
    """
    
    section_id: str
    title: str
    fields: List[FieldTemplate] = field(default_factory=list)
    layout: LayoutType = LayoutType.SINGLE_COLUMN
    collapsible: bool = False
    collapsed: bool = False
    required: bool = False
    visible: bool = True
    help_text: Optional[str] = None
    
    def __post_init__(self):
        """Initialize section template after creation."""
        self.widget: Optional[QWidget] = None
        self._field_widgets: Dict[str, QWidget] = {}
        
        logger.debug(f"Created section template: {self.section_id}")
    
    @abstractmethod
    def create_section_widget(self) -> QWidget:
        """Create the Qt widget for this section.
        
        Returns:
            QWidget: The section widget containing all field widgets
            
        Notes:
            This method must be implemented by all concrete section types.
            The widget should contain all fields arranged according to
            the specified layout type.
        """
        pass
    
    def add_field(self, field_template: FieldTemplate) -> None:
        """Add a field template to this section.
        
        Args:
            field_template: The field template to add
        """
        if field_template.field_id in [f.field_id for f in self.fields]:
            raise ValueError(f"Field {field_template.field_id} already exists in section {self.section_id}")
        
        self.fields.append(field_template)
        logger.debug(f"Added field {field_template.field_id} to section {self.section_id}")
    
    def remove_field(self, field_id: str) -> bool:
        """Remove a field from this section.
        
        Args:
            field_id: ID of the field to remove
            
        Returns:
            bool: True if field was removed, False if not found
        """
        for i, field in enumerate(self.fields):
            if field.field_id == field_id:
                self.fields.pop(i)
                if field_id in self._field_widgets:
                    del self._field_widgets[field_id]
                logger.debug(f"Removed field {field_id} from section {self.section_id}")
                return True
        return False
    
    def get_field(self, field_id: str) -> Optional[FieldTemplate]:
        """Get a field template by ID.
        
        Args:
            field_id: ID of the field to get
            
        Returns:
            FieldTemplate or None if not found
        """
        for field in self.fields:
            if field.field_id == field_id:
                return field
        return None
    
    def validate_section(self) -> ValidationResult:
        """Validate all fields in this section.
        
        Returns:
            ValidationResult: Combined validation result for all fields
        """
        if not self.visible:
            return ValidationResult.success("Section not visible")
        
        results = []
        for field in self.fields:
            try:
                field_result = field.validate()
                results.append(field_result)
            except Exception as e:
                logger.error(f"Field validation failed for {field.field_id}: {e}")
                results.append(ValidationResult.error(
                    f"Validation error in {field.label}",
                    field_id=field.field_id
                ))
        
        combined_result = ValidationResult.combine(results)
        
        # Add section-specific validation if needed
        if self.required and not any(field.get_value() for field in self.fields):
            return ValidationResult.error(f"Section '{self.title}' requires at least one field to be filled")
        
        return combined_result
    
    def reset_section(self) -> None:
        """Reset all fields in this section to default values."""
        for field in self.fields:
            try:
                field.reset()
            except Exception as e:
                logger.warning(f"Failed to reset field {field.field_id}: {e}")
    
    def set_section_enabled(self, enabled: bool) -> None:
        """Enable or disable all fields in this section."""
        for field in self.fields:
            field.set_enabled(enabled)
    
    def set_section_visible(self, visible: bool) -> None:
        """Show or hide this section."""
        self.visible = visible
        if hasattr(self, 'widget') and self.widget:
            self.widget.setVisible(visible)
    
    def get_section_data(self) -> Dict[str, Any]:
        """Get data from all fields in this section.
        
        Returns:
            Dict mapping field IDs to their current values
        """
        return {
            field.field_id: field.get_value()
            for field in self.fields
        }
    
    def set_section_data(self, data: Dict[str, Any]) -> None:
        """Set data for fields in this section.
        
        Args:
            data: Dict mapping field IDs to values
        """
        for field in self.fields:
            if field.field_id in data:
                try:
                    field.set_value(data[field.field_id])
                except Exception as e:
                    logger.warning(f"Failed to set value for field {field.field_id}: {e}")
    
    def _create_layout_widget(self, parent_widget: QWidget) -> QWidget:
        """Create layout widget based on layout type.
        
        Args:
            parent_widget: Parent widget to contain the layout
            
        Returns:
            QWidget: Widget with appropriate layout
        """
        if not PYSIDE6_AVAILABLE:
            return parent_widget
        
        if self.layout == LayoutType.SINGLE_COLUMN:
            layout = QVBoxLayout(parent_widget)
            for field in self.fields:
                if field.visible:
                    field_widget = field.create_widget()
                    self._field_widgets[field.field_id] = field_widget
                    layout.addWidget(field_widget)
        
        elif self.layout == LayoutType.FORM_LAYOUT:
            layout = QFormLayout(parent_widget)
            for field in self.fields:
                if field.visible:
                    field_widget = field.create_widget()
                    self._field_widgets[field.field_id] = field_widget
                    layout.addRow(field.label, field_widget)
        
        elif self.layout == LayoutType.TWO_COLUMN:
            layout = QGridLayout(parent_widget)
            for i, field in enumerate(self.fields):
                if field.visible:
                    field_widget = field.create_widget()
                    self._field_widgets[field.field_id] = field_widget
                    row = i // 2
                    col = i % 2
                    layout.addWidget(field_widget, row, col)
        
        elif self.layout == LayoutType.HORIZONTAL:
            layout = QHBoxLayout(parent_widget)
            for field in self.fields:
                if field.visible:
                    field_widget = field.create_widget()
                    self._field_widgets[field.field_id] = field_widget
                    layout.addWidget(field_widget)
        
        else:
            # Default to single column
            layout = QVBoxLayout(parent_widget)
            for field in self.fields:
                if field.visible:
                    field_widget = field.create_widget()
                    self._field_widgets[field.field_id] = field_widget
                    layout.addWidget(field_widget)
        
        return parent_widget
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert section template to dictionary representation."""
        return {
            'section_id': self.section_id,
            'title': self.title,
            'layout': self.layout.value,
            'collapsible': self.collapsible,
            'collapsed': self.collapsed,
            'required': self.required,
            'visible': self.visible,
            'help_text': self.help_text,
            'fields': [field.to_dict() for field in self.fields],
            'data': self.get_section_data()
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load section template from dictionary representation."""
        if 'visible' in data:
            self.set_section_visible(data['visible'])
        if 'collapsed' in data:
            self.collapsed = data['collapsed']
        if 'data' in data:
            self.set_section_data(data['data'])


class DefaultSectionTemplate(SectionTemplate):
    """Default implementation of section template.
    
    Provides a simple section implementation using QGroupBox with
    configurable layout for fields.
    """
    
    def create_section_widget(self) -> QWidget:
        """Create default section widget with group box."""
        if not PYSIDE6_AVAILABLE:
            # Return mock widget for testing
            return QWidget()
        
        group_box = QGroupBox(self.title)
        group_box.setCheckable(self.collapsible)
        if self.collapsible:
            group_box.setChecked(not self.collapsed)
        
        # Apply layout to group box
        self._create_layout_widget(group_box)
        
        self.widget = group_box
        return group_box


def create_section_layout(layout_type: LayoutType, parent: QWidget = None):
    """Factory function to create layout objects.
    
    Args:
        layout_type: Type of layout to create
        parent: Optional parent widget
        
    Returns:
        Layout object of appropriate type
    """
    if not PYSIDE6_AVAILABLE:
        return None
    
    if layout_type == LayoutType.SINGLE_COLUMN:
        return QVBoxLayout(parent)
    elif layout_type == LayoutType.TWO_COLUMN or layout_type == LayoutType.GRID_LAYOUT:
        return QGridLayout(parent)
    elif layout_type == LayoutType.FORM_LAYOUT:
        return QFormLayout(parent)
    elif layout_type == LayoutType.HORIZONTAL:
        return QHBoxLayout(parent)
    else:
        return QVBoxLayout(parent)
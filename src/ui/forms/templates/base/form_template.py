"""Form template base classes for the RadioForms template system.

This module provides the foundational classes for complete form templates,
which coordinate multiple sections and provide overall form management.

Classes:
    FormTemplate: Abstract base class for complete forms
    FormMetadata: Metadata for form templates

Functions:
    create_form_from_sections: Factory function for form creation

Notes:
    Form templates provide the highest level of organization, coordinating
    multiple sections and providing overall validation and data management.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

# Import base classes
from .section_template import SectionTemplate
from .field_template import ValidationResult

# Import Qt classes with fallback for testing
try:
    from PySide6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, 
                                   QFrame, QSplitter, QTabWidget)
    from PySide6.QtCore import QObject, Signal
    PYSIDE6_AVAILABLE = True
except ImportError:
    # Mock classes for testing without PySide6
    class QWidget:
        pass
    class QVBoxLayout:
        pass
    class QScrollArea:
        pass
    class QFrame:
        pass
    class QSplitter:
        pass
    class QTabWidget:
        pass
    class QObject:
        pass
    def Signal():
        return lambda: None
    PYSIDE6_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class FormMetadata:
    """Metadata for form templates.
    
    Contains information about the form template including version,
    creation date, and compliance information.
    
    Attributes:
        form_id: Unique form identifier (e.g., "ICS-205")
        name: Human-readable form name
        version: Form template version
        description: Description of the form's purpose
        created_date: When this template was created
        modified_date: When this template was last modified
        fema_compliant: Whether form meets FEMA standards
        author: Template author information
        tags: Optional tags for categorization
    """
    
    form_id: str
    name: str
    version: str = "1.0"
    description: str = ""
    created_date: datetime = field(default_factory=datetime.now)
    modified_date: datetime = field(default_factory=datetime.now)
    fema_compliant: bool = True
    author: str = "RadioForms Template System"
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            'form_id': self.form_id,
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'created_date': self.created_date.isoformat(),
            'modified_date': self.modified_date.isoformat(),
            'fema_compliant': self.fema_compliant,
            'author': self.author,
            'tags': self.tags
        }


@dataclass
class FormTemplate(ABC):
    """Abstract base class for complete form templates.
    
    Form templates represent complete ICS forms with all sections,
    validation logic, and data management capabilities.
    
    Attributes:
        metadata: Form metadata information
        sections: List of section templates
        layout: Overall form layout style
        scrollable: Whether form should be scrollable
        max_width: Maximum form width in pixels
        max_height: Maximum form height in pixels
    
    Example:
        >>> class ICS205Template(FormTemplate):
        ...     def create_form_widget(self):
        ...         widget = QWidget()
        ...         layout = QVBoxLayout(widget)
        ...         for section in self.sections:
        ...             layout.addWidget(section.create_section_widget())
        ...         return widget
    """
    
    metadata: FormMetadata
    sections: List[SectionTemplate] = field(default_factory=list)
    layout: str = "vertical"  # vertical, horizontal, tabbed
    scrollable: bool = True
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    
    def __post_init__(self):
        """Initialize form template after creation."""
        self.widget: Optional[QWidget] = None
        self._section_widgets: Dict[str, QWidget] = {}
        self._form_data_cache: Dict[str, Any] = {}
        
        logger.debug(f"Created form template: {self.metadata.form_id}")
    
    @abstractmethod
    def create_form_widget(self) -> QWidget:
        """Create the Qt widget for this complete form.
        
        Returns:
            QWidget: The complete form widget containing all sections
            
        Notes:
            This method must be implemented by all concrete form types.
            The widget should contain all sections arranged according to
            the specified layout.
        """
        pass
    
    def add_section(self, section: SectionTemplate) -> None:
        """Add a section template to this form.
        
        Args:
            section: The section template to add
        """
        if section.section_id in [s.section_id for s in self.sections]:
            raise ValueError(f"Section {section.section_id} already exists in form {self.metadata.form_id}")
        
        self.sections.append(section)
        logger.debug(f"Added section {section.section_id} to form {self.metadata.form_id}")
    
    def remove_section(self, section_id: str) -> bool:
        """Remove a section from this form.
        
        Args:
            section_id: ID of the section to remove
            
        Returns:
            bool: True if section was removed, False if not found
        """
        for i, section in enumerate(self.sections):
            if section.section_id == section_id:
                self.sections.pop(i)
                if section_id in self._section_widgets:
                    del self._section_widgets[section_id]
                logger.debug(f"Removed section {section_id} from form {self.metadata.form_id}")
                return True
        return False
    
    def get_section(self, section_id: str) -> Optional[SectionTemplate]:
        """Get a section template by ID.
        
        Args:
            section_id: ID of the section to get
            
        Returns:
            SectionTemplate or None if not found
        """
        for section in self.sections:
            if section.section_id == section_id:
                return section
        return None
    
    def validate_form(self) -> ValidationResult:
        """Validate all sections and fields in this form.
        
        Returns:
            ValidationResult: Combined validation result for entire form
        """
        results = []
        
        for section in self.sections:
            try:
                section_result = section.validate_section()
                results.append(section_result)
            except Exception as e:
                logger.error(f"Section validation failed for {section.section_id}: {e}")
                results.append(ValidationResult.error(
                    f"Validation error in section '{section.title}'",
                    field_id=section.section_id
                ))
        
        combined_result = ValidationResult.combine(results)
        
        # Add form-level validation if needed
        if not any(section.get_section_data() for section in self.sections):
            return ValidationResult.error("Form cannot be empty")
        
        return combined_result
    
    def reset_form(self) -> None:
        """Reset all sections and fields to default values."""
        for section in self.sections:
            try:
                section.reset_section()
            except Exception as e:
                logger.warning(f"Failed to reset section {section.section_id}: {e}")
        
        self._form_data_cache.clear()
    
    def get_form_data(self) -> Dict[str, Any]:
        """Get data from all sections and fields in this form.
        
        Returns:
            Dict containing complete form data
        """
        form_data = {
            'metadata': self.metadata.to_dict(),
            'sections': {},
            'generated_at': datetime.now().isoformat()
        }
        
        for section in self.sections:
            try:
                section_data = section.get_section_data()
                form_data['sections'][section.section_id] = section_data
            except Exception as e:
                logger.warning(f"Failed to get data from section {section.section_id}: {e}")
                form_data['sections'][section.section_id] = {}
        
        self._form_data_cache = form_data
        return form_data
    
    def set_form_data(self, data: Dict[str, Any]) -> None:
        """Set data for all sections and fields in this form.
        
        Args:
            data: Dict containing form data
        """
        if 'sections' not in data:
            logger.warning("No sections data found in form data")
            return
        
        sections_data = data['sections']
        
        for section in self.sections:
            if section.section_id in sections_data:
                try:
                    section.set_section_data(sections_data[section.section_id])
                except Exception as e:
                    logger.warning(f"Failed to set data for section {section.section_id}: {e}")
    
    def get_field_value(self, section_id: str, field_id: str) -> Any:
        """Get value of a specific field.
        
        Args:
            section_id: ID of the section containing the field
            field_id: ID of the field
            
        Returns:
            Field value or None if not found
        """
        section = self.get_section(section_id)
        if section:
            field = section.get_field(field_id)
            if field:
                return field.get_value()
        return None
    
    def set_field_value(self, section_id: str, field_id: str, value: Any) -> bool:
        """Set value of a specific field.
        
        Args:
            section_id: ID of the section containing the field
            field_id: ID of the field
            value: Value to set
            
        Returns:
            bool: True if value was set, False if field not found
        """
        section = self.get_section(section_id)
        if section:
            field = section.get_field(field_id)
            if field:
                try:
                    field.set_value(value)
                    return True
                except Exception as e:
                    logger.warning(f"Failed to set field value {section_id}.{field_id}: {e}")
        return False
    
    def _create_form_layout(self, parent_widget: QWidget) -> QWidget:
        """Create form layout based on layout type.
        
        Args:
            parent_widget: Parent widget to contain the form
            
        Returns:
            QWidget: Widget with appropriate layout
        """
        if not PYSIDE6_AVAILABLE:
            return parent_widget
        
        if self.layout == "vertical":
            layout = QVBoxLayout(parent_widget)
            for section in self.sections:
                if section.visible:
                    section_widget = section.create_section_widget()
                    self._section_widgets[section.section_id] = section_widget
                    layout.addWidget(section_widget)
        
        elif self.layout == "tabbed":
            tab_widget = QTabWidget(parent_widget)
            main_layout = QVBoxLayout(parent_widget)
            main_layout.addWidget(tab_widget)
            
            for section in self.sections:
                if section.visible:
                    section_widget = section.create_section_widget()
                    self._section_widgets[section.section_id] = section_widget
                    tab_widget.addTab(section_widget, section.title)
        
        elif self.layout == "horizontal":
            splitter = QSplitter(parent_widget)
            main_layout = QVBoxLayout(parent_widget)
            main_layout.addWidget(splitter)
            
            for section in self.sections:
                if section.visible:
                    section_widget = section.create_section_widget()
                    self._section_widgets[section.section_id] = section_widget
                    splitter.addWidget(section_widget)
        
        else:
            # Default to vertical layout
            layout = QVBoxLayout(parent_widget)
            for section in self.sections:
                if section.visible:
                    section_widget = section.create_section_widget()
                    self._section_widgets[section.section_id] = section_widget
                    layout.addWidget(section_widget)
        
        return parent_widget
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert form template to dictionary representation."""
        return {
            'metadata': self.metadata.to_dict(),
            'layout': self.layout,
            'scrollable': self.scrollable,
            'max_width': self.max_width,
            'max_height': self.max_height,
            'sections': [section.to_dict() for section in self.sections],
            'form_data': self.get_form_data()
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load form template from dictionary representation."""
        if 'layout' in data:
            self.layout = data['layout']
        if 'scrollable' in data:
            self.scrollable = data['scrollable']
        if 'form_data' in data:
            self.set_form_data(data['form_data'])


class DefaultFormTemplate(FormTemplate):
    """Default implementation of form template.
    
    Provides a simple form implementation with vertical layout
    and optional scrolling.
    """
    
    def create_form_widget(self) -> QWidget:
        """Create default form widget with vertical layout."""
        if not PYSIDE6_AVAILABLE:
            # Return mock widget for testing
            return QWidget()
        
        if self.scrollable:
            # Create scrollable form
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            
            content_widget = QWidget()
            self._create_form_layout(content_widget)
            scroll_area.setWidget(content_widget)
            
            # Set size constraints if specified
            if self.max_width:
                scroll_area.setMaximumWidth(self.max_width)
            if self.max_height:
                scroll_area.setMaximumHeight(self.max_height)
            
            self.widget = scroll_area
            return scroll_area
        else:
            # Create non-scrollable form
            form_widget = QWidget()
            self._create_form_layout(form_widget)
            
            # Set size constraints if specified
            if self.max_width:
                form_widget.setMaximumWidth(self.max_width)
            if self.max_height:
                form_widget.setMaximumHeight(self.max_height)
            
            self.widget = form_widget
            return form_widget


def create_form_from_sections(form_id: str, name: str, sections: List[SectionTemplate], 
                             **kwargs) -> FormTemplate:
    """Factory function to create form from sections.
    
    Args:
        form_id: Unique form identifier
        name: Human-readable form name
        sections: List of section templates
        **kwargs: Additional form options
        
    Returns:
        FormTemplate: Configured form template
    """
    metadata = FormMetadata(form_id=form_id, name=name)
    form = DefaultFormTemplate(metadata=metadata, sections=sections, **kwargs)
    return form
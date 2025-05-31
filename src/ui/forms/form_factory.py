"""Form factory system for creating and managing ICS form widgets.

This module provides the factory pattern implementation for creating appropriate
form widgets based on form type. It enables dynamic form creation, consistent
form handling, and polymorphic operations across different form types.

The factory system supports:
- Dynamic form widget creation by type
- Consistent form interface across all types
- Type-safe form handling
- Extensible architecture for new form types
- Form lifecycle management

Example:
    >>> from models.base_form import FormType
    >>> 
    >>> # Create form widget by type
    >>> widget = FormWidgetFactory.create_form_widget(FormType.ICS_213)
    >>> widget.show()
    >>> 
    >>> # Create form from existing data
    >>> widget = FormWidgetFactory.create_form_widget_from_data(form_data)
    >>> widget.load_form_data(form_data)

Classes:
    FormWidgetFactory: Main factory for creating form widgets
    FormWidgetInterface: Common interface for all form widgets
    FormWidgetRegistry: Registry for form widget types
    FormSelectionWidget: Widget for selecting form types

Functions:
    register_form_widget: Register new form widget types
    get_available_form_types: Get list of available form types
    create_form_selector: Create form type selection widget

Notes:
    This implementation follows the Factory and Registry patterns to provide
    extensible form management. New form types can be added by registering
    their widget classes with the factory system.
"""

from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Callable, Set
from dataclasses import dataclass
from enum import Enum

# Handle PySide6 imports gracefully for testing environments
try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox,
        QPushButton, QLabel, QGroupBox, QMessageBox, QFrame,
        QScrollArea, QSizePolicy, QApplication
    )
    from PySide6.QtCore import Signal, Qt, QObject
    from PySide6.QtGui import QIcon, QPixmap
    PYSIDE6_AVAILABLE = True
except ImportError:
    # Create stub classes for testing environments
    PYSIDE6_AVAILABLE = False
    
    class QWidget:
        def __init__(self, parent=None): pass
        def show(self): pass
        def hide(self): pass
    
    class QComboBox(QWidget):
        def addItem(self, text, data=None): pass
        def currentData(self): return None
    
    class Signal:
        def __init__(self, *args): pass
        def connect(self, slot): pass
        def emit(self, *args): pass
    
    Qt = type('Qt', (), {})()

# Import form models with fallback handling
try:
    from ...models.base_form import BaseForm, FormType, FormStatus, create_form_from_type
except ImportError:
    # For standalone testing
    sys.path.append('.')
    from src.models.base_form import BaseForm, FormType, FormStatus, create_form_from_type

# Type variable for form widgets
FormWidgetType = TypeVar('FormWidgetType', bound='FormWidgetInterface')


class FormWidgetInterface(ABC):
    """Abstract interface that all form widgets must implement.
    
    This interface ensures that all form widgets provide consistent
    methods for loading data, validation, and lifecycle management.
    It enables polymorphic operations across different form types.
    
    Example:
        >>> class MyFormWidget(QWidget, FormWidgetInterface):
        ...     def load_form_data(self, form_data):
        ...         # Load data into UI components
        ...         pass
        ...     
        ...     def get_form_data(self):
        ...         # Extract data from UI components
        ...         return form_data
    """
    
    @abstractmethod
    def load_form_data(self, form_data: BaseForm) -> None:
        """Load form data into the widget.
        
        Args:
            form_data: Form data to load into the widget.
        """
        pass
    
    @abstractmethod
    def get_form_data(self) -> BaseForm:
        """Get current form data from the widget.
        
        Returns:
            BaseForm: Current form data from the widget.
        """
        pass
    
    @abstractmethod
    def validate_form(self) -> bool:
        """Validate the current form data.
        
        Returns:
            bool: True if form is valid, False otherwise.
        """
        pass
    
    @abstractmethod
    def clear_form(self) -> None:
        """Clear all form data from the widget."""
        pass
    
    @abstractmethod
    def get_form_type(self) -> FormType:
        """Get the form type handled by this widget.
        
        Returns:
            FormType: The form type this widget handles.
        """
        pass
    
    def is_dirty(self) -> bool:
        """Check if form has unsaved changes.
        
        Returns:
            bool: True if form has unsaved changes.
            
        Notes:
            Default implementation returns False. Subclasses should
            override this to provide dirty checking functionality.
        """
        return False
    
    def set_read_only(self, read_only: bool) -> None:
        """Set the widget to read-only mode.
        
        Args:
            read_only: Whether to enable read-only mode.
            
        Notes:
            Default implementation does nothing. Subclasses should
            override this to provide read-only functionality.
        """
        pass


@dataclass
class FormWidgetRegistration:
    """Registration information for a form widget type.
    
    Stores information about a registered form widget including
    the widget class, creation function, and metadata.
    
    Attributes:
        form_type (FormType): Type of form this widget handles.
        widget_class (Type): Class of the form widget.
        display_name (str): Human-readable name for the form type.
        description (str): Description of the form type.
        icon_path (str): Optional path to icon for the form type.
        creation_func (Callable): Function to create widget instances.
    """
    
    form_type: FormType
    widget_class: Type
    display_name: str
    description: str = ""
    icon_path: str = ""
    creation_func: Optional[Callable] = None
    
    def create_widget(self, parent: Optional[QWidget] = None) -> Optional[QWidget]:
        """Create a new widget instance.
        
        Args:
            parent: Parent widget for the new instance.
            
        Returns:
            QWidget: New widget instance or None if creation fails.
        """
        try:
            if self.creation_func:
                return self.creation_func(parent)
            else:
                return self.widget_class(parent)
        except Exception:
            return None


class FormWidgetRegistry:
    """Registry for managing form widget types and their factories.
    
    This registry maintains the mapping between form types and their
    corresponding widget classes. It supports dynamic registration
    and creation of form widgets.
    
    Example:
        >>> registry = FormWidgetRegistry()
        >>> registry.register(FormType.ICS_213, ICS213Widget, "General Message")
        >>> widget = registry.create_widget(FormType.ICS_213)
    """
    
    def __init__(self) -> None:
        """Initialize the widget registry."""
        self._registrations: Dict[FormType, FormWidgetRegistration] = {}
        self._register_default_widgets()
    
    def register(
        self, 
        form_type: FormType,
        widget_class: Type,
        display_name: str,
        description: str = "",
        icon_path: str = "",
        creation_func: Optional[Callable] = None
    ) -> None:
        """Register a form widget type.
        
        Args:
            form_type: Type of form the widget handles.
            widget_class: Class of the form widget.
            display_name: Human-readable name for display.
            description: Description of the form type.
            icon_path: Optional path to icon file.
            creation_func: Optional custom creation function.
        """
        registration = FormWidgetRegistration(
            form_type=form_type,
            widget_class=widget_class,
            display_name=display_name,
            description=description,
            icon_path=icon_path,
            creation_func=creation_func
        )
        self._registrations[form_type] = registration
    
    def unregister(self, form_type: FormType) -> bool:
        """Unregister a form widget type.
        
        Args:
            form_type: Form type to unregister.
            
        Returns:
            bool: True if type was unregistered, False if not found.
        """
        if form_type in self._registrations:
            del self._registrations[form_type]
            return True
        return False
    
    def is_registered(self, form_type: FormType) -> bool:
        """Check if a form type is registered.
        
        Args:
            form_type: Form type to check.
            
        Returns:
            bool: True if form type is registered.
        """
        return form_type in self._registrations
    
    def get_registered_types(self) -> List[FormType]:
        """Get list of all registered form types.
        
        Returns:
            List[FormType]: List of registered form types.
        """
        return list(self._registrations.keys())
    
    def get_registration(self, form_type: FormType) -> Optional[FormWidgetRegistration]:
        """Get registration information for a form type.
        
        Args:
            form_type: Form type to look up.
            
        Returns:
            FormWidgetRegistration: Registration info or None if not found.
        """
        return self._registrations.get(form_type)
    
    def create_widget(
        self, 
        form_type: FormType, 
        parent: Optional[QWidget] = None
    ) -> Optional[QWidget]:
        """Create a widget for the specified form type.
        
        Args:
            form_type: Type of form widget to create.
            parent: Parent widget for the new instance.
            
        Returns:
            QWidget: New widget instance or None if type not registered.
        """
        registration = self._registrations.get(form_type)
        if registration:
            return registration.create_widget(parent)
        return None
    
    def get_display_name(self, form_type: FormType) -> str:
        """Get display name for a form type.
        
        Args:
            form_type: Form type to look up.
            
        Returns:
            str: Display name or form type value if not registered.
        """
        registration = self._registrations.get(form_type)
        if registration:
            return registration.display_name
        return form_type.value
    
    def get_description(self, form_type: FormType) -> str:
        """Get description for a form type.
        
        Args:
            form_type: Form type to look up.
            
        Returns:
            str: Description or empty string if not registered.
        """
        registration = self._registrations.get(form_type)
        if registration:
            return registration.description
        return ""
    
    def _register_default_widgets(self) -> None:
        """Register default form widget types."""
        try:
            # Register ICS-213 widget
            from ..ics213_widget import ICS213Widget
            self.register(
                FormType.ICS_213,
                ICS213Widget,
                "General Message",
                "Used for transmitting messages and communications between ICS positions.",
                ""
            )
        except ImportError:
            pass  # ICS-213 widget not available
        
        try:
            # Register ICS-214 widget
            from ..ics214_widget import ICS214Widget
            self.register(
                FormType.ICS_214,
                ICS214Widget,
                "Activity Log",
                "Records chronological activities and resource assignments for personnel.",
                ""
            )
        except ImportError:
            pass  # ICS-214 widget not available
        
        try:
            # Register ICS-205 template widget
            try:
                from ..template_form_widget import create_ics205_widget
            except ImportError:
                # Try alternative import path for testing
                from ...ui.template_form_widget import create_ics205_widget
            
            self.register(
                FormType.ICS_205,
                create_ics205_widget,
                "Radio Communications Plan",
                "Radio frequency assignment and communication planning for emergency operations.",
                "",
                create_ics205_widget  # Use factory function as creation function
            )
        except ImportError as e:
            # Log the import error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"ICS-205 template not available: {e}")
            pass  # ICS-205 template not available
        
        try:
            # Register ICS-202 template widget
            try:
                from ..template_form_widget import create_ics202_widget
            except ImportError:
                # Try alternative import path for testing
                from ...ui.template_form_widget import create_ics202_widget
            
            self.register(
                FormType.ICS_202,
                create_ics202_widget,
                "Incident Objectives",
                "Incident objectives and command emphasis - cornerstone of the Incident Action Plan.",
                "",
                create_ics202_widget  # Use factory function as creation function
            )
        except ImportError as e:
            # Log the import error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"ICS-202 template not available: {e}")
            pass  # ICS-202 template not available


# Global registry instance (lazy initialization)
_registry = None

def _get_registry() -> FormWidgetRegistry:
    """Get the global registry instance, creating it if necessary."""
    global _registry
    if _registry is None:
        _registry = FormWidgetRegistry()
    return _registry


class FormWidgetFactory:
    """Main factory class for creating form widgets.
    
    This factory provides static methods for creating form widgets
    and managing the form widget registry. It serves as the primary
    interface for form widget creation throughout the application.
    
    Example:
        >>> widget = FormWidgetFactory.create_form_widget(FormType.ICS_213)
        >>> if widget:
        ...     widget.show()
    """
    
    @staticmethod
    def create_form_widget(
        form_type: FormType, 
        parent: Optional[QWidget] = None
    ) -> Optional[QWidget]:
        """Create a form widget for the specified type.
        
        Args:
            form_type: Type of form widget to create.
            parent: Parent widget for the new instance.
            
        Returns:
            QWidget: New form widget or None if type not supported.
        """
        return _get_registry().create_widget(form_type, parent)
    
    @staticmethod
    def create_form_widget_from_data(
        form_data: BaseForm, 
        parent: Optional[QWidget] = None
    ) -> Optional[QWidget]:
        """Create a form widget and load data into it.
        
        Args:
            form_data: Form data to load into the widget.
            parent: Parent widget for the new instance.
            
        Returns:
            QWidget: New form widget with data loaded or None if failed.
        """
        form_type = form_data.get_form_type()
        widget = _get_registry().create_widget(form_type, parent)
        
        if widget and isinstance(widget, FormWidgetInterface):
            widget.load_form_data(form_data)
        
        return widget
    
    @staticmethod
    def get_available_form_types() -> List[FormType]:
        """Get list of available form types.
        
        Returns:
            List[FormType]: List of form types that can be created.
        """
        return _get_registry().get_registered_types()
    
    @staticmethod
    def is_form_type_available(form_type: FormType) -> bool:
        """Check if a form type is available for creation.
        
        Args:
            form_type: Form type to check.
            
        Returns:
            bool: True if form type is available.
        """
        return _get_registry().is_registered(form_type)
    
    @staticmethod
    def get_form_display_name(form_type: FormType) -> str:
        """Get display name for a form type.
        
        Args:
            form_type: Form type to look up.
            
        Returns:
            str: Display name for the form type.
        """
        return _get_registry().get_display_name(form_type)
    
    @staticmethod
    def get_form_description(form_type: FormType) -> str:
        """Get description for a form type.
        
        Args:
            form_type: Form type to look up.
            
        Returns:
            str: Description of the form type.
        """
        return _get_registry().get_description(form_type)
    
    @staticmethod
    def register_form_widget(
        form_type: FormType,
        widget_class: Type,
        display_name: str,
        description: str = "",
        icon_path: str = "",
        creation_func: Optional[Callable] = None
    ) -> None:
        """Register a new form widget type.
        
        Args:
            form_type: Form type to register.
            widget_class: Widget class for the form type.
            display_name: Human-readable name.
            description: Description of the form type.
            icon_path: Optional icon file path.
            creation_func: Optional custom creation function.
        """
        _get_registry().register(
            form_type, widget_class, display_name, 
            description, icon_path, creation_func
        )
    
    @staticmethod
    def get_registry() -> FormWidgetRegistry:
        """Get the global widget registry.
        
        Returns:
            FormWidgetRegistry: The global registry instance.
        """
        return _get_registry()


class FormSelectionWidget(QWidget):
    """Widget for selecting form types from available options.
    
    This widget provides a user interface for selecting which type
    of form to create. It displays available form types with their
    descriptions and handles form creation.
    
    Signals:
        form_selected: Emitted when a form type is selected (FormType)
        form_creation_requested: Emitted when form creation is requested (FormType)
        
    Example:
        >>> selector = FormSelectionWidget()
        >>> selector.form_creation_requested.connect(handle_form_creation)
        >>> selector.show()
    """
    
    # Define signals
    form_selected = Signal(object)  # FormType
    form_creation_requested = Signal(object)  # FormType
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize form selection widget.
        
        Args:
            parent: Parent widget for proper resource management.
        """
        super().__init__(parent)
        self.setup_ui()
        self.populate_form_types()
    
    def setup_ui(self) -> None:
        """Set up the user interface."""
        if not PYSIDE6_AVAILABLE:
            return
        
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Select Form Type")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Form type selection
        form_group = QGroupBox("Available Forms")
        form_layout = QFormLayout(form_group)
        
        self.form_combo = QComboBox()
        self.form_combo.setMinimumWidth(300)
        form_layout.addRow("Form Type:", self.form_combo)
        
        # Description label
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setMinimumHeight(60)
        self.description_label.setStyleSheet(
            "QLabel { background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc; }"
        )
        form_layout.addRow("Description:", self.description_label)
        
        layout.addWidget(form_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.create_button = QPushButton("Create Form")
        self.create_button.setDefault(True)
        button_layout.addWidget(self.create_button)
        
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Connect signals
        self.form_combo.currentIndexChanged.connect(self.on_form_type_changed)
        self.create_button.clicked.connect(self.on_create_clicked)
        self.cancel_button.clicked.connect(self.close)
        
        # Initial state
        self.update_description()
    
    def populate_form_types(self) -> None:
        """Populate the form type combo box with available types."""
        if not PYSIDE6_AVAILABLE:
            return
        
        available_types = FormWidgetFactory.get_available_form_types()
        
        for form_type in available_types:
            display_name = FormWidgetFactory.get_form_display_name(form_type)
            self.form_combo.addItem(f"{form_type.value} - {display_name}", form_type)
        
        # Enable/disable create button based on availability
        self.create_button.setEnabled(len(available_types) > 0)
        
        if len(available_types) == 0:
            self.form_combo.addItem("No forms available", None)
            self.description_label.setText("No form types are currently available.")
    
    def get_selected_form_type(self) -> Optional[FormType]:
        """Get the currently selected form type.
        
        Returns:
            FormType: Selected form type or None if none selected.
        """
        if not PYSIDE6_AVAILABLE:
            return None
        
        return self.form_combo.currentData()
    
    def set_selected_form_type(self, form_type: FormType) -> bool:
        """Set the selected form type.
        
        Args:
            form_type: Form type to select.
            
        Returns:
            bool: True if form type was found and selected.
        """
        if not PYSIDE6_AVAILABLE:
            return False
        
        for i in range(self.form_combo.count()):
            if self.form_combo.itemData(i) == form_type:
                self.form_combo.setCurrentIndex(i)
                return True
        
        return False
    
    def update_description(self) -> None:
        """Update the description label based on selected form type."""
        if not PYSIDE6_AVAILABLE:
            return
        
        form_type = self.get_selected_form_type()
        if form_type:
            description = FormWidgetFactory.get_form_description(form_type)
            if description:
                self.description_label.setText(description)
            else:
                self.description_label.setText(f"Form type: {form_type.value}")
        else:
            self.description_label.setText("No form type selected.")
    
    def on_form_type_changed(self) -> None:
        """Handle form type selection change."""
        self.update_description()
        
        form_type = self.get_selected_form_type()
        if form_type:
            self.form_selected.emit(form_type)
    
    def on_create_clicked(self) -> None:
        """Handle create button click."""
        form_type = self.get_selected_form_type()
        if form_type:
            self.form_creation_requested.emit(form_type)
            self.close()


# Utility functions

def create_form_selector(parent: Optional[QWidget] = None) -> FormSelectionWidget:
    """Create a form type selection widget.
    
    Args:
        parent: Parent widget for the selector.
        
    Returns:
        FormSelectionWidget: New form selection widget.
    """
    return FormSelectionWidget(parent)


def register_form_widget(
    form_type: FormType,
    widget_class: Type,
    display_name: str,
    description: str = "",
    icon_path: str = ""
) -> None:
    """Register a new form widget type with the factory.
    
    Args:
        form_type: Form type to register.
        widget_class: Widget class for the form type.
        display_name: Human-readable name.
        description: Description of the form type.
        icon_path: Optional icon file path.
    """
    FormWidgetFactory.register_form_widget(
        form_type, widget_class, display_name, description, icon_path
    )


def get_available_form_types() -> List[FormType]:
    """Get list of available form types.
    
    Returns:
        List[FormType]: List of available form types.
    """
    return FormWidgetFactory.get_available_form_types()


def create_form_widget_by_type(
    form_type: FormType, 
    parent: Optional[QWidget] = None
) -> Optional[QWidget]:
    """Create a form widget for the specified type.
    
    Args:
        form_type: Type of form widget to create.
        parent: Parent widget for the new instance.
        
    Returns:
        QWidget: New form widget or None if type not supported.
    """
    return FormWidgetFactory.create_form_widget(form_type, parent)


# Example usage and testing
if __name__ == "__main__":
    if PYSIDE6_AVAILABLE:
        app = QApplication(sys.argv)
        
        # Create form selector
        selector = FormSelectionWidget()
        selector.setWindowTitle("RadioForms - Create New Form")
        selector.resize(400, 300)
        selector.show()
        
        # Handle form creation
        def handle_form_creation(form_type):
            print(f"Creating form of type: {form_type.value}")
            widget = FormWidgetFactory.create_form_widget(form_type)
            if widget:
                widget.setWindowTitle(f"RadioForms - {form_type.value}")
                widget.resize(800, 600)
                widget.show()
        
        selector.form_creation_requested.connect(handle_form_creation)
        
        sys.exit(app.exec())
    else:
        print("PySide6 not available - factory system available for testing")
        
        # Test factory functionality without UI
        available_types = get_available_form_types()
        print(f"Available form types: {[t.value for t in available_types]}")
        
        for form_type in available_types:
            display_name = FormWidgetFactory.get_form_display_name(form_type)
            description = FormWidgetFactory.get_form_description(form_type)
            print(f"{form_type.value}: {display_name} - {description}")
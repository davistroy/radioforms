#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base components for form editors.

This module provides the foundation classes for the form editor UI components,
implementing the architecture defined in form_editor_architecture.md.
"""

import datetime
from typing import Dict, Any, List, Optional, Set, Union, Callable, Type, TypeVar

from PySide6.QtCore import Qt, Signal, Slot, QObject, Property, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QPushButton, QCheckBox, QComboBox, QDateTimeEdit,
    QGridLayout, QScrollArea, QFrame, QSplitter, QTableView, 
    QHeaderView, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QIcon, QPixmap, QColor, QPalette, QFont, QFontMetrics

from radioforms.models.base_form import BaseFormModel, ValidationResult
from radioforms.models.form_model_registry import FormModelRegistry


class FieldValidationState:
    """
    Represents the validation state of a field.
    
    Attributes:
        is_valid: Whether the field is currently valid
        error_message: Error message if invalid
        is_modified: Whether the field has been modified by the user
        has_focus: Whether the field currently has focus
    """
    
    def __init__(self):
        """Initialize a new field validation state."""
        self.is_valid = True
        self.error_message = ""
        self.is_modified = False
        self.has_focus = False


class FormField(QWidget):
    """
    Base class for form fields.
    
    This class provides the foundation for all form fields, handling:
    - Field labels
    - Validation display
    - Value change notification
    - Two-way data binding
    
    Subclasses should implement:
    - _create_input_widget: Create the specific input widget
    - _get_value_from_widget: Get the current value from the widget
    - _set_value_to_widget: Set a value to the widget
    """
    
    # Signal emitted when the field value changes
    value_changed = Signal(object)
    
    def __init__(self, field_name: str, label: str, required: bool = False, 
                parent: Optional[QWidget] = None):
        """
        Initialize a form field.
        
        Args:
            field_name: Name of the field (used for data binding)
            label: Label to display for the field
            required: Whether the field is required
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._field_name = field_name
        self._label_text = label
        self._required = required
        self._validation_state = FieldValidationState()
        self._value = None
        self._validators = []
        self._binding_getter = None
        self._binding_setter = None
        
        # Initialize UI
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)
        
        # Label
        label_layout = QHBoxLayout()
        label_layout.setContentsMargins(0, 0, 0, 0)
        
        self._label = QLabel(self._label_text)
        label_layout.addWidget(self._label)
        
        if self._required:
            required_label = QLabel("*")
            required_label.setStyleSheet("color: red;")
            label_layout.addWidget(required_label)
            
        label_layout.addStretch()
        main_layout.addLayout(label_layout)
        
        # Create the input widget (implemented by subclasses)
        self._input_widget = self._create_input_widget()
        main_layout.addWidget(self._input_widget)
        
        # Error message label
        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: red; font-size: 10pt;")
        self._error_label.setVisible(False)
        main_layout.addWidget(self._error_label)
        
        # Set up validation display timer
        self._validation_timer = QTimer(self)
        self._validation_timer.setSingleShot(True)
        self._validation_timer.timeout.connect(self._on_validation_timer)
        
    def _create_input_widget(self) -> QWidget:
        """
        Create the specific input widget for this field type.
        
        Returns:
            The input widget
            
        Note:
            This method should be implemented by subclasses.
        """
        # Default implementation returns a QLineEdit
        widget = QLineEdit()
        widget.textChanged.connect(self._on_value_changed)
        return widget
        
    def _get_value_from_widget(self) -> Any:
        """
        Get the current value from the input widget.
        
        Returns:
            The current value
            
        Note:
            This method should be implemented by subclasses.
        """
        # Default implementation for QLineEdit
        if isinstance(self._input_widget, QLineEdit):
            return self._input_widget.text()
        return None
        
    def _set_value_to_widget(self, value: Any):
        """
        Set a value to the input widget.
        
        Args:
            value: The value to set
            
        Note:
            This method should be implemented by subclasses.
        """
        # Default implementation for QLineEdit
        if isinstance(self._input_widget, QLineEdit):
            self._input_widget.setText(str(value) if value is not None else "")
            
    def _on_value_changed(self, *args):
        """
        Handle value changes in the input widget.
        
        This method is called when the user changes the value in the input widget.
        It updates the internal value, validates it, and emits the value_changed signal.
        """
        # Get the new value from the widget
        new_value = self._get_value_from_widget()
        
        # Update internal value
        old_value = self._value
        self._value = new_value
        
        # Mark as modified
        self._validation_state.is_modified = True
        
        # Validate after a short delay
        self._validation_timer.start(500)
        
        # Emit value changed signal
        if new_value != old_value:
            self.value_changed.emit(new_value)
            
            # Update bound object if binding is set
            if self._binding_setter:
                try:
                    self._binding_setter(new_value)
                except Exception as e:
                    print(f"Error in binding setter: {e}")
                    
    def _on_validation_timer(self):
        """Handle validation timer timeout."""
        # Skip validation if the field has focus and isn't marked as modified
        if self._validation_state.has_focus and not self._validation_state.is_modified:
            return
            
        # Validate the current value
        self.validate()
        
    def set_value(self, value: Any, notify: bool = True):
        """
        Set the field value.
        
        Args:
            value: The value to set
            notify: Whether to emit value_changed signal
        """
        if self._value == value:
            return
            
        self._value = value
        self._set_value_to_widget(value)
        
        if notify:
            self.value_changed.emit(value)
            
    def get_value(self) -> Any:
        """
        Get the current field value.
        
        Returns:
            The current value
        """
        return self._value
        
    def add_validator(self, validator: Callable[[Any], Union[bool, str]]):
        """
        Add a validator function.
        
        Args:
            validator: Function that takes a value and returns True if valid,
                      or an error message string if invalid
        """
        self._validators.append(validator)
        
    def validate(self) -> bool:
        """
        Validate the current value.
        
        Returns:
            True if the value is valid, False otherwise
        """
        # Skip validation if not modified and not required
        if not self._validation_state.is_modified and not self._required:
            return True
            
        # Check if empty and required
        if self._required and (self._value is None or self._value == ""):
            self._validation_state.is_valid = False
            self._validation_state.error_message = f"{self._label_text} is required."
            self._update_validation_display()
            return False
            
        # Run through validators
        for validator in self._validators:
            result = validator(self._value)
            if result is not True:
                self._validation_state.is_valid = False
                self._validation_state.error_message = result if isinstance(result, str) else "Invalid value."
                self._update_validation_display()
                return False
                
        # If we get here, the value is valid
        self._validation_state.is_valid = True
        self._validation_state.error_message = ""
        self._update_validation_display()
        return True
        
    def _update_validation_display(self):
        """Update the UI to reflect the current validation state."""
        if not self._validation_state.is_valid:
            # Show error styling
            self._input_widget.setStyleSheet("border: 1px solid red;")
            self._error_label.setText(self._validation_state.error_message)
            self._error_label.setVisible(True)
        else:
            # Show normal styling
            self._input_widget.setStyleSheet("")
            self._error_label.setVisible(False)
            
    def bind_to(self, obj: Any, getter: Callable[[], Any], setter: Callable[[Any], None]):
        """
        Bind this field to an object property.
        
        Args:
            obj: The object to bind to
            getter: Function to get the property value
            setter: Function to set the property value
        """
        self._binding_getter = getter
        self._binding_setter = setter
        
        # Initial sync from object to field
        try:
            value = getter()
            self.set_value(value, notify=False)
        except Exception as e:
            print(f"Error in binding getter: {e}")
            
    def bind_to_attr(self, obj: Any, attr_name: str):
        """
        Bind this field to an object attribute.
        
        Args:
            obj: The object to bind to
            attr_name: Name of the attribute
        """
        getter = lambda: getattr(obj, attr_name)
        setter = lambda value: setattr(obj, attr_name, value)
        self.bind_to(obj, getter, setter)
        
    def get_field_name(self) -> str:
        """
        Get the field name.
        
        Returns:
            The field name
        """
        return self._field_name
        
    def get_validation_state(self) -> FieldValidationState:
        """
        Get the current validation state.
        
        Returns:
            The validation state
        """
        return self._validation_state
        
    def reset(self):
        """Reset the field to its initial state."""
        self._value = None
        self._set_value_to_widget(None)
        self._validation_state.is_valid = True
        self._validation_state.error_message = ""
        self._validation_state.is_modified = False
        self._update_validation_display()
        

class TextField(FormField):
    """Text field for single-line text input."""
    
    def _create_input_widget(self) -> QWidget:
        """Create a QLineEdit widget."""
        widget = QLineEdit()
        widget.textChanged.connect(self._on_value_changed)
        return widget
        
    def _get_value_from_widget(self) -> str:
        """Get the text value from QLineEdit."""
        return self._input_widget.text()
        
    def _set_value_to_widget(self, value: Any):
        """Set the text value to QLineEdit."""
        self._input_widget.setText(str(value) if value is not None else "")
        

class TextAreaField(FormField):
    """Text field for multi-line text input."""
    
    def _create_input_widget(self) -> QWidget:
        """Create a QTextEdit widget."""
        widget = QTextEdit()
        widget.textChanged.connect(lambda: self._on_value_changed())
        return widget
        
    def _get_value_from_widget(self) -> str:
        """Get the text value from QTextEdit."""
        return self._input_widget.toPlainText()
        
    def _set_value_to_widget(self, value: Any):
        """Set the text value to QTextEdit."""
        self._input_widget.setPlainText(str(value) if value is not None else "")
        

class DateTimeField(FormField):
    """Field for date and time input."""
    
    def _create_input_widget(self) -> QWidget:
        """Create a QDateTimeEdit widget."""
        widget = QDateTimeEdit()
        widget.setCalendarPopup(True)
        widget.setDateTime(datetime.datetime.now())
        widget.dateTimeChanged.connect(lambda dt: self._on_value_changed())
        return widget
        
    def _get_value_from_widget(self) -> datetime.datetime:
        """Get the datetime value from QDateTimeEdit."""
        qt_datetime = self._input_widget.dateTime()
        return datetime.datetime(
            qt_datetime.date().year(),
            qt_datetime.date().month(),
            qt_datetime.date().day(),
            qt_datetime.time().hour(),
            qt_datetime.time().minute(),
            qt_datetime.time().second()
        )
        
    def _set_value_to_widget(self, value: Any):
        """Set the datetime value to QDateTimeEdit."""
        if isinstance(value, datetime.datetime):
            from PySide6.QtCore import QDateTime
            qt_datetime = QDateTime(
                value.year, value.month, value.day,
                value.hour, value.minute, value.second
            )
            self._input_widget.setDateTime(qt_datetime)
            

class ChoiceField(FormField):
    """Field for selecting from a list of options."""
    
    def __init__(self, field_name: str, label: str, choices: List[tuple], 
                required: bool = False, parent: Optional[QWidget] = None):
        """
        Initialize a choice field.
        
        Args:
            field_name: Name of the field
            label: Label to display
            choices: List of (value, display_text) tuples
            required: Whether the field is required
            parent: Parent widget
        """
        self._choices = choices
        super().__init__(field_name, label, required, parent)
        
    def _create_input_widget(self) -> QWidget:
        """Create a QComboBox widget."""
        widget = QComboBox()
        
        # Add choices
        for value, display_text in self._choices:
            widget.addItem(display_text, value)
            
        widget.currentIndexChanged.connect(lambda idx: self._on_value_changed())
        return widget
        
    def _get_value_from_widget(self) -> Any:
        """Get the selected value from QComboBox."""
        return self._input_widget.currentData()
        
    def _set_value_to_widget(self, value: Any):
        """Set the selected value in QComboBox."""
        # Find the index with the matching value
        for i in range(self._input_widget.count()):
            if self._input_widget.itemData(i) == value:
                self._input_widget.setCurrentIndex(i)
                return
                
        # If not found and we have items, select the first one
        if self._input_widget.count() > 0:
            self._input_widget.setCurrentIndex(0)
            

class CheckboxField(FormField):
    """Field for boolean input."""
    
    def _create_input_widget(self) -> QWidget:
        """Create a QCheckBox widget."""
        widget = QCheckBox(self._label_text)
        widget.stateChanged.connect(lambda state: self._on_value_changed())
        
        # Hide the label since the checkbox has text
        self._label.setVisible(False)
        
        return widget
        
    def _get_value_from_widget(self) -> bool:
        """Get the checked state from QCheckBox."""
        return self._input_widget.isChecked()
        
    def _set_value_to_widget(self, value: Any):
        """Set the checked state to QCheckBox."""
        self._input_widget.setChecked(bool(value))
        

class ValidationSummary(QWidget):
    """
    Widget that displays a summary of validation errors.
    
    This widget collects validation errors from multiple fields
    and displays them in a list.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize a validation summary widget."""
        super().__init__(parent)
        self._fields = {}  # field_name -> FormField
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Header
        header = QLabel("Please correct the following errors:")
        header.setStyleSheet("color: red; font-weight: bold;")
        main_layout.addWidget(header)
        
        # Error list
        self._error_list = QVBoxLayout()
        main_layout.addLayout(self._error_list)
        
        # Initially hide
        self.setVisible(False)
        
    def add_field(self, field: FormField):
        """
        Add a field to monitor for validation errors.
        
        Args:
            field: The field to monitor
        """
        field_name = field.get_field_name()
        self._fields[field_name] = field
        
        # Connect to value changed signal to update validation
        field.value_changed.connect(lambda _: self.update_summary())
        
    def clear_fields(self):
        """Clear all monitored fields."""
        self._fields.clear()
        
    def update_summary(self):
        """Update the validation summary based on current field states."""
        # Clear existing errors
        for i in reversed(range(self._error_list.count())):
            item = self._error_list.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
                
        # Collect errors from fields
        has_errors = False
        for field_name, field in self._fields.items():
            validation_state = field.get_validation_state()
            if not validation_state.is_valid:
                has_errors = True
                error_text = f"{field.get_field_name()}: {validation_state.error_message}"
                error_label = QLabel(error_text)
                error_label.setStyleSheet("color: red;")
                self._error_list.addWidget(error_label)
                
        # Show/hide based on error presence
        self.setVisible(has_errors)
        

class FormHeader(QWidget):
    """
    Header widget for form editors.
    
    This widget displays the form title, form type, ID, and state indicator.
    It also provides global actions like save, print, export.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize a form header widget."""
        super().__init__(parent)
        
        self._form_title = ""
        self._form_type = ""
        self._form_id = ""
        self._form_state = ""
        self._form_state_display = ""
        
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)
        
        # Left side: form info
        info_layout = QVBoxLayout()
        
        # Title
        self._title_label = QLabel()
        self._title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        info_layout.addWidget(self._title_label)
        
        # Type and ID
        self._type_id_label = QLabel()
        info_layout.addWidget(self._type_id_label)
        
        main_layout.addLayout(info_layout)
        main_layout.addStretch()
        
        # Right side: state and actions
        action_layout = QVBoxLayout()
        
        # State indicator
        state_layout = QHBoxLayout()
        state_layout.addWidget(QLabel("State:"))
        self._state_indicator = QLabel()
        state_layout.addWidget(self._state_indicator)
        action_layout.addLayout(state_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self._save_button = QPushButton("Save")
        button_layout.addWidget(self._save_button)
        
        self._print_button = QPushButton("Print")
        button_layout.addWidget(self._print_button)
        
        self._export_button = QPushButton("Export")
        button_layout.addWidget(self._export_button)
        
        action_layout.addLayout(button_layout)
        
        main_layout.addLayout(action_layout)
        
        # Set a frame style
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setLineWidth(1)
        
    def set_form_info(self, title: str, form_type: str, form_id: str = ""):
        """
        Set the form information.
        
        Args:
            title: Form title
            form_type: Form type identifier
            form_id: Form ID (empty for new forms)
        """
        self._form_title = title
        self._form_type = form_type
        self._form_id = form_id
        
        # Update labels
        self._title_label.setText(title)
        
        type_id_text = form_type
        if form_id:
            type_id_text += f" (ID: {form_id})"
        self._type_id_label.setText(type_id_text)
        
    def set_form_state(self, state: str, display_text: str):
        """
        Set the form state.
        
        Args:
            state: State identifier
            display_text: Text to display for the state
        """
        self._form_state = state
        self._form_state_display = display_text
        
        # Update state indicator
        color = "blue"  # Default color
        
        # Set color based on state
        if state == "draft":
            color = "blue"
        elif state in ["approved", "finalized"]:
            color = "green"
        elif state in ["transmitted"]:
            color = "orange"
        elif state in ["received", "replied"]:
            color = "purple"
        elif state in ["archived"]:
            color = "gray"
            
        self._state_indicator.setText(f"<span style='color:{color};'>{display_text}</span>")
        
    def connect_save(self, callback: Callable[[], None]):
        """
        Connect the save button to a callback.
        
        Args:
            callback: Function to call when save button is clicked
        """
        self._save_button.clicked.connect(callback)
        
    def connect_print(self, callback: Callable[[], None]):
        """
        Connect the print button to a callback.
        
        Args:
            callback: Function to call when print button is clicked
        """
        self._print_button.clicked.connect(callback)
        
    def connect_export(self, callback: Callable[[], None]):
        """
        Connect the export button to a callback.
        
        Args:
            callback: Function to call when export button is clicked
        """
        self._export_button.clicked.connect(callback)
        

class FormFooter(QWidget):
    """
    Footer widget for form editors.
    
    This widget displays the validation summary, state transition controls,
    and form metadata.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize a form footer widget."""
        super().__init__(parent)
        
        self._validation_summary = ValidationSummary()
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)
        
        # Validation summary
        main_layout.addWidget(self._validation_summary)
        
        # State transition controls
        self._state_controls = QWidget()
        state_layout = QHBoxLayout()
        state_layout.setContentsMargins(0, 0, 0, 0)
        self._state_controls.setLayout(state_layout)
        
        # We'll add buttons dynamically, but set up the container now
        main_layout.addWidget(self._state_controls)
        
        # Metadata
        metadata_layout = QGridLayout()
        
        metadata_layout.addWidget(QLabel("Created:"), 0, 0)
        self._created_label = QLabel()
        metadata_layout.addWidget(self._created_label, 0, 1)
        
        metadata_layout.addWidget(QLabel("Modified:"), 0, 2)
        self._modified_label = QLabel()
        metadata_layout.addWidget(self._modified_label, 0, 3)
        
        metadata_layout.addWidget(QLabel("Version:"), 1, 0)
        self._version_label = QLabel()
        metadata_layout.addWidget(self._version_label, 1, 1)
        
        main_layout.addLayout(metadata_layout)
        
        # Set a frame style
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setLineWidth(1)
        
    def get_validation_summary(self) -> ValidationSummary:
        """
        Get the validation summary widget.
        
        Returns:
            The validation summary widget
        """
        return self._validation_summary
        
    def set_metadata(self, created: Optional[datetime.datetime] = None, 
                    modified: Optional[datetime.datetime] = None, 
                    version: Optional[str] = None):
        """
        Set the form metadata.
        
        Args:
            created: Creation date and time
            modified: Last modified date and time
            version: Version identifier
        """
        if created:
            self._created_label.setText(created.strftime("%Y-%m-%d %H:%M"))
        else:
            self._created_label.setText("N/A")
            
        if modified:
            self._modified_label.setText(modified.strftime("%Y-%m-%d %H:%M"))
        else:
            self._modified_label.setText("N/A")
            
        if version:
            self._version_label.setText(version)
        else:
            self._version_label.setText("1.0")
            
    def set_state_transitions(self, transitions: List[tuple]):
        """
        Set the available state transitions.
        
        Args:
            transitions: List of (action_id, display_text, enabled) tuples
        """
        # Clear existing buttons
        layout = self._state_controls.layout()
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
                
        # Add transition buttons
        for action_id, display_text, enabled in transitions:
            button = QPushButton(display_text)
            button.setProperty("action_id", action_id)
            button.setEnabled(enabled)
            layout.addWidget(button)
            
        # Add stretch to keep buttons aligned left
        layout.addStretch()
        
    def connect_transition(self, action_id: str, callback: Callable[[], None]):
        """
        Connect a state transition button to a callback.
        
        Args:
            action_id: Action identifier
            callback: Function to call when the button is clicked
        """
        layout = self._state_controls.layout()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget() and isinstance(item.widget(), QPushButton):
                button = item.widget()
                if button.property("action_id") == action_id:
                    button.clicked.connect(callback)
                    break
                    

class FormEditorContainer(QWidget):
    """
    Container widget for form editors.
    
    This is the top-level component for form editing, managing:
    - Form loading and saving
    - Validation coordination
    - Subcomponent interaction
    """
    
    # Signal emitted when the form is saved
    form_saved = Signal(object)
    
    # Signal emitted when the form state changes
    state_changed = Signal(str, str)  # state_id, display_text
    
    def __init__(self, form_registry: FormModelRegistry, 
                form: Optional[BaseFormModel] = None, 
                form_id: Optional[str] = None, 
                form_type: Optional[str] = None, 
                parent: Optional[QWidget] = None):
        """
        Initialize a form editor container.
        
        Args:
            form_registry: FormModelRegistry instance
            form: Existing form to edit
            form_id: ID of form to load
            form_type: Type of form to create
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._form_registry = form_registry
        self._form = None
        self._fields = {}  # field_name -> FormField
        
        # Initialize UI
        self._init_ui()
        
        # Load or create form
        if form:
            self.set_form(form)
        elif form_id:
            self.load_form(form_id)
        elif form_type:
            self.create_form(form_type)
            
    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)
        
        # Header
        self._header = FormHeader()
        main_layout.addWidget(self._header)
        
        # Connect header buttons
        self._header.connect_save(self._on_save)
        self._header.connect_print(self._on_print)
        self._header.connect_export(self._on_export)
        
        # Body (will be added when form is set)
        self._body_container = QWidget()
        body_layout = QVBoxLayout()
        body_layout.setContentsMargins(10, 10, 10, 10)
        self._body_container.setLayout(body_layout)
        
        # Scroll area for body
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self._body_container)
        main_layout.addWidget(scroll_area)
        
        # Footer
        self._footer = FormFooter()
        main_layout.addWidget(self._footer)
        
    def _on_save(self):
        """Handle save button click."""
        # Validate the form first
        if not self.validate():
            return
            
        # Save the form
        if self._form:
            try:
                form_id = self._form_registry.save_form(self._form)
                self.form_saved.emit(self._form)
            except Exception as e:
                print(f"Error saving form: {e}")
                # TODO: Show error message to user
                
    def _on_print(self):
        """Handle print button click."""
        # TODO: Implement printing
        print("Print not yet implemented")
        
    def _on_export(self):
        """Handle export button click."""
        # TODO: Implement export
        print("Export not yet implemented")
        
    def create_form(self, form_type: str):
        """
        Create a new form of the specified type.
        
        Args:
            form_type: Type of form to create
        """
        # Create a new form through the registry
        form = self._form_registry.create_form(form_type)
        if form:
            self.set_form(form)
            
    def load_form(self, form_id: str, version_id: Optional[str] = None):
        """
        Load an existing form.
        
        Args:
            form_id: ID of the form to load
            version_id: Optional version ID to load
        """
        # Load the form through the registry
        form = self._form_registry.load_form(form_id, version_id)
        if form:
            self.set_form(form)
            
    def set_form(self, form: BaseFormModel):
        """
        Set the form to edit.
        
        Args:
            form: The form to edit
        """
        self._form = form
        
        # Update header
        if hasattr(form, 'get_form_type'):
            form_type = form.get_form_type()
        else:
            form_type = type(form).__name__
            
        self._header.set_form_info(
            title=self._get_form_title(form),
            form_type=form_type,
            form_id=form.form_id if hasattr(form, 'form_id') else ""
        )
        
        # Update state if available
        if hasattr(form, 'state'):
            state = form.state
            if hasattr(state, 'value'):  # For enum values
                state_id = state.value
            else:
                state_id = str(state)
                
            self._header.set_form_state(state_id, self._get_state_display(state))
            
        # Clear existing body
        body_layout = self._body_container.layout()
        while body_layout.count():
            item = body_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Create form body
        body_widget = self._create_form_body(form)
        if body_widget:
            body_layout.addWidget(body_widget)
            
        # Connect validation summary
        validation_summary = self._footer.get_validation_summary()
        validation_summary.clear_fields()
        for field_name, field in self._fields.items():
            validation_summary.add_field(field)
            
        # Set form metadata
        created = getattr(form, 'created_at', None)
        modified = getattr(form, 'last_modified', None)
        version = getattr(form, 'form_version', None)
        self._footer.set_metadata(created, modified, version)
        
        # Set state transitions
        self._update_state_transitions()
        
    def _create_form_body(self, form: BaseFormModel) -> QWidget:
        """
        Create the form body widget.
        
        This method should be implemented by subclasses to create
        a form-specific body widget.
        
        Args:
            form: The form to create the body for
            
        Returns:
            The form body widget
        """
        # Basic implementation for testing
        # Subclasses should override this to create a proper form body
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Create a generic label
        label = QLabel("Form body not implemented for this form type.")
        layout.addWidget(label)
        
        return widget
        
    def _get_form_title(self, form: BaseFormModel) -> str:
        """
        Get the title for the form.
        
        Args:
            form: The form to get the title for
            
        Returns:
            The form title
        """
        # Default to form type + General Form
        if hasattr(form, 'get_form_type'):
            return f"{form.get_form_type()} Form"
        else:
            return "Form Editor"
            
    def _get_state_display(self, state) -> str:
        """
        Get the display text for a form state.
        
        Args:
            state: The form state
            
        Returns:
            The display text for the state
        """
        # Convert state to string and capitalize
        if hasattr(state, 'value'):
            state_str = state.value
        else:
            state_str = str(state)
            
        return state_str.capitalize()
        
    def _update_state_transitions(self):
        """Update the state transition buttons based on the current form state."""
        if not self._form:
            return
            
        # Get available transitions
        transitions = []
        
        # Check if form has state transitions
        if hasattr(self._form, 'state'):
            current_state = self._form.state
            
            # ICS-213 form transitions
            if hasattr(self._form, 'approve'):
                can_approve = (
                    hasattr(current_state, 'value') and 
                    current_state.value == 'draft'
                )
                transitions.append(('approve', 'Approve', can_approve))
                
            if hasattr(self._form, 'transmit'):
                can_transmit = (
                    hasattr(current_state, 'value') and 
                    current_state.value == 'approved'
                )
                transitions.append(('transmit', 'Transmit', can_transmit))
                
            if hasattr(self._form, 'receive'):
                can_receive = (
                    hasattr(current_state, 'value') and 
                    current_state.value == 'transmitted'
                )
                transitions.append(('receive', 'Receive', can_receive))
                
            if hasattr(self._form, 'reply'):
                can_reply = (
                    hasattr(current_state, 'value') and 
                    current_state.value == 'received'
                )
                transitions.append(('reply', 'Reply', can_reply))
                
            # ICS-214 form transitions
            if hasattr(self._form, 'finalize'):
                can_finalize = (
                    hasattr(current_state, 'value') and 
                    current_state.value == 'draft'
                )
                transitions.append(('finalize', 'Finalize', can_finalize))
                
            if hasattr(self._form, 'review'):
                can_review = (
                    hasattr(current_state, 'value') and 
                    current_state.value == 'finalized'
                )
                transitions.append(('review', 'Review', can_review))
                
            # Common transitions for all forms
            if hasattr(self._form, 'archive'):
                can_archive = (
                    hasattr(current_state, 'value') and 
                    current_state.value != 'archived'
                )
                transitions.append(('archive', 'Archive', can_archive))
                
        # Set transitions in footer
        self._footer.set_state_transitions(transitions)
        
        # Connect transition buttons
        for action_id, _, _ in transitions:
            self._connect_transition(action_id)
            
    def _connect_transition(self, action_id: str):
        """
        Connect a state transition button to its handler.
        
        Args:
            action_id: The action identifier
        """
        if action_id == 'approve':
            self._footer.connect_transition(action_id, self._on_approve)
        elif action_id == 'transmit':
            self._footer.connect_transition(action_id, self._on_transmit)
        elif action_id == 'receive':
            self._footer.connect_transition(action_id, self._on_receive)
        elif action_id == 'reply':
            self._footer.connect_transition(action_id, self._on_reply)
        elif action_id == 'finalize':
            self._footer.connect_transition(action_id, self._on_finalize)
        elif action_id == 'review':
            self._footer.connect_transition(action_id, self._on_review)
        elif action_id == 'archive':
            self._footer.connect_transition(action_id, self._on_archive)
            
    def _on_approve(self):
        """Handle approve button click."""
        if hasattr(self._form, 'approve'):
            # TODO: Show dialog to collect approver information
            name = "John Doe"
            position = "Operations Chief"
            signature = "JDoe"
            
            self._form.approve(name, position, signature)
            self._update_state_after_transition()
            
    def _on_transmit(self):
        """Handle transmit button click."""
        if hasattr(self._form, 'transmit'):
            # TODO: Show dialog to collect transmission information
            operator = "Jane Smith"
            date_time = datetime.datetime.now()
            
            self._form.transmit(operator, date_time)
            self._update_state_after_transition()
            
    def _on_receive(self):
        """Handle receive button click."""
        if hasattr(self._form, 'receive'):
            # TODO: Show dialog to collect receiver information
            operator = "Bob Johnson"
            date_time = datetime.datetime.now()
            
            self._form.receive(operator, date_time)
            self._update_state_after_transition()
            
    def _on_reply(self):
        """Handle reply button click."""
        if hasattr(self._form, 'reply'):
            # TODO: Show dialog to collect reply information
            reply_text = "Reply acknowledged"
            name = "Alice Williams"
            position = "Planning Chief"
            signature = "AWilliams"
            
            self._form.reply(reply_text, name, position, signature)
            self._update_state_after_transition()
            
    def _on_finalize(self):
        """Handle finalize button click."""
        if hasattr(self._form, 'finalize'):
            # TODO: Show dialog to collect preparer information
            name = "John Doe"
            position = "Operations Chief"
            signature = "JDoe"
            
            self._form.finalize(name, position, signature)
            self._update_state_after_transition()
            
    def _on_review(self):
        """Handle review button click."""
        if hasattr(self._form, 'review'):
            # TODO: Show dialog to collect reviewer information
            name = "Jane Smith"
            position = "Planning Chief"
            signature = "JSmith"
            
            self._form.review(name, position, signature)
            self._update_state_after_transition()
            
    def _on_archive(self):
        """Handle archive button click."""
        if hasattr(self._form, 'archive'):
            self._form.archive()
            self._update_state_after_transition()
            
    def _update_state_after_transition(self):
        """Update UI after a state transition."""
        if hasattr(self._form, 'state'):
            state = self._form.state
            if hasattr(state, 'value'):  # For enum values
                state_id = state.value
            else:
                state_id = str(state)
                
            # Update header state
            self._header.set_form_state(state_id, self._get_state_display(state))
            
            # Update available transitions
            self._update_state_transitions()
            
            # Emit state changed signal
            self.state_changed.emit(state_id, self._get_state_display(state))
            
            # Save form after state change
            self._on_save()
            
    def register_field(self, field: FormField):
        """
        Register a field for validation and binding.
        
        Args:
            field: The field to register
        """
        field_name = field.get_field_name()
        self._fields[field_name] = field
        
    def bind_fields_to_form(self):
        """Bind all registered fields to the form."""
        if not self._form:
            return
            
        for field_name, field in self._fields.items():
            # Try property accessor first
            if hasattr(self._form, field_name):
                field.bind_to_attr(self._form, field_name)
            # Try getter/setter methods
            elif (hasattr(self._form, f"get_{field_name}") and 
                 hasattr(self._form, f"set_{field_name}")):
                getter = lambda: getattr(self._form, f"get_{field_name}")()
                setter = lambda value: getattr(self._form, f"set_{field_name}")(value)
                field.bind_to(self._form, getter, setter)
            # Try a direct attribute with underscore prefix
            elif hasattr(self._form, f"_{field_name}"):
                field.bind_to_attr(self._form, f"_{field_name}")
                
    def validate(self) -> bool:
        """
        Validate the form.
        
        Returns:
            True if the form is valid, False otherwise
        """
        # Validate all fields
        all_valid = True
        for field_name, field in self._fields.items():
            if not field.validate():
                all_valid = False
                
        # Update validation summary
        self._footer.get_validation_summary().update_summary()
        
        # Also validate the form model if it has a validate method
        if all_valid and hasattr(self._form, 'validate'):
            result = self._form.validate()
            if hasattr(result, 'is_valid'):
                all_valid = result.is_valid
                
                # TODO: Show form-level validation errors
                
        return all_valid

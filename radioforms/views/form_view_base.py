#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base class for form views.

This module provides the base class for all form views in the application,
defining common UI functionality and interfaces.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QTextEdit, QPushButton, 
    QScrollArea, QFrame, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QFont, QColor, QPalette

from radioforms.models.base_form import BaseFormModel, ValidationResult


class FormViewBase(QWidget):
    """
    Base class for all form views.
    
    This abstract base class provides common functionality for form displays
    and defines the interface that all form views must implement.
    """
    
    # Signals
    form_modified = Signal()
    form_saved = Signal()
    validation_failed = Signal(list)  # List of validation error messages
    
    def __init__(self, form_model=None, parent=None):
        """
        Initialize a form view.
        
        Args:
            form_model: Form model to display and edit
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._form_model = form_model
        self._modified = False
        self._read_only = False
        
        # Common UI elements that all form views will have
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # Form title section
        self.title_frame = QFrame()
        self.title_frame.setFrameShape(QFrame.StyledPanel)
        self.title_frame.setFrameShadow(QFrame.Raised)
        self.title_layout = QVBoxLayout(self.title_frame)
        
        self.form_title_label = QLabel()
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.form_title_label.setFont(title_font)
        self.form_title_label.setAlignment(Qt.AlignCenter)
        
        self.form_subtitle_label = QLabel()
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle_font.setItalic(True)
        self.form_subtitle_label.setFont(subtitle_font)
        self.form_subtitle_label.setAlignment(Qt.AlignCenter)
        
        self.title_layout.addWidget(self.form_title_label)
        self.title_layout.addWidget(self.form_subtitle_label)
        
        # Scroll area for form content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Form content widget (to be filled by subclasses)
        self.form_content = QWidget()
        self.form_layout = QVBoxLayout(self.form_content)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(15)
        
        self.scroll_area.setWidget(self.form_content)
        
        # Button bar for actions
        self.button_frame = QFrame()
        self.button_layout = QHBoxLayout(self.button_frame)
        self.button_layout.setContentsMargins(0, 10, 0, 0)
        
        self.save_button = QPushButton("Save")
        self.print_button = QPushButton("Print")
        self.export_button = QPushButton("Export")
        self.validate_button = QPushButton("Validate")
        
        self.button_layout.addWidget(self.validate_button)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.export_button)
        self.button_layout.addWidget(self.print_button)
        self.button_layout.addWidget(self.save_button)
        
        # Combine all sections
        self.main_layout.addWidget(self.title_frame)
        self.main_layout.addWidget(self.scroll_area, 1)
        self.main_layout.addWidget(self.button_frame)
        
        # Connect signals
        self.save_button.clicked.connect(self.save_form)
        self.print_button.clicked.connect(self.print_form)
        self.export_button.clicked.connect(self.export_form)
        self.validate_button.clicked.connect(self.validate_form)
        
        # Apply initial styling
        self._apply_styling()
        
        # Set up the form if provided
        if form_model:
            self.set_form(form_model)
    
    def _apply_styling(self):
        """Apply consistent styling to the form view."""
        # Set form border
        self.setStyleSheet("""
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 5px;
            }
            
            QLineEdit, QTextEdit {
                border: 1px solid #aaaaaa;
                border-radius: 3px;
                padding: 3px;
            }
            
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #aaaaaa;
                border-radius: 4px;
                padding: 5px 10px;
            }
            
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
    
    def set_form(self, form_model):
        """
        Set the form model to display and edit.
        
        Args:
            form_model: Form model instance
        """
        self._form_model = form_model
        if form_model:
            self._setup_form_display()
            self._connect_form_signals()
            self._modified = False
            self.update_ui_from_model()
    
    def get_form(self):
        """
        Get the current form model.
        
        Returns:
            The current form model instance
        """
        return self._form_model
    
    def is_modified(self):
        """
        Check if the form has been modified.
        
        Returns:
            True if the form has been modified, False otherwise
        """
        return self._modified
    
    def set_read_only(self, read_only):
        """
        Set the read-only state of the form view.
        
        Args:
            read_only: True for read-only, False for editable
        """
        self._read_only = read_only
        self._update_read_only_state()
    
    def is_read_only(self):
        """
        Check if the form view is read-only.
        
        Returns:
            True if the form view is read-only, False otherwise
        """
        return self._read_only
    
    def _update_read_only_state(self):
        """Update the UI elements based on the read-only state."""
        # Common UI update logic
        self.save_button.setEnabled(not self._read_only)
        
        # Subclasses will implement form-specific field updates
    
    def _setup_form_display(self):
        """Set up the form display based on the form model."""
        # Base class updates common elements
        form_type = self._form_model.get_form_type()
        self.form_title_label.setText(f"{form_type} Form")
        
        # Subclasses must implement form-specific setup
    
    def _connect_form_signals(self):
        """Connect signals from the form model to view update handlers."""
        # Base implementation - subclasses will add form-specific connections
        pass
    
    def update_ui_from_model(self):
        """Update UI fields from the form model's data."""
        # Must be implemented by subclasses
        raise NotImplementedError("Subclasses must implement update_ui_from_model()")
    
    def update_model_from_ui(self):
        """Update the form model from UI field values."""
        # Must be implemented by subclasses
        raise NotImplementedError("Subclasses must implement update_model_from_ui()")
    
    @Slot()
    def save_form(self):
        """Save the current form state."""
        if not self._form_model:
            return
            
        # Update model from UI
        self.update_model_from_ui()
        
        # Validate the form
        valid = self.validate_form()
        if not valid:
            return
            
        # Signal for handling by controller
        self.form_saved.emit()
        self._modified = False
    
    @Slot()
    def print_form(self):
        """Print the current form."""
        # Update model from UI
        self.update_model_from_ui()
        
        # This will be handled by controller
        QMessageBox.information(self, "Print", "Printing functionality will be implemented soon.")
    
    @Slot()
    def export_form(self):
        """Export the current form."""
        # Update model from UI
        self.update_model_from_ui()
        
        # This will be handled by controller
        QMessageBox.information(self, "Export", "Export functionality will be implemented soon.")
    
    @Slot()
    def validate_form(self):
        """
        Validate the current form.
        
        Returns:
            True if validation succeeded, False otherwise
        """
        if not self._form_model:
            return False
            
        # Update model from UI
        self.update_model_from_ui()
        
        # Validate the model
        result = self._form_model.validate()
        
        if not result.is_valid:
            # Create list of error messages
            error_messages = []
            for field, message in result.errors.items():
                error_messages.append(f"{field}: {message}")
            
            # Show validation errors
            self._show_validation_errors(result)
            
            # Emit signal with error messages
            self.validation_failed.emit(error_messages)
            return False
            
        return True
    
    def _show_validation_errors(self, validation_result: ValidationResult):
        """
        Display validation errors to the user.
        
        Args:
            validation_result: Validation result containing errors
        """
        if not validation_result.is_valid:
            error_text = "Please correct the following issues:\n\n"
            for field, error in validation_result.errors.items():
                error_text += f"• {error}\n"
            
            QMessageBox.warning(self, "Validation Failed", error_text)
    
    @Slot(str, object, object)
    def _on_form_field_changed(self, field_name, old_value, new_value):
        """
        Handle a form field change event.
        
        Args:
            field_name: Name of the changed field
            old_value: Previous value
            new_value: New value
        """
        # Mark the form as modified
        self._modified = True
        
        # Emit form modified signal
        self.form_modified.emit()
        
        # Subclasses can implement field-specific UI updates
    
    def sizeHint(self):
        """
        Get the recommended size for the widget.
        
        Returns:
            Recommended QSize for the widget
        """
        return QSize(800, 600)

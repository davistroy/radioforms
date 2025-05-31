"""Template form widget wrapper for GUI integration.

This module provides a wrapper widget that integrates template-based forms
(like ICS-205) with the existing form factory system and main window.

Classes:
    TemplateFormWidget: Wrapper widget for template-based forms
    
Functions:
    create_template_form_widget: Factory function for creating template widgets
"""

import logging
from typing import Optional, Dict, Any, Type, Callable
from pathlib import Path

# Handle PySide6 imports gracefully for testing environments
try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
        QMessageBox, QFrame, QScrollArea
    )
    from PySide6.QtCore import Signal, Qt, QTimer
    from PySide6.QtGui import QFont
    PYSIDE6_AVAILABLE = True
except ImportError:
    # Create stub classes for testing environments
    PYSIDE6_AVAILABLE = False
    
    class QWidget:
        def __init__(self, parent=None): pass
        def setLayout(self, layout): pass
        def show(self): pass
        def hide(self): pass
        def update(self): pass
    
    class Signal:
        def __init__(self, *args): pass
        def connect(self, slot): pass
        def emit(self, *args): pass
    
    class QVBoxLayout:
        def __init__(self, parent=None): pass
        def addWidget(self, widget): pass
        def addLayout(self, layout): pass
    
    class QHBoxLayout:
        def __init__(self): pass
        def addWidget(self, widget): pass
        def addStretch(self): pass
    
    class QPushButton:
        def __init__(self, text, parent=None): pass
        def clicked(self): return Signal()
        def setEnabled(self, enabled): pass
    
    class QLabel:
        def __init__(self, text="", parent=None): pass
        def setText(self, text): pass
        def setWordWrap(self, wrap): pass
        def setFont(self, font): pass
    
    class QMessageBox:
        @staticmethod
        def information(parent, title, text): pass
        @staticmethod
        def warning(parent, title, text): pass
        @staticmethod
        def critical(parent, title, text): pass
    
    class QFont:
        def __init__(self): pass
        def setBold(self, bold): pass
        def setPointSize(self, size): pass
    
    Qt = type('Qt', (), {})()

# Import form interfaces
try:
    from ..forms.ics213 import ICS213Form
    from ..models.base_form import BaseForm, FormType
    from .forms.form_factory import FormWidgetInterface
except ImportError:
    # For standalone testing
    BaseForm = object
    FormType = None
    FormWidgetInterface = object
    ICS213Form = None

logger = logging.getLogger(__name__)


class TemplateFormWidget(QWidget):
    """Wrapper widget for template-based forms.
    
    This widget provides a bridge between the template system and the existing
    form factory/main window architecture. It wraps template forms to provide
    the same interface as the legacy form widgets.
    
    Signals:
        form_changed: Emitted when form data changes
        form_saved: Emitted when form is saved (form_id)
        form_loaded: Emitted when form is loaded (form_id)
        validation_changed: Emitted when validation status changes (is_valid)
    
    Example:
        >>> from ui.forms.templates.ics205_template import ICS205Template
        >>> template = ICS205Template()
        >>> widget = TemplateFormWidget(template, form_service)
        >>> widget.show()
    """
    
    # Define signals
    form_changed = Signal() if PYSIDE6_AVAILABLE else Signal()
    form_saved = Signal(int) if PYSIDE6_AVAILABLE else Signal()
    form_loaded = Signal(int) if PYSIDE6_AVAILABLE else Signal()
    validation_changed = Signal(bool) if PYSIDE6_AVAILABLE else Signal()
    
    def __init__(self, template_form, form_service=None, parent: Optional[QWidget] = None):
        """Initialize template form widget.
        
        Args:
            template_form: Template form instance (e.g., ICS205Template)
            form_service: Optional form service for database operations
            parent: Parent widget for proper resource management
        """
        super().__init__(parent)
        
        self.template_form = template_form
        self.form_service = form_service
        self.current_form_id = None
        self.is_dirty = False
        
        logger.info(f"Initializing template form widget for {template_form.form_type}")
        
        # Setup the user interface
        self._setup_ui()
        
        # Connect internal signals if template supports them
        self._connect_template_signals()
        
        logger.debug("Template form widget initialization complete")
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        if not PYSIDE6_AVAILABLE:
            return
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Form header with title and controls
        header_layout = QHBoxLayout()
        
        # Form title
        title_label = QLabel(getattr(self.template_form, 'form_title', 'Template Form'))
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Form controls
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._on_save_clicked)
        self.save_button.setEnabled(False)
        header_layout.addWidget(self.save_button)
        
        self.validate_button = QPushButton("Validate")
        self.validate_button.clicked.connect(self._on_validate_clicked)
        header_layout.addWidget(self.validate_button)
        
        main_layout.addLayout(header_layout)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setWordWrap(True)
        main_layout.addWidget(self.status_label)
        
        # Template form widget (create and embed)
        try:
            if hasattr(self.template_form, 'create_form_widget'):
                template_widget = self.template_form.create_form_widget()
                if template_widget:
                    main_layout.addWidget(template_widget)
                    logger.debug("Template widget created and added successfully")
                else:
                    logger.warning("Template create_form_widget returned None")
                    self._add_error_placeholder("Template widget creation failed")
            else:
                logger.error("Template form missing create_form_widget method")
                self._add_error_placeholder("Template does not support widget creation")
        except Exception as e:
            logger.error(f"Failed to create template widget: {e}")
            self._add_error_placeholder(f"Error creating template: {e}")
    
    def _add_error_placeholder(self, message: str) -> None:
        """Add error placeholder when template widget creation fails."""
        if PYSIDE6_AVAILABLE:
            error_label = QLabel(f"Template Error: {message}")
            error_label.setWordWrap(True)
            error_label.setStyleSheet("color: red; padding: 20px; background-color: #ffeeee; border: 1px solid red;")
            self.layout().addWidget(error_label)
    
    def _connect_template_signals(self) -> None:
        """Connect to template signals if available."""
        # Note: Template forms may not have signals yet
        # This is a placeholder for future signal connections
        pass
    
    def _on_save_clicked(self) -> None:
        """Handle save button click."""
        if not self.form_service:
            self._update_status("No form service available for saving", error=True)
            return
        
        try:
            # Get form data from template
            form_data = self.get_form_data()
            if not form_data:
                self._update_status("No form data to save", error=True)
                return
            
            # TODO: Implement template form saving through form service
            # This requires extending the form service to handle template forms
            self._update_status("Template form saving not yet implemented")
            
            # For now, just mark as saved
            self.is_dirty = False
            self.save_button.setEnabled(False)
            self.form_changed.emit()
            
            logger.info("Template form save completed")
            
        except Exception as e:
            error_msg = f"Save failed: {e}"
            self._update_status(error_msg, error=True)
            logger.error(error_msg)
    
    def _on_validate_clicked(self) -> None:
        """Handle validate button click."""
        try:
            is_valid = self.validate_form()
            
            if is_valid:
                self._update_status("✅ Form validation passed")
                if PYSIDE6_AVAILABLE:
                    QMessageBox.information(
                        self,
                        "Form Validation",
                        "✅ Form is valid and ready for use."
                    )
            else:
                # Get validation details if available
                validation_errors = getattr(self.template_form, 'get_validation_errors', lambda: ["Form has validation errors"])()
                error_text = "\n• ".join(["Form validation failed:"] + validation_errors)
                
                self._update_status("❌ Form validation failed")
                if PYSIDE6_AVAILABLE:
                    QMessageBox.warning(
                        self,
                        "Form Validation Failed",
                        error_text
                    )
            
            self.validation_changed.emit(is_valid)
            
        except Exception as e:
            error_msg = f"Validation error: {e}"
            self._update_status(error_msg, error=True)
            logger.error(error_msg)
    
    def _update_status(self, message: str, error: bool = False) -> None:
        """Update status label with message.
        
        Args:
            message: Status message to display
            error: Whether this is an error message
        """
        if PYSIDE6_AVAILABLE and hasattr(self, 'status_label'):
            self.status_label.setText(message)
            if error:
                self.status_label.setStyleSheet("color: red;")
            else:
                self.status_label.setStyleSheet("color: green;")
        
        logger.info(f"Status: {message}")
    
    # FormWidgetInterface implementation
    
    def load_form_data(self, form_data) -> None:
        """Load form data into the template widget.
        
        Args:
            form_data: Form data to load (BaseForm or dict)
        """
        try:
            if hasattr(form_data, 'to_dict'):
                # BaseForm instance
                data_dict = form_data.to_dict()
            elif isinstance(form_data, dict):
                # Dictionary data
                data_dict = form_data
            else:
                logger.error(f"Unsupported form data type: {type(form_data)}")
                return
            
            # Load data into template
            if hasattr(self.template_form, 'set_data'):
                self.template_form.set_data(data_dict)
            elif hasattr(self.template_form, 'import_data'):
                self.template_form.import_data(data_dict)
            else:
                logger.warning("Template form does not support data loading")
            
            self.is_dirty = False
            self.save_button.setEnabled(False) if PYSIDE6_AVAILABLE else None
            self.form_loaded.emit(0)  # TODO: Use actual form ID
            
            self._update_status("Form data loaded successfully")
            logger.debug("Template form data loaded successfully")
            
        except Exception as e:
            error_msg = f"Failed to load form data: {e}"
            self._update_status(error_msg, error=True)
            logger.error(error_msg)
    
    def get_form_data(self):
        """Get current form data from the template widget.
        
        Returns:
            Form data or None if not available
        """
        try:
            if hasattr(self.template_form, 'get_data'):
                return self.template_form.get_data()
            elif hasattr(self.template_form, 'export_data'):
                return self.template_form.export_data()
            else:
                logger.warning("Template form does not support data export")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get form data: {e}")
            return None
    
    def validate_form(self) -> bool:
        """Validate the current form data.
        
        Returns:
            bool: True if form is valid, False otherwise
        """
        try:
            if hasattr(self.template_form, 'validate'):
                return self.template_form.validate()
            elif hasattr(self.template_form, 'is_valid'):
                return self.template_form.is_valid()
            else:
                # No validation method available
                logger.warning("Template form does not support validation")
                return True
                
        except Exception as e:
            logger.error(f"Form validation failed: {e}")
            return False
    
    def clear_form(self) -> None:
        """Clear all form data from the template widget."""
        try:
            # Get default data and set it
            if hasattr(self.template_form, 'get_default_data'):
                default_data = self.template_form.get_default_data()
                if hasattr(self.template_form, 'set_data'):
                    self.template_form.set_data(default_data)
            elif hasattr(self.template_form, 'clear'):
                self.template_form.clear()
            else:
                logger.warning("Template form does not support clearing")
            
            self.is_dirty = False
            self.save_button.setEnabled(False) if PYSIDE6_AVAILABLE else None
            self._update_status("Form cleared")
            
        except Exception as e:
            error_msg = f"Failed to clear form: {e}"
            self._update_status(error_msg, error=True)
            logger.error(error_msg)
    
    def get_form_type(self) -> Optional[str]:
        """Get the form type handled by this widget.
        
        Returns:
            Form type string or None if not available
        """
        if hasattr(self.template_form, 'form_type'):
            return self.template_form.form_type
        elif hasattr(self.template_form, 'metadata') and hasattr(self.template_form.metadata, 'form_id'):
            return self.template_form.metadata.form_id
        else:
            return "template_form"
    
    def is_dirty_form(self) -> bool:
        """Check if form has unsaved changes.
        
        Returns:
            bool: True if form has unsaved changes
        """
        return self.is_dirty
    
    def set_read_only(self, read_only: bool) -> None:
        """Set the widget to read-only mode.
        
        Args:
            read_only: Whether to enable read-only mode
        """
        # TODO: Implement read-only mode for template forms
        logger.debug(f"Read-only mode {'enabled' if read_only else 'disabled'}")
    
    def has_unsaved_changes(self) -> bool:
        """Check if the form has unsaved changes.
        
        Returns:
            bool: True if there are unsaved changes
        """
        return self.is_dirty
    
    def get_form_title(self) -> str:
        """Get the form title.
        
        Returns:
            str: Form title
        """
        if hasattr(self.template_form, 'form_title'):
            return self.template_form.form_title
        elif hasattr(self.template_form, 'metadata') and hasattr(self.template_form.metadata, 'name'):
            return self.template_form.metadata.name
        else:
            return f"Template Form ({self.get_form_type()})"
    
    def get_form(self):
        """Get the underlying form object.
        
        Returns:
            The template form instance
        """
        return self.template_form


# Factory functions

def create_template_form_widget(template_class: Type, form_service=None, parent: Optional[QWidget] = None, **kwargs) -> TemplateFormWidget:
    """Factory function for creating template form widgets.
    
    Args:
        template_class: Template class to instantiate
        form_service: Optional form service for database operations
        parent: Parent widget
        **kwargs: Arguments to pass to template constructor
        
    Returns:
        TemplateFormWidget: New template form widget
    """
    try:
        # Create template instance
        template_instance = template_class(**kwargs)
        
        # Create wrapper widget
        widget = TemplateFormWidget(template_instance, form_service, parent)
        
        logger.info(f"Created template form widget for {template_class.__name__}")
        return widget
        
    except Exception as e:
        logger.error(f"Failed to create template form widget: {e}")
        # Return empty widget as fallback
        return TemplateFormWidget(None, form_service, parent)


def create_ics205_widget(form_service=None, parent: Optional[QWidget] = None, **kwargs) -> TemplateFormWidget:
    """Convenience function for creating ICS-205 template widget.
    
    Args:
        form_service: Optional form service for database operations
        parent: Parent widget
        **kwargs: Arguments to pass to ICS205Template constructor
        
    Returns:
        TemplateFormWidget: New ICS-205 template form widget
    """
    try:
        from .forms.templates.ics205_template import ICS205Template
        return create_template_form_widget(ICS205Template, form_service, parent, **kwargs)
    except ImportError as e:
        logger.error(f"Failed to import ICS205Template: {e}")
        return TemplateFormWidget(None, form_service, parent)


# Registration helper for form factory integration

def register_template_forms():
    """Register template-based forms with the form factory system."""
    try:
        from .forms.form_factory import FormWidgetFactory, register_form_widget
        from ..models.base_form import FormType
        
        # Register ICS-205 template
        register_form_widget(
            FormType.ICS_205,
            create_ics205_widget,  # Use factory function as creation function
            "Radio Communications Plan",
            "Radio frequency assignment and communication planning for emergency operations",
            "",  # No icon path for now
            create_ics205_widget  # Creation function
        )
        
        logger.info("Template forms registered with form factory")
        
    except ImportError as e:
        logger.warning(f"Could not register template forms: {e}")


# Initialize registration when module is imported
if __name__ == "__main__":
    # Test the widget creation
    if PYSIDE6_AVAILABLE:
        from PySide6.QtWidgets import QApplication
        import sys
        
        app = QApplication(sys.argv)
        
        # Test template widget creation
        widget = create_ics205_widget()
        widget.setWindowTitle("ICS-205 Template Test")
        widget.show()
        
        sys.exit(app.exec())
    else:
        print("PySide6 not available - template widget system available for testing")
        widget = create_ics205_widget()
        print(f"Created widget: {widget}")
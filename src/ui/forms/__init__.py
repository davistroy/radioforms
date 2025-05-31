"""Form UI components and factory system.

This package provides the form widget factory system and UI components
for creating and managing different types of ICS forms within the
RadioForms application.

Modules:
    form_factory: Main factory system for creating form widgets
    
Classes:
    FormWidgetFactory: Factory for creating form widgets by type
    FormSelectionWidget: Widget for selecting form types
    FormWidgetInterface: Abstract interface for form widgets

Functions:
    create_form_widget_by_type: Create form widget by type
    get_available_form_types: Get list of available form types
    register_form_widget: Register new form widget types
"""

# Export main factory classes and functions
try:
    from .form_factory import (
        FormWidgetFactory,
        FormSelectionWidget, 
        FormWidgetInterface,
        FormWidgetRegistry,
        create_form_widget_by_type,
        get_available_form_types,
        register_form_widget,
        create_form_selector
    )
    
    __all__ = [
        'FormWidgetFactory',
        'FormSelectionWidget',
        'FormWidgetInterface', 
        'FormWidgetRegistry',
        'create_form_widget_by_type',
        'get_available_form_types',
        'register_form_widget',
        'create_form_selector'
    ]
    
except ImportError:
    # Handle cases where dependencies aren't available
    __all__ = []
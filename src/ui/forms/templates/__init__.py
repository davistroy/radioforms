"""Form Template System for RadioForms.

This package provides a reusable template system for creating ICS forms
efficiently while maintaining consistency and following CLAUDE.md principles.

The template system consists of:
- Base template classes for fields, sections, and forms
- Concrete field implementations (text, table, contact, etc.)
- Section templates for common form areas (header, approval, etc.)
- Layout managers for different form arrangements
- Configuration-driven form creation system

Example:
    >>> from .registry.template_registry import TemplateRegistry
    >>> from .base.form_template import FormTemplate
    >>> 
    >>> # Create form from configuration
    >>> form_template = TemplateRegistry.create_form_from_config('ics205.yaml')
    >>> form_widget = form_template.create_form_widget()

Classes:
    FieldTemplate: Base class for all field types
    SectionTemplate: Base class for form sections
    FormTemplate: Base class for complete forms
    TemplateRegistry: Central registry for template types

Functions:
    create_form_from_config: Factory function for configuration-based forms
    register_template: Register new template types

Notes:
    All templates follow CLAUDE.md principles:
    - Simple first, add complexity only when needed
    - Explicit configuration over implicit behavior
    - Clear error messages and graceful degradation
    - Performance optimized for emergency operations
"""

# Core template system exports
from .base.field_template import FieldTemplate, ValidationResult, ValidationRule
from .base.section_template import SectionTemplate, LayoutType
from .base.form_template import FormTemplate

# Field template exports
from .fields.text_field import TextFieldTemplate, TextAreaFieldTemplate

# Section template exports  
# (Will be added as implemented)

# Registry exports (will be implemented later)
# from .registry.template_registry import TemplateRegistry

__all__ = [
    # Base classes
    'FieldTemplate',
    'SectionTemplate', 
    'FormTemplate',
    'ValidationResult',
    'ValidationRule',
    'LayoutType',
    
    # Field templates
    'TextFieldTemplate',
    'TextAreaFieldTemplate'
]

# Version info
__version__ = '1.0.0'
__author__ = 'RadioForms Development Team'
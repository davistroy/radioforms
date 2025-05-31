# RadioForms Template System Developer Guide

**Version**: 1.0  
**Last Updated**: May 31, 2024  
**Target Audience**: Developers adding new ICS forms to RadioForms

---

## Overview

The RadioForms Template System provides a comprehensive framework for rapidly implementing new ICS forms with minimal code duplication. This system reduces development time by 50-70% through reusable components and configuration-driven development.

### Key Benefits

- **Rapid Development**: New forms implemented through configuration vs. custom coding
- **Consistency**: All forms follow standardized UI patterns and validation rules
- **Maintainability**: Shared components reduce code duplication and testing overhead
- **Extensibility**: New field types and sections easily added to the system

### Architecture Overview

```
Template System Architecture:
├── base/
│   ├── field_template.py      # Abstract field base + validation framework
│   ├── section_template.py    # Abstract section base + layout management
│   └── form_template.py       # Abstract form base + overall coordination
├── fields/
│   ├── text_field.py         # Text input fields (single/multi-line)
│   ├── date_field.py         # Date/time/datetime pickers
│   └── table_field.py        # Dynamic tables with add/remove rows
├── sections/
│   ├── header_section.py     # Standard ICS form headers
│   └── approval_section.py   # Signature and approval sections
└── [form_name]_template.py   # Complete form implementations
```

---

## Quick Start: Adding a New Form

### Step 1: Analyze the Form Requirements

Before implementation, complete this analysis:

1. **Field Inventory**: List all fields with types (text, date, table, choice)
2. **Section Organization**: Group fields into logical sections
3. **Validation Rules**: Identify required fields, format requirements, business rules
4. **Layout Requirements**: Single/multi-column, tabbed sections, special layouts

### Step 2: Create Form Template File

Create a new file: `src/ui/forms/templates/ics[XXX]_template.py`

```python
"""ICS-[XXX] [Form Name] form template.

This module provides the complete ICS-[XXX] [Form Name] form
implementation using the RadioForms template system.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Import base classes
from .base.form_template import FormTemplate, FormMetadata
from .sections.header_section import HeaderSectionTemplate
from .sections.approval_section import ApprovalSectionTemplate
from .fields.text_field import TextFieldTemplate
from .fields.date_field import DateFieldTemplate

logger = logging.getLogger(__name__)

class ICS[XXX]Template(FormTemplate):
    """ICS-[XXX] [Form Name] form template."""
    
    def __init__(self, **kwargs):
        """Initialize ICS-[XXX] form template."""
        
        # Create form metadata
        metadata = FormMetadata(
            form_id="ics[xxx]",
            name="ICS [XXX] - [FORM TITLE]",
            version="2020.1",
            description="[Form description and purpose]",
            fema_compliant=True,
            tags=["[tag1]", "[tag2]", "[tag3]"]
        )
        
        # Create form sections
        sections = self._create_form_sections(**kwargs)
        
        # Initialize base form template
        super().__init__(
            metadata=metadata,
            sections=sections,
            layout="vertical",
            scrollable=True
        )
    
    def _create_form_sections(self, **kwargs) -> List:
        """Create all sections for the ICS-[XXX] form."""
        sections = []
        
        # 1. Header Section
        header_section = HeaderSectionTemplate(
            form_title="[FORM TITLE]",
            form_number="ICS [XXX]",
            include_form_number=True,
            include_page_info=True
        )
        sections.append(header_section)
        
        # 2. Add your custom sections here
        
        # 3. Approval Section
        approval_section = ApprovalSectionTemplate(
            include_approval=True,
            include_reviewed=False,
            signature_height=60,
            form_type="ics[xxx]"
        )
        sections.append(approval_section)
        
        return sections
```

### Step 3: Implement Required Methods

Add these methods to your form template for full integration:

```python
# Required properties for integration
@property
def form_type(self) -> str:
    """Get the form type identifier."""
    return self.metadata.form_id

@property
def form_title(self) -> str:
    """Get the form title."""
    return self.metadata.name

def get_default_data(self) -> Dict[str, Any]:
    """Get default data structure for the form."""
    return {
        'incident_name': '',
        'operational_period': '',
        'prepared_by': '',
        # Add all form fields here
    }

def set_data(self, data: Dict[str, Any]) -> None:
    """Set form data using simplified interface."""
    # Convert simple data format to full form data structure
    form_data = {
        'sections': {
            'header': {
                'incident_name': data.get('incident_name', ''),
                'operational_period': data.get('operational_period', ''),
                'prepared_by': data.get('prepared_by', '')
            },
            # Add other sections here
        }
    }
    self.set_form_data(form_data)

def get_data(self) -> Dict[str, Any]:
    """Get form data using simplified interface."""
    form_data = self.get_form_data()
    sections = form_data.get('sections', {})
    
    # Extract data in simplified format
    header = sections.get('header', {})
    
    return {
        'incident_name': header.get('incident_name', ''),
        'operational_period': header.get('operational_period', ''),
        'prepared_by': header.get('prepared_by', ''),
        # Add all form fields here
    }

def export_data(self) -> Dict[str, Any]:
    """Export form data with metadata."""
    return {
        'metadata': {
            'form_type': self.form_type,
            'form_title': self.form_title,
            'version': self.metadata.version,
            'export_date': datetime.now().isoformat()
        },
        'form_data': self.get_data()
    }

def import_data(self, export_data: Dict[str, Any]) -> bool:
    """Import form data from exported format."""
    try:
        if 'form_data' in export_data:
            self.set_data(export_data['form_data'])
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to import data: {e}")
        return False
```

### Step 4: Register with Form Factory

Add your form to the form factory system:

```python
# In src/ui/forms/form_factory.py
from .templates.ics[xxx]_template import ICS[XXX]Template

# Add to form type enumeration
class FormType(Enum):
    # ... existing forms
    ICS_[XXX] = "ics[xxx]"

# Add to factory creation method
def create_form_widget_by_type(form_type: FormType) -> QWidget:
    if form_type == FormType.ICS_[XXX]:
        template = ICS[XXX]Template()
        return template.create_form_widget()
    # ... existing forms
```

---

## Field Types Reference

### TextFieldTemplate

For single-line text inputs:

```python
text_field = TextFieldTemplate(
    field_id="field_name",
    label="Field Label",
    placeholder="Enter text...",
    max_length=100,
    required=True,
    validation_rules=[RequiredRule(), MaxLengthRule(100)]
)
```

### TextAreaFieldTemplate

For multi-line text inputs:

```python
textarea_field = TextAreaFieldTemplate(
    field_id="description",
    label="Description",
    placeholder="Enter detailed description...",
    max_length=2000,
    min_rows=4,
    required=False
)
```

### DateFieldTemplate

For date inputs:

```python
date_field = DateFieldTemplate(
    field_id="date_prepared",
    label="Date Prepared",
    required=True,
    default_to_today=True
)
```

### TimeFieldTemplate

For time inputs:

```python
time_field = TimeFieldTemplate(
    field_id="time_prepared",
    label="Time Prepared",
    required=True,
    format_24_hour=True
)
```

### DateTimeFieldTemplate

For combined date/time inputs:

```python
datetime_field = DateTimeFieldTemplate(
    field_id="event_datetime",
    label="Event Date/Time",
    required=True,
    default_to_now=False
)
```

### TableFieldTemplate

For dynamic tables with add/remove capability:

```python
# Define table columns
columns = [
    TableColumn(
        column_id="name",
        label="Name",
        column_type=ColumnType.TEXT,
        width=150,
        required=True
    ),
    TableColumn(
        column_id="position",
        label="Position",
        column_type=ColumnType.CHOICE,
        width=120,
        choices=["Chief", "Deputy", "Officer"],
        required=True
    )
]

# Create table field
table_field = TableFieldTemplate(
    field_id="personnel_table",
    label="Personnel Assignments",
    columns=columns,
    min_rows=5,
    max_rows=50,
    allow_add=True,
    allow_remove=True,
    show_row_numbers=True
)
```

---

## Section Types Reference

### HeaderSectionTemplate

Standard ICS form header with incident information:

```python
header_section = HeaderSectionTemplate(
    form_title="INCIDENT [PURPOSE]",
    form_number="ICS [XXX]",
    include_form_number=True,
    include_page_info=True,
    include_incident_name=True,
    include_operational_period=True,
    include_date_prepared=True
)
```

### ApprovalSectionTemplate

Standard approval section with signatures:

```python
approval_section = ApprovalSectionTemplate(
    include_approval=True,
    include_reviewed=True,
    signature_height=60,
    form_type="ics[xxx]"
)
```

### Custom Section Template

For specialized sections:

```python
from .base.section_template import DefaultSectionTemplate, LayoutType

custom_section = DefaultSectionTemplate(
    section_id="custom_section",
    title="CUSTOM SECTION TITLE",
    fields=[field1, field2, field3],
    layout=LayoutType.SINGLE_COLUMN,
    collapsible=False,
    visible=True
)
```

---

## Validation Framework

### Built-in Validation Rules

```python
from .base.field_template import RequiredRule, MaxLengthRule

# Required field validation
required_rule = RequiredRule("Field Name")

# Maximum length validation
max_length_rule = MaxLengthRule(100, "Field Name")

# Apply to field
field = TextFieldTemplate(
    field_id="sample_field",
    label="Sample Field",
    validation_rules=[required_rule, max_length_rule]
)
```

### Custom Validation Rules

```python
from .base.field_template import ValidationRule, ValidationResult

class EmailValidationRule(ValidationRule):
    """Validates email format."""
    
    def __init__(self, field_label: str = "Email"):
        self.field_label = field_label
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate email format."""
        if not value:
            return ValidationResult.success()
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, str(value)):
            return ValidationResult.error(f"{self.field_label} must be a valid email address")
        
        return ValidationResult.success()

# Use custom rule
email_field = TextFieldTemplate(
    field_id="email",
    label="Email Address",
    validation_rules=[EmailValidationRule("Email Address")]
)
```

---

## Testing Your Form

### Create Integration Test

Create a test file: `test_ics[xxx]_template.py`

```python
#!/usr/bin/env python3
"""Integration test for ICS-[XXX] template."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_ics[xxx]_creation():
    """Test ICS-[XXX] template creation."""
    from src.ui.forms.templates.ics[xxx]_template import ICS[XXX]Template
    
    # Create template
    ics[xxx] = ICS[XXX]Template()
    
    # Test basic properties
    assert ics[xxx].form_type == "ics[xxx]"
    assert ics[xxx].form_title is not None
    assert hasattr(ics[xxx], 'get_default_data')
    
    return True

def test_form_data_handling():
    """Test form data operations."""
    from src.ui.forms.templates.ics[xxx]_template import ICS[XXX]Template
    
    ics[xxx] = ICS[XXX]Template()
    
    # Test data setting and getting
    test_data = {
        'incident_name': 'Test Incident',
        'operational_period': '2024-05-31',
        'prepared_by': 'Test User'
    }
    
    ics[xxx].set_data(test_data)
    retrieved_data = ics[xxx].get_data()
    
    assert retrieved_data['incident_name'] == test_data['incident_name']
    
    return True

def test_export_import():
    """Test export/import functionality."""
    from src.ui.forms.templates.ics[xxx]_template import ICS[XXX]Template
    
    ics[xxx] = ICS[XXX]Template()
    
    # Set test data
    test_data = {'incident_name': 'Export Test'}
    ics[xxx].set_data(test_data)
    
    # Test export
    export_data = ics[xxx].export_data()
    assert 'metadata' in export_data
    assert 'form_data' in export_data
    
    # Test import
    import_success = ics[xxx].import_data(export_data)
    assert import_success == True
    
    return True

if __name__ == "__main__":
    tests = [
        ("ICS-[XXX] Creation", test_ics[xxx]_creation),
        ("Form Data Handling", test_form_data_handling),
        ("Export/Import", test_export_import)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                print(f"✓ {test_name}")
                passed += 1
            else:
                print(f"✗ {test_name}")
        except Exception as e:
            print(f"✗ {test_name}: {e}")
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
```

### Run Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run your form test
python test_ics[xxx]_template.py

# Run template system tests
python -m pytest test_template_system.py -v

# Run integration tests
python test_phase4_integration.py
```

---

## Performance Guidelines

### Template Creation
- Target: <100ms for template instantiation
- Lazy loading: Create widgets only when needed
- Cache validation rules and column definitions

### Data Operations
- Target: <50ms for data setting/getting
- Batch validation: Validate sections together
- Minimize data transformation overhead

### Memory Usage
- Target: <50MB additional memory per form
- Clean up widgets properly with parent-child relationships
- Use weak references for large data structures

---

## Common Patterns

### Multi-Page Forms

```python
def _create_form_sections(self, **kwargs) -> List:
    sections = []
    
    # Page 1 sections
    sections.extend(self._create_page1_sections())
    
    # Page 2 sections  
    sections.extend(self._create_page2_sections())
    
    return sections

def _create_page1_sections(self):
    # Implementation for page 1
    pass

def _create_page2_sections(self):
    # Implementation for page 2
    pass
```

### Conditional Sections

```python
def _create_form_sections(self, **kwargs) -> List:
    sections = []
    
    # Always include header
    sections.append(self._create_header_section())
    
    # Conditional section based on configuration
    if kwargs.get('include_resources', True):
        sections.append(self._create_resources_section())
    
    # Always include approval
    sections.append(self._create_approval_section())
    
    return sections
```

### Related Form Links

```python
def _create_related_forms_section(self):
    """Create section with links to related forms."""
    related_field = TextFieldTemplate(
        field_id="related_ics202",
        label="Related ICS-202 Reference",
        placeholder="Enter ICS-202 form ID if applicable",
        required=False
    )
    
    return DefaultSectionTemplate(
        section_id="related_forms",
        title="RELATED FORMS",
        fields=[related_field]
    )
```

---

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all imports use relative paths within templates
   - Check that parent directories have `__init__.py` files

2. **Widget Creation Failures**
   - Verify PySide6 availability in production
   - Use mock widgets in testing environment

3. **Validation Not Working**
   - Check that validation rules are properly instantiated
   - Ensure ValidationResult objects are returned

4. **Data Export Issues**
   - Verify all form fields are included in data methods
   - Check section ID consistency between creation and data access

### Debug Tips

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test template creation without GUI
template = ICS[XXX]Template()
print(f"Sections: {len(template.sections)}")
for section in template.sections:
    print(f"  - {section.section_id}: {section.title}")

# Test data flow
test_data = {'incident_name': 'Debug Test'}
template.set_data(test_data)
retrieved = template.get_data()
print(f"Data round-trip: {retrieved}")
```

---

## Best Practices

1. **Follow CLAUDE.md Principles**
   - Simple first: Start with basic functionality
   - Explicit over implicit: Clear naming and structure
   - Test everything: 100% integration test coverage

2. **Code Organization**
   - One form per file
   - Group related fields into sections
   - Use descriptive field and section IDs

3. **User Experience**
   - Logical tab order for keyboard navigation
   - Clear field labels and help text
   - Consistent validation error messages

4. **Performance**
   - Lazy load expensive operations
   - Cache frequently accessed data
   - Profile before optimizing

5. **Documentation**
   - Document field purposes and validation rules
   - Include examples in docstrings
   - Maintain change history

---

## Support

For questions or issues with template development:

1. **Check Integration Tests**: Run existing tests to verify system health
2. **Review Existing Templates**: Use ICS-205 as reference implementation
3. **Performance Issues**: Profile with test data before optimization
4. **Validation Problems**: Test validation rules independently

## Template System API Reference

### Base Classes
- `FieldTemplate`: Abstract base for all field types
- `SectionTemplate`: Abstract base for form sections
- `FormTemplate`: Abstract base for complete forms

### Field Types
- `TextFieldTemplate`: Single-line text input
- `TextAreaFieldTemplate`: Multi-line text input
- `DateFieldTemplate`: Date picker
- `TimeFieldTemplate`: Time picker
- `DateTimeFieldTemplate`: Combined date/time picker
- `TableFieldTemplate`: Dynamic table with add/remove rows

### Validation Rules
- `RequiredRule`: Field cannot be empty
- `MaxLengthRule`: String length validation
- `ValidationResult`: Return type for validation operations

This guide provides the foundation for adding new ICS forms to RadioForms efficiently and consistently.
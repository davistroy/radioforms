# Form Models and Management

This document describes the form model components implemented in the RadioForms application, their architecture, and usage patterns.

## Overview

The form management system in RadioForms consists of the following major components:

1. **Base Form Model** - Abstract base class for all ICS form models
2. **Specific Form Models** - Concrete implementations for ICS-213, ICS-214, etc.
3. **Form Registry** - System for registering and discovering form types
4. **Form Factory** - Factory for creating form instances
5. **Form Persistence** - System for saving, loading, and tracking form changes

These components work together to provide a flexible, extensible system for managing ICS forms with support for serialization, validation, and change tracking.

## Base Form Model

Located in `radioforms/models/base_form.py`, this abstract base class provides the foundation for all form models:

- Unique form identification
- Common metadata (creation date, version, etc.)
- Serialization to/from JSON and dictionaries
- Observer pattern for change notification
- Version history tracking
- Validation framework

## ICS-213 General Message Form

Located in `radioforms/models/ics213_form.py`, this concrete implementation represents the ICS-213 General Message form:

- Message routing information (to, from, subject)
- Message content
- Reply/approval fields
- Form-specific validation rules
- Factory method for creating new instances

## ICS-214 Activity Log Form

Located in `radioforms/models/ics214_form.py`, this concrete implementation represents the ICS-214 Activity Log form:

- Incident and operational period information
- Team/personnel details
- Activity log entries with timestamps
- Methods for adding, updating, and removing activities
- Form-specific validation rules

## Form Registry and Factory

Located in `radioforms/models/form_registry.py`, these components manage form type registration and instantiation:

### Form Registry

- Singleton pattern for global form type registration
- Storage of form metadata (display name, description, version)
- Registration of form classes and factory functions
- Form discovery from Python packages

### Form Factory

- Creation of form instances by type
- Loading forms from JSON or dictionary data
- Access to form metadata
- Form type discovery

## Form Persistence and Change Tracking

Located in `radioforms/models/form_persistence.py`, these components manage form state and persistence:

### Change Tracker

- Recording of property changes
- Undo/redo functionality
- Change history access

### Form Manager

- Form creation by type
- Saving forms to disk
- Loading forms from disk
- Form state tracking (new, modified, saved, readonly)
- Backup creation
- Import/export functionality

## Usage Examples

### Creating and Registering a Form Type

```python
from radioforms.models.form_registry import FormRegistry, FormMetadata
from radioforms.models.ics213_form import ICS213Form

# Get the registry singleton
registry = FormRegistry()

# Register a form type
metadata = FormMetadata(
    form_type="ICS-213",
    display_name="General Message",
    description="Used for sending general messages",
    version="1.0"
)
registry.register_form_class(ICS213Form, metadata)
```

### Creating and Using a Form

```python
from radioforms.models.form_registry import FormFactory

# Create a factory
factory = FormFactory()

# Create a form instance
form = factory.create_form("ICS-213")

# Set form properties
form.to = "Operations Section"
form.from_field = "Planning Section"
form.subject = "Resource Request"
form.message = "Please provide additional resources for the next operational period."

# Validate the form
result = form.validate()
if result.is_valid:
    # Serialize to JSON
    json_data = form.to_json()
else:
    # Handle validation errors
    for field, error in result.errors.items():
        print(f"Error in {field}: {error}")
```

### Saving and Loading Forms

```python
from radioforms.models.form_persistence import FormManager

# Create a form manager
manager = FormManager(forms_dir="data/forms")

# Create a form
form = manager.create_form("ICS-213")
form.to = "Incident Command"
form.subject = "Situation Update"

# Save the form
save_path = manager.save_form(form)

# Load a form
loaded_form = manager.load_form(save_path)
```

### Using Change Tracking

```python
from radioforms.models.form_persistence import FormManager

# Create a form manager
manager = FormManager()

# Create a form
form = manager.create_form("ICS-213")
form.to = "Operations"
form.subject = "Initial Message"

# Get the change tracker
tracker = manager.get_tracker(form.form_id)

# Make some changes
form.subject = "Updated Subject"
form.message = "This is an updated message."

# Undo the last change
if tracker.can_undo():
    change = tracker.undo()
    print(f"Undid change to {change.property_name}")

# Redo the change
if tracker.can_redo():
    change = tracker.redo()
    print(f"Redid change to {change.property_name}")
```

## Extending the System

To add a new form type:

1. Create a new class that inherits from `BaseFormModel`
2. Implement form-specific properties and methods
3. Override the `get_form_type()` method to return the form type identifier
4. Implement the `validate()` method for form-specific validation
5. Register the form class with the `FormRegistry`

## Testing

Comprehensive test coverage is provided in the following test files:

### Core Model Tests (`radioforms/tests/test_form_models.py`)
- Form creation and property access
- Serialization and deserialization
- Validation rules
- Form registry and factory functionality
- Change tracking with undo/redo
- Form manager persistence operations

### UI Component Tests (`radioforms/tests/test_views/`)
- Basic UI component initialization and properties (`test_form_views.py`)
- Form tab management and controller interaction (`test_form_tab_widget.py`)
- Signal connections between models and views

## Future Enhancements

Planned enhancements to the form management system:

1. Support for additional ICS form types
2. Integration with PDF generation
3. Export to ICS-DES format for radio transmission
4. Form templates for quick creation
5. Digital signature support

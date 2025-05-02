# Form Models Refactoring Documentation

## Overview

This document describes the changes implemented in the form models refactoring of the RadioForms application. The refactoring transitions from a property-based object model to modern Python dataclasses. This change results in cleaner, more maintainable code with better type hinting and serialization capabilities.

## Key Components

### 1. Form State Enum

Located in `radioforms/models/dataclass_forms.py`, this enum defines the possible states of a form:

```python
class FormState(Enum):
    """Represents the possible states of a form"""
    DRAFT = "draft"
    APPROVED = "approved"
    TRANSMITTED = "transmitted"
    RECEIVED = "received"
    REPLIED = "replied"
    RETURNED = "returned"
    ARCHIVED = "archived"
```

### 2. Base Form Dataclass

Located in `radioforms/models/dataclass_forms.py`, this dataclass provides the foundation for all form models:

```python
@dataclass
class BaseForm:
    """Base class for all form models"""
    form_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    form_type: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    state: FormState = field(default=FormState.DRAFT)
    title: str = ""
    incident_id: Optional[str] = None
    creator_id: Optional[str] = None
```

This base class provides:
- Unique form identification
- Common metadata (creation date, version, etc.)
- Serialization to/from dictionaries
- Basic validation framework

### 3. Specific Form Dataclasses

#### ICS-213 General Message Form

Located in `radioforms/models/dataclass_forms.py`, this dataclass represents the ICS-213 General Message form:

```python
@dataclass
class ICS213Form(BaseForm):
    """ICS-213 General Message form model"""
    form_type: str = "ICS-213"
    
    # Message information
    to: str = ""
    to_position: str = ""
    from_field: str = ""
    from_position: str = ""
    subject: str = ""
    message: str = ""
    # ... additional fields and methods ...
```

#### ICS-214 Activity Log Form

Located in `radioforms/models/dataclass_forms.py`, this dataclass represents the ICS-214 Activity Log form:

```python
@dataclass
class ICS214Form(BaseForm):
    """ICS-214 Activity Log form model"""
    form_type: str = "ICS-214"
    
    # Operational information
    operational_period_from: Optional[datetime] = None
    operational_period_to: Optional[datetime] = None
    incident_name: str = ""
    incident_number: str = ""
    # ... additional fields and methods ...
```

### 4. Helper Dataclasses

For complex forms with nested structures, helper dataclasses are provided:

```python
@dataclass
class ActivityLogEntry:
    """Activity log entry for ICS-214 form"""
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    time: datetime = field(default_factory=datetime.now)
    activity: str = ""

@dataclass
class Personnel:
    """Personnel entry for ICS-214 form"""
    person_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    position: str = ""
    home_agency: str = ""
```

## Key Features

### 1. Serialization & Deserialization

Each form class provides methods for converting between dataclass instances and dictionaries/JSON:

```python
def to_dict(self) -> Dict[str, Any]:
    """Convert to dictionary for serialization"""
    data = asdict(self)
    
    # Handle special types
    data["state"] = self.state.value
    data["created_at"] = self.created_at.isoformat()
    data["updated_at"] = self.updated_at.isoformat()
    
    return data
    
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'BaseForm':
    """Create from dictionary"""
    # ... implementation ...
    return cls(**data_copy)
```

### 2. Validation

Each form class implements validation logic to ensure data integrity:

```python
def validate(self) -> Dict[str, str]:
    """Validate form data and return dictionary of errors"""
    errors = {}
    
    if not self.title:
        errors["title"] = "Title is required"
        
    return errors
```

### 3. State Transitions

Forms implement methods for transitioning between states:

```python
def approve(self, approver_name: str, approver_position: str, approver_signature: str) -> bool:
    """
    Approve the form.
    
    Args:
        approver_name: Name of the approver
        approver_position: Position of the approver
        approver_signature: Signature of the approver
        
    Returns:
        True if the state was changed, False if not
    """
    if self.state != FormState.DRAFT:
        return False
        
    # ... implementation ...
    
    self.state = FormState.APPROVED
    self.updated_at = datetime.now()
    return True
```

## Usage Examples

### Creating a Form

```python
from radioforms.models.dataclass_forms import ICS213Form

# Create a new ICS-213 form
form = ICS213Form(
    title="Resource Request",
    incident_id="incident-123",
    to="Operations Section",
    from_field="Planning Section",
    subject="Additional Resources",
    message="Please provide additional resources for Sector 2."
)

# Access form attributes directly
print(f"Form type: {form.form_type}")
print(f"Title: {form.title}")
print(f"State: {form.state}")
```

### Serializing and Deserializing

```python
import json
from radioforms.models.dataclass_forms import ICS213Form

# Create a form
form = ICS213Form(title="Test Form")

# Convert to dictionary
form_dict = form.to_dict()

# Convert to JSON string
json_str = json.dumps(form_dict)

# Recreate from dictionary
new_form = ICS213Form.from_dict(form_dict)
```

### Validating a Form

```python
from radioforms.models.dataclass_forms import ICS213Form

# Create a form
form = ICS213Form()

# Validate the form
errors = form.validate()

if errors:
    print("Form validation failed:")
    for field, error in errors.items():
        print(f"  {field}: {error}")
else:
    print("Form is valid")
```

### State Transitions

```python
from radioforms.models.dataclass_forms import ICS213Form

# Create a form
form = ICS213Form(
    title="Resource Request",
    to="Operations Section",
    from_field="Planning Section",
    subject="Additional Resources",
    message="Please provide additional resources for Sector 2."
)

# Approve the form
approved = form.approve(
    "Jane Smith",
    "Planning Section Chief",
    "Jane Smith"
)

if approved:
    print(f"Form approved. New state: {form.state}")
else:
    print("Form approval failed")

# Transmit the form
transmitted = form.transmit()
if transmitted:
    print(f"Form transmitted. New state: {form.state}")
```

## Benefits of the New Architecture

1. **Simplified Code**: Dataclasses reduce boilerplate code for class definitions and provide automatic methods like `__init__`, `__repr__`, and `__eq__`.
2. **Better Type Hints**: Explicit type annotations improve IDE auto-completion and static type checking.
3. **Immutable Fields**: Fields can be marked as immutable (`frozen=True`) to prevent accidental modifications.
4. **Custom Field Defaults**: Default factory functions allow dynamic default values.
5. **Serialization**: Easy conversion between dataclasses and dictionaries/JSON using `asdict()`.
6. **Post-Initialization Processing**: The `__post_init__` method allows custom logic after initialization.

## Integration with Database Layer

The dataclass-based form models integrate with the SQLAlchemy database layer:

1. Forms are serialized to JSON using the `to_dict()` method and stored in the `data` field of the `Form` table.
2. When loading a form, the JSON data is deserialized using the `from_dict()` method.
3. Form versions use the same serialization mechanism.

## Migration from Previous Architecture

The new dataclass-based form models support the same functionality as the previous property-based models, with these key improvements:

1. Code is more concise and readable
2. Better type checking and IDE support
3. Simpler serialization and deserialization
4. More explicit state transitions
5. Improved validation framework

The application includes compatibility layers to ensure smooth migration between the previous and new form model implementations.

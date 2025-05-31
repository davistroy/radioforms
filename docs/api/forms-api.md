# Forms API Documentation

## Overview

The Forms API provides the core data models and business logic for ICS forms in the RadioForms application. This module implements the ICS-213 General Message form following FEMA standards and provides validation, serialization, and lifecycle management.

## Module: `src.forms.ics213`

### Classes

#### `Priority(Enum)`

Message priority levels for ICS-213 forms.

```python
class Priority(Enum):
    ROUTINE = "routine"      # Standard operational messages
    URGENT = "urgent"        # Time-sensitive operational messages  
    IMMEDIATE = "immediate"  # Emergency or life-safety messages
```

**Usage Example:**
```python
from src.forms.ics213 import Priority

# Set message priority
form.data.priority = Priority.URGENT
```

#### `FormStatus(Enum)`

Form lifecycle status tracking.

```python
class FormStatus(Enum):
    DRAFT = "draft"              # Initial state, editable
    APPROVED = "approved"        # Validated and approved
    TRANSMITTED = "transmitted"  # Sent via communication
    RECEIVED = "received"        # Acknowledgment received
    REPLIED = "replied"          # Reply provided
    DOCUMENTED = "documented"    # Archived and documented
```

**Usage Example:**
```python
from src.forms.ics213 import FormStatus

# Check form status
if form.status == FormStatus.DRAFT:
    # Form can be edited
    pass
```

#### `Person`

Represents person information used throughout ICS-213 forms.

```python
@dataclass
class Person:
    name: str = ""
    position: str = ""
    signature: str = ""
    contact_info: str = ""
```

**Properties:**
- `is_complete -> bool`: Returns True if both name and position are provided
- `display_name -> str`: Returns formatted "Name, Position" or available field

**Methods:**
- `to_dict() -> Dict[str, str]`: Convert to dictionary for serialization
- `from_dict(data: Dict[str, Any]) -> Person`: Create from dictionary (class method)

**Usage Example:**
```python
from src.forms.ics213 import Person

# Create person
sender = Person(
    name="John Smith",
    position="Incident Commander",
    signature="J.S.",
    contact_info="Radio 001"
)

# Check completeness
if sender.is_complete:
    print(f"Valid person: {sender.display_name}")

# Convert to dictionary
person_dict = sender.to_dict()

# Create from dictionary
restored_person = Person.from_dict(person_dict)
```

#### `ICS213Data`

Core data structure containing all ICS-213 form fields.

```python
@dataclass
class ICS213Data:
    # Header fields
    incident_name: str = ""
    to: Person = field(default_factory=Person)
    from_person: Person = field(default_factory=Person)
    subject: str = ""
    date: str = ""  # YYYY-MM-DD format
    time: str = ""  # HH:MM format
    
    # Message fields
    message: str = ""
    approved_by: Person = field(default_factory=Person)
    
    # Reply fields
    reply: str = ""
    replied_by: Person = field(default_factory=Person)
    reply_date_time: str = ""
    
    # Metadata
    priority: Priority = Priority.ROUTINE
    form_version: str = "1.0"
    reply_requested: bool = False
```

**Usage Example:**
```python
from src.forms.ics213 import ICS213Data, Person, Priority

# Create form data
data = ICS213Data(
    incident_name="Wildfire Alpha",
    to=Person(name="Jane Commander", position="IC"),
    from_person=Person(name="John Operator", position="Ops"),
    subject="Status Update",
    date="2025-05-30",
    time="14:30",
    message="All teams deployed and operational.",
    priority=Priority.URGENT,
    reply_requested=True
)
```

#### `ICS213Form`

Complete ICS-213 form with validation and business logic.

```python
class ICS213Form:
    def __init__(self, data: Optional[ICS213Data] = None) -> None
```

**Attributes:**
- `data: ICS213Data` - Form's data content
- `status: FormStatus` - Current lifecycle status  
- `validation_errors: List[str]` - Current validation errors
- `created_at: datetime` - Creation timestamp
- `updated_at: datetime` - Last modification timestamp

**Methods:**

##### `validate() -> bool`

Validate form according to ICS-213 requirements.

**Returns:** True if valid, False otherwise
**Side Effects:** Updates `validation_errors` list

**Validation Rules:**
- Recipient (To) must have both name and position
- Sender (From) must have both name and position
- Subject is required
- Date and Time are required  
- Message content is required
- If approver specified, must have name and position
- If reply exists, replier must have name and position

**Usage Example:**
```python
form = ICS213Form(data)

if form.validate():
    print("Form is valid")
else:
    for error in form.get_validation_errors():
        print(f"Error: {error}")
```

##### `get_validation_errors() -> List[str]`

Get list of current validation errors.

**Returns:** Copy of validation errors list

##### `is_ready_for_approval() -> bool`

Check if form is ready for approval workflow.

**Returns:** True if form validates and status is DRAFT

##### `is_ready_for_transmission() -> bool`

Check if form is ready for transmission.

**Returns:** True if form validates, status allows transmission, and has approver

##### `approve(approver: Person) -> bool`

Approve the form with approver information.

**Args:**
- `approver: Person` - Person approving the form

**Returns:** True if approval successful, False otherwise

**Usage Example:**
```python
approver = Person(name="Chief Officer", position="Safety Officer")
if form.approve(approver):
    print(f"Form approved by {approver.display_name}")
    print(f"Status: {form.status}")  # FormStatus.APPROVED
```

##### `add_reply(reply_text: str, replier: Person) -> bool`

Add reply to the form.

**Args:**
- `reply_text: str` - Reply message content
- `replier: Person` - Person providing the reply

**Returns:** True if reply added successfully

**Usage Example:**
```python
replier = Person(name="Response Leader", position="Operations Chief")
if form.add_reply("Message received and understood.", replier):
    print("Reply added successfully")
```

##### `to_json() -> str`

Serialize form to JSON string.

**Returns:** JSON representation of complete form

**JSON Structure:**
```json
{
    "data": {
        "incident_name": "...",
        "to": {"name": "...", "position": "..."},
        "from_person": {"name": "...", "position": "..."},
        "subject": "...",
        "date": "...",
        "time": "...",
        "message": "...",
        "priority": "urgent",
        "reply_requested": true
    },
    "status": "draft",
    "created_at": "2025-05-30T14:30:00.123456",
    "updated_at": "2025-05-30T14:30:00.123456",
    "validation_errors": []
}
```

##### `from_json(json_str: str) -> ICS213Form` (class method)

Create form from JSON string.

**Args:**
- `json_str: str` - JSON representation of form

**Returns:** New ICS213Form instance

**Raises:** `ValidationError` if JSON is invalid

**Usage Example:**
```python
# Serialize form
json_data = form.to_json()

# Restore form
restored_form = ICS213Form.from_json(json_data)
```

##### `get_summary() -> str`

Get brief summary of form for display.

**Returns:** Formatted summary string

**Example Output:** `"From: John Operator, Ops | To: Jane Commander, IC | Subject: Status Update"`

### Exceptions

#### `ValidationError(Exception)`

Raised when form validation fails or invalid data is encountered.

**Usage Example:**
```python
try:
    form = ICS213Form.from_json(invalid_json)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

## Usage Patterns

### Creating a New Form

```python
from src.forms.ics213 import ICS213Form, ICS213Data, Person, Priority

# Method 1: Create with data
data = ICS213Data(
    incident_name="Emergency Response",
    to=Person(name="Command Staff", position="IC"),
    from_person=Person(name="Field Team", position="Ops"),
    subject="Situation Report",
    date="2025-05-30",
    time="15:45",
    message="All personnel accounted for. No injuries reported.",
    priority=Priority.URGENT
)
form = ICS213Form(data)

# Method 2: Create empty and populate
form = ICS213Form()
form.data.incident_name = "Emergency Response"
form.data.to = Person(name="Command Staff", position="IC")
# ... populate other fields
```

### Form Validation and Approval Workflow

```python
# Validate form
if not form.validate():
    print("Form has errors:")
    for error in form.get_validation_errors():
        print(f"  - {error}")
    return

# Check if ready for approval
if form.is_ready_for_approval():
    approver = Person(name="Safety Officer", position="SO")
    if form.approve(approver):
        print("Form approved successfully")
    else:
        print("Approval failed")

# Check if ready for transmission
if form.is_ready_for_transmission():
    print("Form ready for transmission")
```

### Serialization and Persistence

```python
# Save form to JSON
json_data = form.to_json()
with open("message.json", "w") as f:
    f.write(json_data)

# Load form from JSON
with open("message.json", "r") as f:
    json_data = f.read()
restored_form = ICS213Form.from_json(json_data)
```

### Reply Handling

```python
# Add reply to received message
replier = Person(name="Incident Commander", position="IC")
reply_text = "Message received. Please proceed with evacuation plan."

if form.add_reply(reply_text, replier):
    print(f"Reply added by {replier.display_name}")
    print(f"Form status: {form.status}")  # FormStatus.REPLIED
```

## Performance Considerations

### Memory Usage
- Each `ICS213Form` instance: ~2-5KB typical
- JSON serialization: ~3-8KB per form typical
- Validation: < 1ms per form typical

### Recommended Practices
- Validate forms before saving to database
- Use batch operations for multiple forms
- Cache validation results when possible
- Reuse `Person` objects for common contacts

## Thread Safety

The forms module classes are **not thread-safe**. If accessing forms from multiple threads:

1. Use appropriate locking mechanisms
2. Create separate form instances per thread
3. Use the database layer for concurrent access
4. Avoid sharing form instances between threads

## Error Handling

### Common Error Scenarios

```python
# Handle validation errors
try:
    if not form.validate():
        # Handle validation failures
        errors = form.get_validation_errors()
        # Display errors to user
        
except Exception as e:
    # Handle unexpected validation errors
    logger.error(f"Validation error: {e}")

# Handle JSON serialization errors
try:
    json_data = form.to_json()
except Exception as e:
    logger.error(f"Serialization failed: {e}")

# Handle JSON parsing errors
try:
    form = ICS213Form.from_json(json_data)
except ValidationError as e:
    # Handle invalid JSON format
    print(f"Invalid form data: {e}")
except Exception as e:
    # Handle other JSON errors
    logger.error(f"JSON parsing failed: {e}")
```

## See Also

- [Database API Documentation](database-api.md)
- [File Service API Documentation](file-service-api.md)
- [ICS-213 Form Specification](../forms/ICS-213-Analysis.md)
- [CLAUDE.md Development Guidelines](../CLAUDE.md)
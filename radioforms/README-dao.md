# RadioForms - Data Access Layer Documentation

This document provides comprehensive documentation for the data access layer of the RadioForms application.

## Overview

The data access layer consists of model entities and Data Access Objects (DAOs) that provide an abstraction between the application logic and the SQLite database. This design follows the DAO pattern and ensures separation of concerns between data access and business logic.

## Database Manager

The `DatabaseManager` class (`database/db_manager.py`) provides core database functionality, including:

- Connection management with thread safety
- Transaction support with context managers
- WAL (Write-Ahead Logging) mode for reliability
- Optimized SQLite settings for performance

## Model Entities

Entity models represent database tables and provide data container functionality:

### Base Models

- `BaseModel`: Base class with ID and common functionality
- `TimestampedModel`: Extends `BaseModel` with creation and update timestamps

### Entity-Specific Models

1. **User** (`database/models/user.py`)
   - Represents a user with name, call sign, and last login time
   - Methods for updating last login timestamp

2. **Incident** (`database/models/incident.py`)
   - Represents an emergency incident with name, description, and date range
   - Methods for checking active status, closing, and reopening incidents

3. **Form** (`database/models/form.py`)
   - Represents an ICS form with metadata (type, title, status)
   - Includes an enum `FormStatus` for tracking form state (DRAFT, FINALIZED, SUBMITTED, ARCHIVED)
   - Methods for changing form status

4. **FormVersion** (`database/models/form_version.py`)
   - Represents a version of a form's content
   - Handles JSON serialization/deserialization of form content
   - Supports the form's version history

5. **Attachment** (`database/models/attachment.py`)
   - Represents a file attachment linked to a form
   - Stores file metadata (path, name, type, size)
   - Methods for working with file paths and checking file types

6. **Setting** (`database/models/setting.py`)
   - Represents an application setting with key-value storage
   - Supports various data types with automatic conversion
   - JSON serialization for complex data types

## Data Access Objects (DAOs)

DAOs provide database operations for each entity type:

### Base DAO

`BaseDAO` (`database/dao/base_dao.py`) provides common functionality:

- Generic CRUD operations (create, read, update, delete)
- Filtering and pagination
- Transaction support

### Entity-Specific DAOs

1. **UserDAO** (`database/dao/user_dao.py`)
   - User management operations
   - Methods for finding users by name or call sign
   - Login tracking

2. **IncidentDAO** (`database/dao/incident_dao.py`)
   - Incident management operations
   - Methods for finding active/closed incidents
   - Date range filtering
   - Statistics generation

3. **FormDAO** (`database/dao/form_dao.py`)
   - Form management with version support
   - Content creation and updates
   - Form searching and filtering
   - Status management
   - Proper deletion with cascade support

4. **AttachmentDAO** (`database/dao/attachment_dao.py`)
   - File attachment management
   - File system operations
   - File type detection
   - Export functionality

5. **SettingDAO** (`database/dao/setting_dao.py`)
   - Application settings management
   - Key-value storage
   - Bulk operations
   - Prefix filtering

## Usage Examples

### Creating a User

```python
from radioforms.database.db_manager import DatabaseManager
from radioforms.database.dao import UserDAO
from radioforms.database.models.user import User

# Create a database manager
db_manager = DatabaseManager("radioforms.db")

# Create a user DAO
user_dao = UserDAO(db_manager)

# Create a user
user = User(name="John Doe", call_sign="KD0ABC")
user_id = user_dao.create(user)

# Find a user by call sign
user = user_dao.find_by_call_sign("KD0ABC")
```

### Creating a Form with Content

```python
from radioforms.database.dao import FormDAO
from radioforms.database.models.form import Form, FormStatus

# Create a form DAO
form_dao = FormDAO(db_manager)

# Create a form
form = Form(
    incident_id=1,
    form_type="ICS-213",
    title="Test Message",
    creator_id=user_id,
    status=FormStatus.DRAFT
)

# Create with content
form_content = {
    "to": "Command",
    "from": "Operations",
    "subject": "Test Message",
    "message": "This is a test message."
}
form_id = form_dao.create_with_content(form, form_content, user_id)

# Retrieve with content
form, content = form_dao.get_with_content(form_id)
```

### Working with Transactions

```python
# Using transaction context manager
with db_manager.transaction() as tx:
    # Create a user
    tx.execute(
        "INSERT INTO users (name, call_sign) VALUES (?, ?)",
        ("Transaction User", "TX1")
    )
    
    # Create an incident
    tx.execute(
        "INSERT INTO incidents (name) VALUES (?)",
        ("Test Incident",)
    )
    
    # If any operation fails, all changes are rolled back
```

## Testing

The data access layer includes comprehensive tests:

- `test_database.py`: Tests database schema and functionality
- `test_database_dao.py`: Tests DAO operations for all entities
- `test_integration.py`: Tests the interaction between components

Run the tests with:

```bash
python -m unittest radioforms.tests.test_database
python -m unittest radioforms.tests.test_database_dao
python -m unittest radioforms.tests.test_integration
```

## Best Practices

- Always use DAO methods instead of direct database access
- Use transactions for operations that modify multiple tables
- Close database connections when done
- Handle exceptions appropriately
- Use the correct DAO for each entity type

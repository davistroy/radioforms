# Database Layer Refactoring Documentation

## Overview

This document describes the changes implemented in the database layer refactoring of the RadioForms application. The refactoring moves from a custom DAO pattern to a modern SQLAlchemy ORM with Repository pattern implementation. This change simplifies the codebase, improves maintainability, and follows industry standards for database access in Python applications.

## Key Components

### 1. SQLAlchemy ORM Models

Located in `radioforms/database/orm_models.py`, these models define the database schema using SQLAlchemy's declarative syntax:

- `Base` - SQLAlchemy declarative base class
- `Incident` - Represents incident information
- `OperationalPeriod` - Represents operational periods within incidents
- `User` - Represents system users
- `Form` - Represents ICS forms
- `FormVersion` - Represents version history for forms
- `Attachment` - Represents files attached to forms
- `Setting` - Represents application settings

These models include relationship definitions that automatically handle the foreign key relationships between tables.

### 2. Repository Pattern Implementation

Located in `radioforms/database/repositories.py`, these repositories provide a clean interface for database operations:

- `BaseRepository` - Common functionality for all repositories
- `IncidentRepository` - Operations for incident records
- `UserRepository` - Operations for user records
- `FormRepository` - Operations for form records
- `OperationalPeriodRepository` - Operations for operational period records
- `AttachmentRepository` - Operations for attachments
- `SettingRepository` - Operations for application settings

Each repository follows a consistent interface with methods like `get_by_id()`, `get_all()`, `create()`, `update()`, and `delete()`.

### 3. Database Manager

Located in `radioforms/database/db_manager_sqlalchemy.py`, this component manages database connections and sessions:

- Database initialization
- Session management
- Connection pooling
- Error handling

### 4. Migration System

Using Alembic for database migrations:

- `alembic.ini` - Configuration file for Alembic
- `migrations/env.py` - Environment setup for migrations
- `migrations/versions/` - Migration script files

## Usage Examples

### Initializing the Database

```python
from radioforms.database.db_manager_sqlalchemy import DatabaseManager

# Create a database manager
db_manager = DatabaseManager('sqlite:///radioforms.db')

# Initialize the database (creates tables if they don't exist)
db_manager.init_db()

# Get a session for database operations
session = db_manager.get_session()
```

### Working with Repositories

```python
from radioforms.database.repositories import UserRepository, IncidentRepository, FormRepository

# Create repositories with the session
user_repo = UserRepository(session)
incident_repo = IncidentRepository(session)
form_repo = FormRepository(session)

# Create a user
user = user_repo.create({
    'name': 'John Doe',
    'callsign': 'JD1',
    'position': 'Incident Commander'
})

# Create an incident
incident = incident_repo.create({
    'name': 'Test Incident',
    'incident_number': 'INC-2023-001',
    'type': 'Exercise',
    'location': 'Test Location',
    'start_date': '2023-05-01'
})

# Create a form
form = form_repo.create({
    'incident_id': incident.incident_id,
    'form_type': 'ICS-213',
    'state': 'draft',
    'title': 'Test Message',
    'data': '{"message": "Test message content"}',
    'created_by': user.user_id
})

# Retrieve a form with its content
retrieved_form, form_content = form_repo.find_with_content(form.form_id)
```

### Running Migrations

```bash
# Generate a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Downgrade to a specific version
alembic downgrade <revision>
```

## Benefits of the New Architecture

1. **Simplified Code**: The repository pattern provides a clean, consistent interface for database operations.
2. **Better Maintainability**: Industry-standard ORM patterns are easier to understand and maintain.
3. **Improved Testing**: Repositories can be easily mocked for unit testing.
4. **Schema Evolution**: Alembic provides robust migration support for evolving the database schema.
5. **Type Safety**: SQLAlchemy models provide better type checking and IDE support.
6. **Performance**: SQLAlchemy includes query optimization and connection pooling.

## Integration with Form Models

The database layer integrates with the dataclass-based form models:

1. Form models are serialized to JSON and stored in the `data` field of the `Form` table.
2. When loading a form, the JSON data is deserialized into the appropriate form dataclass.
3. Form versions are stored in the `FormVersion` table, with the version content as JSON.

## Migration from Previous Architecture

The database tables are largely compatible with the previous architecture, with some key differences:

1. Primary key field names now follow SQLAlchemy conventions.
2. Foreign key relationships are explicitly defined.
3. The data schema supports the same functionality with a cleaner structure.

During application startup, any necessary migrations from the old schema to the new schema are automatically applied using Alembic.

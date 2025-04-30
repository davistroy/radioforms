# DAO Pattern Guide for RadioForms

## Overview

The Data Access Object (DAO) pattern is a structural pattern that isolates the application/business layer from the persistence layer. In RadioForms, we've implemented a consistent DAO architecture to provide:

- Clear separation between business logic and database operations
- Consistent interface for data access across the application
- Support for both object-oriented and dictionary-based data access
- Type safety through Python type hints

This document explains the DAO architecture used in RadioForms and provides guidance for using and extending it.

## Architecture Components

### BaseDAO

The foundation of our DAO architecture is the `BaseDAO` class, which is a generic class that provides common CRUD operations:

```python
class BaseDAO(Generic[T]):
    """Base Data Access Object providing common database operations."""
    
    # Core operations
    def find_by_id(self, entity_id: int, as_dict: bool = False) -> Optional[Union[T, Dict[str, Any]]]: ...
    def find_all(self, limit: int = 1000, offset: int = 0, as_dict: bool = False) -> Union[List[T], List[Dict[str, Any]]]: ...
    def find_by_filter(self, filters: Dict[str, Any], ...) -> Union[List[T], List[Dict[str, Any]]]: ...
    def create(self, entity: Union[T, Dict[str, Any]]) -> int: ...
    def update(self, entity_or_id: Union[T, Dict[str, Any], int], entity_data: Optional[Dict[str, Any]] = None) -> bool: ...
    def delete(self, entity_id: int) -> bool: ...
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int: ...
```

### Entity-Specific DAOs

Each entity type has its own DAO class that extends `BaseDAO` with entity-specific operations:

- **IncidentDAO**: Operations for incident management
- **FormDAO**: Operations for forms and form versions
- **UserDAO**: Operations for users
- **AttachmentDAO**: Operations for file attachments
- **SettingDAO**: Operations for application settings

## Key Design Patterns

### 1. Object-Dictionary Dual Interface

All DAO methods support both object-oriented and dictionary-based access through the `as_dict` parameter:

```python
# Object-oriented style
incident = incident_dao.find_by_id(5)
print(incident.name)

# Dictionary style
incident_dict = incident_dao.find_by_id(5, as_dict=True)
print(incident_dict["name"])
```

This provides flexibility for different use cases:
- Use objects when working with business logic
- Use dictionaries when passing data to UI or API responses

### 2. Method Overloading with Python Overloads

The DAO methods use `@overload` decorators to provide proper type hinting for different parameter combinations:

```python
@overload
def find_by_id(self, entity_id: int) -> Optional[T]: ...

@overload
def find_by_id(self, entity_id: int, as_dict: bool = False) -> Optional[Dict[str, Any]]: ...
```

This ensures proper type checking and IDE auto-completion regardless of which style you use.

### 3. Consistent Naming Conventions

DAO methods follow consistent naming conventions:
- `find_*`: Methods that retrieve data from the database
- `create_*`: Methods that insert new data
- `update_*`: Methods that modify existing data
- `delete_*`: Methods that remove data

## Usage Guidelines

### Basic CRUD Operations

```python
# Create a new entity
incident = Incident(name="Wildfire Response", description="Forest fire response")
incident_id = incident_dao.create(incident)

# Or with a dictionary
incident_data = {"name": "Flood Response", "description": "River flooding"}
incident_id = incident_dao.create(incident_data)

# Find an entity by ID
incident = incident_dao.find_by_id(incident_id)
incident_dict = incident_dao.find_by_id(incident_id, as_dict=True)

# Update an entity
incident.name = "Updated Wildfire Response"
incident_dao.update(incident)

# Or with dictionaries
incident_dao.update(incident_id, {"name": "Updated Flood Response"})

# Delete an entity
incident_dao.delete(incident_id)
```

### Specialized Methods

Each DAO provides entity-specific methods for common operations:

```python
# IncidentDAO specific methods
active_incidents = incident_dao.find_active_incidents()
incident_dao.close_incident(incident_id)
incident_dao.reopen_incident(incident_id)

# FormDAO specific methods
forms = form_dao.find_by_incident(incident_id)
form_with_content = form_dao.find_with_content(form_id)
```

### Transaction Support

Use transaction context managers for operations that require atomicity:

```python
with db_manager.transaction() as tx:
    # Multiple operations that should succeed or fail together
    user_id = user_dao.create(user)
    incident_id = incident_dao.create(incident)
    form_id = form_dao.create_with_content(form, content, user_id)
```

## Performance Considerations

1. Use `as_dict=True` when you don't need entity objects for better performance
2. Use specialized query methods instead of retrieving all records and filtering in Python
3. Consider pagination with `limit` and `offset` parameters for large datasets
4. Use transactions for multiple operations to reduce connection overhead

## Extending the DAO Layer

When adding new entity types or methods:

1. Create a new entity model in `database/models/`
2. Create a new DAO class extending `BaseDAO[YourEntity]`
3. Implement `_row_to_entity` and `_entity_to_values` methods
4. Add specialized methods as needed
5. Follow the dual interface pattern with `as_dict` parameters
6. Add comprehensive docstrings with examples

## Examples

### Entity-Oriented Usage

```python
# Working with incident entities
incidents = incident_dao.find_active_incidents()
for incident in incidents:
    if incident.is_active():
        # Access properties directly
        print(f"Active incident: {incident.name} (started: {incident.start_date})")
        
        # Update the incident
        if some_condition:
            incident_dao.close_incident(incident.id)
```

### Dictionary-Oriented Usage

```python
# Working with incident dictionaries
incidents = incident_dao.find_active_incidents(as_dict=True)
for incident in incidents:
    # Access dictionary keys
    print(f"Active incident: {incident['name']} (started: {incident['start_date']})")
    
    # Update through a dictionary
    if some_condition:
        incident_dao.update(incident['id'], {'description': 'Updated description'})
```

## Best Practices

1. Use transactions for multi-step operations
2. Choose the appropriate interface style (object vs dictionary) based on the use case
3. Use entity objects for business logic, dictionaries for data transfer
4. Leverage specialized query methods instead of retrieving all entities and filtering
5. Write comprehensive tests for DAO classes and methods

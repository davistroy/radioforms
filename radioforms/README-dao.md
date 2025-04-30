# RadioForms Data Access Object (DAO) Layer

This document provides information about the Data Access Object (DAO) pattern implementation in the RadioForms application. The DAO layer serves as an abstraction between the application business logic and the database, providing a consistent interface for CRUD operations.

## BaseDAO

The `BaseDAO` abstract class provides the foundation for all DAO implementations. It defines a standardized interface and implements common functionality for database operations.

### BaseDAO Key Methods

- `find_all(as_dict=False)`: Retrieve all entities of a particular type
- `find_by_id(entity_id, as_dict=False)`: Find an entity by its ID
- `find_by_field(field, value, as_dict=False)`: Find entities by a specific field value
- `find_by_fields(field_dict, as_dict=False)`: Find entities matching multiple field conditions
- `create(entity)`: Create a new entity in the database
- `update(entity_or_id, update_data=None)`: Update an existing entity (supports two calling patterns)
- `delete(entity_id)`: Delete an entity by its ID
- `count(where_clause=None, params=None)`: Count entities with optional filtering
- `exists(entity_id)`: Check if an entity exists by ID

### Using BaseDAO

All concrete DAOs inherit from `BaseDAO` and implement the required abstract methods:

```python
class UserDAO(DAOCacheMixin[User], BaseDAO[User]):
    def __init__(self, db_manager: DatabaseManager):
        BaseDAO.__init__(self, db_manager)
        DAOCacheMixin.__init__(self)
        self.table_name = "users"
        self.pk_column = "id"
        
    def _row_to_entity(self, row: Dict[str, Any]) -> User:
        # Implementation for converting a database row to a User entity
        
    def _entity_to_values(self, entity: User) -> Dict[str, Any]:
        # Implementation for converting a User entity to a dictionary of values
```

## Caching Support

All DAOs include caching support through the `DAOCacheMixin` class. This provides automatic caching of query results and cache invalidation when data is modified.

### Cache Configuration

Cache behavior can be configured per DAO instance:

```python
# Disable caching for a specific DAO
user_dao.configure_cache(enabled=False)

# Set a specific TTL for cache entries
user_dao.configure_cache(ttl=300)  # 5 minutes
```

### How Caching Works

1. **Automatic Query Caching**: Results from methods like `find_by_id` and `find_all` are automatically cached
2. **Cache Invalidation**: The cache is automatically invalidated when data is modified through `create`, `update`, or `delete`
3. **Cache Key Generation**: Cache keys are generated based on the method name and arguments to ensure unique caching
4. **Cache Backends**: Different cache backends can be configured through the `CacheManager`
   - `MemoryCache`: In-memory cache (default)
   - `DiskCache`: Disk-based cache for persistence between restarts
   - `NullCache`: No-op cache implementation (disables caching)

## DAO Implementations

The following DAOs are available in the system:

### IncidentDAO

Provides operations for incidents, including:
- Managing incident status (active/closed)
- Finding incidents by name, status, etc.
- Getting incident statistics

### UserDAO

Provides operations for users, including:
- Finding users by name or call sign
- Tracking user login activity
- Creating users if they don't exist

### FormDAO

Provides operations for forms, including:
- Form content versioning
- Managing form status
- Searching forms by title, incident, type, etc.

### AttachmentDAO

Provides operations for file attachments, including:
- Creating attachments from files
- Managing attachment metadata
- Moving attachments between forms

### SettingDAO

Provides operations for application settings, including:
- Getting and setting key-value pairs
- Getting settings by prefix
- Bulk setting operations

## Input/Output Flexibility

All retrieval methods (`find_*`) support both entity objects and dictionaries as return values through the `as_dict` parameter. This allows for flexibility in how data is consumed by the application.

Similarly, creation and update methods accept both entity objects and dictionaries as input, making it easy to work with data regardless of how it's structured.

## Example Usage

### Basic CRUD Operations

```python
# Create a new user
user = User(name="John Doe", call_sign="JD1")
user_id = user_dao.create(user)

# Find a user by ID
user = user_dao.find_by_id(user_id)

# Update a user
user.name = "Jane Doe"
user_dao.update(user)

# Delete a user
user_dao.delete(user_id)
```

### Using the Dictionary Interface

```python
# Create a new user using a dictionary
user_id = user_dao.create({
    "name": "John Doe",
    "call_sign": "JD1"
})

# Find a user by ID as a dictionary
user_dict = user_dao.find_by_id(user_id, as_dict=True)

# Update a user using dictionary with ID
user_dao.update({
    "id": user_id,
    "name": "Jane Doe"
})

# Alternative update method with ID and update data
user_dao.update(user_id, {
    "name": "Jane Doe"
})
```

### Transaction Support

The DAO layer supports database transactions through the `DatabaseManager`:

```python
# Using a transaction to ensure atomicity
with db_manager.transaction() as tx:
    # Create a user
    user_id = user_dao.create(User(name="John Doe"))
    
    # Create an incident associated with the user
    incident = Incident(name="Test Incident")
    incident_id = incident_dao.create(incident)
    
    # Create a form associated with both
    form = Form(incident_id=incident_id, creator_id=user_id)
    form_id = form_dao.create(form)
    
    # If any operation fails, the entire transaction is rolled back

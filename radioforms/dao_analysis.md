# BaseDAO Structure Analysis

This document analyzes the current DAO implementations and identifies inconsistencies that should be addressed as part of the refactoring effort.

## Current Structure

The application uses a Data Access Object (DAO) pattern with a base class `BaseDAO` and several implementation classes:
- BaseDAO: Abstract base class for all DAOs
- IncidentDAO: Operations related to incidents
- UserDAO: Operations related to users
- FormDAO: Operations for forms and form versions
- AttachmentDAO: Operations for file attachments
- SettingDAO: Operations for application settings

## Identified Inconsistencies

### 1. Method Naming Inconsistencies

| DAO Class | Method Examples | Issues |
|-----------|----------------|--------|
| BaseDAO | `find_by_id()`, `find_all()` | Base class establishes "find_" pattern |
| IncidentDAO | `get_by_id()`, `get_all()` | Uses "get_" instead of "find_" |
| UserDAO | `find_by_name()`, `find_by_call_sign()` | Follows base class pattern |
| FormDAO | `find_by_incident()`, `get_with_content()` | Mixes "find_" and "get_" prefixes |
| SettingDAO | `get_by_key()`, `get_value()` | Primarily uses "get_" prefix |

This inconsistency in method naming makes the API less intuitive and harder to use correctly.

### 2. Parameter Handling Inconsistencies

| DAO Class | Method | Parameter Approach | Issues |
|-----------|--------|-------------------|--------|
| BaseDAO | `update(entity)` | Takes entity object | Base class establishes entity pattern |
| IncidentDAO | `update(incident_id, incident_data)` | Takes ID and dictionary | Different from base class |
| UserDAO | `update(entity)` | Takes entity object | Follows base class pattern |
| FormDAO | `update_with_content(form, content, user_id)` | Takes entity, content dict, and optional ID | Complex mixed approach |

These inconsistencies make it difficult to understand how to correctly call DAO methods without looking at each implementation.

### 3. Return Type Inconsistencies

| DAO Class | Method | Return Type | Issues |
|-----------|--------|------------|--------|
| BaseDAO | `find_by_id()` | `Optional[T]` (entity object) | Base class establishes entity return |
| IncidentDAO | `get_by_id()` | `Optional[Dict[str, Any]]` (dictionary) | Returns dict instead of entity |
| UserDAO | `find_by_id()` | `Optional[User]` (entity object) | Follows base class pattern |
| FormDAO | `get_with_content()` | `Optional[Tuple[Form, Dict[str, Any]]]` | Complex return type |

The mixed return types (entities vs. dictionaries) require clients to handle different types based on which DAO they're using.

### 4. Model/Dictionary Conversion Inconsistencies

| DAO Class | Conversion Approach | Issues |
|-----------|---------------------|--------|
| BaseDAO | Requires `_row_to_entity()` and `_entity_to_values()` | Defines conversion interface |
| IncidentDAO | Does not implement these methods | Works with dictionaries instead of models |
| UserDAO | Implements conversion methods | Follows base class pattern |
| FormDAO | Implements conversion methods | Follows base class pattern |

Some DAOs properly implement the model/dictionary conversion methods while others don't follow this pattern consistently.

### 5. Error Handling Inconsistencies

Some methods handle errors with try/except blocks and raise DAOException, while others allow exceptions to propagate. There's no consistent approach to error handling across the DAO classes.

## Recommendations for Standardization

1. Standardize method naming conventions:
   - Use "find_" prefix for retrieval operations
   - Use "create", "update", "delete" for CRUD operations
   - Use consistent prefixes for specialized operations

2. Standardize parameter handling:
   - All DAOs should accept both entity objects and dictionaries
   - Methods should have consistent signatures across DAOs

3. Standardize return types:
   - Methods should return entity objects by default
   - Provide options to return dictionaries when needed
   - Consistent handling of empty results

4. Implement consistent model/dictionary conversion:
   - All DAOs must implement conversion methods
   - Create utility methods for common conversion tasks

5. Standardize error handling:
   - Consistent approach to error conditions
   - Proper use of DAOException

These standardizations will make the DAO layer more consistent, intuitive, and maintainable, while also making it easier for developers to work with the database layer.

# DAO Usage Examples for RadioForms

This document provides practical examples for using the RadioForms DAO layer. It demonstrates common patterns, best practices, and both entity-oriented and dictionary-oriented approaches.

## Table of Contents

1. [Basic CRUD Operations](#basic-crud-operations)
2. [Working with Incidents](#working-with-incidents)
3. [Form Management](#form-management)
4. [User Operations](#user-operations)
5. [Settings Management](#settings-management)
6. [Transaction Handling](#transaction-handling)
7. [Performance Optimization](#performance-optimization)

## Basic CRUD Operations

### Entity-Oriented Approach

```python
from radioforms.database.db_manager import DatabaseManager
from radioforms.database.dao.incident_dao import IncidentDAO
from radioforms.database.models.incident import Incident

# Initialize database manager and DAO
db_manager = DatabaseManager("path/to/database.db")
incident_dao = IncidentDAO(db_manager)

# Create a new entity
incident = Incident(
    name="Wildfire Response", 
    description="Forest fire in north sector"
)
incident_id = incident_dao.create(incident)
print(f"Created new incident with ID: {incident_id}")

# Retrieve the entity
retrieved_incident = incident_dao.find_by_id(incident_id)
if retrieved_incident:
    print(f"Retrieved incident: {retrieved_incident.name}")
    
    # Update the entity
    retrieved_incident.description = "Forest fire in north sector - Level 2 response"
    incident_dao.update(retrieved_incident)
    print("Updated incident description")
    
    # Delete the entity
    incident_dao.delete(retrieved_incident.id)
    print("Deleted the incident")
```

### Dictionary-Oriented Approach

```python
# Initialize database manager and DAO (as above)

# Create a new entity using a dictionary
incident_data = {
    "name": "Flood Response",
    "description": "River flooding in eastern region",
    "start_date": datetime.now()
}
incident_id = incident_dao.create(incident_data)
print(f"Created new incident with ID: {incident_id}")

# Retrieve as dictionary
incident_dict = incident_dao.find_by_id(incident_id, as_dict=True)
if incident_dict:
    print(f"Retrieved incident: {incident_dict['name']}")
    
    # Update using ID and dictionary
    incident_dao.update(incident_id, {
        "description": "River flooding in eastern region - Evacuation ordered"
    })
    print("Updated incident description")
    
    # Delete using ID
    incident_dao.delete(incident_id)
    print("Deleted the incident")
```

## Working with Incidents

### Finding Active Incidents

```python
# Get all active incidents as entity objects
active_incidents = incident_dao.find_active_incidents()
print(f"Found {len(active_incidents)} active incidents")

for incident in active_incidents:
    print(f"Incident: {incident.name} (Started: {incident.start_date})")
    
    # Example of using entity methods
    duration = incident.get_duration()
    print(f"Duration: {duration.days} days")
```

### Managing Incident Lifecycle

```python
# Create a new incident
incident = Incident(name="Training Exercise", description="Annual drill")
incident_id = incident_dao.create(incident)

# Later, close the incident
incident_dao.close_incident(incident_id)
print("Incident closed")

# If needed, reopen the incident
incident_dao.reopen_incident(incident_id)
print("Incident reopened")
```

### Finding Incidents by Name

```python
# Search for incidents containing "fire" in their name
fire_incidents = incident_dao.find_by_name("fire")
print(f"Found {len(fire_incidents)} incidents related to fires")

# Dictionary-based search with sorting by name
response_incidents = incident_dao.find_by_name("response", as_dict=True)
for incident in sorted(response_incidents, key=lambda i: i['name']):
    print(f"Response incident: {incident['name']}")
```

## Form Management

```python
from radioforms.database.dao.form_dao import FormDAO
from radioforms.database.models.form import Form, FormStatus

# Initialize DAO
form_dao = FormDAO(db_manager)

# Create a form with content
form = Form(
    incident_id=incident_id,
    form_type="ICS-213",
    title="Resource Request",
    creator_id=user_id,
    status=FormStatus.DRAFT
)

# Form content as a dictionary
content = {
    "to": "Logistics",
    "from": "Operations",
    "subject": "Additional Equipment",
    "message": "Request 3 additional pumps for sector 2"
}

# Create the form with its content
form_id = form_dao.create_with_content(form, content, user_id)
print(f"Created form with ID: {form_id}")

# Later, retrieve the form with its content
form_tuple = form_dao.find_with_content(form_id)
if form_tuple:
    form, content = form_tuple
    print(f"Form: {form.title}")
    print(f"Message: {content['message']}")
    
    # Update content
    content["message"] += "\nUpdate: Need 4 pumps instead of 3"
    form_dao.update_with_content(form, content, user_id)
    print("Updated form content")
```

### Finding Forms for an Incident

```python
# Get all forms for an incident
forms = form_dao.find_by_incident(incident_id)
print(f"Incident has {len(forms)} forms")

# Get only final forms (dictionary mode)
final_forms = form_dao.find_by_incident(
    incident_id, 
    status=FormStatus.FINALIZED,
    as_dict=True
)
print(f"Incident has {len(final_forms)} finalized forms")
```

## User Operations

```python
from radioforms.database.dao.user_dao import UserDAO
from radioforms.database.models.user import User

# Initialize DAO
user_dao = UserDAO(db_manager)

# Create a new user
user = User(name="John Smith", call_sign="JS123")
user_id = user_dao.create(user)
print(f"Created user with ID: {user_id}")

# Find by call sign
found_user = user_dao.find_by_call_sign("JS123")
if found_user:
    print(f"Found user: {found_user.name}")
    
    # Update last login time
    user_dao.update_last_login(found_user.id)
    print("Updated user's last login time")
```

## Settings Management

```python
from radioforms.database.dao.setting_dao import SettingDAO

# Initialize DAO
setting_dao = SettingDAO(db_manager)

# Store a setting
setting_dao.set_value("ui.theme", "dark")
print("Theme preference saved")

# Retrieve a setting
theme = setting_dao.get_value("ui.theme", "light")  # Default to light if not found
print(f"Current theme: {theme}")

# Store structured data
user_preferences = {
    "notifications.enabled": True,
    "notifications.sound": True,
    "notifications.vibration": False
}
setting_dao.bulk_set_values(user_preferences)
print("User preferences saved")

# Get settings by prefix
notification_settings = setting_dao.get_settings_as_dict("notifications")
print(f"Notification settings: {notification_settings}")
```

## Transaction Handling

Use transactions when performing multiple related operations that should succeed or fail together:

```python
# Example: Creating a new incident with an initial form
try:
    with db_manager.transaction() as tx:
        # Create incident
        incident_data = {"name": "New Incident", "description": "Test incident"}
        cursor = tx.execute(
            "INSERT INTO incidents (name, description, start_date, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (incident_data["name"], incident_data["description"], datetime.now(), datetime.now(), datetime.now())
        )
        incident_id = cursor.lastrowid
        
        # Create a form for this incident
        cursor = tx.execute(
            """
            INSERT INTO forms (
                incident_id, form_type, title, creator_id, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (incident_id, "ICS-213", "Initial Briefing", user_id, "draft", datetime.now(), datetime.now())
        )
        form_id = cursor.lastrowid
        
        # Add form content
        content = json.dumps({"message": "Initial incident briefing"})
        tx.execute(
            "INSERT INTO form_versions (form_id, version_number, content, created_by, created_at) VALUES (?, ?, ?, ?, ?)",
            (form_id, 1, content, user_id, datetime.now())
        )
        
        print(f"Created incident {incident_id} with initial form {form_id}")
        
except Exception as e:
    print(f"Transaction failed: {e}")
    # The transaction is automatically rolled back
```

## Performance Optimization

### Using Dictionary Mode for Bulk Operations

When processing many records, dictionary mode can be more efficient:

```python
# Get all active incidents as dictionaries (faster than entities)
incidents = incident_dao.find_active_incidents(as_dict=True)

# Process many records efficiently
stats = {
    "with_forms": 0,
    "no_forms": 0
}

for incident in incidents:
    # Check if incident has any forms (without loading them all)
    has_forms = form_dao.count({"incident_id": incident["id"]}) > 0
    if has_forms:
        stats["with_forms"] += 1
    else:
        stats["no_forms"] += 1

print(f"Incidents with forms: {stats['with_forms']}")
print(f"Incidents without forms: {stats['no_forms']}")
```

### Using Pagination for Large Datasets

```python
# Constants for pagination
PAGE_SIZE = 50
current_page = 1

while True:
    # Calculate offset
    offset = (current_page - 1) * PAGE_SIZE
    
    # Get a page of incidents
    incidents = incident_dao.find_all(limit=PAGE_SIZE, offset=offset)
    
    # Break if no more results
    if not incidents:
        break
        
    print(f"Processing page {current_page} ({len(incidents)} incidents)")
    
    # Process the incidents...
    for incident in incidents:
        # Do something with each incident
        pass
        
    # Move to next page
    current_page += 1
```

### Using Specialized Methods Instead of Filtering in Memory

```python
# Inefficient approach (loads all incidents then filters in Python)
all_incidents = incident_dao.find_all()
active_fire_incidents = [
    i for i in all_incidents 
    if i.is_active() and "fire" in i.name.lower()
]

# Efficient approach (filters in the database)
# First, get active incidents
active_incidents = incident_dao.find_active_incidents()
# Then filter for those with "fire" in the name
fire_incidents = [i for i in active_incidents if "fire" in i.name.lower()]

# Even better: create a specialized method in IncidentDAO
# def find_active_by_name(self, name_fragment: str) -> List[Incident]:
#     query = "SELECT * FROM incidents WHERE end_date IS NULL AND name LIKE ?"
#     cursor = self.db_manager.execute(query, (f"%{name_fragment}%",))
#     return [self._row_to_entity(dict(row)) for row in cursor.fetchall()]

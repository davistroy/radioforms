import os
import datetime
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from radioforms.database.orm_models import Base, Incident, Form, User
from radioforms.database.repositories import IncidentRepository, FormRepository, UserRepository
from radioforms.database.db_manager_sqlalchemy import DatabaseManager

def test_sqlalchemy_crud():
    """Test basic CRUD operations with the new SQLAlchemy ORM"""
    # Initialize the database manager
    db_manager = DatabaseManager('sqlite:///test_orm.db')
    db_manager.init_db()
    
    # Get a session
    session = db_manager.get_session()
    
    # Create repositories
    incident_repo = IncidentRepository(session)
    form_repo = FormRepository(session)
    user_repo = UserRepository(session)
    
    print("=== Testing User Repository ===")
    # Create a user
    user_data = {
        'user_id': str(uuid.uuid4()),
        'name': 'Test User',
        'callsign': 'TEST1',
        'position': 'Tester',
        'email': 'test@example.com'
    }
    user = user_repo.create(user_data)
    print(f"Created user: {user.name} (ID: {user.user_id})")
    
    # Get user by ID
    retrieved_user = user_repo.get_by_id(user.user_id)
    print(f"Retrieved user: {retrieved_user.name}")
    
    # Update user
    user_repo.update(user.user_id, {'position': 'Senior Tester'})
    updated_user = user_repo.get_by_id(user.user_id)
    print(f"Updated user position: {updated_user.position}")
    
    print("\n=== Testing Incident Repository ===")
    # Create an incident
    incident_data = {
        'incident_id': str(uuid.uuid4()),
        'name': 'Test Incident',
        'incident_number': 'INC-2025-001',
        'type': 'Test',
        'location': 'Test Location',
        'start_date': '2025-05-01',
        'status': 'active'
    }
    incident = incident_repo.create(incident_data)
    print(f"Created incident: {incident.name} (ID: {incident.incident_id})")
    
    print("\n=== Testing Form Repository ===")
    # Create a form
    form_data = {
        'form_id': str(uuid.uuid4()),
        'incident_id': incident.incident_id,
        'form_type': 'ICS-213',
        'state': 'draft',
        'title': 'Test Form',
        'data': '{"message": "Test message", "to": "Test Recipient", "from": "Test Sender"}',
        'created_by': user.user_id
    }
    form = form_repo.create(form_data)
    print(f"Created form: {form.title} (ID: {form.form_id})")
    
    # Get form with content
    form_with_content = form_repo.find_with_content(form.form_id)
    if form_with_content:
        form_obj, content = form_with_content
        print(f"Retrieved form content: {content}")
    
    # Create form version
    version = form_repo.create_version(
        form.form_id, 
        '{"message": "Updated test message", "to": "Test Recipient", "from": "Test Sender"}',
        user.user_id
    )
    print(f"Created form version: {version.version}")
    
    # Clean up
    form_repo.delete(form.form_id)
    incident_repo.delete(incident.incident_id)
    user_repo.delete(user.user_id)
    
    print("\nTests completed successfully!")
    
    # Close the session
    db_manager.close()
    
    # On Windows, we need to explicitly close the connection and release file locks
    # This is best done in a separate process, so we won't try to remove the file
    print("Note: test_orm.db remains in the directory for inspection")

if __name__ == "__main__":
    test_sqlalchemy_crud()

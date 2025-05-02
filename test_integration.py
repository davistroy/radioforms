import os
import json
import datetime
from radioforms.database.db_manager_sqlalchemy import DatabaseManager
from radioforms.database.repositories import FormRepository, UserRepository, IncidentRepository
from radioforms.models.dataclass_forms import ICS213Form, ICS214Form, ActivityLogEntry, Personnel

def test_form_integration():
    """Test integration between form dataclasses and SQLAlchemy repositories"""
    print("=== Testing Form Integration ===")
    
    # Initialize database
    db_path = "test_integration.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    db_manager = DatabaseManager(f'sqlite:///{db_path}')
    db_manager.init_db()
    session = db_manager.get_session()
    
    # Create repositories
    user_repo = UserRepository(session)
    incident_repo = IncidentRepository(session)
    form_repo = FormRepository(session)
    
    # Create a test user
    user = user_repo.create({
        'name': 'John Doe',
        'callsign': 'JD1',
        'position': 'Incident Commander'
    })
    
    # Create an incident
    incident = incident_repo.create({
        'name': 'Test Incident',
        'incident_number': 'INC-2025-001',
        'type': 'Exercise',
        'location': 'Test Location',
        'start_date': '2025-05-01'
    })
    
    print(f"Created user: {user.name} with ID: {user.user_id}")
    print(f"Created incident: {incident.name} with ID: {incident.incident_id}")
    
    # Create an ICS-213 form using the dataclass
    ics213 = ICS213Form(
        title="Test Message",
        incident_id=incident.incident_id,
        creator_id=user.user_id,
        to="Operations Section",
        to_position="Section Chief",
        from_field="Planning Section",
        from_position="Section Chief",
        subject="Resource Request",
        message="Please provide additional personnel for Sector 2.",
        incident_name=incident.name,
        priority="Priority"
    )
    
    # Save to database
    form_dict = ics213.to_dict()
    
    # ICS213Form.from_dict.__func__ is not JSON serializable, so we need to remove it
    # We'll create a clean dictionary with just the needed fields
    clean_dict = {k: v for k, v in form_dict.items() if not callable(v)}
    
    form = form_repo.create({
        'form_id': ics213.form_id,
        'incident_id': ics213.incident_id,
        'form_type': ics213.form_type,
        'state': form_dict['state'],  # Get the string value
        'title': ics213.title,
        'data': json.dumps(clean_dict),
        'created_by': ics213.creator_id
    })
    
    print(f"Created ICS-213 form: {form.title} with ID: {form.form_id}")
    
    # Now retrieve it
    retrieved_form, content = form_repo.find_with_content(form.form_id)
    print(f"Retrieved form: {retrieved_form.title}")
    print(f"Form content sample: {json.dumps(content, indent=2)[:200]}...")
    
    # Create an ICS-214 form
    activities = [
        ActivityLogEntry(
            time=datetime.datetime.now() - datetime.timedelta(hours=2),
            activity="Started operational period"
        ),
        ActivityLogEntry(
            time=datetime.datetime.now() - datetime.timedelta(hours=1),
            activity="Deployed resources to Sector 2"
        )
    ]
    
    personnel = [
        Personnel(
            name="John Doe",
            position="Section Chief",
            home_agency="Fire Department"
        ),
        Personnel(
            name="Jane Smith",
            position="Team Leader",
            home_agency="EMS"
        )
    ]
    
    ics214 = ICS214Form(
        incident_id=incident.incident_id,
        creator_id=user.user_id,
        incident_name=incident.name,
        incident_number=incident.incident_number,
        operational_period_from=datetime.datetime.now() - datetime.timedelta(hours=12),
        operational_period_to=datetime.datetime.now(),
        unit_name="Planning Section",
        unit_leader_name="John Doe",
        unit_leader_position="Section Chief",
        activities=activities,
        personnel=personnel,
        prepared_by_name="John Doe",
        prepared_by_position="Section Chief"
    )
    
    # Save to database
    form_dict = ics214.to_dict()
    
    # Same fix for ICS214Form - create a clean dictionary
    clean_dict = {k: v for k, v in form_dict.items() if not callable(v)}
    
    form = form_repo.create({
        'form_id': ics214.form_id,
        'incident_id': ics214.incident_id,
        'form_type': ics214.form_type,
        'state': form_dict['state'],
        'title': ics214.title,
        'data': json.dumps(clean_dict),
        'created_by': ics214.creator_id
    })
    
    print(f"Created ICS-214 form: {form.title} with ID: {form.form_id}")
    
    # Now retrieve it
    retrieved_form, content = form_repo.find_with_content(form.form_id)
    print(f"Retrieved form: {retrieved_form.title}")
    print(f"Form has {len(content.get('activities', []))} activities and {len(content.get('personnel', []))} personnel entries")
    
    # Test version creation
    ics213.message = "Please provide additional personnel for Sector 2 and Sector 3."
    form_dict = ics213.to_dict()
    clean_dict = {k: v for k, v in form_dict.items() if not callable(v)}
    version = form_repo.create_version(ics213.form_id, clean_dict, user.user_id)
    print(f"Created form version: {version.version}")
    
    # Clean up
    db_manager.close()
    print("Database connection closed")
    
    # We'll leave the database file for inspection
    print(f"Test database created at: {db_path}")

if __name__ == "__main__":
    test_form_integration()

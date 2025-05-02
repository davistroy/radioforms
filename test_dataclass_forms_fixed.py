import datetime
import json
from radioforms.models.dataclass_forms import FormState, BaseForm, ICS214Form, ActivityLogEntry, Personnel
# Import directly from our modified class
from modified_ics213_form import ModifiedICS213Form

def test_base_form():
    """Test the BaseForm dataclass"""
    # Create a base form
    form = BaseForm(
        form_id="test-form-123",
        form_type="TEST",
        title="Test Form",
        incident_id="test-incident-456",
        creator_id="test-user-789"
    )
    
    print("=== Testing BaseForm ===")
    print(f"Form ID: {form.form_id}")
    print(f"Form Type: {form.form_type}")
    print(f"Title: {form.title}")
    print(f"State: {form.state}")
    
    # Test validation
    errors = form.validate()
    print(f"Validation errors: {errors}")
    
    # Test to_dict() method
    form_dict = form.to_dict()
    print(f"Form as dict: {json.dumps(form_dict, indent=2)}")
    
    # Test from_dict() method
    new_form = BaseForm.from_dict(form_dict)
    print(f"Recreated form from dict - Title: {new_form.title}, Type: {new_form.form_type}")

def test_ics213_form():
    """Test the modified ICS213Form dataclass"""
    # Create an ICS-213 form
    form = ModifiedICS213Form(
        form_id="ics213-test-123",
        title="Test Message",
        incident_id="test-incident-456",
        creator_id="test-user-789",
        to="John Doe",
        to_position="Incident Commander",
        from_field="Jane Smith",
        from_position="Operations Chief",
        subject="Test Subject",
        message="This is a test message for testing the ICS-213 form dataclass.",
        incident_name="Test Incident"
    )
    
    print("\n=== Testing Modified ICS213Form ===")
    print(f"Form ID: {form.form_id}")
    print(f"Form Type: {form.form_type}")
    print(f"Title: {form.title}")
    print(f"To: {form.to}")
    print(f"From: {form.from_field}")
    print(f"Subject: {form.subject}")
    print(f"Message: {form.message}")
    
    # Test validation
    errors = form.validate()
    print(f"Validation errors: {errors}")
    
    # Test state transition
    approved = form.approve("Jane Smith", "Operations Chief", "Jane Smith")
    print(f"Approve result: {approved}")
    print(f"New state: {form.state}")
    
    transmitted = form.transmit()
    print(f"Transmit result: {transmitted}")
    print(f"New state: {form.state}")
    
    received = form.receive("John Doe", "Incident Commander")
    print(f"Receive result: {received}")
    print(f"New state: {form.state}")
    
    # The reply method takes two arguments: reply_text and recipient_signature
    reply_text = "This is a test reply message."
    recipient_signature = "John Doe (signature)"
    replied = form.add_reply(reply_text, recipient_signature)
    print(f"Reply result: {replied}")
    print(f"New state: {form.state}")
    print(f"Reply content: {form.reply_text}")
    
    # Test to_dict() method
    form_dict = form.to_dict()
    print(f"ICS-213 form as dict: {json.dumps(form_dict, indent=2)}")
    
    # Test from_dict() method
    new_form = ModifiedICS213Form.from_dict(form_dict)
    print(f"Recreated ICS-213 form - Subject: {new_form.subject}, State: {new_form.state}")

def test_ics214_form():
    """Test the ICS214Form dataclass"""
    # Create activity log entries
    activities = [
        ActivityLogEntry(
            time=datetime.datetime.now() - datetime.timedelta(hours=2),
            activity="Started shift and received briefing"
        ),
        ActivityLogEntry(
            time=datetime.datetime.now() - datetime.timedelta(hours=1),
            activity="Deployed resources to sector 2"
        ),
        ActivityLogEntry(
            time=datetime.datetime.now(),
            activity="Completed assignment and prepared for handoff"
        )
    ]
    
    # Create personnel entries
    personnel = [
        Personnel(
            name="John Doe",
            position="Team Leader",
            home_agency="Fire Dept."
        ),
        Personnel(
            name="Jane Smith",
            position="Team Member",
            home_agency="Police Dept."
        )
    ]
    
    # Create an ICS-214 form
    form = ICS214Form(
        form_id="ics214-test-123",
        incident_name="Test Incident",
        incident_number="INC-2025-001",
        operational_period_from=datetime.datetime.now() - datetime.timedelta(hours=12),
        operational_period_to=datetime.datetime.now(),
        unit_name="Operations Team Alpha",
        unit_leader_name="John Doe",
        unit_leader_position="Team Leader",
        activities=activities,
        personnel=personnel,
        prepared_by_name="John Doe",
        prepared_by_position="Team Leader"
    )
    
    print("\n=== Testing ICS214Form ===")
    print(f"Form ID: {form.form_id}")
    print(f"Form Type: {form.form_type}")
    print(f"Title: {form.title}")
    print(f"Incident: {form.incident_name} ({form.incident_number})")
    print(f"Unit: {form.unit_name}")
    print(f"Personnel count: {len(form.personnel)}")
    print(f"Activity entries: {len(form.activities)}")
    
    # Test activity logs
    print("\nActivity Log:")
    for i, activity in enumerate(form.activities):
        print(f"  {i+1}. [{activity.time.isoformat()}] {activity.activity}")
    
    # Test validation
    errors = form.validate()
    print(f"Validation errors: {errors}")
    
    # Test adding activity
    new_activity = form.add_activity(
        datetime.datetime.now() + datetime.timedelta(minutes=30),
        "Added a new activity entry"
    )
    print(f"Added new activity: {new_activity.activity}")
    print(f"Activity entries now: {len(form.activities)}")
    
    # Test removing activity
    removed = form.remove_activity(activities[1].entry_id)
    print(f"Remove activity result: {removed}")
    print(f"Activity entries now: {len(form.activities)}")
    
    # Test finalizing form
    finalized = form.finalize("John Doe", "Team Leader", "John Doe")
    print(f"Finalize result: {finalized}")
    print(f"New state: {form.state}")
    
    # Test to_dict() method
    form_dict = form.to_dict()
    print(f"ICS-214 form as dict: {json.dumps(form_dict, indent=2)}")
    
    # Test from_dict() method
    new_form = ICS214Form.from_dict(form_dict)
    print(f"Recreated ICS-214 form - Unit: {new_form.unit_name}, Activities: {len(new_form.activities)}")

if __name__ == "__main__":
    test_base_form()
    test_ics213_form()
    test_ics214_form()

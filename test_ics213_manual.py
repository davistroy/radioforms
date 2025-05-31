#!/usr/bin/env python3
"""Manual test for ICS-213 data model functionality."""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.forms.ics213 import ICS213Form, ICS213Data, Person, Priority, FormStatus


def test_person():
    """Test Person class."""
    print("Testing Person class...")
    
    # Test empty person
    person = Person()
    assert not person.is_complete
    assert person.display_name == "Unknown"
    print("✅ Empty person test passed")
    
    # Test complete person
    person = Person(name="John Smith", position="Operations Chief")
    assert person.is_complete
    assert person.display_name == "John Smith, Operations Chief"
    print("✅ Complete person test passed")
    
    # Test person serialization
    data = person.to_dict()
    person2 = Person.from_dict(data)
    assert person2.name == person.name
    assert person2.position == person.position
    print("✅ Person serialization test passed")


def test_ics213_data():
    """Test ICS213Data class."""
    print("\nTesting ICS213Data class...")
    
    # Test empty data
    data = ICS213Data()
    assert data.subject == ""
    assert data.priority == Priority.ROUTINE
    assert isinstance(data.to, Person)
    print("✅ Empty ICS213Data test passed")
    
    # Test data with persons
    to_person = Person(name="Jane Doe", position="Incident Commander")
    from_person = Person(name="John Smith", position="Operations Chief")
    
    data = ICS213Data(
        incident_name="Test Incident",
        to=to_person,
        from_person=from_person,
        subject="Test Message",
        date="2025-05-30",
        time="14:30",
        message="This is a test message",
        priority=Priority.URGENT
    )
    
    assert data.to.name == "Jane Doe"
    assert data.from_person.name == "John Smith"
    assert data.priority == Priority.URGENT
    print("✅ ICS213Data with persons test passed")
    
    # Test serialization
    dict_data = data.to_dict()
    data2 = ICS213Data.from_dict(dict_data)
    assert data2.subject == data.subject
    assert data2.to.name == data.to.name
    assert data2.priority == data.priority
    print("✅ ICS213Data serialization test passed")


def test_ics213_form():
    """Test ICS213Form class."""
    print("\nTesting ICS213Form class...")
    
    # Test empty form validation
    form = ICS213Form()
    is_valid = form.validate()
    assert not is_valid
    errors = form.get_validation_errors()
    assert len(errors) > 0
    print(f"✅ Empty form validation test passed ({len(errors)} errors found)")
    
    # Test complete form
    data = ICS213Data(
        to=Person(name="Jane Doe", position="Incident Commander"),
        from_person=Person(name="John Smith", position="Operations Chief"),
        subject="Test Message",
        date="2025-05-30",
        time="14:30",
        message="This is a test message for validation"
    )
    
    form = ICS213Form(data)
    is_valid = form.validate()
    assert is_valid
    assert len(form.get_validation_errors()) == 0
    print("✅ Complete form validation test passed")
    
    # Test form approval
    approver = Person(name="Approver Name", position="Incident Commander")
    success = form.approve(approver)
    assert success
    assert form.status == FormStatus.APPROVED
    assert form.data.approved_by.name == "Approver Name"
    print("✅ Form approval test passed")
    
    # Test form reply
    replier = Person(name="Replier Name", position="Operations Chief")
    success = form.add_reply("This is a reply to the message", replier)
    assert success
    assert form.status == FormStatus.REPLIED
    assert form.data.reply == "This is a reply to the message"
    assert form.data.replied_by.name == "Replier Name"
    print("✅ Form reply test passed")
    
    # Test JSON serialization
    json_str = form.to_json()
    form2 = ICS213Form.from_json(json_str)
    assert form2.data.subject == form.data.subject
    assert form2.data.to.name == form.data.to.name
    assert form2.status == form.status
    print("✅ Form JSON serialization test passed")
    
    # Test form summary
    summary = form.get_summary()
    assert "Jane Doe, Incident Commander" in summary
    assert "John Smith, Operations Chief" in summary
    assert "Test Message" in summary
    print("✅ Form summary test passed")


def test_form_lifecycle():
    """Test complete form lifecycle."""
    print("\nTesting complete form lifecycle...")
    
    # 1. Create draft form
    data = ICS213Data(
        incident_name="Wildfire Response 2025",
        to=Person(name="Incident Commander", position="IC"),
        from_person=Person(name="Operations Chief", position="Ops"),
        subject="Resource Request - Additional Engine Companies",
        date="2025-05-30",
        time="14:30",
        message="Request 2 additional engine companies for structure protection in Division A. Current resources are fully committed and additional structures are at risk.",
        priority=Priority.URGENT,
        reply_requested=True
    )
    
    form = ICS213Form(data)
    assert form.status == FormStatus.DRAFT
    assert form.is_ready_for_approval()
    print("✅ Draft form created")
    
    # 2. Approve form
    approver = Person(name="Safety Officer", position="SO", signature="S.O.")
    success = form.approve(approver)
    assert success
    assert form.status == FormStatus.APPROVED
    assert form.is_ready_for_transmission()
    print("✅ Form approved")
    
    # 3. Add reply
    replier = Person(name="Logistics Chief", position="LSC", signature="L.C.")
    reply_text = "2 Engine companies (E-15 and E-22) have been dispatched to Division A. ETA 15 minutes."
    success = form.add_reply(reply_text, replier)
    assert success
    assert form.status == FormStatus.REPLIED
    print("✅ Reply added")
    
    # 4. Final validation
    is_valid = form.validate()
    assert is_valid
    print("✅ Final validation passed")
    
    print(f"\nForm lifecycle complete: {form.get_summary()}")
    print(f"Status: {form.status.value}")


def main():
    """Run all manual tests."""
    print("ICS-213 Data Model Manual Tests")
    print("=" * 40)
    
    try:
        test_person()
        test_ics213_data()
        test_ics213_form()
        test_form_lifecycle()
        
        print("\n🎉 All ICS-213 data model tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
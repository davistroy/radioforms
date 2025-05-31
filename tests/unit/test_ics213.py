"""Unit tests for ICS-213 form data model."""

import pytest
import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.forms.ics213 import (
    ICS213Form, ICS213Data, Person, Priority, FormStatus, ValidationError
)


class TestPerson:
    """Test Person data class."""
    
    def test_person_init_empty(self):
        """Test Person initialization with no data."""
        person = Person()
        assert person.name == ""
        assert person.position == ""
        assert person.signature == ""
        assert person.contact_info == ""
        assert not person.is_complete
    
    def test_person_init_with_data(self):
        """Test Person initialization with data."""
        person = Person(
            name="John Smith",
            position="Operations Chief",
            signature="J. Smith",
            contact_info="Radio: CH1"
        )
        assert person.name == "John Smith"
        assert person.position == "Operations Chief"
        assert person.signature == "J. Smith"
        assert person.contact_info == "Radio: CH1"
        assert person.is_complete
    
    def test_person_strip_whitespace(self):
        """Test that Person strips whitespace."""
        person = Person(
            name="  John Smith  ",
            position="  Operations Chief  "
        )
        assert person.name == "John Smith"
        assert person.position == "Operations Chief"
    
    def test_person_is_complete(self):
        """Test Person.is_complete property."""
        # Empty person
        person = Person()
        assert not person.is_complete
        
        # Name only
        person = Person(name="John")
        assert not person.is_complete
        
        # Position only
        person = Person(position="Chief")
        assert not person.is_complete
        
        # Both name and position
        person = Person(name="John", position="Chief")
        assert person.is_complete
    
    def test_person_display_name(self):
        """Test Person.display_name property."""
        # Both name and position
        person = Person(name="John Smith", position="Operations Chief")
        assert person.display_name == "John Smith, Operations Chief"
        
        # Name only
        person = Person(name="John Smith")
        assert person.display_name == "John Smith"
        
        # Position only
        person = Person(position="Operations Chief")
        assert person.display_name == "Operations Chief"
        
        # Neither
        person = Person()
        assert person.display_name == "Unknown"
    
    def test_person_to_dict(self):
        """Test Person.to_dict method."""
        person = Person(name="John", position="Chief")
        data = person.to_dict()
        
        expected = {
            'name': 'John',
            'position': 'Chief',
            'signature': '',
            'contact_info': ''
        }
        assert data == expected
    
    def test_person_from_dict(self):
        """Test Person.from_dict method."""
        data = {
            'name': 'John Smith',
            'position': 'Operations Chief',
            'signature': 'J. Smith',
            'contact_info': 'Radio: CH1'
        }
        
        person = Person.from_dict(data)
        assert person.name == "John Smith"
        assert person.position == "Operations Chief"
        assert person.signature == "J. Smith"
        assert person.contact_info == "Radio: CH1"
    
    def test_person_from_dict_missing_fields(self):
        """Test Person.from_dict with missing fields."""
        data = {'name': 'John'}
        person = Person.from_dict(data)
        
        assert person.name == "John"
        assert person.position == ""
        assert person.signature == ""
        assert person.contact_info == ""


class TestICS213Data:
    """Test ICS213Data class."""
    
    def test_ics213_data_init_empty(self):
        """Test ICS213Data initialization with no data."""
        data = ICS213Data()
        
        assert data.incident_name == ""
        assert isinstance(data.to, Person)
        assert isinstance(data.from_person, Person)
        assert data.subject == ""
        assert data.date == ""
        assert data.time == ""
        assert data.message == ""
        assert isinstance(data.approved_by, Person)
        assert data.reply == ""
        assert isinstance(data.replied_by, Person)
        assert data.priority == Priority.ROUTINE
        assert data.form_version == "1.0"
        assert data.reply_requested is False
    
    def test_ics213_data_init_with_data(self):
        """Test ICS213Data initialization with data."""
        to_person = Person(name="Jane Doe", position="IC")
        from_person = Person(name="John Smith", position="Ops Chief")
        
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
        
        assert data.incident_name == "Test Incident"
        assert data.to == to_person
        assert data.from_person == from_person
        assert data.subject == "Test Message"
        assert data.date == "2025-05-30"
        assert data.time == "14:30"
        assert data.message == "This is a test message"
        assert data.priority == Priority.URGENT
    
    def test_ics213_data_strip_whitespace(self):
        """Test that ICS213Data strips whitespace."""
        data = ICS213Data(
            incident_name="  Test Incident  ",
            subject="  Test Subject  ",
            message="  Test Message  "
        )
        
        assert data.incident_name == "Test Incident"
        assert data.subject == "Test Subject"
        assert data.message == "Test Message"
    
    def test_ics213_data_to_dict(self):
        """Test ICS213Data.to_dict method."""
        data = ICS213Data(
            subject="Test",
            priority=Priority.URGENT
        )
        
        result = data.to_dict()
        assert isinstance(result, dict)
        assert result['subject'] == "Test"
        assert result['priority'] == "urgent"
        assert 'to' in result
        assert 'from_person' in result
    
    def test_ics213_data_from_dict(self):
        """Test ICS213Data.from_dict method."""
        dict_data = {
            'subject': 'Test Subject',
            'message': 'Test Message',
            'priority': 'urgent',
            'to': {'name': 'Jane', 'position': 'IC'},
            'from_person': {'name': 'John', 'position': 'Ops'}
        }
        
        data = ICS213Data.from_dict(dict_data)
        
        assert data.subject == "Test Subject"
        assert data.message == "Test Message"
        assert data.priority == Priority.URGENT
        assert data.to.name == "Jane"
        assert data.to.position == "IC"
        assert data.from_person.name == "John"
        assert data.from_person.position == "Ops"
    
    def test_ics213_data_from_dict_invalid_priority(self):
        """Test ICS213Data.from_dict with invalid priority."""
        dict_data = {
            'priority': 'invalid_priority'
        }
        
        data = ICS213Data.from_dict(dict_data)
        assert data.priority == Priority.ROUTINE  # Should default


class TestICS213Form:
    """Test ICS213Form class."""
    
    def test_form_init_empty(self):
        """Test ICS213Form initialization with no data."""
        form = ICS213Form()
        
        assert isinstance(form.data, ICS213Data)
        assert form.status == FormStatus.DRAFT
        assert form.validation_errors == []
        assert isinstance(form.created_at, datetime)
        assert isinstance(form.updated_at, datetime)
    
    def test_form_init_with_data(self):
        """Test ICS213Form initialization with data."""
        data = ICS213Data(subject="Test")
        form = ICS213Form(data)
        
        assert form.data == data
        assert form.data.subject == "Test"
    
    def test_form_validate_empty(self):
        """Test validation of empty form."""
        form = ICS213Form()
        
        is_valid = form.validate()
        assert not is_valid
        
        errors = form.get_validation_errors()
        assert len(errors) > 0
        assert any("Recipient" in error for error in errors)
        assert any("Sender" in error for error in errors)
        assert any("Subject" in error for error in errors)
        assert any("Date" in error for error in errors)
        assert any("Time" in error for error in errors)
        assert any("Message" in error for error in errors)
    
    def test_form_validate_complete(self):
        """Test validation of complete form."""
        data = ICS213Data(
            to=Person(name="Jane Doe", position="IC"),
            from_person=Person(name="John Smith", position="Ops Chief"),
            subject="Test Message",
            date="2025-05-30",
            time="14:30",
            message="This is a test message"
        )
        
        form = ICS213Form(data)
        is_valid = form.validate()
        
        assert is_valid
        assert form.get_validation_errors() == []
    
    def test_form_validate_partial_approved_by(self):
        """Test validation with partial approved_by data."""
        data = ICS213Data(
            to=Person(name="Jane Doe", position="IC"),
            from_person=Person(name="John Smith", position="Ops Chief"),
            subject="Test Message",
            date="2025-05-30",
            time="14:30",
            message="This is a test message",
            approved_by=Person(name="Approver")  # Missing position
        )
        
        form = ICS213Form(data)
        is_valid = form.validate()
        
        assert not is_valid
        errors = form.get_validation_errors()
        assert any("Approved by" in error for error in errors)
    
    def test_form_validate_reply_without_replier(self):
        """Test validation with reply but no replier info."""
        data = ICS213Data(
            to=Person(name="Jane Doe", position="IC"),
            from_person=Person(name="John Smith", position="Ops Chief"),
            subject="Test Message",
            date="2025-05-30",
            time="14:30",
            message="This is a test message",
            reply="This is a reply"  # Missing replied_by info
        )
        
        form = ICS213Form(data)
        is_valid = form.validate()
        
        assert not is_valid
        errors = form.get_validation_errors()
        assert any("Replied by" in error for error in errors)
    
    def test_form_approve(self):
        """Test form approval."""
        data = ICS213Data(
            to=Person(name="Jane Doe", position="IC"),
            from_person=Person(name="John Smith", position="Ops Chief"),
            subject="Test Message",
            date="2025-05-30",
            time="14:30",
            message="This is a test message"
        )
        
        form = ICS213Form(data)
        approver = Person(name="Approver", position="IC")
        
        success = form.approve(approver)
        
        assert success
        assert form.status == FormStatus.APPROVED
        assert form.data.approved_by == approver
    
    def test_form_approve_invalid_form(self):
        """Test approval of invalid form."""
        form = ICS213Form()  # Empty form
        approver = Person(name="Approver", position="IC")
        
        success = form.approve(approver)
        
        assert not success
        assert form.status == FormStatus.DRAFT
    
    def test_form_approve_invalid_approver(self):
        """Test approval with invalid approver."""
        data = ICS213Data(
            to=Person(name="Jane Doe", position="IC"),
            from_person=Person(name="John Smith", position="Ops Chief"),
            subject="Test Message",
            date="2025-05-30",
            time="14:30",
            message="This is a test message"
        )
        
        form = ICS213Form(data)
        approver = Person(name="Approver")  # Missing position
        
        success = form.approve(approver)
        
        assert not success
        assert form.status == FormStatus.DRAFT
        errors = form.get_validation_errors()
        assert any("Approver" in error for error in errors)
    
    def test_form_add_reply(self):
        """Test adding reply to form."""
        data = ICS213Data(
            to=Person(name="Jane Doe", position="IC"),
            from_person=Person(name="John Smith", position="Ops Chief"),
            subject="Test Message",
            date="2025-05-30",
            time="14:30",
            message="This is a test message"
        )
        
        form = ICS213Form(data)
        replier = Person(name="Replier", position="IC")
        
        success = form.add_reply("This is a reply", replier)
        
        assert success
        assert form.status == FormStatus.REPLIED
        assert form.data.reply == "This is a reply"
        assert form.data.replied_by == replier
        assert form.data.reply_date_time != ""
    
    def test_form_add_reply_empty_text(self):
        """Test adding empty reply."""
        form = ICS213Form()
        replier = Person(name="Replier", position="IC")
        
        success = form.add_reply("", replier)
        
        assert not success
        errors = form.get_validation_errors()
        assert any("Reply text" in error for error in errors)
    
    def test_form_add_reply_invalid_replier(self):
        """Test adding reply with invalid replier."""
        form = ICS213Form()
        replier = Person(name="Replier")  # Missing position
        
        success = form.add_reply("This is a reply", replier)
        
        assert not success
        errors = form.get_validation_errors()
        assert any("Replier" in error for error in errors)
    
    def test_form_to_json(self):
        """Test form JSON serialization."""
        data = ICS213Data(subject="Test")
        form = ICS213Form(data)
        
        json_str = form.to_json()
        
        assert isinstance(json_str, str)
        
        # Parse to verify it's valid JSON
        parsed = json.loads(json_str)
        assert 'data' in parsed
        assert 'status' in parsed
        assert 'created_at' in parsed
        assert 'updated_at' in parsed
        assert parsed['data']['subject'] == "Test"
    
    def test_form_from_json(self):
        """Test form JSON deserialization."""
        data = ICS213Data(
            subject="Test Message",
            to=Person(name="Jane", position="IC")
        )
        form = ICS213Form(data)
        
        # Serialize then deserialize
        json_str = form.to_json()
        new_form = ICS213Form.from_json(json_str)
        
        assert new_form.data.subject == "Test Message"
        assert new_form.data.to.name == "Jane"
        assert new_form.data.to.position == "IC"
        assert new_form.status == FormStatus.DRAFT
    
    def test_form_from_json_invalid(self):
        """Test form deserialization with invalid JSON."""
        with pytest.raises(ValidationError):
            ICS213Form.from_json("invalid json")
    
    def test_form_get_summary(self):
        """Test form summary generation."""
        data = ICS213Data(
            to=Person(name="Jane Doe", position="IC"),
            from_person=Person(name="John Smith", position="Ops Chief"),
            subject="Test Message"
        )
        
        form = ICS213Form(data)
        summary = form.get_summary()
        
        assert "Jane Doe, IC" in summary
        assert "John Smith, Ops Chief" in summary
        assert "Test Message" in summary
    
    def test_form_str_repr(self):
        """Test form string representations."""
        data = ICS213Data(subject="Test")
        form = ICS213Form(data)
        
        str_repr = str(form)
        assert "ICS213Form" in str_repr
        assert "Test" in str_repr
        
        repr_str = repr(form)
        assert "ICS213Form" in repr_str
        assert "Test" in repr_str
    
    def test_is_ready_for_approval(self):
        """Test is_ready_for_approval method."""
        # Valid form in draft status
        data = ICS213Data(
            to=Person(name="Jane Doe", position="IC"),
            from_person=Person(name="John Smith", position="Ops Chief"),
            subject="Test Message",
            date="2025-05-30",
            time="14:30",
            message="This is a test message"
        )
        
        form = ICS213Form(data)
        assert form.is_ready_for_approval()
        
        # Invalid form
        form = ICS213Form()
        assert not form.is_ready_for_approval()
        
        # Approved form
        form = ICS213Form(data)
        form.status = FormStatus.APPROVED
        assert not form.is_ready_for_approval()
    
    def test_is_ready_for_transmission(self):
        """Test is_ready_for_transmission method."""
        # Valid form with approver
        data = ICS213Data(
            to=Person(name="Jane Doe", position="IC"),
            from_person=Person(name="John Smith", position="Ops Chief"),
            subject="Test Message",
            date="2025-05-30",
            time="14:30",
            message="This is a test message",
            approved_by=Person(name="Approver", position="IC")
        )
        
        form = ICS213Form(data)
        assert form.is_ready_for_transmission()
        
        # Valid form without approver
        data.approved_by = Person()
        form = ICS213Form(data)
        assert not form.is_ready_for_transmission()
        
        # Invalid form
        form = ICS213Form()
        assert not form.is_ready_for_transmission()
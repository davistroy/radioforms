"""Unit tests for ICS-214 Activity Log data model and functionality.

This module provides comprehensive unit tests for the ICS-214 Activity Log
implementation, including data models, validation logic, JSON serialization,
and business rule compliance testing.

The tests follow the established testing patterns and ensure >95% coverage
of the ICS-214 module functionality as required by the development standards.

Test Categories:
    - ResourceAssignment model tests
    - ActivityEntry model tests  
    - OperationalPeriod model tests
    - ICS214Data model tests
    - ICS214Form model tests
    - Factory function tests
    - Validation function tests
    - JSON serialization tests
    - Business rule compliance tests

Example:
    Run all ICS-214 tests:
    >>> python -m pytest tests/unit/test_ics214.py -v
    
    Run specific test class:
    >>> python -m pytest tests/unit/test_ics214.py::TestICS214Data -v
"""

import pytest
import json
from datetime import datetime, date, time
from typing import List, Dict, Any

from src.models.ics214 import (
    ResourceAssignment, ActivityEntry, OperationalPeriod, Person,
    ICS214Data, ICS214Form, create_new_ics214, load_ics214_from_json,
    validate_activity_sequence
)


class TestResourceAssignment:
    """Test cases for ResourceAssignment data model."""
    
    def test_resource_assignment_creation(self):
        """Test basic resource assignment creation."""
        resource = ResourceAssignment(
            name="Engine 5240",
            ics_position="Single Resource",
            home_agency="CAL FIRE - Unit 5240",
            contact_info="Radio Channel 8"
        )
        
        assert resource.name == "Engine 5240"
        assert resource.ics_position == "Single Resource"
        assert resource.home_agency == "CAL FIRE - Unit 5240"
        assert resource.contact_info == "Radio Channel 8"
    
    def test_resource_assignment_default_values(self):
        """Test resource assignment with default values."""
        resource = ResourceAssignment()
        
        assert resource.name == ""
        assert resource.ics_position == ""
        assert resource.home_agency == ""
        assert resource.contact_info == ""
    
    def test_resource_assignment_post_init_cleanup(self):
        """Test string cleanup in post-initialization."""
        resource = ResourceAssignment(
            name="  Engine 5240  ",
            ics_position="  Single Resource  ",
            home_agency="  CAL FIRE  ",
            contact_info="  Radio 8  "
        )
        
        assert resource.name == "Engine 5240"
        assert resource.ics_position == "Single Resource"
        assert resource.home_agency == "CAL FIRE"
        assert resource.contact_info == "Radio 8"
    
    def test_resource_assignment_validation_valid(self):
        """Test validation of valid resource assignment."""
        resource = ResourceAssignment(
            name="Engine 5240",
            ics_position="Single Resource",
            home_agency="CAL FIRE"
        )
        
        assert resource.is_valid() is True
    
    def test_resource_assignment_validation_invalid_empty_name(self):
        """Test validation with empty name (invalid)."""
        resource = ResourceAssignment(
            name="",
            ics_position="Single Resource",
            home_agency="CAL FIRE"
        )
        
        assert resource.is_valid() is False
    
    def test_resource_assignment_validation_invalid_empty_position(self):
        """Test validation with empty position when position is set."""
        resource = ResourceAssignment(
            name="Engine 5240",
            ics_position="  ",  # Empty after strip
            home_agency="CAL FIRE"
        )
        
        assert resource.is_valid() is False
    
    def test_resource_assignment_to_dict(self):
        """Test conversion to dictionary."""
        resource = ResourceAssignment(
            name="Engine 5240",
            ics_position="Single Resource",
            home_agency="CAL FIRE",
            contact_info="Radio 8"
        )
        
        expected = {
            'name': 'Engine 5240',
            'ics_position': 'Single Resource',
            'home_agency': 'CAL FIRE',
            'contact_info': 'Radio 8'
        }
        
        assert resource.to_dict() == expected
    
    def test_resource_assignment_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'name': 'Engine 5240',
            'ics_position': 'Single Resource',
            'home_agency': 'CAL FIRE',
            'contact_info': 'Radio 8'
        }
        
        resource = ResourceAssignment.from_dict(data)
        
        assert resource.name == "Engine 5240"
        assert resource.ics_position == "Single Resource"
        assert resource.home_agency == "CAL FIRE"
        assert resource.contact_info == "Radio 8"
    
    def test_resource_assignment_from_dict_missing_fields(self):
        """Test creation from incomplete dictionary."""
        data = {'name': 'Engine 5240'}
        
        resource = ResourceAssignment.from_dict(data)
        
        assert resource.name == "Engine 5240"
        assert resource.ics_position == ""
        assert resource.home_agency == ""
        assert resource.contact_info == ""


class TestActivityEntry:
    """Test cases for ActivityEntry data model."""
    
    def test_activity_entry_creation(self):
        """Test basic activity entry creation."""
        dt = datetime(2024, 5, 30, 14, 30)
        activity = ActivityEntry(
            datetime=dt,
            notable_activities="Deployed strike team to Division A",
            location="Sector North",
            personnel_involved="Strike Team Leader, 4 crew members"
        )
        
        assert activity.datetime == dt
        assert activity.notable_activities == "Deployed strike team to Division A"
        assert activity.location == "Sector North"
        assert activity.personnel_involved == "Strike Team Leader, 4 crew members"
    
    def test_activity_entry_default_creation(self):
        """Test activity entry creation with defaults."""
        activity = ActivityEntry()
        
        # Should have current datetime (within 1 second)
        now = datetime.now()
        assert abs((activity.datetime - now).total_seconds()) < 1
        assert activity.notable_activities == ""
        assert activity.location == ""
        assert activity.personnel_involved == ""
    
    def test_activity_entry_post_init_cleanup(self):
        """Test string cleanup in post-initialization."""
        activity = ActivityEntry(
            notable_activities="  Important activity  ",
            location="  Location A  ",
            personnel_involved="  Person 1, Person 2  "
        )
        
        assert activity.notable_activities == "Important activity"
        assert activity.location == "Location A"
        assert activity.personnel_involved == "Person 1, Person 2"
    
    def test_activity_entry_validation_valid(self):
        """Test validation of valid activity entry."""
        activity = ActivityEntry(
            datetime=datetime(2024, 5, 30, 14, 30),
            notable_activities="Deployed resources to assigned location for containment operations"
        )
        
        assert activity.is_valid() is True
    
    def test_activity_entry_validation_invalid_empty_activities(self):
        """Test validation with empty activities (invalid)."""
        activity = ActivityEntry(
            datetime=datetime(2024, 5, 30, 14, 30),
            notable_activities=""
        )
        
        assert activity.is_valid() is False
    
    def test_activity_entry_validation_invalid_short_activities(self):
        """Test validation with too short activities (invalid)."""
        activity = ActivityEntry(
            datetime=datetime(2024, 5, 30, 14, 30),
            notable_activities="Short"  # Less than 10 characters
        )
        
        assert activity.is_valid() is False
    
    def test_activity_entry_validation_invalid_datetime(self):
        """Test validation with invalid datetime."""
        activity = ActivityEntry(
            datetime="not a datetime",  # Invalid datetime
            notable_activities="Valid activity description for testing purposes"
        )
        
        assert activity.is_valid() is False
    
    def test_activity_entry_format_time(self):
        """Test time formatting."""
        activity = ActivityEntry(datetime=datetime(2024, 5, 30, 14, 30, 45))
        
        assert activity.format_time() == "14:30"
    
    def test_activity_entry_format_date(self):
        """Test date formatting."""
        activity = ActivityEntry(datetime=datetime(2024, 5, 30, 14, 30, 45))
        
        assert activity.format_date() == "2024-05-30"
    
    def test_activity_entry_to_dict(self):
        """Test conversion to dictionary."""
        dt = datetime(2024, 5, 30, 14, 30)
        activity = ActivityEntry(
            datetime=dt,
            notable_activities="Test activity",
            location="Test location",
            personnel_involved="Test personnel"
        )
        
        result = activity.to_dict()
        
        assert result['datetime'] == dt.isoformat()
        assert result['notable_activities'] == "Test activity"
        assert result['location'] == "Test location"
        assert result['personnel_involved'] == "Test personnel"
    
    def test_activity_entry_from_dict(self):
        """Test creation from dictionary."""
        dt = datetime(2024, 5, 30, 14, 30)
        data = {
            'datetime': dt.isoformat(),
            'notable_activities': 'Test activity',
            'location': 'Test location',
            'personnel_involved': 'Test personnel'
        }
        
        activity = ActivityEntry.from_dict(data)
        
        assert activity.datetime == dt
        assert activity.notable_activities == "Test activity"
        assert activity.location == "Test location"
        assert activity.personnel_involved == "Test personnel"
    
    def test_activity_entry_from_dict_missing_datetime(self):
        """Test creation from dictionary with missing datetime."""
        data = {'notable_activities': 'Test activity'}
        
        activity = ActivityEntry.from_dict(data)
        
        # Should use current time
        now = datetime.now()
        assert abs((activity.datetime - now).total_seconds()) < 1
        assert activity.notable_activities == "Test activity"


class TestOperationalPeriod:
    """Test cases for OperationalPeriod data model."""
    
    def test_operational_period_creation(self):
        """Test basic operational period creation."""
        period = OperationalPeriod(
            from_date=date(2024, 5, 30),
            from_time=time(6, 0),
            to_date=date(2024, 5, 30),
            to_time=time(18, 0)
        )
        
        assert period.from_date == date(2024, 5, 30)
        assert period.from_time == time(6, 0)
        assert period.to_date == date(2024, 5, 30)
        assert period.to_time == time(18, 0)
    
    def test_operational_period_default_creation(self):
        """Test operational period creation with defaults."""
        period = OperationalPeriod()
        
        # Should use today's date with default times
        today = date.today()
        assert period.from_date == today
        assert period.to_date == today
        assert period.from_time == time(6, 0)
        assert period.to_time == time(18, 0)
    
    def test_operational_period_validation_valid_same_day(self):
        """Test validation of valid same-day period."""
        period = OperationalPeriod(
            from_date=date(2024, 5, 30),
            from_time=time(6, 0),
            to_date=date(2024, 5, 30),
            to_time=time(18, 0)
        )
        
        assert period.is_valid() is True
    
    def test_operational_period_validation_valid_multi_day(self):
        """Test validation of valid multi-day period."""
        period = OperationalPeriod(
            from_date=date(2024, 5, 30),
            from_time=time(18, 0),
            to_date=date(2024, 5, 31),
            to_time=time(6, 0)
        )
        
        assert period.is_valid() is True
    
    def test_operational_period_validation_invalid_same_time(self):
        """Test validation of invalid period (same start and end)."""
        period = OperationalPeriod(
            from_date=date(2024, 5, 30),
            from_time=time(12, 0),
            to_date=date(2024, 5, 30),
            to_time=time(12, 0)
        )
        
        assert period.is_valid() is False
    
    def test_operational_period_validation_invalid_end_before_start(self):
        """Test validation of invalid period (end before start)."""
        period = OperationalPeriod(
            from_date=date(2024, 5, 30),
            from_time=time(18, 0),
            to_date=date(2024, 5, 30),
            to_time=time(6, 0)
        )
        
        assert period.is_valid() is False
    
    def test_operational_period_format_same_day(self):
        """Test formatting of same-day period."""
        period = OperationalPeriod(
            from_date=date(2024, 5, 30),
            from_time=time(6, 0),
            to_date=date(2024, 5, 30),
            to_time=time(18, 0)
        )
        
        expected = "2024-05-30 06:00 - 18:00"
        assert period.format_period() == expected
    
    def test_operational_period_format_multi_day(self):
        """Test formatting of multi-day period."""
        period = OperationalPeriod(
            from_date=date(2024, 5, 30),
            from_time=time(18, 0),
            to_date=date(2024, 5, 31),
            to_time=time(6, 0)
        )
        
        expected = "2024-05-30 18:00 - 2024-05-31 06:00"
        assert period.format_period() == expected
    
    def test_operational_period_to_dict(self):
        """Test conversion to dictionary."""
        period = OperationalPeriod(
            from_date=date(2024, 5, 30),
            from_time=time(6, 0),
            to_date=date(2024, 5, 30),
            to_time=time(18, 0)
        )
        
        expected = {
            'from_date': '2024-05-30',
            'from_time': '06:00:00',
            'to_date': '2024-05-30',
            'to_time': '18:00:00'
        }
        
        assert period.to_dict() == expected
    
    def test_operational_period_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'from_date': '2024-05-30',
            'from_time': '06:00:00',
            'to_date': '2024-05-30',
            'to_time': '18:00:00'
        }
        
        period = OperationalPeriod.from_dict(data)
        
        assert period.from_date == date(2024, 5, 30)
        assert period.from_time == time(6, 0)
        assert period.to_date == date(2024, 5, 30)
        assert period.to_time == time(18, 0)


class TestICS214Data:
    """Test cases for ICS214Data main data model."""
    
    def test_ics214_data_creation(self):
        """Test basic ICS-214 data creation."""
        data = ICS214Data(
            incident_name="Test Incident",
            name="John Doe",
            ics_position="Operations Chief",
            home_agency="Test Agency"
        )
        
        assert data.incident_name == "Test Incident"
        assert data.name == "John Doe"
        assert data.ics_position == "Operations Chief"
        assert data.home_agency == "Test Agency"
        assert isinstance(data.operational_period, OperationalPeriod)
        assert data.resources_assigned == []
        assert data.activity_log == []
        assert isinstance(data.prepared_by, Person)
    
    def test_ics214_data_default_creation(self):
        """Test ICS-214 data creation with defaults."""
        data = ICS214Data()
        
        assert data.incident_name == ""
        assert data.name == ""
        assert data.ics_position == ""
        assert data.home_agency == ""
        assert isinstance(data.operational_period, OperationalPeriod)
        assert data.resources_assigned == []
        assert data.activity_log == []
        assert data.form_version == "ICS 214 (Rev. 9/2010)"
        assert data.page_number == "Page 1"
    
    def test_ics214_data_post_init_cleanup(self):
        """Test string cleanup in post-initialization."""
        data = ICS214Data(
            incident_name="  Test Incident  ",
            name="  John Doe  ",
            ics_position="  Operations Chief  ",
            home_agency="  Test Agency  "
        )
        
        assert data.incident_name == "Test Incident"
        assert data.name == "John Doe"
        assert data.ics_position == "Operations Chief"
        assert data.home_agency == "Test Agency"
    
    def test_ics214_data_validation_valid_minimal(self):
        """Test validation of minimal valid ICS-214 data."""
        data = ICS214Data(
            incident_name="Test Incident",
            name="John Doe",
            ics_position="Operations Chief",
            home_agency="Test Agency"
        )
        
        # Add required activity and prepared by
        activity = ActivityEntry(
            datetime=datetime.now(),
            notable_activities="Test activity for validation purposes"
        )
        data.activity_log.append(activity)
        data.prepared_by.name = "Jane Smith"
        
        assert data.is_valid() is True
    
    def test_ics214_data_validation_invalid_missing_incident_name(self):
        """Test validation with missing incident name."""
        data = ICS214Data(
            incident_name="",  # Missing
            name="John Doe",
            ics_position="Operations Chief",
            home_agency="Test Agency"
        )
        
        activity = ActivityEntry(
            datetime=datetime.now(),
            notable_activities="Test activity for validation purposes"
        )
        data.activity_log.append(activity)
        data.prepared_by.name = "Jane Smith"
        
        assert data.is_valid() is False
    
    def test_ics214_data_validation_invalid_missing_name(self):
        """Test validation with missing individual name."""
        data = ICS214Data(
            incident_name="Test Incident",
            name="",  # Missing
            ics_position="Operations Chief",
            home_agency="Test Agency"
        )
        
        activity = ActivityEntry(
            datetime=datetime.now(),
            notable_activities="Test activity for validation purposes"
        )
        data.activity_log.append(activity)
        data.prepared_by.name = "Jane Smith"
        
        assert data.is_valid() is False
    
    def test_ics214_data_validation_invalid_no_activities(self):
        """Test validation with no activity entries (R-ICS214-05)."""
        data = ICS214Data(
            incident_name="Test Incident",
            name="John Doe",
            ics_position="Operations Chief",
            home_agency="Test Agency"
        )
        
        data.prepared_by.name = "Jane Smith"
        # No activities added
        
        assert data.is_valid() is False
    
    def test_ics214_data_validation_invalid_bad_activity_sequence(self):
        """Test validation with invalid activity sequence (R-ICS214-07)."""
        data = ICS214Data(
            incident_name="Test Incident",
            name="John Doe",
            ics_position="Operations Chief",
            home_agency="Test Agency"
        )
        
        # Add activities in wrong chronological order
        activity1 = ActivityEntry(
            datetime=datetime(2024, 5, 30, 12, 0),
            notable_activities="Second activity in time but first in list"
        )
        activity2 = ActivityEntry(
            datetime=datetime(2024, 5, 30, 8, 0),
            notable_activities="First activity in time but second in list"
        )
        data.activity_log = [activity1, activity2]  # Wrong order
        data.prepared_by.name = "Jane Smith"
        
        assert data.is_valid() is False
    
    def test_ics214_data_sort_activities_by_time(self):
        """Test automatic sorting of activities by time."""
        data = ICS214Data()
        
        # Add activities out of order
        activity1 = ActivityEntry(
            datetime=datetime(2024, 5, 30, 12, 0),
            notable_activities="Second activity"
        )
        activity2 = ActivityEntry(
            datetime=datetime(2024, 5, 30, 8, 0),
            notable_activities="First activity"
        )
        activity3 = ActivityEntry(
            datetime=datetime(2024, 5, 30, 16, 0),
            notable_activities="Third activity"
        )
        
        data.activity_log = [activity1, activity2, activity3]
        data.sort_activities_by_time()
        
        # Should be sorted by datetime
        assert data.activity_log[0].datetime == datetime(2024, 5, 30, 8, 0)
        assert data.activity_log[1].datetime == datetime(2024, 5, 30, 12, 0)
        assert data.activity_log[2].datetime == datetime(2024, 5, 30, 16, 0)
    
    def test_ics214_data_add_activity_valid(self):
        """Test adding valid activity."""
        data = ICS214Data()
        
        activity = ActivityEntry(
            datetime=datetime.now(),
            notable_activities="Test activity for validation purposes"
        )
        
        result = data.add_activity(activity)
        
        assert result is True
        assert len(data.activity_log) == 1
        assert data.activity_log[0] == activity
    
    def test_ics214_data_add_activity_invalid(self):
        """Test adding invalid activity."""
        data = ICS214Data()
        
        activity = ActivityEntry(
            datetime=datetime.now(),
            notable_activities=""  # Invalid - empty
        )
        
        result = data.add_activity(activity)
        
        assert result is False
        assert len(data.activity_log) == 0
    
    def test_ics214_data_remove_activity_valid_index(self):
        """Test removing activity with valid index."""
        data = ICS214Data()
        
        activity = ActivityEntry(
            datetime=datetime.now(),
            notable_activities="Test activity for validation purposes"
        )
        data.activity_log.append(activity)
        
        result = data.remove_activity(0)
        
        assert result is True
        assert len(data.activity_log) == 0
    
    def test_ics214_data_remove_activity_invalid_index(self):
        """Test removing activity with invalid index."""
        data = ICS214Data()
        
        result = data.remove_activity(0)  # No activities exist
        
        assert result is False
    
    def test_ics214_data_add_resource_valid(self):
        """Test adding valid resource."""
        data = ICS214Data()
        
        resource = ResourceAssignment(name="Engine 5240")
        
        result = data.add_resource(resource)
        
        assert result is True
        assert len(data.resources_assigned) == 1
        assert data.resources_assigned[0] == resource
    
    def test_ics214_data_add_resource_invalid(self):
        """Test adding invalid resource."""
        data = ICS214Data()
        
        resource = ResourceAssignment(name="")  # Invalid - empty name
        
        result = data.add_resource(resource)
        
        assert result is False
        assert len(data.resources_assigned) == 0
    
    def test_ics214_data_remove_resource_valid_index(self):
        """Test removing resource with valid index."""
        data = ICS214Data()
        
        resource = ResourceAssignment(name="Engine 5240")
        data.resources_assigned.append(resource)
        
        result = data.remove_resource(0)
        
        assert result is True
        assert len(data.resources_assigned) == 0
    
    def test_ics214_data_remove_resource_invalid_index(self):
        """Test removing resource with invalid index."""
        data = ICS214Data()
        
        result = data.remove_resource(0)  # No resources exist
        
        assert result is False
    
    def test_ics214_data_get_counts(self):
        """Test getting activity and resource counts."""
        data = ICS214Data()
        
        # Add activities
        activity1 = ActivityEntry(
            datetime=datetime.now(),
            notable_activities="First activity for testing purposes"
        )
        activity2 = ActivityEntry(
            datetime=datetime.now(),
            notable_activities="Second activity for testing purposes"
        )
        data.activity_log = [activity1, activity2]
        
        # Add resources
        resource1 = ResourceAssignment(name="Engine 5240")
        resource2 = ResourceAssignment(name="Engine 5241")
        data.resources_assigned = [resource1, resource2]
        
        assert data.get_activity_count() == 2
        assert data.get_resource_count() == 2
    
    def test_ics214_data_to_json(self):
        """Test JSON serialization."""
        data = ICS214Data(
            incident_name="Test Incident",
            name="John Doe",
            ics_position="Operations Chief",
            home_agency="Test Agency"
        )
        
        json_str = data.to_json()
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed['form_type'] == 'ICS-214'
        assert parsed['incident_name'] == 'Test Incident'
        assert parsed['name'] == 'John Doe'
    
    def test_ics214_data_from_json(self):
        """Test JSON deserialization."""
        json_data = '''
        {
            "form_type": "ICS-214",
            "incident_name": "Test Incident",
            "name": "John Doe",
            "ics_position": "Operations Chief",
            "home_agency": "Test Agency",
            "operational_period": {
                "from_date": "2024-05-30",
                "from_time": "06:00:00",
                "to_date": "2024-05-30",
                "to_time": "18:00:00"
            },
            "resources_assigned": [],
            "activity_log": [],
            "prepared_by": {
                "name": "",
                "position": "",
                "signature": ""
            }
        }
        '''
        
        data = ICS214Data.from_json(json_data)
        
        assert data.incident_name == "Test Incident"
        assert data.name == "John Doe"
        assert data.ics_position == "Operations Chief"
        assert data.home_agency == "Test Agency"
    
    def test_ics214_data_from_json_invalid(self):
        """Test JSON deserialization with invalid data."""
        json_data = '{"invalid": "json structure"}'
        
        with pytest.raises(ValueError):
            ICS214Data.from_json(json_data)


class TestICS214Form:
    """Test cases for ICS214Form complete form model."""
    
    def test_ics214_form_creation(self):
        """Test basic ICS-214 form creation."""
        form = ICS214Form()
        
        assert isinstance(form.data, ICS214Data)
        assert form.form_id != ""
        assert form.status == "draft"
        assert form.tags == []
    
    def test_ics214_form_with_data(self):
        """Test ICS-214 form creation with data."""
        data = ICS214Data(incident_name="Test Incident")
        form = ICS214Form(data=data)
        
        assert form.data.incident_name == "Test Incident"
        assert form.form_id != ""
    
    def test_ics214_form_post_init_generates_id(self):
        """Test that post-init generates unique form ID."""
        form1 = ICS214Form()
        form2 = ICS214Form()
        
        assert form1.form_id != form2.form_id
        assert form1.form_id.startswith("ics214_")
        assert form2.form_id.startswith("ics214_")
    
    def test_ics214_form_validation(self):
        """Test form validation delegates to data model."""
        form = ICS214Form()
        
        # Initially invalid (missing required fields)
        assert form.is_valid() is False
        
        # Make data valid
        form.data.incident_name = "Test Incident"
        form.data.name = "John Doe"
        form.data.ics_position = "Operations Chief"
        form.data.home_agency = "Test Agency"
        form.data.prepared_by.name = "Jane Smith"
        
        activity = ActivityEntry(
            datetime=datetime.now(),
            notable_activities="Test activity for validation purposes"
        )
        form.data.activity_log.append(activity)
        
        assert form.is_valid() is True
    
    def test_ics214_form_set_status_valid(self):
        """Test setting valid status."""
        form = ICS214Form()
        
        assert form.set_status("completed") is True
        assert form.status == "completed"
        
        assert form.set_status("submitted") is True
        assert form.status == "submitted"
        
        assert form.set_status("archived") is True
        assert form.status == "archived"
    
    def test_ics214_form_set_status_invalid(self):
        """Test setting invalid status."""
        form = ICS214Form()
        original_status = form.status
        
        assert form.set_status("invalid_status") is False
        assert form.status == original_status
    
    def test_ics214_form_add_tag(self):
        """Test adding tags."""
        form = ICS214Form()
        
        assert form.add_tag("training") is True
        assert "training" in form.tags
        
        assert form.add_tag("exercise") is True
        assert "exercise" in form.tags
        
        # Duplicate tag should not be added
        assert form.add_tag("training") is False
        assert form.tags.count("training") == 1
    
    def test_ics214_form_remove_tag(self):
        """Test removing tags."""
        form = ICS214Form()
        form.tags = ["training", "exercise"]
        
        assert form.remove_tag("training") is True
        assert "training" not in form.tags
        
        assert form.remove_tag("nonexistent") is False
    
    def test_ics214_form_to_json(self):
        """Test complete form JSON serialization."""
        form = ICS214Form()
        form.data.incident_name = "Test Incident"
        form.set_status("completed")
        form.add_tag("training")
        
        json_str = form.to_json()
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed['form_id'] == form.form_id
        assert parsed['status'] == "completed"
        assert parsed['tags'] == ["training"]
        assert parsed['incident_name'] == "Test Incident"
    
    def test_ics214_form_from_json(self):
        """Test complete form JSON deserialization."""
        json_data = '''
        {
            "form_type": "ICS-214",
            "form_id": "test_form_id",
            "status": "completed",
            "tags": ["training", "exercise"],
            "incident_name": "Test Incident",
            "name": "John Doe",
            "ics_position": "Operations Chief",
            "home_agency": "Test Agency",
            "operational_period": {
                "from_date": "2024-05-30",
                "from_time": "06:00:00",
                "to_date": "2024-05-30",
                "to_time": "18:00:00"
            },
            "resources_assigned": [],
            "activity_log": [],
            "prepared_by": {
                "name": "",
                "position": "",
                "signature": ""
            }
        }
        '''
        
        form = ICS214Form.from_json(json_data)
        
        assert form.form_id == "test_form_id"
        assert form.status == "completed"
        assert form.tags == ["training", "exercise"]
        assert form.data.incident_name == "Test Incident"


class TestFactoryFunctions:
    """Test cases for factory functions."""
    
    def test_create_new_ics214(self):
        """Test create_new_ics214 factory function."""
        form = create_new_ics214()
        
        assert isinstance(form, ICS214Form)
        assert isinstance(form.data, ICS214Data)
        assert form.status == "draft"
        assert form.form_id != ""
    
    def test_load_ics214_from_json(self):
        """Test load_ics214_from_json factory function."""
        json_data = '''
        {
            "form_type": "ICS-214",
            "incident_name": "Test Incident",
            "name": "John Doe",
            "ics_position": "Operations Chief",
            "home_agency": "Test Agency",
            "operational_period": {
                "from_date": "2024-05-30",
                "from_time": "06:00:00",
                "to_date": "2024-05-30",
                "to_time": "18:00:00"
            },
            "resources_assigned": [],
            "activity_log": [],
            "prepared_by": {
                "name": "",
                "position": "",
                "signature": ""
            }
        }
        '''
        
        form = load_ics214_from_json(json_data)
        
        assert isinstance(form, ICS214Form)
        assert form.data.incident_name == "Test Incident"
        assert form.data.name == "John Doe"


class TestValidationFunctions:
    """Test cases for validation utility functions."""
    
    def test_validate_activity_sequence_valid_empty(self):
        """Test validation of empty activity sequence."""
        activities = []
        
        assert validate_activity_sequence(activities) is True
    
    def test_validate_activity_sequence_valid_single(self):
        """Test validation of single activity."""
        activities = [
            ActivityEntry(
                datetime=datetime(2024, 5, 30, 8, 0),
                notable_activities="Single activity for testing purposes"
            )
        ]
        
        assert validate_activity_sequence(activities) is True
    
    def test_validate_activity_sequence_valid_multiple(self):
        """Test validation of valid chronological sequence."""
        activities = [
            ActivityEntry(
                datetime=datetime(2024, 5, 30, 8, 0),
                notable_activities="First activity for testing purposes"
            ),
            ActivityEntry(
                datetime=datetime(2024, 5, 30, 12, 0),
                notable_activities="Second activity for testing purposes"
            ),
            ActivityEntry(
                datetime=datetime(2024, 5, 30, 16, 0),
                notable_activities="Third activity for testing purposes"
            )
        ]
        
        assert validate_activity_sequence(activities) is True
    
    def test_validate_activity_sequence_invalid_out_of_order(self):
        """Test validation of invalid chronological sequence."""
        activities = [
            ActivityEntry(
                datetime=datetime(2024, 5, 30, 12, 0),
                notable_activities="Second activity in chronological order"
            ),
            ActivityEntry(
                datetime=datetime(2024, 5, 30, 8, 0),
                notable_activities="First activity in chronological order"
            )
        ]
        
        assert validate_activity_sequence(activities) is False


class TestBusinessRuleCompliance:
    """Test cases for ICS-214 business rule compliance."""
    
    def test_rule_ics214_01_incident_name_required(self):
        """Test business rule R-ICS214-01: Incident Name must be provided."""
        data = ICS214Data(
            incident_name="",  # Violates R-ICS214-01
            name="John Doe",
            ics_position="Operations Chief",
            home_agency="Test Agency"
        )
        
        activity = ActivityEntry(
            datetime=datetime.now(),
            notable_activities="Test activity for validation purposes"
        )
        data.activity_log.append(activity)
        data.prepared_by.name = "Jane Smith"
        
        assert data.is_valid() is False
    
    def test_rule_ics214_02_operational_period_valid(self):
        """Test business rule R-ICS214-02: Operational Period must be valid."""
        data = ICS214Data(
            incident_name="Test Incident",
            name="John Doe",
            ics_position="Operations Chief",
            home_agency="Test Agency"
        )
        
        # Invalid operational period (end before start)
        data.operational_period = OperationalPeriod(
            from_date=date(2024, 5, 30),
            from_time=time(18, 0),
            to_date=date(2024, 5, 30),
            to_time=time(6, 0)
        )
        
        activity = ActivityEntry(
            datetime=datetime.now(),
            notable_activities="Test activity for validation purposes"
        )
        data.activity_log.append(activity)
        data.prepared_by.name = "Jane Smith"
        
        assert data.is_valid() is False
    
    def test_rule_ics214_05_at_least_one_activity(self):
        """Test business rule R-ICS214-05: At least one activity should be recorded."""
        data = ICS214Data(
            incident_name="Test Incident",
            name="John Doe",
            ics_position="Operations Chief",
            home_agency="Test Agency"
        )
        
        data.prepared_by.name = "Jane Smith"
        # No activities - violates R-ICS214-05
        
        assert data.is_valid() is False
    
    def test_rule_ics214_06_activity_entries_complete(self):
        """Test business rule R-ICS214-06: Activities must include datetime and description."""
        data = ICS214Data(
            incident_name="Test Incident",
            name="John Doe",
            ics_position="Operations Chief",
            home_agency="Test Agency"
        )
        
        # Activity with missing description - violates R-ICS214-06
        activity = ActivityEntry(
            datetime=datetime.now(),
            notable_activities=""  # Missing description
        )
        data.activity_log.append(activity)
        data.prepared_by.name = "Jane Smith"
        
        assert data.is_valid() is False
    
    def test_rule_ics214_07_chronological_order(self):
        """Test business rule R-ICS214-07: Activities should be in chronological order."""
        data = ICS214Data(
            incident_name="Test Incident",
            name="John Doe",
            ics_position="Operations Chief",
            home_agency="Test Agency"
        )
        
        # Activities out of chronological order - violates R-ICS214-07
        activity1 = ActivityEntry(
            datetime=datetime(2024, 5, 30, 12, 0),
            notable_activities="Second activity chronologically"
        )
        activity2 = ActivityEntry(
            datetime=datetime(2024, 5, 30, 8, 0),
            notable_activities="First activity chronologically"
        )
        data.activity_log = [activity1, activity2]  # Wrong order
        data.prepared_by.name = "Jane Smith"
        
        assert data.is_valid() is False
    
    def test_rule_ics214_08_prepared_by_required(self):
        """Test business rule R-ICS214-08: Prepared By must include name, position, signature."""
        data = ICS214Data(
            incident_name="Test Incident",
            name="John Doe",
            ics_position="Operations Chief",
            home_agency="Test Agency"
        )
        
        activity = ActivityEntry(
            datetime=datetime.now(),
            notable_activities="Test activity for validation purposes"
        )
        data.activity_log.append(activity)
        # Missing prepared by name - violates R-ICS214-08
        data.prepared_by.name = ""
        
        assert data.is_valid() is False


if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v", "--tb=short"])
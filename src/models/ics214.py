"""ICS-214 Activity Log data model and validation.

This module provides comprehensive data models for ICS-214 Activity Log forms,
following FEMA standards for incident command system documentation. The ICS-214
is used to record chronological activities and resource assignments for personnel
during incident operations.

The module implements a repeatable activity tracking system with time-sequence
validation and multi-day operational period support as specified in the ICS-214
form analysis and RadioForms requirements.

Example:
    >>> from datetime import datetime
    >>> 
    >>> # Create activity entries
    >>> activities = [
    ...     ActivityEntry(
    ...         datetime=datetime(2024, 5, 30, 8, 0),
    ...         notable_activities="Arrived on scene, assumed Operations Chief role"
    ...     ),
    ...     ActivityEntry(
    ...         datetime=datetime(2024, 5, 30, 9, 30),
    ...         notable_activities="Established operational sectors, deployed resources"
    ...     )
    ... ]
    >>> 
    >>> # Create ICS-214 form
    >>> form = ICS214Data(
    ...     incident_name="Mountain View Wildfire",
    ...     name="John Smith",
    ...     ics_position="Operations Section Chief",
    ...     home_agency="CAL FIRE - Unit 5240",
    ...     activity_log=activities
    ... )
    >>> 
    >>> # Validate and process
    >>> if form.is_valid():
    ...     json_data = form.to_json()
    ...     print(f"Activity log contains {len(form.activity_log)} entries")

Classes:
    ResourceAssignment: Represents a resource assigned to the individual
    ActivityEntry: Represents a single notable activity with timestamp
    OperationalPeriod: Represents the operational period date/time range
    Person: Person information for prepared by section (imported from ics213)
    ICS214Data: Complete ICS-214 form data model
    ICS214Form: Complete form with UI integration capabilities

Functions:
    create_new_ics214: Factory function for creating new ICS-214 forms
    load_ics214_from_json: Load ICS-214 from JSON representation
    validate_activity_sequence: Validate chronological order of activities

Notes:
    This implementation follows the FEMA ICS-214 specification with emphasis
    on activity tracking, resource management, and time sequence validation.
    The design supports both individual and unit-level activity logging.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

# Import shared person class from ICS-213 and base form interface
try:
    from ..forms.ics213 import Person
    from .base_form import BaseForm, FormType, FormValidationResult
except ImportError:
    # For standalone testing, import from absolute path
    import sys
    sys.path.append('.')
    from src.forms.ics213 import Person
    from src.models.base_form import BaseForm, FormType, FormValidationResult


@dataclass
class ResourceAssignment:
    """Represents a resource assigned to an individual for ICS-214 forms.
    
    This class encapsulates information about resources (personnel, equipment,
    or units) assigned to the individual completing the activity log. Used in
    the Resources Assigned section of ICS-214 forms.
    
    Attributes:
        name (str): Name of the assigned resource (person, equipment, etc.).
        ics_position (str): ICS position or role of the resource.
        home_agency (str): Agency and unit designation of the resource.
        contact_info (str): Optional contact information for the resource.
        
    Example:
        >>> resource = ResourceAssignment(
        ...     name="Engine 5240",
        ...     ics_position="Single Resource",
        ...     home_agency="CAL FIRE - Unit 5240",
        ...     contact_info="Radio Channel 8"
        ... )
        >>> print(f"Resource: {resource.name} from {resource.home_agency}")
    """
    
    name: str = ""
    ics_position: str = ""
    home_agency: str = ""
    contact_info: str = ""
    
    def __post_init__(self) -> None:
        """Post-initialization validation and cleanup."""
        # Clean up string fields
        self.name = self.name.strip()
        self.ics_position = self.ics_position.strip()
        self.home_agency = self.home_agency.strip()
        self.contact_info = self.contact_info.strip()
    
    def is_valid(self) -> bool:
        """Validate resource assignment data.
        
        Returns:
            bool: True if the resource assignment data is valid, False otherwise.
            
        Notes:
            Resource name is required. Other fields are optional but recommended
            for complete resource tracking and contact purposes.
        """
        # Name is required for resource assignment
        if not self.name.strip():
            return False
            
        # If position is specified, it should not be empty
        if self.ics_position and not self.ics_position.strip():
            return False
            
        return True
    
    def to_dict(self) -> Dict[str, str]:
        """Convert resource assignment to dictionary representation.
        
        Returns:
            Dict[str, str]: Dictionary containing all resource assignment fields.
        """
        return {
            'name': self.name,
            'ics_position': self.ics_position,
            'home_agency': self.home_agency,
            'contact_info': self.contact_info
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> ResourceAssignment:
        """Create ResourceAssignment from dictionary data.
        
        Args:
            data: Dictionary containing resource assignment fields.
            
        Returns:
            ResourceAssignment: New resource assignment instance.
        """
        return cls(
            name=data.get('name', ''),
            ics_position=data.get('ics_position', ''),
            home_agency=data.get('home_agency', ''),
            contact_info=data.get('contact_info', '')
        )


@dataclass
class ActivityEntry:
    """Represents a single notable activity entry in ICS-214 Activity Log.
    
    This class captures individual activities with timestamps for chronological
    documentation in the ICS-214 Activity Log section. Each entry represents
    a significant event or action during the operational period.
    
    Attributes:
        datetime (datetime): When the activity occurred (required).
        notable_activities (str): Description of the activity (required).
        location (str): Optional location where activity occurred.
        personnel_involved (str): Optional personnel involved in activity.
        
    Example:
        >>> from datetime import datetime
        >>> activity = ActivityEntry(
        ...     datetime=datetime(2024, 5, 30, 14, 30),
        ...     notable_activities="Deployed strike team to Division A",
        ...     location="Sector North",
        ...     personnel_involved="Strike Team Leader, 4 crew members"
        ... )
        >>> print(f"Activity at {activity.datetime}: {activity.notable_activities}")
    """
    
    datetime: datetime = field(default_factory=datetime.now)
    notable_activities: str = ""
    location: str = ""
    personnel_involved: str = ""
    
    def __post_init__(self) -> None:
        """Post-initialization validation and cleanup."""
        # Clean up string fields
        self.notable_activities = self.notable_activities.strip()
        self.location = self.location.strip()
        self.personnel_involved = self.personnel_involved.strip()
        
        # Ensure datetime is properly initialized
        if not isinstance(self.datetime, datetime):
            self.datetime = datetime.now()
    
    def is_valid(self) -> bool:
        """Validate activity entry data.
        
        Returns:
            bool: True if the activity entry is valid, False otherwise.
            
        Notes:
            Both datetime and notable_activities are required fields.
            The activity description should be meaningful and not empty.
        """
        # DateTime and activities are required
        if not isinstance(self.datetime, datetime):
            return False
            
        if not self.notable_activities.strip():
            return False
        
        # Activity description should be meaningful (at least 10 characters)
        if len(self.notable_activities.strip()) < 10:
            return False
            
        return True
    
    def to_dict(self) -> Dict[str, str]:
        """Convert activity entry to dictionary representation.
        
        Returns:
            Dict[str, str]: Dictionary containing all activity entry fields.
        """
        return {
            'datetime': self.datetime.isoformat(),
            'notable_activities': self.notable_activities,
            'location': self.location,
            'personnel_involved': self.personnel_involved
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> ActivityEntry:
        """Create ActivityEntry from dictionary data.
        
        Args:
            data: Dictionary containing activity entry fields.
            
        Returns:
            ActivityEntry: New activity entry instance.
            
        Raises:
            ValueError: If datetime string cannot be parsed.
        """
        # Parse datetime from ISO format
        dt_str = data.get('datetime', '')
        if dt_str:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        else:
            dt = datetime.now()
            
        return cls(
            datetime=dt,
            notable_activities=data.get('notable_activities', ''),
            location=data.get('location', ''),
            personnel_involved=data.get('personnel_involved', '')
        )
    
    def format_time(self) -> str:
        """Format activity time for display.
        
        Returns:
            str: Formatted time string (HH:MM format).
        """
        return self.datetime.strftime("%H:%M")
    
    def format_date(self) -> str:
        """Format activity date for display.
        
        Returns:
            str: Formatted date string (YYYY-MM-DD format).
        """
        return self.datetime.strftime("%Y-%m-%d")


@dataclass
class OperationalPeriod:
    """Represents the operational period for ICS-214 forms.
    
    This class defines the time interval for which the activity log applies,
    supporting both single-day and multi-day operational periods as required
    by ICS-214 specifications.
    
    Attributes:
        from_date (date): Start date of operational period.
        from_time (time): Start time of operational period.
        to_date (date): End date of operational period.
        to_time (time): End time of operational period.
        
    Example:
        >>> from datetime import date, time
        >>> period = OperationalPeriod(
        ...     from_date=date(2024, 5, 30),
        ...     from_time=time(6, 0),
        ...     to_date=date(2024, 5, 30),
        ...     to_time=time(18, 0)
        ... )
        >>> print(f"Period: {period.format_period()}")
    """
    
    from_date: date = field(default_factory=date.today)
    from_time: time = field(default_factory=lambda: time(6, 0))
    to_date: date = field(default_factory=date.today)
    to_time: time = field(default_factory=lambda: time(18, 0))
    
    def is_valid(self) -> bool:
        """Validate operational period data.
        
        Returns:
            bool: True if the operational period is valid, False otherwise.
            
        Notes:
            End date/time must be after start date/time for valid period.
        """
        # Create datetime objects for comparison
        start_datetime = datetime.combine(self.from_date, self.from_time)
        end_datetime = datetime.combine(self.to_date, self.to_time)
        
        # End must be after start
        return end_datetime > start_datetime
    
    def format_period(self) -> str:
        """Format operational period for display.
        
        Returns:
            str: Formatted operational period string.
        """
        if self.from_date == self.to_date:
            return f"{self.from_date.strftime('%Y-%m-%d')} {self.from_time.strftime('%H:%M')} - {self.to_time.strftime('%H:%M')}"
        else:
            return f"{self.from_date.strftime('%Y-%m-%d')} {self.from_time.strftime('%H:%M')} - {self.to_date.strftime('%Y-%m-%d')} {self.to_time.strftime('%H:%M')}"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert operational period to dictionary representation.
        
        Returns:
            Dict[str, str]: Dictionary containing all period fields.
        """
        return {
            'from_date': self.from_date.isoformat(),
            'from_time': self.from_time.isoformat(),
            'to_date': self.to_date.isoformat(),
            'to_time': self.to_time.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> OperationalPeriod:
        """Create OperationalPeriod from dictionary data.
        
        Args:
            data: Dictionary containing operational period fields.
            
        Returns:
            OperationalPeriod: New operational period instance.
        """
        return cls(
            from_date=date.fromisoformat(data.get('from_date', date.today().isoformat())),
            from_time=time.fromisoformat(data.get('from_time', '06:00:00')),
            to_date=date.fromisoformat(data.get('to_date', date.today().isoformat())),
            to_time=time.fromisoformat(data.get('to_time', '18:00:00'))
        )


@dataclass
class ICS214Data:
    """Complete data model for ICS-214 Activity Log forms.
    
    This class represents all data fields and sections of an ICS-214 Activity Log
    form as specified by FEMA standards. It includes header information, resource
    assignments, activity entries, and footer information with comprehensive
    validation and serialization capabilities.
    
    The model supports dynamic activity tracking, time-sequence validation,
    and multi-day operational periods as required for incident documentation.
    
    Attributes:
        incident_name (str): Name assigned to the incident (required).
        operational_period (OperationalPeriod): Time interval for the log.
        name (str): Name of individual completing the log (required).
        ics_position (str): ICS position of individual (required).
        home_agency (str): Agency and unit of individual (required).
        resources_assigned (List[ResourceAssignment]): Resources assigned to individual.
        activity_log (List[ActivityEntry]): Chronological list of activities (required).
        prepared_by (Person): Information about form preparer (required).
        form_version (str): Version of ICS-214 form being used.
        page_number (str): Page number information.
        
    Example:
        >>> form = ICS214Data(
        ...     incident_name="River Flood Response",
        ...     name="Jane Doe",
        ...     ics_position="Logistics Section Chief",
        ...     home_agency="County Emergency Services"
        ... )
        >>> 
        >>> # Add activity
        >>> activity = ActivityEntry(
        ...     datetime=datetime(2024, 5, 30, 10, 0),
        ...     notable_activities="Established supply distribution point"
        ... )
        >>> form.activity_log.append(activity)
        >>> 
        >>> if form.is_valid():
        ...     json_output = form.to_json()
    """
    
    # Header fields - incident and individual identification
    incident_name: str = ""
    operational_period: OperationalPeriod = field(default_factory=OperationalPeriod)
    name: str = ""
    ics_position: str = ""
    home_agency: str = ""
    
    # Resources assigned section
    resources_assigned: List[ResourceAssignment] = field(default_factory=list)
    
    # Activity log section - main content
    activity_log: List[ActivityEntry] = field(default_factory=list)
    
    # Footer section
    prepared_by: Person = field(default_factory=Person)
    
    # Metadata fields
    form_version: str = "ICS 214 (Rev. 9/2010)"
    page_number: str = "Page 1"
    created_date: datetime = field(default_factory=datetime.now)
    modified_date: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self) -> None:
        """Post-initialization validation and cleanup."""
        # Clean up string fields
        self.incident_name = self.incident_name.strip()
        self.name = self.name.strip()
        self.ics_position = self.ics_position.strip()
        self.home_agency = self.home_agency.strip()
        self.form_version = self.form_version.strip()
        self.page_number = self.page_number.strip()
        
        # Update modified date
        self.modified_date = datetime.now()
        
        # Sort activities by datetime
        self.sort_activities_by_time()
    
    def is_valid(self) -> bool:
        """Validate complete ICS-214 form data.
        
        Returns:
            bool: True if all form data is valid, False otherwise.
            
        Notes:
            Validates all required fields, operational period, activity entries,
            and resource assignments according to ICS-214 business rules.
        """
        # Validate required header fields
        if not self.incident_name.strip():
            return False
        if not self.name.strip():
            return False
        if not self.ics_position.strip():
            return False
        if not self.home_agency.strip():
            return False
        
        # Validate operational period
        if not self.operational_period.is_valid():
            return False
        
        # At least one activity entry should be present (R-ICS214-05)
        if len(self.activity_log) == 0:
            return False
        
        # Validate all activity entries
        for activity in self.activity_log:
            if not activity.is_valid():
                return False
        
        # Validate all resource assignments
        for resource in self.resources_assigned:
            if not resource.is_valid():
                return False
        
        # Validate prepared by information
        if not self.prepared_by.name.strip():
            return False
        
        # Validate activity chronological order (R-ICS214-07)
        if not self.is_activity_sequence_valid():
            return False
        
        return True
    
    def sort_activities_by_time(self) -> None:
        """Sort activity entries by datetime in chronological order.
        
        Notes:
            This method ensures activities are maintained in chronological
            order as required by ICS-214 business rule R-ICS214-07.
        """
        self.activity_log.sort(key=lambda x: x.datetime)
    
    def is_activity_sequence_valid(self) -> bool:
        """Validate that activities are in chronological order.
        
        Returns:
            bool: True if activities are in proper chronological sequence.
            
        Notes:
            Implements business rule R-ICS214-07 for chronological ordering.
        """
        if len(self.activity_log) <= 1:
            return True
        
        for i in range(1, len(self.activity_log)):
            if self.activity_log[i].datetime < self.activity_log[i-1].datetime:
                return False
        
        return True
    
    def add_activity(self, activity: ActivityEntry) -> bool:
        """Add a new activity entry to the log.
        
        Args:
            activity: Activity entry to add to the log.
            
        Returns:
            bool: True if activity was added successfully, False otherwise.
            
        Notes:
            Activities are automatically sorted after addition to maintain
            chronological order as required by ICS-214 specifications.
        """
        if not activity.is_valid():
            return False
        
        self.activity_log.append(activity)
        self.sort_activities_by_time()
        self.modified_date = datetime.now()
        return True
    
    def remove_activity(self, index: int) -> bool:
        """Remove an activity entry from the log.
        
        Args:
            index: Index of activity to remove from the log.
            
        Returns:
            bool: True if activity was removed successfully, False otherwise.
        """
        if 0 <= index < len(self.activity_log):
            del self.activity_log[index]
            self.modified_date = datetime.now()
            return True
        return False
    
    def add_resource(self, resource: ResourceAssignment) -> bool:
        """Add a resource assignment to the form.
        
        Args:
            resource: Resource assignment to add to the form.
            
        Returns:
            bool: True if resource was added successfully, False otherwise.
        """
        if not resource.is_valid():
            return False
        
        self.resources_assigned.append(resource)
        self.modified_date = datetime.now()
        return True
    
    def remove_resource(self, index: int) -> bool:
        """Remove a resource assignment from the form.
        
        Args:
            index: Index of resource to remove from assignments.
            
        Returns:
            bool: True if resource was removed successfully, False otherwise.
        """
        if 0 <= index < len(self.resources_assigned):
            del self.resources_assigned[index]
            self.modified_date = datetime.now()
            return True
        return False
    
    def get_activity_count(self) -> int:
        """Get the total number of activity entries.
        
        Returns:
            int: Number of activity entries in the log.
        """
        return len(self.activity_log)
    
    def get_resource_count(self) -> int:
        """Get the total number of resource assignments.
        
        Returns:
            int: Number of resource assignments.
        """
        return len(self.resources_assigned)
    
    def to_json(self) -> str:
        """Serialize ICS-214 form data to JSON format.
        
        Returns:
            str: JSON representation of the form data.
            
        Example:
            >>> form = ICS214Data(incident_name="Test Incident")
            >>> json_data = form.to_json()
            >>> print(json_data)
        """
        data = {
            'form_type': 'ICS-214',
            'form_version': self.form_version,
            'incident_name': self.incident_name,
            'operational_period': self.operational_period.to_dict(),
            'name': self.name,
            'ics_position': self.ics_position,
            'home_agency': self.home_agency,
            'resources_assigned': [resource.to_dict() for resource in self.resources_assigned],
            'activity_log': [activity.to_dict() for activity in self.activity_log],
            'prepared_by': self.prepared_by.to_dict(),
            'page_number': self.page_number,
            'created_date': self.created_date.isoformat(),
            'modified_date': self.modified_date.isoformat()
        }
        return json.dumps(data, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ICS214Data:
        """Create ICS214Data from dictionary representation.
        
        Args:
            data: Dictionary containing form data.
            
        Returns:
            ICS214Data: New form instance from dictionary data.
            
        Raises:
            ValueError: If data is invalid or malformed.
        """
        try:
            # Parse operational period
            op_period = OperationalPeriod.from_dict(data.get('operational_period', {}))
            
            # Parse resources assigned
            resources = [
                ResourceAssignment.from_dict(resource_data)
                for resource_data in data.get('resources_assigned', [])
            ]
            
            # Parse activity log
            activities = [
                ActivityEntry.from_dict(activity_data)
                for activity_data in data.get('activity_log', [])
            ]
            
            # Parse prepared by person
            prepared_by = Person.from_dict(data.get('prepared_by', {}))
            
            # Parse datetime fields
            created_date = datetime.now()
            modified_date = datetime.now()
            
            if data.get('created_date'):
                created_date = datetime.fromisoformat(data['created_date'].replace('Z', '+00:00'))
            if data.get('modified_date'):
                modified_date = datetime.fromisoformat(data['modified_date'].replace('Z', '+00:00'))
            
            return cls(
                incident_name=data.get('incident_name', ''),
                operational_period=op_period,
                name=data.get('name', ''),
                ics_position=data.get('ics_position', ''),
                home_agency=data.get('home_agency', ''),
                resources_assigned=resources,
                activity_log=activities,
                prepared_by=prepared_by,
                form_version=data.get('form_version', 'ICS 214 (Rev. 9/2010)'),
                page_number=data.get('page_number', 'Page 1'),
                created_date=created_date,
                modified_date=modified_date
            )
            
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid data for ICS-214 form: {e}")
    
    @classmethod
    def from_json(cls, json_data: str) -> ICS214Data:
        """Create ICS214Data from JSON representation.
        
        Args:
            json_data: JSON string containing form data.
            
        Returns:
            ICS214Data: New form instance from JSON data.
            
        Raises:
            ValueError: If JSON data is invalid or malformed.
        """
        try:
            data = json.loads(json_data)
            return cls.from_dict(data)
            
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid JSON data for ICS-214 form: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert form data to dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary containing all form data.
        """
        return {
            'form_type': 'ICS-214',
            'form_version': self.form_version,
            'incident_name': self.incident_name,
            'operational_period': self.operational_period.to_dict(),
            'name': self.name,
            'ics_position': self.ics_position,
            'home_agency': self.home_agency,
            'resources_assigned': [resource.to_dict() for resource in self.resources_assigned],
            'activity_log': [activity.to_dict() for activity in self.activity_log],
            'prepared_by': self.prepared_by.to_dict(),
            'page_number': self.page_number,
            'created_date': self.created_date.isoformat(),
            'modified_date': self.modified_date.isoformat()
        }


class ICS214Form(BaseForm):
    """Complete ICS-214 form with UI integration capabilities.
    
    This class extends ICS214Data with additional functionality for UI integration,
    form lifecycle management, and advanced operations required by the RadioForms
    application architecture.
    
    Attributes:
        data (ICS214Data): Core form data model.
        form_id (str): Unique identifier for the form instance.
        status (str): Current form status (draft, completed, submitted).
        tags (List[str]): User-defined tags for organization.
        
    Example:
        >>> form = ICS214Form()
        >>> form.data.incident_name = "Training Exercise"
        >>> form.data.name = "Training Officer"
        >>> form.set_status("draft")
        >>> form.add_tag("training")
    """
    
    def __init__(self, data: Optional[ICS214Data] = None) -> None:
        """Initialize ICS-214 form with optional data.
        
        Args:
            data: Optional ICS214Data instance to initialize with.
        """
        # Initialize base form
        super().__init__()
        self.metadata.form_type = FormType.ICS_214
        
        # Initialize ICS-214 specific data
        self.data = data or ICS214Data()
        self.form_id = ""
        self.status = "draft"  # draft, completed, submitted, archived
        
        # Generate unique form ID based on timestamp
        if not self.form_id:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            self.form_id = f"ics214_{timestamp}"
    
    def is_valid(self) -> bool:
        """Validate the complete form including UI state.
        
        Returns:
            bool: True if form is valid, False otherwise.
        """
        return self.data.is_valid()
    
    def set_status(self, status: str) -> bool:
        """Set the form status.
        
        Args:
            status: New status value (draft, completed, submitted, archived).
            
        Returns:
            bool: True if status was set successfully, False otherwise.
        """
        valid_statuses = {'draft', 'completed', 'submitted', 'archived'}
        if status in valid_statuses:
            self.status = status
            self.data.modified_date = datetime.now()
            return True
        return False
    
    # Tag methods inherited from BaseForm
    
    # JSON serialization inherited from BaseForm
    
    # JSON deserialization inherited from BaseForm
    
    # BaseForm interface implementation
    
    def get_form_type(self) -> FormType:
        """Get the type of this form.
        
        Returns:
            FormType: The ICS-214 form type.
        """
        return FormType.ICS_214
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert form to dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary containing all form data.
        """
        form_dict = self.data.to_dict()
        form_dict.update({
            'form_id': self.form_id,
            'status': self.status,
        })
        return form_dict
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load form data from dictionary representation.
        
        Args:
            data: Dictionary containing form data.
        """
        # Extract form metadata
        self.form_id = data.pop('form_id', '')
        self.status = data.pop('status', 'draft')
        
        # Load form data
        self.data = ICS214Data.from_json(json.dumps(data))
    
    def validate_detailed(self) -> FormValidationResult:
        """Perform detailed validation with specific error information.
        
        Returns:
            FormValidationResult: Detailed validation result.
        """
        result = FormValidationResult()
        
        # Use existing validation logic from data model
        if self.data.is_valid():
            result.is_valid = True
        else:
            result.is_valid = False
            result.add_error("Form data validation failed")
            
            # Add specific validation errors based on data model validation
            if not self.data.incident_name.strip():
                result.add_error("Incident name is required", "incident_name")
            if not self.data.name.strip():
                result.add_error("Name is required", "name")
            if not self.data.ics_position.strip():
                result.add_error("ICS position is required", "ics_position")
            if not self.data.home_agency.strip():
                result.add_error("Home agency is required", "home_agency")
            if len(self.data.activity_log) == 0:
                result.add_error("At least one activity entry is required", "activity_log")
            if not self.data.prepared_by.name.strip():
                result.add_error("Prepared by name is required", "prepared_by_name")
        
        return result


# Factory functions for creating forms

def create_new_ics214() -> ICS214Form:
    """Factory function for creating new ICS-214 forms.
    
    Creates a new ICS-214 form with default values and current timestamp,
    ready for user input and customization.
    
    Returns:
        ICS214Form: New ICS-214 form instance with default values.
        
    Example:
        >>> form = create_new_ics214()
        >>> form.data.incident_name = "My Incident"
        >>> form.data.name = "John Doe"
    """
    return ICS214Form()


def load_ics214_from_json(json_data: str) -> ICS214Form:
    """Load ICS-214 form from JSON representation.
    
    Args:
        json_data: JSON string containing form data.
        
    Returns:
        ICS214Form: Form instance loaded from JSON data.
        
    Raises:
        ValueError: If JSON data is invalid or malformed.
        
    Example:
        >>> json_str = '{"form_type": "ICS-214", "incident_name": "Test"}'
        >>> form = load_ics214_from_json(json_str)
        >>> print(form.data.incident_name)
    """
    form = ICS214Form()
    form.from_json(json_data)
    return form


def validate_activity_sequence(activities: List[ActivityEntry]) -> bool:
    """Validate chronological order of activity entries.
    
    Args:
        activities: List of activity entries to validate.
        
    Returns:
        bool: True if activities are in chronological order, False otherwise.
        
    Notes:
        This function implements business rule R-ICS214-07 for chronological
        ordering of activities in the activity log.
        
    Example:
        >>> activities = [
        ...     ActivityEntry(datetime(2024, 5, 30, 8, 0), "Start shift"),
        ...     ActivityEntry(datetime(2024, 5, 30, 12, 0), "Lunch break"),
        ...     ActivityEntry(datetime(2024, 5, 30, 16, 0), "End shift")
        ... ]
        >>> is_valid = validate_activity_sequence(activities)
        >>> print(f"Sequence valid: {is_valid}")
    """
    if len(activities) <= 1:
        return True
    
    for i in range(1, len(activities)):
        if activities[i].datetime < activities[i-1].datetime:
            return False
    
    return True
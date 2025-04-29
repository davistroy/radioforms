#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ICS-214 Activity Log form model.

This module implements the data model for the ICS-214 Activity Log form,
which is used to record activity details during incident operations.
"""

import datetime
from typing import Dict, Any, List, Optional, Union

from radioforms.models.base_form import BaseFormModel, ValidationResult


class ActivityLogEntry:
    """
    Represents a single activity log entry in the ICS-214 form.
    """
    
    def __init__(self, time: Optional[datetime.time] = None, 
                 activity: str = "", entry_id: Optional[str] = None):
        """
        Initialize an activity log entry.
        
        Args:
            time: Time of the activity
            activity: Description of the activity
            entry_id: Unique identifier for the entry (generated if not provided)
        """
        import uuid
        self.entry_id = entry_id or str(uuid.uuid4())
        self.time = time or datetime.datetime.now().time()
        self.activity = activity
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the activity log entry to a dictionary.
        
        Returns:
            Dictionary representation of the activity log entry
        """
        return {
            "entry_id": self.entry_id,
            "time": self.time.isoformat() if self.time else None,
            "activity": self.activity
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActivityLogEntry':
        """
        Create an activity log entry from a dictionary.
        
        Args:
            data: Dictionary containing activity log entry data
            
        Returns:
            A new ActivityLogEntry instance
        """
        entry = cls(entry_id=data.get("entry_id"))
        
        time_str = data.get("time")
        if time_str:
            entry.time = datetime.time.fromisoformat(time_str)
            
        entry.activity = data.get("activity", "")
        
        return entry


class ICS214Form(BaseFormModel):
    """
    ICS-214 Activity Log form model.
    
    This form is used to record activity details during incident operations,
    including personnel assignments and significant events.
    """
    
    def __init__(self, form_id: Optional[str] = None):
        """
        Initialize the ICS-214 form.
        
        Args:
            form_id: Unique identifier for the form (generated if not provided)
        """
        super().__init__(form_id)
        
        # Incident information
        self._incident_name = ""
        self._date_prepared = datetime.datetime.now()
        self._time_prepared = self._date_prepared.time()
        
        # Team information
        self._team_name = ""
        self._ics_position = ""
        self._home_agency = ""
        
        # Activity log entries
        self._activity_log: List[ActivityLogEntry] = []
        
        # Prepared by information
        self._prepared_name = ""
        self._prepared_position = ""
        self._prepared_signature = ""
        
        # Register property setters for change tracking
        self._register_properties()
        
    def _register_properties(self):
        """Register all properties for change tracking."""
        # Incident information
        self.register_property("incident_name", self._set_incident_name)
        self.register_property("date_prepared", self._set_date_prepared)
        self.register_property("time_prepared", self._set_time_prepared)
        
        # Team information
        self.register_property("team_name", self._set_team_name)
        self.register_property("ics_position", self._set_ics_position)
        self.register_property("home_agency", self._set_home_agency)
        
        # Prepared by information
        self.register_property("prepared_name", self._set_prepared_name)
        self.register_property("prepared_position", self._set_prepared_position)
        self.register_property("prepared_signature", self._set_prepared_signature)
        
    # Incident information property setters
    
    def _set_incident_name(self, value: str):
        """Set the incident name with change tracking."""
        old_value = self._incident_name
        self._incident_name = value
        self.notify_observers("incident_name", old_value, value)
        
    def _set_date_prepared(self, value: datetime.datetime):
        """Set the preparation date with change tracking."""
        old_value = self._date_prepared
        self._date_prepared = value
        self.notify_observers("date_prepared", old_value, value)
        
    def _set_time_prepared(self, value: datetime.time):
        """Set the preparation time with change tracking."""
        old_value = self._time_prepared
        self._time_prepared = value
        self.notify_observers("time_prepared", old_value, value)
        
    # Team information property setters
    
    def _set_team_name(self, value: str):
        """Set the team name with change tracking."""
        old_value = self._team_name
        self._team_name = value
        self.notify_observers("team_name", old_value, value)
        
    def _set_ics_position(self, value: str):
        """Set the ICS position with change tracking."""
        old_value = self._ics_position
        self._ics_position = value
        self.notify_observers("ics_position", old_value, value)
        
    def _set_home_agency(self, value: str):
        """Set the home agency with change tracking."""
        old_value = self._home_agency
        self._home_agency = value
        self.notify_observers("home_agency", old_value, value)
        
    # Prepared by information property setters
    
    def _set_prepared_name(self, value: str):
        """Set the preparer's name with change tracking."""
        old_value = self._prepared_name
        self._prepared_name = value
        self.notify_observers("prepared_name", old_value, value)
        
    def _set_prepared_position(self, value: str):
        """Set the preparer's position with change tracking."""
        old_value = self._prepared_position
        self._prepared_position = value
        self.notify_observers("prepared_position", old_value, value)
        
    def _set_prepared_signature(self, value: str):
        """Set the preparer's signature with change tracking."""
        old_value = self._prepared_signature
        self._prepared_signature = value
        self.notify_observers("prepared_signature", old_value, value)
        
    # Property getters and setters
    
    @property
    def incident_name(self) -> str:
        """Get the incident name."""
        return self._incident_name
        
    @incident_name.setter
    def incident_name(self, value: str):
        """Set the incident name."""
        self.set_property("incident_name", value)
        
    @property
    def date_prepared(self) -> datetime.datetime:
        """Get the preparation date."""
        return self._date_prepared
        
    @date_prepared.setter
    def date_prepared(self, value: datetime.datetime):
        """Set the preparation date."""
        self.set_property("date_prepared", value)
        
    @property
    def time_prepared(self) -> datetime.time:
        """Get the preparation time."""
        return self._time_prepared
        
    @time_prepared.setter
    def time_prepared(self, value: datetime.time):
        """Set the preparation time."""
        self.set_property("time_prepared", value)
        
    @property
    def team_name(self) -> str:
        """Get the team name."""
        return self._team_name
        
    @team_name.setter
    def team_name(self, value: str):
        """Set the team name."""
        self.set_property("team_name", value)
        
    @property
    def ics_position(self) -> str:
        """Get the ICS position."""
        return self._ics_position
        
    @ics_position.setter
    def ics_position(self, value: str):
        """Set the ICS position."""
        self.set_property("ics_position", value)
        
    @property
    def home_agency(self) -> str:
        """Get the home agency."""
        return self._home_agency
        
    @home_agency.setter
    def home_agency(self, value: str):
        """Set the home agency."""
        self.set_property("home_agency", value)
        
    @property
    def prepared_name(self) -> str:
        """Get the preparer's name."""
        return self._prepared_name
        
    @prepared_name.setter
    def prepared_name(self, value: str):
        """Set the preparer's name."""
        self.set_property("prepared_name", value)
        
    @property
    def prepared_position(self) -> str:
        """Get the preparer's position."""
        return self._prepared_position
        
    @prepared_position.setter
    def prepared_position(self, value: str):
        """Set the preparer's position."""
        self.set_property("prepared_position", value)
        
    @property
    def prepared_signature(self) -> str:
        """Get the preparer's signature."""
        return self._prepared_signature
        
    @prepared_signature.setter
    def prepared_signature(self, value: str):
        """Set the preparer's signature."""
        self.set_property("prepared_signature", value)
        
    @property
    def activity_log(self) -> List[ActivityLogEntry]:
        """Get the activity log entries."""
        return self._activity_log.copy()
        
    # Activity log entry methods
    
    def add_activity(self, time: Optional[Union[datetime.time, datetime.datetime]] = None, 
                    activity: str = "") -> ActivityLogEntry:
        """
        Add a new activity log entry.
        
        Args:
            time: Time of the activity (current time if not provided)
            activity: Description of the activity
            
        Returns:
            The created ActivityLogEntry
        """
        # Convert datetime to time if needed
        if isinstance(time, datetime.datetime):
            time = time.time()
            
        # Use current time if not provided
        if time is None:
            time = datetime.datetime.now().time()
            
        entry = ActivityLogEntry(time, activity)
        self._activity_log.append(entry)
        
        # Notify observers of the change (list of entries)
        self.notify_observers("activity_log", None, self._activity_log)
        
        return entry
        
    def update_activity(self, entry_id: str, time: Optional[datetime.time] = None, 
                       activity: Optional[str] = None) -> bool:
        """
        Update an existing activity log entry.
        
        Args:
            entry_id: ID of the entry to update
            time: New time (if None, keep existing)
            activity: New activity description (if None, keep existing)
            
        Returns:
            True if entry was found and updated, False otherwise
        """
        for entry in self._activity_log:
            if entry.entry_id == entry_id:
                # Store old values for change tracking
                old_entry = ActivityLogEntry(entry.time, entry.activity, entry.entry_id)
                
                # Update fields if provided
                if time is not None:
                    entry.time = time
                    
                if activity is not None:
                    entry.activity = activity
                    
                # Notify observers of the change
                self.notify_observers("activity_log", old_entry, entry)
                return True
                
        return False
        
    def remove_activity(self, entry_id: str) -> bool:
        """
        Remove an activity log entry.
        
        Args:
            entry_id: ID of the entry to remove
            
        Returns:
            True if entry was found and removed, False otherwise
        """
        for i, entry in enumerate(self._activity_log):
            if entry.entry_id == entry_id:
                # Store the entry to be removed
                old_entry = entry
                
                # Remove the entry
                self._activity_log.pop(i)
                
                # Notify observers of the change
                self.notify_observers("activity_log", old_entry, None)
                return True
                
        return False
        
    def clear_activities(self):
        """
        Remove all activity log entries.
        """
        if self._activity_log:
            old_entries = self._activity_log.copy()
            self._activity_log.clear()
            
            # Notify observers of the change
            self.notify_observers("activity_log", old_entries, [])
        
    # Override methods
    
    def get_form_type(self) -> str:
        """
        Get the form type identifier.
        
        Returns:
            String identifier for the form type
        """
        return "ICS-214"
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the form to a dictionary.
        
        Returns:
            Dictionary representation of the form
        """
        # Get the base dictionary with common fields
        data = super().to_dict()
        
        # Add form-specific fields
        data.update({
            # Incident information
            "incident_name": self._incident_name,
            "date_prepared": self._date_prepared.isoformat() if self._date_prepared else None,
            "time_prepared": self._time_prepared.isoformat() if self._time_prepared else None,
            
            # Team information
            "team_name": self._team_name,
            "ics_position": self._ics_position,
            "home_agency": self._home_agency,
            
            # Activity log entries
            "activity_log": [entry.to_dict() for entry in self._activity_log],
            
            # Prepared by information
            "prepared_name": self._prepared_name,
            "prepared_position": self._prepared_position,
            "prepared_signature": self._prepared_signature
        })
        
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ICS214Form':
        """
        Create a form instance from a dictionary.
        
        Args:
            data: Dictionary representation of the form
            
        Returns:
            A new form instance
        """
        # Create the form with base fields
        form = super(ICS214Form, cls).from_dict(data)
        
        # Parse date/time fields
        date_prepared = data.get("date_prepared")
        if date_prepared:
            form._date_prepared = datetime.datetime.fromisoformat(date_prepared)
            
        time_prepared = data.get("time_prepared")
        if time_prepared:
            form._time_prepared = datetime.time.fromisoformat(time_prepared)
            
        # Set string fields
        form._incident_name = data.get("incident_name", "")
        form._team_name = data.get("team_name", "")
        form._ics_position = data.get("ics_position", "")
        form._home_agency = data.get("home_agency", "")
        form._prepared_name = data.get("prepared_name", "")
        form._prepared_position = data.get("prepared_position", "")
        form._prepared_signature = data.get("prepared_signature", "")
        
        # Parse activity log entries
        activity_log_data = data.get("activity_log", [])
        form._activity_log = [ActivityLogEntry.from_dict(entry_data) 
                             for entry_data in activity_log_data]
        
        return form
        
    def validate(self) -> ValidationResult:
        """
        Validate the form data.
        
        Returns:
            ValidationResult with validation status and any errors
        """
        # Start with basic validation from the parent class
        result = super().validate()
        
        # Validate required fields
        if not self._incident_name:
            result.add_error("incident_name", "Incident name is required")
            
        if not self._team_name:
            result.add_error("team_name", "Team name is required")
            
        if not self._prepared_name:
            result.add_error("prepared_name", "Prepared by name is required")
            
        # Validate lengths
        if len(self._incident_name) > 100:
            result.add_error("incident_name", "Incident name cannot exceed 100 characters")
            
        if len(self._team_name) > 100:
            result.add_error("team_name", "Team name cannot exceed 100 characters")
            
        if len(self._ics_position) > 100:
            result.add_error("ics_position", "ICS position cannot exceed 100 characters")
            
        if len(self._home_agency) > 100:
            result.add_error("home_agency", "Home agency cannot exceed 100 characters")
            
        # Check for valid dates
        if self._date_prepared and self._date_prepared > datetime.datetime.now():
            result.add_error("date_prepared", "Date prepared cannot be in the future")
            
        # Validate activity log entries
        for i, entry in enumerate(self._activity_log):
            if not entry.activity:
                result.add_error(f"activity_log.{i}.activity", 
                                f"Activity description is required for entry #{i+1}")
                
            if len(entry.activity) > 500:
                result.add_error(f"activity_log.{i}.activity", 
                                f"Activity description cannot exceed 500 characters for entry #{i+1}")
                                
        return result
        
    @classmethod
    def create_new(cls) -> 'ICS214Form':
        """
        Factory method to create a new ICS-214 form with default values.
        
        Returns:
            A new ICS-214 form instance
        """
        form = cls()
        # Set current date/time for preparation
        now = datetime.datetime.now()
        form._date_prepared = now
        form._time_prepared = now.time()
        
        return form

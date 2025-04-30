#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enhanced ICS-214 Activity Log form model.

This module implements an improved data model for the ICS-214 Activity Log form,
with enhanced validation, DAO integration, support for form state tracking,
and improved activity log entry management.
"""

import datetime
import re
from enum import Enum
from typing import Dict, Any, List, Optional, Set, Union, Tuple

from radioforms.models.base_form import BaseFormModel, ValidationResult
from radioforms.database.dao.form_dao_refactored import FormDAO
from radioforms.database.dao.attachment_dao_refactored import AttachmentDAO


class FormState(Enum):
    """
    Represents the possible states of an ICS-214 form.
    """
    DRAFT = "draft"
    FINALIZED = "finalized"  # Signed off by preparer
    REVIEWED = "reviewed"    # Reviewed by supervisor
    ARCHIVED = "archived"    # Archived in records


class ActivityLogEntry:
    """
    Represents a single activity log entry in the ICS-214 form with enhanced validation.
    """
    
    def __init__(self, time: Optional[datetime.time] = None, 
                 activity: str = "", notable: bool = False,
                 entry_id: Optional[str] = None):
        """
        Initialize an activity log entry.
        
        Args:
            time: Time of the activity
            activity: Description of the activity
            notable: Flag for notable/significant events
            entry_id: Unique identifier for the entry (generated if not provided)
        """
        import uuid
        self.entry_id = entry_id or str(uuid.uuid4())
        self.time = time or datetime.datetime.now().time()
        self.activity = activity
        self.notable = notable
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the activity log entry to a dictionary.
        
        Returns:
            Dictionary representation of the activity log entry
        """
        return {
            "entry_id": self.entry_id,
            "time": self.time.isoformat() if self.time else None,
            "activity": self.activity,
            "notable": self.notable
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
            try:
                entry.time = datetime.time.fromisoformat(time_str)
            except (ValueError, TypeError):
                entry.time = datetime.datetime.now().time()
                
        entry.activity = data.get("activity", "")
        entry.notable = data.get("notable", False)
        
        return entry
        
    def validate(self) -> ValidationResult:
        """
        Validate the activity log entry.
        
        Returns:
            ValidationResult with validation status and any errors
        """
        result = ValidationResult()
        
        # Activity description is required
        if not self.activity:
            result.add_error("activity", "Activity description is required")
            
        # Check length
        if len(self.activity) > 500:
            result.add_error("activity", "Activity description cannot exceed 500 characters")
            
        # Check for valid time
        if self.time and self.time > datetime.datetime.now().time():
            result.add_error("time", "Activity time cannot be in the future")
            
        return result


class EnhancedICS214Form(BaseFormModel):
    """
    Enhanced ICS-214 Activity Log form model.
    
    This form is used to record activity details during incident operations,
    with enhanced validation, state tracking, and DAO integration.
    """
    
    def __init__(self, form_id: Optional[str] = None):
        """
        Initialize the ICS-214 form.
        
        Args:
            form_id: Unique identifier for the form (generated if not provided)
        """
        super().__init__(form_id)
        
        # Form state
        self._state = FormState.DRAFT
        self._form_version = "2.0"  # ICS-214 form version
        
        # Incident information
        self._incident_name = ""
        self._incident_number = ""
        self._date_prepared = datetime.datetime.now()
        self._time_prepared = self._date_prepared.time()
        self._operational_period = ""
        
        # Team information
        self._team_name = ""
        self._ics_position = ""
        self._home_agency = ""
        
        # Activity log entries
        self._activity_log: List[ActivityLogEntry] = []
        
        # Personnel assigned
        self._personnel: List[Dict[str, str]] = []  # Name, ICS position, home agency
        
        # Prepared by information
        self._prepared_name = ""
        self._prepared_position = ""
        self._prepared_date = datetime.datetime.now()
        self._prepared_time = self._prepared_date.time()
        self._prepared_signature = ""
        
        # Review information
        self._reviewer_name = ""
        self._reviewer_position = ""
        self._reviewer_date = None
        self._reviewer_time = None
        self._reviewer_signature = ""
        
        # Attachments
        self._attachments = []
        
        # Register property setters for change tracking
        self._register_properties()
        
    def _register_properties(self):
        """Register all properties for change tracking."""
        # Form state
        self.register_property("state", self._set_state)
        self.register_property("form_version", self._set_form_version)
        
        # Incident information
        self.register_property("incident_name", self._set_incident_name)
        self.register_property("incident_number", self._set_incident_number)
        self.register_property("date_prepared", self._set_date_prepared)
        self.register_property("time_prepared", self._set_time_prepared)
        self.register_property("operational_period", self._set_operational_period)
        
        # Team information
        self.register_property("team_name", self._set_team_name)
        self.register_property("ics_position", self._set_ics_position)
        self.register_property("home_agency", self._set_home_agency)
        
        # Activity log
        self.register_property("activity_log", self._set_activity_log)
        
        # Personnel assigned
        self.register_property("personnel", self._set_personnel)
        
        # Prepared by information
        self.register_property("prepared_name", self._set_prepared_name)
        self.register_property("prepared_position", self._set_prepared_position)
        self.register_property("prepared_date", self._set_prepared_date)
        self.register_property("prepared_time", self._set_prepared_time)
        self.register_property("prepared_signature", self._set_prepared_signature)
        
        # Review information
        self.register_property("reviewer_name", self._set_reviewer_name)
        self.register_property("reviewer_position", self._set_reviewer_position)
        self.register_property("reviewer_date", self._set_reviewer_date)
        self.register_property("reviewer_time", self._set_reviewer_time)
        self.register_property("reviewer_signature", self._set_reviewer_signature)
        
        # Attachments
        self.register_property("attachments", self._set_attachments)
        
    # Form state property setters
    
    def _set_state(self, value: Union[FormState, str]):
        """Set the form state with change tracking."""
        old_value = self._state
        
        # Convert string to enum if needed
        if isinstance(value, str):
            try:
                value = FormState(value.lower())
            except ValueError:
                raise ValueError(f"Invalid form state: {value}")
                
        self._state = value
        self.notify_observers("state", old_value, value)
        
    def _set_form_version(self, value: str):
        """Set the form version with change tracking."""
        old_value = self._form_version
        self._form_version = value
        self.notify_observers("form_version", old_value, value)
        
    # Incident information property setters
    
    def _set_incident_name(self, value: str):
        """Set the incident name with change tracking."""
        old_value = self._incident_name
        self._incident_name = value
        self.notify_observers("incident_name", old_value, value)
        
    def _set_incident_number(self, value: str):
        """Set the incident number with change tracking."""
        old_value = self._incident_number
        self._incident_number = value
        self.notify_observers("incident_number", old_value, value)
        
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
        
    def _set_operational_period(self, value: str):
        """Set the operational period with change tracking."""
        old_value = self._operational_period
        self._operational_period = value
        self.notify_observers("operational_period", old_value, value)
        
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
        
    # Activity log property setter
    
    def _set_activity_log(self, value: List[ActivityLogEntry]):
        """Set the activity log with change tracking."""
        old_value = self._activity_log.copy()
        self._activity_log = value
        self.notify_observers("activity_log", old_value, value)
        
    # Personnel property setter
    
    def _set_personnel(self, value: List[Dict[str, str]]):
        """Set the personnel list with change tracking."""
        old_value = self._personnel.copy()
        self._personnel = value
        self.notify_observers("personnel", old_value, value)
        
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
        
    def _set_prepared_date(self, value: datetime.datetime):
        """Set the preparer's date with change tracking."""
        old_value = self._prepared_date
        self._prepared_date = value
        self.notify_observers("prepared_date", old_value, value)
        
    def _set_prepared_time(self, value: datetime.time):
        """Set the preparer's time with change tracking."""
        old_value = self._prepared_time
        self._prepared_time = value
        self.notify_observers("prepared_time", old_value, value)
        
    def _set_prepared_signature(self, value: str):
        """Set the preparer's signature with change tracking."""
        old_value = self._prepared_signature
        self._prepared_signature = value
        self.notify_observers("prepared_signature", old_value, value)
        
    # Review information property setters
    
    def _set_reviewer_name(self, value: str):
        """Set the reviewer's name with change tracking."""
        old_value = self._reviewer_name
        self._reviewer_name = value
        self.notify_observers("reviewer_name", old_value, value)
        
    def _set_reviewer_position(self, value: str):
        """Set the reviewer's position with change tracking."""
        old_value = self._reviewer_position
        self._reviewer_position = value
        self.notify_observers("reviewer_position", old_value, value)
        
    def _set_reviewer_date(self, value: Optional[datetime.datetime]):
        """Set the reviewer's date with change tracking."""
        old_value = self._reviewer_date
        self._reviewer_date = value
        self.notify_observers("reviewer_date", old_value, value)
        
    def _set_reviewer_time(self, value: Optional[datetime.time]):
        """Set the reviewer's time with change tracking."""
        old_value = self._reviewer_time
        self._reviewer_time = value
        self.notify_observers("reviewer_time", old_value, value)
        
    def _set_reviewer_signature(self, value: str):
        """Set the reviewer's signature with change tracking."""
        old_value = self._reviewer_signature
        self._reviewer_signature = value
        self.notify_observers("reviewer_signature", old_value, value)
        
    # Attachments property setter
    
    def _set_attachments(self, value: List[str]):
        """Set the attachments list with change tracking."""
        old_value = self._attachments.copy()
        self._attachments = value
        self.notify_observers("attachments", old_value, value)
        
    # Property getters
    
    @property
    def state(self) -> FormState:
        """Get the form state."""
        return self._state
        
    @state.setter
    def state(self, value: Union[FormState, str]):
        """Set the form state."""
        self.set_property("state", value)
        
    @property
    def form_version(self) -> str:
        """Get the form version."""
        return self._form_version
        
    @form_version.setter
    def form_version(self, value: str):
        """Set the form version."""
        self.set_property("form_version", value)
        
    @property
    def incident_name(self) -> str:
        """Get the incident name."""
        return self._incident_name
        
    @incident_name.setter
    def incident_name(self, value: str):
        """Set the incident name."""
        self.set_property("incident_name", value)
        
    @property
    def incident_number(self) -> str:
        """Get the incident number."""
        return self._incident_number
        
    @incident_number.setter
    def incident_number(self, value: str):
        """Set the incident number."""
        self.set_property("incident_number", value)
        
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
    def operational_period(self) -> str:
        """Get the operational period."""
        return self._operational_period
        
    @operational_period.setter
    def operational_period(self, value: str):
        """Set the operational period."""
        self.set_property("operational_period", value)
        
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
    def activity_log(self) -> List[ActivityLogEntry]:
        """Get the activity log entries."""
        return self._activity_log.copy()
        
    @property
    def personnel(self) -> List[Dict[str, str]]:
        """Get the personnel list."""
        return self._personnel.copy()
        
    @personnel.setter
    def personnel(self, value: List[Dict[str, str]]):
        """Set the personnel list."""
        self.set_property("personnel", value)
        
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
    def prepared_date(self) -> datetime.datetime:
        """Get the preparer's date."""
        return self._prepared_date
        
    @prepared_date.setter
    def prepared_date(self, value: datetime.datetime):
        """Set the preparer's date."""
        self.set_property("prepared_date", value)
        
    @property
    def prepared_time(self) -> datetime.time:
        """Get the preparer's time."""
        return self._prepared_time
        
    @prepared_time.setter
    def prepared_time(self, value: datetime.time):
        """Set the preparer's time."""
        self.set_property("prepared_time", value)
        
    @property
    def prepared_signature(self) -> str:
        """Get the preparer's signature."""
        return self._prepared_signature
        
    @prepared_signature.setter
    def prepared_signature(self, value: str):
        """Set the preparer's signature."""
        self.set_property("prepared_signature", value)
        
    @property
    def reviewer_name(self) -> str:
        """Get the reviewer's name."""
        return self._reviewer_name
        
    @reviewer_name.setter
    def reviewer_name(self, value: str):
        """Set the reviewer's name."""
        self.set_property("reviewer_name", value)
        
    @property
    def reviewer_position(self) -> str:
        """Get the reviewer's position."""
        return self._reviewer_position
        
    @reviewer_position.setter
    def reviewer_position(self, value: str):
        """Set the reviewer's position."""
        self.set_property("reviewer_position", value)
        
    @property
    def reviewer_date(self) -> Optional[datetime.datetime]:
        """Get the reviewer's date."""
        return self._reviewer_date
        
    @reviewer_date.setter
    def reviewer_date(self, value: Optional[datetime.datetime]):
        """Set the reviewer's date."""
        self.set_property("reviewer_date", value)
        
    @property
    def reviewer_time(self) -> Optional[datetime.time]:
        """Get the reviewer's time."""
        return self._reviewer_time
        
    @reviewer_time.setter
    def reviewer_time(self, value: Optional[datetime.time]):
        """Set the reviewer's time."""
        self.set_property("reviewer_time", value)
        
    @property
    def reviewer_signature(self) -> str:
        """Get the reviewer's signature."""
        return self._reviewer_signature
        
    @reviewer_signature.setter
    def reviewer_signature(self, value: str):
        """Set the reviewer's signature."""
        self.set_property("reviewer_signature", value)
        
    @property
    def attachments(self) -> List[str]:
        """Get the attachments list."""
        return self._attachments.copy()
        
    @attachments.setter
    def attachments(self, value: List[str]):
        """Set the attachments list."""
        self.set_property("attachments", value)
        
    # Activity log entry methods
    
    def add_activity(self, time: Optional[Union[datetime.time, datetime.datetime]] = None, 
                    activity: str = "", notable: bool = False) -> ActivityLogEntry:
        """
        Add a new activity log entry.
        
        Args:
            time: Time of the activity (current time if not provided)
            activity: Description of the activity
            notable: Flag for notable/significant events
            
        Returns:
            The created ActivityLogEntry
        """
        # Convert datetime to time if needed
        if isinstance(time, datetime.datetime):
            time = time.time()
            
        # Use current time if not provided
        if time is None:
            time = datetime.datetime.now().time()
            
        entry = ActivityLogEntry(time, activity, notable)
        
        # Create a new copy of the list with the added entry
        new_activity_log = self._activity_log.copy()
        new_activity_log.append(entry)
        
        # Use the property setter to ensure change tracking
        self.set_property("activity_log", new_activity_log)
        
        return entry
        
    def update_activity(self, entry_id: str, time: Optional[datetime.time] = None, 
                       activity: Optional[str] = None, 
                       notable: Optional[bool] = None) -> bool:
        """
        Update an existing activity log entry.
        
        Args:
            entry_id: ID of the entry to update
            time: New time (if None, keep existing)
            activity: New activity description (if None, keep existing)
            notable: New notable flag (if None, keep existing)
            
        Returns:
            True if entry was found and updated, False otherwise
        """
        # Find the entry to update
        entry_index = None
        for i, entry in enumerate(self._activity_log):
            if entry.entry_id == entry_id:
                entry_index = i
                break
                
        if entry_index is None:
            return False
            
        # Create a copy of the list and the entry to update
        new_activity_log = self._activity_log.copy()
        old_entry = new_activity_log[entry_index]
        new_entry = ActivityLogEntry(
            time=time if time is not None else old_entry.time,
            activity=activity if activity is not None else old_entry.activity,
            notable=notable if notable is not None else old_entry.notable,
            entry_id=old_entry.entry_id
        )
        
        # Replace the old entry with the updated one
        new_activity_log[entry_index] = new_entry
        
        # Use the property setter to ensure change tracking
        self.set_property("activity_log", new_activity_log)
        
        return True
        
    def remove_activity(self, entry_id: str) -> bool:
        """
        Remove an activity log entry.
        
        Args:
            entry_id: ID of the entry to remove
            
        Returns:
            True if entry was found and removed, False otherwise
        """
        # Find the entry to remove
        entry_index = None
        for i, entry in enumerate(self._activity_log):
            if entry.entry_id == entry_id:
                entry_index = i
                break
                
        if entry_index is None:
            return False
            
        # Create a copy of the list without the entry to remove
        new_activity_log = self._activity_log.copy()
        new_activity_log.pop(entry_index)
        
        # Use the property setter to ensure change tracking
        self.set_property("activity_log", new_activity_log)
        
        return True
        
    def clear_activities(self):
        """
        Remove all activity log entries.
        """
        if self._activity_log:
            # Use the property setter to ensure change tracking
            self.set_property("activity_log", [])
    
    def get_notable_activities(self) -> List[ActivityLogEntry]:
        """
        Get all notable activity entries.
        
        Returns:
            List of notable activity entries
        """
        return [entry for entry in self._activity_log if entry.notable]
    
    def get_activities_by_timerange(self, start_time: datetime.time, 
                                   end_time: datetime.time) -> List[ActivityLogEntry]:
        """
        Get activity entries within a specific time range.
        
        Args:
            start_time: Start time of the range
            end_time: End time of the range
            
        Returns:
            List of activity entries within the time range
        """
        return [
            entry for entry in self._activity_log 
            if start_time <= entry.time <= end_time
        ]
    
    # Personnel methods
    
    def add_personnel(self, name: str, position: str, agency: str) -> Dict[str, str]:
        """
        Add a personnel entry.
        
        Args:
            name: Name of the personnel
            position: ICS position
            agency: Home agency
            
        Returns:
            The created personnel entry
        """
        person = {
            "name": name,
            "position": position,
            "agency": agency
        }
        
        # Create a new copy of the list with the added entry
        new_personnel = self._personnel.copy()
        new_personnel.append(person)
        
        # Use the property setter to ensure change tracking
        self.set_property("personnel", new_personnel)
        
        return person
        
    def update_personnel(self, index: int, name: Optional[str] = None, 
                        position: Optional[str] = None, 
                        agency: Optional[str] = None) -> bool:
        """
        Update a personnel entry.
        
        Args:
            index: Index of the personnel entry to update
            name: New name (if None, keep existing)
            position: New position (if None, keep existing)
            agency: New agency (if None, keep existing)
            
        Returns:
            True if entry was found and updated, False otherwise
        """
        if index < 0 or index >= len(self._personnel):
            return False
            
        # Create a copy of the list and the entry to update
        new_personnel = self._personnel.copy()
        old_person = new_personnel[index]
        new_person = {
            "name": name if name is not None else old_person.get("name", ""),
            "position": position if position is not None else old_person.get("position", ""),
            "agency": agency if agency is not None else old_person.get("agency", "")
        }
        
        # Replace the old entry with the updated one
        new_personnel[index] = new_person
        
        # Use the property setter to ensure change tracking
        self.set_property("personnel", new_personnel)
        
        return True
        
    def remove_personnel(self, index: int) -> bool:
        """
        Remove a personnel entry.
        
        Args:
            index: Index of the personnel entry to remove
            
        Returns:
            True if entry was found and removed, False otherwise
        """
        if index < 0 or index >= len(self._personnel):
            return False
            
        # Create a copy of the list without the entry to remove
        new_personnel = self._personnel.copy()
        new_personnel.pop(index)
        
        # Use the property setter to ensure change tracking
        self.set_property("personnel", new_personnel)
        
        return True
        
    def clear_personnel(self):
        """
        Remove all personnel entries.
        """
        if self._personnel:
            # Use the property setter to ensure change tracking
            self.set_property("personnel", [])
    
    # Attachment management methods
    
    def add_attachment(self, attachment_id: str) -> bool:
        """
        Add an attachment to the form.
        
        Args:
            attachment_id: ID of the attachment to add
            
        Returns:
            True if the attachment was added, False if it was already present
        """
        if attachment_id in self._attachments:
            return False
            
        new_attachments = self._attachments.copy()
        new_attachments.append(attachment_id)
        self.attachments = new_attachments
        return True
        
    def remove_attachment(self, attachment_id: str) -> bool:
        """
        Remove an attachment from the form.
        
        Args:
            attachment_id: ID of the attachment to remove
            
        Returns:
            True if the attachment was removed, False if it wasn't found
        """
        if attachment_id not in self._attachments:
            return False
            
        new_attachments = self._attachments.copy()
        new_attachments.remove(attachment_id)
        self.attachments = new_attachments
        return True
        
    # Form state transition methods
    
    def finalize(self, prepared_name: str, prepared_position: str, 
                prepared_signature: str) -> bool:
        """
        Finalize the form.
        
        Args:
            prepared_name: Name of the preparer
            prepared_position: Position of the preparer
            prepared_signature: Signature of the preparer
            
        Returns:
            True if the state was changed, False if not
        """
        if self._state != FormState.DRAFT:
            return False
            
        # Ensure required fields are set
        if not self._incident_name or not self._team_name:
            return False
            
        # Set preparer information
        self.prepared_name = prepared_name
        self.prepared_position = prepared_position
        self.prepared_signature = prepared_signature
        self.prepared_date = datetime.datetime.now()
        self.prepared_time = self.prepared_date.time()
        
        # Update state
        self.state = FormState.FINALIZED
        return True
        
    def review(self, reviewer_name: str, reviewer_position: str, 
              reviewer_signature: str) -> bool:
        """
        Mark the form as reviewed.
        
        Args:
            reviewer_name: Name of the reviewer
            reviewer_position: Position of the reviewer
            reviewer_signature: Signature of the reviewer
            
        Returns:
            True if the state was changed, False if not
        """
        if self._state != FormState.FINALIZED:
            return False
            
        # Set reviewer information
        self.reviewer_name = reviewer_name
        self.reviewer_position = reviewer_position
        self.reviewer_signature = reviewer_signature
        self.reviewer_date = datetime.datetime.now()
        self.reviewer_time = self.reviewer_date.time()
        
        # Update state
        self.state = FormState.REVIEWED
        return True
        
    def archive(self) -> bool:
        """
        Archive the form.
        
        Returns:
            True if the state was changed, False if not
        """
        if self._state in [FormState.ARCHIVED]:
            return False
            
        self.state = FormState.ARCHIVED
        return True
    
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
            # Form state
            "state": self._state.value if self._state else None,
            "form_version": self._form_version,
            
            # Incident information
            "incident_name": self._incident_name,
            "incident_number": self._incident_number,
            "date_prepared": self._date_prepared.isoformat() if self._date_prepared else None,
            "time_prepared": self._time_prepared.isoformat() if self._time_prepared else None,
            "operational_period": self._operational_period,
            
            # Team information
            "team_name": self._team_name,
            "ics_position": self._ics_position,
            "home_agency": self._home_agency,
            
            # Activity log entries
            "activity_log": [entry.to_dict() for entry in self._activity_log],
            
            # Personnel assigned
            "personnel": self._personnel,
            
            # Prepared by information
            "prepared_name": self._prepared_name,
            "prepared_position": self._prepared_position,
            "prepared_date": self._prepared_date.isoformat() if self._prepared_date else None,
            "prepared_time": self._prepared_time.isoformat() if self._prepared_time else None,
            "prepared_signature": self._prepared_signature,
            
            # Review information
            "reviewer_name": self._reviewer_name,
            "reviewer_position": self._reviewer_position,
            "reviewer_date": self._reviewer_date.isoformat() if self._reviewer_date else None,
            "reviewer_time": self._reviewer_time.isoformat() if self._reviewer_time else None,
            "reviewer_signature": self._reviewer_signature,
            
            # Attachments
            "attachments": self._attachments
        })
        
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnhancedICS214Form':
        """
        Create a form instance from a dictionary.
        
        Args:
            data: Dictionary representation of the form
            
        Returns:
            A new form instance
        """
        # Create the form with base fields
        form = super(EnhancedICS214Form, cls).from_dict(data)
        
        # Set form state
        if "state" in data:
            try:
                form._state = FormState(data["state"]) if data["state"] else FormState.DRAFT
            except (ValueError, TypeError):
                form._state = FormState.DRAFT
                
        form._form_version = data.get("form_version", "2.0")
        
        # Set incident information
        form._incident_name = data.get("incident_name", "")
        form._incident_number = data.get("incident_number", "")
        form._operational_period = data.get("operational_period", "")
        
        # Parse date/time fields
        date_prepared = data.get("date_prepared")
        if date_prepared:
            try:
                form._date_prepared = datetime.datetime.fromisoformat(date_prepared)
            except (ValueError, TypeError):
                form._date_prepared = datetime.datetime.now()
                
        time_prepared = data.get("time_prepared")
        if time_prepared:
            try:
                form._time_prepared = datetime.time.fromisoformat(time_prepared)
            except (ValueError, TypeError):
                form._time_prepared = datetime.datetime.now().time()
                
        prepared_date = data.get("prepared_date")
        if prepared_date:
            try:
                form._prepared_date = datetime.datetime.fromisoformat(prepared_date)
            except (ValueError, TypeError):
                form._prepared_date = datetime.datetime.now()
                
        prepared_time = data.get("prepared_time")
        if prepared_time:
            try:
                form._prepared_time = datetime.time.fromisoformat(prepared_time)
            except (ValueError, TypeError):
                form._prepared_time = datetime.datetime.now().time()
                
        reviewer_date = data.get("reviewer_date")
        if reviewer_date:
            try:
                form._reviewer_date = datetime.datetime.fromisoformat(reviewer_date)
            except (ValueError, TypeError):
                form._reviewer_date = None
                
        reviewer_time = data.get("reviewer_time")
        if reviewer_time:
            try:
                form._reviewer_time = datetime.time.fromisoformat(reviewer_time)
            except (ValueError, TypeError):
                form._reviewer_time = None
                
        # Set team information
        form._team_name = data.get("team_name", "")
        form._ics_position = data.get("ics_position", "")
        form._home_agency = data.get("home_agency", "")
        
        # Set activity log entries
        if "activity_log" in data and isinstance(data["activity_log"], list):
            form._activity_log = [
                ActivityLogEntry.from_dict(entry_data) 
                for entry_data in data["activity_log"]
            ]
            
        # Set personnel assigned
        if "personnel" in data and isinstance(data["personnel"], list):
            form._personnel = data.get("personnel", [])
            
        # Set prepared by information
        form._prepared_name = data.get("prepared_name", "")
        form._prepared_position = data.get("prepared_position", "")
        form._prepared_signature = data.get("prepared_signature", "")
        
        # Set review information
        form._reviewer_name = data.get("reviewer_name", "")
        form._reviewer_position = data.get("reviewer_position", "")
        form._reviewer_signature = data.get("reviewer_signature", "")
        
        # Set attachments
        form._attachments = data.get("attachments", [])
        
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
            result.add_error("team_name", "Team/Unit name is required")
            
        # Validate field formats using regex
        name_pattern = re.compile(r'^[A-Za-z\s\-\.]+$')
        
        if self._prepared_name and not name_pattern.match(self._prepared_name):
            result.add_error("prepared_name", "Preparer name can only contain letters, spaces, and hyphens")
            
        if self._reviewer_name and not name_pattern.match(self._reviewer_name):
            result.add_error("reviewer_name", "Reviewer name can only contain letters, spaces, and hyphens")
            
        # Validate field lengths
        max_lengths = {
            "incident_name": 100,
            "incident_number": 50,
            "operational_period": 100,
            "team_name": 100,
            "ics_position": 100,
            "home_agency": 100,
            "prepared_name": 100,
            "prepared_position": 100,
            "prepared_signature": 100,
            "reviewer_name": 100,
            "reviewer_position": 100,
            "reviewer_signature": 100
        }
        
        for field, max_length in max_lengths.items():
            value = getattr(self, f"_{field}")
            if value and len(str(value)) > max_length:
                result.add_error(field, f"{field.replace('_', ' ').title()} cannot exceed {max_length} characters")
        
        # Check for valid dates
        now = datetime.datetime.now()
        
        if self._date_prepared and self._date_prepared > now:
            result.add_error("date_prepared", "Preparation date cannot be in the future")
            
        if self._prepared_date and self._prepared_date > now:
            result.add_error("prepared_date", "Prepared date cannot be in the future")
            
        # Only validate reviewer date if it's provided (it's optional)
        if self._reviewer_date and self._reviewer_date > now:
            result.add_error("reviewer_date", "Reviewer date cannot be in the future")
            
        # Only validate if reviewed after prepared
        if self._reviewer_date and self._prepared_date and self._reviewer_date < self._prepared_date:
            result.add_error("reviewer_date", "Review date cannot be earlier than the preparation date")
            
        # Validate activity log entries
        for i, entry in enumerate(self._activity_log):
            entry_result = entry.validate()
            if not entry_result.is_valid:
                for field, error in entry_result.errors.items():
                    result.add_error(f"activity_log[{i}].{field}", error)
                    
        # Validate personnel entries
        for i, person in enumerate(self._personnel):
            if not person.get("name"):
                result.add_error(f"personnel[{i}].name", "Personnel name is required")
                
            if len(person.get("name", "")) > 100:
                result.add_error(f"personnel[{i}].name", "Personnel name cannot exceed 100 characters")
                
        # State-specific validation
        if self._state == FormState.FINALIZED and not self._prepared_signature:
            result.add_error("prepared_signature", "Finalized forms must have a preparer signature")
            
        if self._state == FormState.REVIEWED and not self._reviewer_signature:
            result.add_error("reviewer_signature", "Reviewed forms must have a reviewer signature")
            
        return result
    
    @classmethod
    def create_new(cls) -> 'EnhancedICS214Form':
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
        form._prepared_date = now
        form._prepared_time = now.time()
        form._state = FormState.DRAFT
        
        return form
    
    @classmethod
    def create_with_dao(cls, form_dao: FormDAO) -> 'EnhancedICS214Form':
        """
        Factory method to create a new form with DAO integration.
        
        Args:
            form_dao: FormDAO instance for persistence
            
        Returns:
            A new ICS-214 form instance with DAO integration
        """
        form = cls.create_new()
        
        # Save to database immediately to get an ID
        form_dict = form.to_dict()
        form_id = form_dao.create(form_dict)
        form.form_id = str(form_id)
        
        return form
    
    def save_to_dao(self, form_dao: FormDAO, create_version: bool = True) -> str:
        """
        Save the form to the database using the provided DAO.
        
        Args:
            form_dao: FormDAO instance for persistence
            create_version: Whether to create a new version
            
        Returns:
            The saved form ID
        """
        # Update last_modified timestamp
        self.last_modified = datetime.datetime.now()
        
        # Convert to dictionary
        form_dict = self.to_dict()
        
        # Determine if this is a new form or an update
        if self.form_id and form_dao.find_by_id(self.form_id):
            # Update existing form
            form_dao.update(form_dict)
            form_id = self.form_id
            
            # Create version if requested and available
            if create_version and hasattr(form_dao, 'create_version'):
                try:
                    form_dao.create_version(form_id, form_dict)
                except AttributeError:
                    pass  # Version creation not supported
        else:
            # Create new form
            form_id = form_dao.create(form_dict)
            self.form_id = str(form_id)
            
        return self.form_id
    
    @classmethod
    def load_from_dao(cls, form_dao: FormDAO, form_id: str, version_id: Optional[str] = None) -> Optional['EnhancedICS214Form']:
        """
        Load a form from the database using the provided DAO.
        
        Args:
            form_dao: FormDAO instance for persistence
            form_id: ID of the form to load
            version_id: Optional version ID to load
            
        Returns:
            The loaded form instance, or None if not found
        """
        # Load form data from DAO
        if version_id and hasattr(form_dao, 'find_version_by_id'):
            try:
                form_dict = form_dao.find_version_by_id(version_id)
            except AttributeError:
                form_dict = None
        else:
            form_dict = form_dao.find_by_id(form_id)
            
        # Return None if form not found
        if not form_dict:
            return None
            
        # Create form instance from dictionary
        return cls.from_dict(form_dict)
        
    def bulk_add_activities(self, activities: List[Dict[str, Any]]) -> List[ActivityLogEntry]:
        """
        Add multiple activity log entries at once.
        
        Args:
            activities: List of dictionaries with 'time', 'activity', and optional 'notable' fields
            
        Returns:
            List of created ActivityLogEntry objects
        """
        if not activities:
            return []
            
        # Create new entries
        new_entries = []
        for activity_data in activities:
            time_val = activity_data.get('time')
            activity_text = activity_data.get('activity', '')
            notable = activity_data.get('notable', False)
            
            entry = ActivityLogEntry(time_val, activity_text, notable)
            new_entries.append(entry)
            
        # Create a new copy of the activity log with added entries
        new_activity_log = self._activity_log.copy() + new_entries
        
        # Use the property setter to ensure change tracking
        self.set_property("activity_log", new_activity_log)
        
        return new_entries
        
    def bulk_add_personnel(self, personnel: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Add multiple personnel entries at once.
        
        Args:
            personnel: List of dictionaries with 'name', 'position', and 'agency' fields
            
        Returns:
            List of created personnel dictionaries
        """
        if not personnel:
            return []
            
        # Create a new copy of the personnel list with added entries
        new_personnel = self._personnel.copy() + personnel
        
        # Use the property setter to ensure change tracking
        self.set_property("personnel", new_personnel)
        
        return personnel

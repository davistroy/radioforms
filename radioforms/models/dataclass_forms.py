from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union
import uuid
import json

class FormState(Enum):
    """Represents the possible states of a form"""
    DRAFT = "draft"
    APPROVED = "approved"
    TRANSMITTED = "transmitted"
    RECEIVED = "received"
    REPLIED = "replied"
    RETURNED = "returned"
    ARCHIVED = "archived"

@dataclass
class BaseForm:
    """Base class for all form models"""
    form_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    form_type: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    state: FormState = field(default=FormState.DRAFT)
    title: str = ""
    incident_id: Optional[str] = None
    creator_id: Optional[str] = None
    
    def validate(self) -> Dict[str, str]:
        """Validate form data and return dictionary of errors"""
        errors = {}
        
        if not self.title:
            errors["title"] = "Title is required"
            
        return errors
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        
        # Handle special types
        data["state"] = self.state.value
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseForm':
        """Create from dictionary"""
        # Make a copy to avoid modifying the original
        data_copy = data.copy()
        
        # Handle special types
        if "state" in data_copy:
            try:
                data_copy["state"] = FormState(data_copy["state"])
            except ValueError:
                data_copy["state"] = FormState.DRAFT
                
        if "created_at" in data_copy and isinstance(data_copy["created_at"], str):
            try:
                data_copy["created_at"] = datetime.fromisoformat(data_copy["created_at"])
            except ValueError:
                data_copy["created_at"] = datetime.now()
                
        if "updated_at" in data_copy and isinstance(data_copy["updated_at"], str):
            try:
                data_copy["updated_at"] = datetime.fromisoformat(data_copy["updated_at"])
            except ValueError:
                data_copy["updated_at"] = datetime.now()
                
        return cls(**data_copy)


@dataclass
class ICS213Form(BaseForm):
    """ICS-213 General Message form model"""
    form_type: str = "ICS-213"
    
    # Message information
    to: str = ""
    to_position: str = ""
    from_field: str = ""
    from_position: str = ""
    subject: str = ""
    message: str = ""
    message_date: datetime = field(default_factory=datetime.now)
    
    # Sender information
    sender_name: str = ""
    sender_position: str = ""
    sender_signature: str = ""
    sender_date: Optional[datetime] = None
    
    # Recipient information
    recipient_name: str = ""
    recipient_position: str = ""
    recipient_signature: str = ""
    recipient_date: Optional[datetime] = None
    reply: str = ""
    
    # Reference information
    incident_name: str = ""
    priority: str = "Routine"  # Routine, Priority, or Immediate
    
    def __post_init__(self):
        """Initialize after dataclass init"""
        if not self.title and self.subject:
            self.title = self.subject
            
        if not self.sender_date:
            self.sender_date = self.created_at
    
    def validate(self) -> Dict[str, str]:
        """Validate form data and return dictionary of errors"""
        errors = super().validate()
        
        # Required fields
        if not self.to:
            errors["to"] = "To field is required"
            
        if not self.from_field:
            errors["from_field"] = "From field is required"
            
        if not self.subject:
            errors["subject"] = "Subject is required"
            
        if not self.message:
            errors["message"] = "Message content is required"
            
        # Field length validations
        max_lengths = {
            "to": 100,
            "to_position": 100,
            "from_field": 100,
            "from_position": 100,
            "subject": 150,
            "message": 2000,
            "sender_name": 100,
            "sender_position": 100,
            "recipient_name": 100,
            "recipient_position": 100,
            "reply": 1000,
            "incident_name": 100
        }
        
        for field, max_length in max_lengths.items():
            value = getattr(self, field)
            if value and len(str(value)) > max_length:
                errors[field] = f"{field.replace('_', ' ').title()} cannot exceed {max_length} characters"
        
        # State-specific validations
        if self.state == FormState.APPROVED and not self.sender_signature:
            errors["sender_signature"] = "Approved messages must have a sender signature"
            
        if self.state == FormState.REPLIED and not self.reply:
            errors["reply"] = "Replied messages must include reply content"
            
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = super().to_dict()
        
        # Handle date fields
        if self.message_date:
            data["message_date"] = self.message_date.isoformat()
            
        if self.sender_date:
            data["sender_date"] = self.sender_date.isoformat()
            
        if self.recipient_date:
            data["recipient_date"] = self.recipient_date.isoformat()
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ICS213Form':
        """Create from dictionary"""
        # Make a copy to avoid modifying the original
        data_copy = data.copy()
        
        # Handle date fields
        for date_field in ["message_date", "sender_date", "recipient_date"]:
            if date_field in data_copy and isinstance(data_copy[date_field], str):
                try:
                    data_copy[date_field] = datetime.fromisoformat(data_copy[date_field])
                except ValueError:
                    if date_field == "message_date":
                        data_copy[date_field] = datetime.now()
                    else:
                        data_copy[date_field] = None
                        
        return super().from_dict.__func__(cls, data_copy)
    
    # State transition methods
    def approve(self, approver_name: str, approver_position: str, approver_signature: str) -> bool:
        """
        Approve the form.
        
        Args:
            approver_name: Name of the approver
            approver_position: Position of the approver
            approver_signature: Signature of the approver
            
        Returns:
            True if the state was changed, False if not
        """
        if self.state != FormState.DRAFT:
            return False
            
        # Set approver information
        self.sender_name = approver_name
        self.sender_position = approver_position
        self.sender_signature = approver_signature
        self.sender_date = datetime.now()
        
        # Update state
        self.state = FormState.APPROVED
        self.updated_at = datetime.now()
        return True
        
    def transmit(self) -> bool:
        """
        Mark the form as transmitted.
        
        Returns:
            True if the state was changed, False if not
        """
        if self.state not in [FormState.DRAFT, FormState.APPROVED]:
            return False
            
        self.state = FormState.TRANSMITTED
        self.updated_at = datetime.now()
        return True
        
    def receive(self, recipient_name: str, recipient_position: str) -> bool:
        """
        Mark the form as received.
        
        Args:
            recipient_name: Name of the recipient
            recipient_position: Position of the recipient
            
        Returns:
            True if the state was changed, False if not
        """
        if self.state != FormState.TRANSMITTED:
            return False
            
        self.recipient_name = recipient_name
        self.recipient_position = recipient_position
        self.recipient_date = datetime.now()
        
        self.state = FormState.RECEIVED
        self.updated_at = datetime.now()
        return True
        
    def reply(self, reply_text: str, recipient_signature: str) -> bool:
        """
        Add a reply to the message.
        
        Args:
            reply_text: Reply content
            recipient_signature: Signature of the recipient
            
        Returns:
            True if the state was changed, False if not
        """
        if self.state != FormState.RECEIVED:
            return False
            
        self.reply = reply_text
        self.recipient_signature = recipient_signature
        
        self.state = FormState.REPLIED
        self.updated_at = datetime.now()
        return True


@dataclass
class ActivityLogEntry:
    """Activity log entry for ICS-214 form"""
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    time: datetime = field(default_factory=datetime.now)
    activity: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "entry_id": self.entry_id,
            "time": self.time.isoformat() if self.time else None,
            "activity": self.activity
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActivityLogEntry':
        """Create from dictionary"""
        entry_id = data.get("entry_id", str(uuid.uuid4()))
        
        # Parse time
        time = None
        if "time" in data and data["time"]:
            try:
                time = datetime.fromisoformat(data["time"])
            except ValueError:
                time = datetime.now()
        else:
            time = datetime.now()
            
        activity = data.get("activity", "")
        
        return cls(entry_id=entry_id, time=time, activity=activity)


@dataclass
class Personnel:
    """Personnel entry for ICS-214 form"""
    person_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    position: str = ""
    home_agency: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "person_id": self.person_id,
            "name": self.name,
            "position": self.position,
            "home_agency": self.home_agency
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Personnel':
        """Create from dictionary"""
        person_id = data.get("person_id", str(uuid.uuid4()))
        name = data.get("name", "")
        position = data.get("position", "")
        home_agency = data.get("home_agency", "")
        
        return cls(
            person_id=person_id,
            name=name,
            position=position,
            home_agency=home_agency
        )


@dataclass
class ICS214Form(BaseForm):
    """ICS-214 Activity Log form model"""
    form_type: str = "ICS-214"
    
    # Operational information
    operational_period_from: Optional[datetime] = None
    operational_period_to: Optional[datetime] = None
    incident_name: str = ""
    incident_number: str = ""
    
    # Unit information
    unit_name: str = ""
    unit_leader_name: str = ""
    unit_leader_position: str = ""
    
    # Activity log
    activities: List[ActivityLogEntry] = field(default_factory=list)
    
    # Personnel
    personnel: List[Personnel] = field(default_factory=list)
    
    # Prepared by
    prepared_by_name: str = ""
    prepared_by_position: str = ""
    prepared_by_signature: str = ""
    prepared_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize after dataclass init"""
        if not self.title and self.unit_name:
            self.title = f"{self.unit_name} - Activity Log"
            
        if not self.prepared_date:
            self.prepared_date = self.created_at
            
    def validate(self) -> Dict[str, str]:
        """Validate form data and return dictionary of errors"""
        errors = super().validate()
        
        # Required fields
        if not self.unit_name:
            errors["unit_name"] = "Unit name is required"
            
        if not self.unit_leader_name:
            errors["unit_leader_name"] = "Unit leader name is required"
            
        # Operational period validation
        if self.operational_period_from and self.operational_period_to:
            if self.operational_period_from > self.operational_period_to:
                errors["operational_period"] = "Operational period end must be after start"
                
        # Field length validations
        max_lengths = {
            "incident_name": 100,
            "incident_number": 50,
            "unit_name": 100,
            "unit_leader_name": 100,
            "unit_leader_position": 100,
            "prepared_by_name": 100,
            "prepared_by_position": 100
        }
        
        for field, max_length in max_lengths.items():
            value = getattr(self, field)
            if value and len(str(value)) > max_length:
                errors[field] = f"{field.replace('_', ' ').title()} cannot exceed {max_length} characters"
        
        # Validate activity entries
        if len(self.activities) == 0:
            errors["activities"] = "At least one activity entry is required"
        else:
            for i, activity in enumerate(self.activities):
                if not activity.activity.strip():
                    errors[f"activity_{i}"] = f"Activity entry {i+1} cannot be empty"
        
        # State-specific validations
        if self.state != FormState.DRAFT and not self.prepared_by_signature:
            errors["prepared_by_signature"] = "Form must be signed when not in draft state"
            
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = super().to_dict()
        
        # Handle date fields
        if self.operational_period_from:
            data["operational_period_from"] = self.operational_period_from.isoformat()
            
        if self.operational_period_to:
            data["operational_period_to"] = self.operational_period_to.isoformat()
            
        if self.prepared_date:
            data["prepared_date"] = self.prepared_date.isoformat()
            
        # Handle complex fields
        data["activities"] = [activity.to_dict() for activity in self.activities]
        data["personnel"] = [person.to_dict() for person in self.personnel]
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ICS214Form':
        """Create from dictionary"""
        # Make a copy to avoid modifying the original
        data_copy = data.copy()
        
        # Handle date fields
        for date_field in ["operational_period_from", "operational_period_to", "prepared_date"]:
            if date_field in data_copy and isinstance(data_copy[date_field], str):
                try:
                    data_copy[date_field] = datetime.fromisoformat(data_copy[date_field])
                except ValueError:
                    data_copy[date_field] = None
        
        # Handle activities
        activities = []
        if "activities" in data_copy and isinstance(data_copy["activities"], list):
            for activity_data in data_copy["activities"]:
                activities.append(ActivityLogEntry.from_dict(activity_data))
        data_copy["activities"] = activities
        
        # Handle personnel
        personnel = []
        if "personnel" in data_copy and isinstance(data_copy["personnel"], list):
            for person_data in data_copy["personnel"]:
                personnel.append(Personnel.from_dict(person_data))
        data_copy["personnel"] = personnel
                        
        return super().from_dict.__func__(cls, data_copy)
    
    # Helper methods
    def add_activity(self, time: datetime, activity: str) -> ActivityLogEntry:
        """Add an activity to the log"""
        entry = ActivityLogEntry(time=time, activity=activity)
        self.activities.append(entry)
        self.updated_at = datetime.now()
        return entry
        
    def remove_activity(self, entry_id: str) -> bool:
        """Remove an activity from the log"""
        for i, entry in enumerate(self.activities):
            if entry.entry_id == entry_id:
                del self.activities[i]
                self.updated_at = datetime.now()
                return True
        return False
        
    def add_personnel(self, name: str, position: str, home_agency: str) -> Personnel:
        """Add personnel to the form"""
        person = Personnel(name=name, position=position, home_agency=home_agency)
        self.personnel.append(person)
        self.updated_at = datetime.now()
        return person
        
    def remove_personnel(self, person_id: str) -> bool:
        """Remove personnel from the form"""
        for i, person in enumerate(self.personnel):
            if person.person_id == person_id:
                del self.personnel[i]
                self.updated_at = datetime.now()
                return True
        return False
    
    # State transition methods
    def finalize(self, preparer_name: str, preparer_position: str, preparer_signature: str) -> bool:
        """
        Finalize the form.
        
        Args:
            preparer_name: Name of the preparer
            preparer_position: Position of the preparer
            preparer_signature: Signature of the preparer
            
        Returns:
            True if the state was changed, False if not
        """
        if self.state != FormState.DRAFT:
            return False
            
        # Set preparer information
        self.prepared_by_name = preparer_name
        self.prepared_by_position = preparer_position
        self.prepared_by_signature = preparer_signature
        self.prepared_date = datetime.now()
        
        # Update state
        self.state = FormState.APPROVED
        self.updated_at = datetime.now()
        return True

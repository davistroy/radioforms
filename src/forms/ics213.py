"""ICS-213 General Message form data model.

This module implements the data model, validation, and business logic
for the ICS-213 General Message form following CLAUDE.md principles.
"""

import json
import logging
from datetime import datetime, date, time
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from enum import Enum


logger = logging.getLogger(__name__)


class Priority(Enum):
    """Message priority levels."""
    ROUTINE = "routine"
    URGENT = "urgent"
    IMMEDIATE = "immediate"


class FormStatus(Enum):
    """Form lifecycle status."""
    DRAFT = "draft"
    APPROVED = "approved"
    TRANSMITTED = "transmitted"
    RECEIVED = "received"
    REPLIED = "replied"
    DOCUMENTED = "documented"


@dataclass
class Person:
    """Represents a person with name and position.
    
    Used for To, From, Approved by, and Replied by fields.
    """
    name: str = ""
    position: str = ""
    signature: str = ""
    contact_info: str = ""
    
    def __post_init__(self):
        """Validate person data after initialization."""
        self.name = self.name.strip()
        self.position = self.position.strip()
        self.signature = self.signature.strip()
        self.contact_info = self.contact_info.strip()
    
    @property
    def is_complete(self) -> bool:
        """Check if person has required minimum information."""
        return bool(self.name and self.position)
    
    @property
    def display_name(self) -> str:
        """Get formatted display name."""
        if self.name and self.position:
            return f"{self.name}, {self.position}"
        elif self.name:
            return self.name
        elif self.position:
            return self.position
        return "Unknown"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Person':
        """Create Person from dictionary."""
        return cls(
            name=data.get('name', ''),
            position=data.get('position', ''),
            signature=data.get('signature', ''),
            contact_info=data.get('contact_info', '')
        )


@dataclass
class ICS213Data:
    """Core data structure for ICS-213 General Message form.
    
    This class follows the simplified approach in CLAUDE.md:
    - Start with essential fields only
    - Add validation incrementally
    - Keep it simple for MVP
    """
    
    # Header fields
    incident_name: str = ""
    to: Person = field(default_factory=Person)
    from_person: Person = field(default_factory=Person)  # 'from' is Python keyword
    subject: str = ""
    date: str = ""  # Start with string, can enhance to date object later
    time: str = ""  # Start with string, can enhance to time object later
    
    # Message fields
    message: str = ""
    approved_by: Person = field(default_factory=Person)
    
    # Reply fields
    reply: str = ""
    replied_by: Person = field(default_factory=Person)
    reply_date_time: str = ""
    
    # Metadata
    priority: Priority = Priority.ROUTINE
    form_version: str = "1.0"
    reply_requested: bool = False
    
    def __post_init__(self):
        """Clean up data after initialization."""
        self.incident_name = self.incident_name.strip()
        self.subject = self.subject.strip()
        self.message = self.message.strip()
        self.reply = self.reply.strip()
        self.date = self.date.strip()
        self.time = self.time.strip()
        self.reply_date_time = self.reply_date_time.strip()
        
        # Ensure Person objects
        if not isinstance(self.to, Person):
            self.to = Person()
        if not isinstance(self.from_person, Person):
            self.from_person = Person()
        if not isinstance(self.approved_by, Person):
            self.approved_by = Person()
        if not isinstance(self.replied_by, Person):
            self.replied_by = Person()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert enum to string
        data['priority'] = self.priority.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ICS213Data':
        """Create ICS213Data from dictionary."""
        # Handle priority enum
        priority_value = data.get('priority', Priority.ROUTINE.value)
        if isinstance(priority_value, str):
            try:
                priority = Priority(priority_value)
            except ValueError:
                priority = Priority.ROUTINE
        else:
            priority = priority_value
        
        # Handle Person objects
        to_data = data.get('to', {})
        from_data = data.get('from_person', {})
        approved_data = data.get('approved_by', {})
        replied_data = data.get('replied_by', {})
        
        return cls(
            incident_name=data.get('incident_name', ''),
            to=Person.from_dict(to_data) if isinstance(to_data, dict) else Person(),
            from_person=Person.from_dict(from_data) if isinstance(from_data, dict) else Person(),
            subject=data.get('subject', ''),
            date=data.get('date', ''),
            time=data.get('time', ''),
            message=data.get('message', ''),
            approved_by=Person.from_dict(approved_data) if isinstance(approved_data, dict) else Person(),
            reply=data.get('reply', ''),
            replied_by=Person.from_dict(replied_data) if isinstance(replied_data, dict) else Person(),
            reply_date_time=data.get('reply_date_time', ''),
            priority=priority,
            form_version=data.get('form_version', '1.0'),
            reply_requested=data.get('reply_requested', False)
        )


class ValidationError(Exception):
    """Raised when form validation fails."""
    pass


class ICS213Form:
    """ICS-213 General Message form with validation and business logic.
    
    This class provides:
    - Form data management
    - Validation according to ICS-213 rules
    - Status tracking
    - JSON serialization
    """
    
    def __init__(self, data: Optional[ICS213Data] = None):
        """Initialize form with optional data."""
        self.data = data or ICS213Data()
        self.status = FormStatus.DRAFT
        self.validation_errors: List[str] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        logger.debug("ICS213Form initialized")
    
    def validate(self) -> bool:
        """Validate form data according to ICS-213 requirements.
        
        Returns:
            True if form is valid, False otherwise
            
        Validation errors are stored in self.validation_errors
        """
        self.validation_errors = []
        
        # R-ICS213-01: To (recipient) must be provided with minimum name and position
        if not self.data.to.is_complete:
            self.validation_errors.append("Recipient (To) must have both name and position")
        
        # R-ICS213-02: From (sender) must be provided with minimum name and position  
        if not self.data.from_person.is_complete:
            self.validation_errors.append("Sender (From) must have both name and position")
        
        # R-ICS213-03: Subject must be provided
        if not self.data.subject:
            self.validation_errors.append("Subject is required")
        
        # R-ICS213-04: Date and Time must be provided and valid
        if not self.data.date:
            self.validation_errors.append("Date is required")
        
        if not self.data.time:
            self.validation_errors.append("Time is required")
        
        # R-ICS213-05: Message content must be provided
        if not self.data.message:
            self.validation_errors.append("Message content is required")
        
        # R-ICS213-06: Approved by must include minimum info if provided
        if (self.data.approved_by.name or self.data.approved_by.position or 
            self.data.approved_by.signature):
            if not self.data.approved_by.is_complete:
                self.validation_errors.append("Approved by must have both name and position if provided")
        
        # R-ICS213-07: Replied by must include minimum info if reply is provided
        if self.data.reply:
            if not self.data.replied_by.is_complete:
                self.validation_errors.append("Replied by must have both name and position when reply is provided")
        
        is_valid = len(self.validation_errors) == 0
        
        if is_valid:
            logger.debug("ICS213Form validation passed")
        else:
            logger.debug(f"ICS213Form validation failed: {self.validation_errors}")
        
        return is_valid
    
    def get_validation_errors(self) -> List[str]:
        """Get list of current validation errors."""
        return self.validation_errors.copy()
    
    def is_ready_for_approval(self) -> bool:
        """Check if form is ready for approval."""
        return self.validate() and self.status == FormStatus.DRAFT
    
    def is_ready_for_transmission(self) -> bool:
        """Check if form is ready for transmission."""
        return (self.validate() and 
                self.status in [FormStatus.DRAFT, FormStatus.APPROVED] and
                self.data.approved_by.is_complete)
    
    def approve(self, approver: Person) -> bool:
        """Approve the form with approver information.
        
        Args:
            approver: Person approving the form
            
        Returns:
            True if approval successful, False otherwise
        """
        if not self.is_ready_for_approval():
            return False
        
        if not approver.is_complete:
            self.validation_errors = ["Approver must have both name and position"]
            return False
        
        self.data.approved_by = approver
        self.status = FormStatus.APPROVED
        self.updated_at = datetime.now()
        
        logger.info(f"ICS213Form approved by {approver.display_name}")
        return True
    
    def add_reply(self, reply_text: str, replier: Person) -> bool:
        """Add reply to the form.
        
        Args:
            reply_text: Reply message content
            replier: Person providing the reply
            
        Returns:
            True if reply added successfully, False otherwise
        """
        if not reply_text.strip():
            self.validation_errors = ["Reply text cannot be empty"]
            return False
        
        if not replier.is_complete:
            self.validation_errors = ["Replier must have both name and position"]
            return False
        
        self.data.reply = reply_text.strip()
        self.data.replied_by = replier
        self.data.reply_date_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.status = FormStatus.REPLIED
        self.updated_at = datetime.now()
        
        logger.info(f"Reply added to ICS213Form by {replier.display_name}")
        return True
    
    def to_json(self) -> str:
        """Convert form to JSON string."""
        form_dict = {
            'data': self.data.to_dict(),
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'validation_errors': self.validation_errors
        }
        return json.dumps(form_dict, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ICS213Form':
        """Create form from JSON string."""
        try:
            form_dict = json.loads(json_str)
            
            # Create form with data
            data = ICS213Data.from_dict(form_dict.get('data', {}))
            form = cls(data)
            
            # Set metadata
            status_value = form_dict.get('status', FormStatus.DRAFT.value)
            try:
                form.status = FormStatus(status_value)
            except ValueError:
                form.status = FormStatus.DRAFT
            
            # Parse timestamps
            created_str = form_dict.get('created_at')
            if created_str:
                try:
                    form.created_at = datetime.fromisoformat(created_str)
                except ValueError:
                    pass
            
            updated_str = form_dict.get('updated_at')
            if updated_str:
                try:
                    form.updated_at = datetime.fromisoformat(updated_str)
                except ValueError:
                    pass
            
            form.validation_errors = form_dict.get('validation_errors', [])
            
            logger.debug("ICS213Form loaded from JSON")
            return form
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Failed to load ICS213Form from JSON: {e}")
            raise ValidationError(f"Invalid JSON format: {e}") from e
    
    def get_summary(self) -> str:
        """Get a brief summary of the form."""
        to_name = self.data.to.display_name
        from_name = self.data.from_person.display_name
        subject = self.data.subject or "No Subject"
        
        return f"From: {from_name} | To: {to_name} | Subject: {subject}"
    
    def __str__(self) -> str:
        """String representation of the form."""
        return f"ICS213Form({self.get_summary()}) - Status: {self.status.value}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"ICS213Form(status={self.status.value}, "
                f"from={self.data.from_person.display_name}, "
                f"to={self.data.to.display_name}, "
                f"subject='{self.data.subject}')")
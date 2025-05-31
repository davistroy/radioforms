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

# Import base form interface
try:
    from ..models.base_form import BaseForm, FormType, FormValidationResult
except ImportError:
    # For standalone testing
    import sys
    sys.path.append('.')
    from src.models.base_form import BaseForm, FormType, FormValidationResult


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
    """Represents a person with name and position information for ICS-213 forms.
    
    This class encapsulates person information used throughout ICS-213 forms
    including sender, recipient, approver, and replier. Provides validation
    and formatting methods for display and data exchange.
    
    Attributes:
        name (str): Full name of the person (e.g., "John Smith").
        position (str): Position or role (e.g., "IC", "Operations Chief").
        signature (str): Electronic signature or initials (e.g., "J.S.").
        contact_info (str): Contact information (e.g., "Radio 123", phone number).
    
    Examples:
        >>> person = Person(name="John Smith", position="IC")
        >>> print(person.display_name)
        John Smith, IC
        >>> print(person.is_complete)
        True
        
        >>> incomplete = Person(name="John")
        >>> print(incomplete.is_complete)
        False
    
    Note:
        A person is considered "complete" if both name and position are provided.
        This is the minimum requirement for form validation.
    """
    name: str = ""
    position: str = ""
    signature: str = ""
    contact_info: str = ""
    
    def __post_init__(self) -> None:
        """Validate and normalize person data after initialization.
        
        Strips whitespace from all string fields to ensure consistent data.
        Called automatically by dataclass after object creation.
        """
        self.name = self.name.strip()
        self.position = self.position.strip()
        self.signature = self.signature.strip()
        self.contact_info = self.contact_info.strip()
    
    @property
    def is_complete(self) -> bool:
        """Check if person has the minimum required information for form validation.
        
        Returns:
            bool: True if both name and position are non-empty, False otherwise.
            
        Examples:
            >>> Person(name="John Smith", position="IC").is_complete
            True
            >>> Person(name="John Smith").is_complete
            False
        """
        return bool(self.name and self.position)
    
    @property
    def display_name(self) -> str:
        """Get formatted display name for UI presentation.
        
        Returns:
            str: Formatted name as "Name, Position" if both available,
                 otherwise returns the available field, or "Unknown" if empty.
                 
        Examples:
            >>> Person(name="John Smith", position="IC").display_name
            'John Smith, IC'
            >>> Person(name="John Smith").display_name
            'John Smith'
            >>> Person().display_name
            'Unknown'
        """
        if self.name and self.position:
            return f"{self.name}, {self.position}"
        elif self.name:
            return self.name
        elif self.position:
            return self.position
        return "Unknown"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert person to dictionary for JSON serialization.
        
        Returns:
            Dict[str, str]: Dictionary with all person fields as string values.
            
        Examples:
            >>> person = Person(name="John", position="IC")
            >>> person.to_dict()
            {'name': 'John', 'position': 'IC', 'signature': '', 'contact_info': ''}
        """
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Person':
        """Create Person instance from dictionary data.
        
        Args:
            data (Dict[str, Any]): Dictionary containing person data.
                Expected keys: 'name', 'position', 'signature', 'contact_info'.
                Missing keys will use empty string defaults.
                
        Returns:
            Person: New Person instance with data from dictionary.
            
        Examples:
            >>> data = {'name': 'John Smith', 'position': 'IC'}
            >>> person = Person.from_dict(data)
            >>> person.name
            'John Smith'
        """
        return cls(
            name=data.get('name', ''),
            position=data.get('position', ''),
            signature=data.get('signature', ''),
            contact_info=data.get('contact_info', '')
        )


@dataclass
class ICS213Data:
    """Core data structure for ICS-213 General Message form.
    
    This class represents all the data fields in an ICS-213 General Message form,
    following FEMA ICS standards. It provides structured storage for message
    transmission between incident command personnel.
    
    The class follows the simplified approach outlined in CLAUDE.md:
    - Start with essential fields only
    - Add validation incrementally  
    - Keep it simple for MVP
    - Use string types for dates/times initially
    
    Attributes:
        incident_name (str): Name of the incident this message relates to.
        to (Person): Recipient of the message (name and position required).
        from_person (Person): Sender of the message (name and position required).
        subject (str): Brief subject line describing the message content.
        date (str): Date of message in YYYY-MM-DD format.
        time (str): Time of message in HH:MM format (24-hour).
        message (str): Main message content.
        approved_by (Person): Person who approved the message (optional).
        reply (str): Reply message content (if applicable).
        replied_by (Person): Person who provided the reply (if applicable).
        reply_date_time (str): Date and time of reply in ISO format.
        priority (Priority): Message priority level (routine/urgent/immediate).
        form_version (str): Version of the form schema.
        reply_requested (bool): Whether a reply is requested.
        
    Examples:
        >>> # Create a basic message
        >>> data = ICS213Data(
        ...     incident_name="Wildfire Alpha",
        ...     to=Person(name="John Smith", position="IC"),
        ...     from_person=Person(name="Jane Doe", position="Ops"),
        ...     subject="Status Update",
        ...     date="2025-05-30",
        ...     time="14:30",
        ...     message="All teams deployed and operational.",
        ...     priority=Priority.URGENT
        ... )
        
        >>> # Create with reply
        >>> data.reply = "Message received and understood."
        >>> data.replied_by = Person(name="John Smith", position="IC")
        
    Note:
        The 'from' field is named 'from_person' because 'from' is a Python keyword.
        Date and time fields use string format for simplicity in the MVP version.
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
    
    def __post_init__(self) -> None:
        """Clean up and normalize data after initialization.
        
        Strips whitespace from all string fields to ensure consistent data
        and prevent validation issues caused by leading/trailing spaces.
        Called automatically by dataclass after object creation.
        
        Note:
            This method is called automatically and should not be called manually.
            Person objects are not modified here as they have their own post_init.
        """
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


class ICS213Form(BaseForm):
    """ICS-213 General Message form with comprehensive validation and business logic.
    
    This class encapsulates a complete ICS-213 form including data, validation,
    status tracking, and serialization capabilities. It follows FEMA ICS-213
    standards and provides the core functionality for message management in
    the RadioForms application.
    
    The form implements a complete lifecycle:
    1. DRAFT - Initial state, allows editing and validation
    2. APPROVED - Validated and approved for transmission
    3. TRANSMITTED - Sent via radio or other means
    4. RECEIVED - Acknowledgment received
    5. REPLIED - Reply has been provided
    6. DOCUMENTED - Archived and documented
    
    Key Features:
        - Comprehensive validation according to ICS-213 requirements
        - Status tracking throughout form lifecycle
        - JSON serialization for data persistence and exchange
        - Error tracking and reporting
        - Timestamp management for audit trails
        - Support for approval workflows
        - Reply handling capabilities
    
    Attributes:
        data (ICS213Data): The form's data content.
        status (FormStatus): Current lifecycle status of the form.
        validation_errors (List[str]): List of current validation errors.
        created_at (datetime): Timestamp when form was created.
        updated_at (datetime): Timestamp when form was last modified.
    
    Examples:
        >>> # Create a new form
        >>> form = ICS213Form()
        >>> form.data.incident_name = "Wildfire Alpha"
        >>> form.data.to = Person(name="John Smith", position="IC")
        >>> form.data.from_person = Person(name="Jane Doe", position="Ops")
        >>> form.data.subject = "Status Update"
        >>> form.data.message = "All teams deployed successfully."
        
        >>> # Validate the form
        >>> if form.validate():
        ...     print("Form is valid")
        ... else:
        ...     print(f"Errors: {form.get_validation_errors()}")
        
        >>> # Approve the form
        >>> approver = Person(name="Chief Officer", position="IC")
        >>> if form.approve(approver):
        ...     print(f"Form approved by {approver.display_name}")
        
        >>> # Serialize to JSON
        >>> json_data = form.to_json()
        >>> restored_form = ICS213Form.from_json(json_data)
        
    Note:
        Forms must be validated before approval or transmission. The validation
        method populates the validation_errors list with specific issues that
        need to be addressed.
    """
    
    def __init__(self, data: Optional[ICS213Data] = None) -> None:
        """Initialize ICS-213 form with optional data.
        
        Creates a new ICS-213 form in DRAFT status with empty validation errors.
        If no data is provided, initializes with empty ICS213Data instance.
        
        Args:
            data (Optional[ICS213Data]): Initial form data. If None, creates
                empty data structure with default values.
                
        Examples:
            >>> # Create empty form
            >>> form = ICS213Form()
            >>> form.status
            <FormStatus.DRAFT: 'draft'>
            
            >>> # Create form with data
            >>> data = ICS213Data(incident_name="Test Incident")
            >>> form = ICS213Form(data)
            >>> form.data.incident_name
            'Test Incident'
        """
        # Initialize base form
        super().__init__()
        self.metadata.form_type = FormType.ICS_213
        
        # Initialize ICS-213 specific data
        self.data = data or ICS213Data()
        self.status = FormStatus.DRAFT
        self.validation_errors: List[str] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        logger.debug("ICS213Form initialized")
    
    def validate(self) -> bool:
        """Validate form data according to ICS-213 requirements.
        
        Performs comprehensive validation of all form fields according to
        FEMA ICS-213 standards. Validation errors are cleared and repopulated
        on each call, so this method can be called multiple times.
        
        Validation Rules:
            - Recipient (To) must have both name and position
            - Sender (From) must have both name and position  
            - Subject is required
            - Date and Time are required
            - Message content is required
            - If approver is specified, must have name and position
            - If reply exists, replier must have name and position
        
        Returns:
            bool: True if form passes all validation rules, False otherwise.
            
        Side Effects:
            Updates self.validation_errors list with specific error messages
            for any validation failures found.
            
        Examples:
            >>> form = ICS213Form()
            >>> form.validate()
            False
            >>> len(form.validation_errors) > 0
            True
            
            >>> # Fill required fields
            >>> form.data.to = Person(name="John", position="IC")
            >>> form.data.from_person = Person(name="Jane", position="Ops")
            >>> form.data.subject = "Test"
            >>> form.data.date = "2025-05-30"
            >>> form.data.time = "14:30"
            >>> form.data.message = "Test message"
            >>> form.validate()
            True
            >>> len(form.validation_errors)
            0
            
        Note:
            Validation must pass before a form can be approved or transmitted.
            Use get_validation_errors() to retrieve human-readable error messages.
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
    
    # BaseForm interface implementation
    
    def get_form_type(self) -> FormType:
        """Get the type of this form.
        
        Returns:
            FormType: The ICS-213 form type.
        """
        return FormType.ICS_213
    
    def is_valid(self) -> bool:
        """Check if the form data is valid.
        
        Returns:
            bool: True if form is valid, False otherwise.
        """
        return self.validate()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert form to dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary containing all form data.
        """
        return {
            'form_type': 'ICS-213',
            'status': self.status.value,
            'validation_errors': self.validation_errors.copy(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'data': asdict(self.data)
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load form data from dictionary representation.
        
        Args:
            data: Dictionary containing form data.
        """
        # Load status
        if 'status' in data:
            try:
                self.status = FormStatus(data['status'])
            except ValueError:
                self.status = FormStatus.DRAFT
        
        # Load timestamps
        if 'created_at' in data:
            try:
                self.created_at = datetime.fromisoformat(data['created_at'])
            except ValueError:
                pass
        
        if 'updated_at' in data:
            try:
                self.updated_at = datetime.fromisoformat(data['updated_at'])
            except ValueError:
                pass
        
        # Load validation errors
        self.validation_errors = data.get('validation_errors', [])
        
        # Load form data
        if 'data' in data:
            self.data = ICS213Data.from_dict(data['data'])
    
    def validate_detailed(self) -> FormValidationResult:
        """Perform detailed validation with specific error information.
        
        Returns:
            FormValidationResult: Detailed validation result.
        """
        result = FormValidationResult()
        
        # Clear and repopulate validation errors
        self.validation_errors.clear()
        
        # Check recipient
        if not self.data.to.name.strip():
            error = "Recipient name is required"
            self.validation_errors.append(error)
            result.add_error(error, 'to_name')
        
        if not self.data.to.position.strip():
            error = "Recipient position is required"
            self.validation_errors.append(error)
            result.add_error(error, 'to_position')
        
        # Check sender
        if not self.data.from_person.name.strip():
            error = "Sender name is required"
            self.validation_errors.append(error)
            result.add_error(error, 'from_name')
        
        if not self.data.from_person.position.strip():
            error = "Sender position is required"
            self.validation_errors.append(error)
            result.add_error(error, 'from_position')
        
        # Check subject
        if not self.data.subject.strip():
            error = "Subject is required"
            self.validation_errors.append(error)
            result.add_error(error, 'subject')
        
        # Check message
        if not self.data.message.strip():
            error = "Message content is required"
            self.validation_errors.append(error)
            result.add_error(error, 'message')
        
        # Check approved_by if specified
        if self.data.approved_by.name.strip() and not self.data.approved_by.position.strip():
            error = "Approved by position is required when approved by name is specified"
            self.validation_errors.append(error)
            result.add_error(error, 'approved_by_position')
        
        result.is_valid = len(self.validation_errors) == 0
        
        return result
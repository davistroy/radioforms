#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enhanced ICS-213 General Message form model.

This module implements an improved data model for the ICS-213 General Message form,
with enhanced validation, DAO integration, and support for form state tracking
and attachments.
"""

import datetime
import re
from enum import Enum
from typing import Dict, Any, List, Optional, Set, Union

from radioforms.models.base_form import BaseFormModel, ValidationResult
from radioforms.database.dao.form_dao_refactored import FormDAO
from radioforms.database.dao.attachment_dao_refactored import AttachmentDAO


class FormState(Enum):
    """
    Represents the possible states of an ICS-213 form.
    """
    DRAFT = "draft"
    APPROVED = "approved"
    TRANSMITTED = "transmitted"
    RECEIVED = "received"
    REPLIED = "replied"
    RETURNED = "returned"
    ARCHIVED = "archived"


class EnhancedICS213Form(BaseFormModel):
    """
    Enhanced ICS-213 General Message form model.
    
    This form is used for general message communication in incident management systems.
    It includes fields for message details, sender information, and recipient information,
    with enhanced validation, state tracking, and attachment support.
    """
    
    def __init__(self, form_id: Optional[str] = None):
        """
        Initialize the ICS-213 form.
        
        Args:
            form_id: Unique identifier for the form (generated if not provided)
        """
        super().__init__(form_id)
        
        # Form state
        self._state = FormState.DRAFT
        self._form_version = "2.0"  # ICS-213 form version
        
        # Incident information
        self._incident_name = ""
        
        # Message information
        self._to = ""
        self._to_position = ""
        self._from = ""
        self._from_position = ""
        self._subject = ""
        self._message_date = datetime.datetime.now()
        self._message_time = self._message_date.time()
        self._message = ""
        
        # Sender information
        self._sender_name = ""
        self._sender_position = ""
        self._sender_date = datetime.datetime.now()
        self._sender_time = self._sender_date.time()
        self._sender_signature = ""
        
        # Recipient information
        self._recipient_name = ""
        self._recipient_position = ""
        self._recipient_date = None
        self._recipient_time = None
        self._recipient_signature = ""
        self._reply = ""
        
        # Tracking information
        self._transmission_method = ""  # How the message was transmitted
        self._priority = "Routine"  # Priority level (Routine, Priority, Immediate)
        self._attachments = []  # List of attachment IDs
        
        # Register property setters for change tracking
        self._register_properties()
        
    def _register_properties(self):
        """Register all properties for change tracking."""
        # Form state
        self.register_property("state", self._set_state)
        self.register_property("form_version", self._set_form_version)
        
        # Incident information
        self.register_property("incident_name", self._set_incident_name)
        
        # Message information
        self.register_property("to", self._set_to)
        self.register_property("to_position", self._set_to_position)
        self.register_property("from", self._set_from)
        self.register_property("from_position", self._set_from_position)
        self.register_property("subject", self._set_subject)
        self.register_property("message_date", self._set_message_date)
        self.register_property("message_time", self._set_message_time)
        self.register_property("message", self._set_message)
        
        # Sender information
        self.register_property("sender_name", self._set_sender_name)
        self.register_property("sender_position", self._set_sender_position)
        self.register_property("sender_date", self._set_sender_date)
        self.register_property("sender_time", self._set_sender_time)
        self.register_property("sender_signature", self._set_sender_signature)
        
        # Recipient information
        self.register_property("recipient_name", self._set_recipient_name)
        self.register_property("recipient_position", self._set_recipient_position)
        self.register_property("recipient_date", self._set_recipient_date)
        self.register_property("recipient_time", self._set_recipient_time)
        self.register_property("recipient_signature", self._set_recipient_signature)
        self.register_property("reply", self._set_reply)
        
        # Tracking information
        self.register_property("transmission_method", self._set_transmission_method)
        self.register_property("priority", self._set_priority)
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
        
    # Message information property setters
    
    def _set_to(self, value: str):
        """Set the 'to' field with change tracking."""
        old_value = self._to
        self._to = value
        self.notify_observers("to", old_value, value)
        
    def _set_to_position(self, value: str):
        """Set the 'to position' field with change tracking."""
        old_value = self._to_position
        self._to_position = value
        self.notify_observers("to_position", old_value, value)
        
    def _set_from(self, value: str):
        """Set the 'from' field with change tracking."""
        old_value = self._from
        self._from = value
        self.notify_observers("from", old_value, value)
        
    def _set_from_position(self, value: str):
        """Set the 'from position' field with change tracking."""
        old_value = self._from_position
        self._from_position = value
        self.notify_observers("from_position", old_value, value)
        
    def _set_subject(self, value: str):
        """Set the subject field with change tracking."""
        old_value = self._subject
        self._subject = value
        self.notify_observers("subject", old_value, value)
        
    def _set_message_date(self, value: datetime.datetime):
        """Set the message date with change tracking."""
        old_value = self._message_date
        self._message_date = value
        self.notify_observers("message_date", old_value, value)
        
    def _set_message_time(self, value: datetime.time):
        """Set the message time with change tracking."""
        old_value = self._message_time
        self._message_time = value
        self.notify_observers("message_time", old_value, value)
        
    def _set_message(self, value: str):
        """Set the message field with change tracking."""
        old_value = self._message
        self._message = value
        self.notify_observers("message", old_value, value)
        
    # Sender information property setters
    
    def _set_sender_name(self, value: str):
        """Set the sender's name with change tracking."""
        old_value = self._sender_name
        self._sender_name = value
        self.notify_observers("sender_name", old_value, value)
        
    def _set_sender_position(self, value: str):
        """Set the sender's position with change tracking."""
        old_value = self._sender_position
        self._sender_position = value
        self.notify_observers("sender_position", old_value, value)
        
    def _set_sender_date(self, value: datetime.datetime):
        """Set the sender's date with change tracking."""
        old_value = self._sender_date
        self._sender_date = value
        self.notify_observers("sender_date", old_value, value)
        
    def _set_sender_time(self, value: datetime.time):
        """Set the sender's time with change tracking."""
        old_value = self._sender_time
        self._sender_time = value
        self.notify_observers("sender_time", old_value, value)
        
    def _set_sender_signature(self, value: str):
        """Set the sender's signature with change tracking."""
        old_value = self._sender_signature
        self._sender_signature = value
        self.notify_observers("sender_signature", old_value, value)
        
    # Recipient information property setters
    
    def _set_recipient_name(self, value: str):
        """Set the recipient's name with change tracking."""
        old_value = self._recipient_name
        self._recipient_name = value
        self.notify_observers("recipient_name", old_value, value)
        
    def _set_recipient_position(self, value: str):
        """Set the recipient's position with change tracking."""
        old_value = self._recipient_position
        self._recipient_position = value
        self.notify_observers("recipient_position", old_value, value)
        
    def _set_recipient_date(self, value: Optional[datetime.datetime]):
        """Set the recipient's date with change tracking."""
        old_value = self._recipient_date
        self._recipient_date = value
        self.notify_observers("recipient_date", old_value, value)
        
    def _set_recipient_time(self, value: Optional[datetime.time]):
        """Set the recipient's time with change tracking."""
        old_value = self._recipient_time
        self._recipient_time = value
        self.notify_observers("recipient_time", old_value, value)
        
    def _set_recipient_signature(self, value: str):
        """Set the recipient's signature with change tracking."""
        old_value = self._recipient_signature
        self._recipient_signature = value
        self.notify_observers("recipient_signature", old_value, value)
        
    def _set_reply(self, value: str):
        """Set the reply field with change tracking."""
        old_value = self._reply
        self._reply = value
        self.notify_observers("reply", old_value, value)
        
    # Tracking information property setters
    
    def _set_transmission_method(self, value: str):
        """Set the transmission method with change tracking."""
        old_value = self._transmission_method
        self._transmission_method = value
        self.notify_observers("transmission_method", old_value, value)
        
    def _set_priority(self, value: str):
        """Set the priority level with change tracking."""
        valid_priorities = ["Routine", "Priority", "Immediate"]
        if value not in valid_priorities:
            raise ValueError(f"Invalid priority: {value}. Must be one of: {', '.join(valid_priorities)}")
            
        old_value = self._priority
        self._priority = value
        self.notify_observers("priority", old_value, value)
        
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
    def to(self) -> str:
        """Get the 'to' field value."""
        return self._to
        
    @to.setter
    def to(self, value: str):
        """Set the 'to' field value."""
        self.set_property("to", value)
        
    @property
    def to_position(self) -> str:
        """Get the 'to position' field value."""
        return self._to_position
        
    @to_position.setter
    def to_position(self, value: str):
        """Set the 'to position' field value."""
        self.set_property("to_position", value)
        
    @property
    def from_field(self) -> str:
        """Get the 'from' field value."""
        return self._from
        
    @from_field.setter
    def from_field(self, value: str):
        """Set the 'from' field value."""
        self.set_property("from", value)
        
    @property
    def from_position(self) -> str:
        """Get the 'from position' field value."""
        return self._from_position
        
    @from_position.setter
    def from_position(self, value: str):
        """Set the 'from position' field value."""
        self.set_property("from_position", value)
        
    @property
    def subject(self) -> str:
        """Get the subject field value."""
        return self._subject
        
    @subject.setter
    def subject(self, value: str):
        """Set the subject field value."""
        self.set_property("subject", value)
        
    @property
    def message_date(self) -> datetime.datetime:
        """Get the message date value."""
        return self._message_date
        
    @message_date.setter
    def message_date(self, value: datetime.datetime):
        """Set the message date value."""
        self.set_property("message_date", value)
        
    @property
    def message_time(self) -> datetime.time:
        """Get the message time value."""
        return self._message_time
        
    @message_time.setter
    def message_time(self, value: datetime.time):
        """Set the message time value."""
        self.set_property("message_time", value)
        
    @property
    def message(self) -> str:
        """Get the message field value."""
        return self._message
        
    @message.setter
    def message(self, value: str):
        """Set the message field value."""
        self.set_property("message", value)
        
    @property
    def sender_name(self) -> str:
        """Get the sender's name value."""
        return self._sender_name
        
    @sender_name.setter
    def sender_name(self, value: str):
        """Set the sender's name value."""
        self.set_property("sender_name", value)
        
    @property
    def sender_position(self) -> str:
        """Get the sender's position value."""
        return self._sender_position
        
    @sender_position.setter
    def sender_position(self, value: str):
        """Set the sender's position value."""
        self.set_property("sender_position", value)
        
    @property
    def sender_date(self) -> datetime.datetime:
        """Get the sender's date value."""
        return self._sender_date
        
    @sender_date.setter
    def sender_date(self, value: datetime.datetime):
        """Set the sender's date value."""
        self.set_property("sender_date", value)
        
    @property
    def sender_time(self) -> datetime.time:
        """Get the sender's time value."""
        return self._sender_time
        
    @sender_time.setter
    def sender_time(self, value: datetime.time):
        """Set the sender's time value."""
        self.set_property("sender_time", value)
        
    @property
    def sender_signature(self) -> str:
        """Get the sender's signature value."""
        return self._sender_signature
        
    @sender_signature.setter
    def sender_signature(self, value: str):
        """Set the sender's signature value."""
        self.set_property("sender_signature", value)
        
    @property
    def recipient_name(self) -> str:
        """Get the recipient's name value."""
        return self._recipient_name
        
    @recipient_name.setter
    def recipient_name(self, value: str):
        """Set the recipient's name value."""
        self.set_property("recipient_name", value)
        
    @property
    def recipient_position(self) -> str:
        """Get the recipient's position value."""
        return self._recipient_position
        
    @recipient_position.setter
    def recipient_position(self, value: str):
        """Set the recipient's position value."""
        self.set_property("recipient_position", value)
        
    @property
    def recipient_date(self) -> Optional[datetime.datetime]:
        """Get the recipient's date value."""
        return self._recipient_date
        
    @recipient_date.setter
    def recipient_date(self, value: Optional[datetime.datetime]):
        """Set the recipient's date value."""
        self.set_property("recipient_date", value)
        
    @property
    def recipient_time(self) -> Optional[datetime.time]:
        """Get the recipient's time value."""
        return self._recipient_time
        
    @recipient_time.setter
    def recipient_time(self, value: Optional[datetime.time]):
        """Set the recipient's time value."""
        self.set_property("recipient_time", value)
        
    @property
    def recipient_signature(self) -> str:
        """Get the recipient's signature value."""
        return self._recipient_signature
        
    @recipient_signature.setter
    def recipient_signature(self, value: str):
        """Set the recipient's signature value."""
        self.set_property("recipient_signature", value)
        
    @property
    def reply(self) -> str:
        """Get the reply field value."""
        return self._reply
        
    @reply.setter
    def reply(self, value: str):
        """Set the reply field value."""
        self.set_property("reply", value)
        
    @property
    def transmission_method(self) -> str:
        """Get the transmission method value."""
        return self._transmission_method
        
    @transmission_method.setter
    def transmission_method(self, value: str):
        """Set the transmission method value."""
        self.set_property("transmission_method", value)
        
    @property
    def priority(self) -> str:
        """Get the priority level value."""
        return self._priority
        
    @priority.setter
    def priority(self, value: str):
        """Set the priority level value."""
        self.set_property("priority", value)
        
    @property
    def attachments(self) -> List[str]:
        """Get the attachments list value."""
        return self._attachments.copy()
        
    @attachments.setter
    def attachments(self, value: List[str]):
        """Set the attachments list value."""
        self.set_property("attachments", value)
        
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
        if self._state != FormState.DRAFT:
            return False
            
        # Set approver information
        self.sender_name = approver_name
        self.sender_position = approver_position
        self.sender_signature = approver_signature
        self.sender_date = datetime.datetime.now()
        self.sender_time = self.sender_date.time()
        
        # Update state
        self.state = FormState.APPROVED
        return True
        
    def transmit(self, method: str = "Digital") -> bool:
        """
        Mark the form as transmitted.
        
        Args:
            method: Method of transmission
            
        Returns:
            True if the state was changed, False if not
        """
        if self._state not in [FormState.DRAFT, FormState.APPROVED]:
            return False
            
        self.transmission_method = method
        self.state = FormState.TRANSMITTED
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
        if self._state != FormState.TRANSMITTED:
            return False
            
        self.recipient_name = recipient_name
        self.recipient_position = recipient_position
        self.recipient_date = datetime.datetime.now()
        self.recipient_time = self.recipient_date.time()
        
        self.state = FormState.RECEIVED
        return True
        
    def reply_to_message(self, reply_text: str, recipient_signature: str) -> bool:
        """
        Add a reply to the message.
        
        Args:
            reply_text: Text of the reply
            recipient_signature: Signature of the recipient
            
        Returns:
            True if the state was changed, False if not
        """
        if self._state != FormState.RECEIVED:
            return False
            
        self.reply = reply_text
        self.recipient_signature = recipient_signature
        self.recipient_date = datetime.datetime.now()
        self.recipient_time = self.recipient_date.time()
        
        self.state = FormState.REPLIED
        return True
        
    def return_to_sender(self) -> bool:
        """
        Mark the form as returned to sender.
        
        Returns:
            True if the state was changed, False if not
        """
        if self._state != FormState.REPLIED:
            return False
            
        self.state = FormState.RETURNED
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
        return "ICS-213"
        
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
            
            # Message information
            "to": self._to,
            "to_position": self._to_position,
            "from": self._from,
            "from_position": self._from_position,
            "subject": self._subject,
            "message_date": self._message_date.isoformat() if self._message_date else None,
            "message_time": self._message_time.isoformat() if self._message_time else None,
            "message": self._message,
            
            # Sender information
            "sender_name": self._sender_name,
            "sender_position": self._sender_position,
            "sender_date": self._sender_date.isoformat() if self._sender_date else None,
            "sender_time": self._sender_time.isoformat() if self._sender_time else None,
            "sender_signature": self._sender_signature,
            
            # Recipient information
            "recipient_name": self._recipient_name,
            "recipient_position": self._recipient_position,
            "recipient_date": self._recipient_date.isoformat() if self._recipient_date else None,
            "recipient_time": self._recipient_time.isoformat() if self._recipient_time else None,
            "recipient_signature": self._recipient_signature,
            "reply": self._reply,
            
            # Tracking information
            "transmission_method": self._transmission_method,
            "priority": self._priority,
            "attachments": self._attachments
        })
        
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnhancedICS213Form':
        """
        Create a form instance from a dictionary.
        
        Args:
            data: Dictionary representation of the form
            
        Returns:
            A new form instance
        """
        # Create the form with base fields
        form = super(EnhancedICS213Form, cls).from_dict(data)
        
        # Set form state
        if "state" in data:
            try:
                form._state = FormState(data["state"]) if data["state"] else FormState.DRAFT
            except (ValueError, TypeError):
                form._state = FormState.DRAFT
                
        form._form_version = data.get("form_version", "2.0")
        
        # Set incident information
        form._incident_name = data.get("incident_name", "")
        
        # Parse date/time fields
        message_date = data.get("message_date")
        if message_date:
            try:
                form._message_date = datetime.datetime.fromisoformat(message_date)
            except (ValueError, TypeError):
                form._message_date = datetime.datetime.now()
                
        message_time = data.get("message_time")
        if message_time:
            try:
                form._message_time = datetime.time.fromisoformat(message_time)
            except (ValueError, TypeError):
                form._message_time = datetime.datetime.now().time()
                
        sender_date = data.get("sender_date")
        if sender_date:
            try:
                form._sender_date = datetime.datetime.fromisoformat(sender_date)
            except (ValueError, TypeError):
                form._sender_date = datetime.datetime.now()
                
        sender_time = data.get("sender_time")
        if sender_time:
            try:
                form._sender_time = datetime.time.fromisoformat(sender_time)
            except (ValueError, TypeError):
                form._sender_time = datetime.datetime.now().time()
                
        recipient_date = data.get("recipient_date")
        if recipient_date:
            try:
                form._recipient_date = datetime.datetime.fromisoformat(recipient_date)
            except (ValueError, TypeError):
                form._recipient_date = None
                
        recipient_time = data.get("recipient_time")
        if recipient_time:
            try:
                form._recipient_time = datetime.time.fromisoformat(recipient_time)
            except (ValueError, TypeError):
                form._recipient_time = None
                
        # Set string fields
        form._to = data.get("to", "")
        form._to_position = data.get("to_position", "")
        form._from = data.get("from", "")
        form._from_position = data.get("from_position", "")
        form._subject = data.get("subject", "")
        form._message = data.get("message", "")
        
        form._sender_name = data.get("sender_name", "")
        form._sender_position = data.get("sender_position", "")
        form._sender_signature = data.get("sender_signature", "")
        
        form._recipient_name = data.get("recipient_name", "")
        form._recipient_position = data.get("recipient_position", "")
        form._recipient_signature = data.get("recipient_signature", "")
        form._reply = data.get("reply", "")
        
        # Set tracking information
        form._transmission_method = data.get("transmission_method", "")
        form._priority = data.get("priority", "Routine")
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
        if not self._to:
            result.add_error("to", "To field is required")
            
        if not self._from:
            result.add_error("from", "From field is required")
            
        if not self._subject:
            result.add_error("subject", "Subject is required")
            
        if not self._message:
            result.add_error("message", "Message content is required")
            
        if not self._sender_name:
            result.add_error("sender_name", "Sender name is required")
            
        # Validate field formats using regex
        name_pattern = re.compile(r'^[A-Za-z\s\-\.]+$')
        
        if self._sender_name and not name_pattern.match(self._sender_name):
            result.add_error("sender_name", "Sender name can only contain letters, spaces, and hyphens")
            
        if self._recipient_name and not name_pattern.match(self._recipient_name):
            result.add_error("recipient_name", "Recipient name can only contain letters, spaces, and hyphens")
            
        # Cross-field validation
        if self._subject and "URGENT" in self._subject.upper() and not self._message.strip():
            result.add_error("message", "Urgent messages must include message content")
            
        # Validate field lengths
        max_lengths = {
            "to": 100,
            "to_position": 100,
            "from": 100,
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
            value = getattr(self, f"_{field}")
            if value and len(str(value)) > max_length:
                result.add_error(field, f"{field.replace('_', ' ').title()} cannot exceed {max_length} characters")
        
        # Check for valid dates
        now = datetime.datetime.now()
        
        if self._message_date and self._message_date > now:
            result.add_error("message_date", "Message date cannot be in the future")
            
        if self._sender_date and self._sender_date > now:
            result.add_error("sender_date", "Sender date cannot be in the future")
            
        # Only validate recipient date if it's provided (it's optional)
        if self._recipient_date and self._recipient_date > now:
            result.add_error("recipient_date", "Recipient date cannot be in the future")
            
        # Only validate if received before reply
        if self._recipient_date and self._message_date and self._recipient_date < self._message_date:
            result.add_error("recipient_date", "Reply date cannot be earlier than the message date")
            
        # State-specific validation
        if self._state == FormState.APPROVED and not self._sender_signature:
            result.add_error("sender_signature", "Approved messages must have a sender signature")
            
        if self._state == FormState.REPLIED and not self._reply:
            result.add_error("reply", "Replied messages must include reply content")
            
        if self._state == FormState.REPLIED and not self._recipient_signature:
            result.add_error("recipient_signature", "Replied messages must have a recipient signature")
            
        return result
    
    @classmethod
    def create_new(cls) -> 'EnhancedICS213Form':
        """
        Factory method to create a new ICS-213 form with default values.
        
        Returns:
            A new ICS-213 form instance
        """
        form = cls()
        # Set current date/time for message
        now = datetime.datetime.now()
        form._message_date = now
        form._message_time = now.time()
        form._sender_date = now
        form._sender_time = now.time()
        form._state = FormState.DRAFT
        form._priority = "Routine"
        
        return form
    
    @classmethod
    def create_with_dao(cls, form_dao: FormDAO) -> 'EnhancedICS213Form':
        """
        Factory method to create a new form with DAO integration.
        
        Args:
            form_dao: FormDAO instance for persistence
            
        Returns:
            A new ICS-213 form instance with DAO integration
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
    def load_from_dao(cls, form_dao: FormDAO, form_id: str, version_id: Optional[str] = None) -> Optional['EnhancedICS213Form']:
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

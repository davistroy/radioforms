#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ICS-213 General Message form model.

This module implements the data model for the ICS-213 General Message form,
which is used for general message communication in incident management.
"""

import datetime
from typing import Dict, Any, List, Optional

from radioforms.models.base_form import BaseFormModel, ValidationResult


class ICS213Form(BaseFormModel):
    """
    ICS-213 General Message form model.
    
    This form is used for general message communication in incident management systems.
    It includes fields for message details, sender information, and recipient information.
    """
    
    def __init__(self, form_id: Optional[str] = None):
        """
        Initialize the ICS-213 form.
        
        Args:
            form_id: Unique identifier for the form (generated if not provided)
        """
        super().__init__(form_id)
        
        # Message information
        self._to = ""
        self._from = ""
        self._subject = ""
        self._message_date = datetime.datetime.now()
        self._message_time = self._message_date.time()
        self._message = ""
        
        # Sender information
        self._sender_name = ""
        self._sender_position = ""
        self._sender_date = datetime.datetime.now()
        self._sender_time = self._sender_date.time()
        
        # Recipient information
        self._recipient_name = ""
        self._recipient_position = ""
        self._recipient_date = None
        self._recipient_time = None
        self._reply = ""
        
        # Register property setters for change tracking
        self._register_properties()
        
    def _register_properties(self):
        """Register all properties for change tracking."""
        # Message information
        self.register_property("to", self._set_to)
        self.register_property("from", self._set_from)
        self.register_property("subject", self._set_subject)
        self.register_property("message_date", self._set_message_date)
        self.register_property("message_time", self._set_message_time)
        self.register_property("message", self._set_message)
        
        # Sender information
        self.register_property("sender_name", self._set_sender_name)
        self.register_property("sender_position", self._set_sender_position)
        self.register_property("sender_date", self._set_sender_date)
        self.register_property("sender_time", self._set_sender_time)
        
        # Recipient information
        self.register_property("recipient_name", self._set_recipient_name)
        self.register_property("recipient_position", self._set_recipient_position)
        self.register_property("recipient_date", self._set_recipient_date)
        self.register_property("recipient_time", self._set_recipient_time)
        self.register_property("reply", self._set_reply)
        
    # Message information property setters
    
    def _set_to(self, value: str):
        """Set the 'to' field with change tracking."""
        old_value = self._to
        self._to = value
        self.notify_observers("to", old_value, value)
        
    def _set_from(self, value: str):
        """Set the 'from' field with change tracking."""
        old_value = self._from
        self._from = value
        self.notify_observers("from", old_value, value)
        
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
        
    def _set_reply(self, value: str):
        """Set the reply field with change tracking."""
        old_value = self._reply
        self._reply = value
        self.notify_observers("reply", old_value, value)
        
    # Property getters
    
    @property
    def to(self) -> str:
        """Get the 'to' field value."""
        return self._to
        
    @to.setter
    def to(self, value: str):
        """Set the 'to' field value."""
        self.set_property("to", value)
        
    @property
    def from_field(self) -> str:
        """Get the 'from' field value."""
        return self._from
        
    @from_field.setter
    def from_field(self, value: str):
        """Set the 'from' field value."""
        self.set_property("from", value)
        
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
    def reply(self) -> str:
        """Get the reply field value."""
        return self._reply
        
    @reply.setter
    def reply(self, value: str):
        """Set the reply field value."""
        self.set_property("reply", value)
        
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
            # Message information
            "to": self._to,
            "from": self._from,
            "subject": self._subject,
            "message_date": self._message_date.isoformat() if self._message_date else None,
            "message_time": self._message_time.isoformat() if self._message_time else None,
            "message": self._message,
            
            # Sender information
            "sender_name": self._sender_name,
            "sender_position": self._sender_position,
            "sender_date": self._sender_date.isoformat() if self._sender_date else None,
            "sender_time": self._sender_time.isoformat() if self._sender_time else None,
            
            # Recipient information
            "recipient_name": self._recipient_name,
            "recipient_position": self._recipient_position,
            "recipient_date": self._recipient_date.isoformat() if self._recipient_date else None,
            "recipient_time": self._recipient_time.isoformat() if self._recipient_time else None,
            "reply": self._reply
        })
        
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ICS213Form':
        """
        Create a form instance from a dictionary.
        
        Args:
            data: Dictionary representation of the form
            
        Returns:
            A new form instance
        """
        # Create the form with base fields
        form = super(ICS213Form, cls).from_dict(data)
        
        # Parse date/time fields
        message_date = data.get("message_date")
        if message_date:
            form._message_date = datetime.datetime.fromisoformat(message_date)
            
        message_time = data.get("message_time")
        if message_time:
            form._message_time = datetime.time.fromisoformat(message_time)
            
        sender_date = data.get("sender_date")
        if sender_date:
            form._sender_date = datetime.datetime.fromisoformat(sender_date)
            
        sender_time = data.get("sender_time")
        if sender_time:
            form._sender_time = datetime.time.fromisoformat(sender_time)
            
        recipient_date = data.get("recipient_date")
        if recipient_date:
            form._recipient_date = datetime.datetime.fromisoformat(recipient_date)
            
        recipient_time = data.get("recipient_time")
        if recipient_time:
            form._recipient_time = datetime.time.fromisoformat(recipient_time)
            
        # Set string fields
        form._to = data.get("to", "")
        form._from = data.get("from", "")
        form._subject = data.get("subject", "")
        form._message = data.get("message", "")
        form._sender_name = data.get("sender_name", "")
        form._sender_position = data.get("sender_position", "")
        form._recipient_name = data.get("recipient_name", "")
        form._recipient_position = data.get("recipient_position", "")
        form._reply = data.get("reply", "")
        
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
            
        # Validate lengths
        if len(self._to) > 100:
            result.add_error("to", "To field cannot exceed 100 characters")
            
        if len(self._from) > 100:
            result.add_error("from", "From field cannot exceed 100 characters")
            
        if len(self._subject) > 150:
            result.add_error("subject", "Subject cannot exceed 150 characters")
            
        if len(self._message) > 2000:
            result.add_error("message", "Message cannot exceed 2000 characters")
            
        # Check for valid dates
        if self._message_date and self._message_date > datetime.datetime.now():
            result.add_error("message_date", "Message date cannot be in the future")
            
        if self._sender_date and self._sender_date > datetime.datetime.now():
            result.add_error("sender_date", "Sender date cannot be in the future")
            
        # Only validate recipient date if it's provided (it's optional)
        if self._recipient_date and self._recipient_date > datetime.datetime.now():
            result.add_error("recipient_date", "Recipient date cannot be in the future")
            
        return result
        
    @classmethod
    def create_new(cls) -> 'ICS213Form':
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
        
        return form

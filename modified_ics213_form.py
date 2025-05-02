from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from radioforms.models.dataclass_forms import BaseForm, FormState

@dataclass
class ModifiedICS213Form(BaseForm):
    """ICS-213 General Message form model - Modified version"""
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
    reply_text: str = ""  # Renamed from 'reply' to 'reply_text' to avoid method name conflict
    
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
            "reply_text": 1000,  # Updated field name
            "incident_name": 100
        }
        
        for field, max_length in max_lengths.items():
            value = getattr(self, field)
            if value and len(str(value)) > max_length:
                errors[field] = f"{field.replace('_', ' ').title()} cannot exceed {max_length} characters"
        
        # State-specific validations
        if self.state == FormState.APPROVED and not self.sender_signature:
            errors["sender_signature"] = "Approved messages must have a sender signature"
            
        if self.state == FormState.REPLIED and not self.reply_text:  # Updated field name
            errors["reply_text"] = "Replied messages must include reply content"
            
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
    def from_dict(cls, data: Dict[str, Any]) -> 'ModifiedICS213Form':
        """Create from dictionary"""
        # Make a copy to avoid modifying the original
        data_copy = data.copy()
        
        # Handle field name change (for backward compatibility)
        if 'reply' in data_copy and 'reply_text' not in data_copy:
            data_copy['reply_text'] = data_copy['reply']
            del data_copy['reply']
        
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
                        
        return super(ModifiedICS213Form, cls).from_dict(data_copy)
    
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
        
    def add_reply(self, reply_text: str, recipient_signature: str) -> bool:
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
            
        self.reply_text = reply_text  # Use renamed field
        self.recipient_signature = recipient_signature
        
        self.state = FormState.REPLIED
        self.updated_at = datetime.now()
        return True

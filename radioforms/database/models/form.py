#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Form entity model representing a form in the system.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum, auto

from radioforms.database.models.base_model import TimestampedModel


class FormStatus(Enum):
    """Enum representing the status of a form."""
    DRAFT = "draft"
    FINALIZED = "finalized"
    SUBMITTED = "submitted"
    ARCHIVED = "archived"
    
    def __str__(self) -> str:
        """String representation of the enum value."""
        return self.value


class Form(TimestampedModel):
    """
    Form entity model representing an ICS form.
    
    Stores form metadata such as type, title, status, etc.
    The actual form content is stored in the FormVersion entity.
    """
    
    def __init__(self, id: Optional[int] = None, 
                incident_id: Optional[int] = None,
                form_type: str = "",
                title: str = "",
                creator_id: Optional[int] = None,
                status: FormStatus = FormStatus.DRAFT,
                created_at: Optional[datetime] = None,
                updated_at: Optional[datetime] = None):
        """
        Initialize a Form entity.
        
        Args:
            id: Form ID
            incident_id: ID of the incident this form belongs to (optional)
            form_type: Type of form (e.g., 'ICS-213', 'ICS-214')
            title: Form title
            creator_id: ID of the user who created the form (optional)
            status: Form status (default: DRAFT)
            created_at: Timestamp when the form was created
            updated_at: Timestamp when the form was last updated
        """
        super().__init__(id, created_at, updated_at)
        self.incident_id = incident_id
        self.form_type = form_type
        self.title = title
        self.creator_id = creator_id
        
        # If status is provided as a string, convert it to enum
        if isinstance(status, str):
            try:
                self.status = FormStatus(status)
            except ValueError:
                self.status = FormStatus.DRAFT
        else:
            self.status = status
        
    def finalize(self):
        """Mark the form as finalized."""
        self.status = FormStatus.FINALIZED
        self.touch()
        
    def submit(self):
        """Mark the form as submitted."""
        self.status = FormStatus.SUBMITTED
        self.touch()
        
    def archive(self):
        """Mark the form as archived."""
        self.status = FormStatus.ARCHIVED
        self.touch()
        
    def revert_to_draft(self):
        """Revert the form to draft status."""
        self.status = FormStatus.DRAFT
        self.touch()
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Form':
        """
        Create a Form instance from a dictionary.
        
        Args:
            data: Dictionary containing form data
            
        Returns:
            A new Form instance
        """
        # Handle status field
        if 'status' in data and isinstance(data['status'], str):
            try:
                data['status'] = FormStatus(data['status'])
            except ValueError:
                data['status'] = FormStatus.DRAFT
                
        # Convert string dates to datetime objects if needed
        for date_field in ['created_at', 'updated_at']:
            if isinstance(data.get(date_field), str):
                data[date_field] = datetime.fromisoformat(data[date_field])
                
        return super(Form, cls).from_dict(data)
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the form to a dictionary.
        
        Returns:
            Dictionary representation of the form
        """
        data = super().to_dict()
        
        # Convert status enum to string
        if 'status' in data and isinstance(data['status'], FormStatus):
            data['status'] = data['status'].value
            
        return data
        
    def __str__(self) -> str:
        """
        Return a string representation of the Form.
        
        Returns:
            String representation
        """
        return f"{self.form_type}: {self.title} ({self.status})"

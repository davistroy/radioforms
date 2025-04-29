#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FormVersion entity model representing a version of a form's content.
"""

from typing import Optional, Dict, Any, Union
from datetime import datetime
import json

from radioforms.database.models.base_model import TimestampedModel


class FormVersion(TimestampedModel):
    """
    FormVersion entity model representing a version of a form's content.
    
    Stores the actual content of a form at a specific version, enabling
    version history tracking.
    """
    
    def __init__(self, id: Optional[int] = None, 
                form_id: int = 0,
                version_number: int = 1,
                content: Union[str, Dict[str, Any]] = "",
                created_by: Optional[int] = None,
                created_at: Optional[datetime] = None):
        """
        Initialize a FormVersion entity.
        
        Args:
            id: FormVersion ID
            form_id: ID of the form this version belongs to
            version_number: Sequential version number (1-based)
            content: JSON content of the form (as string or dict)
            created_by: ID of the user who created this version
            created_at: Timestamp when this version was created
        """
        super().__init__(id, created_at, created_at)  # updated_at is same as created_at
        self.form_id = form_id
        self.version_number = version_number
        
        # Handle content field
        if isinstance(content, dict):
            self.content = json.dumps(content)
        else:
            self.content = content
            
        self.created_by = created_by
        
    def get_content_dict(self) -> Dict[str, Any]:
        """
        Get the form content as a dictionary.
        
        Returns:
            Dictionary containing the form content
        """
        if not self.content:
            return {}
            
        try:
            return json.loads(self.content)
        except json.JSONDecodeError:
            return {}
            
    def set_content_dict(self, content_dict: Dict[str, Any]):
        """
        Set the form content from a dictionary.
        
        Args:
            content_dict: Dictionary containing the form content
        """
        self.content = json.dumps(content_dict)
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FormVersion':
        """
        Create a FormVersion instance from a dictionary.
        
        Args:
            data: Dictionary containing form version data
            
        Returns:
            A new FormVersion instance
        """
        # Handle created_at field
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
                
        return super(FormVersion, cls).from_dict(data)
        
    def __str__(self) -> str:
        """
        Return a string representation of the FormVersion.
        
        Returns:
            String representation
        """
        return f"Form #{self.form_id} Version {self.version_number}"

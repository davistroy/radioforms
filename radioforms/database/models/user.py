#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
User entity model representing a user in the system.
"""

from typing import Optional, Dict, Any
from datetime import datetime

from radioforms.database.models.base_model import TimestampedModel


class User(TimestampedModel):
    """
    User entity model representing a user in the system.
    
    Stores user information such as name, call sign, and last login time.
    """
    
    def __init__(self, id: Optional[int] = None, 
                name: str = "", 
                call_sign: Optional[str] = None,
                last_login: Optional[datetime] = None,
                created_at: Optional[datetime] = None,
                updated_at: Optional[datetime] = None):
        """
        Initialize a User entity.
        
        Args:
            id: User ID
            name: User's full name
            call_sign: User's call sign (optional)
            last_login: Timestamp of the user's last login (optional)
            created_at: Timestamp when the user was created
            updated_at: Timestamp when the user was last updated
        """
        super().__init__(id, created_at, updated_at)
        self.name = name
        self.call_sign = call_sign
        self.last_login = last_login
        
    def update_last_login(self):
        """Update the last_login timestamp to the current time."""
        self.last_login = datetime.now()
        self.touch()  # Also update the updated_at timestamp
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Create a User instance from a dictionary.
        
        Args:
            data: Dictionary containing user data
            
        Returns:
            A new User instance
        """
        # Convert string dates to datetime objects if needed
        if isinstance(data.get('last_login'), str):
            data['last_login'] = datetime.fromisoformat(data['last_login'])
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
            
        return super(User, cls).from_dict(data)
        
    def __str__(self) -> str:
        """
        Return a string representation of the User.
        
        Returns:
            String representation
        """
        if self.call_sign:
            return f"{self.name} ({self.call_sign})"
        return self.name

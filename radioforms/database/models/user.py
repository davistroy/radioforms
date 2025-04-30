#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
User model for the application.

This module defines the User model class which represents a user in the application.
"""

from typing import Optional, Dict, Any
from datetime import datetime


class User:
    """
    User model class.
    
    This class represents a user in the application.
    """
    
    def __init__(
        self,
        id: Optional[int] = None,
        name: str = "",
        call_sign: Optional[str] = None,
        last_login: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialize a User object.
        
        Args:
            id: User ID (None for new users)
            name: User's name
            call_sign: User's call sign (amateur radio)
            last_login: Last login time
            created_at: Creation time
            updated_at: Last update time
        """
        self.id = id
        self.name = name
        self.call_sign = call_sign
        self.last_login = last_login
        self.created_at = created_at
        self.updated_at = updated_at
        
    def __str__(self) -> str:
        """
        Get string representation of the user.
        
        Returns:
            String representation
        """
        return f"User(id={self.id}, name='{self.name}', call_sign='{self.call_sign}')"
        
    def __repr__(self) -> str:
        """
        Get debug representation of the user.
        
        Returns:
            Debug representation
        """
        return (f"User(id={self.id}, name='{self.name}', call_sign='{self.call_sign}', "
                f"last_login={self.last_login}, created_at={self.created_at}, "
                f"updated_at={self.updated_at})")
                
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert user to dictionary.
        
        Returns:
            Dictionary representation of the user
        """
        return {
            "id": self.id,
            "name": self.name,
            "call_sign": self.call_sign,
            "last_login": self.last_login,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Create a User from a dictionary.
        
        Args:
            data: Dictionary with user data
            
        Returns:
            User object
        """
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            call_sign=data.get("call_sign"),
            last_login=data.get("last_login"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )

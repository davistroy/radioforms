#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base model for database entities.
"""

from typing import Any, Dict, Optional
from datetime import datetime


class BaseModel:
    """
    Base class for all database entity models.
    
    Provides common functionality and attributes shared by all entity models.
    """
    
    def __init__(self, id: Optional[int] = None):
        """
        Initialize the base model.
        
        Args:
            id: Optional entity ID
        """
        self.id = id
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model to a dictionary.
        
        Returns:
            Dictionary representation of the model
        """
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):  # Skip private fields
                result[key] = value
        return result
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """
        Create a model instance from a dictionary.
        
        Args:
            data: Dictionary containing model data
            
        Returns:
            A new model instance
        """
        instance = cls()
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance


class TimestampedModel(BaseModel):
    """
    Base model with creation and update timestamps.
    
    Extends BaseModel with created_at and updated_at timestamps.
    """
    
    def __init__(self, id: Optional[int] = None, 
                created_at: Optional[datetime] = None,
                updated_at: Optional[datetime] = None):
        """
        Initialize the timestamped model.
        
        Args:
            id: Optional entity ID
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        super().__init__(id)
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or self.created_at
        
    def touch(self):
        """Update the updated_at timestamp to the current time."""
        self.updated_at = datetime.now()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Incident entity model representing an incident in the system.
"""

from typing import Optional, Dict, Any
from datetime import datetime

from radioforms.database.models.base_model import TimestampedModel


class Incident(TimestampedModel):
    """
    Incident entity model representing an emergency incident.
    
    Stores incident information such as name, description, and date range.
    """
    
    def __init__(self, id: Optional[int] = None, 
                name: str = "", 
                description: Optional[str] = None,
                start_date: Optional[datetime] = None,
                end_date: Optional[datetime] = None,
                created_at: Optional[datetime] = None,
                updated_at: Optional[datetime] = None):
        """
        Initialize an Incident entity.
        
        Args:
            id: Incident ID
            name: Incident name
            description: Incident description (optional)
            start_date: Start date of the incident (optional)
            end_date: End date of the incident, if closed (optional)
            created_at: Timestamp when the incident was created
            updated_at: Timestamp when the incident was last updated
        """
        super().__init__(id, created_at, updated_at)
        self.name = name
        self.description = description
        self.start_date = start_date or datetime.now()
        self.end_date = end_date
        
    def is_active(self) -> bool:
        """
        Check if the incident is currently active.
        
        Returns:
            True if the incident is active (no end date), False otherwise
        """
        return self.end_date is None
        
    def close(self, end_date: Optional[datetime] = None):
        """
        Close the incident by setting an end date.
        
        Args:
            end_date: End date to set (defaults to current time)
        """
        self.end_date = end_date or datetime.now()
        self.touch()
        
    def reopen(self):
        """Reopen a closed incident by clearing the end date."""
        self.end_date = None
        self.touch()
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Incident':
        """
        Create an Incident instance from a dictionary.
        
        Args:
            data: Dictionary containing incident data
            
        Returns:
            A new Incident instance
        """
        # Convert string dates to datetime objects if needed
        for date_field in ['start_date', 'end_date', 'created_at', 'updated_at']:
            if isinstance(data.get(date_field), str):
                data[date_field] = datetime.fromisoformat(data[date_field])
                
        return super(Incident, cls).from_dict(data)
        
    def __str__(self) -> str:
        """
        Return a string representation of the Incident.
        
        Returns:
            String representation
        """
        status = "Active" if self.is_active() else "Closed"
        return f"{self.name} ({status})"

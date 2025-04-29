#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Data Access Object for incident operations.

This module provides a DAO for interacting with incident data in the database.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from radioforms.database.dao.base_dao import BaseDAO
from radioforms.database.db_manager import DatabaseManager


class IncidentDAO(BaseDAO):
    """
    Data Access Object for incident operations.
    
    This class provides methods to create, read, update, and delete
    incident records in the database.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the incident DAO.
        
        Args:
            db_manager: Database manager instance
        """
        super().__init__(db_manager)
        self.table_name = 'incidents'
    
    def create(self, incident_data: Dict[str, Any]) -> Optional[int]:
        """
        Create a new incident record.
        
        Args:
            incident_data: Incident data dictionary
            
        Returns:
            Incident ID if successful, None otherwise
        """
        # Add timestamps if not present
        if 'created_at' not in incident_data:
            incident_data['created_at'] = datetime.now()
        if 'updated_at' not in incident_data:
            incident_data['updated_at'] = datetime.now()
        
        # Set start_date to now if not provided
        if 'start_date' not in incident_data or incident_data['start_date'] is None:
            incident_data['start_date'] = datetime.now()
        
        return super().create(incident_data)
    
    def update(self, incident_id: int, incident_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing incident record.
        
        Args:
            incident_id: Incident ID to update
            incident_data: Updated incident data dictionary
            
        Returns:
            Updated incident dictionary if successful, None otherwise
        """
        # Add updated timestamp if not present
        if 'updated_at' not in incident_data:
            incident_data['updated_at'] = datetime.now()
            
        return super().update(incident_id, incident_data)
    
    def get_by_id(self, incident_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an incident record by ID.
        
        Args:
            incident_id: Incident ID to retrieve
            
        Returns:
            Incident dictionary if found, None otherwise
        """
        return super().get_by_id(incident_id)
    
    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get an incident record by name.
        
        Args:
            name: Incident name to search for
            
        Returns:
            Incident dictionary if found, None otherwise
        """
        query = "SELECT * FROM incidents WHERE name = ? LIMIT 1"
        cursor = self.db_manager.execute(query, (name,))
        result = cursor.fetchone()
        
        return dict(result) if result else None
    
    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all incident records.
        
        Returns:
            List of incident dictionaries
        """
        query = "SELECT * FROM incidents ORDER BY created_at DESC"
        cursor = self.db_manager.execute(query)
        results = cursor.fetchall()
        
        return [dict(row) for row in results]
    
    def get_active(self) -> List[Dict[str, Any]]:
        """
        Get all active incidents (no end_date).
        
        Returns:
            List of active incident dictionaries
        """
        query = "SELECT * FROM incidents WHERE end_date IS NULL ORDER BY created_at DESC"
        cursor = self.db_manager.execute(query)
        results = cursor.fetchall()
        
        return [dict(row) for row in results]
    
    def delete(self, incident_id: int) -> bool:
        """
        Delete an incident record.
        
        Args:
            incident_id: Incident ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        return super().delete(incident_id)
    
    def close_incident(self, incident_id: int) -> bool:
        """
        Close an incident by setting its end_date.
        
        Args:
            incident_id: Incident ID to close
            
        Returns:
            True if successful, False otherwise
        """
        update_data = {
            'end_date': datetime.now(),
            'updated_at': datetime.now()
        }
        
        result = self.update(incident_id, update_data)
        return result is not None
    
    def get_forms_for_incident(self, incident_id: int) -> List[Dict[str, Any]]:
        """
        Get all forms associated with an incident.
        
        Args:
            incident_id: Incident ID to get forms for
            
        Returns:
            List of form dictionaries
        """
        query = """
        SELECT f.* FROM forms f
        WHERE f.incident_id = ?
        ORDER BY f.created_at DESC
        """
        
        cursor = self.db_manager.execute(query, (incident_id,))
        results = cursor.fetchall()
        
        return [dict(row) for row in results]

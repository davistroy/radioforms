#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Data Access Object for incident operations.

This module provides a DAO for interacting with incident data in the database.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union, TypeVar, Generic, cast

from radioforms.database.dao.base_dao import BaseDAO, DAOException
from radioforms.database.models.incident import Incident
from radioforms.database.db_manager import DatabaseManager
from radioforms.database.dao.dao_cache_mixin import DAOCacheMixin


class IncidentDAO(DAOCacheMixin[Incident], BaseDAO[Incident]):
    """
    Data Access Object for incident operations.
    
    This class provides methods to create, read, update, and delete
    incident records in the database.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the incident DAO with a database manager.
        
        This constructor sets up the DAO with the appropriate table name and primary key column.
        
        Args:
            db_manager: Database manager instance that provides database connection and operations
        """
        BaseDAO.__init__(self, db_manager)
        DAOCacheMixin.__init__(self)
        self.table_name = 'incidents'
        self.pk_column = 'id'
    
    def _row_to_entity(self, row: Dict[str, Any]) -> Incident:
        """
        Convert a database row to an Incident entity object.
        
        Args:
            row: Dictionary containing column names and values from the database
            
        Returns:
            A properly initialized Incident entity with all attributes set from the row data
        """
        return Incident(
            id=row.get('id'),
            name=row.get('name', ''),
            description=row.get('description'),
            start_date=row.get('start_date'),
            end_date=row.get('end_date'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    def _entity_to_values(self, entity: Incident) -> Dict[str, Any]:
        """
        Convert an Incident entity to a dictionary of database column values.
        
        Args:
            entity: The Incident entity object to convert
            
        Returns:
            Dictionary containing column names and their corresponding values from the entity
        """
        values = {
            'name': entity.name,
            'description': entity.description,
            'start_date': entity.start_date,
            'end_date': entity.end_date,
            'created_at': entity.created_at,
            'updated_at': entity.updated_at
        }
        
        if entity.id is not None:
            values['id'] = entity.id
            
        return values
    
    def create(self, incident: Union[Incident, Dict[str, Any]]) -> int:
        """
        Create a new incident record in the database.
        
        Args:
            incident: Incident entity object or data dictionary containing incident attributes
            
        Returns:
            The ID (primary key) of the newly created incident record
            
        Examples:
            >>> incident = Incident(name="Wildfire Response", description="Forest fire response")
            >>> incident_id = incident_dao.create(incident)
            
            >>> incident_data = {"name": "Flood Response", "description": "River flooding"}
            >>> incident_id = incident_dao.create(incident_data)
        """
        # Convert to dictionary if it's an entity
        incident_data = incident if isinstance(incident, dict) else self._entity_to_values(incident)
        
        # Add timestamps if not present
        now = datetime.now()
        if 'created_at' not in incident_data or incident_data['created_at'] is None:
            incident_data['created_at'] = now
        if 'updated_at' not in incident_data or incident_data['updated_at'] is None:
            incident_data['updated_at'] = now
        
        # Set start_date to now if not provided
        if 'start_date' not in incident_data or incident_data['start_date'] is None:
            incident_data['start_date'] = now
        
        return super().create(incident_data)
    
    def find_by_name(self, name: str, as_dict: bool = False) -> Union[List[Incident], List[Dict[str, Any]]]:
        """
        Find incident records by partial name match using SQL LIKE operator.
        
        Args:
            name: Incident name or partial name to search for (will be wrapped in % wildcards)
            as_dict: When True, return dictionaries instead of entity objects
            
        Returns:
            List of matching incidents as either entity objects or dictionaries
            
        Examples:
            >>> incidents = incident_dao.find_by_name("fire")  # Finds "Wildfire", "Fire Drill", etc.
            >>> dict_incidents = incident_dao.find_by_name("response", as_dict=True)
        """
        query = "SELECT * FROM incidents WHERE name LIKE ?"
        cursor = self.db_manager.execute(query, (f"%{name}%",))
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def find_all(self, as_dict: bool = False, order_by: str = "created_at DESC") -> Union[List[Incident], List[Dict[str, Any]]]:
        """
        Find all incident records in the database with customizable sorting.
        
        Args:
            as_dict: When True, return dictionaries instead of entity objects
            order_by: SQL ORDER BY clause specifying how to sort the results
                      (default: "created_at DESC" sorts by creation date, newest first)
            
        Returns:
            List of all incidents in the database as either entity objects or dictionaries
            
        Examples:
            >>> all_incidents = incident_dao.find_all()
            >>> incidents_by_name = incident_dao.find_all(order_by="name ASC")
            >>> incidents_dict = incident_dao.find_all(as_dict=True)
        """
        query = f"SELECT * FROM incidents ORDER BY {order_by}"
        cursor = self.db_manager.execute(query)
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def find_active(self, as_dict: bool = False, order_by: str = "created_at DESC") -> Union[List[Incident], List[Dict[str, Any]]]:
        """
        Find all active incidents (those with no end_date) with customizable sorting.
        
        Args:
            as_dict: When True, return dictionaries instead of entity objects
            order_by: SQL ORDER BY clause specifying how to sort the results
                      (default: "created_at DESC" sorts by creation date, newest first)
            
        Returns:
            List of active incidents as either entity objects or dictionaries
            
        Examples:
            >>> active_incidents = incident_dao.find_active()
            >>> active_dict = incident_dao.find_active(as_dict=True)
            >>> active_by_name = incident_dao.find_active(order_by="name ASC")
        """
        query = f"SELECT * FROM incidents WHERE end_date IS NULL ORDER BY {order_by}"
        cursor = self.db_manager.execute(query)
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def set_incident_closed(self, incident_id: int) -> bool:
        """
        Close an incident by setting its end_date to the current time.
        
        Args:
            incident_id: The database ID of the incident to close
            
        Returns:
            True if the incident was successfully closed, False otherwise
            
        Example:
            >>> success = incident_dao.set_incident_closed(5)
            >>> if success:
            >>>     print("Incident #5 was successfully closed")
        """
        update_data = {
            'end_date': datetime.now(),
            'updated_at': datetime.now()
        }
        
        return self.update(incident_id, update_data)
    
    def set_incident_active(self, incident_id: int) -> bool:
        """
        Reopen a closed incident by clearing its end_date field.
        
        Args:
            incident_id: The database ID of the incident to reopen
            
        Returns:
            True if the incident was successfully reopened, False otherwise
            
        Example:
            >>> success = incident_dao.set_incident_active(5)
            >>> if success:
            >>>     print("Incident #5 was successfully reopened")
        """
        update_data = {
            'end_date': None,
            'updated_at': datetime.now()
        }
        
        return self.update(incident_id, update_data)
    
    def find_forms_by_incident(self, incident_id: int, as_dict: bool = True) -> Union[List[Dict[str, Any]], List[Any]]:
        """
        Find all forms associated with a specific incident.
        
        Args:
            incident_id: The database ID of the incident to find forms for
            as_dict: When True, return dictionaries (default is True)
            
        Returns:
            List of form data, ordered by creation date (newest first)
            
        Example:
            >>> forms = incident_dao.find_forms_by_incident(5)
            >>> print(f"Found {len(forms)} forms for incident #5")
            >>> for form in forms:
            >>>     print(f"Form ID: {form['id']}, Type: {form['form_type']}")
        """
        query = """
        SELECT f.* FROM forms f
        WHERE f.incident_id = ?
        ORDER BY f.created_at DESC
        """
        
        cursor = self.db_manager.execute(query, (incident_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def find_incident_stats(self) -> Dict[str, int]:
        """
        Get aggregated statistics about incidents in the database.
        
        Returns:
            Dictionary with statistics including total, active, and closed incident counts
            
        Example:
            >>> stats = incident_dao.find_incident_stats()
            >>> print(f"System has {stats['total']} incidents ({stats['active']} active, {stats['closed']} closed)")
        """
        # Get all incidents
        all_incidents = self.find_all()
        total = len(all_incidents)
        
        # Count active incidents (those with is_active() == True)
        active = sum(1 for incident in all_incidents if incident.is_active())
        
        return {
            'total': total,
            'active': active,
            'closed': total - active
        }

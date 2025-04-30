#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Data Access Object for incident operations.

This module provides a DAO for interacting with incident data in the database.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union, overload

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
        
        This method maps database column values to appropriate attributes of the Incident model,
        correctly handling optional fields and data type conversions.
        
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
        
        This method maps the Incident object's attributes to their corresponding
        database column names, making the object ready for storage in the database.
        The dictionary keys match the column names in the incidents table.
        
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
    
    @overload
    def create(self, incident: Incident) -> int:
        ...
    
    @overload
    def create(self, incident_data: Dict[str, Any]) -> int:
        ...
    
    def create(self, incident: Union[Incident, Dict[str, Any]]) -> int:
        """
        Create a new incident record in the database.
        
        This method supports both entity objects and dictionaries as input.
        It ensures all required fields are present, automatically setting
        timestamps and start_date if not provided.
        
        Args:
            incident: Incident entity object or data dictionary containing incident attributes
            
        Returns:
            The ID (primary key) of the newly created incident record
            
        Example:
            >>> incident = Incident(name="Wildfire Response", description="Forest fire response")
            >>> incident_id = incident_dao.create(incident)
            
            Or with a dictionary:
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
    
    @overload
    def find_by_name(self, name: str) -> List[Incident]:
        ...
    
    @overload
    def find_by_name(self, name: str, as_dict: bool = False) -> List[Dict[str, Any]]:
        ...
    
    def find_by_name(self, name: str, as_dict: bool = False) -> Union[List[Incident], List[Dict[str, Any]]]:
        """
        Find incident records by partial name match using SQL LIKE operator.
        
        This method performs a case-insensitive search for incidents whose names
        contain the provided search string. It's useful for implementing search
        functionality in the application.
        
        Args:
            name: Incident name or partial name to search for (will be wrapped in % wildcards)
            as_dict: When True, return dictionaries instead of entity objects
            
        Returns:
            List of matching incidents (as objects or dictionaries based on as_dict parameter)
            
        Example:
            >>> incidents = incident_dao.find_by_name("fire")  # Finds "Wildfire", "Fire Drill", etc.
            >>> dict_incidents = incident_dao.find_by_name("response", as_dict=True)
        """
        query = "SELECT * FROM incidents WHERE name LIKE ?"
        cursor = self.db_manager.execute(query, (f"%{name}%",))
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
    
    @overload
    def find_all_incidents(self, order_by: str = "created_at DESC") -> List[Incident]:
        ...
    
    @overload
    def find_all_incidents(self, order_by: str = "created_at DESC", as_dict: bool = False) -> List[Dict[str, Any]]:
        ...
    
    def find_all_incidents(self, order_by: str = "created_at DESC", 
                         as_dict: bool = False) -> Union[List[Incident], List[Dict[str, Any]]]:
        """
        Find all incident records in the database with customizable sorting.
        
        This method retrieves all incidents regardless of their status.
        Results can be ordered by any valid column in the incidents table.
        
        Args:
            order_by: SQL ORDER BY clause specifying how to sort the results
                      (default: "created_at DESC" sorts by creation date, newest first)
            as_dict: When True, return dictionaries instead of entity objects
            
        Returns:
            List of all incidents in the database (as objects or dictionaries based on as_dict)
            
        Example:
            >>> all_incidents = incident_dao.find_all_incidents()
            >>> incidents_by_name = incident_dao.find_all_incidents("name ASC")
            >>> incidents_dict = incident_dao.find_all_incidents(as_dict=True)
        """
        query = f"SELECT * FROM incidents ORDER BY {order_by}"
        cursor = self.db_manager.execute(query)
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
    
    @overload
    def find_active_incidents(self, order_by: str = "created_at DESC") -> List[Incident]:
        ...
    
    @overload
    def find_active_incidents(self, order_by: str = "created_at DESC", as_dict: bool = False) -> List[Dict[str, Any]]:
        ...
    
    def find_active_incidents(self, order_by: str = "created_at DESC", 
                            as_dict: bool = False) -> Union[List[Incident], List[Dict[str, Any]]]:
        """
        Find all active incidents (those with no end_date) with customizable sorting.
        
        An incident is considered "active" when its end_date is NULL in the database.
        This is useful for displaying only current/ongoing incidents in the application.
        
        Args:
            order_by: SQL ORDER BY clause specifying how to sort the results
                     (default: "created_at DESC" sorts by creation date, newest first)
            as_dict: When True, return dictionaries instead of entity objects
            
        Returns:
            List of active incidents (as objects or dictionaries based on as_dict parameter)
            
        Example:
            >>> active_incidents = incident_dao.find_active_incidents()
            >>> active_dict = incident_dao.find_active_incidents(as_dict=True)
            >>> active_by_name = incident_dao.find_active_incidents("name ASC")
        """
        query = f"SELECT * FROM incidents WHERE end_date IS NULL ORDER BY {order_by}"
        cursor = self.db_manager.execute(query)
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def close_incident(self, incident_id: int) -> bool:
        """
        Close an incident by setting its end_date to the current time.
        
        This method marks an incident as closed/completed by setting its end_date
        to the current timestamp. Closed incidents will no longer appear in 
        active incident lists but remain in the database for historical records.
        
        Args:
            incident_id: The database ID of the incident to close
            
        Returns:
            True if the incident was successfully closed, False if it wasn't found or couldn't be updated
            
        Example:
            >>> success = incident_dao.close_incident(5)
            >>> if success:
            >>>     print("Incident #5 was successfully closed")
        """
        update_data = {
            'end_date': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Now using the two-parameter form of update
        return self.update(incident_id, update_data)
    
    def reopen_incident(self, incident_id: int) -> bool:
        """
        Reopen a closed incident by clearing its end_date field.
        
        This method reverses the closing of an incident by setting its end_date
        to NULL in the database. This makes the incident appear in active incident
        lists again. Use this when an incident was closed prematurely or needs
        to be reopened for additional work.
        
        Args:
            incident_id: The database ID of the incident to reopen
            
        Returns:
            True if the incident was successfully reopened, False if it wasn't found or couldn't be updated
            
        Example:
            >>> success = incident_dao.reopen_incident(5)
            >>> if success:
            >>>     print("Incident #5 was successfully reopened")
        """
        update_data = {
            'end_date': None,
            'updated_at': datetime.now()
        }
        
        # Now using the two-parameter form of update
        return self.update(incident_id, update_data)
    
    def find_forms_for_incident(self, incident_id: int, as_dict: bool = True) -> List[Dict[str, Any]]:
        """
        Find all forms associated with a specific incident.
        
        This method performs a relational query to find all forms that have
        the specified incident ID. Results are returned in descending order
        by creation date (newest first).
        
        Args:
            incident_id: The database ID of the incident to find forms for
            as_dict: When True, return dictionaries (default is True)
            
        Returns:
            List of form data as dictionaries, ordered by creation date (newest first)
            
        Example:
            >>> forms = incident_dao.find_forms_for_incident(5)
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
    
    def get_incident_stats(self) -> Dict[str, int]:
        """
        Get aggregated statistics about incidents in the database.
        
        This method calculates summary statistics for all incidents, including
        total count, active count (no end_date), and closed count (with end_date).
        It's useful for dashboard displays and system reporting.
        
        Returns:
            Dictionary with the following keys:
            - 'total': Total number of incidents in the database
            - 'active': Number of active (ongoing) incidents
            - 'closed': Number of closed (completed) incidents
            
        Example:
            >>> stats = incident_dao.get_incident_stats()
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

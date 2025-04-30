#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base DAO (Data Access Object) abstract class.

This module provides the base DAO class that all concrete DAO implementations
should extend. It defines the standard interface for database operations.
"""

import logging
import sqlite3
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Generic, Union, cast, overload
from radioforms.database.db_manager import DatabaseManager


class DAOException(Exception):
    """Exception raised for errors in the DAO layer."""
    pass

# Configure logger
logger = logging.getLogger(__name__)

# Type variable for the entity type
T = TypeVar('T')


class BaseDAO(Generic[T], ABC):
    """
    Base DAO (Data Access Object) abstract class.
    
    This class defines the standard interface for database operations
    and provides common implementation for basic CRUD operations.
    
    Type Parameters:
        T: The entity type for this DAO
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the DAO with a database manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.table_name = None  # Override in subclass
        self.pk_column = 'id'   # Default primary key column name, override if different
        
    @abstractmethod
    def _row_to_entity(self, row: Dict[str, Any]) -> T:
        """
        Convert a database row to an entity object.
        
        Args:
            row: Database row as a dictionary
            
        Returns:
            Entity object
        """
        pass
        
    @abstractmethod
    def _entity_to_values(self, entity: T) -> Dict[str, Any]:
        """
        Convert an entity object to a dictionary of column values.
        
        Args:
            entity: Entity object
            
        Returns:
            Dictionary of column values
        """
        pass
        
    def _entity_or_dict_to_values(self, entity: Union[T, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convert an entity object or dictionary to a dictionary of column values.
        
        Args:
            entity: Entity object or dictionary
            
        Returns:
            Dictionary of column values
        """
        if isinstance(entity, dict):
            return entity
        return self._entity_to_values(entity)
        
    def create(self, entity: Union[T, Dict[str, Any]]) -> int:
        """
        Create a new entity in the database.
        
        Args:
            entity: Entity object or dictionary to create
            
        Returns:
            ID of the created entity
        """
        if self.table_name is None:
            raise ValueError("table_name must be set in the DAO subclass")
            
        # Convert entity to values
        values = self._entity_or_dict_to_values(entity)
        
        # Remove None values
        values = {k: v for k, v in values.items() if v is not None}
        
        # Remove primary key if it's None or not in values
        values.pop(self.pk_column, None)
        
        # Build the query
        columns = list(values.keys())
        placeholders = ['?'] * len(columns)
        parameters = list(values.values())
        
        query = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        
        # Execute the query
        cursor = self.db_manager.execute(query, parameters)
        
        # Get the last inserted ID
        entity_id = cursor.lastrowid
        
        # Commit the transaction
        self.db_manager.commit()
        
        return entity_id
        
    def update(self, entity_or_id: Union[T, Dict[str, Any], Any], update_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an existing entity in the database.
        
        This method supports two calling patterns:
        1. update(entity) - where entity is an object or dict with an ID
        2. update(entity_id, update_data) - where entity_id is the ID and update_data is a dict of values
        
        Args:
            entity_or_id: Entity object, dictionary, or entity ID
            update_data: If entity_or_id is an ID, this contains the update values
            
        Returns:
            True if the update was successful, False otherwise
        """
        if self.table_name is None:
            raise ValueError("table_name must be set in the DAO subclass")
            
        if update_data is not None:
            # Called as update(entity_id, update_data)
            entity_id = entity_or_id
            values = update_data
        else:
            # Called as update(entity)
            # Convert entity to values
            values = self._entity_or_dict_to_values(entity_or_id)
            
            # Check if primary key is present
            entity_id = values.get(self.pk_column)
            if entity_id is None:
                raise ValueError(f"Primary key ({self.pk_column}) must be present for update")
                
            # Remove primary key from values
            values.pop(self.pk_column, None)
        
        # We need to handle SQL NULL values differently than just omitting the field
        # For SQL NULL, we need to keep the field in the query but use NULL in SQL
        set_parts = []
        parameters = []
        
        for column, value in values.items():
            if value is None:
                # Use SQL NULL for None values
                set_parts.append(f"{column} = NULL")
            else:
                # Use parameter placeholder for non-None values
                set_parts.append(f"{column} = ?")
                parameters.append(value)
        
        # Add the entity ID to parameters
        parameters.append(entity_id)
        
        # Build the query
        set_clause = ', '.join(set_parts)
        
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {self.pk_column} = ?"
        
        # Execute the query
        cursor = self.db_manager.execute(query, parameters)
        
        # Commit the transaction
        self.db_manager.commit()
        
        return cursor.rowcount > 0
        
    def delete(self, entity_id: Any) -> bool:
        """
        Delete an entity from the database.
        
        Args:
            entity_id: ID of the entity to delete
            
        Returns:
            True if the delete was successful, False otherwise
        """
        if self.table_name is None:
            raise ValueError("table_name must be set in the DAO subclass")
            
        # Build the query
        query = f"DELETE FROM {self.table_name} WHERE {self.pk_column} = ?"
        
        # Execute the query
        cursor = self.db_manager.execute(query, [entity_id])
        
        # Commit the transaction
        self.db_manager.commit()
        
        return cursor.rowcount > 0
        
    def find_by_id(self, entity_id: Any, as_dict: bool = False) -> Optional[Union[T, Dict[str, Any]]]:
        """
        Find an entity by its ID.
        
        Args:
            entity_id: ID of the entity to find
            as_dict: Whether to return a dictionary instead of an entity object
            
        Returns:
            Entity object, dictionary, or None if not found
        """
        if self.table_name is None:
            raise ValueError("table_name must be set in the DAO subclass")
            
        # Build the query
        query = f"SELECT * FROM {self.table_name} WHERE {self.pk_column} = ?"
        
        # Execute the query
        cursor = self.db_manager.execute(query, [entity_id])
        
        # Get the result
        row = cursor.fetchone()
        
        if row is None:
            return None
            
        # Convert row to entity or return as dict
        if as_dict:
            return dict(row)
        else:
            return self._row_to_entity(dict(row))
            
    def find_all(self, as_dict: bool = False) -> List[Union[T, Dict[str, Any]]]:
        """
        Find all entities.
        
        Args:
            as_dict: Whether to return dictionaries instead of entity objects
            
        Returns:
            List of entity objects or dictionaries
        """
        if self.table_name is None:
            raise ValueError("table_name must be set in the DAO subclass")
            
        # Build the query
        query = f"SELECT * FROM {self.table_name}"
        
        # Execute the query
        cursor = self.db_manager.execute(query)
        
        # Get the results
        rows = cursor.fetchall()
        
        # Convert rows to entities or return as dicts
        if as_dict:
            return [dict(row) for row in rows]
        else:
            return [self._row_to_entity(dict(row)) for row in rows]
            
    def find_by_field(self, field: str, value: Any, as_dict: bool = False) -> List[Union[T, Dict[str, Any]]]:
        """
        Find entities by a field value.
        
        Args:
            field: Field name to search by
            value: Value to match
            as_dict: Whether to return dictionaries instead of entity objects
            
        Returns:
            List of entity objects or dictionaries
        """
        if self.table_name is None:
            raise ValueError("table_name must be set in the DAO subclass")
            
        # Build the query
        query = f"SELECT * FROM {self.table_name} WHERE {field} = ?"
        
        # Execute the query
        cursor = self.db_manager.execute(query, [value])
        
        # Get the results
        rows = cursor.fetchall()
        
        # Convert rows to entities or return as dicts
        if as_dict:
            return [dict(row) for row in rows]
        else:
            return [self._row_to_entity(dict(row)) for row in rows]
            
    def find_by_fields(self, field_dict: Dict[str, Any], as_dict: bool = False) -> List[Union[T, Dict[str, Any]]]:
        """
        Find entities by multiple field values.
        
        Args:
            field_dict: Dictionary of field names and values to match
            as_dict: Whether to return dictionaries instead of entity objects
            
        Returns:
            List of entity objects or dictionaries
        """
        if self.table_name is None:
            raise ValueError("table_name must be set in the DAO subclass")
            
        # Build the query
        where_clause = ' AND '.join([f"{field} = ?" for field in field_dict.keys()])
        parameters = list(field_dict.values())
        
        query = f"SELECT * FROM {self.table_name} WHERE {where_clause}"
        
        # Execute the query
        cursor = self.db_manager.execute(query, parameters)
        
        # Get the results
        rows = cursor.fetchall()
        
        # Convert rows to entities or return as dicts
        if as_dict:
            return [dict(row) for row in rows]
        else:
            return [self._row_to_entity(dict(row)) for row in rows]
            
    def count(self, where_clause: Optional[str] = None, params: Optional[List[Any]] = None) -> int:
        """
        Count entities with optional filtering.
        
        Args:
            where_clause: Optional WHERE clause for filtering
            params: Parameters for the WHERE clause
            
        Returns:
            Count of matching entities
        """
        if self.table_name is None:
            raise ValueError("table_name must be set in the DAO subclass")
            
        # Build the query
        query = f"SELECT COUNT(*) AS count FROM {self.table_name}"
        
        if where_clause:
            query += f" WHERE {where_clause}"
            
        # Execute the query
        cursor = self.db_manager.execute(query, params or [])
        
        # Get the result
        row = cursor.fetchone()
        
        return row['count'] if row else 0
        
    def exists(self, entity_id: Any) -> bool:
        """
        Check if an entity exists by ID.
        
        Args:
            entity_id: ID of the entity to check
            
        Returns:
            True if the entity exists, False otherwise
        """
        return self.find_by_id(entity_id) is not None
        
    def execute(self, query: str, params: Optional[List[Any]] = None) -> sqlite3.Cursor:
        """
        Execute a custom query.
        
        Args:
            query: SQL query to execute
            params: Parameters for the query
            
        Returns:
            Database cursor for the executed query
        """
        return self.db_manager.execute(query, params or [])

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base Data Access Object (DAO) for database operations.
"""

from typing import Any, Dict, List, Optional, Tuple, TypeVar, Generic, Union
import sqlite3
from pathlib import Path

from radioforms.database.db_manager import DatabaseManager

# Generic type for entity objects
T = TypeVar('T')

class BaseDAO(Generic[T]):
    """
    Base Data Access Object providing common database operations.
    
    This abstract class provides the foundation for entity-specific DAOs
    with generalized CRUD operations and transaction support.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the DAO with a database manager.
        
        Args:
            db_manager: Database manager instance for database operations
        """
        self.db_manager = db_manager
        self.table_name = ""  # Must be set by subclasses
        self.pk_column = "id"  # Default primary key column name
        
    def find_by_id(self, entity_id: int) -> Optional[T]:
        """
        Find an entity by its ID.
        
        Args:
            entity_id: The entity's primary key value
            
        Returns:
            The entity if found, None otherwise
        """
        query = f"SELECT * FROM {self.table_name} WHERE {self.pk_column} = ?"
        cursor = self.db_manager.execute(query, (entity_id,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_entity(dict(row))
        return None
        
    def find_all(self, limit: int = 1000, offset: int = 0) -> List[T]:
        """
        Find all entities with optional pagination.
        
        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip
            
        Returns:
            List of entities
        """
        query = f"SELECT * FROM {self.table_name} LIMIT ? OFFSET ?"
        cursor = self.db_manager.execute(query, (limit, offset))
        
        return [self._row_to_entity(dict(row)) for row in cursor.fetchall()]
        
    def find_by_filter(self, filters: Dict[str, Any], 
                     order_by: Optional[str] = None, 
                     limit: int = 1000, 
                     offset: int = 0) -> List[T]:
        """
        Find entities matching the given filters.
        
        Args:
            filters: Dictionary of column names and values to filter by
            order_by: Optional column name to order by (can include ASC/DESC)
            limit: Maximum number of entities to return
            offset: Number of entities to skip
            
        Returns:
            List of entities matching the filters
        """
        # Build WHERE clause from filters
        where_clauses = []
        params = []
        
        for column, value in filters.items():
            where_clauses.append(f"{column} = ?")
            params.append(value)
            
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Build query
        query = f"SELECT * FROM {self.table_name} WHERE {where_clause}"
        
        # Add ORDER BY if specified
        if order_by:
            query += f" ORDER BY {order_by}"
            
        # Add LIMIT and OFFSET
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        # Execute query
        cursor = self.db_manager.execute(query, params)
        
        return [self._row_to_entity(dict(row)) for row in cursor.fetchall()]
        
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities matching the given filters.
        
        Args:
            filters: Optional dictionary of column names and values to filter by
            
        Returns:
            Count of matching entities
        """
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        params = []
        
        # Add WHERE clause if filters are provided
        if filters:
            where_clauses = []
            for column, value in filters.items():
                where_clauses.append(f"{column} = ?")
                params.append(value)
                
            where_clause = " AND ".join(where_clauses)
            query += f" WHERE {where_clause}"
            
        # Execute query
        cursor = self.db_manager.execute(query, params)
        result = cursor.fetchone()
        
        return result[0] if result else 0
        
    def create(self, entity: T) -> int:
        """
        Create a new entity in the database.
        
        Args:
            entity: The entity to create
            
        Returns:
            The ID of the created entity
        """
        # Convert entity to column values
        values = self._entity_to_values(entity)
        
        # Remove the ID column if it's None or 0
        if self.pk_column in values and (values[self.pk_column] is None or values[self.pk_column] == 0):
            del values[self.pk_column]
            
        # Build SQL query
        columns = ", ".join(values.keys())
        placeholders = ", ".join(["?"] * len(values))
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        
        # Execute query
        cursor = self.db_manager.execute(query, tuple(values.values()))
        self.db_manager.commit()
        
        return cursor.lastrowid
        
    def update(self, entity: T) -> bool:
        """
        Update an existing entity in the database.
        
        Args:
            entity: The entity to update
            
        Returns:
            True if the entity was updated, False otherwise
        """
        # Convert entity to column values
        values = self._entity_to_values(entity)
        
        # Ensure ID exists
        if self.pk_column not in values or values[self.pk_column] is None:
            raise ValueError(f"Cannot update entity without {self.pk_column}")
            
        # Extract ID and remove from values
        entity_id = values[self.pk_column]
        del values[self.pk_column]
        
        # Build SQL query
        set_clause = ", ".join([f"{column} = ?" for column in values.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {self.pk_column} = ?"
        
        # Execute query
        params = list(values.values())
        params.append(entity_id)
        cursor = self.db_manager.execute(query, params)
        self.db_manager.commit()
        
        return cursor.rowcount > 0
        
    def delete(self, entity_id: int) -> bool:
        """
        Delete an entity from the database.
        
        Args:
            entity_id: The ID of the entity to delete
            
        Returns:
            True if the entity was deleted, False otherwise
        """
        query = f"DELETE FROM {self.table_name} WHERE {self.pk_column} = ?"
        cursor = self.db_manager.execute(query, (entity_id,))
        self.db_manager.commit()
        
        return cursor.rowcount > 0
        
    def delete_by_filter(self, filters: Dict[str, Any]) -> int:
        """
        Delete entities matching the given filters.
        
        Args:
            filters: Dictionary of column names and values to filter by
            
        Returns:
            Number of entities deleted
        """
        # Build WHERE clause from filters
        where_clauses = []
        params = []
        
        for column, value in filters.items():
            where_clauses.append(f"{column} = ?")
            params.append(value)
            
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Build query
        query = f"DELETE FROM {self.table_name} WHERE {where_clause}"
        
        # Execute query
        cursor = self.db_manager.execute(query, params)
        self.db_manager.commit()
        
        return cursor.rowcount
        
    def begin_transaction(self):
        """Begin a database transaction."""
        return self.db_manager.transaction()
        
    def _row_to_entity(self, row: Dict[str, Any]) -> T:
        """
        Convert a database row to an entity object.
        
        This method must be implemented by subclasses.
        
        Args:
            row: Dictionary containing column names and values
            
        Returns:
            An entity object
        """
        raise NotImplementedError("Subclasses must implement _row_to_entity")
        
    def _entity_to_values(self, entity: T) -> Dict[str, Any]:
        """
        Convert an entity object to a dictionary of column values.
        
        This method must be implemented by subclasses.
        
        Args:
            entity: The entity object
            
        Returns:
            Dictionary containing column names and values
        """
        raise NotImplementedError("Subclasses must implement _entity_to_values")


class DAOException(Exception):
    """Exception raised for DAO-related errors."""
    
    def __init__(self, message: str, cause: Optional[Exception] = None):
        """
        Initialize with a message and optional cause.
        
        Args:
            message: Error message
            cause: The exception that caused this error, if any
        """
        self.message = message
        self.cause = cause
        super().__init__(message)

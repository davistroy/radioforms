#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Extended BaseDAO with bulk operation capabilities.

This module provides enhanced BaseDAO functionality for performing efficient batch
operations on multiple entities in a single transaction.
"""

from typing import Any, Dict, List, Optional, Tuple, TypeVar, Generic, Union, Iterable
from typing import cast, Type, overload, Callable, Set
import sqlite3
from datetime import datetime
import itertools

from radioforms.database.dao.base_dao import BaseDAO, DAOException
from radioforms.database.db_manager import DatabaseManager

# Generic type for entity objects
T = TypeVar('T')

class BulkOperationsBaseDAO(BaseDAO[T]):
    """
    Extended BaseDAO with bulk operation capabilities.
    
    This class extends the BaseDAO to provide efficient bulk operations for 
    creating, updating, and deleting multiple entities in a single transaction,
    significantly improving performance for batch operations.
    
    Type Parameters:
        T: The entity type this DAO manages
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the DAO with a database manager.
        
        Args:
            db_manager: Database manager instance for database operations
        """
        super().__init__(db_manager)
        self._batch_size = 100  # Default batch size for chunking large operations
    
    # -------------------------------------------------------------------------
    # Bulk Creation Operations
    # -------------------------------------------------------------------------
    
    @overload
    def bulk_create(self, entities: List[T]) -> List[int]:
        """
        Create multiple entity objects in a single transaction.
        
        Args:
            entities: List of entity objects to create
            
        Returns:
            List of IDs for the created entities in the same order
        """
        ...
        
    @overload
    def bulk_create(self, entity_dicts: List[Dict[str, Any]]) -> List[int]:
        """
        Create multiple entities from dictionaries in a single transaction.
        
        Args:
            entity_dicts: List of dictionaries containing entity data
            
        Returns:
            List of IDs for the created entities in the same order
        """
        ...
        
    def bulk_create(self, entities: Union[List[T], List[Dict[str, Any]]]) -> List[int]:
        """
        Create multiple entities in a single transaction.
        
        This method significantly improves performance when creating multiple
        entities by using a single transaction and batch SQL execution.
        
        Args:
            entities: List of entity objects or dictionaries to create
            
        Returns:
            List of IDs for the created entities in the same order
            
        Raises:
            DAOException: If an error occurs during the bulk creation
            
        Example:
            >>> user_dicts = [
            ...     {"name": "User 1", "call_sign": "U1"},
            ...     {"name": "User 2", "call_sign": "U2"}
            ... ]
            >>> user_ids = user_dao.bulk_create(user_dicts)
            >>> print(f"Created users with IDs: {user_ids}")
        """
        if not entities:
            return []  # Nothing to create
            
        # Initialize result list for IDs
        entity_ids = []
        
        try:
            # Process in batches to avoid large transactions
            for batch in self._chunk_list(entities, self._batch_size):
                batch_ids = self._perform_bulk_create(batch)
                entity_ids.extend(batch_ids)
                
            return entity_ids
            
        except Exception as e:
            raise DAOException(f"Error during bulk creation: {e}", e)
    
    def _perform_bulk_create(self, entities: Union[List[T], List[Dict[str, Any]]]) -> List[int]:
        """
        Perform the actual bulk creation of entities in a single transaction.
        
        Args:
            entities: List of entity objects or dictionaries to create
            
        Returns:
            List of IDs for the created entities
        """
        # Process the entities into a list of dictionaries
        value_dicts = []
        for entity in entities:
            if isinstance(entity, dict):
                values = entity.copy()
            else:
                values = self._entity_to_values(entity)
                
            # Ensure timestamps are set
            now = datetime.now()
            if 'created_at' not in values or values['created_at'] is None:
                values['created_at'] = now
            if 'updated_at' not in values or values['updated_at'] is None:
                values['updated_at'] = now
                
            # Remove the ID column if it's None or 0
            if self.pk_column in values and (values[self.pk_column] is None or values[self.pk_column] == 0):
                del values[self.pk_column]
                
            value_dicts.append(values)
            
        # If no entities are valid for creation, return empty list
        if not value_dicts:
            return []
            
        # Ensure all dictionaries have the same keys (columns)
        all_keys = set()
        for values in value_dicts:
            all_keys.update(values.keys())
            
        # Create consistent dictionaries with all keys
        for values in value_dicts:
            for key in all_keys:
                if key not in values:
                    values[key] = None
        
        # Choose a common set of columns for the insert
        columns = sorted(all_keys)
        
        # Build SQL query with multiple value sets
        placeholders = ", ".join(["?"] * len(columns))
        query = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        # Create parameter tuples in correct column order
        param_sets = []
        for values in value_dicts:
            params = tuple(values.get(col) for col in columns)
            param_sets.append(params)
            
        # Execute the query within a transaction
        with self.db_manager.transaction() as tx:
            entity_ids = []
            
            # Insert entities one by one to get IDs back
            # SQLite doesn't support returning multiple IDs in a single executemany call
            for params in param_sets:
                cursor = tx.execute(query, params)
                entity_ids.append(cursor.lastrowid)
                
        return entity_ids
    
    # -------------------------------------------------------------------------
    # Bulk Update Operations
    # -------------------------------------------------------------------------
    
    @overload
    def bulk_update(self, entities: List[T]) -> int:
        """
        Update multiple entity objects in a single transaction.
        
        Args:
            entities: List of entity objects to update
            
        Returns:
            Number of entities successfully updated
        """
        ...
        
    @overload
    def bulk_update(self, entity_dicts: List[Dict[str, Any]]) -> int:
        """
        Update multiple entities from dictionaries in a single transaction.
        
        Args:
            entity_dicts: List of dictionaries containing entity data with IDs
            
        Returns:
            Number of entities successfully updated
        """
        ...
        
    @overload
    def bulk_update(self, entity_ids: List[int], common_values: Dict[str, Any]) -> int:
        """
        Update multiple entities with the same values by ID.
        
        Args:
            entity_ids: List of entity IDs to update
            common_values: Dictionary of values to apply to all entities
            
        Returns:
            Number of entities successfully updated
        """
        ...
        
    def bulk_update(self, entities_or_ids: Union[List[T], List[Dict[str, Any]], List[int]], 
                  common_values: Optional[Dict[str, Any]] = None) -> int:
        """
        Update multiple entities in a single transaction.
        
        This method supports three calling patterns:
        1. bulk_update(entities) - Update using a list of entity objects
        2. bulk_update(entity_dicts) - Update using a list of dictionaries with IDs
        3. bulk_update(entity_ids, common_values) - Update multiple IDs with the same values
        
        Args:
            entities_or_ids: List of entity objects, dictionaries, or IDs
            common_values: Dictionary of values to apply to all entities (when using IDs)
            
        Returns:
            Number of entities successfully updated
            
        Raises:
            DAOException: If an error occurs during the bulk update
            ValueError: If the entity IDs are missing or invalid
            
        Example:
            >>> # Update multiple entities with the same status
            >>> incident_ids = [1, 2, 3, 4]
            >>> updated = incident_dao.bulk_update(incident_ids, {"status": "active"})
            >>> print(f"Updated {updated} incidents")
        """
        if not entities_or_ids:
            return 0  # Nothing to update
            
        try:
            # Handle different calling patterns
            if common_values is not None:
                # Pattern: bulk_update(entity_ids, common_values)
                if not all(isinstance(entity_id, (int, str)) for entity_id in entities_or_ids):
                    raise ValueError("All elements must be valid IDs when using common_values")
                return self._bulk_update_by_ids(cast(List[int], entities_or_ids), common_values)
            elif isinstance(entities_or_ids[0], dict):
                # Pattern: bulk_update(entity_dicts)
                return self._bulk_update_dicts(cast(List[Dict[str, Any]], entities_or_ids))
            else:
                # Pattern: bulk_update(entities)
                return self._bulk_update_entities(cast(List[T], entities_or_ids))
                
        except Exception as e:
            raise DAOException(f"Error during bulk update: {e}", e)
    
    def _bulk_update_entities(self, entities: List[T]) -> int:
        """
        Update multiple entity objects in a single transaction.
        
        Args:
            entities: List of entity objects to update
            
        Returns:
            Number of entities successfully updated
        """
        # Convert entities to dictionaries
        entity_dicts = []
        for entity in entities:
            values = self._entity_to_values(entity)
            if self.pk_column not in values or values[self.pk_column] is None:
                raise ValueError(f"Entity missing {self.pk_column}")
            entity_dicts.append(values)
            
        return self._bulk_update_dicts(entity_dicts)
    
    def _bulk_update_dicts(self, entity_dicts: List[Dict[str, Any]]) -> int:
        """
        Update multiple entity dictionaries in a single transaction.
        
        Args:
            entity_dicts: List of dictionaries containing entity data with IDs
            
        Returns:
            Number of entities successfully updated
        """
        if not entity_dicts:
            return 0
            
        # Process in batches to avoid large transactions
        updated_count = 0
        for batch in self._chunk_list(entity_dicts, self._batch_size):
            with self.db_manager.transaction() as tx:
                for entity_dict in batch:
                    # Copy the dictionary to avoid modifying the original
                    values = entity_dict.copy()
                    
                    # Ensure entity has an ID
                    if self.pk_column not in values or values[self.pk_column] is None:
                        raise ValueError(f"Entity missing {self.pk_column}")
                        
                    # Get the ID and remove it from values
                    entity_id = values.pop(self.pk_column)
                    
                    # Set updated_at if not already present
                    if 'updated_at' not in values or values['updated_at'] is None:
                        values['updated_at'] = datetime.now()
                        
                    # Build and execute update query
                    set_clause = ", ".join([f"{column} = ?" for column in values.keys()])
                    query = f"UPDATE {self.table_name} SET {set_clause} WHERE {self.pk_column} = ?"
                    
                    params = list(values.values())
                    params.append(entity_id)
                    cursor = tx.execute(query, params)
                    
                    updated_count += cursor.rowcount
                    
        return updated_count
    
    def _bulk_update_by_ids(self, entity_ids: List[int], common_values: Dict[str, Any]) -> int:
        """
        Update multiple entities with the same values by ID.
        
        Args:
            entity_ids: List of entity IDs to update
            common_values: Dictionary of values to apply to all entities
            
        Returns:
            Number of entities successfully updated
        """
        if not entity_ids or not common_values:
            return 0
            
        # Ensure updated_at is set
        values = common_values.copy()
        if 'updated_at' not in values or values['updated_at'] is None:
            values['updated_at'] = datetime.now()
            
        # Build SET clause
        set_clause = ", ".join([f"{column} = ?" for column in values.keys()])
        
        # Process in batches to avoid large IN clauses
        updated_count = 0
        for id_batch in self._chunk_list(entity_ids, self._batch_size):
            # Build WHERE clause with placeholders for the IN condition
            placeholders = ", ".join(["?"] * len(id_batch))
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE {self.pk_column} IN ({placeholders})"
            
            # Prepare parameters (column values followed by IDs)
            params = list(values.values())
            params.extend(id_batch)
            
            # Execute the update
            with self.db_manager.transaction() as tx:
                cursor = tx.execute(query, params)
                updated_count += cursor.rowcount
                
        return updated_count
    
    # -------------------------------------------------------------------------
    # Bulk Delete Operations
    # -------------------------------------------------------------------------
    
    def bulk_delete(self, entity_ids: List[int]) -> int:
        """
        Delete multiple entities by ID in a single transaction.
        
        Args:
            entity_ids: List of entity IDs to delete
            
        Returns:
            Number of entities successfully deleted
            
        Raises:
            DAOException: If an error occurs during the bulk deletion
            
        Example:
            >>> form_ids = [10, 11, 12]
            >>> deleted = form_dao.bulk_delete(form_ids)
            >>> print(f"Deleted {deleted} forms")
        """
        if not entity_ids:
            return 0  # Nothing to delete
            
        try:
            # Process in batches to avoid large IN clauses
            deleted_count = 0
            for id_batch in self._chunk_list(entity_ids, self._batch_size):
                # Build query with IN clause
                placeholders = ", ".join(["?"] * len(id_batch))
                query = f"DELETE FROM {self.table_name} WHERE {self.pk_column} IN ({placeholders})"
                
                # Execute the delete
                with self.db_manager.transaction() as tx:
                    cursor = tx.execute(query, id_batch)
                    deleted_count += cursor.rowcount
                    
            return deleted_count
            
        except Exception as e:
            raise DAOException(f"Error during bulk deletion: {e}", e)
    
    def bulk_delete_by_filter(self, filters: Dict[str, Any]) -> int:
        """
        Delete multiple entities matching the given filters.
        
        Args:
            filters: Dictionary of column names and values to filter by
            
        Returns:
            Number of entities deleted
            
        Raises:
            DAOException: If an error occurs during the bulk deletion
            
        Example:
            >>> # Delete all draft forms for a specific incident
            >>> deleted = form_dao.bulk_delete_by_filter({
            ...     "incident_id": 5,
            ...     "status": "draft"
            ... })
            >>> print(f"Deleted {deleted} draft forms")
        """
        if not filters:
            raise ValueError("Filters must be provided for bulk_delete_by_filter")
            
        try:
            # Build WHERE clause from filters
            where_clauses = []
            params = []
            
            for column, value in filters.items():
                where_clauses.append(f"{column} = ?")
                params.append(value)
                
            where_clause = " AND ".join(where_clauses)
            
            # Build query
            query = f"DELETE FROM {self.table_name} WHERE {where_clause}"
            
            # Execute query within transaction
            with self.db_manager.transaction() as tx:
                cursor = tx.execute(query, params)
                return cursor.rowcount
                
        except Exception as e:
            raise DAOException(f"Error during bulk deletion by filter: {e}", e)
    
    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------
    
    def set_batch_size(self, batch_size: int) -> None:
        """
        Set the batch size for chunking large operations.
        
        Args:
            batch_size: Number of entities to process in each batch
            
        Raises:
            ValueError: If batch_size is less than 1
        """
        if batch_size < 1:
            raise ValueError("Batch size must be at least 1")
        self._batch_size = batch_size
    
    def get_batch_size(self) -> int:
        """
        Get the current batch size for chunking operations.
        
        Returns:
            Current batch size
        """
        return self._batch_size
    
    def _chunk_list(self, items: List, chunk_size: int) -> List[List]:
        """
        Split a list into chunks of specified size.
        
        Args:
            items: List to split
            chunk_size: Size of each chunk
            
        Returns:
            List of chunks
        """
        for i in range(0, len(items), chunk_size):
            yield items[i:i + chunk_size]
            
    def process_in_batches(self, items: List, process_func: Callable[[List], Any], 
                         batch_size: Optional[int] = None) -> List:
        """
        Process a large list of items in smaller batches.
        
        This utility method helps manage memory usage and transaction size
        when processing large datasets.
        
        Args:
            items: List of items to process
            process_func: Function that processes a batch of items
            batch_size: Optional custom batch size (defaults to class batch size)
            
        Returns:
            Combined results from processing all batches
            
        Example:
            >>> # Process 1000 forms in batches of 100
            >>> def process_batch(forms_batch):
            ...     results = []
            ...     for form in forms_batch:
            ...         # Process each form
            ...         results.append(processed_result)
            ...     return results
            >>> 
            >>> all_results = form_dao.process_in_batches(
            ...     all_forms, process_batch, batch_size=100
            ... )
        """
        if not items:
            return []
            
        chunk_size = batch_size or self._batch_size
        results = []
        
        for chunk in self._chunk_list(items, chunk_size):
            chunk_results = process_func(chunk)
            if chunk_results:
                if isinstance(chunk_results, list):
                    results.extend(chunk_results)
                else:
                    results.append(chunk_results)
                    
        return results

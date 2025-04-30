#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cache mixin for DAO classes to enable caching functionality.

This module provides a mixin class that can be added to DAO implementations
to enable caching of query results and automatic cache invalidation when
data is modified.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Generic, Union, cast, Type

from radioforms.database.cache.cache_manager import get_cache_manager
from radioforms.database.cache.cache_backends import CacheBackend
from radioforms.database.dao.base_dao import BaseDAO

# Configure logger
logger = logging.getLogger(__name__)

# Type variable for the entity type
T = TypeVar('T')

class DAOCacheMixin(Generic[T]):
    """
    Mixin class that provides caching functionality for DAO classes.
    
    This mixin should be added to DAO classes to enable caching of query results
    and automatic cache invalidation when data is modified. It works with the
    standard BaseDAO interface.
    
    Example:
        >>> class UserDAO(DAOCacheMixin[User], BaseDAO[User]):
        ...     def __init__(self, db_manager: DatabaseManager):
        ...         BaseDAO.__init__(self, db_manager)
        ...         DAOCacheMixin.__init__(self)
        ...         self.table_name = 'users'
    """
    
    def __init__(self, cache_enabled: bool = True, cache_ttl: Optional[int] = None):
        """
        Initialize the cache mixin.
        
        Args:
            cache_enabled: Whether caching is enabled
            cache_ttl: Time-to-live for cache entries in seconds
        """
        self._cache_enabled = cache_enabled
        self._cache_ttl = cache_ttl
        self._cache_name = f"{self.__class__.__name__.lower()}_cache"
        
    def _get_cache(self) -> CacheBackend:
        """
        Get the cache backend for this DAO.
        
        Returns:
            Cache backend instance
        """
        return get_cache_manager().get_cache(self._cache_name)
        
    def _generate_cache_key(self, method: str, *args: Any, **kwargs: Any) -> str:
        """
        Generate a cache key for a method call.
        
        Args:
            method: Name of the method
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Cache key string
        """
        # Include class name in the key
        key_parts = [self.__class__.__name__, method]
        
        # Add args (excluding self)
        for arg in args:
            key_parts.append(str(arg))
            
        # Add kwargs
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
            
        return ":".join(key_parts)
        
    def _invalidate_cache(self, pattern: Optional[str] = None) -> None:
        """
        Invalidate cached entries matching a pattern.
        
        Args:
            pattern: Pattern to match cache keys against, or None to use class name
        """
        if not self._cache_enabled:
            return
            
        cache = self._get_cache()
        
        if pattern is None:
            pattern = self.__class__.__name__
            
        count = cache.invalidate_pattern(pattern)
        if count > 0:
            logger.debug(f"Invalidated {count} cache entries for {self.__class__.__name__}")
            
    def configure_cache(self, enabled: bool = True, ttl: Optional[int] = None) -> None:
        """
        Configure the cache settings for this DAO.
        
        Args:
            enabled: Whether caching is enabled
            ttl: Time-to-live for cache entries in seconds
        """
        self._cache_enabled = enabled
        self._cache_ttl = ttl
        
    # Now override the standard BaseDAO methods to add caching

    def find_by_id(self, entity_id: Any, as_dict: bool = False) -> Optional[Union[T, Dict[str, Any]]]:
        """
        Find an entity by its ID, with caching.
        
        Args:
            entity_id: ID of the entity to find
            as_dict: Whether to return a dictionary instead of an entity object
            
        Returns:
            Entity object, dictionary, or None if not found
        """
        if not self._cache_enabled:
            # Pass through to the parent implementation
            return super().find_by_id(entity_id, as_dict)
            
        # Generate cache key
        cache_key = self._generate_cache_key("find_by_id", entity_id, as_dict=as_dict)
        
        # Try to get from cache
        cache = self._get_cache()
        hit, value = cache.get(cache_key)
        
        if hit:
            logger.debug(f"Cache hit for {cache_key}")
            return value
            
        # Cache miss, get from database
        logger.debug(f"Cache miss for {cache_key}")
        result = super().find_by_id(entity_id, as_dict)
        
        # Cache the result
        if result is not None:
            cache.set(cache_key, result, self._cache_ttl)
            
        return result
        
    def find_all(self, as_dict: bool = False) -> List[Union[T, Dict[str, Any]]]:
        """
        Find all entities, with caching.
        
        Args:
            as_dict: Whether to return dictionaries instead of entity objects
            
        Returns:
            List of entity objects or dictionaries
        """
        if not self._cache_enabled:
            # Pass through to the parent implementation
            return super().find_all(as_dict)
            
        # Generate cache key
        cache_key = self._generate_cache_key("find_all", as_dict=as_dict)
        
        # Try to get from cache
        cache = self._get_cache()
        hit, value = cache.get(cache_key)
        
        if hit:
            logger.debug(f"Cache hit for {cache_key}")
            return value
            
        # Cache miss, get from database
        logger.debug(f"Cache miss for {cache_key}")
        result = super().find_all(as_dict)
        
        # Cache the result
        cache.set(cache_key, result, self._cache_ttl)
            
        return result
        
    def find_by_field(self, field: str, value: Any, as_dict: bool = False) -> List[Union[T, Dict[str, Any]]]:
        """
        Find entities by a field value, with caching.
        
        Args:
            field: Field name to search by
            value: Value to match
            as_dict: Whether to return dictionaries instead of entity objects
            
        Returns:
            List of entity objects or dictionaries
        """
        if not self._cache_enabled:
            # Pass through to the parent implementation
            return super().find_by_field(field, value, as_dict)
            
        # Generate cache key
        cache_key = self._generate_cache_key("find_by_field", field, value, as_dict=as_dict)
        
        # Try to get from cache
        cache = self._get_cache()
        hit, value_from_cache = cache.get(cache_key)
        
        if hit:
            logger.debug(f"Cache hit for {cache_key}")
            return value_from_cache
            
        # Cache miss, get from database
        logger.debug(f"Cache miss for {cache_key}")
        result = super().find_by_field(field, value, as_dict)
        
        # Cache the result
        cache.set(cache_key, result, self._cache_ttl)
            
        return result
        
    def find_by_fields(self, field_dict: Dict[str, Any], as_dict: bool = False) -> List[Union[T, Dict[str, Any]]]:
        """
        Find entities by multiple field values, with caching.
        
        Args:
            field_dict: Dictionary of field names and values to match
            as_dict: Whether to return dictionaries instead of entity objects
            
        Returns:
            List of entity objects or dictionaries
        """
        if not self._cache_enabled:
            # Pass through to the parent implementation
            return super().find_by_fields(field_dict, as_dict)
            
        # Generate cache key
        # Sort field_dict items to ensure consistent keys
        sorted_items = sorted(field_dict.items())
        cache_key = self._generate_cache_key("find_by_fields", str(sorted_items), as_dict=as_dict)
        
        # Try to get from cache
        cache = self._get_cache()
        hit, value = cache.get(cache_key)
        
        if hit:
            logger.debug(f"Cache hit for {cache_key}")
            return value
            
        # Cache miss, get from database
        logger.debug(f"Cache miss for {cache_key}")
        result = super().find_by_fields(field_dict, as_dict)
        
        # Cache the result
        cache.set(cache_key, result, self._cache_ttl)
            
        return result
        
    def create(self, entity: Union[T, Dict[str, Any]]) -> int:
        """
        Create a new entity in the database, invalidating cache.
        
        Args:
            entity: Entity object or dictionary to create
            
        Returns:
            ID of the created entity
        """
        # Call the parent implementation
        entity_id = super().create(entity)
        
        # Invalidate cache
        self._invalidate_cache()
        
        return entity_id
        
    def update(self, entity_or_id: Union[T, Dict[str, Any], Any], update_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an existing entity in the database, invalidating cache.
        
        This method supports two calling patterns:
        1. update(entity) - where entity is an object or dict with an ID
        2. update(entity_id, update_data) - where entity_id is the ID and update_data is a dict of values
        
        Args:
            entity_or_id: Entity object, dictionary, or entity ID
            update_data: If entity_or_id is an ID, this contains the update values
            
        Returns:
            True if the update was successful, False otherwise
        """
        # Call the parent implementation
        if update_data is not None:
            # Called as update(entity_id, update_data)
            result = BaseDAO.update(self, entity_or_id, update_data)
        else:
            # Called as update(entity)
            result = BaseDAO.update(self, entity_or_id)
        
        # Invalidate cache
        if result:
            self._invalidate_cache()
            
        return result
        
    def delete(self, entity_id: Any) -> bool:
        """
        Delete an entity from the database, invalidating cache.
        
        Args:
            entity_id: ID of the entity to delete
            
        Returns:
            True if the delete was successful, False otherwise
        """
        # Call the parent implementation
        result = super().delete(entity_id)
        
        # Invalidate cache
        if result:
            self._invalidate_cache()
            
        return result
        
    def count(self, where_clause: Optional[str] = None, params: Optional[List[Any]] = None) -> int:
        """
        Count entities with optional filtering, with caching.
        
        Args:
            where_clause: Optional WHERE clause for filtering
            params: Parameters for the WHERE clause
            
        Returns:
            Count of matching entities
        """
        if not self._cache_enabled:
            # Pass through to the parent implementation
            return super().count(where_clause, params)
            
        # Generate cache key
        params_str = str(params) if params else "None"
        cache_key = self._generate_cache_key("count", where_clause or "None", params_str)
        
        # Try to get from cache
        cache = self._get_cache()
        hit, value = cache.get(cache_key)
        
        if hit:
            logger.debug(f"Cache hit for {cache_key}")
            return value
            
        # Cache miss, get from database
        logger.debug(f"Cache miss for {cache_key}")
        result = super().count(where_clause, params)
        
        # Cache the result
        cache.set(cache_key, result, self._cache_ttl)
            
        return result
        
    def exists(self, entity_id: Any) -> bool:
        """
        Check if an entity exists by ID, with caching.
        
        Args:
            entity_id: ID of the entity to check
            
        Returns:
            True if the entity exists, False otherwise
        """
        if not self._cache_enabled:
            # Pass through to the parent implementation
            return super().exists(entity_id)
            
        # Generate cache key
        cache_key = self._generate_cache_key("exists", entity_id)
        
        # Try to get from cache
        cache = self._get_cache()
        hit, value = cache.get(cache_key)
        
        if hit:
            logger.debug(f"Cache hit for {cache_key}")
            return value
            
        # Cache miss, get from database
        logger.debug(f"Cache miss for {cache_key}")
        result = super().exists(entity_id)
        
        # Cache the result
        cache.set(cache_key, result, self._cache_ttl)
            
        return result

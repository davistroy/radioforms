#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DAO caching mixin for database operations.

This module provides a mixin class for adding caching capabilities to DAO classes,
improving performance for frequently accessed data.
"""

import logging
import functools
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Generic, Union, Type

from radioforms.database.cache.cache_manager import get_cache_manager
from radioforms.database.cache.cache_backends import CacheBackend

# Configure logger
logger = logging.getLogger(__name__)

# Type variable for the entity type
T = TypeVar('T')


class DAOCacheMixin(Generic[T]):
    """
    Mixin class for adding caching capabilities to DAO classes.
    
    This class provides cached versions of common DAO methods and
    handles cache invalidation for write operations.
    
    Type Parameters:
        T: The entity type for this DAO
    """
    
    def __init__(self):
        """Initialize the DAO cache mixin."""
        # These are expected to be set by the BaseDAO class
        self.table_name = None  # Override in subclass
        self.pk_column = 'id'   # Default primary key column name
        
        # Cache settings with defaults
        self._cache_enabled = True
        self._cache_name = None  # Default will be set based on table_name
        self._cache_ttl = None   # Use cache default
        self._entity_types = {}  # Used for advanced caching scenarios
        
    def configure_cache(self, enabled: bool = True, cache_name: Optional[str] = None, 
                      ttl: Optional[int] = None) -> None:
        """
        Configure caching for this DAO.
        
        Args:
            enabled: Whether caching is enabled for this DAO
            cache_name: Optional name of the cache to use
            ttl: Optional time-to-live in seconds for cached items
        """
        self._cache_enabled = enabled
        
        if cache_name:
            self._cache_name = cache_name
            
        if ttl is not None:
            self._cache_ttl = ttl
            
        logger.debug(f"Cache configured for {self.__class__.__name__}: enabled={enabled}, "
                    f"cache_name={self._cache_name}, ttl={self._cache_ttl}")
        
    def _get_cache(self) -> CacheBackend:
        """
        Get the cache instance for this DAO.
        
        Returns:
            Cache instance
        """
        if not self._cache_enabled:
            return get_cache_manager().get_cache(backend="null")
            
        # Determine cache name based on table_name if not explicitly set
        cache_name = self._cache_name
        if cache_name is None and hasattr(self, 'table_name') and self.table_name:
            cache_name = f"dao:{self.table_name}"
        elif cache_name is None:
            cache_name = f"dao:{self.__class__.__name__}"
            
        # Get the cache
        return get_cache_manager().get_cache(cache_name, ttl=self._cache_ttl)
        
    def _generate_key(self, method_name: str, *args: Any, **kwargs: Any) -> str:
        """
        Generate a cache key for a method call.
        
        Args:
            method_name: Name of the method being called
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Cache key string
        """
        # Start with table name and method
        if hasattr(self, 'table_name') and self.table_name:
            key_parts = [self.table_name, method_name]
        else:
            key_parts = [self.__class__.__name__, method_name]
            
        # Add args (convert to strings)
        for arg in args:
            if isinstance(arg, (str, int, float, bool)) or arg is None:
                key_parts.append(str(arg))
            else:
                # For complex objects, use a hash
                key_parts.append(f"hash:{hash(str(arg))}")
                
        # Add kwargs (sorted for consistency)
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (str, int, float, bool)) or v is None:
                key_parts.append(f"{k}:{v}")
            else:
                # For complex objects, use a hash
                key_parts.append(f"{k}:hash:{hash(str(v))}")
                
        return ":".join(key_parts)
        
    def _invalidate_all(self) -> int:
        """
        Invalidate all cache entries for this DAO.
        
        Returns:
            Number of entries invalidated
        """
        if not self._cache_enabled:
            return 0
            
        cache = self._get_cache()
        
        # Determine pattern to invalidate
        if hasattr(self, 'table_name') and self.table_name:
            pattern = self.table_name
        else:
            pattern = self.__class__.__name__
            
        # Invalidate all entries matching the pattern
        count = cache.invalidate_pattern(pattern)
        
        if count > 0:
            logger.debug(f"Invalidated {count} cache entries for {pattern}")
            
        return count
        
    def _invalidate_by_id(self, entity_id: Any) -> int:
        """
        Invalidate cache entries for a specific entity ID.
        
        Args:
            entity_id: ID of the entity to invalidate
            
        Returns:
            Number of entries invalidated
        """
        if not self._cache_enabled:
            return 0
            
        cache = self._get_cache()
        
        # Determine pattern to invalidate
        if hasattr(self, 'table_name') and self.table_name:
            pattern = f"{self.table_name}:find_by_id:{entity_id}"
        else:
            pattern = f"{self.__class__.__name__}:find_by_id:{entity_id}"
            
        # Invalidate specific entry
        count = cache.invalidate_pattern(pattern)
        
        if count > 0:
            logger.debug(f"Invalidated {count} cache entries for {pattern}")
            
        return count
        
    def cached_find_by_id(self, entity_id: Any, as_dict: bool = False) -> Optional[Union[T, Dict[str, Any]]]:
        """
        Find entity by ID with caching.
        
        Args:
            entity_id: ID of the entity to find
            as_dict: Whether to return a dictionary instead of an entity object
            
        Returns:
            Entity object, dictionary, or None if not found
        """
        if not self._cache_enabled:
            # Caching disabled - call the base method directly
            return super().find_by_id(entity_id, as_dict)
            
        # Get the cache
        cache = self._get_cache()
        
        # Generate cache key
        key = self._generate_key("find_by_id", entity_id, as_dict=as_dict)
        
        # Try to get from cache
        hit, value = cache.get(key)
        if hit:
            logger.debug(f"Cache hit for {key}")
            return value
            
        # Cache miss, call the base method
        logger.debug(f"Cache miss for {key}")
        result = super().find_by_id(entity_id, as_dict)
        
        # Store in cache
        if result is not None:
            cache.set(key, result)
            
        return result
        
    def cached_find_all(self, as_dict: bool = False) -> List[Union[T, Dict[str, Any]]]:
        """
        Find all entities with caching.
        
        Args:
            as_dict: Whether to return dictionaries instead of entity objects
            
        Returns:
            List of entity objects or dictionaries
        """
        if not self._cache_enabled:
            # Caching disabled - call the base method directly
            return super().find_all(as_dict)
            
        # Get the cache
        cache = self._get_cache()
        
        # Generate cache key
        key = self._generate_key("find_all", as_dict=as_dict)
        
        # Try to get from cache
        hit, value = cache.get(key)
        if hit:
            logger.debug(f"Cache hit for {key}")
            return value
            
        # Cache miss, call the base method
        logger.debug(f"Cache miss for {key}")
        result = super().find_all(as_dict)
        
        # Store in cache
        cache.set(key, result)
        
        return result
        
    def cached_find_by_field(self, field: str, value: Any, as_dict: bool = False) -> List[Union[T, Dict[str, Any]]]:
        """
        Find entities by field value with caching.
        
        Args:
            field: Field name to search on
            value: Value to match
            as_dict: Whether to return dictionaries instead of entity objects
            
        Returns:
            List of entity objects or dictionaries
        """
        if not self._cache_enabled:
            # Caching disabled - call the base method directly
            return super().find_by_field(field, value, as_dict)
            
        # Get the cache
        cache = self._get_cache()
        
        # Generate cache key
        key = self._generate_key("find_by_field", field, value, as_dict=as_dict)
        
        # Try to get from cache
        hit, value_from_cache = cache.get(key)
        if hit:
            logger.debug(f"Cache hit for {key}")
            return value_from_cache
            
        # Cache miss, call the base method
        logger.debug(f"Cache miss for {key}")
        result = super().find_by_field(field, value, as_dict)
        
        # Store in cache
        cache.set(key, result)
        
        return result
        
    def cached_find_by_fields(self, field_dict: Dict[str, Any], as_dict: bool = False) -> List[Union[T, Dict[str, Any]]]:
        """
        Find entities by multiple field values with caching.
        
        Args:
            field_dict: Dictionary of field names and values to match
            as_dict: Whether to return dictionaries instead of entity objects
            
        Returns:
            List of entity objects or dictionaries
        """
        if not self._cache_enabled:
            # Caching disabled - call the base method directly
            return super().find_by_fields(field_dict, as_dict)
            
        # Get the cache
        cache = self._get_cache()
        
        # Generate cache key - special handling for the field_dict
        sorted_items = sorted(field_dict.items())
        key_parts = [self._generate_key("find_by_fields", as_dict=as_dict)]
        for field, value in sorted_items:
            key_parts.append(f"{field}:{value}")
        key = ":".join(key_parts)
        
        # Try to get from cache
        hit, value = cache.get(key)
        if hit:
            logger.debug(f"Cache hit for {key}")
            return value
            
        # Cache miss, call the base method
        logger.debug(f"Cache miss for {key}")
        result = super().find_by_fields(field_dict, as_dict)
        
        # Store in cache
        cache.set(key, result)
        
        return result
        
    def cached_count(self, where_clause: Optional[str] = None, params: Optional[List[Any]] = None) -> int:
        """
        Count entities with caching.
        
        Args:
            where_clause: Optional WHERE clause for filtering
            params: Parameters for the WHERE clause
            
        Returns:
            Count of matching entities
        """
        if not self._cache_enabled:
            # Caching disabled - call the base method directly
            return super().count(where_clause, params)
            
        # Get the cache
        cache = self._get_cache()
        
        # Generate cache key
        key = self._generate_key("count", where_clause, str(params) if params else None)
        
        # Try to get from cache
        hit, value = cache.get(key)
        if hit:
            logger.debug(f"Cache hit for {key}")
            return value
            
        # Cache miss, call the base method
        logger.debug(f"Cache miss for {key}")
        result = super().count(where_clause, params)
        
        # Store in cache
        cache.set(key, result)
        
        return result
        
    def create(self, entity: Union[T, Dict[str, Any]]) -> int:
        """
        Create a new entity and invalidate relevant caches.
        
        Args:
            entity: Entity object or dictionary to create
            
        Returns:
            ID of the created entity
        """
        # Create the entity
        entity_id = super().create(entity)
        
        # Invalidate caches
        if self._cache_enabled:
            self._invalidate_all()
            
        return entity_id
        
    def update(self, entity: Union[T, Dict[str, Any]]) -> bool:
        """
        Update an entity and invalidate relevant caches.
        
        Args:
            entity: Entity object or dictionary to update
            
        Returns:
            True if the update was successful, False otherwise
        """
        # Get entity ID for targeted invalidation
        entity_id = None
        if isinstance(entity, dict):
            entity_id = entity.get(self.pk_column)
        elif hasattr(entity, self.pk_column):
            entity_id = getattr(entity, self.pk_column)
            
        # Update the entity
        result = super().update(entity)
        
        # Invalidate caches
        if self._cache_enabled and result:
            if entity_id:
                # Invalidate specific entity
                self._invalidate_by_id(entity_id)
                
            # Invalidate collection caches
            cache = self._get_cache()
            cache.invalidate_pattern("find_all")
            cache.invalidate_pattern("find_by_field")
            cache.invalidate_pattern("find_by_fields")
            cache.invalidate_pattern("count")
            
        return result
        
    def delete(self, entity_id: Any) -> bool:
        """
        Delete an entity and invalidate relevant caches.
        
        Args:
            entity_id: ID of the entity to delete
            
        Returns:
            True if the delete was successful, False otherwise
        """
        # Delete the entity
        result = super().delete(entity_id)
        
        # Invalidate caches
        if self._cache_enabled and result:
            # Invalidate specific entity
            self._invalidate_by_id(entity_id)
            
            # Invalidate collection caches
            cache = self._get_cache()
            cache.invalidate_pattern("find_all")
            cache.invalidate_pattern("find_by_field")
            cache.invalidate_pattern("find_by_fields")
            cache.invalidate_pattern("count")
            
        return result


# Add method aliases for convenient access
def cached_method(method_name):
    """
    Create a method that delegates to a cached version.
    
    Args:
        method_name: Name of the method to cache
        
    Returns:
        Delegating method
    """
    @functools.wraps(getattr(DAOCacheMixin, f"cached_{method_name}"))
    def wrapper(self, *args, **kwargs):
        cached_method = getattr(self, f"cached_{method_name}")
        return cached_method(*args, **kwargs)
    return wrapper

# Add method aliases to DAOCacheMixin
setattr(DAOCacheMixin, "find_by_id", cached_method("find_by_id"))
setattr(DAOCacheMixin, "find_all", cached_method("find_all"))
setattr(DAOCacheMixin, "find_by_field", cached_method("find_by_field"))
setattr(DAOCacheMixin, "find_by_fields", cached_method("find_by_fields"))
setattr(DAOCacheMixin, "count", cached_method("count"))

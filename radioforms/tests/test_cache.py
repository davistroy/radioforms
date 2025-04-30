#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the caching functionality.

This module contains tests for the cache backends, cache manager,
cache decorators, and DAO cache mixin.
"""

import unittest
import tempfile
import os
import time
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional

from radioforms.database.db_manager import DatabaseManager
from radioforms.database.dao.base_dao import BaseDAO
from radioforms.database.models.user import User
from radioforms.database.cache.cache_backends import (
    MemoryCache, DiskCache, NullCache
)
from radioforms.database.cache.cache_manager import (
    CacheManager, get_cache_manager
)
from radioforms.database.cache.cache_decorators import (
    cacheable, invalidate_cache, multi_cache, cache_result
)
from radioforms.database.cache.dao_cache_mixin import DAOCacheMixin


class TestMemoryCache(unittest.TestCase):
    """Test case for the MemoryCache backend."""
    
    def test_basic_operations(self):
        """Test basic cache operations (get, set, delete)."""
        cache = MemoryCache(max_size=100)
        
        # Test set and get
        cache.set("key1", "value1")
        hit, value = cache.get("key1")
        self.assertTrue(hit)
        self.assertEqual(value, "value1")
        
        # Test miss
        hit, value = cache.get("nonexistent")
        self.assertFalse(hit)
        self.assertIsNone(value)
        
        # Test delete
        result = cache.delete("key1")
        self.assertTrue(result)
        hit, value = cache.get("key1")
        self.assertFalse(hit)
        
        # Test delete nonexistent
        result = cache.delete("nonexistent")
        self.assertFalse(result)
        
    def test_ttl(self):
        """Test time-to-live functionality."""
        cache = MemoryCache(max_size=100)
        
        # Set with short TTL
        cache.set("key1", "value1", ttl=0.1)  # 100ms TTL
        
        # Should be available immediately
        hit, value = cache.get("key1")
        self.assertTrue(hit)
        self.assertEqual(value, "value1")
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Should be expired now
        hit, value = cache.get("key1")
        self.assertFalse(hit)
        
    def test_max_size(self):
        """Test max size limit and eviction."""
        cache = MemoryCache(max_size=3)
        
        # Fill the cache with explicit access times to ensure a clear LRU order
        # key2 will be oldest, then key3, then key1 (newest)
        cache.set("key2", "value2")
        time.sleep(0.01)  # Small delay to ensure different access times
        cache.set("key3", "value3")
        time.sleep(0.01)
        cache.set("key1", "value1")
        
        # Verify all items are in cache
        self.assertTrue(cache.get("key1")[0])
        self.assertTrue(cache.get("key2")[0])
        self.assertTrue(cache.get("key3")[0])
        
        # Add one more item to trigger eviction of the least recently used (key2)
        cache.set("key4", "value4")
        
        # key2 should be evicted (oldest)
        # key1, key3, key4 should remain
        self.assertTrue(cache.get("key1")[0])
        self.assertFalse(cache.get("key2")[0])
        self.assertTrue(cache.get("key3")[0])
        self.assertTrue(cache.get("key4")[0])
        
    def test_clear(self):
        """Test clearing the cache."""
        cache = MemoryCache(max_size=100)
        
        # Add some items
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        # Clear the cache
        cache.clear()
        
        # Verify items are gone
        self.assertFalse(cache.get("key1")[0])
        self.assertFalse(cache.get("key2")[0])
        
    def test_invalidate_pattern(self):
        """Test invalidating by pattern."""
        cache = MemoryCache(max_size=100)
        
        # Add items with different patterns
        cache.set("prefix:key1", "value1")
        cache.set("prefix:key2", "value2")
        cache.set("other:key3", "value3")
        
        # Invalidate by pattern
        count = cache.invalidate_pattern("prefix:")
        
        # Should have invalidated 2 items
        self.assertEqual(count, 2)
        
        # Verify correct items were invalidated
        self.assertFalse(cache.get("prefix:key1")[0])
        self.assertFalse(cache.get("prefix:key2")[0])
        self.assertTrue(cache.get("other:key3")[0])
        
    def test_get_stats(self):
        """Test getting cache statistics."""
        cache = MemoryCache(max_size=100)
        
        # Add some items
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        # Get a hit
        cache.get("key1")
        
        # Get a miss
        cache.get("nonexistent")
        
        # Get stats
        stats = cache.get_stats()
        
        # Verify stats
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["sets"], 2)
        self.assertEqual(stats["size"], 2)


class TestDiskCache(unittest.TestCase):
    """Test case for the DiskCache backend."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for cache files
        self.temp_dir = tempfile.mkdtemp()
        self.cache = DiskCache(cache_dir=self.temp_dir)
        
    def tearDown(self):
        """Clean up after the test."""
        # Remove the temporary directory
        try:
            shutil.rmtree(self.temp_dir)
        except (PermissionError, OSError):
            # On Windows, sometimes files can't be deleted immediately
            pass
            
    def test_basic_operations(self):
        """Test basic cache operations (get, set, delete)."""
        # Test set and get
        self.cache.set("key1", "value1")
        hit, value = self.cache.get("key1")
        self.assertTrue(hit)
        self.assertEqual(value, "value1")
        
        # Test miss
        hit, value = self.cache.get("nonexistent")
        self.assertFalse(hit)
        self.assertIsNone(value)
        
        # Test delete
        result = self.cache.delete("key1")
        self.assertTrue(result)
        hit, value = self.cache.get("key1")
        self.assertFalse(hit)
        
        # Test delete nonexistent
        result = self.cache.delete("nonexistent")
        self.assertFalse(result)
        
    def test_ttl(self):
        """Test time-to-live functionality."""
        # Set with short TTL
        self.cache.set("key1", "value1", ttl=0.1)  # 100ms TTL
        
        # Should be available immediately
        hit, value = self.cache.get("key1")
        self.assertTrue(hit)
        self.assertEqual(value, "value1")
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Should be expired now
        hit, value = self.cache.get("key1")
        self.assertFalse(hit)
        
    def test_clear(self):
        """Test clearing the cache."""
        # Add some items
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        # Clear the cache
        self.cache.clear()
        
        # Verify items are gone
        self.assertFalse(self.cache.get("key1")[0])
        self.assertFalse(self.cache.get("key2")[0])
        
    def test_invalidate_pattern(self):
        """Test invalidating by pattern."""
        # Add items with different patterns
        self.cache.set("prefix:key1", "value1")
        self.cache.set("prefix:key2", "value2")
        self.cache.set("other:key3", "value3")
        
        # Invalidate by pattern
        count = self.cache.invalidate_pattern("prefix:")
        
        # Should have invalidated 2 items
        self.assertEqual(count, 2)
        
        # Verify correct items were invalidated
        self.assertFalse(self.cache.get("prefix:key1")[0])
        self.assertFalse(self.cache.get("prefix:key2")[0])
        self.assertTrue(self.cache.get("other:key3")[0])
        
    def test_complex_values(self):
        """Test caching complex Python objects."""
        # Define a complex object
        complex_obj = {
            "name": "Test",
            "numbers": [1, 2, 3],
            "nested": {
                "a": 1,
                "b": 2
            }
        }
        
        # Cache the object
        self.cache.set("complex", complex_obj)
        
        # Retrieve it
        hit, value = self.cache.get("complex")
        
        # Verify it matches
        self.assertTrue(hit)
        self.assertEqual(value, complex_obj)
        
    def test_get_stats(self):
        """Test getting cache statistics."""
        # Add some items
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        # Get a hit
        self.cache.get("key1")
        
        # Get a miss
        self.cache.get("nonexistent")
        
        # Get stats
        stats = self.cache.get_stats()
        
        # Verify stats
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["sets"], 2)
        self.assertEqual(stats["size"], 2)
        
        # Disk cache should have disk usage stats
        self.assertIn("disk_usage_bytes", stats)
        self.assertIn("disk_usage_mb", stats)


class TestNullCache(unittest.TestCase):
    """Test case for the NullCache backend."""
    
    def test_operations(self):
        """Test that NullCache operations do nothing."""
        cache = NullCache()
        
        # Set should do nothing
        cache.set("key1", "value1")
        
        # Get should always return miss
        hit, value = cache.get("key1")
        self.assertFalse(hit)
        self.assertIsNone(value)
        
        # Delete should return False
        result = cache.delete("key1")
        self.assertFalse(result)
        
        # Clear should do nothing
        cache.clear()
        
        # Invalidate should return 0
        count = cache.invalidate_pattern("anything")
        self.assertEqual(count, 0)
        
        # Stats should show zeros
        stats = cache.get_stats()
        self.assertEqual(stats["size"], 0)
        self.assertEqual(stats["hit_rate"], 0.0)


class TestCacheManager(unittest.TestCase):
    """Test case for the CacheManager."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for cache files
        self.temp_dir = tempfile.mkdtemp()
        
        # Reset the singleton instance
        CacheManager._instance = None
        
    def tearDown(self):
        """Clean up after the test."""
        # Remove the temporary directory
        try:
            shutil.rmtree(self.temp_dir)
        except (PermissionError, OSError):
            # On Windows, sometimes files can't be deleted immediately
            pass
            
    def test_get_cache(self):
        """Test getting caches with different configurations."""
        manager = get_cache_manager()
        
        # Configure with disk cache directory
        manager.configure({
            "disk_cache": {
                "base_dir": self.temp_dir
            }
        })
        
        # Get memory cache
        memory_cache = manager.get_cache("test_memory", backend="memory")
        self.assertIsInstance(memory_cache, MemoryCache)
        
        # Get disk cache
        disk_cache = manager.get_cache("test_disk", backend="disk")
        self.assertIsInstance(disk_cache, DiskCache)
        
        # Get null cache
        null_cache = manager.get_cache("test_null", backend="null")
        self.assertIsInstance(null_cache, NullCache)
        
        # Get default cache (should be memory by default)
        default_cache = manager.get_cache("test_default")
        self.assertIsInstance(default_cache, MemoryCache)
        
    def test_configure(self):
        """Test configuring the cache manager."""
        manager = get_cache_manager()
        
        # Default config
        self.assertTrue(manager._config["enabled"])
        
        # Update configuration
        manager.configure({
            "enabled": False,
            "default_backend": "disk",
            "default_ttl": 600,
            "memory_cache": {
                "max_size": 5000
            }
        })
        
        # Check updated config
        self.assertFalse(manager._config["enabled"])
        self.assertEqual(manager._config["default_backend"], "disk")
        self.assertEqual(manager._config["default_ttl"], 600)
        self.assertEqual(manager._config["memory_cache"]["max_size"], 5000)
        
        # Get cache when disabled
        cache = manager.get_cache("test")
        self.assertIsInstance(cache, NullCache)
        
    def test_clear_all_caches(self):
        """Test clearing all caches."""
        manager = get_cache_manager()
        
        # Get some caches and add data
        cache1 = manager.get_cache("test1")
        cache2 = manager.get_cache("test2")
        
        cache1.set("key1", "value1")
        cache2.set("key2", "value2")
        
        # Verify data is there
        self.assertTrue(cache1.get("key1")[0])
        self.assertTrue(cache2.get("key2")[0])
        
        # Clear all caches
        manager.clear_all_caches()
        
        # Verify data is gone
        self.assertFalse(cache1.get("key1")[0])
        self.assertFalse(cache2.get("key2")[0])
        
    def test_get_stats(self):
        """Test getting stats for all caches."""
        manager = get_cache_manager()
        
        # Get some caches and add data
        cache1 = manager.get_cache("test1")
        cache2 = manager.get_cache("test2")
        
        cache1.set("key1", "value1")
        cache2.set("key2", "value2")
        
        # Get a hit for cache1
        cache1.get("key1")
        
        # Get stats
        stats = manager.get_stats()
        
        # Verify stats
        self.assertIn("test1:memory", stats)
        self.assertIn("test2:memory", stats)
        self.assertEqual(stats["test1:memory"]["hits"], 1)
        self.assertEqual(stats["test2:memory"]["hits"], 0)


# Sample DAO for testing the cache mixin
class CachedUserDAO(DAOCacheMixin[User], BaseDAO[User]):
    """Sample DAO for testing the cache mixin."""
    
    def __init__(self, db_manager: DatabaseManager):
        BaseDAO.__init__(self, db_manager)
        DAOCacheMixin.__init__(self)
        self.table_name = 'users'
        self.pk_column = 'id'
        
    def _row_to_entity(self, row: Dict[str, Any]) -> User:
        """Convert a row to a User entity."""
        return User(
            id=row.get('id'),
            name=row.get('name', ''),
            call_sign=row.get('call_sign'),
            last_login=row.get('last_login'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
        
    def _entity_to_values(self, entity: User) -> Dict[str, Any]:
        """Convert a User entity to values for database operations."""
        values = {
            'name': entity.name,
            'call_sign': entity.call_sign,
            'last_login': entity.last_login
        }
        
        if entity.id is not None:
            values['id'] = entity.id
            
        return values


class TestDAOCacheMixin(unittest.TestCase):
    """Test case for the DAOCacheMixin."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary database
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_file.close()
        
        # Create a database manager
        self.db_manager = DatabaseManager(self.temp_file.name)
        
        # Create a cached DAO
        self.user_dao = CachedUserDAO(self.db_manager)
        
        # Create test data
        self._create_test_data()
        
        # Reset cache manager
        CacheManager._instance = None
        
    def tearDown(self):
        """Clean up after the test."""
        # Close database
        self.db_manager.close()
        
        # Remove temporary file
        try:
            os.unlink(self.temp_file.name)
        except (PermissionError, OSError):
            # On Windows, sometimes files can't be deleted immediately
            pass
            
    def _create_test_data(self):
        """Create test data in the database."""
        # Create users table
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            call_sign TEXT,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Add some test users
        self.user_dao.create(User(name="Test User 1", call_sign="TU1"))
        self.user_dao.create(User(name="Test User 2", call_sign="TU2"))
        self.user_dao.create(User(name="Test User 3", call_sign="TU3"))
        
    def test_find_by_id_caching(self):
        """Test caching for find_by_id method."""
        # Get the cache
        cache = self.user_dao._get_cache()
        
        # Clear any existing cache entries
        cache.clear()
        
        # First call should be a cache miss
        user1 = self.user_dao.find_by_id(1)
        self.assertEqual(user1.name, "Test User 1")
        
        # Get cache stats
        stats = cache.get_stats()
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["hits"], 0)
        
        # Second call should be a cache hit
        user1_again = self.user_dao.find_by_id(1)
        self.assertEqual(user1_again.name, "Test User 1")
        
        # Get updated stats
        stats = cache.get_stats()
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["hits"], 1)
        
    def test_find_all_caching(self):
        """Test caching for find_all method."""
        # Get the cache
        cache = self.user_dao._get_cache()
        
        # Clear any existing cache entries
        cache.clear()
        
        # First call should be a cache miss
        users = self.user_dao.find_all()
        self.assertEqual(len(users), 3)
        
        # Get cache stats
        stats = cache.get_stats()
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["hits"], 0)
        
        # Second call should be a cache hit
        users_again = self.user_dao.find_all()
        self.assertEqual(len(users_again), 3)
        
        # Get updated stats
        stats = cache.get_stats()
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["hits"], 1)
        
    def test_find_by_field_caching(self):
        """Test caching for find_by_field method."""
        # Get the cache
        cache = self.user_dao._get_cache()
        
        # Clear any existing cache entries
        cache.clear()
        
        # First call should be a cache miss
        users = self.user_dao.find_by_field("call_sign", "TU1")
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].name, "Test User 1")
        
        # Get cache stats
        stats = cache.get_stats()
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["hits"], 0)
        
        # Second call should be a cache hit
        users_again = self.user_dao.find_by_field("call_sign", "TU1")
        self.assertEqual(len(users_again), 1)
        self.assertEqual(users_again[0].name, "Test User 1")
        
        # Get updated stats
        stats = cache.get_stats()
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["hits"], 1)
        
    def test_create_invalidates_cache(self):
        """Test that creating a new entity invalidates the cache."""
        # Get the cache
        cache = self.user_dao._get_cache()
        
        # Clear any existing cache entries
        cache.clear()
        
        # Load all users into cache
        users = self.user_dao.find_all()
        self.assertEqual(len(users), 3)
        
        # Create a new user
        self.user_dao.create(User(name="Test User 4", call_sign="TU4"))
        
        # The cache should be invalidated, so this should be a miss
        users_after = self.user_dao.find_all()
        self.assertEqual(len(users_after), 4)
        
        # Get cache stats
        stats = cache.get_stats()
        self.assertEqual(stats["misses"], 2)
        self.assertEqual(stats["hits"], 0)
        
    def test_update_invalidates_cache(self):
        """Test that updating an entity invalidates the cache."""
        # Get the cache
        cache = self.user_dao._get_cache()
        
        # Clear any existing cache entries
        cache.clear()
        
        # Load a user into cache
        user1 = self.user_dao.find_by_id(1)
        self.assertEqual(user1.name, "Test User 1")
        
        # Update the user
        user1.name = "Updated User 1"
        self.user_dao.update(user1)
        
        # The cache should be invalidated, so this should be a miss
        user1_after = self.user_dao.find_by_id(1)
        self.assertEqual(user1_after.name, "Updated User 1")
        
        # Get cache stats
        stats = cache.get_stats()
        self.assertEqual(stats["misses"], 2)
        self.assertEqual(stats["hits"], 0)
        
    def test_delete_invalidates_cache(self):
        """Test that deleting an entity invalidates the cache."""
        # Get the cache
        cache = self.user_dao._get_cache()
        
        # Clear any existing cache entries
        cache.clear()
        
        # Load all users into cache
        users = self.user_dao.find_all()
        self.assertEqual(len(users), 3)
        
        # Delete a user
        self.user_dao.delete(1)
        
        # The cache should be invalidated, so this should be a miss
        users_after = self.user_dao.find_all()
        self.assertEqual(len(users_after), 2)
        
        # Get cache stats
        stats = cache.get_stats()
        self.assertEqual(stats["misses"], 2)
        self.assertEqual(stats["hits"], 0)
        
        # Verify user 1 is gone
        user1 = self.user_dao.find_by_id(1)
        self.assertIsNone(user1)
        
    def test_configure_cache(self):
        """Test configuring the cache for a DAO."""
        # Configure cache
        self.user_dao.configure_cache(enabled=False)
        
        # Cache should be disabled
        self.assertFalse(self.user_dao._cache_enabled)
        
        # Find by ID should not use cache
        user1 = self.user_dao.find_by_id(1)
        user1_again = self.user_dao.find_by_id(1)
        
        # Get cache - should be a NullCache
        cache = self.user_dao._get_cache()
        self.assertIsInstance(cache, NullCache)
        
        # Enable cache again
        self.user_dao.configure_cache(enabled=True, ttl=60)
        
        # Cache should be enabled
        self.assertTrue(self.user_dao._cache_enabled)
        self.assertEqual(self.user_dao._cache_ttl, 60)


# Function for testing cache decorators
counter = 0

@cacheable(cache_name="test_cache", ttl=60)
def expensive_calculation(a, b):
    """Sample expensive function for testing cacheable decorator."""
    global counter
    counter += 1
    return a + b
    
@invalidate_cache(cache_name="test_cache")
def invalidate_calculation():
    """Function that invalidates the test_cache."""
    global counter
    return counter
    
@multi_cache([
    {"cache_name": "cache1", "ttl": 30},
    {"cache_name": "cache2", "ttl": 60}
])
def multi_cached_function(x):
    """Function for testing multi_cache decorator."""
    global counter
    counter += 1
    return x * 2
    
@cache_result
def simple_cached_function(x):
    """Function for testing the simple cache_result decorator."""
    global counter
    counter += 1
    return x * 3


class TestCacheDecorators(unittest.TestCase):
    """Test case for the cache decorators."""
    
    def setUp(self):
        """Set up the test environment."""
        # Reset the singleton instance
        CacheManager._instance = None
        
        # Reset the counter
        global counter
        counter = 0
        
    def test_cacheable_decorator(self):
        """Test the cacheable decorator."""
        # First call should execute the function
        result1 = expensive_calculation(1, 2)
        self.assertEqual(result1, 3)
        self.assertEqual(counter, 1)
        
        # Second call with same args should use cache
        result2 = expensive_calculation(1, 2)
        self.assertEqual(result2, 3)
        self.assertEqual(counter, 1)  # Counter shouldn't change
        
        # Call with different args should execute again
        result3 = expensive_calculation(2, 3)
        self.assertEqual(result3, 5)
        self.assertEqual(counter, 2)
        
    def test_invalidate_cache_decorator(self):
        """Test the invalidate_cache decorator."""
        # Reset counter for this test
        global counter
        counter = 0
        
        # Call the function to cache result
        result1 = expensive_calculation(3, 4)
        self.assertEqual(result1, 7)
        self.assertEqual(counter, 1)
        
        # Call again to verify it's cached
        result2 = expensive_calculation(3, 4)
        self.assertEqual(result2, 7)
        self.assertEqual(counter, 1)  # Counter shouldn't change
        
        # Invalidate the cache
        invalidate_calculation()
        
        # Call again - should execute the function
        result3 = expensive_calculation(3, 4)
        self.assertEqual(result3, 7)
        self.assertEqual(counter, 2)  # Counter should change
        
    def test_multi_cache_decorator(self):
        """Test the multi_cache decorator."""
        # Reset counter for this test
        global counter
        counter = 0
        
        # First call should execute the function
        result1 = multi_cached_function(5)
        self.assertEqual(result1, 10)
        self.assertEqual(counter, 1)
        
        # Second call with same args should use cache
        result2 = multi_cached_function(5)
        self.assertEqual(result2, 10)
        self.assertEqual(counter, 1)  # Counter shouldn't change
        
        # Call with different args should execute again
        result3 = multi_cached_function(6)
        self.assertEqual(result3, 12)
        self.assertEqual(counter, 2)
        
    def test_cache_result_decorator(self):
        """Test the cache_result decorator."""
        # Reset counter for this test
        global counter
        counter = 0
        
        # First call should execute the function
        result1 = simple_cached_function(2)
        self.assertEqual(result1, 6)
        self.assertEqual(counter, 1)
        
        # Second call with same args should use cache
        result2 = simple_cached_function(2)
        self.assertEqual(result2, 6)
        self.assertEqual(counter, 1)  # Counter shouldn't change
        
        # Call with different args should execute again
        result3 = simple_cached_function(3)
        self.assertEqual(result3, 9)
        self.assertEqual(counter, 2)


if __name__ == "__main__":
    unittest.main()

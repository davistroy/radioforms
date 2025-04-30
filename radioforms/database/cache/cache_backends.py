#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cache backend implementations for database operations.

This module provides different cache backend implementations for storing
and retrieving cached data, with various storage mechanisms and features.
"""

import time
import pickle
import threading
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Set, Union
from pathlib import Path
import hashlib
import json
import weakref
from datetime import datetime, timedelta
from functools import lru_cache

# Configure logger
logger = logging.getLogger(__name__)


class CacheBackend(ABC):
    """
    Abstract base class for cache backend implementations.
    
    This class defines the interface that all cache backends must implement,
    providing methods for storing, retrieving, and invalidating cached data.
    """
    
    @abstractmethod
    def get(self, key: str) -> Tuple[bool, Any]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: Cache key to retrieve
            
        Returns:
            Tuple of (hit, value) where hit is True if the key was found, 
            and value is the cached value (or None if not found)
        """
        pass
        
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store a value in the cache.
        
        Args:
            key: Cache key to store
            value: Value to cache
            ttl: Time-to-live in seconds, or None for no expiration
        """
        pass
        
    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete a specific key from the cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if the key was deleted, False if it didn't exist
        """
        pass
        
    @abstractmethod
    def clear(self) -> None:
        """Clear all cached data."""
        pass
        
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary of cache statistics
        """
        pass
        
    @abstractmethod
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching a pattern.
        
        Args:
            pattern: Pattern to match cache keys against
            
        Returns:
            Number of keys invalidated
        """
        pass


class MemoryCache(CacheBackend):
    """
    In-memory cache implementation.
    
    This cache backend stores data in memory, with optional expiration.
    It provides fast access but data is lost when the process terminates.
    """
    
    def __init__(self, max_size: int = 10000, default_ttl: Optional[int] = None):
        """
        Initialize an in-memory cache.
        
        Args:
            max_size: Maximum number of items to store in the cache
            default_ttl: Default time-to-live for cached items in seconds
        """
        self._cache = {}  # Key -> (value, expiration_time)
        self._access_times = {}  # Key -> last access time
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = threading.RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0,
            "clears": 0
        }
        
    def get(self, key: str) -> Tuple[bool, Any]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: Cache key to retrieve
            
        Returns:
            Tuple of (hit, value) where hit is True if the key was found, 
            and value is the cached value (or None if not found)
        """
        with self._lock:
            current_time = time.time()
            
            if key in self._cache:
                value, expires_at = self._cache[key]
                
                # Check if expired
                if expires_at is not None and current_time > expires_at:
                    # Expired
                    del self._cache[key]
                    if key in self._access_times:
                        del self._access_times[key]
                    self._stats["misses"] += 1
                    return False, None
                    
                # Update access time
                self._access_times[key] = current_time
                self._stats["hits"] += 1
                return True, value
            else:
                self._stats["misses"] += 1
                return False, None
                
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store a value in the cache.
        
        Args:
            key: Cache key to store
            value: Value to cache
            ttl: Time-to-live in seconds, or None for no expiration
        """
        with self._lock:
            # Check cache size and evict if necessary
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._evict_one()
                
            current_time = time.time()
            
            # Calculate expiration time
            if ttl is None:
                ttl = self._default_ttl
                
            expires_at = None if ttl is None else current_time + ttl
            
            # Store value and update access time
            self._cache[key] = (value, expires_at)
            self._access_times[key] = current_time
            self._stats["sets"] += 1
            
    def delete(self, key: str) -> bool:
        """
        Delete a specific key from the cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if the key was deleted, False if it didn't exist
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
                self._stats["deletes"] += 1
                return True
            return False
            
    def clear(self) -> None:
        """Clear all cached data."""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
            self._stats["clears"] += 1
            
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary of cache statistics
        """
        with self._lock:
            stats = dict(self._stats)
            stats["size"] = len(self._cache)
            stats["max_size"] = self._max_size
            
            # Calculate hit rate
            total_requests = stats["hits"] + stats["misses"]
            stats["hit_rate"] = stats["hits"] / total_requests if total_requests > 0 else 0.0
            
            return stats
            
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching a pattern.
        
        Args:
            pattern: Pattern to match cache keys against (using simple substring matching)
            
        Returns:
            Number of keys invalidated
        """
        count = 0
        with self._lock:
            keys_to_delete = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
                count += 1
                
            self._stats["deletes"] += count
            return count
            
    def _evict_one(self) -> None:
        """Evict the least recently used item from the cache."""
        if not self._access_times:
            return
            
        # Find the least recently accessed key
        oldest_item = min(self._access_times.items(), key=lambda x: x[1])
        oldest_key = oldest_item[0]
        
        # Remove it from the cache
        if oldest_key in self._cache:
            del self._cache[oldest_key]
            del self._access_times[oldest_key]
            self._stats["evictions"] += 1
            logger.debug(f"Evicted cache key: {oldest_key}")


class DiskCache(CacheBackend):
    """
    Disk-based cache implementation.
    
    This cache backend stores data on disk, allowing it to persist between
    process restarts and handle larger datasets than memory-only caches.
    """
    
    def __init__(self, cache_dir: Union[str, Path], default_ttl: Optional[int] = None):
        """
        Initialize a disk-based cache.
        
        Args:
            cache_dir: Directory to store cache files
            default_ttl: Default time-to-live for cached items in seconds
        """
        self._cache_dir = Path(cache_dir)
        self._default_ttl = default_ttl
        self._metadata_file = self._cache_dir / "metadata.json"
        self._lock = threading.RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "clears": 0
        }
        
        # Create cache directory if it doesn't exist
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load metadata if it exists
        self._metadata = self._load_metadata()
        
    def get(self, key: str) -> Tuple[bool, Any]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: Cache key to retrieve
            
        Returns:
            Tuple of (hit, value) where hit is True if the key was found, 
            and value is the cached value (or None if not found)
        """
        cache_file = self._get_cache_file(key)
        metadata_key = self._hash_key(key)
        
        with self._lock:
            current_time = time.time()
            
            # Check if key exists in metadata and is not expired
            if metadata_key in self._metadata:
                expires_at = self._metadata[metadata_key].get("expires_at")
                
                if expires_at is not None and current_time > expires_at:
                    # Expired - remove from disk and metadata
                    self._remove_cache_file(cache_file)
                    del self._metadata[metadata_key]
                    self._save_metadata()
                    self._stats["misses"] += 1
                    return False, None
                    
                # Not expired, try to load from disk
                if cache_file.exists():
                    try:
                        with open(cache_file, "rb") as f:
                            value = pickle.load(f)
                            
                        # Update last access time
                        self._metadata[metadata_key]["last_accessed"] = current_time
                        self._save_metadata()
                        self._stats["hits"] += 1
                        return True, value
                    except (pickle.PickleError, IOError) as e:
                        # Error loading from disk
                        logger.warning(f"Error loading cache file {cache_file}: {e}")
                        self._stats["misses"] += 1
                        return False, None
                        
            # Not found or error
            self._stats["misses"] += 1
            return False, None
            
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store a value in the cache.
        
        Args:
            key: Cache key to store
            value: Value to cache
            ttl: Time-to-live in seconds, or None for no expiration
        """
        cache_file = self._get_cache_file(key)
        metadata_key = self._hash_key(key)
        
        with self._lock:
            current_time = time.time()
            
            # Calculate expiration time
            if ttl is None:
                ttl = self._default_ttl
                
            expires_at = None if ttl is None else current_time + ttl
            
            # Save value to disk
            try:
                # Ensure parent directories exist
                cache_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(cache_file, "wb") as f:
                    pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)
                    
                # Update metadata
                self._metadata[metadata_key] = {
                    "key": key,
                    "created_at": current_time,
                    "last_accessed": current_time,
                    "expires_at": expires_at,
                    "file_path": str(cache_file.relative_to(self._cache_dir))
                }
                
                self._save_metadata()
                self._stats["sets"] += 1
            except (pickle.PickleError, IOError) as e:
                logger.error(f"Error writing to cache file {cache_file}: {e}")
                
    def delete(self, key: str) -> bool:
        """
        Delete a specific key from the cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if the key was deleted, False if it didn't exist
        """
        cache_file = self._get_cache_file(key)
        metadata_key = self._hash_key(key)
        
        with self._lock:
            if metadata_key in self._metadata:
                # Remove from disk
                self._remove_cache_file(cache_file)
                
                # Remove from metadata
                del self._metadata[metadata_key]
                self._save_metadata()
                
                self._stats["deletes"] += 1
                return True
                
            return False
            
    def clear(self) -> None:
        """Clear all cached data."""
        with self._lock:
            # Clear all cache files
            for item in self._metadata.values():
                file_path = item.get("file_path")
                if file_path:
                    file_path = self._cache_dir / file_path
                    self._remove_cache_file(file_path)
                    
            # Clear metadata
            self._metadata.clear()
            self._save_metadata()
            
            self._stats["clears"] += 1
            
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary of cache statistics
        """
        with self._lock:
            stats = dict(self._stats)
            stats["size"] = len(self._metadata)
            
            # Calculate hit rate
            total_requests = stats["hits"] + stats["misses"]
            stats["hit_rate"] = stats["hits"] / total_requests if total_requests > 0 else 0.0
            
            # Calculate disk usage
            try:
                disk_usage = sum(f.stat().st_size for f in self._cache_dir.glob("**/*") if f.is_file())
                stats["disk_usage_bytes"] = disk_usage
                stats["disk_usage_mb"] = disk_usage / (1024 * 1024)
            except Exception as e:
                logger.warning(f"Error calculating disk usage: {e}")
                stats["disk_usage_bytes"] = 0
                stats["disk_usage_mb"] = 0
                
            return stats
            
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching a pattern.
        
        Args:
            pattern: Pattern to match cache keys against (simple substring matching)
            
        Returns:
            Number of keys invalidated
        """
        count = 0
        with self._lock:
            # Find all metadata keys with matching original keys
            items_to_delete = []
            for metadata_key, item in self._metadata.items():
                if pattern in item.get("key", ""):
                    items_to_delete.append((metadata_key, item))
                    
            # Delete matching items
            for metadata_key, item in items_to_delete:
                file_path = item.get("file_path")
                if file_path:
                    file_path = self._cache_dir / file_path
                    self._remove_cache_file(file_path)
                    
                del self._metadata[metadata_key]
                count += 1
                
            if count > 0:
                self._save_metadata()
                self._stats["deletes"] += count
                
            return count
            
    def _get_cache_file(self, key: str) -> Path:
        """
        Get the file path for a cache key.
        
        Args:
            key: Cache key
            
        Returns:
            Path object for the cache file
        """
        # Use a hashed filename to avoid filesystem issues
        hashed_key = self._hash_key(key)
        
        # Split into subdirectories to avoid too many files in one directory
        sub_dir = hashed_key[:2]
        return self._cache_dir / sub_dir / f"{hashed_key}.cache"
        
    def _hash_key(self, key: str) -> str:
        """
        Hash a cache key for use in filenames and metadata.
        
        Args:
            key: Cache key
            
        Returns:
            Hashed key string
        """
        return hashlib.md5(key.encode('utf-8')).hexdigest()
        
    def _remove_cache_file(self, path: Path) -> None:
        """
        Remove a cache file if it exists.
        
        Args:
            path: Path to the cache file
        """
        try:
            if path.exists():
                path.unlink()
        except OSError as e:
            logger.warning(f"Error removing cache file {path}: {e}")
            
    def _load_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        Load metadata from disk.
        
        Returns:
            Dictionary of cache metadata
        """
        if self._metadata_file.exists():
            try:
                with open(self._metadata_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Error loading cache metadata: {e}")
                
        return {}
        
    def _save_metadata(self) -> None:
        """Save metadata to disk."""
        try:
            with open(self._metadata_file, "w") as f:
                json.dump(self._metadata, f)
        except IOError as e:
            logger.error(f"Error saving cache metadata: {e}")


class NullCache(CacheBackend):
    """
    No-op cache implementation.
    
    This cache backend doesn't actually cache anything. It's useful for
    disabling caching without changing code.
    """
    
    def __init__(self):
        """Initialize a null cache."""
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "clears": 0
        }
        
    def get(self, key: str) -> Tuple[bool, Any]:
        """
        Retrieve a value from the cache (always returns miss).
        
        Args:
            key: Cache key to retrieve
            
        Returns:
            Tuple of (False, None) indicating cache miss
        """
        self._stats["misses"] += 1
        return False, None
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store a value in the cache (no-op).
        
        Args:
            key: Cache key to store
            value: Value to cache
            ttl: Time-to-live in seconds, or None for no expiration
        """
        self._stats["sets"] += 1
        
    def delete(self, key: str) -> bool:
        """
        Delete a specific key from the cache (no-op).
        
        Args:
            key: Cache key to delete
            
        Returns:
            False as nothing is ever actually cached
        """
        self._stats["deletes"] += 1
        return False
        
    def clear(self) -> None:
        """Clear all cached data (no-op)."""
        self._stats["clears"] += 1
        
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary of cache statistics
        """
        stats = dict(self._stats)
        stats["size"] = 0
        stats["hit_rate"] = 0.0
        return stats
        
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching a pattern (no-op).
        
        Args:
            pattern: Pattern to match cache keys against
            
        Returns:
            0 as nothing is ever actually cached
        """
        return 0

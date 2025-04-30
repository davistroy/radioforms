#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cache manager for database operations.

This module provides a centralized manager for cache instances,
allowing for configuration and retrieval of caches throughout the application.
"""

import os
import logging
from typing import Dict, Any, Optional, Union, Type
from pathlib import Path

from radioforms.database.cache.cache_backends import (
    CacheBackend, 
    MemoryCache, 
    DiskCache, 
    NullCache
)

# Configure logger
logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manager for cache instances.
    
    This class provides a centralized way to create, configure, and
    retrieve cache instances for different parts of the application.
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'CacheManager':
        """
        Get the singleton instance of CacheManager.
        
        Returns:
            CacheManager instance
        """
        if cls._instance is None:
            cls._instance = CacheManager()
        return cls._instance
        
    def __init__(self):
        """Initialize the cache manager."""
        self._caches = {}  # name -> cache instance
        self._config = {
            "default_backend": "memory",
            "default_ttl": 300,  # 5 minutes
            "enabled": True,
            "memory_cache": {
                "max_size": 10000
            },
            "disk_cache": {
                "base_dir": None  # Default will be set in _get_default_cache_dir()
            }
        }
        
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the cache manager.
        
        Args:
            config: Dictionary of configuration options
        """
        # Update the configuration
        for key, value in config.items():
            if key in self._config:
                if isinstance(self._config[key], dict) and isinstance(value, dict):
                    # Merge dictionaries for nested configs
                    self._config[key].update(value)
                else:
                    # Replace non-dict values
                    self._config[key] = value
                    
        # Log configuration changes
        logger.info(f"Cache manager configured: {self._config}")
        
    def get_cache(self, name: str = "default", backend: Optional[str] = None, 
                  ttl: Optional[int] = None) -> CacheBackend:
        """
        Get a cache instance.
        
        Args:
            name: Name of the cache instance
            backend: Optional backend type ("memory", "disk", "null"), 
                    defaults to the configured default_backend
            ttl: Optional time-to-live in seconds,
                defaults to the configured default_ttl
                
        Returns:
            Cache instance
        """
        # Check if caching is enabled
        if not self._config["enabled"]:
            return NullCache()
            
        # Generate a unique cache key
        cache_key = f"{name}:{backend or self._config['default_backend']}"
        
        # Return existing cache if available
        if cache_key in self._caches:
            return self._caches[cache_key]
            
        # Create new cache instance
        backend_type = backend or self._config["default_backend"]
        cache_ttl = ttl if ttl is not None else self._config["default_ttl"]
        
        if backend_type == "memory":
            # Create memory cache
            max_size = self._config["memory_cache"]["max_size"]
            cache = MemoryCache(max_size=max_size, default_ttl=cache_ttl)
        elif backend_type == "disk":
            # Create disk cache
            base_dir = self._config["disk_cache"].get("base_dir") or self._get_default_cache_dir()
            cache_dir = Path(base_dir) / name
            cache = DiskCache(cache_dir=cache_dir, default_ttl=cache_ttl)
        elif backend_type == "null":
            # Create null cache (no caching)
            cache = NullCache()
        else:
            # Unknown backend, use null cache
            logger.warning(f"Unknown cache backend: {backend_type}")
            cache = NullCache()
            
        # Store and return the cache
        self._caches[cache_key] = cache
        return cache
        
    def clear_all_caches(self) -> None:
        """Clear all cache instances."""
        for cache in self._caches.values():
            cache.clear()
            
        logger.info("All caches cleared")
        
    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all cache instances.
        
        Returns:
            Dictionary mapping cache names to stats dictionaries
        """
        return {name: cache.get_stats() for name, cache in self._caches.items()}
        
    def _get_default_cache_dir(self) -> Path:
        """
        Get the default directory for disk caches.
        
        Returns:
            Path object for the cache directory
        """
        # Check if the application has a data directory
        app_data_dir = os.environ.get("RADIOFORMS_DATA_DIR")
        if app_data_dir:
            base_dir = Path(app_data_dir) / "cache"
        else:
            # Fall back to a platform-appropriate location
            if os.name == "nt":  # Windows
                base_dir = Path(os.environ.get("LOCALAPPDATA", "C:/Temp")) / "RadioForms" / "cache"
            else:  # Unix-like
                base_dir = Path(os.environ.get("XDG_CACHE_HOME", 
                                             Path.home() / ".cache")) / "radioforms"
                                             
        # Create the directory if it doesn't exist
        base_dir.mkdir(parents=True, exist_ok=True)
        
        return base_dir


# Convenience function to get the cache manager
def get_cache_manager() -> CacheManager:
    """
    Get the singleton instance of the CacheManager.
    
    Returns:
        CacheManager instance
    """
    return CacheManager.get_instance()

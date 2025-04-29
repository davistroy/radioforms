#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Application configuration management.
"""

import os
import json
import configparser
from pathlib import Path


class AppConfig:
    """
    Manages application configuration settings with support for default values,
    user-specific overrides, and persistent storage.
    """
    
    DEFAULT_CONFIG = {
        "application": {
            "name": "RadioForms",
            "version": "0.1.0",
        },
        "database": {
            "path": str(Path.home() / "radioforms.db"),
            "wal_mode": True,
        },
        "ui": {
            "theme": "default",
            "font_size": 12,
        },
        "forms": {
            "auto_save": True,
            "auto_save_interval": 60,  # seconds
        }
    }
    
    def __init__(self):
        """Initialize configuration with defaults and load user settings."""
        # Set up paths
        self.app_dir = self._get_app_directory()
        self.config_file = self.app_dir / "config.json"
        
        # Initialize with defaults
        self.config = self.DEFAULT_CONFIG.copy()
        
        # Load user config if it exists
        self._load_config()
        
    def _get_app_directory(self):
        """Get or create the application data directory."""
        home = Path.home()
        
        # Platform-specific app data directory
        if os.name == 'nt':  # Windows
            app_dir = home / "AppData" / "Local" / "RadioForms"
        else:  # macOS, Linux, etc.
            app_dir = home / ".radioforms"
            
        # Create directory if it doesn't exist
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir
        
    def _load_config(self):
        """Load configuration from the config file if it exists."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                
                # Update default config with user settings
                self._update_config_recursive(self.config, user_config)
            except Exception as e:
                # In a real app, this would use the error handling system
                print(f"Error loading configuration: {e}")
                
    def _update_config_recursive(self, target, source):
        """Recursively update configuration dictionaries."""
        for key, value in source.items():
            if isinstance(value, dict) and key in target:
                self._update_config_recursive(target[key], value)
            else:
                target[key] = value
                
    def save(self):
        """Save the current configuration to disk."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            # In a real app, this would use the error handling system
            print(f"Error saving configuration: {e}")
            
    def get(self, section, key, default=None):
        """
        Get a configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            default: Value to return if the key is not found
            
        Returns:
            The configuration value or default if not found
        """
        try:
            return self.config[section][key]
        except KeyError:
            return default
            
    def set(self, section, key, value):
        """
        Set a configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Value to set
        """
        # Create section if it doesn't exist
        if section not in self.config:
            self.config[section] = {}
            
        self.config[section][key] = value

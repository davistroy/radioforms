#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Application configuration module.

This module provides access to application configuration settings from
a configuration file or environment variables.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional


class AppConfig:
    """
    Application configuration class.
    
    This class provides access to application configuration settings,
    with support for loading from a config file and environment variables.
    """
    
    # Default configuration settings
    DEFAULT_CONFIG = {
        'application': {
            'name': 'RadioForms',
            'version': '0.1.0',
            'data_dir': os.path.expanduser('~/.radioforms'),
            'log_level': 'INFO'
        },
        'database': {
            'path': os.path.expanduser('~/.radioforms/radioforms.db'),
            'backup_dir': os.path.expanduser('~/.radioforms/backups')
        },
        'ui': {
            'theme': 'system',
            'font_size': 10,
            'show_tooltips': True
        },
        'forms': {
            'autosave_interval': 300,  # seconds
            'default_save_dir': os.path.expanduser('~/Documents/RadioForms')
        },
        'network': {
            'api_url': '',
            'timeout': 30,
            'retry_attempts': 3
        }
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the application configuration.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        # Initialize with default configuration
        self.config = self.DEFAULT_CONFIG.copy()
        
        # Create configuration directory if it doesn't exist
        config_dir = Path(self.config['application']['data_dir'])
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # If config file is not specified, use default location
        if config_file is None:
            config_file = os.path.join(
                self.config['application']['data_dir'],
                'config.json'
            )
        
        # Load configuration from file if it exists
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                self._merge_config(file_config)
            except Exception as e:
                logging.warning(f"Error loading configuration file: {e}")
        
        # Override with environment variables
        self._load_from_env()
    
    def _merge_config(self, config: Dict[str, Any]):
        """
        Merge a configuration dictionary with the current configuration.
        
        Args:
            config: Configuration dictionary to merge
        """
        for section, section_config in config.items():
            if section in self.config:
                if isinstance(section_config, dict) and isinstance(self.config[section], dict):
                    self.config[section].update(section_config)
                else:
                    self.config[section] = section_config
            else:
                self.config[section] = section_config
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Environment variables are expected to be in the format:
        # RADIOFORMS_SECTION_KEY=value
        
        prefix = 'RADIOFORMS_'
        for key, value in os.environ.items():
            if key.startswith(prefix):
                parts = key[len(prefix):].lower().split('_', 1)
                if len(parts) == 2:
                    section, option = parts
                    if section in self.config and option in self.config[section]:
                        # Convert value to the appropriate type
                        current_value = self.config[section][option]
                        if isinstance(current_value, bool):
                            self.config[section][option] = value.lower() in ('true', 'yes', '1')
                        elif isinstance(current_value, int):
                            try:
                                self.config[section][option] = int(value)
                            except ValueError:
                                pass
                        elif isinstance(current_value, float):
                            try:
                                self.config[section][option] = float(value)
                            except ValueError:
                                pass
                        else:
                            # String or other type
                            self.config[section][option] = value
    
    def get(self, section: str, option: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            section: Configuration section
            option: Configuration option
            default: Default value if not found
            
        Returns:
            Configuration value, or default if not found
        """
        try:
            return self.config[section][option]
        except KeyError:
            return default
    
    def set(self, section: str, option: str, value: Any):
        """
        Set a configuration value.
        
        Args:
            section: Configuration section
            option: Configuration option
            value: Value to set
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][option] = value
    
    def save(self, config_file: Optional[str] = None):
        """
        Save configuration to a file.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        if config_file is None:
            config_file = os.path.join(
                self.config['application']['data_dir'],
                'config.json'
            )
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")
            return False
    
    def get_database_path(self) -> str:
        """
        Get the database path.
        
        Returns:
            Database path
        """
        return self.get('database', 'path')
    
    def get_data_dir(self) -> str:
        """
        Get the application data directory.
        
        Returns:
            Application data directory
        """
        return self.get('application', 'data_dir')

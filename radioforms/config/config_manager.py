#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration Manager for RadioForms.

This module provides a configuration manager for RadioForms that handles
reading, writing, and managing application configuration settings.
"""

import os
import sys
import logging
import configparser
from pathlib import Path
from typing import Dict, Any, Optional, List, Union


class ConfigManager:
    """
    Configuration manager for RadioForms.
    
    This class handles reading, writing, and managing application
    configuration settings. It provides a simple interface for accessing
    and modifying configuration values with default fallbacks.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self._config_path = config_path
        self._config = configparser.ConfigParser()
        self._logger = logging.getLogger(__name__)
        
        # Load configuration if file exists
        self._load()
        
    def _load(self):
        """Load configuration from the file."""
        if os.path.exists(self._config_path):
            try:
                self._config.read(self._config_path)
                self._logger.info(f"Configuration loaded from {self._config_path}")
            except Exception as e:
                self._logger.error(f"Failed to load configuration: {e}")
        else:
            self._logger.info(f"Configuration file {self._config_path} does not exist, using defaults")
            
    def save(self):
        """Save configuration to the file."""
        try:
            # Ensure the directory exists
            config_dir = os.path.dirname(self._config_path)
            os.makedirs(config_dir, exist_ok=True)
            
            # Write the configuration to the file
            with open(self._config_path, 'w') as config_file:
                self._config.write(config_file)
                
            self._logger.info(f"Configuration saved to {self._config_path}")
            return True
        except Exception as e:
            self._logger.error(f"Failed to save configuration: {e}")
            return False
            
    def get_value(self, section: str, key: str, default: str = "") -> str:
        """
        Get a configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if section/key doesn't exist
            
        Returns:
            The configuration value, or the default if not found
        """
        try:
            if section in self._config and key in self._config[section]:
                return self._config[section][key]
            else:
                return default
        except Exception as e:
            self._logger.error(f"Failed to get configuration value {section}.{key}: {e}")
            return default
            
    def set_value(self, section: str, key: str, value: str):
        """
        Set a configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Value to set
        """
        try:
            # Create section if it doesn't exist
            if section not in self._config:
                self._config[section] = {}
                
            # Set the value
            self._config[section][key] = str(value)
            
            self._logger.debug(f"Configuration value {section}.{key} set to {value}")
        except Exception as e:
            self._logger.error(f"Failed to set configuration value {section}.{key}: {e}")
            
    def get_boolean(self, section: str, key: str, default: bool = False) -> bool:
        """
        Get a boolean configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if section/key doesn't exist
            
        Returns:
            The configuration value as a boolean, or the default if not found
        """
        value = self.get_value(section, key, str(default)).lower()
        return value in ["true", "yes", "1", "t", "y"]
        
    def get_int(self, section: str, key: str, default: int = 0) -> int:
        """
        Get an integer configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if section/key doesn't exist
            
        Returns:
            The configuration value as an integer, or the default if not found
        """
        try:
            return int(self.get_value(section, key, str(default)))
        except ValueError:
            return default
            
    def get_float(self, section: str, key: str, default: float = 0.0) -> float:
        """
        Get a float configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if section/key doesn't exist
            
        Returns:
            The configuration value as a float, or the default if not found
        """
        try:
            return float(self.get_value(section, key, str(default)))
        except ValueError:
            return default
            
    def get_list(self, section: str, key: str, default: List[str] = None) -> List[str]:
        """
        Get a list configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if section/key doesn't exist
            
        Returns:
            The configuration value as a list, or the default if not found
        """
        if default is None:
            default = []
            
        value = self.get_value(section, key, "")
        if not value:
            return default
            
        # Split the value by commas
        return [item.strip() for item in value.split(",")]
        
    def get_sections(self) -> List[str]:
        """
        Get all configuration sections.
        
        Returns:
            List of section names
        """
        return list(self._config.sections())
        
    def get_section_values(self, section: str) -> Dict[str, str]:
        """
        Get all values in a section.
        
        Args:
            section: Configuration section
            
        Returns:
            Dictionary of key-value pairs in the section
        """
        if section in self._config:
            return dict(self._config[section])
        else:
            return {}
            
    def remove_section(self, section: str):
        """
        Remove a configuration section.
        
        Args:
            section: Configuration section to remove
        """
        if section in self._config:
            self._config.remove_section(section)
            
    def remove_option(self, section: str, key: str):
        """
        Remove a configuration option.
        
        Args:
            section: Configuration section
            key: Configuration key to remove
        """
        if section in self._config and key in self._config[section]:
            self._config.remove_option(section, key)


def load_default_config() -> ConfigManager:
    """
    Load the default application configuration.
    
    Returns:
        ConfigManager instance with default configuration
    """
    # Determine config path
    config_dir = Path.home() / ".radioforms"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = str(config_dir / "config.ini")
    
    # Create config manager
    config_manager = ConfigManager(config_path)
    
    # Set default values if not already set
    if not config_manager.get_value("General", "first_run"):
        config_manager.set_value("General", "first_run", "true")
        
    if not config_manager.get_value("Database", "path"):
        # Default database path
        documents_path = Path.home() / "Documents" / "RadioForms"
        documents_path.mkdir(parents=True, exist_ok=True)
        db_path = str(documents_path / "radioforms.db")
        config_manager.set_value("Database", "path", db_path)
        
    if not config_manager.get_value("Database", "auto_backup"):
        config_manager.set_value("Database", "auto_backup", "true")
        
    if not config_manager.get_value("Forms", "enabled_forms"):
        # Default enabled forms
        enabled_forms = ["ICS-213", "ICS-214", "ICS-309"]
        config_manager.set_value("Forms", "enabled_forms", ",".join(enabled_forms))
        
    # Save config if any defaults were applied
    config_manager.save()
    
    return config_manager

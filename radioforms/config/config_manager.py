#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration manager for application settings and user profiles.

This module provides functionality for storing and retrieving configuration
settings, managing user profiles, and handling application startup settings.
"""

import ctypes
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from radioforms.database.dao.setting_dao import SettingDAO
from radioforms.database.dao.user_dao import UserDAO
from radioforms.database.db_manager import DatabaseManager
from radioforms.database.models.setting import Setting


class ConfigManager:
    """
    Manages application configuration settings and user profiles.
    
    This class handles the storage and retrieval of application settings,
    user profile information, and configuration data in the database.
    """
    
    # Configuration key constants
    FIRST_RUN = "app.first_run"
    LAST_USER_ID = "app.last_user_id"
    LAST_INCIDENT_ID = "app.last_incident_id"
    APP_VERSION = "app.version"
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the configuration manager.
        
        Args:
            db_manager: Database manager instance for data storage
        """
        self.db_manager = db_manager
        self.setting_dao = SettingDAO(db_manager)
        self.user_dao = UserDAO(db_manager)
        self.cache = {}  # Simple cache for frequently accessed settings
        
        # Initialize with default configuration if needed
        self._init_config()
    
    def _init_config(self):
        """Initialize default configuration if this is the first run."""
        # Check if the first run flag is set
        first_run = self.get_setting(self.FIRST_RUN, None)
        
        if first_run is None:
            # This is the first run, set up default configuration
            with self.db_manager.transaction():
                # Set the first run flag to False for future runs
                self.set_setting(self.FIRST_RUN, "false")
                
                # Set the application version
                self.set_setting(self.APP_VERSION, "0.1.0")
                
                # Log initialization
                logging.info("Initialized default configuration")
    
    def is_first_run(self) -> bool:
        """
        Check if this is the first run of the application.
        
        Returns:
            True if this is the first run, False otherwise
        """
        first_run = self.get_setting(self.FIRST_RUN, None)
        return first_run is None or first_run.lower() == "true"
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration setting value.
        
        Args:
            key: Setting key
            default: Default value if setting is not found
            
        Returns:
            Setting value, or default if not found
        """
        # Check cache first
        if key in self.cache:
            return self.cache[key]
        
        # Query the database
        setting = self.setting_dao.get_by_key(key)
        
        if setting:
            # Cache the result for future use
            self.cache[key] = setting.value
            return setting.value
        
        return default
    
    def set_setting(self, key: str, value: Any) -> bool:
        """
        Set a configuration setting value.
        
        Args:
            key: Setting key
            value: Setting value
            
        Returns:
            True if successful, False otherwise
        """
        # Update cache
        self.cache[key] = value
        
        # Check if setting exists
        setting_obj = self.setting_dao.get_by_key(key)
        
        if setting_obj:
            # Update existing setting
            setting_obj.value = value
            setting_obj.updated_at = datetime.now()
            # Pass the updated entity directly to the update method
            result = self.setting_dao.update(setting_obj)
            return result is not None
        else:
            # Create new setting
            new_setting = Setting(
                key=key,
                value=value,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            setting_id = self.setting_dao.create(new_setting)
            return setting_id is not None
    
    def clear_cache(self):
        """Clear the configuration cache."""
        self.cache = {}
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get the current user profile.
        
        Returns:
            Current user profile, or None if not set
        """
        user_id = self.get_setting(self.LAST_USER_ID)
        if not user_id:
            return None
        
        try:
            user_id = int(user_id)
            return self.user_dao.get_by_id(user_id)
        except (ValueError, TypeError):
            return None
    
    def set_current_user(self, user_id: int) -> bool:
        """
        Set the current user profile.
        
        Args:
            user_id: User ID to set as current
            
        Returns:
            True if successful, False otherwise
        """
        return self.set_setting(self.LAST_USER_ID, str(user_id))
    
    def get_users(self) -> List[Dict[str, Any]]:
        """
        Get all user profiles.
        
        Returns:
            List of user profiles
        """
        return self.user_dao.find_all()
    
    def create_or_update_user(self, user_data: Dict[str, Any]) -> Optional[int]:
        """
        Create a new user profile or update an existing one.
        
        Args:
            user_data: User profile data
            
        Returns:
            User ID if successful, None otherwise
        """
        user_id = user_data.get('id')
        
        with self.db_manager.transaction():
            if user_id:
                # Update existing user
                user_data['updated_at'] = datetime.now()
                # Convert to a User object before updating
                from radioforms.database.models.user import User
                user_obj = User(
                    id=user_id,
                    name=user_data.get('name', ''),
                    call_sign=user_data.get('call_sign'),
                    last_login=user_data.get('last_login'),
                    created_at=user_data.get('created_at'),
                    updated_at=user_data.get('updated_at')
                )
                result = self.user_dao.update(user_obj)
                return user_id if result else None
            else:
                # Create new user
                user_data['created_at'] = datetime.now()
                user_data['updated_at'] = datetime.now()
                # Convert to a User object before creating
                from radioforms.database.models.user import User
                user_obj = User(
                    name=user_data.get('name', ''),
                    call_sign=user_data.get('call_sign'),
                    last_login=user_data.get('last_login'),
                    created_at=user_data.get('created_at'),
                    updated_at=user_data.get('updated_at')
                )
                return self.user_dao.create(user_obj)
    
    def validate_database(self) -> Tuple[bool, List[str]]:
        """
        Validate the database structure and integrity.
        
        Returns:
            Tuple of (success, error_messages)
        """
        errors = []
        
        try:
            # Check that we can query settings
            self.setting_dao.find_all()
            
            # Check that we can query users
            self.user_dao.find_all()
            
        except Exception as e:
            errors.append(f"Database validation error: {str(e)}")
            return False, errors
        
        return len(errors) == 0, errors


class SystemIntegrityChecker:
    """
    Checks the integrity of the application system.
    
    This class provides functionality to verify the integrity of the
    application, including file system access, disk space, and
    database connection.
    """
    
    def __init__(self, db_manager: DatabaseManager, app_directory: str):
        """
        Initialize the system integrity checker.
        
        Args:
            db_manager: Database manager instance
            app_directory: Application directory path
        """
        self.db_manager = db_manager
        self.app_directory = Path(app_directory)
    
    def check_file_system_access(self) -> Tuple[bool, List[str]]:
        """
        Check if the application has access to the file system.
        
        Returns:
            Tuple of (success, error_messages)
        """
        errors = []
        
        # Check if the application directory exists and is readable
        if not self.app_directory.exists():
            errors.append(f"Application directory does not exist: {self.app_directory}")
            return False, errors
        
        if not os.access(self.app_directory, os.R_OK):
            errors.append(f"Cannot read from application directory: {self.app_directory}")
            return False, errors
        
        # Check write access by creating a temporary file
        test_file = self.app_directory / f".test_{time.time()}"
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            errors.append(f"Cannot write to application directory: {str(e)}")
            return False, errors
        
        return True, []
    
    def check_disk_space(self, min_free_mb: int = 100) -> Tuple[bool, List[str]]:
        """
        Check if there is enough disk space available.
        
        Args:
            min_free_mb: Minimum required free space in MB
            
        Returns:
            Tuple of (success, error_messages)
        """
        errors = []
        
        try:
            # Get free space on the drive where the application is located
            if os.name == 'nt':  # Windows
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(str(self.app_directory)),
                    None, None,
                    ctypes.byref(free_bytes)
                )
                free_mb = free_bytes.value / (1024 * 1024)
            else:  # Unix-like
                stat = os.statvfs(self.app_directory)
                free_mb = (stat.f_frsize * stat.f_bavail) / (1024 * 1024)
            
            if free_mb < min_free_mb:
                errors.append(
                    f"Insufficient disk space: {free_mb:.1f} MB available, "
                    f"{min_free_mb} MB required"
                )
                return False, errors
                
        except Exception as e:
            errors.append(f"Error checking disk space: {str(e)}")
            return False, errors
        
        return True, []
    
    def check_database_connection(self) -> Tuple[bool, List[str]]:
        """
        Check if the database connection is working.
        
        Returns:
            Tuple of (success, error_messages)
        """
        errors = []
        
        try:
            # Execute a simple query to verify connection
            cursor = self.db_manager.execute("SELECT 1")
            result = cursor.fetchone()
            
            if result is None or result[0] != 1:
                errors.append("Database connection test failed")
                return False, errors
                
        except Exception as e:
            errors.append(f"Database connection error: {str(e)}")
            return False, errors
        
        return True, []
    
    def check_all(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Run all integrity checks.
        
        Returns:
            Tuple of (success, results_dict)
        """
        results = {}
        
        # Check file system access
        fs_success, fs_errors = self.check_file_system_access()
        results['file_system'] = {
            'success': fs_success,
            'errors': fs_errors
        }
        
        # Check disk space
        disk_success, disk_errors = self.check_disk_space()
        results['disk_space'] = {
            'success': disk_success,
            'errors': disk_errors
        }
        
        # Check database connection
        db_success, db_errors = self.check_database_connection()
        results['database'] = {
            'success': db_success,
            'errors': db_errors
        }
        
        # Check if all checks passed
        all_success = fs_success and disk_success and db_success
        
        return all_success, results

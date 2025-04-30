#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setting Data Access Object (DAO) for database operations related to application settings.
"""

from typing import Any, Dict, List, Optional, Union, overload
from datetime import datetime

from radioforms.database.dao.base_dao import BaseDAO, DAOException
from radioforms.database.models.setting import Setting
from radioforms.database.db_manager import DatabaseManager
from radioforms.database.dao.dao_cache_mixin import DAOCacheMixin


class SettingDAO(DAOCacheMixin[Setting], BaseDAO[Setting]):
    """
    Data Access Object for Setting entities, providing database operations
    for creating, retrieving, updating, and deleting application settings.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the SettingDAO with a database manager.
        
        Args:
            db_manager: Database manager for database operations
        """
        BaseDAO.__init__(self, db_manager)
        DAOCacheMixin.__init__(self)
        self.table_name = "settings"
        self.pk_column = "id"
        
    def _row_to_entity(self, row: Dict[str, Any]) -> Setting:
        """
        Convert a database row to a Setting entity.
        
        Args:
            row: Dictionary containing column names and values
            
        Returns:
            A Setting entity
        """
        return Setting(
            id=row.get('id'),
            key=row.get('key', ''),
            value=row.get('value'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
        
    def _entity_to_values(self, entity: Setting) -> Dict[str, Any]:
        """
        Convert a Setting entity to a dictionary of column values.
        
        Args:
            entity: The Setting entity
            
        Returns:
            Dictionary containing column names and values
        """
        values = {
            'key': entity.key,
            'value': entity._value,  # Use _value directly to avoid deserialization
            'created_at': entity.created_at,
            'updated_at': entity.updated_at
        }
        
        if entity.id is not None:
            values['id'] = entity.id
            
        return values
        
    @overload
    def find_by_key(self, key: str) -> Optional[Setting]:
        ...
        
    @overload
    def find_by_key(self, key: str, as_dict: bool = False) -> Optional[Dict[str, Any]]:
        ...
        
    def find_by_key(self, key: str, as_dict: bool = False) -> Optional[Union[Setting, Dict[str, Any]]]:
        """
        Find a setting by its key.
        
        Args:
            key: The setting key
            as_dict: When True, return a dictionary instead of an entity object
            
        Returns:
            The setting if found (as object or dictionary based on as_dict), None otherwise
        """
        query = f"SELECT * FROM {self.table_name} WHERE key = ?"
        cursor = self.db_manager.execute(query, (key,))
        row = cursor.fetchone()
        
        if row:
            row_dict = dict(row)
            return row_dict if as_dict else self._row_to_entity(row_dict)
        return None
        
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value by its key, with an optional default.
        
        Args:
            key: The setting key
            default: Default value to return if the setting is not found
            
        Returns:
            The setting value if found, default otherwise
        """
        setting = self.find_by_key(key)
        if setting:
            return setting.value
        return default
        
    def set_value(self, key: str, value: Any) -> Setting:
        """
        Set a setting value, creating it if it doesn't exist.
        
        Args:
            key: The setting key
            value: The setting value
            
        Returns:
            The updated or created Setting entity
        """
        # First, check if the setting exists
        setting = self.find_by_key(key)
        
        if setting:
            # Update existing setting
            setting.value = value
            self.update(setting)
        else:
            # Create new setting
            setting = Setting(key=key, value=value)
            setting_id = self.create(setting)
            setting.id = setting_id
            
        return setting
        
    def delete_by_key(self, key: str) -> bool:
        """
        Delete a setting by its key.
        
        Args:
            key: The setting key
            
        Returns:
            True if the setting was deleted, False otherwise
        """
        query = f"DELETE FROM {self.table_name} WHERE key = ?"
        cursor = self.db_manager.execute(query, (key,))
        self.db_manager.commit()
        
        return cursor.rowcount > 0
        
    def get_settings_by_prefix(self, prefix: str) -> List[Setting]:
        """
        Get all settings with keys that start with a specific prefix.
        
        Args:
            prefix: The key prefix to match
            
        Returns:
            List of matching settings
        """
        query = f"SELECT * FROM {self.table_name} WHERE key LIKE ?"
        cursor = self.db_manager.execute(query, (f"{prefix}%",))
        
        return [self._row_to_entity(dict(row)) for row in cursor.fetchall()]
        
    def get_settings_as_dict(self, prefix: Optional[str] = None) -> Dict[str, Any]:
        """
        Get settings as a dictionary of key-value pairs.
        
        Args:
            prefix: Optional key prefix to filter by
            
        Returns:
            Dictionary of settings
        """
        if prefix:
            settings = self.get_settings_by_prefix(prefix)
        else:
            settings = self.find_all()
            
        return {setting.key: setting.value for setting in settings}
        
    def bulk_set_values(self, settings_dict: Dict[str, Any]) -> int:
        """
        Set multiple settings at once.
        
        Args:
            settings_dict: Dictionary of key-value pairs
            
        Returns:
            Number of settings set
        """
        count = 0
        
        for key, value in settings_dict.items():
            self.set_value(key, value)
            count += 1
            
        return count

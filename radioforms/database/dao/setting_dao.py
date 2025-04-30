#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setting Data Access Object (DAO) for database operations related to application settings.
"""

from typing import Any, Dict, List, Optional, Union
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
        
    def find_by_key(self, key: str, as_dict: bool = False) -> Optional[Union[Setting, Dict[str, Any]]]:
        """
        Find a setting by its key.
        
        Args:
            key: The setting key
            as_dict: When True, return a dictionary instead of an entity object
            
        Returns:
            The setting as either entity object or dictionary, or None if not found
            
        Examples:
            >>> setting = setting_dao.find_by_key("app.theme")
            >>> setting_dict = setting_dao.find_by_key("app.theme", as_dict=True)
        """
        query = f"SELECT * FROM {self.table_name} WHERE key = ?"
        cursor = self.db_manager.execute(query, (key,))
        row = cursor.fetchone()
        
        if row:
            row_dict = dict(row)
            return row_dict if as_dict else self._row_to_entity(row_dict)
        return None
        
    def find_value(self, key: str, default: Any = None) -> Any:
        """
        Find a setting value by its key, with an optional default.
        
        Args:
            key: The setting key
            default: Default value to return if the setting is not found
            
        Returns:
            The setting value if found, default otherwise
            
        Examples:
            >>> theme = setting_dao.find_value("app.theme", "light")
            >>> max_items = setting_dao.find_value("app.max_items", 10)
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
            
        Examples:
            >>> setting = setting_dao.set_value("app.theme", "dark")
            >>> setting = setting_dao.set_value("app.max_items", 20)
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
            
        Examples:
            >>> deleted = setting_dao.delete_by_key("app.temp_setting")
            >>> if deleted:
            >>>     print("Setting was successfully deleted")
        """
        query = f"DELETE FROM {self.table_name} WHERE key = ?"
        cursor = self.db_manager.execute(query, (key,))
        self.db_manager.commit()
        
        # Invalidate cache manually since we're bypassing BaseDAO's delete method
        self._invalidate_cache()
        
        return cursor.rowcount > 0
        
    def find_by_prefix(self, prefix: str, as_dict: bool = False) -> Union[List[Setting], List[Dict[str, Any]]]:
        """
        Find all settings with keys that start with a specific prefix.
        
        Args:
            prefix: The key prefix to match
            as_dict: When True, return dictionaries instead of entity objects
            
        Returns:
            List of matching settings as either entity objects or dictionaries
            
        Examples:
            >>> ui_settings = setting_dao.find_by_prefix("ui.")
            >>> network_settings = setting_dao.find_by_prefix("network.", as_dict=True)
        """
        query = f"SELECT * FROM {self.table_name} WHERE key LIKE ?"
        cursor = self.db_manager.execute(query, (f"{prefix}%",))
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
        
    def find_as_dict(self, prefix: Optional[str] = None) -> Dict[str, Any]:
        """
        Find settings as a dictionary of key-value pairs.
        
        Args:
            prefix: Optional key prefix to filter by
            
        Returns:
            Dictionary of settings with keys mapped to their values
            
        Examples:
            >>> all_settings = setting_dao.find_as_dict()
            >>> ui_settings = setting_dao.find_as_dict("ui.")
        """
        if prefix:
            settings = self.find_by_prefix(prefix)
        else:
            settings = self.find_all()
            
        return {setting.key: setting.value for setting in settings}
        
    def set_values_bulk(self, settings_dict: Dict[str, Any]) -> int:
        """
        Set multiple settings at once.
        
        Args:
            settings_dict: Dictionary of key-value pairs
            
        Returns:
            Number of settings set
            
        Examples:
            >>> ui_settings = {
            >>>     "ui.theme": "dark",
            >>>     "ui.font_size": 14,
            >>>     "ui.show_toolbar": True
            >>> }
            >>> count = setting_dao.set_values_bulk(ui_settings)
            >>> print(f"Set {count} settings")
        """
        count = 0
        
        with self.db_manager.transaction():
            for key, value in settings_dict.items():
                self.set_value(key, value)
                count += 1
            
        return count

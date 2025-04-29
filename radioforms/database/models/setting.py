#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setting entity model representing an application setting in the system.
"""

from typing import Optional, Dict, Any, Union
from datetime import datetime
import json

from radioforms.database.models.base_model import TimestampedModel


class Setting(TimestampedModel):
    """
    Setting entity model representing an application setting.
    
    Stores key-value pairs for application settings with
    timestamp tracking.
    """
    
    def __init__(self, id: Optional[int] = None, 
                key: str = "",
                value: Union[str, int, float, bool, Dict, None] = None,
                created_at: Optional[datetime] = None,
                updated_at: Optional[datetime] = None):
        """
        Initialize a Setting entity.
        
        Args:
            id: Setting ID
            key: Setting key (name)
            value: Setting value (can be any JSON-serializable type)
            created_at: Timestamp when the setting was created
            updated_at: Timestamp when the setting was last updated
        """
        super().__init__(id, created_at, updated_at)
        self.key = key
        
        # Store value as JSON string if it's a complex type
        if isinstance(value, (dict, list)):
            self._value = json.dumps(value)
        else:
            self._value = value
            
    @property
    def value(self) -> Any:
        """
        Get the setting value, automatically deserializing JSON if needed.
        
        Returns:
            The setting value
        """
        if self._value is None:
            return None
            
        # If the value is a string that looks like JSON, try to deserialize it
        if isinstance(self._value, str):
            if self._value.strip().startswith(("{", "[")):
                try:
                    return json.loads(self._value)
                except json.JSONDecodeError:
                    return self._value
            
            # Try to convert numeric strings to appropriate types
            try:
                # If it's an integer
                if self._value.isdigit() or (self._value.startswith('-') and self._value[1:].isdigit()):
                    return int(self._value)
                # If it's a float
                elif '.' in self._value:
                    return float(self._value)
            except (ValueError, TypeError):
                pass
                
        return self._value
        
    @value.setter
    def value(self, value: Any):
        """
        Set the setting value, automatically serializing to JSON if needed.
        
        Args:
            value: The new setting value
        """
        if isinstance(value, (dict, list)):
            self._value = json.dumps(value)
        else:
            self._value = value
            
        # Update the "updated_at" timestamp
        self.touch()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the setting to a dictionary.
        
        Returns:
            Dictionary representation
        """
        data = super().to_dict()
        
        # Rename _value to value in the output
        if '_value' in data:
            data['value'] = self.value
            del data['_value']
            
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Setting':
        """
        Create a Setting instance from a dictionary.
        
        Args:
            data: Dictionary containing setting data
            
        Returns:
            A new Setting instance
        """
        # Convert string dates to datetime objects if needed
        for date_field in ['created_at', 'updated_at']:
            if isinstance(data.get(date_field), str):
                data[date_field] = datetime.fromisoformat(data[date_field])
                
        # Clone the dictionary to avoid modifying the original
        setting_data = data.copy()
        
        # Handle the value field specially
        if 'value' in setting_data:
            value = setting_data.pop('value')
            
            # Create the setting with the extracted value
            setting = cls(
                id=setting_data.get('id'),
                key=setting_data.get('key', ''),
                value=value,
                created_at=setting_data.get('created_at'),
                updated_at=setting_data.get('updated_at')
            )
            return setting
            
        # If no value field, use default constructor
        return super(Setting, cls).from_dict(data)
        
    def __str__(self) -> str:
        """
        Return a string representation of the Setting.
        
        Returns:
            String representation
        """
        return f"{self.key} = {self.value}"

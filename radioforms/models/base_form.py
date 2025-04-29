#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base form model that defines common functionality for all form types.
"""

import json
import uuid
import datetime
from typing import Dict, Any, List, Optional, Set, Callable


class Observable:
    """
    Mixin class that implements the observer pattern for change tracking.
    """
    
    def __init__(self):
        """Initialize the Observable mixin."""
        self._observers = set()
        self._changed = False
        
    def add_observer(self, observer):
        """
        Add an observer to receive change notifications.
        
        Args:
            observer: A callable that accepts (observable, property_name, old_value, new_value)
        """
        self._observers.add(observer)
        
    def remove_observer(self, observer):
        """
        Remove an observer.
        
        Args:
            observer: The observer to remove
        """
        self._observers.discard(observer)
        
    def notify_observers(self, property_name, old_value, new_value):
        """
        Notify all observers of a change.
        
        Args:
            property_name: Name of the property that changed
            old_value: Previous value
            new_value: New value
        """
        self._changed = True
        for observer in self._observers:
            observer(self, property_name, old_value, new_value)


class ValidationResult:
    """
    Represents the result of a validation operation.
    """
    
    def __init__(self, is_valid: bool = True, errors: Dict[str, List[str]] = None):
        """
        Initialize a validation result.
        
        Args:
            is_valid: Whether the validation passed
            errors: Dictionary of field names to list of error messages
        """
        self.is_valid = is_valid
        self.errors = errors or {}
        
    def add_error(self, field_name: str, message: str):
        """
        Add a validation error.
        
        Args:
            field_name: Name of the field with the error
            message: Error message
        """
        if field_name not in self.errors:
            self.errors[field_name] = []
            
        self.errors[field_name].append(message)
        self.is_valid = False
        
    def merge(self, other: 'ValidationResult'):
        """
        Merge another validation result into this one.
        
        Args:
            other: Another ValidationResult to merge
        """
        if not other.is_valid:
            self.is_valid = False
            
        for field_name, messages in other.errors.items():
            for message in messages:
                self.add_error(field_name, message)


class BaseFormModel(Observable):
    """
    Base class for all form models with common functionality.
    """
    
    def __init__(self, form_id: Optional[str] = None):
        """
        Initialize the base form model.
        
        Args:
            form_id: Unique identifier for the form (generated if not provided)
        """
        super().__init__()
        self.form_id = form_id or str(uuid.uuid4())
        self.version = 1
        self.creation_date = datetime.datetime.now()
        self.last_modified = self.creation_date
        self._property_setters = {}
        
    def register_property(self, property_name: str, setter: Callable):
        """
        Register a property setter for change tracking.
        
        Args:
            property_name: Name of the property
            setter: Setter function that accepts the new value
        """
        self._property_setters[property_name] = setter
        
    def set_property(self, property_name: str, value: Any):
        """
        Set a property value with change tracking.
        
        Args:
            property_name: Name of the property
            value: New value
        
        Raises:
            AttributeError: If the property doesn't exist
        """
        if property_name not in self._property_setters:
            raise AttributeError(f"Property {property_name} not found or not registered")
            
        setter = self._property_setters[property_name]
        setter(value)
        
    def to_json(self) -> str:
        """
        Serialize the form to JSON.
        
        Returns:
            JSON representation of the form
        """
        return json.dumps(self.to_dict(), indent=2)
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the form to a dictionary.
        
        Returns:
            Dictionary representation of the form
        
        Notes:
            Subclasses should override this method to include their specific properties.
        """
        return {
            "form_id": self.form_id,
            "version": self.version,
            "creation_date": self.creation_date.isoformat(),
            "last_modified": self.last_modified.isoformat(),
            "form_type": self.get_form_type()
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseFormModel':
        """
        Create a form instance from a dictionary.
        
        Args:
            data: Dictionary representation of the form
            
        Returns:
            A new form instance
            
        Notes:
            Subclasses should override this method to handle their specific properties.
        """
        form = cls(form_id=data.get("form_id"))
        form.version = data.get("version", 1)
        
        # Parse dates if they exist
        if "creation_date" in data:
            form.creation_date = datetime.datetime.fromisoformat(data["creation_date"])
            
        if "last_modified" in data:
            form.last_modified = datetime.datetime.fromisoformat(data["last_modified"])
            
        return form
        
    @classmethod
    def from_json(cls, json_str: str) -> 'BaseFormModel':
        """
        Create a form instance from a JSON string.
        
        Args:
            json_str: JSON representation of the form
            
        Returns:
            A new form instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
        
    def validate(self) -> ValidationResult:
        """
        Validate the form data.
        
        Returns:
            ValidationResult with validation status and any errors
            
        Notes:
            Subclasses should override this method to validate their specific fields.
        """
        result = ValidationResult()
        
        # Basic validation for common fields
        if not self.form_id:
            result.add_error("form_id", "Form ID is required")
            
        return result
        
    def create_new_version(self):
        """
        Create a new version of the form.
        
        Notes:
            This updates the version number and last_modified timestamp.
        """
        self.version += 1
        self.last_modified = datetime.datetime.now()
        
    def get_form_type(self) -> str:
        """
        Get the form type identifier.
        
        Returns:
            String identifier for the form type
            
        Notes:
            Subclasses must override this method to return their specific form type.
        """
        return "base"  # Subclasses should override this

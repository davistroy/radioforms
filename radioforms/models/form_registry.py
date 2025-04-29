#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Form registry and factory for managing form types.

This module provides classes for registering form model classes and
creating instances of different form types.
"""

from typing import Dict, Any, Type, List, Optional, Callable, Tuple, Union
import importlib
import inspect
import os
import json
import datetime

from radioforms.models.base_form import BaseFormModel


class FormMetadata:
    """
    Metadata for a registered form type.
    """
    
    def __init__(self, form_type: str, display_name: str, 
                description: str, version: str):
        """
        Initialize form metadata.
        
        Args:
            form_type: Identifier for the form type (e.g., 'ICS-213')
            display_name: Human-readable name for display
            description: Description of the form purpose
            version: Version identifier for this form type
        """
        self.form_type = form_type
        self.display_name = display_name
        self.description = description
        self.version = version
        self.last_updated = datetime.datetime.now().isoformat()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert metadata to a dictionary.
        
        Returns:
            Dictionary representation of the metadata
        """
        return {
            "form_type": self.form_type,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "last_updated": self.last_updated
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FormMetadata':
        """
        Create form metadata from a dictionary.
        
        Args:
            data: Dictionary containing metadata
            
        Returns:
            A new FormMetadata instance
        """
        metadata = cls(
            data.get("form_type", ""),
            data.get("display_name", ""),
            data.get("description", ""),
            data.get("version", "")
        )
        metadata.last_updated = data.get("last_updated", metadata.last_updated)
        return metadata


class FormRegistry:
    """
    Registry for form model classes.
    
    This class maintains a registry of form model classes and their metadata,
    allowing for discovery and instantiation of different form types.
    """
    
    _instance = None
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(FormRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        """Initialize the form registry."""
        if self._initialized:
            return
            
        self._form_classes: Dict[str, Type[BaseFormModel]] = {}
        self._form_metadata: Dict[str, FormMetadata] = {}
        self._form_creators: Dict[str, Callable[[], BaseFormModel]] = {}
        self._initialized = True
        
    def register_form_class(self, form_class: Type[BaseFormModel], 
                          metadata: FormMetadata,
                          creator_func: Optional[Callable[[], BaseFormModel]] = None) -> None:
        """
        Register a form class with metadata.
        
        Args:
            form_class: Form model class (must inherit from BaseFormModel)
            metadata: Metadata for the form type
            creator_func: Optional factory function for creating new instances
        """
        # Verify the class inherits from BaseFormModel
        if not issubclass(form_class, BaseFormModel):
            raise TypeError(f"Form class {form_class.__name__} must inherit from BaseFormModel")
            
        # Register the class and metadata
        form_type = metadata.form_type
        self._form_classes[form_type] = form_class
        self._form_metadata[form_type] = metadata
        
        # Register the creator function or use create_new classmethod if available
        if creator_func:
            self._form_creators[form_type] = creator_func
        elif hasattr(form_class, 'create_new') and callable(getattr(form_class, 'create_new')):
            self._form_creators[form_type] = getattr(form_class, 'create_new')
        else:
            # Default creator function
            self._form_creators[form_type] = lambda: form_class()
            
    def unregister_form_class(self, form_type: str) -> bool:
        """
        Unregister a form class.
        
        Args:
            form_type: Identifier for the form type to unregister
            
        Returns:
            True if the form type was unregistered, False if not found
        """
        if form_type in self._form_classes:
            del self._form_classes[form_type]
            del self._form_metadata[form_type]
            if form_type in self._form_creators:
                del self._form_creators[form_type]
            return True
        return False
        
    def get_form_class(self, form_type: str) -> Optional[Type[BaseFormModel]]:
        """
        Get a form class by type.
        
        Args:
            form_type: Identifier for the form type
            
        Returns:
            The form class if found, None otherwise
        """
        return self._form_classes.get(form_type)
        
    def get_form_metadata(self, form_type: str) -> Optional[FormMetadata]:
        """
        Get metadata for a form type.
        
        Args:
            form_type: Identifier for the form type
            
        Returns:
            FormMetadata if found, None otherwise
        """
        return self._form_metadata.get(form_type)
        
    def get_all_form_types(self) -> List[str]:
        """
        Get a list of all registered form types.
        
        Returns:
            List of form type identifiers
        """
        return list(self._form_classes.keys())
        
    def get_all_metadata(self) -> Dict[str, FormMetadata]:
        """
        Get all registered form metadata.
        
        Returns:
            Dictionary mapping form types to metadata
        """
        return self._form_metadata.copy()
        
    def create_form(self, form_type: str) -> Optional[BaseFormModel]:
        """
        Create a new instance of a form type.
        
        Args:
            form_type: Identifier for the form type
            
        Returns:
            A new form instance if the type is registered, None otherwise
        """
        if form_type in self._form_creators:
            return self._form_creators[form_type]()
        return None
        
    def load_form_from_dict(self, data: Dict[str, Any]) -> Optional[BaseFormModel]:
        """
        Load a form from a dictionary.
        
        Args:
            data: Dictionary representation of a form
            
        Returns:
            A form instance if the type is registered, None otherwise
        """
        form_type = data.get("form_type")
        if not form_type or form_type not in self._form_classes:
            return None
            
        form_class = self._form_classes[form_type]
        return form_class.from_dict(data)
        
    def load_form_from_json(self, json_str: str) -> Optional[BaseFormModel]:
        """
        Load a form from a JSON string.
        
        Args:
            json_str: JSON representation of a form
            
        Returns:
            A form instance if the type is registered, None otherwise
        """
        try:
            data = json.loads(json_str)
            return self.load_form_from_dict(data)
        except json.JSONDecodeError:
            return None
            
    def discover_form_classes(self, package_name: str = 'radioforms.models') -> List[str]:
        """
        Discover and register form classes from a package.
        
        Args:
            package_name: Name of the package to search for form classes
            
        Returns:
            List of form types that were registered
        """
        registered_types = []
        
        try:
            package = importlib.import_module(package_name)
            package_path = os.path.dirname(package.__file__)
            
            # Find all Python files in the package
            for filename in os.listdir(package_path):
                if not filename.endswith('.py') or filename == '__init__.py':
                    continue
                    
                module_name = f"{package_name}.{filename[:-3]}"
                
                try:
                    module = importlib.import_module(module_name)
                    
                    # Look for classes that inherit from BaseFormModel
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (issubclass(obj, BaseFormModel) and 
                            obj is not BaseFormModel and
                            hasattr(obj, 'get_form_type')):
                            
                            # Try to instantiate to get the form type
                            try:
                                form_instance = obj()
                                form_type = form_instance.get_form_type()
                                
                                # Create default metadata (can be enhanced)
                                metadata = FormMetadata(
                                    form_type=form_type,
                                    display_name=name,
                                    description=obj.__doc__ or f"{form_type} Form",
                                    version="1.0"
                                )
                                
                                # Register the form class
                                self.register_form_class(obj, metadata)
                                registered_types.append(form_type)
                                
                            except Exception:
                                # Skip if instantiation fails
                                continue
                                
                except ImportError:
                    # Skip if module import fails
                    continue
                    
        except (ImportError, OSError):
            # Return empty list if package not found or other error
            pass
            
        return registered_types


class FormFactory:
    """
    Factory for creating and managing form instances.
    
    This class provides methods for creating, loading, and saving forms,
    using the FormRegistry to access registered form types.
    """
    
    def __init__(self, registry: Optional[FormRegistry] = None):
        """
        Initialize the form factory.
        
        Args:
            registry: FormRegistry instance (creates new one if not provided)
        """
        self.registry = registry or FormRegistry()
        
    def create_form(self, form_type: str) -> Optional[BaseFormModel]:
        """
        Create a new form instance.
        
        Args:
            form_type: Identifier for the form type
            
        Returns:
            A new form instance if the type is registered, None otherwise
        """
        return self.registry.create_form(form_type)
        
    def load_form(self, form_data: Union[str, Dict[str, Any]]) -> Optional[BaseFormModel]:
        """
        Load a form from JSON string or dictionary.
        
        Args:
            form_data: Form data as JSON string or dictionary
            
        Returns:
            A form instance if valid and type is registered, None otherwise
        """
        if isinstance(form_data, str):
            return self.registry.load_form_from_json(form_data)
        else:
            return self.registry.load_form_from_dict(form_data)
            
    def save_form_to_json(self, form: BaseFormModel) -> str:
        """
        Save a form to a JSON string.
        
        Args:
            form: Form instance to save
            
        Returns:
            JSON representation of the form
        """
        return form.to_json()
        
    def get_available_form_types(self) -> List[Tuple[str, str]]:
        """
        Get a list of available form types with display names.
        
        Returns:
            List of tuples containing (form_type, display_name)
        """
        result = []
        
        for form_type, metadata in self.registry.get_all_metadata().items():
            result.append((form_type, metadata.display_name))
            
        return sorted(result, key=lambda x: x[0])
        
    def get_form_metadata(self, form_type: str) -> Optional[FormMetadata]:
        """
        Get metadata for a form type.
        
        Args:
            form_type: Identifier for the form type
            
        Returns:
            FormMetadata if found, None otherwise
        """
        return self.registry.get_form_metadata(form_type)
        
    def discover_forms(self, package_name: str = 'radioforms.models') -> List[str]:
        """
        Discover and register form classes from a package.
        
        Args:
            package_name: Name of the package to search for form classes
            
        Returns:
            List of form types that were registered
        """
        return self.registry.discover_form_classes(package_name)

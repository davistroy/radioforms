#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Form Model Registry for RadioForms.

This module provides a registry system for form models to enable
easy creation, access, and management of different form types.
"""

from typing import Dict, Type, Optional, List, Any, Union, Callable, TypeVar

from radioforms.models.base_form import BaseFormModel
from radioforms.models.enhanced_ics213_form import EnhancedICS213Form
from radioforms.models.enhanced_ics214_form import EnhancedICS214Form
from radioforms.database.dao.form_dao_refactored import FormDAO

# Type variable for form classes
T = TypeVar('T', bound=BaseFormModel)


class FormModelRegistry:
    """
    Registry for form model classes and factory methods.
    
    This class maintains a registry of form model types and provides
    factory methods for creating form instances. It integrates with
    the DAO layer for persistence operations.
    """
    
    # Singleton instance
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'FormModelRegistry':
        """
        Get the singleton instance of the registry.
        
        Returns:
            The singleton FormModelRegistry instance
        """
        if cls._instance is None:
            cls._instance = FormModelRegistry()
        return cls._instance
    
    def __init__(self):
        """Initialize the form model registry."""
        if FormModelRegistry._instance is not None:
            raise RuntimeError("FormModelRegistry is a singleton. Use get_instance() instead.")
            
        # Initialize registry
        self._registry: Dict[str, Type[BaseFormModel]] = {}
        self._form_dao: Optional[FormDAO] = None
        
        # Register standard form types
        self.register_model("ICS-213", EnhancedICS213Form)
        self.register_model("ICS-214", EnhancedICS214Form)
        
    def register_model(self, form_type: str, form_class: Type[BaseFormModel]) -> None:
        """
        Register a form model class for a specific form type.
        
        Args:
            form_type: The form type identifier (e.g., "ICS-213")
            form_class: The form model class to register
        """
        self._registry[form_type] = form_class
        
    def unregister_model(self, form_type: str) -> None:
        """
        Unregister a form model class.
        
        Args:
            form_type: The form type identifier to unregister
        """
        if form_type in self._registry:
            del self._registry[form_type]
            
    def set_form_dao(self, form_dao: FormDAO) -> None:
        """
        Set the FormDAO instance for persistence operations.
        
        Args:
            form_dao: The FormDAO instance to use
        """
        self._form_dao = form_dao
        
    def get_form_dao(self) -> Optional[FormDAO]:
        """
        Get the current FormDAO instance.
        
        Returns:
            The current FormDAO instance, or None if not set
        """
        return self._form_dao
        
    def get_registered_types(self) -> List[str]:
        """
        Get a list of all registered form types.
        
        Returns:
            List of registered form type identifiers
        """
        return list(self._registry.keys())
        
    def get_model_class(self, form_type: str) -> Optional[Type[BaseFormModel]]:
        """
        Get the form model class for a specific form type.
        
        Args:
            form_type: The form type identifier
            
        Returns:
            The form model class, or None if not registered
        """
        return self._registry.get(form_type)
        
    def create_form(self, form_type: str, **kwargs) -> Optional[BaseFormModel]:
        """
        Create a new form instance of the specified type.
        
        Args:
            form_type: The form type identifier
            **kwargs: Additional arguments to pass to the form constructor
            
        Returns:
            A new form instance, or None if the form type is not registered
        """
        form_class = self.get_model_class(form_type)
        if not form_class:
            return None
            
        return form_class(**kwargs)
        
    def create_form_with_dao(self, form_type: str) -> Optional[BaseFormModel]:
        """
        Create a new form instance with DAO integration.
        
        Args:
            form_type: The form type identifier
            
        Returns:
            A new form instance with DAO integration, or None if the type is not registered
            or the DAO is not set
        """
        if not self._form_dao:
            raise RuntimeError("FormDAO not set. Call set_form_dao() before using this method.")
            
        form_class = self.get_model_class(form_type)
        if not form_class:
            return None
            
        return form_class.create_with_dao(self._form_dao)
        
    def load_form(self, form_id: str, version_id: Optional[str] = None) -> Optional[BaseFormModel]:
        """
        Load a form from the database.
        
        Args:
            form_id: The ID of the form to load
            version_id: Optional version ID to load
            
        Returns:
            The loaded form instance, or None if not found
            
        Raises:
            RuntimeError: If FormDAO is not set
        """
        if not self._form_dao:
            raise RuntimeError("FormDAO not set. Call set_form_dao() before using this method.")
            
        # Load form data from DAO
        if version_id and hasattr(self._form_dao, 'find_version_by_id'):
            try:
                form_dict = self._form_dao.find_version_by_id(version_id)
            except (AttributeError, TypeError):
                form_dict = None
        else:
            form_dict = self._form_dao.find_by_id(form_id)
            
        # Return None if form not found
        if not form_dict:
            return None
            
        # Determine form type
        form_type = form_dict.get("form_type")
        form_class = self.get_model_class(form_type)
        
        if not form_class:
            # Try to guess form type from structure
            for type_name, cls in self._registry.items():
                # Create an instance and see if it can be loaded
                try:
                    form = cls.from_dict(form_dict)
                    return form
                except (KeyError, ValueError, TypeError):
                    continue
                    
            # No suitable class found
            return None
            
        # Create form instance from dictionary
        return form_class.from_dict(form_dict)
        
    def save_form(self, form: BaseFormModel, create_version: bool = True) -> str:
        """
        Save a form to the database.
        
        Args:
            form: The form to save
            create_version: Whether to create a new version
            
        Returns:
            The saved form ID
            
        Raises:
            RuntimeError: If FormDAO is not set
        """
        if not self._form_dao:
            raise RuntimeError("FormDAO not set. Call set_form_dao() before using this method.")
            
        return form.save_to_dao(self._form_dao, create_version)
        
    def find_forms(self, criteria: Dict[str, Any] = None, as_dict: bool = False) -> List[Union[BaseFormModel, Dict[str, Any]]]:
        """
        Find forms matching the specified criteria.
        
        Args:
            criteria: Dictionary of search criteria
            as_dict: Whether to return dictionaries (True) or form instances (False)
            
        Returns:
            List of forms or form dictionaries
            
        Raises:
            RuntimeError: If FormDAO is not set
        """
        if not self._form_dao:
            raise RuntimeError("FormDAO not set. Call set_form_dao() before using this method.")
            
        criteria = criteria or {}
        
        # Use find_by method if available
        if hasattr(self._form_dao, 'find_by'):
            try:
                results = self._form_dao.find_by(criteria, as_dict=True)
            except (AttributeError, TypeError):
                # Fall back to find_all
                results = self._form_dao.find_all(as_dict=True)
                
                # Filter results manually if find_by not available
                if criteria:
                    filtered_results = []
                    for form_dict in results:
                        match = True
                        for key, value in criteria.items():
                            if key not in form_dict or form_dict[key] != value:
                                match = False
                                break
                        if match:
                            filtered_results.append(form_dict)
                    results = filtered_results
        else:
            # Fall back to find_all
            results = self._form_dao.find_all(as_dict=True)
            
            # Filter results manually if find_by not available
            if criteria:
                filtered_results = []
                for form_dict in results:
                    match = True
                    for key, value in criteria.items():
                        if key not in form_dict or form_dict[key] != value:
                            match = False
                            break
                    if match:
                        filtered_results.append(form_dict)
                results = filtered_results
                
        # Return dictionaries if requested
        if as_dict:
            return results
            
        # Convert dictionaries to form instances
        forms = []
        for form_dict in results:
            form_type = form_dict.get("form_type")
            form_class = self.get_model_class(form_type)
            
            if not form_class:
                # Skip if we can't determine form type
                continue
                
            form = form_class.from_dict(form_dict)
            forms.append(form)
            
        return forms
        
    def find_forms_by_type(self, form_type: str, as_dict: bool = False) -> List[Union[BaseFormModel, Dict[str, Any]]]:
        """
        Find all forms of a specific type.
        
        Args:
            form_type: The form type to find
            as_dict: Whether to return dictionaries (True) or form instances (False)
            
        Returns:
            List of forms or form dictionaries
            
        Raises:
            RuntimeError: If FormDAO is not set
        """
        return self.find_forms({"form_type": form_type}, as_dict)
        
    def get_form_template(self, form_type: str) -> Optional[BaseFormModel]:
        """
        Get a template form instance for the specified type.
        
        This creates a new form instance with default values but does not persist it.
        
        Args:
            form_type: The form type identifier
            
        Returns:
            A new form instance, or None if the form type is not registered
        """
        form_class = self.get_model_class(form_type)
        if not form_class:
            return None
            
        return form_class.create_new()
        
    def register_form_types_from_factory(self, factory_func: Callable[[], Dict[str, Type[BaseFormModel]]]) -> None:
        """
        Register form types from a factory function.
        
        This is useful for plugins that want to register custom form types.
        
        Args:
            factory_func: A function that returns a dictionary mapping form type identifiers to form classes
        """
        form_types = factory_func()
        for form_type, form_class in form_types.items():
            self.register_model(form_type, form_class)

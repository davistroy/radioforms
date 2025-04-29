#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Forms controller module.

This module provides the controller for managing forms in the application,
including their creation, loading, saving, and presentation in the UI.
"""

from typing import Dict, Any, List, Optional, Type

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject, Signal, Slot, QDateTime

from radioforms.models.base_form import BaseFormModel
from radioforms.models.ics213_form import ICS213Form
from radioforms.models.ics214_form import ICS214Form
from radioforms.models.form_registry import FormFactory
from radioforms.models.form_persistence import FormManager, FormState
from radioforms.views.form_view_base import FormViewBase
from radioforms.views.ics213_form_view import ICS213FormView
from radioforms.views.ics214_form_view import ICS214FormView


class FormViewController:
    """
    Controller for managing the views associated with forms.
    
    This controller maps form types to their corresponding views and
    creates the appropriate view for a given form model.
    """
    
    # Map of form types to view classes
    _form_view_classes: Dict[str, Type[FormViewBase]] = {
        "ICS-213": ICS213FormView,
        "ICS-214": ICS214FormView,
    }
    
    @classmethod
    def create_view_for_form(cls, form_model: BaseFormModel, parent=None) -> Optional[FormViewBase]:
        """
        Create a view for the specified form model.
        
        Args:
            form_model: Form model to create a view for
            parent: Parent widget for the view
            
        Returns:
            A form view instance, or None if no view is available for the form type
        """
        if not form_model:
            return None
            
        form_type = form_model.get_form_type()
        
        # Get the view class for this form type
        view_class = cls._form_view_classes.get(form_type)
        
        # If no view class is found, return None
        if not view_class:
            return None
            
        # Create and return a view instance
        return view_class(form_model, parent)
    
    @classmethod
    def register_form_view(cls, form_type: str, view_class: Type[FormViewBase]):
        """
        Register a form view class for a form type.
        
        Args:
            form_type: Form type identifier
            view_class: Form view class
        """
        cls._form_view_classes[form_type] = view_class
    
    @classmethod
    def get_available_form_types(cls) -> List[str]:
        """
        Get a list of form types with available views.
        
        Returns:
            List of form type identifiers
        """
        return list(cls._form_view_classes.keys())


class FormsController(QObject):
    """
    Controller for managing forms in the application.
    
    This controller handles the creation, loading, saving, and business logic
    for forms, coordinating between models, views, and data storage.
    """
    
    # Signals
    form_created = Signal(BaseFormModel)
    form_loaded = Signal(BaseFormModel)
    form_saved = Signal(BaseFormModel, str)  # form, path
    form_closed = Signal(str)  # form_id
    
    def __init__(self, parent=None):
        """
        Initialize the forms controller.
        
        Args:
            parent: Parent QObject
        """
        super().__init__(parent)
        
        # Initialize form registry and manager
        self.form_factory = FormFactory()
        self.form_manager = FormManager()
        
        # Discover available form types
        self.form_factory.discover_forms()
        
        # Currently open forms - dict of form_id to form_model
        self.open_forms: Dict[str, BaseFormModel] = {}
    
    def create_form(self, form_type: str) -> Optional[BaseFormModel]:
        """
        Create a new form of the specified type.
        
        Args:
            form_type: Type of form to create
            
        Returns:
            New form model instance, or None if the type is not supported
        """
        # Create form using the manager (which will create a tracker)
        form = self.form_manager.create_form(form_type)
        
        if form:
            # Add to open forms
            self.open_forms[form.form_id] = form
            
            # Emit signal
            self.form_created.emit(form)
            
        return form
    
    def load_form(self, path: str) -> Optional[BaseFormModel]:
        """
        Load a form from disk.
        
        Args:
            path: Path to the form file
            
        Returns:
            Loaded form model, or None if loading failed
        """
        # Load the form
        form = self.form_manager.load_form(path)
        
        if form:
            # Add to open forms
            self.open_forms[form.form_id] = form
            
            # Emit signal
            self.form_loaded.emit(form)
            
        return form
    
    def save_form(self, form_id: str, path: Optional[str] = None) -> Optional[str]:
        """
        Save a form to disk.
        
        Args:
            form_id: ID of the form to save
            path: Path to save to, or None to use default
            
        Returns:
            Path where the form was saved, or None if saving failed
        """
        # Get the form
        form = self.open_forms.get(form_id)
        if not form:
            return None
            
        # Save the form
        save_path = self.form_manager.save_form(form, path)
        
        if save_path:
            # Emit signal
            self.form_saved.emit(form, save_path)
            
        return save_path
    
    def close_form(self, form_id: str) -> bool:
        """
        Close a form.
        
        Args:
            form_id: ID of the form to close
            
        Returns:
            True if the form was closed, False if not found
        """
        # Check if the form is open
        if form_id not in self.open_forms:
            return False
            
        # Remove from open forms
        del self.open_forms[form_id]
        
        # Emit signal
        self.form_closed.emit(form_id)
        
        return True
    
    def create_view_for_form(self, form_id: str, parent=None) -> Optional[FormViewBase]:
        """
        Create a view for a form.
        
        Args:
            form_id: ID of the form to create a view for
            parent: Parent widget
            
        Returns:
            Form view instance, or None if the form is not found or no view is available
        """
        # Get the form
        form = self.open_forms.get(form_id)
        if not form:
            return None
            
        # Create view
        return FormViewController.create_view_for_form(form, parent)
    
    def get_available_form_types(self) -> List[str]:
        """
        Get a list of available form types.
        
        Returns:
            List of form type identifiers
        """
        # Get form types registered in both the form factory and view controller
        factory_types = self.form_factory.get_available_form_types()
        view_types = FormViewController.get_available_form_types()
        
        # Filter to only include types that have both a model and a view
        available_types = []
        for form_type, display_name in factory_types:
            if form_type in view_types:
                available_types.append((form_type, display_name))
                
        return available_types
    
    def is_form_modified(self, form_id: str) -> bool:
        """
        Check if a form has been modified.
        
        Args:
            form_id: ID of the form to check
            
        Returns:
            True if modified, False otherwise
        """
        # Get the form tracker
        tracker = self.form_manager.get_tracker(form_id)
        if not tracker:
            return False
            
        return tracker.is_modified()
    
    def get_form_state(self, form_id: str) -> Optional[FormState]:
        """
        Get the state of a form.
        
        Args:
            form_id: ID of the form to check
            
        Returns:
            Form state, or None if not found
        """
        return self.form_manager.get_form_state(form_id)

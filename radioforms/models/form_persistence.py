#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Form persistence and change tracking.

This module provides functionality for saving and loading forms,
tracking changes for undo/redo support, and managing form state.
"""

import os
import json
import datetime
import shutil
from enum import Enum
from typing import Dict, Any, List, Optional, Union, Tuple, Callable

from radioforms.models.base_form import BaseFormModel
from radioforms.models.form_registry import FormFactory, FormRegistry


class FormState(Enum):
    """Enum representing the state of a form."""
    NEW = "new"
    MODIFIED = "modified"
    SAVED = "saved"
    READONLY = "readonly"


class ChangeRecord:
    """
    Record of a change to a form property.
    """
    
    def __init__(self, property_name: str, old_value: Any, new_value: Any,
                timestamp: Optional[datetime.datetime] = None):
        """
        Initialize a change record.
        
        Args:
            property_name: Name of the property that changed
            old_value: Previous value of the property
            new_value: New value of the property
            timestamp: When the change occurred (defaults to now)
        """
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value
        self.timestamp = timestamp or datetime.datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the change record to a dictionary.
        
        Returns:
            Dictionary representation of the change record
        """
        return {
            "property": self.property_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "timestamp": self.timestamp.isoformat()
        }


class ChangeTracker:
    """
    Tracks changes to a form for undo/redo functionality.
    """
    
    def __init__(self, form: BaseFormModel):
        """
        Initialize a change tracker for a form.
        
        Args:
            form: The form to track changes for
        """
        self.form = form
        self.undo_stack: List[ChangeRecord] = []
        self.redo_stack: List[ChangeRecord] = []
        self.max_history = 100  # Maximum number of changes to track
        
        # Register as an observer on the form
        self.form.add_observer(self._on_form_changed)
        
    def _on_form_changed(self, form: BaseFormModel, property_name: str, 
                       old_value: Any, new_value: Any):
        """
        Handle form change events.
        
        Args:
            form: The form that changed
            property_name: Name of the property that changed
            old_value: Previous value of the property
            new_value: New value of the property
        """
        # Record the change
        change = ChangeRecord(property_name, old_value, new_value)
        self.undo_stack.append(change)
        
        # Clear the redo stack when a new change occurs
        if hasattr(self, 'redo_stack'):  # Ensure attribute exists
            self.redo_stack.clear()
        
        # Limit the size of the undo stack
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
            
    def can_undo(self) -> bool:
        """
        Check if undo is available.
        
        Returns:
            True if undo is available, False otherwise
        """
        return len(self.undo_stack) > 0
        
    def can_redo(self) -> bool:
        """
        Check if redo is available.
        
        Returns:
            True if redo is available, False otherwise
        """
        return len(self.redo_stack) > 0
        
    def undo(self) -> Optional[ChangeRecord]:
        """
        Undo the last change.
        
        Returns:
            The change record that was undone, or None if no changes to undo
        """
        if not self.can_undo():
            return None
            
        # Get the last change
        change = self.undo_stack.pop()
        
        # Add to redo stack
        self.redo_stack.append(change)
        
        # Apply the reverse change to the form
        # We need to bypass the observer mechanism to avoid recursive changes
        property_name = change.property_name
        if hasattr(self.form, f"_set_{property_name}"):
            # Call the internal setter directly
            setter = getattr(self.form, f"_set_{property_name}")
            setter(change.old_value)
        elif hasattr(self.form, f"_{property_name}"):
            # Set the internal field directly
            setattr(self.form, f"_{property_name}", change.old_value)
        
        # Disable observer during this change to avoid recording it
        old_observers = self.form._observers.copy()
        self.form._observers.clear()
        
        # Re-enable observers
        self.form._observers = old_observers
            
        return change
        
    def redo(self) -> Optional[ChangeRecord]:
        """
        Redo the last undone change.
        
        Returns:
            The change record that was redone, or None if no changes to redo
        """
        if not self.can_redo():
            return None
            
        # Get the last undone change
        change = self.redo_stack.pop()
        
        # Add to undo stack
        self.undo_stack.append(change)
        
        # Disable observer during this change to avoid recording it
        old_observers = self.form._observers.copy()
        self.form._observers.clear()
        
        # Apply the change to the form
        # We need to bypass the observer mechanism to avoid recursive changes
        property_name = change.property_name
        if hasattr(self.form, f"_set_{property_name}"):
            # Call the internal setter directly
            setter = getattr(self.form, f"_set_{property_name}")
            setter(change.new_value)
        elif hasattr(self.form, f"_{property_name}"):
            # Set the internal field directly
            setattr(self.form, f"_{property_name}", change.new_value)
            
        # Re-enable observers
        self.form._observers = old_observers
            
        return change
        
    def get_undo_history(self) -> List[ChangeRecord]:
        """
        Get the undo history.
        
        Returns:
            List of change records in the undo stack (most recent last)
        """
        return self.undo_stack.copy()
        
    def get_redo_history(self) -> List[ChangeRecord]:
        """
        Get the redo history.
        
        Returns:
            List of change records in the redo stack (most recent last)
        """
        return self.redo_stack.copy()
        
    def clear_history(self):
        """Clear all undo and redo history."""
        self.undo_stack.clear()
        self.redo_stack.clear()


class FormManager:
    """
    Manages form persistence, state, and change tracking.
    """
    
    def __init__(self, forms_dir: str = "forms", factory: Optional[FormFactory] = None):
        """
        Initialize the form manager.
        
        Args:
            forms_dir: Directory to store form files
            factory: FormFactory instance (creates new one if not provided)
        """
        self.forms_dir = forms_dir
        self.factory = factory or FormFactory()
        self.trackers: Dict[str, ChangeTracker] = {}
        self.form_states: Dict[str, FormState] = {}
        
        # Create forms directory if it doesn't exist
        os.makedirs(forms_dir, exist_ok=True)
        
        # Discover available form types
        self.factory.discover_forms()
        
    def create_form(self, form_type: str) -> Optional[BaseFormModel]:
        """
        Create a new form instance.
        
        Args:
            form_type: Type of form to create
            
        Returns:
            A new form instance if the type is registered, None otherwise
        """
        form = self.factory.create_form(form_type)
        
        if form:
            # Create change tracker
            self.trackers[form.form_id] = ChangeTracker(form)
            self.form_states[form.form_id] = FormState.NEW
            
        return form
        
    def save_form(self, form: BaseFormModel, path: Optional[str] = None) -> str:
        """
        Save a form to disk.
        
        Args:
            form: Form to save
            path: Path to save to (defaults to forms_dir/form_type/form_id.json)
            
        Returns:
            Path where the form was saved
        """
        form_type = form.get_form_type()
        form_id = form.form_id
        
        if path is None:
            # Create directory for this form type if it doesn't exist
            type_dir = os.path.join(self.forms_dir, form_type)
            os.makedirs(type_dir, exist_ok=True)
            
            # Default path is forms_dir/form_type/form_id.json
            path = os.path.join(type_dir, f"{form_id}.json")
            
        # Save the form as JSON
        with open(path, 'w', encoding='utf-8') as f:
            f.write(form.to_json())
            
        # Update the form state
        self.form_states[form_id] = FormState.SAVED
        
        # Clear history after saving
        if form_id in self.trackers:
            self.trackers[form_id].clear_history()
            
        # Update the form version
        form.create_new_version()
        
        return path
        
    def load_form(self, path: str) -> Optional[BaseFormModel]:
        """
        Load a form from disk.
        
        Args:
            path: Path to load from
            
        Returns:
            The loaded form if successful, None otherwise
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                form_json = f.read()
                
            form = self.factory.load_form(form_json)
            
            if form:
                # Create change tracker
                self.trackers[form.form_id] = ChangeTracker(form)
                self.form_states[form.form_id] = FormState.SAVED
                
            return form
            
        except (IOError, json.JSONDecodeError):
            return None
            
    def get_form_state(self, form_id: str) -> FormState:
        """
        Get the state of a form.
        
        Args:
            form_id: ID of the form
            
        Returns:
            State of the form, or FormState.NEW if not tracked
        """
        return self.form_states.get(form_id, FormState.NEW)
        
    def set_form_state(self, form_id: str, state: FormState):
        """
        Set the state of a form.
        
        Args:
            form_id: ID of the form
            state: New state for the form
        """
        self.form_states[form_id] = state
        
    def get_tracker(self, form_id: str) -> Optional[ChangeTracker]:
        """
        Get the change tracker for a form.
        
        Args:
            form_id: ID of the form
            
        Returns:
            ChangeTracker if found, None otherwise
        """
        return self.trackers.get(form_id)
        
    def create_backup(self, form: BaseFormModel) -> str:
        """
        Create a backup of a form.
        
        Args:
            form: Form to back up
            
        Returns:
            Path to the backup file
        """
        form_type = form.get_form_type()
        form_id = form.form_id
        
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(self.forms_dir, "backups", form_type)
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create a timestamped backup filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"{form_id}_{timestamp}.json")
        
        # Save the backup
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(form.to_json())
            
        return backup_path
        
    def list_forms(self, form_type: Optional[str] = None) -> List[str]:
        """
        List available form files.
        
        Args:
            form_type: Optional type to filter by
            
        Returns:
            List of paths to form files
        """
        result = []
        
        if form_type:
            # List forms of a specific type
            type_dir = os.path.join(self.forms_dir, form_type)
            if os.path.isdir(type_dir):
                for filename in os.listdir(type_dir):
                    if filename.endswith('.json'):
                        result.append(os.path.join(type_dir, filename))
        else:
            # List all forms
            for type_name in os.listdir(self.forms_dir):
                type_dir = os.path.join(self.forms_dir, type_name)
                if os.path.isdir(type_dir) and not type_name == "backups":
                    for filename in os.listdir(type_dir):
                        if filename.endswith('.json'):
                            result.append(os.path.join(type_dir, filename))
                            
        return result
        
    def export_form(self, form: BaseFormModel, export_dir: str) -> str:
        """
        Export a form to a different location.
        
        Args:
            form: Form to export
            export_dir: Directory to export to
            
        Returns:
            Path to the exported file
        """
        form_type = form.get_form_type()
        form_id = form.form_id
        
        # Create export directory if it doesn't exist
        os.makedirs(export_dir, exist_ok=True)
        
        # Create export filename
        export_path = os.path.join(export_dir, f"{form_type}_{form_id}.json")
        
        # Save the export
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(form.to_json())
            
        return export_path
        
    def import_form(self, path: str, create_copy: bool = True) -> Optional[BaseFormModel]:
        """
        Import a form from a different location.
        
        Args:
            path: Path to import from
            create_copy: Whether to create a copy with a new form_id
            
        Returns:
            The imported form if successful, None otherwise
        """
        form = self.load_form(path)
        
        if form and create_copy:
            # Create a copy with a new form_id
            form_dict = form.to_dict()
            
            # Remove the form_id to generate a new one
            if "form_id" in form_dict:
                del form_dict["form_id"]
                
            # Create a new form from the dictionary
            form = self.factory.load_form(form_dict)
            
            if form:
                # Create change tracker
                self.trackers[form.form_id] = ChangeTracker(form)
                self.form_states[form.form_id] = FormState.NEW
                
        return form

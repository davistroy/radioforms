#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Form tab widget implementation.

This module provides a specialized tab widget for managing form views.
"""

from PySide6.QtWidgets import (
    QTabWidget, QWidget, QMenu, QMessageBox, QInputDialog,
    QFileDialog, QVBoxLayout
)
from PySide6.QtCore import Qt, Signal, Slot, QObject, QPoint

from radioforms.views.form_view_base import FormViewBase
from radioforms.models.base_form import BaseFormModel


class FormTabWidget(QTabWidget):
    """
    Tab widget for managing form views.
    
    This widget extends QTabWidget to handle form-specific operations
    such as validation, saving, and closing with unsaved changes.
    """
    
    # Signals
    form_closed = Signal(str)  # form_id
    
    def __init__(self, controller, parent=None):
        """
        Initialize the form tab widget.
        
        Args:
            controller: Application controller
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.controller = controller
        
        # Map of tab index to form ID
        self.tab_forms = {}
        
        # Configure tab widget
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Connect signals
        self.tabCloseRequested.connect(self._on_tab_close_requested)
        self.customContextMenuRequested.connect(self._on_context_menu_requested)
    
    def add_form_tab(self, form: BaseFormModel, title: str = None):
        """
        Add a new tab for a form.
        
        Args:
            form: Form model to display
            title: Tab title (uses form type if None)
            
        Returns:
            The index of the new tab, or -1 if the form could not be added
        """
        # Check if form is already open
        form_id = form.form_id
        for index, existing_id in self.tab_forms.items():
            if existing_id == form_id:
                # Form is already open, switch to its tab
                self.setCurrentIndex(index)
                return index
        
        # Create a view for the form
        form_view = self.controller.forms_controller.create_view_for_form(form_id, self)
        
        if not form_view:
            return -1
            
        # Connect form view signals
        self._connect_form_view_signals(form_view)
            
        # Create a container widget for the form
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(form_view)
        
        # Add the tab
        if not title:
            title = f"{form.get_form_type()}"
            
        index = self.addTab(container, title)
        
        # Store the form ID
        self.tab_forms[index] = form_id
        
        # Set the new tab as active
        self.setCurrentIndex(index)
        
        return index
    
    def _connect_form_view_signals(self, form_view: FormViewBase):
        """
        Connect signals from a form view.
        
        Args:
            form_view: Form view to connect
        """
        # Connect form modified signal to update tab label with * indicator
        form_view.form_modified.connect(
            lambda: self._update_tab_modified(form_view.get_form())
        )
        
        # Connect form saved signal to update tab label
        form_view.form_saved.connect(
            lambda: self._update_tab_saved(form_view.get_form())
        )
        
        # Connect validation failed signal if needed later
        form_view.validation_failed.connect(self._on_validation_failed)
    
    def _update_tab_modified(self, form: BaseFormModel):
        """
        Update tab label to indicate modifications.
        
        Args:
            form: Form that was modified
        """
        # Find the tab index for this form
        form_id = form.form_id
        tab_index = -1
        
        for index, existing_id in self.tab_forms.items():
            if existing_id == form_id:
                tab_index = index
                break
                
        if tab_index == -1:
            return
            
        # Update the tab text
        current_text = self.tabText(tab_index)
        if not current_text.endswith('*'):
            self.setTabText(tab_index, f"{current_text}*")
    
    def _update_tab_saved(self, form: BaseFormModel):
        """
        Update tab label after saving.
        
        Args:
            form: Form that was saved
        """
        # Find the tab index for this form
        form_id = form.form_id
        tab_index = -1
        
        for index, existing_id in self.tab_forms.items():
            if existing_id == form_id:
                tab_index = index
                break
                
        if tab_index == -1:
            return
            
        # Update the tab text to remove the * indicator
        current_text = self.tabText(tab_index)
        if current_text.endswith('*'):
            self.setTabText(tab_index, current_text[:-1])
    
    @Slot(int)
    def _on_tab_close_requested(self, index: int):
        """
        Handle a request to close a tab.
        
        Args:
            index: Index of the tab to close
        """
        # Get the form ID for this tab
        form_id = self.tab_forms.get(index)
        if not form_id:
            return
            
        # Check if the form has unsaved changes
        if self.controller.forms_controller.is_form_modified(form_id):
            # Ask the user if they want to save changes
            response = QMessageBox.question(
                self,
                "Save Changes",
                "This form has unsaved changes. Do you want to save before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if response == QMessageBox.Cancel:
                # User cancelled - don't close the tab
                return
                
            if response == QMessageBox.Save:
                # Save the form first
                save_path = self.controller.forms_controller.save_form(form_id)
                if not save_path:
                    # Saving failed - don't close the tab
                    QMessageBox.warning(
                        self,
                        "Save Failed",
                        "Failed to save the form. The tab will not be closed."
                    )
                    return
        
        # Close the form
        self.controller.forms_controller.close_form(form_id)
        
        # Remove the tab
        self.removeTab(index)
        
        # Update the tab_forms mapping
        del self.tab_forms[index]
        
        # Update indices for tabs after the one that was removed
        new_tab_forms = {}
        for old_index, form_id in self.tab_forms.items():
            if old_index < index:
                new_tab_forms[old_index] = form_id
            else:
                new_tab_forms[old_index - 1] = form_id
                
        self.tab_forms = new_tab_forms
        
        # Emit signal
        self.form_closed.emit(form_id)
    
    @Slot(list)
    def _on_validation_failed(self, errors: list):
        """
        Handle validation failure.
        
        Args:
            errors: List of validation error messages
        """
        # Currently, validation errors are handled in the form view itself
        # This slot can be used for additional processing if needed
        pass
    
    @Slot(QPoint)
    def _on_context_menu_requested(self, pos):
        """
        Show a context menu for the tab.
        
        Args:
            pos: Position where the context menu was requested
        """
        # Get the tab index at the requested position
        index = self.tabBar().tabAt(pos)
        if index == -1:
            return
            
        # Create a context menu
        menu = QMenu(self)
        
        # Add actions
        close_action = menu.addAction("Close")
        close_all_action = menu.addAction("Close All")
        close_others_action = menu.addAction("Close Others")
        
        menu.addSeparator()
        
        save_action = menu.addAction("Save")
        save_as_action = menu.addAction("Save As...")
        
        # Show the menu and get the selected action
        action = menu.exec(self.tabBar().mapToGlobal(pos))
        
        # Handle the selected action
        if action == close_action:
            self._on_tab_close_requested(index)
        elif action == close_all_action:
            self._close_all_tabs()
        elif action == close_others_action:
            self._close_other_tabs(index)
        elif action == save_action:
            self._save_tab(index)
        elif action == save_as_action:
            self._save_tab_as(index)
    
    def _close_all_tabs(self):
        """Close all tabs."""
        # Copy the list of indices to avoid modification during iteration
        indices = list(self.tab_forms.keys())
        
        # Close tabs in reverse order to avoid index shifting
        for index in sorted(indices, reverse=True):
            self._on_tab_close_requested(index)
    
    def _close_other_tabs(self, keep_index: int):
        """
        Close all tabs except the specified one.
        
        Args:
            keep_index: Index of the tab to keep open
        """
        # Copy the list of indices to avoid modification during iteration
        indices = list(self.tab_forms.keys())
        
        # Close tabs in reverse order to avoid index shifting
        for index in sorted(indices, reverse=True):
            if index != keep_index:
                self._on_tab_close_requested(index)
    
    def _save_tab(self, index: int):
        """
        Save the form in the specified tab.
        
        Args:
            index: Index of the tab to save
        """
        # Get the form ID for this tab
        form_id = self.tab_forms.get(index)
        if not form_id:
            return
            
        # Save the form
        save_path = self.controller.forms_controller.save_form(form_id)
        
        if not save_path:
            QMessageBox.warning(
                self,
                "Save Failed",
                "Failed to save the form."
            )
    
    def _save_tab_as(self, index: int):
        """
        Save the form in the specified tab to a new location.
        
        Args:
            index: Index of the tab to save
        """
        # Get the form ID for this tab
        form_id = self.tab_forms.get(index)
        if not form_id:
            return
            
        # Get the form type
        form = self.controller.forms_controller.open_forms.get(form_id)
        if not form:
            return
            
        form_type = form.get_form_type()
        
        # Show a file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Form As",
            "",
            f"{form_type} Forms (*.json);;All Files (*)"
        )
        
        if not file_path:
            # User cancelled
            return
            
        # Add .json extension if not present
        if not file_path.lower().endswith('.json'):
            file_path += '.json'
            
        # Save the form
        save_path = self.controller.forms_controller.save_form(form_id, file_path)
        
        if not save_path:
            QMessageBox.warning(
                self,
                "Save Failed",
                "Failed to save the form."
            )

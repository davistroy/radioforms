"""Base form interface and common functionality for all ICS forms.

This module provides the abstract base class and common interface for all ICS forms
in the RadioForms application. It defines the contract that all form implementations
must follow, enabling consistent handling and polymorphic operations across
different form types.

The base form interface supports:
- Common validation patterns
- Unified JSON serialization
- Standard lifecycle management
- Type-safe form operations
- Consistent metadata handling

Example:
    >>> from models.ics213 import ICS213Form
    >>> from models.ics214 import ICS214Form
    >>> 
    >>> forms = [ICS213Form(), ICS214Form()]
    >>> for form in forms:
    ...     if isinstance(form, BaseForm):
    ...         print(f"Form type: {form.get_form_type()}")
    ...         print(f"Valid: {form.is_valid()}")

Classes:
    BaseForm: Abstract base class for all ICS forms
    FormMetadata: Common metadata for form instances
    FormValidationResult: Structured validation result information

Functions:
    create_form_from_type: Factory function for creating forms by type
    get_supported_form_types: Get list of all supported form types
    validate_form_data: Common validation utility

Notes:
    This implementation follows the Factory and Template Method patterns
    to provide consistent form handling while allowing form-specific
    customization. All concrete form classes must inherit from BaseForm.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union, Protocol
from enum import Enum

# Type variable for form instances
T = TypeVar('T', bound='BaseForm')


class FormType(Enum):
    """Enumeration of supported ICS form types."""
    
    ICS_213 = "ICS-213"
    ICS_214 = "ICS-214"
    ICS_201 = "ICS-201"
    ICS_202 = "ICS-202"
    ICS_203 = "ICS-203"
    ICS_204 = "ICS-204"
    ICS_205 = "ICS-205"
    ICS_205A = "ICS-205A"
    ICS_206 = "ICS-206"
    ICS_207 = "ICS-207"
    ICS_208 = "ICS-208"
    ICS_209 = "ICS-209"
    ICS_210 = "ICS-210"
    ICS_211 = "ICS-211"
    ICS_215 = "ICS-215"
    ICS_215A = "ICS-215A"
    ICS_218 = "ICS-218"
    ICS_220 = "ICS-220"
    ICS_221 = "ICS-221"
    ICS_225 = "ICS-225"


class FormStatus(Enum):
    """Enumeration of form lifecycle status values."""
    
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"


@dataclass
class FormValidationResult:
    """Structured result from form validation operations.
    
    Provides detailed information about validation success/failure with
    specific error messages and field-level validation details.
    
    Attributes:
        is_valid (bool): Whether the form passed validation.
        errors (List[str]): List of validation error messages.
        warnings (List[str]): List of validation warnings.
        field_errors (Dict[str, List[str]]): Field-specific error messages.
        validation_timestamp (datetime): When validation was performed.
        
    Example:
        >>> result = FormValidationResult(
        ...     is_valid=False,
        ...     errors=["Incident name is required"],
        ...     field_errors={"incident_name": ["This field is required"]}
        ... )
        >>> print(f"Valid: {result.is_valid}, Errors: {len(result.errors)}")
    """
    
    is_valid: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    field_errors: Dict[str, List[str]] = field(default_factory=dict)
    validation_timestamp: datetime = field(default_factory=datetime.now)
    
    def add_error(self, error: str, field: Optional[str] = None) -> None:
        """Add a validation error.
        
        Args:
            error: Error message to add.
            field: Optional field name for field-specific errors.
        """
        self.errors.append(error)
        if field:
            if field not in self.field_errors:
                self.field_errors[field] = []
            self.field_errors[field].append(error)
    
    def add_warning(self, warning: str) -> None:
        """Add a validation warning.
        
        Args:
            warning: Warning message to add.
        """
        self.warnings.append(warning)
    
    def has_errors(self) -> bool:
        """Check if validation result has any errors.
        
        Returns:
            bool: True if there are validation errors.
        """
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if validation result has any warnings.
        
        Returns:
            bool: True if there are validation warnings.
        """
        return len(self.warnings) > 0
    
    def get_error_summary(self) -> str:
        """Get a summary of all validation errors.
        
        Returns:
            str: Summary string of all errors.
        """
        if not self.has_errors():
            return "No validation errors"
        
        return f"{len(self.errors)} validation error(s): " + "; ".join(self.errors)


@dataclass
class FormMetadata:
    """Common metadata for all form instances.
    
    Provides standard metadata fields that all forms share, including
    lifecycle information, user data, and system timestamps.
    
    Attributes:
        form_id (str): Unique identifier for the form instance.
        form_type (FormType): Type of ICS form.
        status (FormStatus): Current lifecycle status.
        created_date (datetime): When the form was created.
        modified_date (datetime): When the form was last modified.
        created_by (str): User who created the form.
        modified_by (str): User who last modified the form.
        tags (Set[str]): User-defined tags for organization.
        version (int): Version number for change tracking.
        
    Example:
        >>> metadata = FormMetadata(
        ...     form_type=FormType.ICS_213,
        ...     created_by="John Doe",
        ...     tags={"training", "exercise"}
        ... )
        >>> print(f"Form: {metadata.form_type.value}, Version: {metadata.version}")
    """
    
    form_id: str = ""
    form_type: FormType = FormType.ICS_213
    status: FormStatus = FormStatus.DRAFT
    created_date: datetime = field(default_factory=datetime.now)
    modified_date: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    modified_by: str = ""
    tags: Set[str] = field(default_factory=set)
    version: int = 1
    
    def __post_init__(self) -> None:
        """Post-initialization processing."""
        # Generate form ID if not provided
        if not self.form_id:
            timestamp = self.created_date.strftime("%Y%m%d_%H%M%S_%f")
            form_prefix = self.form_type.value.lower().replace("-", "")
            self.form_id = f"{form_prefix}_{timestamp}"
        
        # Ensure tags is a set
        if isinstance(self.tags, list):
            self.tags = set(self.tags)
    
    def update_modified(self, modified_by: str = "") -> None:
        """Update modification timestamp and user.
        
        Args:
            modified_by: User making the modification.
        """
        self.modified_date = datetime.now()
        if modified_by:
            self.modified_by = modified_by
    
    def add_tag(self, tag: str) -> bool:
        """Add a tag to the form.
        
        Args:
            tag: Tag to add.
            
        Returns:
            bool: True if tag was added, False if already exists.
        """
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.add(tag)
            return True
        return False
    
    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the form.
        
        Args:
            tag: Tag to remove.
            
        Returns:
            bool: True if tag was removed, False if not found.
        """
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)
            return True
        return False
    
    def increment_version(self) -> None:
        """Increment the version number and update modified date."""
        self.version += 1
        self.modified_date = datetime.now()


class BaseForm(ABC):
    """Abstract base class for all ICS forms.
    
    This abstract base class defines the common interface that all ICS form
    implementations must provide. It ensures consistent behavior across
    different form types and enables polymorphic operations.
    
    All concrete form classes (ICS213Form, ICS214Form, etc.) must inherit
    from this class and implement the abstract methods.
    
    Example:
        >>> class CustomForm(BaseForm):
        ...     def get_form_type(self) -> FormType:
        ...         return FormType.ICS_213
        ...     
        ...     def is_valid(self) -> bool:
        ...         return True
        ...     
        ...     def to_dict(self) -> Dict[str, Any]:
        ...         return {"form_type": "ICS-213"}
    """
    
    def __init__(self) -> None:
        """Initialize base form with metadata."""
        self.metadata = FormMetadata()
    
    @abstractmethod
    def get_form_type(self) -> FormType:
        """Get the type of this form.
        
        Returns:
            FormType: The specific ICS form type.
        """
        pass
    
    @abstractmethod
    def is_valid(self) -> bool:
        """Check if the form data is valid.
        
        Returns:
            bool: True if form is valid, False otherwise.
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert form to dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary containing all form data.
        """
        pass
    
    @abstractmethod
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load form data from dictionary representation.
        
        Args:
            data: Dictionary containing form data.
        """
        pass
    
    def validate_detailed(self) -> FormValidationResult:
        """Perform detailed validation with specific error information.
        
        Returns:
            FormValidationResult: Detailed validation result.
            
        Notes:
            Default implementation calls is_valid(). Subclasses should
            override this method to provide detailed validation results.
        """
        result = FormValidationResult()
        result.is_valid = self.is_valid()
        if not result.is_valid:
            result.add_error("Form validation failed")
        return result
    
    def to_json(self) -> str:
        """Serialize form to JSON string.
        
        Returns:
            str: JSON representation of the form.
        """
        data = self.to_dict()
        # Add metadata
        data.update({
            'metadata': {
                'form_id': self.metadata.form_id,
                'form_type': self.metadata.form_type.value,
                'status': self.metadata.status.value,
                'created_date': self.metadata.created_date.isoformat(),
                'modified_date': self.metadata.modified_date.isoformat(),
                'created_by': self.metadata.created_by,
                'modified_by': self.metadata.modified_by,
                'tags': list(self.metadata.tags),
                'version': self.metadata.version
            }
        })
        return json.dumps(data, indent=2)
    
    def from_json(self, json_data: str) -> None:
        """Load form data from JSON string.
        
        Args:
            json_data: JSON string containing form data.
            
        Raises:
            ValueError: If JSON data is invalid.
        """
        try:
            data = json.loads(json_data)
            
            # Load metadata if present
            if 'metadata' in data:
                metadata_dict = data.pop('metadata')
                self.metadata.form_id = metadata_dict.get('form_id', '')
                self.metadata.form_type = FormType(metadata_dict.get('form_type', 'ICS-213'))
                self.metadata.status = FormStatus(metadata_dict.get('status', 'draft'))
                self.metadata.created_by = metadata_dict.get('created_by', '')
                self.metadata.modified_by = metadata_dict.get('modified_by', '')
                self.metadata.tags = set(metadata_dict.get('tags', []))
                self.metadata.version = metadata_dict.get('version', 1)
                
                # Parse timestamps
                if metadata_dict.get('created_date'):
                    self.metadata.created_date = datetime.fromisoformat(
                        metadata_dict['created_date'].replace('Z', '+00:00')
                    )
                if metadata_dict.get('modified_date'):
                    self.metadata.modified_date = datetime.fromisoformat(
                        metadata_dict['modified_date'].replace('Z', '+00:00')
                    )
            
            # Load form-specific data
            self.from_dict(data)
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            raise ValueError(f"Invalid JSON data for form: {e}")
    
    def get_form_id(self) -> str:
        """Get the unique form identifier.
        
        Returns:
            str: Form ID.
        """
        return self.metadata.form_id
    
    def get_status(self) -> FormStatus:
        """Get the current form status.
        
        Returns:
            FormStatus: Current status.
        """
        return self.metadata.status
    
    def set_status(self, status: FormStatus, modified_by: str = "") -> None:
        """Set the form status.
        
        Args:
            status: New status to set.
            modified_by: User making the change.
        """
        self.metadata.status = status
        self.metadata.update_modified(modified_by)
    
    def add_tag(self, tag: str) -> bool:
        """Add a tag to the form.
        
        Args:
            tag: Tag to add.
            
        Returns:
            bool: True if tag was added.
        """
        return self.metadata.add_tag(tag)
    
    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the form.
        
        Args:
            tag: Tag to remove.
            
        Returns:
            bool: True if tag was removed.
        """
        return self.metadata.remove_tag(tag)
    
    def get_tags(self) -> Set[str]:
        """Get all tags for this form.
        
        Returns:
            Set[str]: Set of tags.
        """
        return self.metadata.tags.copy()
    
    def get_created_date(self) -> datetime:
        """Get the form creation date.
        
        Returns:
            datetime: Creation date.
        """
        return self.metadata.created_date
    
    def get_modified_date(self) -> datetime:
        """Get the form modification date.
        
        Returns:
            datetime: Last modification date.
        """
        return self.metadata.modified_date
    
    def get_version(self) -> int:
        """Get the form version number.
        
        Returns:
            int: Version number.
        """
        return self.metadata.version
    
    def increment_version(self, modified_by: str = "") -> None:
        """Increment version and update modification info.
        
        Args:
            modified_by: User making the change.
        """
        self.metadata.increment_version()
        if modified_by:
            self.metadata.modified_by = modified_by


# Utility functions for form operations

def get_supported_form_types() -> List[FormType]:
    """Get list of all supported form types.
    
    Returns:
        List[FormType]: List of supported form types.
    """
    return list(FormType)


def create_form_from_type(form_type: FormType) -> Optional[BaseForm]:
    """Factory function to create form instances by type.
    
    Args:
        form_type: Type of form to create.
        
    Returns:
        BaseForm: New form instance or None if type not supported.
        
    Notes:
        This function will be extended as more form types are implemented.
        Currently supports ICS-213 and ICS-214 forms.
    """
    try:
        if form_type == FormType.ICS_213:
            # Import here to avoid circular dependencies
            from ..forms.ics213 import ICS213Form
            return ICS213Form()
        elif form_type == FormType.ICS_214:
            # Import here to avoid circular dependencies  
            from .ics214 import ICS214Form
            return ICS214Form()
        # Add more form types as they are implemented
        else:
            return None
    except ImportError:
        # Handle cases where form modules aren't available
        return None


def validate_form_data(form: BaseForm) -> FormValidationResult:
    """Common validation utility for any form type.
    
    Args:
        form: Form instance to validate.
        
    Returns:
        FormValidationResult: Detailed validation result.
    """
    return form.validate_detailed()


def get_form_type_from_string(form_type_str: str) -> Optional[FormType]:
    """Convert string to FormType enum.
    
    Args:
        form_type_str: String representation of form type.
        
    Returns:
        FormType: Matching form type or None if not found.
    """
    try:
        return FormType(form_type_str)
    except ValueError:
        return None


def is_form_type_supported(form_type: FormType) -> bool:
    """Check if a form type is currently supported.
    
    Args:
        form_type: Form type to check.
        
    Returns:
        bool: True if form type is supported.
    """
    # Currently supported types
    supported_types = {FormType.ICS_213, FormType.ICS_214}
    return form_type in supported_types
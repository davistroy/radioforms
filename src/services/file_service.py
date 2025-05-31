"""File operations service for RadioForms.

This module provides file import/export functionality including JSON
export/import with proper validation and error handling.
"""

import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..forms.ics213 import ICS213Form, ValidationError
from ..database.connection import DatabaseError


logger = logging.getLogger(__name__)


class FileServiceError(Exception):
    """Base exception for file service errors."""
    pass


class FileService:
    """Service for file operations including export/import.
    
    This class handles JSON export/import operations with proper
    validation, error handling, and backup creation.
    """
    
    def __init__(self):
        """Initialize file service."""
        self.logger = logging.getLogger(__name__)
        self.logger.debug("FileService initialized")
    
    def export_form_to_json(self, form: ICS213Form, file_path: Path, 
                           include_metadata: bool = True) -> bool:
        """Export form to JSON file.
        
        Args:
            form: ICS213Form to export
            file_path: Path to save JSON file
            include_metadata: Whether to include export metadata
            
        Returns:
            True if export successful
            
        Raises:
            FileServiceError: If export operation fails
        """
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup if file exists
            if file_path.exists():
                self._create_backup(file_path)
            
            # Prepare export data
            export_data = {
                "radioforms_export": {
                    "format_version": "1.0",
                    "export_timestamp": datetime.now().isoformat(),
                    "form_type": "ICS-213"
                },
                "form": json.loads(form.to_json())
            }
            
            if include_metadata:
                export_data["metadata"] = {
                    "exported_by": "RadioForms v0.1.0",
                    "export_date": datetime.now().strftime("%Y-%m-%d"),
                    "export_time": datetime.now().strftime("%H:%M:%S"),
                    "form_summary": form.get_summary()
                }
            
            # Write JSON file with proper formatting
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Form exported to {file_path}")
            return True
            
        except (IOError, OSError) as e:
            error_msg = f"Failed to export form to {file_path}: {e}"
            self.logger.error(error_msg)
            raise FileServiceError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error during export: {e}"
            self.logger.error(error_msg)
            raise FileServiceError(error_msg) from e
    
    def import_form_from_json(self, file_path: Path) -> ICS213Form:
        """Import form from JSON file.
        
        Args:
            file_path: Path to JSON file to import
            
        Returns:
            Imported ICS213Form
            
        Raises:
            FileServiceError: If import operation fails
            ValidationError: If imported data is invalid
        """
        try:
            # Check file exists and is readable
            if not file_path.exists():
                raise FileServiceError(f"File not found: {file_path}")
            
            if not file_path.is_file():
                raise FileServiceError(f"Path is not a file: {file_path}")
            
            # Read and parse JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate export format
            self._validate_import_data(data)
            
            # Extract form data
            form_data = data.get("form", {})
            
            # Create form from imported data
            form = ICS213Form.from_json(json.dumps(form_data))
            
            # Validate imported form
            if not form.validate():
                errors = form.get_validation_errors()
                raise ValidationError(f"Imported form is invalid: {errors}")
            
            self.logger.info(f"Form imported from {file_path}")
            return form
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format in {file_path}: {e}"
            self.logger.error(error_msg)
            raise FileServiceError(error_msg) from e
        except ValidationError:
            raise  # Re-raise validation errors as-is
        except (IOError, OSError) as e:
            error_msg = f"Failed to read file {file_path}: {e}"
            self.logger.error(error_msg)
            raise FileServiceError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error during import: {e}"
            self.logger.error(error_msg)
            raise FileServiceError(error_msg) from e
    
    def export_multiple_forms(self, forms: List[ICS213Form], file_path: Path) -> bool:
        """Export multiple forms to a single JSON file.
        
        Args:
            forms: List of ICS213Forms to export
            file_path: Path to save JSON file
            
        Returns:
            True if export successful
            
        Raises:
            FileServiceError: If export operation fails
        """
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup if file exists
            if file_path.exists():
                self._create_backup(file_path)
            
            # Prepare export data
            export_data = {
                "radioforms_export": {
                    "format_version": "1.0",
                    "export_timestamp": datetime.now().isoformat(),
                    "form_type": "ICS-213",
                    "form_count": len(forms)
                },
                "forms": [json.loads(form.to_json()) for form in forms],
                "metadata": {
                    "exported_by": "RadioForms v0.1.0",
                    "export_date": datetime.now().strftime("%Y-%m-%d"),
                    "export_time": datetime.now().strftime("%H:%M:%S"),
                    "form_summaries": [form.get_summary() for form in forms]
                }
            }
            
            # Write JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported {len(forms)} forms to {file_path}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to export multiple forms: {e}"
            self.logger.error(error_msg)
            raise FileServiceError(error_msg) from e
    
    def import_multiple_forms(self, file_path: Path) -> List[ICS213Form]:
        """Import multiple forms from JSON file.
        
        Args:
            file_path: Path to JSON file containing multiple forms
            
        Returns:
            List of imported ICS213Forms
            
        Raises:
            FileServiceError: If import operation fails
        """
        try:
            # Read and parse JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate format
            self._validate_import_data(data)
            
            # Check if it's multiple forms format
            if "forms" not in data:
                raise FileServiceError("File does not contain multiple forms")
            
            forms_data = data["forms"]
            if not isinstance(forms_data, list):
                raise FileServiceError("Forms data is not a list")
            
            # Import each form
            forms = []
            for i, form_data in enumerate(forms_data):
                try:
                    form = ICS213Form.from_json(json.dumps(form_data))
                    if not form.validate():
                        errors = form.get_validation_errors()
                        self.logger.warning(f"Form {i+1} has validation errors: {errors}")
                    forms.append(form)
                except Exception as e:
                    self.logger.error(f"Failed to import form {i+1}: {e}")
                    # Continue with other forms
            
            self.logger.info(f"Imported {len(forms)} forms from {file_path}")
            return forms
            
        except FileServiceError:
            raise  # Re-raise our own exceptions
        except Exception as e:
            error_msg = f"Failed to import multiple forms: {e}"
            self.logger.error(error_msg)
            raise FileServiceError(error_msg) from e
    
    def validate_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Validate JSON file format without importing.
        
        Args:
            file_path: Path to JSON file to validate
            
        Returns:
            Dictionary with validation results
        """
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "info": {}
        }
        
        try:
            # Check file exists
            if not file_path.exists():
                result["errors"].append(f"File not found: {file_path}")
                return result
            
            # Read and parse JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate structure
            try:
                self._validate_import_data(data)
            except FileServiceError as e:
                result["errors"].append(str(e))
                return result
            
            # Get info about the file
            export_info = data.get("radioforms_export", {})
            result["info"] = {
                "format_version": export_info.get("format_version"),
                "export_timestamp": export_info.get("export_timestamp"),
                "form_type": export_info.get("form_type"),
                "form_count": export_info.get("form_count", 1)
            }
            
            # Check for multiple forms
            if "forms" in data:
                result["info"]["is_multiple"] = True
                result["info"]["form_count"] = len(data["forms"])
            else:
                result["info"]["is_multiple"] = False
            
            result["valid"] = True
            self.logger.debug(f"Validated JSON file: {file_path}")
            
        except json.JSONDecodeError as e:
            result["errors"].append(f"Invalid JSON format: {e}")
        except Exception as e:
            result["errors"].append(f"Validation error: {e}")
        
        return result
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats.
        
        Returns:
            List of supported file extensions
        """
        return [".json"]
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get information about a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        info = {
            "exists": file_path.exists(),
            "size": 0,
            "modified": None,
            "readable": False,
            "writable": False
        }
        
        try:
            if file_path.exists():
                stat = file_path.stat()
                info["size"] = stat.st_size
                info["modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                info["readable"] = file_path.is_file() and os.access(file_path, os.R_OK)
                info["writable"] = os.access(file_path.parent, os.W_OK)
        except Exception as e:
            info["error"] = str(e)
        
        return info
    
    def _validate_import_data(self, data: Dict[str, Any]) -> None:
        """Validate imported JSON data structure.
        
        Args:
            data: Parsed JSON data
            
        Raises:
            FileServiceError: If data structure is invalid
        """
        if not isinstance(data, dict):
            raise FileServiceError("Root element must be an object")
        
        # Check for RadioForms export header
        if "radioforms_export" not in data:
            raise FileServiceError("Missing RadioForms export header")
        
        export_info = data["radioforms_export"]
        if not isinstance(export_info, dict):
            raise FileServiceError("Export header must be an object")
        
        # Check format version
        format_version = export_info.get("format_version")
        if format_version != "1.0":
            raise FileServiceError(f"Unsupported format version: {format_version}")
        
        # Check form type
        form_type = export_info.get("form_type")
        if form_type != "ICS-213":
            raise FileServiceError(f"Unsupported form type: {form_type}")
        
        # Check for form data
        if "form" not in data and "forms" not in data:
            raise FileServiceError("No form data found")
    
    def _create_backup(self, file_path: Path) -> Path:
        """Create backup of existing file.
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.with_suffix(f".backup_{timestamp}{file_path.suffix}")
        
        try:
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.warning(f"Failed to create backup: {e}")
            raise FileServiceError(f"Failed to create backup: {e}") from e
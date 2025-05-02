#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Form Loading Enhancement Script.

This script enhances the form model registry's form loading mechanism to better
handle form type resolution, addressing the "Form type not found for form" warnings.
"""

import sys
import os
import logging
import re
from pathlib import Path
import json

# Add parent directory to path to import RadioForms modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def enhance_form_registry_loading():
    """
    Enhance the form model registry's form loading mechanism.
    
    Returns:
        True if successful, False otherwise
    """
    registry_path = Path("radioforms/models/form_model_registry.py")
    
    if not registry_path.exists():
        logger.error(f"Registry file not found: {registry_path}")
        return False
    
    # Read current content
    with open(registry_path, 'r') as f:
        content = f.read()
    
    # Track changes
    changes_made = []
    
    # 1. Find the load_form method
    load_form_pattern = r'def load_form\(self, form_id: str.*?return form\s*\n' 
    load_form_match = re.search(load_form_pattern, content, re.DOTALL)
    
    if not load_form_match:
        logger.error("Could not find load_form method in registry")
        return False
    
    # Get current method
    current_method = load_form_match.group(0)
    
    # 2. Create enhanced method with improved form type resolution
    enhanced_method = """def load_form(self, form_id: str, version_id: str = None) -> Optional[Any]:
        \"\"\"
        Load a form from the database.
        
        Args:
            form_id: Form ID
            version_id: Optional version ID to load a specific version
            
        Returns:
            Form instance, or None if not found
        \"\"\"
        if self._form_dao is None:
            self._logger.error("Form DAO not set")
            return None
            
        try:
            # Use direct SQL to bypass DAO issues
            conn = self._form_dao.db_manager.connect()
            
            # Load form data
            if version_id:
                cursor = conn.execute(
                    \"\"\"
                    SELECT content FROM form_versions
                    WHERE version_id = ?
                    \"\"\",
                    (version_id,)
                )
                version_row = cursor.fetchone()
                if not version_row:
                    self._logger.warning(f"Form version with ID {version_id} not found")
                    return None
                
                # Parse version content
                try:
                    form_data = json.loads(version_row['content'])
                except (json.JSONDecodeError, TypeError):
                    form_data = {}
                
                # Get form type from form data
                form_type = form_data.get("form_type")
                
                # Also get form metadata
                cursor = conn.execute(
                    \"\"\"
                    SELECT * FROM forms
                    WHERE form_id = ?
                    \"\"\",
                    (form_id,)
                )
                form_row = cursor.fetchone()
                if form_row:
                    # Add form metadata to form data
                    form_data.update({
                        "form_id": form_id,
                        "form_type": form_row["form_type"],
                        "state": form_row["state"],
                        "created_at": form_row["created_at"],
                        "updated_at": form_row["updated_at"]
                    })
            else:
                # Load current form data
                cursor = conn.execute(
                    \"\"\"
                    SELECT * FROM forms
                    WHERE form_id = ?
                    \"\"\",
                    (form_id,)
                )
                form_row = cursor.fetchone()
                
                if not form_row:
                    self._logger.warning(f"Form with ID {form_id} not found")
                    return None
                    
                # Get form metadata
                form_data = dict(form_row)
                
                # Parse form content from data field
                if "data" in form_data and form_data["data"]:
                    try:
                        content_data = json.loads(form_data["data"])
                        # Add content data to form data
                        for key, value in content_data.items():
                            if key not in form_data:
                                form_data[key] = value
                    except json.JSONDecodeError:
                        self._logger.warning(f"Could not parse form data for form {form_id}")
            
            # Get form type with fallback mechanisms
            form_type = form_data.get("form_type")
            
            # Fallback 1: Try to infer form type from form ID prefix (e.g., 'ICS213-...')
            if not form_type:
                for registered_type in self._form_types.keys():
                    if form_id.upper().startswith(registered_type.upper() + '-'):
                        form_type = registered_type
                        self._logger.info(f"Inferred form type {form_type} from form ID {form_id}")
                        break
            
            # Fallback 2: Look for type indicators in data content
            if not form_type and "data" in form_data and form_data["data"]:
                try:
                    content_data = json.loads(form_data["data"])
                    # Check for type-specific fields
                    if "message" in content_data and "from_field" in content_data:
                        form_type = "ICS-213"
                        self._logger.info(f"Inferred form type ICS-213 from content fields for form {form_id}")
                    elif "activity_log" in content_data:
                        form_type = "ICS-214"
                        self._logger.info(f"Inferred form type ICS-214 from content fields for form {form_id}")
                except (json.JSONDecodeError, TypeError):
                    pass
            
            # Final check
            if not form_type:
                self._logger.warning(f"Form type not found for form {form_id}")
                # Try default to a generic form type if available
                for common_type in ["ICS-213", "ICS-214"]:
                    if common_type in self._form_types:
                        form_type = common_type
                        self._logger.info(f"Using default form type {form_type} for form {form_id}")
                        break
                if not form_type:
                    return None
                
            if form_type not in self._form_types:
                self._logger.warning(f"Form type {form_type} not registered")
                return None
                
            # Create form instance
            model_class = self._form_types[form_type]
            
            # Check if the form has a from_dict method
            if hasattr(model_class, 'from_dict') and callable(getattr(model_class, 'from_dict')):
                # Use the form's from_dict method
                form = model_class.from_dict(form_data)
            else:
                # Create a new instance and manually set attributes
                form = model_class()
                
                # Process JSON data if present
                if "data" in form_data and form_data["data"]:
                    try:
                        # Try to parse JSON data
                        json_data = json.loads(form_data["data"])
                        
                        # Update form attributes from JSON data
                        for key, value in json_data.items():
                            if hasattr(form, key):
                                setattr(form, key, value)
                    except json.JSONDecodeError:
                        self._logger.warning(f"Could not parse JSON data for form {form_id}")
                        
                # Set form metadata fields directly from form_data
                for key in ["form_id", "form_type", "state", "status", "created_at", "updated_at", "title"]:
                    if key in form_data and hasattr(form, key):
                        setattr(form, key, form_data[key])
                        
                # Also try to copy any other fields that might be in the form
                for key, value in form_data.items():
                    if key not in ["form_id", "form_type", "state", "status", "created_at", "updated_at", "data", "title"]:
                        if hasattr(form, key):
                            setattr(form, key, value)
            
            # Ensure the form ID is set
            form.form_id = form_id
            
            self._logger.debug(f"Loaded form of type {form_type} with ID {form_id}")
            
            return form
            
        except Exception as e:
            self._logger.error(f"Failed to load form {form_id}: {e}")
            return None
"""
    
    # Replace the method
    new_content = content.replace(current_method, enhanced_method)
    if new_content != content:
        changes_made.append("Enhanced form loading method with improved form type resolution")
    
    # 3. Fix form type resolution in form_versions
    version_pattern = r'self\.form_dao\.find_version_by_id = MagicMock\(.*?content'
    version_match = re.search(version_pattern, content, re.DOTALL)
    
    if version_match:
        # Add form_type field to make sure it's properly extracted
        fixed_version = """# Enhance version handling to include form_type in content field
            cursor = conn.execute(
                \"\"\"
                SELECT v.*, f.form_type 
                FROM form_versions v
                JOIN forms f ON v.form_id = f.form_id
                WHERE v.version_id = ?
                \"\"\",
                (version_id,)
            )
            version_row = cursor.fetchone()
            if not version_row:
                self._logger.warning(f"Form version with ID {version_id} not found")
                return None
            
            # Add form_type to content if not present
            try:
                content_data = json.loads(version_row['content'])
                if 'form_type' not in content_data and 'form_type' in version_row:
                    content_data['form_type'] = version_row['form_type']
                    version_row['content'] = json.dumps(content_data)
            except (json.JSONDecodeError, TypeError):
                pass
            
            # Parse version content"""
        
        new_content = new_content.replace("""# Parse version content""", fixed_version)
        if new_content != content:
            changes_made.append("Enhanced version handling to include form_type field")
    
    # Save changes
    if changes_made:
        with open(registry_path, 'w') as f:
            f.write(new_content)
        
        logger.info("Form registry loading enhanced:")
        for change in changes_made:
            logger.info(f"- {change}")
        
        return True
    else:
        logger.info("No changes made to form registry loading")
        return False


def main():
    """Run the script."""
    logger.info("Starting form loading enhancement script")
    
    if enhance_form_registry_loading():
        logger.info("Form loading mechanism enhanced successfully")
        return 0
    else:
        logger.warning("Failed to enhance form loading mechanism")
        return 1


if __name__ == "__main__":
    sys.exit(main())

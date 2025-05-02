#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enhanced Form Resolver.

This module provides advanced form type resolution capabilities to improve 
form loading reliability, especially for edge cases and ambiguous form types.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
import datetime

logger = logging.getLogger(__name__)


class FormTypeResolver:
    """
    Resolver for determining form types from various data sources.
    
    This class implements advanced heuristics for determining the correct form type
    when loading forms, using multiple signals and fallback strategies.
    """
    
    # Form type signature patterns - these are field combinations that uniquely identify form types
    FORM_SIGNATURES = {
        "ICS-213": {
            "required_fields": ["to", "from", "subject", "message"],
            "optional_fields": ["approved_by", "reply", "date", "time"],
            "pattern": r"ICS.?213|General Message"
        },
        "ICS-214": {
            "required_fields": ["activity_log", "prepared_by"],
            "optional_fields": ["name", "position", "home_agency", "date_from", "date_to"],
            "pattern": r"ICS.?214|Activity Log"
        }
        # Additional form types can be added here
    }
    
    # Form type ID patterns - these are regex patterns that can identify form types from form IDs
    ID_PATTERNS = {
        r"(?i)ICS.?213": "ICS-213",
        r"(?i)ICS.?214": "ICS-214",
        r"(?i)message": "ICS-213"
    }
    
    # Form metadata mappings - maps field names across different form versions
    FIELD_MAPPINGS = {
        # For ICS-213 forms
        "sender": "from",
        "recipient": "to",
        "from_field": "from",
        "to_field": "to",
        "message_body": "message",
        
        # For ICS-214 forms
        "activities": "activity_log",
        "personnel": "personnel_list",
        "preparer": "prepared_by"
    }
    
    def __init__(self, default_form_type: Optional[str] = None, 
                 strict_matching: bool = False):
        """
        Initialize the form type resolver.
        
        Args:
            default_form_type: Default form type to use when no match is found
            strict_matching: If True, only return a match if confident
        """
        self.default_form_type = default_form_type
        self.strict_matching = strict_matching
    
    def resolve_form_type(self, form_data: Dict[str, Any], 
                          form_id: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Determine form type from form data, ID, and metadata using multiple strategies.
        
        Args:
            form_data: Form data dictionary
            form_id: Optional form ID
            metadata: Optional metadata dictionary
            
        Returns:
            Resolved form type, or default form type if no match found
        """
        # Start with the highest confidence signals
        
        # 1. Check explicit form_type in form_data or metadata
        form_type = self._check_explicit_type(form_data, metadata)
        if form_type:
            logger.debug(f"Resolved form type from explicit type: {form_type}")
            return form_type
            
        # 2. Check form ID for type indicators
        if form_id:
            form_type = self._check_id_pattern(form_id)
            if form_type:
                logger.debug(f"Resolved form type from ID pattern: {form_type}")
                return form_type
                
        # 3. Check form content signatures
        form_type = self._check_form_signature(form_data)
        if form_type:
            logger.debug(f"Resolved form type from form signature: {form_type}")
            return form_type
            
        # 4. Check for title or other text indicators
        form_type = self._check_text_indicators(form_data, metadata)
        if form_type:
            logger.debug(f"Resolved form type from text indicators: {form_type}")
            return form_type
            
        # 5. Make educated guess based on known form structures
        form_type = self._guess_from_structure(form_data)
        if form_type:
            logger.debug(f"Guessed form type from structure: {form_type}")
            return form_type
            
        # 6. Fall back to default
        if self.default_form_type:
            logger.warning(f"Using default form type '{self.default_form_type}' for form {form_id or 'unknown'}")
            return self.default_form_type
            
        # 7. If no default, return most common type as last resort
        logger.warning(f"Could not determine form type for form {form_id or 'unknown'}, defaulting to ICS-213")
        return "ICS-213"  # Fallback to most common form type
    
    def _check_explicit_type(self, form_data: Dict[str, Any], 
                             metadata: Optional[Dict[str, Any]]) -> Optional[str]:
        """
        Check for explicit form type in form data or metadata.
        
        Args:
            form_data: Form data dictionary
            metadata: Optional metadata dictionary
            
        Returns:
            Form type if found, None otherwise
        """
        # Check form_data
        if "form_type" in form_data and form_data["form_type"]:
            return self._normalize_form_type(form_data["form_type"])
            
        if "type" in form_data and form_data["type"]:
            return self._normalize_form_type(form_data["type"])
            
        # Check metadata
        if metadata:
            if "form_type" in metadata and metadata["form_type"]:
                return self._normalize_form_type(metadata["form_type"])
                
            if "type" in metadata and metadata["type"]:
                return self._normalize_form_type(metadata["type"])
                
        return None
    
    def _check_id_pattern(self, form_id: str) -> Optional[str]:
        """
        Check form ID for type indicators using regex patterns.
        
        Args:
            form_id: Form ID
            
        Returns:
            Form type if found, None otherwise
        """
        for pattern, form_type in self.ID_PATTERNS.items():
            if re.search(pattern, form_id):
                return form_type
                
        return None
    
    def _check_form_signature(self, form_data: Dict[str, Any]) -> Optional[str]:
        """
        Check for form type signatures in form data.
        
        Args:
            form_data: Form data dictionary
            
        Returns:
            Form type if found, None otherwise
        """
        # Normalize field names
        normalized_data = self._normalize_field_names(form_data)
        
        # Check each form signature
        form_type_scores = {}
        
        for form_type, signature in self.FORM_SIGNATURES.items():
            score = 0
            
            # Check required fields
            required_fields = signature["required_fields"]
            for field in required_fields:
                if field in normalized_data and normalized_data[field]:
                    score += 2
                    
            # Check optional fields
            optional_fields = signature["optional_fields"]
            for field in optional_fields:
                if field in normalized_data and normalized_data[field]:
                    score += 1
            
            # Check pattern against all text content
            pattern = signature["pattern"]
            for field, value in normalized_data.items():
                if isinstance(value, str) and re.search(pattern, value, re.IGNORECASE):
                    score += 3
            
            # Record score
            form_type_scores[form_type] = score
        
        # Find highest score
        if form_type_scores:
            best_form_type = max(form_type_scores.items(), key=lambda x: x[1])
            
            # Only return if score is substantial
            if best_form_type[1] >= 3 or not self.strict_matching:
                return best_form_type[0]
        
        return None
    
    def _check_text_indicators(self, form_data: Dict[str, Any], 
                               metadata: Optional[Dict[str, Any]]) -> Optional[str]:
        """
        Check for form type indicators in text fields.
        
        Args:
            form_data: Form data dictionary
            metadata: Optional metadata dictionary
            
        Returns:
            Form type if found, None otherwise
        """
        # Combine all text fields from form_data and metadata
        all_text = []
        
        # Add form_data text fields
        for field, value in form_data.items():
            if isinstance(value, str):
                all_text.append(value)
                
        # Add metadata text fields
        if metadata:
            for field, value in metadata.items():
                if isinstance(value, str):
                    all_text.append(value)
        
        # Check text for form type indicators
        combined_text = " ".join(all_text)
        
        # Check specific patterns
        if re.search(r"ICS.?213|General Message", combined_text, re.IGNORECASE):
            return "ICS-213"
            
        if re.search(r"ICS.?214|Activity Log", combined_text, re.IGNORECASE):
            return "ICS-214"
        
        return None
    
    def _guess_from_structure(self, form_data: Dict[str, Any]) -> Optional[str]:
        """
        Make educated guess about form type based on form structure.
        
        Args:
            form_data: Form data dictionary
            
        Returns:
            Form type if confident guess can be made, None otherwise
        """
        # Normalize field names
        normalized_data = self._normalize_field_names(form_data)
        
        # Check for activity_log or personnel_list (indicates ICS-214)
        if ("activity_log" in normalized_data and isinstance(normalized_data["activity_log"], list)) or \
           ("personnel_list" in normalized_data and isinstance(normalized_data["personnel_list"], list)):
            return "ICS-214"
            
        # Check for message and subject (indicates ICS-213)
        if "message" in normalized_data and "subject" in normalized_data:
            return "ICS-213"
            
        # Check for from/to fields (indicates ICS-213)
        if ("from" in normalized_data or "sender" in normalized_data) and \
           ("to" in normalized_data or "recipient" in normalized_data):
            return "ICS-213"
        
        return None
    
    def _normalize_form_type(self, form_type: str) -> str:
        """
        Normalize form type string to standard format.
        
        Args:
            form_type: Form type string
            
        Returns:
            Normalized form type
        """
        form_type = form_type.upper().strip()
        
        # Remove spaces and hyphens
        clean_type = re.sub(r'[^a-zA-Z0-9]', '', form_type)
        
        # Common mappings
        if clean_type == "ICS213" or clean_type == "213":
            return "ICS-213"
            
        if clean_type == "ICS214" or clean_type == "214":
            return "ICS-214"
            
        # Try to extract ICS number
        match = re.search(r'ICS\.?([0-9]+)', form_type, re.IGNORECASE)
        if match:
            return f"ICS-{match.group(1)}"
            
        # Return original if no mapping found
        return form_type
    
    def _normalize_field_names(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize field names to standard names.
        
        Args:
            form_data: Form data dictionary
            
        Returns:
            Dictionary with normalized field names
        """
        normalized_data = {}
        
        for field, value in form_data.items():
            # Convert to lower case for comparison
            field_lower = field.lower()
            
            # Use mapping if available
            if field_lower in self.FIELD_MAPPINGS:
                normalized_field = self.FIELD_MAPPINGS[field_lower]
            else:
                normalized_field = field
                
            normalized_data[normalized_field] = value
        
        return normalized_data


class NestedFieldExtractor:
    """
    Extracts and flattens fields from nested JSON data structures.
    
    This utility class is used to extract fields from nested structures
    for form type resolution.
    """
    
    @staticmethod
    def extract_all_fields(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract all fields from a nested data structure.
        
        Args:
            data: Nested data structure
            
        Returns:
            Flattened dictionary with all fields
        """
        result = {}
        
        def extract_recursive(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{prefix}.{key}" if prefix else key
                    if isinstance(value, (dict, list)):
                        extract_recursive(value, new_key)
                    else:
                        result[new_key] = value
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_key = f"{prefix}[{i}]"
                    if isinstance(item, (dict, list)):
                        extract_recursive(item, new_key)
                    else:
                        result[new_key] = item
        
        extract_recursive(data)
        return result


class FormMetadataExtractor:
    """
    Extracts metadata from form data structures.
    
    This utility class extracts common metadata from form data structures,
    which can be used for form type resolution.
    """
    
    @staticmethod
    def extract_metadata(form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from form data.
        
        Args:
            form_data: Form data dictionary
            
        Returns:
            Dictionary with extracted metadata
        """
        metadata = {}
        
        # Extract common metadata fields
        for field in ["form_id", "form_type", "state", "title", "created_at", "updated_at"]:
            if field in form_data:
                metadata[field] = form_data[field]
        
        # Extract text content for searching
        text_content = []
        
        for field, value in form_data.items():
            if isinstance(value, str):
                if len(value) > 3:  # Skip very short values
                    text_content.append(value)
        
        if text_content:
            metadata["text_content"] = " ".join(text_content)
        
        return metadata


def resolve_form_type(form_data: Dict[str, Any], form_id: Optional[str] = None) -> str:
    """
    Convenience function to resolve form type.
    
    Args:
        form_data: Form data dictionary
        form_id: Optional form ID
        
    Returns:
        Resolved form type
    """
    # Extract metadata
    metadata = FormMetadataExtractor.extract_metadata(form_data)
    
    # Flatten nested structures if needed
    if "data" in form_data and isinstance(form_data["data"], (str, dict)):
        if isinstance(form_data["data"], str):
            try:
                nested_data = json.loads(form_data["data"])
                if isinstance(nested_data, dict):
                    flat_data = NestedFieldExtractor.extract_all_fields(nested_data)
                    form_data.update(flat_data)
            except json.JSONDecodeError:
                pass
        elif isinstance(form_data["data"], dict):
            flat_data = NestedFieldExtractor.extract_all_fields(form_data["data"])
            form_data.update(flat_data)
    
    # Use resolver
    resolver = FormTypeResolver(default_form_type="ICS-213")
    return resolver.resolve_form_type(form_data, form_id, metadata)


def extract_form_type_from_id(form_id: str) -> Optional[str]:
    """
    Extract form type from form ID.
    
    Args:
        form_id: Form ID
        
    Returns:
        Extracted form type, or None if not found
    """
    # Check form ID patterns
    for pattern, form_type in FormTypeResolver.ID_PATTERNS.items():
        if re.search(pattern, form_id):
            return form_type
    
    return None


if __name__ == "__main__":
    # Example usage
    test_data = {
        "form_id": "ICS213-123",
        "data": json.dumps({
            "to": "Jane Doe",
            "from": "John Smith",
            "subject": "Test Message",
            "message": "This is a test message"
        })
    }
    
    form_type = resolve_form_type(test_data, test_data["form_id"])
    print(f"Resolved form type: {form_type}")

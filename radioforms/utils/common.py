#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Common utility functions used throughout the application.
"""

import os
import re
import json
import datetime
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID with an optional prefix.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        A unique identifier string
    """
    import uuid
    unique_id = str(uuid.uuid4())
    return f"{prefix}{unique_id}" if prefix else unique_id


def format_date(date: datetime.datetime, format_str: str = "%Y-%m-%d") -> str:
    """
    Format a datetime object as a string.
    
    Args:
        date: Datetime object to format
        format_str: Format string (default: YYYY-MM-DD)
        
    Returns:
        Formatted date string
    """
    if not date:
        return ""
    return date.strftime(format_str)


def parse_date(date_str: str, format_str: str = "%Y-%m-%d") -> Optional[datetime.datetime]:
    """
    Parse a date string into a datetime object.
    
    Args:
        date_str: Date string to parse
        format_str: Format string (default: YYYY-MM-DD)
        
    Returns:
        Datetime object or None if parsing fails
    """
    if not date_str:
        return None
        
    try:
        return datetime.datetime.strptime(date_str, format_str)
    except ValueError:
        return None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Replace invalid characters with underscores
    return re.sub(r'[\\/*?:"<>|]', "_", filename)


def ensure_dir_exists(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object for the directory
    """
    path_obj = Path(path)
    os.makedirs(path_obj, exist_ok=True)
    return path_obj


def calculate_file_hash(file_path: Union[str, Path]) -> str:
    """
    Calculate the SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Hex string of the file hash
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in 64kb chunks
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def deep_merge(target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries, recursively merging nested dictionaries.
    
    Args:
        target: Target dictionary (modified in-place)
        source: Source dictionary (values override target)
        
    Returns:
        The modified target dictionary
    """
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            deep_merge(target[key], value)
        else:
            target[key] = value
    return target


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.
    
    Args:
        text: String to truncate
        max_length: Maximum length (default: 100)
        suffix: Suffix to add if truncated (default: "...")
        
    Returns:
        Truncated string
    """
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


class Singleton(type):
    """
    Metaclass for implementing the Singleton pattern.
    
    Usage:
        class MyClass(metaclass=Singleton):
            pass
    """
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Attachment entity model representing a file attachment in the system.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from radioforms.database.models.base_model import TimestampedModel


class Attachment(TimestampedModel):
    """
    Attachment entity model representing a file attachment to a form.
    
    Stores metadata about file attachments, including file path, name, 
    type, and size.
    """
    
    def __init__(self, id: Optional[int] = None, 
                form_id: int = 0,
                file_path: str = "",
                file_name: str = "",
                file_type: str = "",
                file_size: int = 0,
                created_at: Optional[datetime] = None,
                updated_at: Optional[datetime] = None):
        """
        Initialize an Attachment entity.
        
        Args:
            id: Attachment ID
            form_id: ID of the form this attachment belongs to
            file_path: Path to the file on disk
            file_name: Original name of the file
            file_type: MIME type or file extension
            file_size: Size of the file in bytes
            created_at: Timestamp when the attachment was created
            updated_at: Timestamp when the attachment was last updated
        """
        super().__init__(id, created_at, updated_at or created_at)  # Default updated_at to created_at if not provided
        self.form_id = form_id
        self.file_path = file_path
        self.file_name = file_name
        self.file_type = file_type
        self.file_size = file_size
        
    def get_path(self) -> Path:
        """
        Get the file path as a Path object.
        
        Returns:
            Path object representing the file path
        """
        return Path(self.file_path)
        
    def get_extension(self) -> str:
        """
        Get the file extension.
        
        Returns:
            File extension (without dot)
        """
        return Path(self.file_name).suffix.lstrip('.')
        
    def is_image(self) -> bool:
        """
        Check if the attachment is an image.
        
        Returns:
            True if the file is an image, False otherwise
        """
        image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff', 'image/webp']
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'webp']
        
        return (
            self.file_type.lower() in image_types or
            self.get_extension().lower() in image_extensions
        )
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Attachment':
        """
        Create an Attachment instance from a dictionary.
        
        Args:
            data: Dictionary containing attachment data
            
        Returns:
            A new Attachment instance
        """
        # Convert string dates to datetime objects if needed
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
                
        return super(Attachment, cls).from_dict(data)
        
    def __str__(self) -> str:
        """
        Return a string representation of the Attachment.
        
        Returns:
            String representation
        """
        size_kb = self.file_size / 1024
        return f"{self.file_name} ({size_kb:.1f} KB)"

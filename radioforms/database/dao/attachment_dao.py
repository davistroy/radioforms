#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Attachment Data Access Object (DAO) for database operations related to file attachments.
"""

from typing import Any, Dict, List, Optional, Tuple, Union, overload
import os
import shutil
from pathlib import Path
from datetime import datetime
import mimetypes

from radioforms.database.dao.base_dao import BaseDAO, DAOException
from radioforms.database.models.attachment import Attachment
from radioforms.database.db_manager import DatabaseManager
from radioforms.database.dao.dao_cache_mixin import DAOCacheMixin


class AttachmentDAO(DAOCacheMixin[Attachment], BaseDAO[Attachment]):
    """
    Data Access Object for Attachment entities, providing database operations
    for creating, retrieving, updating, and deleting file attachments.
    """
    
    def __init__(self, db_manager: DatabaseManager, attachment_dir: Optional[str] = None):
        """
        Initialize the AttachmentDAO with a database manager and attachment directory.
        
        Args:
            db_manager: Database manager for database operations
            attachment_dir: Directory to store attachments (defaults to 'attachments' in current dir)
        """
        BaseDAO.__init__(self, db_manager)
        DAOCacheMixin.__init__(self)
        self.table_name = "attachments"
        self.pk_column = "id"
        
        # Set up attachment directory
        self.attachment_dir = Path(attachment_dir) if attachment_dir else Path("attachments")
        os.makedirs(self.attachment_dir, exist_ok=True)
        
    def _row_to_entity(self, row: Dict[str, Any]) -> Attachment:
        """
        Convert a database row to an Attachment entity.
        
        Args:
            row: Dictionary containing column names and values
            
        Returns:
            An Attachment entity
        """
        return Attachment(
            id=row.get('id'),
            form_id=row.get('form_id'),
            file_path=row.get('file_path', ''),
            file_name=row.get('file_name', ''),
            file_type=row.get('file_type', ''),
            file_size=row.get('file_size', 0),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
        
    def _entity_to_values(self, entity: Attachment) -> Dict[str, Any]:
        """
        Convert an Attachment entity to a dictionary of column values.
        
        Args:
            entity: The Attachment entity
            
        Returns:
            Dictionary containing column names and values
        """
        # Ensure both created_at and updated_at are set
        now = datetime.now()
        created_at = entity.created_at or now
        
        # For updates, always set updated_at to current time
        # For new entities, use the entity's updated_at or created_at
        if entity.id is not None:
            # This is an update operation, set updated_at to current time
            updated_at = now
            # Update the entity's updated_at value to maintain consistency
            entity.updated_at = now
        else:
            # This is a new entity, use existing updated_at or created_at
            updated_at = entity.updated_at or created_at
        
        values = {
            'form_id': entity.form_id,
            'file_path': entity.file_path,
            'file_name': entity.file_name,
            'file_type': entity.file_type,
            'file_size': entity.file_size,
            'created_at': created_at,
            'updated_at': updated_at
        }
        
        if entity.id is not None:
            values['id'] = entity.id
            
        return values
        
    def create_from_file(self, form_id: int, file_path: str, 
                        file_name: Optional[str] = None,
                        file_type: Optional[str] = None) -> Attachment:
        """
        Create an attachment by copying a file to the attachment directory.
        
        Args:
            form_id: ID of the form to attach to
            file_path: Path to the source file
            file_name: Name to use for the file (defaults to source file name)
            file_type: MIME type of the file (defaults to guessed from extension)
            
        Returns:
            The created Attachment entity
            
        Raises:
            DAOException: If the file cannot be copied or created
        """
        try:
            # Convert to Path for easier manipulation
            source_path = Path(file_path)
            
            # Set default file name if not provided
            if not file_name:
                file_name = source_path.name
                
            # Create a unique filename based on timestamp
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            unique_name = f"{timestamp}_{file_name}"
            
            # Create form-specific subdirectory
            form_dir = self.attachment_dir / str(form_id)
            os.makedirs(form_dir, exist_ok=True)
            
            # Destination path
            dest_path = form_dir / unique_name
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            
            # Get file size
            file_size = os.path.getsize(dest_path)
            
            # Determine file type if not provided
            if not file_type:
                file_type, _ = mimetypes.guess_type(file_name)
                if not file_type:
                    # Default to application/octet-stream if cannot determine
                    file_type = "application/octet-stream"
                    
            # Create attachment entity
            attachment = Attachment(
                form_id=form_id,
                file_path=str(dest_path),
                file_name=file_name,
                file_type=file_type,
                file_size=file_size
            )
            
            # Save to database
            attachment_id = self.create(attachment)
            attachment.id = attachment_id
            
            return attachment
            
        except (IOError, OSError) as e:
            raise DAOException(f"Failed to create attachment: {e}", e)
            
    def delete_with_file(self, attachment_id: int) -> bool:
        """
        Delete an attachment and its associated file.
        
        Args:
            attachment_id: ID of the attachment to delete
            
        Returns:
            True if the attachment was deleted, False otherwise
        """
        # Get the attachment first to get the file path
        attachment = self.find_by_id(attachment_id)
        if not attachment:
            return False
            
        # Delete the file if it exists
        try:
            if os.path.exists(attachment.file_path):
                os.remove(attachment.file_path)
        except (IOError, OSError):
            # Continue with database deletion even if file deletion fails
            pass
            
        # Delete from database
        return self.delete(attachment_id)
        
    def find_by_form(self, form_id: int) -> List[Attachment]:
        """
        Find all attachments for a specific form.
        
        Args:
            form_id: ID of the form
            
        Returns:
            List of attachments
        """
        query = f"SELECT * FROM {self.table_name} WHERE form_id = ?"
        cursor = self.db_manager.execute(query, (form_id,))
        
        return [self._row_to_entity(dict(row)) for row in cursor.fetchall()]
        
    def move_attachments(self, from_form_id: int, to_form_id: int) -> int:
        """
        Move attachments from one form to another.
        
        Args:
            from_form_id: Source form ID
            to_form_id: Destination form ID
            
        Returns:
            Number of attachments moved
        """
        # Get the attachments for the source form
        attachments = self.find_by_form(from_form_id)
        
        if not attachments:
            return 0
            
        # Create destination directory if it doesn't exist
        dest_dir = self.attachment_dir / str(to_form_id)
        os.makedirs(dest_dir, exist_ok=True)
        
        moved_count = 0
        
        for attachment in attachments:
            try:
                # Create a new filename in the destination directory
                source_path = Path(attachment.file_path)
                dest_path = dest_dir / source_path.name
                
                # Move the file if it exists
                if source_path.exists():
                    shutil.move(source_path, dest_path)
                    
                # Update the database record
                query = f"UPDATE {self.table_name} SET form_id = ?, file_path = ? WHERE id = ?"
                self.db_manager.execute(query, (to_form_id, str(dest_path), attachment.id))
                self.db_manager.commit()
                
                moved_count += 1
                
            except (IOError, OSError):
                # Continue with other attachments even if one fails
                continue
                
        return moved_count
        
    def get_attachment_info(self, attachment_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about an attachment.
        
        Args:
            attachment_id: ID of the attachment
            
        Returns:
            Dictionary with attachment details, or None if not found
        """
        attachment = self.find_by_id(attachment_id)
        if not attachment:
            return None
            
        info = attachment.to_dict()
        
        # Add additional information
        file_path = Path(attachment.file_path)
        info['exists'] = file_path.exists()
        
        if info['exists']:
            info['last_modified'] = datetime.fromtimestamp(
                os.path.getmtime(file_path)
            )
            
        info['extension'] = attachment.get_extension()
        info['is_image'] = attachment.is_image()
        
        return info
        
    def export_attachment(self, attachment_id: int, export_path: str) -> bool:
        """
        Export (copy) an attachment to a specified location.
        
        Args:
            attachment_id: ID of the attachment to export
            export_path: Path to export the file to
            
        Returns:
            True if the attachment was exported successfully, False otherwise
        """
        attachment = self.find_by_id(attachment_id)
        if not attachment:
            return False
            
        source_path = Path(attachment.file_path)
        if not source_path.exists():
            return False
            
        try:
            # If export_path is a directory, use the original filename
            if os.path.isdir(export_path):
                dest_path = Path(export_path) / attachment.file_name
            else:
                dest_path = Path(export_path)
                
            # Copy the file
            shutil.copy2(source_path, dest_path)
            return True
            
        except (IOError, OSError):
            return False

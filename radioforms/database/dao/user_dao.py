#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
User Data Access Object (DAO) for database operations related to users.
"""

from typing import Any, Dict, List, Optional, Tuple, Union, overload
from datetime import datetime

from radioforms.database.dao.base_dao import BaseDAO, DAOException
from radioforms.database.models.user import User
from radioforms.database.db_manager import DatabaseManager
from radioforms.database.dao.dao_cache_mixin import DAOCacheMixin


class UserDAO(DAOCacheMixin[User], BaseDAO[User]):
    """
    Data Access Object for User entities, providing database operations
    for creating, retrieving, updating, and deleting users.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the UserDAO with a database manager.
        
        Args:
            db_manager: Database manager for database operations
        """
        BaseDAO.__init__(self, db_manager)
        DAOCacheMixin.__init__(self)
        self.table_name = "users"
        self.pk_column = "id"
        
    def _row_to_entity(self, row: Dict[str, Any]) -> User:
        """
        Convert a database row to a User entity.
        
        Args:
            row: Dictionary containing column names and values
            
        Returns:
            A User entity
        """
        return User(
            id=row.get('id'),
            name=row.get('name', ''),
            call_sign=row.get('call_sign'),
            last_login=row.get('last_login'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
        
    def _entity_to_values(self, entity: User) -> Dict[str, Any]:
        """
        Convert a User entity to a dictionary of column values.
        
        Args:
            entity: The User entity
            
        Returns:
            Dictionary containing column names and values
        """
        values = {
            'name': entity.name,
            'call_sign': entity.call_sign,
            'last_login': entity.last_login,
            'created_at': entity.created_at,
            'updated_at': entity.updated_at
        }
        
        if entity.id is not None:
            values['id'] = entity.id
            
        return values
    
    @overload
    def find_by_name(self, name: str) -> List[User]:
        ...
    
    @overload
    def find_by_name(self, name: str, as_dict: bool = False) -> List[Dict[str, Any]]:
        ...
    
    def find_by_name(self, name: str, as_dict: bool = False) -> Union[List[User], List[Dict[str, Any]]]:
        """
        Find users by name (case-insensitive partial match).
        
        Args:
            name: Name or part of name to search for
            as_dict: When True, return dictionaries instead of entity objects
            
        Returns:
            List of matching users (as objects or dictionaries based on as_dict)
        """
        query = f"SELECT * FROM {self.table_name} WHERE name LIKE ?"
        cursor = self.db_manager.execute(query, (f"%{name}%",))
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
    
    @overload
    def find_by_call_sign(self, call_sign: str) -> Optional[User]:
        ...
    
    @overload
    def find_by_call_sign(self, call_sign: str, as_dict: bool = False) -> Optional[Dict[str, Any]]:
        ...
    
    def find_by_call_sign(self, call_sign: str, as_dict: bool = False) -> Optional[Union[User, Dict[str, Any]]]:
        """
        Find a user by exact call sign (case-insensitive).
        
        Args:
            call_sign: Call sign to search for
            as_dict: When True, return a dictionary instead of an entity object
            
        Returns:
            Matching user (as object or dictionary based on as_dict) or None if not found
        """
        query = f"SELECT * FROM {self.table_name} WHERE call_sign = ? COLLATE NOCASE"
        cursor = self.db_manager.execute(query, (call_sign,))
        row = cursor.fetchone()
        
        if row:
            row_dict = dict(row)
            return row_dict if as_dict else self._row_to_entity(row_dict)
        return None
        
    def update_last_login(self, user_id: int) -> bool:
        """
        Update the last login time for a user.
        
        Args:
            user_id: ID of the user to update
            
        Returns:
            True if the user was updated, False otherwise
        """
        now = datetime.now()
        update_data = {
            'last_login': now,
            'updated_at': now
        }
        
        # Now using the two-parameter form of update with explicit parameters
        return self.update(user_id, update_data)
    
    @overload
    def find_recent_users(self, limit: int = 10) -> List[User]:
        ...
    
    @overload
    def find_recent_users(self, limit: int = 10, as_dict: bool = False) -> List[Dict[str, Any]]:
        ...
    
    def find_recent_users(self, limit: int = 10, as_dict: bool = False) -> Union[List[User], List[Dict[str, Any]]]:
        """
        Find the most recently logged in users.
        
        Args:
            limit: Maximum number of users to return
            as_dict: When True, return dictionaries instead of entity objects
            
        Returns:
            List of users sorted by most recent login (as objects or dictionaries based on as_dict)
        """
        query = f"""
            SELECT * FROM {self.table_name} 
            WHERE last_login IS NOT NULL 
            ORDER BY last_login DESC 
            LIMIT ?
        """
        cursor = self.db_manager.execute(query, (limit,))
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
    
    @overload
    def create_user_if_not_exists(self, name: str, call_sign: Optional[str] = None) -> User:
        ...
    
    @overload
    def create_user_if_not_exists(self, name: str, call_sign: Optional[str] = None, as_dict: bool = False) -> Dict[str, Any]:
        ...
    
    def create_user_if_not_exists(self, name: str, call_sign: Optional[str] = None, 
                               as_dict: bool = False) -> Union[User, Dict[str, Any]]:
        """
        Create a new user if one with the same name/call sign doesn't exist.
        
        Args:
            name: User's name
            call_sign: User's call sign (optional)
            as_dict: When True, return a dictionary instead of an entity object
            
        Returns:
            The existing or newly created user (as object or dictionary based on as_dict)
        """
        # First, try to find by call sign if provided
        if call_sign:
            existing_user = self.find_by_call_sign(call_sign)
            if existing_user:
                if as_dict:
                    return self.to_dict(existing_user) if not isinstance(existing_user, dict) else existing_user
                return existing_user
                
        # Then, try to find by exact name match
        query = f"SELECT * FROM {self.table_name} WHERE name = ? COLLATE NOCASE"
        cursor = self.db_manager.execute(query, (name,))
        row = cursor.fetchone()
        
        if row:
            row_dict = dict(row)
            return row_dict if as_dict else self._row_to_entity(row_dict)
            
        # If no user found, create a new one
        user = User(name=name, call_sign=call_sign)
        user_id = self.create(user)
        user.id = user_id
        
        if as_dict:
            return self.to_dict(user)
        return user

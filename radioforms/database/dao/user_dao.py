#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
User Data Access Object (DAO) for database operations related to users.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
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
    
    def find_by_name(self, name: str, as_dict: bool = False) -> Union[List[User], List[Dict[str, Any]]]:
        """
        Find users by name (case-insensitive partial match).
        
        Args:
            name: Name or part of name to search for
            as_dict: When True, return dictionaries instead of entity objects
            
        Returns:
            List of matching users as either entity objects or dictionaries
            
        Examples:
            >>> users = user_dao.find_by_name("John")
            >>> user_dicts = user_dao.find_by_name("Smith", as_dict=True)
        """
        query = f"SELECT * FROM {self.table_name} WHERE name LIKE ?"
        cursor = self.db_manager.execute(query, (f"%{name}%",))
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def find_by_call_sign(self, call_sign: str, as_dict: bool = False) -> Optional[Union[User, Dict[str, Any]]]:
        """
        Find a user by exact call sign (case-insensitive).
        
        Args:
            call_sign: Call sign to search for
            as_dict: When True, return a dictionary instead of an entity object
            
        Returns:
            Matching user as either entity object or dictionary, or None if not found
            
        Examples:
            >>> user = user_dao.find_by_call_sign("W1AW")
            >>> user_dict = user_dao.find_by_call_sign("K5XYZ", as_dict=True)
        """
        query = f"SELECT * FROM {self.table_name} WHERE call_sign = ? COLLATE NOCASE"
        cursor = self.db_manager.execute(query, (call_sign,))
        row = cursor.fetchone()
        
        if row:
            row_dict = dict(row)
            return row_dict if as_dict else self._row_to_entity(row_dict)
        return None
        
    def set_last_login_time(self, user_id: int) -> bool:
        """
        Update the last login time for a user to the current time.
        
        Args:
            user_id: ID of the user to update
            
        Returns:
            True if the user was updated, False otherwise
            
        Example:
            >>> success = user_dao.set_last_login_time(5)
            >>> if success:
            >>>     print("User #5 login time updated")
        """
        now = datetime.now()
        update_data = {
            'last_login': now,
            'updated_at': now
        }
        
        return self.update(user_id, update_data)
    
    def find_recent(self, as_dict: bool = False, limit: int = 10) -> Union[List[User], List[Dict[str, Any]]]:
        """
        Find the most recently logged in users.
        
        Args:
            as_dict: When True, return dictionaries instead of entity objects
            limit: Maximum number of users to return
            
        Returns:
            List of users sorted by most recent login as either entity objects or dictionaries
            
        Examples:
            >>> recent_users = user_dao.find_recent()
            >>> recent_dicts = user_dao.find_recent(as_dict=True, limit=5)
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
    
    def find_or_create(self, name: str, call_sign: Optional[str] = None, 
                      as_dict: bool = False) -> Union[User, Dict[str, Any]]:
        """
        Find an existing user or create a new one if not found.
        
        Args:
            name: User's name
            call_sign: User's call sign (optional)
            as_dict: When True, return a dictionary instead of an entity object
            
        Returns:
            The existing or newly created user as either entity object or dictionary
            
        Examples:
            >>> user = user_dao.find_or_create("John Smith", "K5ABC")
            >>> user_dict = user_dao.find_or_create("Jane Doe", as_dict=True)
        """
        # First, try to find by call sign if provided
        if call_sign:
            existing_user = self.find_by_call_sign(call_sign)
            if existing_user:
                if as_dict:
                    if not isinstance(existing_user, dict):
                        return self._entity_to_values(existing_user)
                    return existing_user
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
            return self._entity_to_values(user)
        return user

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Incident Data Access Object (DAO) for database operations related to incidents.
"""

from typing import Any, Dict, List, Optional, Tuple
import datetime

from radioforms.database.dao.base_dao import BaseDAO, DAOException
from radioforms.database.models.incident import Incident
from radioforms.database.db_manager import DatabaseManager


class IncidentDAO(BaseDAO[Incident]):
    """
    Data Access Object for Incident entities, providing database operations
    for creating, retrieving, updating, and deleting incidents.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the IncidentDAO with a database manager.
        
        Args:
            db_manager: Database manager for database operations
        """
        super().__init__(db_manager)
        self.table_name = "incidents"
        self.pk_column = "id"
        
    def _row_to_entity(self, row: Dict[str, Any]) -> Incident:
        """
        Convert a database row to an Incident entity.
        
        Args:
            row: Dictionary containing column names and values
            
        Returns:
            An Incident entity
        """
        return Incident(
            id=row.get('id'),
            name=row.get('name', ''),
            description=row.get('description'),
            start_date=row.get('start_date'),
            end_date=row.get('end_date'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
        
    def _entity_to_values(self, entity: Incident) -> Dict[str, Any]:
        """
        Convert an Incident entity to a dictionary of column values.
        
        Args:
            entity: The Incident entity
            
        Returns:
            Dictionary containing column names and values
        """
        values = {
            'name': entity.name,
            'description': entity.description,
            'start_date': entity.start_date,
            'end_date': entity.end_date,
            'created_at': entity.created_at,
            'updated_at': entity.updated_at
        }
        
        if entity.id is not None:
            values['id'] = entity.id
            
        return values
        
    def find_by_name(self, name: str) -> List[Incident]:
        """
        Find incidents by name (case-insensitive partial match).
        
        Args:
            name: Name or part of name to search for
            
        Returns:
            List of matching incidents
        """
        query = f"SELECT * FROM {self.table_name} WHERE name LIKE ?"
        cursor = self.db_manager.execute(query, (f"%{name}%",))
        
        return [self._row_to_entity(dict(row)) for row in cursor.fetchall()]
        
    def find_active_incidents(self, order_by: str = "start_date DESC") -> List[Incident]:
        """
        Find all active incidents (no end date).
        
        Args:
            order_by: Column to order by with optional direction
            
        Returns:
            List of active incidents
        """
        query = f"SELECT * FROM {self.table_name} WHERE end_date IS NULL ORDER BY {order_by}"
        cursor = self.db_manager.execute(query)
        
        return [self._row_to_entity(dict(row)) for row in cursor.fetchall()]
        
    def find_closed_incidents(self, order_by: str = "end_date DESC") -> List[Incident]:
        """
        Find all closed incidents (with end date).
        
        Args:
            order_by: Column to order by with optional direction
            
        Returns:
            List of closed incidents
        """
        query = f"SELECT * FROM {self.table_name} WHERE end_date IS NOT NULL ORDER BY {order_by}"
        cursor = self.db_manager.execute(query)
        
        return [self._row_to_entity(dict(row)) for row in cursor.fetchall()]
        
    def find_in_date_range(self, start_date: datetime.datetime, 
                         end_date: datetime.datetime) -> List[Incident]:
        """
        Find incidents that overlap with the specified date range.
        
        Args:
            start_date: Start of the date range
            end_date: End of the date range
            
        Returns:
            List of incidents in the date range
        """
        query = f"""
            SELECT * FROM {self.table_name} 
            WHERE 
                (start_date <= ? AND (end_date IS NULL OR end_date >= ?))
            ORDER BY start_date DESC
        """
        cursor = self.db_manager.execute(query, (end_date, start_date))
        
        return [self._row_to_entity(dict(row)) for row in cursor.fetchall()]
        
    def close_incident(self, incident_id: int, end_date: Optional[datetime.datetime] = None) -> bool:
        """
        Close an incident by setting its end date.
        
        Args:
            incident_id: ID of the incident to close
            end_date: End date to set (defaults to current time)
            
        Returns:
            True if the incident was closed, False otherwise
        """
        now = datetime.datetime.now()
        end_date = end_date or now
        
        query = f"UPDATE {self.table_name} SET end_date = ?, updated_at = ? WHERE id = ?"
        cursor = self.db_manager.execute(query, (end_date, now, incident_id))
        self.db_manager.commit()
        
        return cursor.rowcount > 0
        
    def reopen_incident(self, incident_id: int) -> bool:
        """
        Reopen a closed incident by clearing its end date.
        
        Args:
            incident_id: ID of the incident to reopen
            
        Returns:
            True if the incident was reopened, False otherwise
        """
        now = datetime.datetime.now()
        
        query = f"UPDATE {self.table_name} SET end_date = NULL, updated_at = ? WHERE id = ?"
        cursor = self.db_manager.execute(query, (now, incident_id))
        self.db_manager.commit()
        
        return cursor.rowcount > 0
        
    def get_incident_stats(self) -> Dict[str, int]:
        """
        Get statistics about incidents.
        
        Returns:
            Dictionary with stats (total, active, closed)
        """
        stats = {}
        
        # Get total count
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        cursor = self.db_manager.execute(query)
        stats['total'] = cursor.fetchone()[0]
        
        # Get active count
        query = f"SELECT COUNT(*) FROM {self.table_name} WHERE end_date IS NULL"
        cursor = self.db_manager.execute(query)
        stats['active'] = cursor.fetchone()[0]
        
        # Get closed count
        query = f"SELECT COUNT(*) FROM {self.table_name} WHERE end_date IS NOT NULL"
        cursor = self.db_manager.execute(query)
        stats['closed'] = cursor.fetchone()[0]
        
        return stats

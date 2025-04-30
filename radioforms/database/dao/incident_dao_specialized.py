#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enhanced Incident DAO with specialized query methods.

This extends the IncidentDAO with optimized query methods for common operations
across the application.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union, overload

from radioforms.database.dao.incident_dao import IncidentDAO
from radioforms.database.models.incident import Incident
from radioforms.database.db_manager import DatabaseManager


class EnhancedIncidentDAO(IncidentDAO):
    """
    Enhanced Data Access Object for incident operations with specialized query methods.
    
    This class extends the base IncidentDAO with additional query methods that optimize
    common access patterns and provide more targeted data retrieval options.
    """
    
    def find_by_date_range(self, start_date: datetime, end_date: datetime, 
                         include_closed: bool = True, as_dict: bool = False) -> Union[List[Incident], List[Dict[str, Any]]]:
        """
        Find incidents that started within a specific date range.
        
        This specialized query efficiently retrieves incidents that started within the 
        specified date range, with an option to include or exclude closed incidents.
        
        Args:
            start_date: The beginning of the date range to search
            end_date: The end of the date range to search
            include_closed: When True, include incidents that have been closed
            as_dict: When True, return dictionaries instead of entity objects
            
        Returns:
            List of incidents (as objects or dictionaries based on as_dict parameter)
            
        Example:
            >>> # Find incidents from last week
            >>> week_ago = datetime.now() - timedelta(days=7)
            >>> incidents = incident_dao.find_by_date_range(week_ago, datetime.now())
        """
        query = """
        SELECT * FROM incidents 
        WHERE start_date >= ? AND start_date <= ?
        """
        
        params = [start_date, end_date]
        
        if not include_closed:
            query += " AND end_date IS NULL"
            
        query += " ORDER BY start_date DESC"
        
        cursor = self.db_manager.execute(query, params)
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def find_recently_active(self, days: int = 7, as_dict: bool = False) -> Union[List[Incident], List[Dict[str, Any]]]:
        """
        Find incidents that have been active within the specified number of days.
        
        This method finds incidents that were either created or updated within 
        the specified time period, providing a quick way to see recent activity.
        
        Args:
            days: Number of days to look back for activity
            as_dict: When True, return dictionaries instead of entity objects
            
        Returns:
            List of recently active incidents, sorted by most recent activity first
            
        Example:
            >>> # Get incidents with activity in the last 3 days
            >>> recent = incident_dao.find_recently_active(3)
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = """
        SELECT * FROM incidents
        WHERE created_at >= ? OR updated_at >= ?
        ORDER BY 
            CASE
                WHEN updated_at > created_at THEN updated_at
                ELSE created_at
            END DESC
        """
        
        params = [cutoff_date, cutoff_date]
        
        cursor = self.db_manager.execute(query, params)
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def search_incidents(self, 
                        name: Optional[str] = None,
                        description: Optional[str] = None,
                        active_only: bool = False,
                        start_date_from: Optional[datetime] = None,
                        start_date_to: Optional[datetime] = None,
                        order_by: str = "start_date DESC",
                        limit: int = 100,
                        as_dict: bool = False) -> Union[List[Incident], List[Dict[str, Any]]]:
        """
        Advanced search for incidents with multiple optional filter criteria.
        
        This method provides a flexible way to search for incidents based on
        various criteria, allowing for complex filtering with a single query.
        
        Args:
            name: Optional name pattern to search for (case-insensitive, substring match)
            description: Optional description text to search for
            active_only: When True, only return active (non-closed) incidents
            start_date_from: Optional start of date range filter
            start_date_to: Optional end of date range filter
            order_by: SQL ORDER BY clause for sorting results
            limit: Maximum number of results to return
            as_dict: When True, return dictionaries instead of entity objects
            
        Returns:
            List of matching incidents (as objects or dictionaries based on as_dict parameter)
            
        Example:
            >>> # Search for active fire incidents started in the last month
            >>> month_ago = datetime.now() - timedelta(days=30)
            >>> fires = incident_dao.search_incidents(
            ...     name="fire", 
            ...     active_only=True,
            ...     start_date_from=month_ago
            ... )
        """
        query_parts = ["SELECT * FROM incidents WHERE 1=1"]
        params = []
        
        # Add name filter
        if name:
            query_parts.append("AND name LIKE ?")
            params.append(f"%{name}%")
            
        # Add description filter
        if description:
            query_parts.append("AND description LIKE ?")
            params.append(f"%{description}%")
            
        # Add active-only filter
        if active_only:
            query_parts.append("AND end_date IS NULL")
            
        # Add date range filters
        if start_date_from:
            query_parts.append("AND start_date >= ?")
            params.append(start_date_from)
            
        if start_date_to:
            query_parts.append("AND start_date <= ?")
            params.append(start_date_to)
            
        # Add order by and limit
        query_parts.append(f"ORDER BY {order_by}")
        query_parts.append("LIMIT ?")
        params.append(limit)
        
        # Combine query parts
        query = " ".join(query_parts)
        
        # Execute query
        cursor = self.db_manager.execute(query, params)
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def get_incidents_with_form_counts(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get incidents with their associated form counts.
        
        This specialized query joins incidents with forms to provide a count of forms
        associated with each incident, useful for summary displays and dashboards.
        
        Args:
            active_only: When True, only include active (non-closed) incidents
            
        Returns:
            List of dictionaries containing incident data with an additional 'form_count' field
            
        Example:
            >>> incidents_with_counts = incident_dao.get_incidents_with_form_counts()
            >>> for inc in incidents_with_counts:
            >>>     print(f"Incident: {inc['name']} - Forms: {inc['form_count']}")
        """
        query = """
        SELECT 
            i.*, 
            COUNT(f.id) as form_count
        FROM 
            incidents i
        LEFT JOIN 
            forms f ON i.id = f.incident_id
        """
        
        if active_only:
            query += " WHERE i.end_date IS NULL"
            
        query += """
        GROUP BY 
            i.id
        ORDER BY 
            i.start_date DESC
        """
        
        cursor = self.db_manager.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_form_stats_by_incident(self, incident_id: int) -> Dict[str, int]:
        """
        Get statistics about forms associated with a specific incident.
        
        This method provides a summary of form statuses (draft, finalized, etc.)
        for a given incident, useful for dashboards and progress tracking.
        
        Args:
            incident_id: ID of the incident to get form statistics for
            
        Returns:
            Dictionary with form status counts, e.g., {'draft': 5, 'finalized': 3}
            
        Example:
            >>> stats = incident_dao.get_form_stats_by_incident(5)
            >>> print(f"Draft forms: {stats.get('draft', 0)}")
            >>> print(f"Finalized forms: {stats.get('finalized', 0)}")
        """
        query = """
        SELECT 
            status, 
            COUNT(*) as count
        FROM 
            forms
        WHERE 
            incident_id = ?
        GROUP BY 
            status
        """
        
        cursor = self.db_manager.execute(query, (incident_id,))
        
        # Initialize result with all possible statuses set to 0
        result = {status.lower(): 0 for status in ['draft', 'in_progress', 'finalized', 'archived']}
        
        # Update with actual counts
        for row in cursor.fetchall():
            status = row['status'].lower()
            result[status] = row['count']
            
        return result
    
    def find_incidents_by_form_type(self, form_type: str, as_dict: bool = False) -> Union[List[Incident], List[Dict[str, Any]]]:
        """
        Find incidents that have forms of a specific type.
        
        This specialized query retrieves incidents that are associated with at least
        one form of the specified type, useful for finding incidents related to
        specific operational areas.
        
        Args:
            form_type: The form type to search for (e.g., "ICS-213")
            as_dict: When True, return dictionaries instead of entity objects
            
        Returns:
            List of incidents that have at least one form of the specified type
            
        Example:
            >>> # Find incidents with resource request forms
            >>> incidents = incident_dao.find_incidents_by_form_type("ICS-213")
        """
        query = """
        SELECT DISTINCT 
            i.* 
        FROM 
            incidents i
        INNER JOIN 
            forms f ON i.id = f.incident_id
        WHERE 
            f.form_type = ?
        ORDER BY 
            i.start_date DESC
        """
        
        cursor = self.db_manager.execute(query, (form_type,))
        rows = cursor.fetchall()
        
        if as_dict:
            return [dict(row) for row in rows]
        return [self._row_to_entity(dict(row)) for row in rows]

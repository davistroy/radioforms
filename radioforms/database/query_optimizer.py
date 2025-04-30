#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Database query optimization utilities.

This module provides tools for analyzing and optimizing database queries,
including index recommendations, query rewriting suggestions, and
performance optimization strategies.
"""

import re
import sqlite3
import logging
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from pathlib import Path
import json

from radioforms.database.query_profiler import query_profiler
from radioforms.database.db_manager import DatabaseManager

# Configure logger
logger = logging.getLogger(__name__)


class QueryAnalyzer:
    """
    Utility for analyzing SQL queries and providing optimization recommendations.
    
    This class parses SQL queries to identify patterns and provide recommendations
    for query optimization, including index suggestions and query rewriting.
    """
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize the query analyzer.
        
        Args:
            db_manager: Optional database manager for schema analysis
        """
        self.db_manager = db_manager
        self.table_columns = {}  # Cache for table schema information
        self.existing_indices = {}  # Cache for existing index information
        
    def analyze_query(self, query: str, params: Any = None) -> Dict[str, Any]:
        """
        Analyze a SQL query and provide optimization recommendations.
        
        Args:
            query: SQL query string to analyze
            params: Optional query parameters
            
        Returns:
            Dictionary containing analysis results and recommendations
        """
        # Determine query type and basic structure
        query_type = self._get_query_type(query)
        
        # Base analysis structure
        analysis = {
            "query_type": query_type,
            "query": query,
            "params": params,
            "tables_referenced": [],
            "columns_referenced": [],
            "where_conditions": [],
            "joins": [],
            "order_by": [],
            "group_by": [],
            "issues": [],
            "recommendations": []
        }
        
        try:
            # Perform type-specific analysis
            if query_type == "select":
                self._analyze_select_query(query, analysis)
            elif query_type == "insert":
                self._analyze_insert_query(query, analysis)
            elif query_type == "update":
                self._analyze_update_query(query, analysis)
            elif query_type == "delete":
                self._analyze_delete_query(query, analysis)
                
            # General analysis and recommendations
            self._check_for_common_issues(query, analysis)
            self._generate_recommendations(analysis)
            
        except Exception as e:
            analysis["issues"].append(f"Error analyzing query: {str(e)}")
            logger.warning(f"Error analyzing query: {str(e)}", exc_info=True)
            
        return analysis
    
    def analyze_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Analyze the slowest queries from the profiler and provide optimization recommendations.
        
        Args:
            limit: Maximum number of slow queries to analyze
            
        Returns:
            List of dictionaries containing analysis results for each slow query
        """
        slow_queries = query_profiler.get_slow_queries(limit)
        results = []
        
        for query_info in slow_queries:
            query = query_info["query"]
            params = query_info["params"]
            execution_time = query_info["execution_time"]
            
            # Skip non-SQL queries (e.g., function calls)
            if query.startswith("Function:") or query.startswith("Transaction:"):
                continue
                
            # Analyze the query
            analysis = self.analyze_query(query, params)
            analysis["execution_time"] = execution_time
            results.append(analysis)
            
        return results
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get the schema information for a table.
        
        Args:
            table_name: Name of the table to get schema for
            
        Returns:
            List of column information dictionaries
        """
        if not self.db_manager:
            return []
            
        # Check cache first
        if table_name in self.table_columns:
            return self.table_columns[table_name]
            
        # Query the database for table schema
        try:
            query = f"PRAGMA table_info({table_name})"
            cursor = self.db_manager.execute(query)
            columns = [dict(row) for row in cursor.fetchall()]
            
            # Cache the result
            self.table_columns[table_name] = columns
            return columns
        except Exception as e:
            logger.warning(f"Error getting schema for table {table_name}: {str(e)}")
            return []
            
    def get_table_indices(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get the index information for a table.
        
        Args:
            table_name: Name of the table to get indices for
            
        Returns:
            List of index information dictionaries
        """
        if not self.db_manager:
            return []
            
        # Check cache first
        if table_name in self.existing_indices:
            return self.existing_indices[table_name]
            
        # Query the database for index information
        try:
            query = f"PRAGMA index_list({table_name})"
            cursor = self.db_manager.execute(query)
            indices = []
            
            for idx_info in cursor.fetchall():
                idx_info_dict = dict(idx_info)
                idx_name = idx_info_dict["name"]
                
                # Get detailed index info (columns)
                detail_query = f"PRAGMA index_info({idx_name})"
                detail_cursor = self.db_manager.execute(detail_query)
                columns = [dict(col)["name"] for col in detail_cursor.fetchall()]
                
                idx_info_dict["columns"] = columns
                indices.append(idx_info_dict)
                
            # Cache the result
            self.existing_indices[table_name] = indices
            return indices
        except Exception as e:
            logger.warning(f"Error getting indices for table {table_name}: {str(e)}")
            return []
    
    def generate_optimization_report(self) -> str:
        """
        Generate a comprehensive optimization report based on profiled queries.
        
        Returns:
            Formatted report string with optimization recommendations
        """
        # Get query statistics from profiler
        summary = query_profiler.get_summary()
        if summary["total_queries"] == 0:
            return "No queries have been profiled yet."
            
        # Analyze slow queries
        slow_query_analyses = self.analyze_slow_queries(20)
        
        # Collect index recommendations
        recommended_indices = {}
        for analysis in slow_query_analyses:
            for recommendation in analysis.get("recommendations", []):
                if recommendation.get("type") == "create_index":
                    table = recommendation.get("table")
                    columns = tuple(recommendation.get("columns", []))
                    
                    if table and columns:
                        if table not in recommended_indices:
                            recommended_indices[table] = {}
                            
                        if columns not in recommended_indices[table]:
                            recommended_indices[table][columns] = {
                                "count": 0,
                                "queries": [],
                                "estimated_impact": 0.0
                            }
                            
                        # Increment references to this index recommendation
                        recommended_indices[table][columns]["count"] += 1
                        
                        # Add query reference
                        query_ref = analysis.get("query", "")
                        if len(query_ref) > 100:
                            query_ref = query_ref[:97] + "..."
                            
                        if query_ref not in recommended_indices[table][columns]["queries"]:
                            recommended_indices[table][columns]["queries"].append(query_ref)
                            
                        # Add impact (based on execution time)
                        # Assume index could improve performance by 50% (conservative estimate)
                        exec_time = analysis.get("execution_time", 0)
                        estimated_impact = exec_time * 0.5
                        recommended_indices[table][columns]["estimated_impact"] += estimated_impact
        
        # Generate report
        report = []
        report.append("=====================================================")
        report.append("      DATABASE QUERY OPTIMIZATION REPORT        ")
        report.append("=====================================================")
        report.append("")
        
        # Overall statistics
        report.append("OVERALL QUERY PERFORMANCE:")
        report.append(f"Total Queries Analyzed: {summary['total_queries']}")
        report.append(f"Average Query Time:     {summary['avg_execution_time']:.4f}s")
        report.append(f"Number of Slow Queries: {summary['slow_query_count']}")
        report.append("")
        
        # Index recommendations
        report.append("RECOMMENDED INDICES:")
        if not recommended_indices:
            report.append("  No index recommendations based on current query patterns.")
        else:
            # Sort recommendations by estimated impact
            all_recommendations = []
            for table, indices in recommended_indices.items():
                for columns, data in indices.items():
                    all_recommendations.append({
                        "table": table,
                        "columns": columns,
                        "count": data["count"],
                        "estimated_impact": data["estimated_impact"],
                        "queries": data["queries"]
                    })
                    
            all_recommendations.sort(key=lambda x: x["estimated_impact"], reverse=True)
            
            for i, rec in enumerate(all_recommendations, 1):
                columns_str = ", ".join(rec["columns"])
                report.append(f"  {i}. Table: {rec['table']}")
                report.append(f"     Columns: {columns_str}")
                report.append(f"     Referenced in {rec['count']} queries")
                report.append(f"     Estimated Time Savings: {rec['estimated_impact']:.4f}s per execution")
                report.append(f"     Example Query: {rec['queries'][0] if rec['queries'] else 'N/A'}")
                report.append("")
                
                # Add a sample SQL command to create the index
                idx_name = f"idx_{rec['table']}_{'_'.join(rec['columns'])}"
                create_idx_sql = f"CREATE INDEX {idx_name} ON {rec['table']} ({columns_str});"
                report.append(f"     SQL: {create_idx_sql}")
                report.append("")
        
        # Query rewriting recommendations
        report.append("QUERY REWRITING RECOMMENDATIONS:")
        query_recommendations = set()
        for analysis in slow_query_analyses:
            for recommendation in analysis.get("recommendations", []):
                if recommendation.get("type") == "rewrite_query":
                    rec_text = recommendation.get("description", "")
                    if rec_text:
                        query_recommendations.add(rec_text)
                        
        if not query_recommendations:
            report.append("  No query rewriting recommendations based on current query patterns.")
        else:
            for i, rec in enumerate(sorted(query_recommendations), 1):
                report.append(f"  {i}. {rec}")
                
        # Schema optimization suggestions
        report.append("")
        report.append("SCHEMA OPTIMIZATION SUGGESTIONS:")
        tables_to_optimize = set(recommended_indices.keys())
        if not tables_to_optimize:
            report.append("  No schema optimizations recommended based on current query patterns.")
        else:
            for table in sorted(tables_to_optimize):
                report.append(f"  Table: {table}")
                
                # Get column information
                columns = self.get_table_schema(table)
                if columns:
                    primaryKey = None
                    non_indexed_columns = []
                    
                    for col in columns:
                        if col.get("pk") == 1:
                            primaryKey = col.get("name")
                        else:
                            # Check if column might need indexing
                            if "id" in col.get("name", "").lower() or col.get("name", "").endswith("_id"):
                                non_indexed_columns.append(col.get("name"))
                    
                    # Report primary key
                    if primaryKey:
                        report.append(f"    Primary Key: {primaryKey}")
                    else:
                        report.append(f"    Warning: No primary key defined")
                        
                    # Report potential foreign keys that might need indices
                    if non_indexed_columns:
                        report.append(f"    Potential Foreign Keys to Consider Indexing:")
                        for col in non_indexed_columns:
                            report.append(f"      - {col}")
                            
                report.append("")
                
        return "\n".join(report)
    
    def _get_query_type(self, query: str) -> str:
        """
        Determine the type of a query based on its SQL.
        
        Args:
            query: SQL query string
            
        Returns:
            Query type string (e.g., "select", "insert")
        """
        query = query.strip().lower()
        if query.startswith("select"):
            return "select"
        elif query.startswith("insert"):
            return "insert"
        elif query.startswith("update"):
            return "update"
        elif query.startswith("delete"):
            return "delete"
        elif query.startswith("create"):
            return "create"
        elif query.startswith("alter"):
            return "alter"
        elif query.startswith("drop"):
            return "drop"
        else:
            return "other"
    
    def _analyze_select_query(self, query: str, analysis: Dict[str, Any]):
        """
        Analyze a SELECT query and update the analysis dictionary.
        
        Args:
            query: SQL query string
            analysis: Analysis dictionary to update
        """
        # Extract referenced tables
        from_clause_match = re.search(r'\bFROM\s+(.+?)(?:\s+WHERE|\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|\s*$)', 
                                   query, re.IGNORECASE | re.DOTALL)
        if from_clause_match:
            from_clause = from_clause_match.group(1).strip()
            tables = self._extract_tables_from_clause(from_clause)
            analysis["tables_referenced"] = tables
            
        # Extract columns
        columns_match = re.search(r'SELECT\s+(.+?)\s+FROM', query, re.IGNORECASE | re.DOTALL)
        if columns_match:
            columns_clause = columns_match.group(1).strip()
            if columns_clause != '*':
                columns = self._extract_columns(columns_clause)
                analysis["columns_referenced"] = columns
            else:
                analysis["columns_referenced"] = ["*"]
                
        # Extract WHERE conditions
        where_match = re.search(r'\bWHERE\s+(.+?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|\s*$)', 
                              query, re.IGNORECASE | re.DOTALL)
        if where_match:
            where_clause = where_match.group(1).strip()
            conditions = self._extract_conditions(where_clause)
            analysis["where_conditions"] = conditions
            
        # Extract JOIN conditions
        join_pattern = r'\b(INNER|LEFT|RIGHT|OUTER|CROSS)?\s*JOIN\s+([^\s]+)\s+ON\s+(.+?)(?:\s+(?:INNER|LEFT|RIGHT|OUTER|CROSS)?\s*JOIN|\s+WHERE|\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|\s*$)'
        for match in re.finditer(join_pattern, query, re.IGNORECASE | re.DOTALL):
            join_type = match.group(1) or "INNER"
            join_table = match.group(2).strip()
            join_condition = match.group(3).strip()
            
            analysis["joins"].append({
                "type": join_type.upper(),
                "table": join_table,
                "condition": join_condition
            })
            
            # Add joined table to tables_referenced if not already there
            if join_table not in analysis["tables_referenced"]:
                analysis["tables_referenced"].append(join_table)
                
        # Extract ORDER BY
        order_match = re.search(r'\bORDER\s+BY\s+(.+?)(?:\s+LIMIT|\s*$)', 
                              query, re.IGNORECASE | re.DOTALL)
        if order_match:
            order_clause = order_match.group(1).strip()
            order_parts = order_clause.split(',')
            for part in order_parts:
                part = part.strip()
                if part:
                    direction = "ASC"
                    if " DESC" in part.upper():
                        direction = "DESC"
                        part = part.replace(" DESC", "").replace(" desc", "").strip()
                    elif " ASC" in part.upper():
                        part = part.replace(" ASC", "").replace(" asc", "").strip()
                        
                    analysis["order_by"].append({
                        "column": part,
                        "direction": direction
                    })
                    
        # Extract GROUP BY
        group_match = re.search(r'\bGROUP\s+BY\s+(.+?)(?:\s+HAVING|\s+ORDER\s+BY|\s+LIMIT|\s*$)', 
                              query, re.IGNORECASE | re.DOTALL)
        if group_match:
            group_clause = group_match.group(1).strip()
            group_columns = [col.strip() for col in group_clause.split(',')]
            analysis["group_by"] = group_columns
            
    def _analyze_insert_query(self, query: str, analysis: Dict[str, Any]):
        """
        Analyze an INSERT query and update the analysis dictionary.
        
        Args:
            query: SQL query string
            analysis: Analysis dictionary to update
        """
        # Extract target table
        table_match = re.search(r'INSERT\s+INTO\s+([^\s(]+)', query, re.IGNORECASE)
        if table_match:
            table = table_match.group(1).strip()
            analysis["tables_referenced"] = [table]
            
        # Extract columns
        columns_match = re.search(r'INSERT\s+INTO\s+[^\s(]+\s*\(([^)]+)\)', query, re.IGNORECASE)
        if columns_match:
            columns_str = columns_match.group(1).strip()
            columns = [col.strip() for col in columns_str.split(',')]
            analysis["columns_referenced"] = columns
            
    def _analyze_update_query(self, query: str, analysis: Dict[str, Any]):
        """
        Analyze an UPDATE query and update the analysis dictionary.
        
        Args:
            query: SQL query string
            analysis: Analysis dictionary to update
        """
        # Extract target table
        table_match = re.search(r'UPDATE\s+([^\s]+)', query, re.IGNORECASE)
        if table_match:
            table = table_match.group(1).strip()
            analysis["tables_referenced"] = [table]
            
        # Extract SET columns
        set_match = re.search(r'SET\s+(.+?)(?:\s+WHERE|\s*$)', query, re.IGNORECASE | re.DOTALL)
        if set_match:
            set_clause = set_match.group(1).strip()
            sets = set_clause.split(',')
            columns = []
            
            for item in sets:
                col_match = re.search(r'([^\s=]+)\s*=', item.strip())
                if col_match:
                    columns.append(col_match.group(1).strip())
                    
            analysis["columns_referenced"] = columns
            
        # Extract WHERE conditions
        where_match = re.search(r'\bWHERE\s+(.+?)(?:\s*$)', query, re.IGNORECASE | re.DOTALL)
        if where_match:
            where_clause = where_match.group(1).strip()
            conditions = self._extract_conditions(where_clause)
            analysis["where_conditions"] = conditions
            
    def _analyze_delete_query(self, query: str, analysis: Dict[str, Any]):
        """
        Analyze a DELETE query and update the analysis dictionary.
        
        Args:
            query: SQL query string
            analysis: Analysis dictionary to update
        """
        # Extract target table
        table_match = re.search(r'DELETE\s+FROM\s+([^\s]+)', query, re.IGNORECASE)
        if table_match:
            table = table_match.group(1).strip()
            analysis["tables_referenced"] = [table]
            
        # Extract WHERE conditions
        where_match = re.search(r'\bWHERE\s+(.+?)(?:\s*$)', query, re.IGNORECASE | re.DOTALL)
        if where_match:
            where_clause = where_match.group(1).strip()
            conditions = self._extract_conditions(where_clause)
            analysis["where_conditions"] = conditions
            
    def _extract_tables_from_clause(self, from_clause: str) -> List[str]:
        """
        Extract table names from a FROM clause.
        
        Args:
            from_clause: SQL FROM clause
            
        Returns:
            List of table names
        """
        # Handle simple comma-separated tables
        if ',' in from_clause and 'join' not in from_clause.lower():
            tables = []
            for part in from_clause.split(','):
                # Extract table name, handling aliases
                table_parts = part.strip().split()
                if table_parts:
                    tables.append(table_parts[0].strip())
            return tables
        else:
            # Extract the first table (before any JOINs)
            table_parts = from_clause.split()
            if table_parts:
                return [table_parts[0].strip()]
            return []
            
    def _extract_columns(self, columns_clause: str) -> List[str]:
        """
        Extract column names from a SELECT column list.
        
        Args:
            columns_clause: Comma-separated column list
            
        Returns:
            List of column names or expressions
        """
        columns = []
        
        # Split by commas, but handle function calls with commas inside parentheses
        parts = []
        current_part = ""
        paren_level = 0
        
        for char in columns_clause:
            if char == '(':
                paren_level += 1
                current_part += char
            elif char == ')':
                paren_level -= 1
                current_part += char
            elif char == ',' and paren_level == 0:
                parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += char
                
        if current_part:
            parts.append(current_part.strip())
            
        # Process each part to extract column names
        for part in parts:
            # Handle column aliases
            if ' AS ' in part.upper():
                column_parts = part.split(' AS ', 1)
                column = column_parts[0].strip()
            else:
                # Check for space-based aliases
                column_parts = part.split()
                if len(column_parts) > 1 and column_parts[0].lower() not in ('distinct', 'all'):
                    column = column_parts[0].strip()
                else:
                    column = part.strip()
                    
            columns.append(column)
            
        return columns
        
    def _extract_conditions(self, where_clause: str) -> List[Dict[str, str]]:
        """
        Extract conditions from a WHERE clause.
        
        Args:
            where_clause: SQL WHERE clause
            
        Returns:
            List of condition dictionaries
        """
        # This is a simplified approach - a full SQL parser would be more accurate
        # but also much more complex
        
        # Split by AND/OR, but handle parentheses
        conditions = []
        current_condition = ""
        paren_level = 0
        i = 0
        
        while i < len(where_clause):
            if where_clause[i:i+5].upper() == ' AND ' and paren_level == 0:
                if current_condition:
                    conditions.append({
                        "condition": current_condition.strip(),
                        "operator": "AND"
                    })
                current_condition = ""
                i += 5
            elif where_clause[i:i+4].upper() == ' OR ' and paren_level == 0:
                if current_condition:
                    conditions.append({
                        "condition": current_condition.strip(),
                        "operator": "OR"
                    })
                current_condition = ""
                i += 4
            elif where_clause[i] == '(':
                paren_level += 1
                current_condition += where_clause[i]
                i += 1
            elif where_clause[i] == ')':
                paren_level -= 1
                current_condition += where_clause[i]
                i += 1
            else:
                current_condition += where_clause[i]
                i += 1
                
        if current_condition:
            conditions.append({
                "condition": current_condition.strip(),
                "operator": None  # Last condition has no following operator
            })
            
        # Extract column names from conditions
        for condition in conditions:
            # Try to extract the column name from the condition
            # This is a simplified approach that works for common cases
            cond = condition["condition"]
            
            # Handle simple equality, inequality, and LIKE conditions
            col_match = re.search(r'([^\s()]+)\s*(?:=|!=|<>|>|<|>=|<=|LIKE|IN)\s', cond, re.IGNORECASE)
            if col_match:
                condition["column"] = col_match.group(1).strip()
                
        return conditions
        
    def _check_for_common_issues(self, query: str, analysis: Dict[str, Any]):
        """
        Check for common performance issues in the query.
        
        Args:
            query: SQL query string
            analysis: Analysis dictionary to update
        """
        query_lower = query.lower()
        
        # Check for SELECT *
        if analysis["query_type"] == "select" and "*" in analysis["columns_referenced"]:
            analysis["issues"].append({
                "type": "select_all",
                "description": "Using SELECT * can be inefficient. Consider selecting only needed columns."
            })
            
        # Check for missing WHERE clause in SELECT
        if (analysis["query_type"] == "select" and 
            not analysis["where_conditions"] and 
            not re.search(r'\bWHERE\b', query_lower)):
            analysis["issues"].append({
                "type": "missing_where",
                "description": "SELECT without WHERE clause might return too many rows."
            })
            
        # Check for LIKE with leading wildcard
        if "LIKE" in query.upper() and re.search(r"LIKE\s*['%]%", query_lower):
            analysis["issues"].append({
                "type": "leading_wildcard",
                "description": "LIKE with leading wildcard (%...) prevents index usage."
            })
            
        # Check for functions in WHERE conditions
        if analysis["where_conditions"]:
            for condition in analysis["where_conditions"]:
                cond = condition.get("condition", "").lower()
                if (
                    ("(" in cond and ")" in cond) and 
                    any(func in cond for func in ["substr(", "lower(", "upper(", "trim(", "date(", "strftime("])
                ):
                    analysis["issues"].append({
                        "type": "function_in_where",
                        "description": f"Function in WHERE condition prevents index usage: {condition['condition']}"
                    })
                    
        # Check for complex JOINs without proper indices
        if len(analysis["joins"]) > 2:
            analysis["issues"].append({
                "type": "complex_joins",
                "description": f"Query contains {len(analysis['joins'])} JOINs, which might be inefficient without proper indices."
            })
            
        # Check for ORDER BY on non-indexed columns
        if analysis["order_by"] and analysis["tables_referenced"]:
            for order_item in analysis["order_by"]:
                column = order_item["column"]
                
                # Check if any table_referenced has an index on this column
                # This is a simplified check - a more accurate one would consider table aliases
                is_likely_indexed = False
                
                for table in analysis["tables_referenced"]:
                    # Get indices for this table
                    indices = self.get_table_indices(table)
                    
                    for idx in indices:
                        if column in idx.get("columns", []):
                            is_likely_indexed = True
                            break
                            
                    if is_likely_indexed:
                        break
                        
                if not is_likely_indexed:
                    analysis["issues"].append({
                        "type": "unindexed_order_by",
                        "description": f"ORDER BY on potentially non-indexed column: {column}"
                    })
                    
    def _generate_recommendations(self, analysis: Dict[str, Any]):
        """
        Generate optimization recommendations based on the analysis.
        
        Args:
            analysis: Analysis dictionary to update with recommendations
        """
        # Generate index recommendations
        if analysis["query_type"] in ("select", "update", "delete"):
            self._recommend_indices(analysis)
            
        # Generate query rewriting recommendations
        self._recommend_query_rewrites(analysis)
        
        # Generate schema optimization recommendations
        if analysis["tables_referenced"]:
            self._recommend_schema_optimizations(analysis)
            
    def _recommend_indices(self, analysis: Dict[str, Any]):
        """
        Generate index recommendations based on query analysis.
        
        Args:
            analysis: Analysis dictionary to update with recommendations
        """
        # Check WHERE conditions for potential indices
        for condition in analysis["where_conditions"]:
            if "column" in condition:
                column = condition["column"]
                
                # Skip conditions with functions
                if "(" in column or ")" in column:
                    continue
                    
                # Determine table for this column
                table = self._guess_table_for_column(column, analysis["tables_referenced"])
                if not table:
                    continue
                    
                # Check if an index already exists
                indices = self.get_table_indices(table)
                already_indexed = False
                
                for idx in indices:
                    if column in idx.get("columns", []):
                        already_indexed = True
                        break
                        
                if not already_indexed:
                    analysis["recommendations"].append({
                        "type": "create_index",
                        "table": table,
                        "columns": [column],
                        "description": f"Create an index on {table}.{column} to optimize filtering."
                    })
                    
        # Check for JOIN conditions
        for join in analysis["joins"]:
            condition = join.get("condition", "")
            
            # Extract the columns from the join condition (simplified approach)
            match = re.search(r'(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)', condition)
            if match:
                table1, col1, table2, col2 = match.groups()
                
                # Check if indices exist for these columns
                indices1 = self.get_table_indices(table1)
                indices2 = self.get_table_indices(table2)
                
                indexed1 = any(col1 in idx.get("columns", []) for idx in indices1)
                indexed2 = any(col2 in idx.get("columns", []) for idx in indices2)
                
                # Recommend indices for join columns if missing
                if not indexed1:
                    analysis["recommendations"].append({
                        "type": "create_index",
                        "table": table1,
                        "columns": [col1],
                        "description": f"Create an index on {table1}.{col1} to optimize JOIN performance."
                    })
                    
                if not indexed2:
                    analysis["recommendations"].append({
                        "type": "create_index",
                        "table": table2,
                        "columns": [col2],
                        "description": f"Create an index on {table2}.{col2} to optimize JOIN performance."
                    })
                    
        # Check for ORDER BY columns
        if analysis["order_by"]:
            for order_item in analysis["order_by"]:
                column = order_item["column"]
                
                # Skip if column contains a function
                if "(" in column or ")" in column:
                    continue
                    
                # Determine table for this column
                table = self._guess_table_for_column(column, analysis["tables_referenced"])
                if not table:
                    continue
                    
                # Check if an index already exists
                indices = self.get_table_indices(table)
                already_indexed = False
                
                for idx in indices:
                    if column in idx.get("columns", []):
                        already_indexed = True
                        break
                        
                if not already_indexed:
                    analysis["recommendations"].append({
                        "type": "create_index",
                        "table": table,
                        "columns": [column],
                        "description": f"Create an index on {table}.{column} to optimize ORDER BY."
                    })
                    
        # Check for GROUP BY columns
        if analysis["group_by"]:
            for column in analysis["group_by"]:
                # Skip if column contains a function
                if "(" in column or ")" in column:
                    continue
                    
                # Determine table for this column
                table = self._guess_table_for_column(column, analysis["tables_referenced"])
                if not table:
                    continue
                    
                # Check if an index already exists
                indices = self.get_table_indices(table)
                already_indexed = False
                
                for idx in indices:
                    if column in idx.get("columns", []):
                        already_indexed = True
                        break
                        
                if not already_indexed:
                    analysis["recommendations"].append({
                        "type": "create_index",
                        "table": table,
                        "columns": [column],
                        "description": f"Create an index on {table}.{column} to optimize GROUP BY."
                    })
    
    def _recommend_query_rewrites(self, analysis: Dict[str, Any]):
        """
        Generate query rewriting recommendations based on analysis.
        
        Args:
            analysis: Analysis dictionary to update with recommendations
        """
        # Check for SELECT *
        if analysis["query_type"] == "select" and "*" in analysis["columns_referenced"]:
            analysis["recommendations"].append({
                "type": "rewrite_query",
                "description": "Replace SELECT * with explicit column names to improve performance."
            })
            
        # Check for LIKE with leading wildcard
        for condition in analysis["where_conditions"]:
            cond = condition.get("condition", "").upper()
            if "LIKE" in cond and "%'" in cond:
                analysis["recommendations"].append({
                    "type": "rewrite_query",
                    "description": "Avoid LIKE with leading wildcard (%...) as it prevents efficient index usage."
                })
                break
                
        # Check for functions in WHERE conditions
        for condition in analysis["where_conditions"]:
            cond = condition.get("condition", "").lower()
            if (
                ("(" in cond and ")" in cond) and 
                any(func in cond for func in ["substr(", "lower(", "upper(", "trim(", "date(", "strftime("])
            ):
                analysis["recommendations"].append({
                    "type": "rewrite_query",
                    "description": "Move functions from WHERE conditions to avoid preventing index usage."
                })
                break
                
        # Check for unnecessary DISTINCT
        if (
            analysis["query_type"] == "select" and 
            any("distinct" in col.lower() for col in analysis["columns_referenced"])
        ):
            analysis["recommendations"].append({
                "type": "rewrite_query",
                "description": "Consider whether DISTINCT is necessary, as it can impact performance."
            })
            
        # Check for complex JOINs
        if len(analysis["joins"]) > 2:
            analysis["recommendations"].append({
                "type": "rewrite_query",
                "description": f"Consider breaking down the query with {len(analysis['joins'])} JOINs into smaller queries."
            })
            
        # Check for LIMIT without ORDER BY
        if "LIMIT" in analysis["query"].upper() and not analysis["order_by"]:
            analysis["recommendations"].append({
                "type": "rewrite_query",
                "description": "Add an ORDER BY clause when using LIMIT to ensure consistent results."
            })
            
    def _recommend_schema_optimizations(self, analysis: Dict[str, Any]):
        """
        Generate schema optimization recommendations based on analysis.
        
        Args:
            analysis: Analysis dictionary to update with recommendations
        """
        for table in analysis["tables_referenced"]:
            # Get column information
            columns = self.get_table_schema(table)
            
            # Check for foreign keys that might need indices
            for col in columns:
                col_name = col.get("name", "")
                if (
                    col_name.endswith("_id") or 
                    (col_name != "id" and "id" in col_name.lower())
                ):
                    # Check if already indexed
                    indices = self.get_table_indices(table)
                    already_indexed = False
                    
                    for idx in indices:
                        if col_name in idx.get("columns", []):
                            already_indexed = True
                            break
                            
                    if not already_indexed:
                        analysis["recommendations"].append({
                            "type": "schema_optimization",
                            "table": table,
                            "column": col_name,
                            "description": f"Consider adding an index on potential foreign key: {table}.{col_name}"
                        })
                        
    def _guess_table_for_column(self, column: str, tables: List[str]) -> Optional[str]:
        """
        Guess which table a column belongs to.
        
        Args:
            column: Column name or expression
            tables: List of tables in the query
            
        Returns:
            Table name, or None if can't determine
        """
        # Check if column already has a table prefix
        if "." in column:
            parts = column.split(".", 1)
            return parts[0]
            
        # Try to find the column in each table's schema
        for table in tables:
            columns = self.get_table_schema(table)
            for col in columns:
                if col.get("name") == column:
                    return table
                    
        # If we can't determine, just use the first table as a guess
        if tables:
            return tables[0]
            
        return None


class QueryOptimizer:
    """
    High-level utility for optimizing database queries.
    
    This class serves as an entry point for the query optimization functionality,
    providing methods to profile, analyze, and optimize queries.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the query optimizer.
        
        Args:
            db_manager: Database manager for accessing the database
        """
        self.db_manager = db_manager
        self.analyzer = QueryAnalyzer(db_manager)
        self.profiler = query_profiler
        
    def enable_profiling(self, log_all: bool = False, slow_threshold: float = 0.1):
        """
        Enable query profiling for performance monitoring.
        
        Args:
            log_all: Whether to log all queries or only slow ones
            slow_threshold: Threshold in seconds for slow query classification
        """
        self.profiler.enable(log_all, slow_threshold)
        
    def disable_profiling(self):
        """Disable query profiling."""
        self.profiler.disable()
        
    def reset_profiling_stats(self):
        """Reset profiling statistics."""
        self.profiler.reset_stats()
        
    def instrument_db_manager(self):
        """
        Instrument the database manager to profile all queries.
        
        This method monkey-patches the database manager's execute and
        executemany methods to automatically profile all queries.
        """
        if hasattr(self.db_manager, 'connection'):
            self.profiler.instrument_connection(self.db_manager.connection)
        elif hasattr(self.db_manager, '_local') and hasattr(self.db_manager._local, 'connection'):
            self.profiler.instrument_connection(self.db_manager._local.connection)
            
    def generate_optimization_report(self) -> str:
        """
        Generate a comprehensive optimization report.
        
        Returns:
            Formatted report string with optimization recommendations
        """
        return self.analyzer.generate_optimization_report()
        
    def get_profile_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the query profiling statistics.
        
        Returns:
            Dictionary containing query profiling summary
        """
        return self.profiler.get_summary()
        
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the slowest queries recorded.
        
        Args:
            limit: Maximum number of slow queries to return
            
        Returns:
            List of dictionaries containing slow query details
        """
        return self.profiler.get_slow_queries(limit)
        
    def analyze_query(self, query: str, params: Any = None) -> Dict[str, Any]:
        """
        Analyze a SQL query and provide optimization recommendations.
        
        Args:
            query: SQL query string to analyze
            params: Optional query parameters
            
        Returns:
            Dictionary containing analysis results and recommendations
        """
        return self.analyzer.analyze_query(query, params)
        
    def create_recommended_indices(self, confirm: bool = False) -> int:
        """
        Create recommended indices based on query analysis.
        
        Args:
            confirm: Whether to execute the CREATE INDEX statements
            
        Returns:
            Number of indices created
        """
        # Analyze slow queries
        analyses = self.analyzer.analyze_slow_queries(20)
        
        # Collect index recommendations
        recommended_indices = {}
        for analysis in analyses:
            for recommendation in analysis.get("recommendations", []):
                if recommendation.get("type") == "create_index":
                    table = recommendation.get("table")
                    columns = tuple(recommendation.get("columns", []))
                    
                    if table and columns:
                        if table not in recommended_indices:
                            recommended_indices[table] = set()
                            
                        recommended_indices[table].add(columns)
                        
        # Create indices if confirmed
        if confirm:
            created_count = 0
            
            for table, columns_set in recommended_indices.items():
                for columns in columns_set:
                    # Generate index name
                    idx_name = f"idx_{table}_{'_'.join(columns)}"
                    columns_str = ", ".join(columns)
                    
                    # Create the index
                    query = f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({columns_str})"
                    try:
                        self.db_manager.execute(query)
                        self.db_manager.commit()
                        created_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to create index {idx_name}: {str(e)}")
                        
            return created_count
        else:
            # Just return the count of recommended indices
            return sum(len(columns_set) for columns_set in recommended_indices.values())


# Convenience function to get a query optimizer instance
def get_query_optimizer(db_manager: DatabaseManager) -> QueryOptimizer:
    """
    Get a query optimizer instance.
    
    Args:
        db_manager: Database manager instance
        
    Returns:
        QueryOptimizer instance
    """
    return QueryOptimizer(db_manager)

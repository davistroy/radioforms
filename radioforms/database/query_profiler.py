#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Query profiling utilities for performance optimization.

This module provides tools for measuring and analyzing database query performance,
helping to identify and optimize slow or inefficient queries.
"""

import time
import logging
import functools
import sqlite3
import traceback
from typing import Any, Dict, List, Optional, Callable, Union, Tuple
from contextlib import contextmanager
import threading
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)


class QueryProfilerStats:
    """
    Class for storing query profiling statistics.
    
    This class maintains cumulative statistics about query execution,
    including execution time, query counts, and performance metrics.
    """
    
    def __init__(self):
        """Initialize query profiler statistics."""
        self.reset()
        
    def reset(self):
        """Reset all statistics to initial values."""
        self.total_queries = 0
        self.total_execution_time = 0.0
        self.min_execution_time = float('inf')
        self.max_execution_time = 0.0
        self.avg_execution_time = 0.0
        self.query_types = {}  # Type -> count
        self.slow_queries = []  # List of (query, params, time, timestamp)
        self.query_history = []  # List of (query, params, time, timestamp)
        self._lock = threading.Lock()  # Thread safety for stat updates
        
    def record_query(self, query: str, params: Any, execution_time: float, 
                   query_type: str = "unknown"):
        """
        Record statistics for a single query execution.
        
        Args:
            query: The SQL query string
            params: Query parameters
            execution_time: Query execution time in seconds
            query_type: Optional query classification (e.g., "select", "insert")
        """
        with self._lock:
            # Update counters
            self.total_queries += 1
            self.total_execution_time += execution_time
            self.min_execution_time = min(self.min_execution_time, execution_time)
            self.max_execution_time = max(self.max_execution_time, execution_time)
            self.avg_execution_time = self.total_execution_time / self.total_queries
            
            # Update query type stats
            self.query_types[query_type] = self.query_types.get(query_type, 0) + 1
            
            # Add to query history
            timestamp = datetime.now()
            query_info = (query, params, execution_time, timestamp)
            self.query_history.append(query_info)
            
            # Track slow queries (over 100ms)
            if execution_time > 0.1:
                self.slow_queries.append(query_info)
                # Keep only the 100 slowest queries
                self.slow_queries.sort(key=lambda x: x[2], reverse=True)
                if len(self.slow_queries) > 100:
                    self.slow_queries.pop()
            
            # Keep query history manageable
            if len(self.query_history) > 1000:
                self.query_history = self.query_history[-1000:]
                
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the collected query statistics.
        
        Returns:
            Dictionary containing query profiling summary
        """
        with self._lock:
            return {
                "total_queries": self.total_queries,
                "total_execution_time": self.total_execution_time,
                "avg_execution_time": self.avg_execution_time,
                "min_execution_time": self.min_execution_time if self.total_queries > 0 else 0,
                "max_execution_time": self.max_execution_time,
                "query_types": dict(self.query_types),
                "slow_query_count": len(self.slow_queries)
            }
            
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the slowest queries recorded.
        
        Args:
            limit: Maximum number of slow queries to return
            
        Returns:
            List of dictionaries containing slow query details
        """
        with self._lock:
            result = []
            for query, params, execution_time, timestamp in self.slow_queries[:limit]:
                result.append({
                    "query": query,
                    "params": str(params),
                    "execution_time": execution_time,
                    "timestamp": timestamp
                })
            return result
            
    def get_type_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """
        Get a breakdown of query statistics by query type.
        
        Returns:
            Dictionary mapping query types to their statistics
        """
        with self._lock:
            result = {}
            for query_type, count in self.query_types.items():
                # Filter query history for this type
                type_queries = [
                    q for q in self.query_history 
                    if self._get_query_type(q[0]) == query_type
                ]
                
                # Calculate type-specific stats
                if type_queries:
                    type_times = [q[2] for q in type_queries]
                    result[query_type] = {
                        "count": count,
                        "avg_time": sum(type_times) / len(type_times),
                        "max_time": max(type_times),
                        "total_time": sum(type_times)
                    }
                else:
                    result[query_type] = {
                        "count": count,
                        "avg_time": 0,
                        "max_time": 0,
                        "total_time": 0
                    }
                    
            return result
            
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
        elif query.startswith("pragma"):
            return "pragma"
        else:
            return "other"


class QueryProfiler:
    """
    Utility for profiling database queries.
    
    This class provides methods to profile database queries, measure execution
    time, and identify slow or inefficient queries for optimization.
    """
    
    _instance = None
    _stats = None
    
    @classmethod
    def get_instance(cls) -> 'QueryProfiler':
        """
        Get the singleton instance of QueryProfiler.
        
        Returns:
            QueryProfiler instance
        """
        if cls._instance is None:
            cls._instance = QueryProfiler()
        return cls._instance
    
    def __init__(self):
        """Initialize the query profiler."""
        if QueryProfiler._stats is None:
            QueryProfiler._stats = QueryProfilerStats()
        self.stats = QueryProfiler._stats
        self.enabled = False
        self.slow_query_threshold = 0.1  # 100ms
        self.log_all_queries = False
        self.original_execute = None
        self.original_executemany = None
        
    def enable(self, log_all: bool = False, slow_threshold: float = 0.1):
        """
        Enable query profiling.
        
        Args:
            log_all: Whether to log all queries or only slow ones
            slow_threshold: Threshold in seconds for slow query classification
        """
        self.enabled = True
        self.log_all_queries = log_all
        self.slow_query_threshold = slow_threshold
        logger.info("Query profiling enabled")
        
    def disable(self):
        """Disable query profiling."""
        self.enabled = False
        logger.info("Query profiling disabled")
        
    def reset_stats(self):
        """Reset all profiling statistics."""
        self.stats.reset()
        logger.info("Query profiling statistics reset")
        
    @contextmanager
    def profile_query(self, query: str, params: Any = None, query_type: str = None):
        """
        Context manager for profiling a query.
        
        Args:
            query: SQL query string
            params: Query parameters
            query_type: Optional query classification
            
        Yields:
            None - this is just for timing the enclosed code
            
        Example:
            >>> with query_profiler.profile_query("SELECT * FROM users WHERE id = ?", (user_id,)):
            ...     cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            ...     user = cursor.fetchone()
        """
        if not self.enabled:
            yield
            return
            
        # Determine query type if not provided
        if query_type is None:
            query_type = self.stats._get_query_type(query)
            
        start_time = time.time()
        try:
            yield
        finally:
            execution_time = time.time() - start_time
            self.stats.record_query(query, params, execution_time, query_type)
            
            # Log slow queries
            if execution_time >= self.slow_query_threshold:
                logger.warning(f"Slow query ({execution_time:.4f}s): {query} - Params: {params}")
            elif self.log_all_queries:
                logger.debug(f"Query ({execution_time:.4f}s): {query} - Params: {params}")
    
    def profile_function(self, func=None, *, name=None):
        """
        Decorator for profiling a function that executes database queries.
        
        Args:
            func: Function to be profiled
            name: Optional custom name for the function in profiling data
            
        Returns:
            Decorated function
            
        Example:
            >>> @query_profiler.profile_function
            ... def find_user_by_id(user_id):
            ...     cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            ...     return cursor.fetchone()
        """
        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                if not self.enabled:
                    return f(*args, **kwargs)
                    
                func_name = name or f.__qualname__
                query_type = "function"
                
                start_time = time.time()
                try:
                    result = f(*args, **kwargs)
                    return result
                finally:
                    execution_time = time.time() - start_time
                    self.stats.record_query(f"Function: {func_name}", args, execution_time, query_type)
                    
                    # Log slow function calls
                    if execution_time >= self.slow_query_threshold:
                        logger.warning(f"Slow function ({execution_time:.4f}s): {func_name}")
                    elif self.log_all_queries:
                        logger.debug(f"Function ({execution_time:.4f}s): {func_name}")
        
        if func is None:
            return decorator
        return decorator(func)
    
    def instrument_connection(self, connection: sqlite3.Connection):
        """
        Instrument a SQLite connection to automatically profile all queries.
        
        This method monkey-patches the connection's execute and executemany
        methods to automatically profile all queries performed on this connection.
        
        Args:
            connection: SQLite connection to instrument
            
        Note:
            This should be used with caution in production environments.
        """
        if not hasattr(connection, '_original_execute'):
            # Store original methods
            connection._original_execute = connection.execute
            connection._original_executemany = connection.executemany
            
            # Replace with profiling versions
            def profiled_execute(sql, parameters=None):
                with self.profile_query(sql, parameters):
                    return connection._original_execute(sql, parameters)
                    
            def profiled_executemany(sql, parameters=None):
                with self.profile_query(sql, parameters):
                    return connection._original_executemany(sql, parameters)
                    
            connection.execute = profiled_execute
            connection.executemany = profiled_executemany
            
    def remove_instrumentation(self, connection: sqlite3.Connection):
        """
        Remove profiling instrumentation from a SQLite connection.
        
        Args:
            connection: SQLite connection to restore to original state
        """
        if hasattr(connection, '_original_execute'):
            connection.execute = connection._original_execute
            connection.executemany = connection._original_executemany
            del connection._original_execute
            del connection._original_executemany
            
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the query profiling statistics.
        
        Returns:
            Dictionary containing query profiling summary
        """
        return self.stats.get_summary()
        
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the slowest queries recorded.
        
        Args:
            limit: Maximum number of slow queries to return
            
        Returns:
            List of dictionaries containing slow query details
        """
        return self.stats.get_slow_queries(limit)
        
    def get_type_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """
        Get a breakdown of query statistics by query type.
        
        Returns:
            Dictionary mapping query types to their statistics
        """
        return self.stats.get_type_breakdown()
        
    def print_summary(self):
        """Print a summary of the query profiling statistics to the logger."""
        summary = self.get_summary()
        
        logger.info("===== Query Profiling Summary =====")
        logger.info(f"Total Queries: {summary['total_queries']}")
        logger.info(f"Total Execution Time: {summary['total_execution_time']:.4f}s")
        logger.info(f"Average Execution Time: {summary['avg_execution_time']:.4f}s")
        logger.info(f"Min Execution Time: {summary['min_execution_time']:.4f}s")
        logger.info(f"Max Execution Time: {summary['max_execution_time']:.4f}s")
        logger.info(f"Slow Query Count: {summary['slow_query_count']}")
        
        logger.info("Query Types:")
        for query_type, count in summary['query_types'].items():
            logger.info(f"  {query_type}: {count}")
            
        logger.info("Top Slow Queries:")
        for i, query_info in enumerate(self.get_slow_queries(5), 1):
            logger.info(f"  {i}. {query_info['execution_time']:.4f}s - {query_info['query']}")
            
    def generate_report(self) -> str:
        """
        Generate a detailed profiling report.
        
        Returns:
            Formatted report string
        """
        summary = self.get_summary()
        type_breakdown = self.get_type_breakdown()
        slow_queries = self.get_slow_queries(10)
        
        report = []
        report.append("===============================================")
        report.append("      DATABASE QUERY PERFORMANCE REPORT        ")
        report.append("===============================================")
        report.append("")
        
        report.append("OVERALL STATISTICS:")
        report.append(f"Total Queries Executed: {summary['total_queries']}")
        report.append(f"Total Execution Time:   {summary['total_execution_time']:.4f}s")
        report.append(f"Average Query Time:     {summary['avg_execution_time']:.4f}s")
        report.append(f"Slowest Query Time:     {summary['max_execution_time']:.4f}s")
        report.append(f"Number of Slow Queries: {summary['slow_query_count']}")
        report.append("")
        
        report.append("QUERY TYPE BREAKDOWN:")
        for query_type, stats in type_breakdown.items():
            report.append(f"  {query_type.upper()}:")
            report.append(f"    Count:        {stats['count']}")
            report.append(f"    Average Time: {stats['avg_time']:.4f}s")
            report.append(f"    Max Time:     {stats['max_time']:.4f}s")
            report.append(f"    Total Time:   {stats['total_time']:.4f}s")
        report.append("")
        
        report.append("TOP 10 SLOWEST QUERIES:")
        for i, query_info in enumerate(slow_queries, 1):
            report.append(f"  {i}. Time: {query_info['execution_time']:.4f}s")
            report.append(f"     Query: {query_info['query']}")
            report.append(f"     Params: {query_info['params']}")
            report.append(f"     Timestamp: {query_info['timestamp']}")
            report.append("")
            
        report.append("PERFORMANCE RECOMMENDATIONS:")
        
        # Add some basic recommendations based on the statistics
        if summary['avg_execution_time'] > 0.1:
            report.append("- Overall query performance is slow. Consider adding indices for frequently used columns.")
            
        select_stats = type_breakdown.get('select', {})
        if select_stats.get('avg_time', 0) > 0.1:
            report.append("- SELECT queries are running slowly. Review complex joins and consider query optimization.")
            
        if len(slow_queries) > 5:
            report.append("- Multiple slow queries detected. Consider reviewing database schema and adding appropriate indices.")
            
        if summary['total_queries'] > 1000:
            report.append("- Large number of queries executed. Consider using bulk operations or optimizing query patterns.")
            
        return "\n".join(report)


# Convenience singleton instance
query_profiler = QueryProfiler.get_instance()


@contextmanager
def profile_transaction(name: str = "Transaction"):
    """
    Context manager for profiling a database transaction.
    
    Args:
        name: Name to identify this transaction in profiling data
        
    Yields:
        None - this is just for timing the enclosed code
        
    Example:
        >>> with profile_transaction("Create User"):
        ...     # Series of database operations
        ...     db.execute("INSERT INTO users ...")
        ...     db.execute("INSERT INTO profiles ...")
    """
    profiler = QueryProfiler.get_instance()
    if not profiler.enabled:
        yield
        return
        
    start_time = time.time()
    try:
        yield
    finally:
        execution_time = time.time() - start_time
        profiler.stats.record_query(f"Transaction: {name}", None, execution_time, "transaction")
        
        # Log transaction time
        if execution_time >= profiler.slow_query_threshold:
            logger.warning(f"Slow transaction ({execution_time:.4f}s): {name}")
        elif profiler.log_all_queries:
            logger.debug(f"Transaction ({execution_time:.4f}s): {name}")

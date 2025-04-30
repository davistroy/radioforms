#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for query profiling and optimization functionality.

This module contains tests for the query profiler and optimizer classes,
ensuring they correctly measure, analyze, and optimize database queries.
"""

import unittest
import tempfile
import sqlite3
import os
import time
from pathlib import Path
from typing import Dict, List, Any

from radioforms.database.db_manager import DatabaseManager
from radioforms.database.query_profiler import QueryProfilerStats, QueryProfiler, profile_transaction
from radioforms.database.query_optimizer import QueryAnalyzer, QueryOptimizer, get_query_optimizer


class QueryProfilerTestCase(unittest.TestCase):
    """Test case for query profiling functionality."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary database
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_profiler.db"
        
        # Create a database manager
        self.db_manager = DatabaseManager(self.db_path)
        
        # Create test tables
        self._create_test_schema()
        
        # Reset profiler
        self.profiler = QueryProfiler.get_instance()
        self.profiler.reset_stats()
        
    def tearDown(self):
        """Clean up after the test."""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
            
        self.temp_dir.cleanup()
        
    def _create_test_schema(self):
        """Create test tables and data for profiling tests."""
        # Users table
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Products table
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Orders table with relationship to users
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Order items table with relationships to orders and products
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price_each REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
        ''')
        
        # Create indexes
        self.db_manager.execute('CREATE INDEX idx_orders_user_id ON orders(user_id)')
        self.db_manager.execute('CREATE INDEX idx_order_items_order_id ON order_items(order_id)')
        self.db_manager.execute('CREATE INDEX idx_order_items_product_id ON order_items(product_id)')
        
        # Insert test data
        # Users
        self.db_manager.execute("INSERT INTO users (name, email) VALUES (?, ?)", 
                               ("User 1", "user1@example.com"))
        self.db_manager.execute("INSERT INTO users (name, email) VALUES (?, ?)", 
                               ("User 2", "user2@example.com"))
        
        # Products
        self.db_manager.execute("INSERT INTO products (name, price) VALUES (?, ?)", 
                               ("Product 1", 10.99))
        self.db_manager.execute("INSERT INTO products (name, price) VALUES (?, ?)", 
                               ("Product 2", 5.99))
        self.db_manager.execute("INSERT INTO products (name, price) VALUES (?, ?)", 
                               ("Product 3", 15.99))
        
        # Orders
        self.db_manager.execute(
            "INSERT INTO orders (user_id, total_amount, status) VALUES (?, ?, ?)", 
            (1, 16.98, "completed")
        )
        self.db_manager.execute(
            "INSERT INTO orders (user_id, total_amount, status) VALUES (?, ?, ?)", 
            (2, 10.99, "pending")
        )
        
        # Order Items
        self.db_manager.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price_each) VALUES (?, ?, ?, ?)",
            (1, 1, 1, 10.99)
        )
        self.db_manager.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price_each) VALUES (?, ?, ?, ?)",
            (1, 2, 1, 5.99)
        )
        self.db_manager.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price_each) VALUES (?, ?, ?, ?)",
            (2, 1, 1, 10.99)
        )
        
        self.db_manager.commit()
        
    def test_query_profiler_stats(self):
        """Test the QueryProfilerStats class for recording and summarizing query statistics."""
        # Create a new QueryProfilerStats instance
        stats = QueryProfilerStats()
        
        # Record some test queries
        stats.record_query("SELECT * FROM test", None, 0.05, "select")
        stats.record_query("INSERT INTO test VALUES (1, 2, 3)", (1, 2, 3), 0.02, "insert")
        stats.record_query("UPDATE test SET col = 1", None, 0.03, "update")
        stats.record_query("DELETE FROM test", None, 0.01, "delete")
        stats.record_query("SELECT * FROM test WHERE id = ?", (1,), 0.2, "select")  # Slow query
        
        # Check statistics
        summary = stats.get_summary()
        self.assertEqual(summary["total_queries"], 5)
        self.assertAlmostEqual(summary["total_execution_time"], 0.31, places=2)
        self.assertAlmostEqual(summary["avg_execution_time"], 0.062, places=3)
        self.assertAlmostEqual(summary["min_execution_time"], 0.01, places=2)
        self.assertAlmostEqual(summary["max_execution_time"], 0.2, places=2)
        
        # Check query types
        self.assertEqual(summary["query_types"]["select"], 2)
        self.assertEqual(summary["query_types"]["insert"], 1)
        self.assertEqual(summary["query_types"]["update"], 1)
        self.assertEqual(summary["query_types"]["delete"], 1)
        
        # Check slow queries
        slow_queries = stats.get_slow_queries()
        self.assertEqual(len(slow_queries), 1)
        self.assertEqual(slow_queries[0]["query"], "SELECT * FROM test WHERE id = ?")
        self.assertAlmostEqual(slow_queries[0]["execution_time"], 0.2, places=2)
        
    def test_query_profiling(self):
        """Test query profiling using the profiler context manager."""
        # Enable profiling
        self.profiler.enable()
        
        # Execute some queries with profiling
        with self.profiler.profile_query("SELECT * FROM users"):
            self.db_manager.execute("SELECT * FROM users")
            
        with self.profiler.profile_query("INSERT INTO users (name, email) VALUES (?, ?)", ("Test User", "test@example.com")):
            self.db_manager.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Test User", "test@example.com"))
            
        # Get profiling results
        summary = self.profiler.get_summary()
        self.assertEqual(summary["total_queries"], 2)
        self.assertGreaterEqual(summary["total_execution_time"], 0)
        
        # Disable profiling
        self.profiler.disable()
        
    def test_query_profiling_decorator(self):
        """Test query profiling using the decorator."""
        # Enable profiling
        self.profiler.reset_stats()
        self.profiler.enable()
        
        # Define a test function with the profiling decorator
        @self.profiler.profile_function
        def test_query_function():
            self.db_manager.execute("SELECT * FROM users WHERE id = ?", (1,))
            return True
            
        # Call the function
        result = test_query_function()
        self.assertTrue(result)
        
        # Check profiling results
        summary = self.profiler.get_summary()
        self.assertEqual(summary["total_queries"], 1)
        self.assertGreaterEqual(summary["total_execution_time"], 0)
        
        # Verify function name in the query record
        self.assertTrue(any("Function: test_query_function" in q["query"] 
                          for q in self.profiler.get_slow_queries(limit=10)))
        
        # Disable profiling
        self.profiler.disable()
        
    def test_transaction_profiling(self):
        """Test transaction profiling using the context manager."""
        # Enable profiling
        self.profiler.reset_stats()
        self.profiler.enable()
        
        # Execute a transaction with profiling
        with profile_transaction("Test Transaction"):
            # Multiple queries in one transaction
            self.db_manager.execute("INSERT INTO products (name, price) VALUES (?, ?)", 
                                 ("Test Product", 25.99))
            self.db_manager.execute("SELECT * FROM products WHERE price > ?", (20.0,))
            self.db_manager.commit()
            
        # Check profiling results
        summary = self.profiler.get_summary()
        self.assertEqual(summary["total_queries"], 1)  # The transaction counts as one query
        self.assertGreaterEqual(summary["total_execution_time"], 0)
        
        # Verify transaction name in the query record
        slow_queries = self.profiler.get_slow_queries(limit=10)
        self.assertTrue(any("Transaction: Test Transaction" in q["query"] for q in slow_queries))
        
        # Disable profiling
        self.profiler.disable()
        
    def test_instrumentation(self):
        """Test automatic instrumentation of database connections."""
        # Enable profiling
        self.profiler.reset_stats()
        self.profiler.enable()
        
        # Instrument the connection
        self.profiler.instrument_connection(self.db_manager._get_connection())
        
        # Execute some queries - should be automatically profiled
        self.db_manager.execute("SELECT * FROM users")
        self.db_manager.execute("SELECT * FROM products WHERE price > ?", (10.0,))
        
        # Check profiling results
        summary = self.profiler.get_summary()
        self.assertEqual(summary["total_queries"], 2)
        
        # Remove instrumentation
        self.profiler.remove_instrumentation(self.db_manager._get_connection())
        
        # Execute another query - should not be profiled
        self.db_manager.execute("SELECT * FROM orders")
        
        # Check that the count hasn't changed
        new_summary = self.profiler.get_summary()
        self.assertEqual(new_summary["total_queries"], 2)
        
        # Disable profiling
        self.profiler.disable()


class QueryAnalyzerTestCase(unittest.TestCase):
    """Test case for query analysis functionality."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary database
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_analyzer.db"
        
        # Create a database manager
        self.db_manager = DatabaseManager(self.db_path)
        
        # Create test tables
        self._create_test_schema()
        
        # Create analyzer
        self.analyzer = QueryAnalyzer(self.db_manager)
        
    def tearDown(self):
        """Clean up after the test."""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
            
        self.temp_dir.cleanup()
        
    def _create_test_schema(self):
        """Create test tables and data for analysis tests."""
        # Users table
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Products table
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Orders table with relationship to users
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create some indices
        self.db_manager.execute('CREATE INDEX idx_users_email ON users(email)')
        self.db_manager.execute('CREATE INDEX idx_orders_user_id ON orders(user_id)')
        
        # Commit changes
        self.db_manager.commit()
        
    def test_analyze_select_query(self):
        """Test analysis of SELECT queries."""
        # Analyze a simple SELECT query
        query = "SELECT * FROM users WHERE id = 1"
        analysis = self.analyzer.analyze_query(query)
        
        # Check basic analysis results
        self.assertEqual(analysis["query_type"], "select")
        self.assertEqual(analysis["tables_referenced"], ["users"])
        self.assertEqual(analysis["columns_referenced"], ["*"])
        
        # Check WHERE conditions
        self.assertEqual(len(analysis["where_conditions"]), 1)
        self.assertEqual(analysis["where_conditions"][0]["condition"], "id = 1")
        
        # Check for issues - using SELECT *
        issues = [issue["type"] for issue in analysis["issues"]]
        self.assertIn("select_all", issues)
        
        # Check for recommendations
        recommendations = [rec["type"] for rec in analysis["recommendations"]]
        self.assertIn("rewrite_query", recommendations)
        
    def test_analyze_complex_query(self):
        """Test analysis of a complex query with joins and grouping."""
        # Analyze a more complex query
        query = """
        SELECT u.name, COUNT(o.id) as order_count, SUM(o.total_amount) as total_spent
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE u.id > 1
        GROUP BY u.id
        ORDER BY total_spent DESC
        LIMIT 10
        """
        
        analysis = self.analyzer.analyze_query(query)
        
        # Check basic analysis results
        self.assertEqual(analysis["query_type"], "select")
        self.assertEqual(analysis["tables_referenced"], ["users"])  # First table before joins
        
        # Check joins
        self.assertEqual(len(analysis["joins"]), 1)
        self.assertEqual(analysis["joins"][0]["table"], "orders")
        self.assertEqual(analysis["joins"][0]["type"], "LEFT")
        
        # Check GROUP BY
        self.assertEqual(analysis["group_by"], ["u.id"])
        
        # Check ORDER BY
        self.assertEqual(len(analysis["order_by"]), 1)
        self.assertEqual(analysis["order_by"][0]["column"], "total_spent")
        self.assertEqual(analysis["order_by"][0]["direction"], "DESC")
        
    def test_analyze_insert_query(self):
        """Test analysis of INSERT queries."""
        # Analyze an INSERT query
        query = "INSERT INTO products (name, price, category) VALUES ('Test', 9.99, 'Electronics')"
        analysis = self.analyzer.analyze_query(query)
        
        # Check basic analysis results
        self.assertEqual(analysis["query_type"], "insert")
        self.assertEqual(analysis["tables_referenced"], ["products"])
        self.assertEqual(set(analysis["columns_referenced"]), set(["name", "price", "category"]))
        
    def test_analyze_update_query(self):
        """Test analysis of UPDATE queries."""
        # Analyze an UPDATE query
        query = "UPDATE products SET price = 19.99, category = 'Premium' WHERE id = 1"
        analysis = self.analyzer.analyze_query(query)
        
        # Check basic analysis results
        self.assertEqual(analysis["query_type"], "update")
        self.assertEqual(analysis["tables_referenced"], ["products"])
        self.assertEqual(set(analysis["columns_referenced"]), set(["price", "category"]))
        
        # Check WHERE conditions
        self.assertEqual(len(analysis["where_conditions"]), 1)
        self.assertEqual(analysis["where_conditions"][0]["condition"], "id = 1")
        
    def test_analyze_leading_wildcard(self):
        """Test analysis of queries with leading wildcards in LIKE."""
        # Analyze a query with a leading wildcard
        query = "SELECT * FROM products WHERE name LIKE '%Book%'"
        analysis = self.analyzer.analyze_query(query)
        
        # Check for issues related to leading wildcard
        issues = [issue["type"] for issue in analysis["issues"]]
        self.assertIn("leading_wildcard", issues)
        
        # Check for recommendations
        recommendations = [rec["type"] for rec in analysis["recommendations"]]
        self.assertIn("rewrite_query", recommendations)
        
    def test_index_recommendations(self):
        """Test index recommendations based on query analysis."""
        # Analyze a query that could benefit from an index
        query = "SELECT * FROM products WHERE category = 'Electronics' ORDER BY price DESC"
        analysis = self.analyzer.analyze_query(query)
        
        # Check for index recommendations
        index_recommendations = [rec for rec in analysis["recommendations"] 
                               if rec["type"] == "create_index"]
        
        # There should be at least one index recommendation
        self.assertGreaterEqual(len(index_recommendations), 1)
        
        # Should recommend index for the WHERE clause
        category_indices = [rec for rec in index_recommendations 
                          if "category" in rec["columns"]]
        self.assertGreaterEqual(len(category_indices), 1)
        
        # Should recommend index for the ORDER BY clause
        price_indices = [rec for rec in index_recommendations 
                       if "price" in rec["columns"]]
        self.assertGreaterEqual(len(price_indices), 1)


class QueryOptimizerTestCase(unittest.TestCase):
    """Test case for query optimizer functionality."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary database
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_optimizer.db"
        
        # Create a database manager
        self.db_manager = DatabaseManager(self.db_path)
        
        # Create test tables
        self._create_test_schema()
        
        # Create optimizer
        self.optimizer = QueryOptimizer(self.db_manager)
        
    def tearDown(self):
        """Clean up after the test."""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
            
        self.temp_dir.cleanup()
        
    def _create_test_schema(self):
        """Create test tables and data for optimizer tests."""
        # Create tables similar to the analyzer tests
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create some indices but leave others for the optimizer to recommend
        self.db_manager.execute('CREATE INDEX idx_users_email ON users(email)')
        
        # Add some data
        for i in range(10):
            self.db_manager.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                (f"User {i}", f"user{i}@example.com")
            )
            
        for i in range(20):
            category = "Electronics" if i % 3 == 0 else "Books" if i % 3 == 1 else "Home"
            self.db_manager.execute(
                "INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
                (f"Product {i}", 10.0 + i, category)
            )
            
        for i in range(5):
            self.db_manager.execute(
                "INSERT INTO orders (user_id, total_amount, status) VALUES (?, ?, ?)",
                (i + 1, 50.0 + i * 10, "completed" if i % 2 == 0 else "pending")
            )
            
        self.db_manager.commit()
        
    def test_enable_profiling(self):
        """Test enabling and disabling query profiling."""
        # Enable profiling
        self.optimizer.enable_profiling(log_all=True)
        
        # Execute some queries
        self.db_manager.execute("SELECT * FROM users")
        self.db_manager.execute("SELECT * FROM products WHERE price > ?", (20.0,))
        
        # Check profiling results
        summary = self.optimizer.get_profile_summary()
        self.assertEqual(summary["total_queries"], 2)
        
        # Disable profiling
        self.optimizer.disable_profiling()
        
        # Execute another query
        self.db_manager.execute("SELECT * FROM orders")
        
        # Check that count hasn't changed
        new_summary = self.optimizer.get_profile_summary()
        self.assertEqual(new_summary["total_queries"], 2)
        
    def test_query_analysis(self):
        """Test query analysis through the optimizer."""
        # Analyze a query
        query = "SELECT * FROM products WHERE category = 'Electronics' ORDER BY price DESC"
        result = self.optimizer.analyze_query(query)
        
        # Verify analysis result
        self.assertEqual(result["query_type"], "select")
        self.assertEqual(result["tables_referenced"], ["products"])
        
        # Verify recommendations
        recommendations = [rec["type"] for rec in result["recommendations"]]
        self.assertIn("create_index", recommendations)
        self.assertIn("rewrite_query", recommendations)
        
    def test_instrumentation(self):
        """Test instrumenting the database manager for automatic profiling."""
        # Reset profiling stats
        self.optimizer.reset_profiling_stats()
        
        # Enable profiling
        self.optimizer.enable_profiling()
        
        # Instrument the database manager
        self.optimizer.instrument_db_manager()
        
        # Execute queries - should be automatically profiled
        self.db_manager.execute("SELECT * FROM users")
        self.db_manager.execute("SELECT * FROM products")
        
        # Check profiling results
        summary = self.optimizer.get_profile_summary()
        self.assertEqual(summary["total_queries"], 2)
        
    def test_optimization_report(self):
        """Test generating an optimization report."""
        # Enable profiling and instrument the connection
        self.optimizer.reset_profiling_stats()
        self.optimizer.enable_profiling()
        self.optimizer.instrument_db_manager()
        
        # Execute some queries to be profiled
        self.db_manager.execute("SELECT * FROM products WHERE category = 'Electronics'")
        self.db_manager.execute("SELECT * FROM products WHERE name LIKE '%1%'")
        self.db_manager.execute("""
            SELECT u.name, COUNT(o.id) as order_count 
            FROM users u 
            LEFT JOIN orders o ON u.id = o.user_id 
            GROUP BY u.id
        """)
        
        # Generate an optimization report
        report = self.optimizer.generate_optimization_report()
        
        # The report should be a non-empty string
        self.assertTrue(isinstance(report, str))
        self.assertGreater(len(report), 0)
        
    def test_create_recommended_indices(self):
        """Test creating recommended indices."""
        # Enable profiling and instrument the connection
        self.optimizer.reset_profiling_stats()
        self.optimizer.enable_profiling()
        self.optimizer.instrument_db_manager()
        
        # Execute a query that could benefit from an index
        self.db_manager.execute("SELECT * FROM products WHERE category = 'Electronics'")
        
        # Get count of recommended indices without creating them
        recommended_count = self.optimizer.create_recommended_indices(confirm=False)
        
        # There should be at least one recommended index
        self.assertGreaterEqual(recommended_count, 1)
        
        # Create the recommended indices
        created_count = self.optimizer.create_recommended_indices(confirm=True)
        
        # Verify indices were created
        self.assertGreaterEqual(created_count, 1)
        
        # Check that the index exists in the database
        cursor = self.db_manager.execute("PRAGMA index_list(products)")
        indices = [dict(row)["name"] for row in cursor.fetchall()]
        
        # There should be an index on the 'category' column
        category_index = [idx for idx in indices if "category" in idx.lower()]
        self.assertTrue(len(category_index) > 0)
        
    def test_convenience_function(self):
        """Test the convenience function for getting a query optimizer."""
        # Get an optimizer using the convenience function
        optimizer = get_query_optimizer(self.db_manager)
        
        # Verify it's a valid QueryOptimizer instance
        self.assertIsInstance(optimizer, QueryOptimizer)
        self.assertEqual(optimizer.db_manager, self.db_manager)


if __name__ == "__main__":
    unittest.main()

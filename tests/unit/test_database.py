"""Unit tests for database module."""

import pytest
import sqlite3
import tempfile
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.database.connection import (
    DatabaseManager, DatabaseError, DatabaseConnectionError, DatabaseCorruptionError
)
from src.database.schema import SchemaManager, SCHEMA_VERSION
from src.database.migrations import MigrationManager, Migration


class TestDatabaseManager:
    """Test DatabaseManager class."""
    
    def test_init(self, tmp_path):
        """Test DatabaseManager initialization."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        
        assert db_manager.database_path == db_path
        assert db_manager.timeout == 30.0
        assert db_path.parent.exists()  # Directory should be created
    
    def test_create_connection(self, tmp_path):
        """Test database connection creation."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        
        conn = db_manager.create_connection()
        
        assert isinstance(conn, sqlite3.Connection)
        
        # Test that WAL mode is enabled
        cursor = conn.execute("PRAGMA journal_mode")
        journal_mode = cursor.fetchone()[0]
        assert journal_mode.upper() == "WAL"
        
        # Test that foreign keys are enabled
        cursor = conn.execute("PRAGMA foreign_keys")
        foreign_keys = cursor.fetchone()[0]
        assert foreign_keys == 1
        
        conn.close()
    
    def test_get_connection_context_manager(self, tmp_path):
        """Test connection context manager."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        
        with db_manager.get_connection() as conn:
            assert isinstance(conn, sqlite3.Connection)
            
            # Create a test table and commit explicitly
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            conn.execute("INSERT INTO test (name) VALUES ('test')")
            conn.commit()
        
        # Connection should be closed after context
        # Verify data was saved by opening new connection
        with db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT name FROM test")
            result = cursor.fetchone()
            assert result is not None
            assert result[0] == "test"
    
    def test_get_transaction(self, tmp_path):
        """Test transaction context manager."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        
        # Create table first
        with db_manager.get_connection() as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        
        # Test successful transaction
        with db_manager.get_transaction() as conn:
            conn.execute("INSERT INTO test (name) VALUES ('test1')")
            conn.execute("INSERT INTO test (name) VALUES ('test2')")
        
        # Verify data was committed
        with db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM test")
            count = cursor.fetchone()[0]
            assert count == 2
        
        # Test transaction rollback on exception
        try:
            with db_manager.get_transaction() as conn:
                conn.execute("INSERT INTO test (name) VALUES ('test3')")
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Verify rollback - should still have only 2 records
        with db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM test")
            count = cursor.fetchone()[0]
            assert count == 2
    
    def test_execute_script(self, tmp_path):
        """Test SQL script execution."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        
        script = """
        CREATE TABLE test1 (id INTEGER PRIMARY KEY);
        CREATE TABLE test2 (id INTEGER PRIMARY KEY);
        INSERT INTO test1 (id) VALUES (1);
        INSERT INTO test2 (id) VALUES (2);
        """
        
        db_manager.execute_script(script)
        
        # Verify tables were created
        with db_manager.get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in cursor.fetchall()]
            assert 'test1' in tables
            assert 'test2' in tables
    
    def test_backup_database(self, tmp_path):
        """Test database backup."""
        db_path = tmp_path / "test.db"
        backup_path = tmp_path / "backup.db"
        
        db_manager = DatabaseManager(db_path)
        
        # Create some data and commit explicitly
        with db_manager.get_connection() as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            conn.execute("INSERT INTO test (name) VALUES ('backup_test')")
            conn.commit()
        
        # Create backup
        db_manager.backup_database(backup_path)
        
        assert backup_path.exists()
        
        # Verify backup contains data
        backup_manager = DatabaseManager(backup_path)
        with backup_manager.get_connection() as conn:
            cursor = conn.execute("SELECT name FROM test")
            result = cursor.fetchone()
            assert result is not None
            assert result[0] == "backup_test"
    
    def test_get_database_info(self, tmp_path):
        """Test database information retrieval."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        
        # Create some data
        with db_manager.get_connection() as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        
        info = db_manager.get_database_info()
        
        assert 'sqlite_version' in info
        assert 'page_count' in info
        assert 'page_size' in info
        assert 'journal_mode' in info
        assert info['journal_mode'].upper() == 'WAL'
        assert info['foreign_keys_enabled'] is True
        assert 'test' in info['tables']
    
    def test_invalid_database_file(self, tmp_path):
        """Test handling of invalid database file."""
        # Create a non-database file
        fake_db = tmp_path / "fake.db"
        fake_db.write_text("This is not a database file")
        
        db_manager = DatabaseManager(fake_db)
        
        with pytest.raises(DatabaseConnectionError) as exc_info:
            db_manager.create_connection()
        
        assert "not a valid SQLite database" in str(exc_info.value)


class TestSchemaManager:
    """Test SchemaManager class."""
    
    def test_initialize_database(self, tmp_path):
        """Test database initialization."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        schema_manager = SchemaManager(db_manager)
        
        schema_manager.initialize_database()
        
        # Verify tables were created
        with db_manager.get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['app_metadata', 'forms', 'form_versions']
            for table in expected_tables:
                assert table in tables
        
        # Verify metadata was inserted
        with db_manager.get_connection() as conn:
            cursor = conn.execute(
                "SELECT value FROM app_metadata WHERE key = 'schema_version'"
            )
            result = cursor.fetchone()
            assert result[0] == str(SCHEMA_VERSION)
    
    def test_validate_schema(self, tmp_path):
        """Test schema validation."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        schema_manager = SchemaManager(db_manager)
        
        # Initialize database
        schema_manager.initialize_database()
        
        # Validation should pass
        assert schema_manager.validate_schema() is True
    
    def test_get_schema_info(self, tmp_path):
        """Test schema information retrieval."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        schema_manager = SchemaManager(db_manager)
        
        schema_manager.initialize_database()
        
        info = schema_manager.get_schema_info()
        
        assert info['schema_version'] == SCHEMA_VERSION
        assert 'tables' in info
        assert 'indexes' in info
        assert 'forms' in info['tables']
        assert info['tables']['forms']['row_count'] == 0
    
    def test_create_sample_data(self, tmp_path):
        """Test sample data creation."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        schema_manager = SchemaManager(db_manager)
        
        schema_manager.initialize_database()
        schema_manager.create_sample_data()
        
        # Verify sample data was created
        with db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM forms")
            count = cursor.fetchone()[0]
            assert count > 0
            
            # Check that sample forms have proper structure
            cursor = conn.execute("SELECT form_type, data FROM forms LIMIT 1")
            result = cursor.fetchone()
            assert result[0] == 'ICS-213'
            assert '"subject"' in result[1]  # Verify JSON structure
    
    def test_reset_database(self, tmp_path):
        """Test database reset."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        schema_manager = SchemaManager(db_manager)
        
        # Initialize and add data
        schema_manager.initialize_database()
        schema_manager.create_sample_data()
        
        # Verify data exists
        with db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM forms")
            count = cursor.fetchone()[0]
            assert count > 0
        
        # Reset database
        schema_manager.reset_database()
        
        # Verify data was cleared but schema exists
        with db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM forms")
            count = cursor.fetchone()[0]
            assert count == 0
            
            # Verify tables still exist
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in cursor.fetchall()]
            assert 'forms' in tables


class TestMigrationManager:
    """Test MigrationManager class."""
    
    def test_get_current_version_empty_db(self, tmp_path):
        """Test getting version from empty database."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        migration_manager = MigrationManager(db_manager)
        
        version = migration_manager.get_current_version()
        assert version == 0
    
    def test_get_current_version_initialized_db(self, tmp_path):
        """Test getting version from initialized database."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        schema_manager = SchemaManager(db_manager)
        migration_manager = MigrationManager(db_manager)
        
        # Initialize database
        schema_manager.initialize_database()
        
        version = migration_manager.get_current_version()
        assert version == SCHEMA_VERSION
    
    def test_migrate_to_latest(self, tmp_path):
        """Test migration to latest version."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        migration_manager = MigrationManager(db_manager)
        
        # Database should start at version 0
        assert migration_manager.get_current_version() == 0
        
        # Migrate to latest
        migration_manager.migrate_to_latest()
        
        # Should be at current schema version
        assert migration_manager.get_current_version() == SCHEMA_VERSION
        
        # Verify tables were created
        with db_manager.get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in cursor.fetchall()]
            assert 'forms' in tables
    
    def test_get_pending_migrations(self, tmp_path):
        """Test getting pending migrations."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        migration_manager = MigrationManager(db_manager)
        
        # Should have pending migrations for empty database
        pending = migration_manager.get_pending_migrations()
        assert len(pending) > 0
        
        # Apply migrations
        migration_manager.migrate_to_latest()
        
        # Should have no pending migrations
        pending = migration_manager.get_pending_migrations()
        assert len(pending) == 0
    
    def test_validate_migrations(self, tmp_path):
        """Test migration validation."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        migration_manager = MigrationManager(db_manager)
        
        # Built-in migrations should be valid
        assert migration_manager.validate_migrations() is True
    
    def test_get_migration_status(self, tmp_path):
        """Test migration status information."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        migration_manager = MigrationManager(db_manager)
        
        status = migration_manager.get_migration_status()
        
        assert 'current_version' in status
        assert 'latest_version' in status
        assert 'migrations_pending' in status
        assert 'migrations' in status
        
        assert status['current_version'] == 0
        assert status['latest_version'] == SCHEMA_VERSION
        assert status['migrations_pending'] > 0


class TestMigration:
    """Test Migration class."""
    
    def test_migration_creation(self):
        """Test migration creation."""
        up_func = MagicMock()
        down_func = MagicMock()
        
        migration = Migration(
            version=1,
            description="Test migration",
            up_func=up_func,
            down_func=down_func
        )
        
        assert migration.version == 1
        assert migration.description == "Test migration"
        assert migration.up_func == up_func
        assert migration.down_func == down_func
    
    def test_migration_apply(self, tmp_path):
        """Test migration application."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        
        up_func = MagicMock()
        migration = Migration(1, "Test", up_func)
        
        migration.apply(db_manager)
        up_func.assert_called_once_with(db_manager)
    
    def test_migration_revert(self, tmp_path):
        """Test migration revert."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        
        up_func = MagicMock()
        down_func = MagicMock()
        migration = Migration(1, "Test", up_func, down_func)
        
        migration.revert(db_manager)
        down_func.assert_called_once_with(db_manager)
    
    def test_migration_revert_not_implemented(self, tmp_path):
        """Test migration revert without down function."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(db_path)
        
        up_func = MagicMock()
        migration = Migration(1, "Test", up_func)  # No down function
        
        with pytest.raises(NotImplementedError):
            migration.revert(db_manager)
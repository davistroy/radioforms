"""Database migration system.

This module provides a simple database migration system for schema evolution
and data transformation during application updates.
"""

import logging
from typing import List, Dict, Any, Callable
from pathlib import Path

from .connection import DatabaseManager, DatabaseError
from .schema import SCHEMA_VERSION


class Migration:
    """Represents a single database migration.
    
    Each migration has a version number, description, and up/down functions
    for applying and reverting the migration.
    """
    
    def __init__(
        self,
        version: int,
        description: str,
        up_func: Callable[[DatabaseManager], None],
        down_func: Callable[[DatabaseManager], None] = None
    ) -> None:
        """Initialize migration.
        
        Args:
            version: Migration version number
            description: Human-readable description
            up_func: Function to apply the migration
            down_func: Function to revert the migration (optional)
        """
        self.version = version
        self.description = description
        self.up_func = up_func
        self.down_func = down_func
    
    def apply(self, db_manager: DatabaseManager) -> None:
        """Apply this migration.
        
        Args:
            db_manager: Database manager instance
        """
        self.up_func(db_manager)
    
    def revert(self, db_manager: DatabaseManager) -> None:
        """Revert this migration.
        
        Args:
            db_manager: Database manager instance
            
        Raises:
            NotImplementedError: If no down function provided
        """
        if self.down_func is None:
            raise NotImplementedError(f"Migration {self.version} cannot be reverted")
        self.down_func(db_manager)


class MigrationManager:
    """Manages database schema migrations.
    
    This class handles:
    - Migration tracking and execution
    - Schema version management
    - Migration validation
    - Rollback capabilities
    
    Example:
        migration_manager = MigrationManager(db_manager)
        migration_manager.migrate_to_latest()
    """
    
    def __init__(self, db_manager: DatabaseManager) -> None:
        """Initialize migration manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.migrations: List[Migration] = []
        
        # Register built-in migrations
        self._register_migrations()
    
    def _register_migrations(self) -> None:
        """Register all available migrations."""
        # Migration 1: Initial schema creation
        self.migrations.append(
            Migration(
                version=1,
                description="Initial schema creation",
                up_func=self._migration_001_up,
                down_func=self._migration_001_down
            )
        )
        
        # Future migrations would be added here
        # self.migrations.append(Migration(2, "Add user preferences", ...))
    
    def _migration_001_up(self, db_manager: DatabaseManager) -> None:
        """Migration 001: Create initial schema."""
        from .schema import SchemaManager
        
        schema_manager = SchemaManager(db_manager)
        schema_manager.initialize_database()
        
        self.logger.info("Migration 001: Initial schema created")
    
    def _migration_001_down(self, db_manager: DatabaseManager) -> None:
        """Migration 001 rollback: Drop all tables."""
        try:
            with db_manager.get_transaction() as conn:
                # Get all tables
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                tables = [row[0] for row in cursor.fetchall()]
                
                # Drop all tables except SQLite internal ones
                for table in tables:
                    if not table.startswith('sqlite_'):
                        conn.execute(f"DROP TABLE IF EXISTS {table}")
                        self.logger.debug(f"Dropped table: {table}")
            
            self.logger.info("Migration 001 rollback: All tables dropped")
            
        except Exception as e:
            raise DatabaseError(f"Failed to rollback migration 001: {e}") from e
    
    def get_current_version(self) -> int:
        """Get current database schema version.
        
        Returns:
            Current schema version, or 0 if not initialized
        """
        try:
            with self.db_manager.get_connection() as conn:
                # Check if metadata table exists
                cursor = conn.execute(
                    """
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='app_metadata'
                    """
                )
                
                if not cursor.fetchone():
                    return 0  # Database not initialized
                
                # Get schema version
                cursor = conn.execute(
                    "SELECT value FROM app_metadata WHERE key = 'schema_version'"
                )
                result = cursor.fetchone()
                
                return int(result[0]) if result else 0
                
        except Exception as e:
            self.logger.error(f"Failed to get current version: {e}")
            return 0
    
    def set_version(self, version: int) -> None:
        """Set database schema version.
        
        Args:
            version: Version number to set
        """
        try:
            with self.db_manager.get_transaction() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO app_metadata (key, value) 
                    VALUES ('schema_version', ?)
                    """,
                    (str(version),)
                )
            
            self.logger.debug(f"Schema version set to {version}")
            
        except Exception as e:
            raise DatabaseError(f"Failed to set schema version: {e}") from e
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get list of pending migrations.
        
        Returns:
            List of migrations that need to be applied
        """
        current_version = self.get_current_version()
        
        pending = [
            migration for migration in self.migrations
            if migration.version > current_version
        ]
        
        # Sort by version
        pending.sort(key=lambda m: m.version)
        
        return pending
    
    def migrate_to_latest(self) -> None:
        """Apply all pending migrations to reach latest schema version.
        
        Raises:
            DatabaseError: If migration fails
        """
        pending = self.get_pending_migrations()
        
        if not pending:
            self.logger.info("Database is already at latest version")
            return
        
        self.logger.info(f"Applying {len(pending)} pending migrations")
        
        try:
            for migration in pending:
                self.logger.info(
                    f"Applying migration {migration.version}: {migration.description}"
                )
                
                # Apply migration
                migration.apply(self.db_manager)
                
                # Update version
                self.set_version(migration.version)
                
                self.logger.info(f"Migration {migration.version} completed successfully")
            
            final_version = self.get_current_version()
            self.logger.info(f"Database migrated to version {final_version}")
            
        except Exception as e:
            error_msg = f"Migration failed: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def migrate_to_version(self, target_version: int) -> None:
        """Migrate to a specific schema version.
        
        Args:
            target_version: Target schema version
            
        Raises:
            DatabaseError: If migration fails
        """
        current_version = self.get_current_version()
        
        if target_version == current_version:
            self.logger.info(f"Database is already at version {target_version}")
            return
        
        if target_version > current_version:
            # Forward migration
            pending = [
                m for m in self.migrations
                if current_version < m.version <= target_version
            ]
            
            for migration in sorted(pending, key=lambda m: m.version):
                self.logger.info(
                    f"Applying migration {migration.version}: {migration.description}"
                )
                migration.apply(self.db_manager)
                self.set_version(migration.version)
                
        else:
            # Rollback migration
            to_rollback = [
                m for m in self.migrations
                if target_version < m.version <= current_version
            ]
            
            for migration in sorted(to_rollback, key=lambda m: m.version, reverse=True):
                self.logger.info(
                    f"Rolling back migration {migration.version}: {migration.description}"
                )
                migration.revert(self.db_manager)
                self.set_version(migration.version - 1)
        
        final_version = self.get_current_version()
        self.logger.info(f"Database migrated to version {final_version}")
    
    def validate_migrations(self) -> bool:
        """Validate migration consistency and ordering.
        
        Returns:
            True if migrations are valid
            
        Raises:
            DatabaseError: If validation fails
        """
        # Check for duplicate versions
        versions = [m.version for m in self.migrations]
        if len(versions) != len(set(versions)):
            raise DatabaseError("Duplicate migration versions found")
        
        # Check for sequential numbering
        sorted_versions = sorted(versions)
        for i, version in enumerate(sorted_versions, 1):
            if version != i:
                raise DatabaseError(f"Migration versions must be sequential, missing version {i}")
        
        # Check that latest migration matches expected schema version
        if sorted_versions and sorted_versions[-1] != SCHEMA_VERSION:
            raise DatabaseError(
                f"Latest migration version {sorted_versions[-1]} does not match "
                f"expected schema version {SCHEMA_VERSION}"
            )
        
        self.logger.debug("Migration validation passed")
        return True
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get detailed migration status information.
        
        Returns:
            Dictionary with migration status
        """
        current_version = self.get_current_version()
        pending = self.get_pending_migrations()
        
        status = {
            'current_version': current_version,
            'latest_version': SCHEMA_VERSION,
            'migrations_pending': len(pending),
            'migrations': []
        }
        
        for migration in self.migrations:
            migration_status = {
                'version': migration.version,
                'description': migration.description,
                'applied': migration.version <= current_version,
                'can_rollback': migration.down_func is not None
            }
            status['migrations'].append(migration_status)
        
        return status
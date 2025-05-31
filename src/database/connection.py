"""Database connection management.

This module provides SQLite database connection management with proper
resource handling, WAL mode activation, and error recovery.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, ContextManager, Any
from contextlib import contextmanager


class DatabaseError(Exception):
    """Base exception for database-related errors."""
    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""
    pass


class DatabaseCorruptionError(DatabaseError):
    """Raised when database corruption is detected."""
    pass


class DatabaseManager:
    """Manages SQLite database connections with proper resource handling.
    
    This class provides:
    - Connection pooling and management
    - WAL mode activation for improved concurrency
    - Automatic database initialization
    - Error recovery for common issues
    - Transaction management
    
    Example:
        db_manager = DatabaseManager(Path("radioforms.db"))
        with db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM forms")
            results = cursor.fetchall()
    """
    
    def __init__(self, database_path: Path, timeout: float = 30.0) -> None:
        """Initialize database manager.
        
        Args:
            database_path: Path to SQLite database file
            timeout: Connection timeout in seconds
        """
        self.database_path = database_path
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        # Ensure database directory exists
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"DatabaseManager initialized for: {database_path}")
    
    def _configure_connection(self, conn: sqlite3.Connection) -> None:
        """Configure a SQLite connection with optimal settings.
        
        Args:
            conn: SQLite connection to configure
        """
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Set WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode = WAL")
        
        # Set reasonable timeout
        conn.execute(f"PRAGMA busy_timeout = {int(self.timeout * 1000)}")
        
        # Enable automatic index creation
        conn.execute("PRAGMA automatic_index = ON")
        
        # Set page size for better performance
        conn.execute("PRAGMA page_size = 4096")
        
        # Commit the pragma settings
        conn.commit()
        
        self.logger.debug("Database connection configured with WAL mode and optimizations")
    
    def _check_database_integrity(self, conn: sqlite3.Connection) -> bool:
        """Check database integrity.
        
        Args:
            conn: Database connection to check
            
        Returns:
            True if database is intact, False if corrupted
            
        Raises:
            DatabaseCorruptionError: If corruption is detected
        """
        try:
            cursor = conn.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            if result and result[0] != "ok":
                error_msg = f"Database integrity check failed: {result[0]}"
                self.logger.error(error_msg)
                raise DatabaseCorruptionError(error_msg)
            
            self.logger.debug("Database integrity check passed")
            return True
            
        except sqlite3.Error as e:
            error_msg = f"Database integrity check failed: {e}"
            self.logger.error(error_msg)
            raise DatabaseCorruptionError(error_msg) from e
    
    def create_connection(self) -> sqlite3.Connection:
        """Create a new database connection.
        
        Returns:
            Configured SQLite connection
            
        Raises:
            DatabaseConnectionError: If connection fails
            DatabaseCorruptionError: If database is corrupted
        """
        try:
            # Check if database file exists and is readable
            if self.database_path.exists():
                if not self.database_path.is_file():
                    raise DatabaseConnectionError(
                        f"Database path exists but is not a file: {self.database_path}"
                    )
                
                # Check file permissions
                if not self.database_path.stat().st_size == 0:  # Not empty
                    try:
                        with open(self.database_path, 'rb') as f:
                            header = f.read(16)
                            if not header.startswith(b'SQLite format 3'):
                                raise DatabaseConnectionError(
                                    f"File is not a valid SQLite database: {self.database_path}"
                                )
                    except IOError as e:
                        raise DatabaseConnectionError(
                            f"Cannot read database file: {e}"
                        ) from e
            
            # Create connection
            conn = sqlite3.Connection(
                str(self.database_path),
                timeout=self.timeout,
                check_same_thread=False
            )
            
            # Configure connection
            self._configure_connection(conn)
            
            # Check integrity if database exists
            if self.database_path.exists() and self.database_path.stat().st_size > 0:
                self._check_database_integrity(conn)
            
            self.logger.info(f"Database connection created: {self.database_path}")
            return conn
            
        except sqlite3.Error as e:
            error_msg = f"Failed to connect to database {self.database_path}: {e}"
            self.logger.error(error_msg)
            raise DatabaseConnectionError(error_msg) from e
        except (IOError, OSError) as e:
            error_msg = f"File system error accessing database {self.database_path}: {e}"
            self.logger.error(error_msg)
            raise DatabaseConnectionError(error_msg) from e
    
    @contextmanager
    def get_connection(self) -> ContextManager[sqlite3.Connection]:
        """Get a database connection as a context manager.
        
        Yields:
            Configured SQLite connection
            
        Example:
            with db_manager.get_connection() as conn:
                conn.execute("INSERT INTO forms (...) VALUES (...)")
        """
        conn = None
        try:
            conn = self.create_connection()
            yield conn
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                    self.logger.debug("Transaction rolled back due to error")
                except sqlite3.Error:
                    pass  # Rollback failed, connection may be closed
            raise
        finally:
            if conn:
                try:
                    conn.close()
                    self.logger.debug("Database connection closed")
                except sqlite3.Error as e:
                    self.logger.warning(f"Error closing connection: {e}")
    
    @contextmanager
    def get_transaction(self) -> ContextManager[sqlite3.Connection]:
        """Get a database connection with automatic transaction management.
        
        Yields:
            Configured SQLite connection with transaction
            
        The transaction is automatically committed on success or rolled back on error.
        
        Example:
            with db_manager.get_transaction() as conn:
                conn.execute("INSERT INTO forms (...) VALUES (...)")
                conn.execute("UPDATE metadata SET last_modified = ?", (datetime.now(),))
                # Automatically committed here
        """
        with self.get_connection() as conn:
            try:
                conn.execute("BEGIN")
                yield conn
                conn.execute("COMMIT")
                self.logger.debug("Transaction committed successfully")
            except Exception as e:
                try:
                    conn.execute("ROLLBACK")
                    self.logger.debug("Transaction rolled back due to error")
                except sqlite3.Error:
                    pass  # Rollback failed
                raise
    
    def execute_script(self, script: str) -> None:
        """Execute a SQL script.
        
        Args:
            script: SQL script to execute
            
        Raises:
            DatabaseError: If script execution fails
        """
        try:
            with self.get_connection() as conn:
                conn.executescript(script)
            
            self.logger.info("SQL script executed successfully")
            
        except sqlite3.Error as e:
            error_msg = f"Failed to execute SQL script: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def backup_database(self, backup_path: Path) -> None:
        """Create a backup of the database.
        
        Args:
            backup_path: Path for backup file
            
        Raises:
            DatabaseError: If backup fails
        """
        try:
            # Ensure backup directory exists
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            with self.get_connection() as source_conn:
                backup_conn = sqlite3.connect(str(backup_path))
                try:
                    source_conn.backup(backup_conn)
                    self.logger.info(f"Database backed up to: {backup_path}")
                finally:
                    backup_conn.close()
                    
        except sqlite3.Error as e:
            error_msg = f"Failed to backup database to {backup_path}: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
        except (IOError, OSError) as e:
            error_msg = f"File system error during backup to {backup_path}: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def get_database_info(self) -> dict[str, Any]:
        """Get database information and statistics.
        
        Returns:
            Dictionary with database information
        """
        try:
            with self.get_connection() as conn:
                info = {}
                
                # Database file info
                if self.database_path.exists():
                    stat = self.database_path.stat()
                    info['file_size'] = stat.st_size
                    info['last_modified'] = stat.st_mtime
                
                # SQLite version and settings
                cursor = conn.execute("SELECT sqlite_version()")
                info['sqlite_version'] = cursor.fetchone()[0]
                
                cursor = conn.execute("PRAGMA page_count")
                info['page_count'] = cursor.fetchone()[0]
                
                cursor = conn.execute("PRAGMA page_size")
                info['page_size'] = cursor.fetchone()[0]
                
                cursor = conn.execute("PRAGMA journal_mode")
                info['journal_mode'] = cursor.fetchone()[0]
                
                cursor = conn.execute("PRAGMA foreign_keys")
                info['foreign_keys_enabled'] = bool(cursor.fetchone()[0])
                
                # Table information
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                )
                info['tables'] = [row[0] for row in cursor.fetchall()]
                
                return info
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get database info: {e}")
            return {'error': str(e)}
    
    def vacuum_database(self) -> None:
        """Vacuum the database to reclaim space and optimize.
        
        Raises:
            DatabaseError: If vacuum operation fails
        """
        try:
            with self.get_connection() as conn:
                conn.execute("VACUUM")
            
            self.logger.info("Database vacuum completed successfully")
            
        except sqlite3.Error as e:
            error_msg = f"Failed to vacuum database: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
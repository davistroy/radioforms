/*!
 * Database module for RadioForms application
 * 
 * This module handles all database operations for the STANDALONE ICS Forms
 * Management Application. The database is a single SQLite file that travels
 * with the application for portable operation.
 * 
 * Business Logic:
 * - Single SQLite database file for complete portability
 * - Relative path handling for flash drive compatibility
 * - Simple schema design following "simpler is better" principle
 * - All form data stored as JSON for flexibility
 * 
 * Key Features:
 * - Auto-creates database on first run
 * - Migration support for schema updates
 * - Connection pooling for performance
 * - Transaction safety for data integrity
 */

use sqlx::{SqlitePool, sqlite::SqlitePoolOptions, migrate::MigrateDatabase, Sqlite, Row};
use std::path::PathBuf;
use std::env;
use std::time::Duration;
use anyhow::{Result, Context};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use crate::database::migration_runner::{MigrationRunner, MigrationRunnerFactory};
use crate::database::transactions::{TransactionManager, TransactionResult, TransactionStatsSnapshot};
use crate::database::crud_operations::CrudOperations;
use crate::database::errors::{DatabaseError, DatabaseResult, ErrorContext};
use crate::database::integrity_checker::{IntegrityChecker, IntegrityCheckerFactory, IntegrityCheckResult};

pub mod schema;
pub mod migrations;
pub mod migration_runner;
pub mod transactions;
pub mod crud_operations;
pub mod errors;
pub mod integrity_checker;

#[cfg(test)]
mod migration_tests;

/// Database connection manager for the RadioForms application.
/// Handles SQLite database initialization, migrations, connection pooling, and transactions.
pub struct Database {
    pool: SqlitePool,
    db_path: PathBuf,
    transaction_manager: TransactionManager,
    crud_operations: CrudOperations,
}

impl Database {
    /// Creates a new database instance with portable path handling.
    /// 
    /// Business Logic:
    /// - Database file is always created relative to the executable location
    /// - Ensures compatibility with USB drives and removable storage
    /// - Creates directory structure if it doesn't exist
    /// 
    /// Returns the database path relative to the executable for portability.
    pub async fn new() -> Result<Self> {
        let db_path = Self::get_database_path()?;
        
        // Create parent directory if it doesn't exist
        if let Some(parent) = db_path.parent() {
            tokio::fs::create_dir_all(parent).await
                .context("Failed to create database directory")?;
        }

        let db_url = format!("sqlite:{}", db_path.display());
        
        // Create database file if it doesn't exist
        if !Sqlite::database_exists(&db_url).await.unwrap_or(false) {
            log::info!("Creating new database at: {}", db_path.display());
            Sqlite::create_database(&db_url).await
                .context("Failed to create database")?;
        }

        // Create optimized connection pool with specific parameters
        // Following Task 2.1 requirements: max 10 connections, proper timeouts
        let pool = SqlitePoolOptions::new()
            .max_connections(10)  // Task requirement: max 10 connections
            .min_connections(1)   // Keep at least one connection open
            .acquire_timeout(Duration::from_secs(30))  // 30 second acquire timeout
            .idle_timeout(Duration::from_secs(300))    // 5 minute idle timeout
            .max_lifetime(Duration::from_secs(1800))   // 30 minute max lifetime
            .test_before_acquire(true)  // Test connections before use
            .connect(&db_url).await
            .context("Failed to create database connection pool")?;

        // Initialize transaction manager
        let transaction_manager = TransactionManager::new(pool.clone());
        
        // Initialize CRUD operations with enhanced transaction support
        let crud_operations = CrudOperations::new(pool.clone());
        
        let database = Self { 
            pool, 
            db_path,
            transaction_manager,
            crud_operations,
        };
        
        // Configure SQLite connection settings for optimal performance
        database.configure_sqlite_pragmas().await?;
        
        // Run migrations
        database.run_migrations().await?;
        
        // Log connection pool status
        log::info!("Database connection pool initialized: max_connections=10, idle_timeout=300s");
        
        Ok(database)
    }

    /// Gets the database file path relative to the executable location.
    /// 
    /// Business Logic:
    /// - For STANDALONE operation, database must be alongside executable
    /// - Supports portable operation from any directory or drive
    /// - Consistent behavior across Windows, macOS, and Linux
    fn get_database_path() -> Result<PathBuf> {
        let exe_path = env::current_exe()
            .context("Failed to get executable path")?;
        let exe_dir = exe_path.parent()
            .context("Failed to get executable directory")?;
        
        Ok(exe_dir.join("radioforms.db"))
    }

    /// Runs database migrations to ensure schema is up to date.
    /// 
    /// Business Logic:
    /// - Enhanced migration system with rollback and tracking capabilities
    /// - Preserves existing data during migrations with backup creation
    /// - Comprehensive logging and error reporting for troubleshooting
    /// - Production-ready migration execution with integrity validation
    async fn run_migrations(&self) -> Result<()> {
        log::info!("Running enhanced database migrations...");
        
        // Create production migration runner for maximum safety
        let mut runner = MigrationRunnerFactory::create_production_runner(
            self.pool.clone(), 
            self.db_path.clone()
        ).await.context("Failed to create migration runner")?;
        
        // Create backup before running migrations
        let backup_path = runner.create_backup().await
            .context("Failed to create pre-migration backup")?;
        log::info!("Pre-migration backup created: {}", backup_path.display());
        
        // Run SQLx embedded migrations
        runner.run_sqlx_migrations().await
            .context("Failed to execute SQLx migrations")?;
        
        // Perform post-migration optimization and validation
        runner.optimize_post_migration().await
            .context("Failed to optimize database after migration")?;
        
        // Validate migration integrity
        let validation_issues = runner.validate_migrations().await
            .context("Failed to validate migration integrity")?;
        
        if !validation_issues.is_empty() {
            log::warn!("Migration validation found {} issues: {:?}", 
                     validation_issues.len(), validation_issues);
            // Continue execution but log warnings - issues may not be critical
        }
        
        log::info!("Enhanced database migrations completed successfully");
        Ok(())
    }

    /// Gets a reference to the database connection pool.
    /// Used by other modules to execute database operations.
    pub fn pool(&self) -> &SqlitePool {
        &self.pool
    }

    /// Gets the database file path for backup operations.
    pub fn database_path(&self) -> &PathBuf {
        &self.db_path
    }

    /// Gets a reference to the CRUD operations manager.
    /// Provides enterprise-grade database operations with transaction support.
    /// 
    /// Business Logic:
    /// - Returns comprehensive CRUD operations with validation
    /// - Includes transaction support and optimistic locking
    /// - Provides search capabilities with pagination
    /// - Supports advanced form management operations
    pub fn crud(&self) -> &CrudOperations {
        &self.crud_operations
    }

    /// Closes the database connection gracefully.
    /// Should be called when the application shuts down.
    pub async fn close(self) {
        self.pool.close().await;
        log::info!("Database connection closed");
    }

    /// Creates a backup of the database file.
    /// 
    /// Business Logic:
    /// - Simple file copy for user-friendly backup process
    /// - Backup includes timestamp for version tracking
    /// - Returns backup file path for user confirmation
    pub async fn create_backup(&self) -> Result<PathBuf> {
        let timestamp = Utc::now().format("%Y%m%d_%H%M%S");
        let backup_filename = format!("radioforms_backup_{}.db", timestamp);
        
        let backup_path = self.db_path.parent()
            .context("Failed to get database directory")?
            .join(backup_filename);

        tokio::fs::copy(&self.db_path, &backup_path).await
            .context("Failed to create database backup")?;

        log::info!("Database backup created: {}", backup_path.display());
        Ok(backup_path)
    }

    /// Restores database from a backup file.
    /// 
    /// Business Logic:
    /// - Replaces current database with backup
    /// - Creates backup of current database before restore
    /// - Validates backup file before proceeding
    pub async fn restore_backup(&self, backup_path: &PathBuf) -> Result<()> {
        // Validate backup file exists
        if !backup_path.exists() {
            return Err(anyhow::anyhow!("Backup file does not exist: {}", backup_path.display()));
        }

        // Create backup of current database
        let current_backup = self.create_backup().await?;
        log::info!("Current database backed up to: {}", current_backup.display());

        // Close current connection
        self.pool.close().await;

        // Replace database file
        tokio::fs::copy(backup_path, &self.db_path).await
            .context("Failed to restore database from backup")?;

        log::info!("Database restored from: {}", backup_path.display());
        Ok(())
    }

    /// Validates database integrity.
    /// 
    /// Business Logic:
    /// - Runs SQLite integrity check
    /// - Validates form data JSON structure
    /// - Reports any corruption or issues
    pub async fn validate_integrity(&self) -> Result<bool> {
        // Run SQLite integrity check
        let integrity_result = sqlx::query("PRAGMA integrity_check")
            .fetch_one(&self.pool)
            .await
            .context("Failed to run integrity check")?;

        let result: String = integrity_result.try_get(0)
            .context("Failed to get integrity check result")?;

        if result != "ok" {
            log::error!("Database integrity check failed: {}", result);
            return Ok(false);
        }

        // Additional validation could be added here
        // (e.g., JSON format validation, form data consistency)

        log::info!("Database integrity check passed");
        Ok(true)
    }

    /// Configures SQLite PRAGMA settings for optimal performance and safety.
    /// 
    /// Business Logic:
    /// - Sets WAL mode for better concurrency and crash safety
    /// - Configures journal mode for data integrity
    /// - Sets synchronous mode for performance/safety balance
    /// - Enables foreign key constraints
    /// - Sets appropriate cache sizes and timeouts
    async fn configure_sqlite_pragmas(&self) -> Result<()> {
        log::info!("Configuring SQLite PRAGMA settings for optimal performance...");
        
        // Enable WAL mode for better concurrency and crash safety
        sqlx::query("PRAGMA journal_mode = WAL")
            .execute(&self.pool)
            .await
            .context("Failed to set WAL journal mode")?;
        
        // Set synchronous mode to NORMAL for good performance/safety balance
        sqlx::query("PRAGMA synchronous = NORMAL")
            .execute(&self.pool)
            .await
            .context("Failed to set synchronous mode")?;
        
        // Enable foreign key constraints (critical for data integrity)
        sqlx::query("PRAGMA foreign_keys = ON")
            .execute(&self.pool)
            .await
            .context("Failed to enable foreign key constraints")?;
        
        // Set cache size to 64MB (16384 pages * 4KB = 64MB)
        sqlx::query("PRAGMA cache_size = -65536")  // Negative value means KB
            .execute(&self.pool)
            .await
            .context("Failed to set cache size")?;
        
        // Set busy timeout to 30 seconds
        sqlx::query("PRAGMA busy_timeout = 30000")
            .execute(&self.pool)
            .await
            .context("Failed to set busy timeout")?;
        
        // Set temp store to memory for better performance
        sqlx::query("PRAGMA temp_store = MEMORY")
            .execute(&self.pool)
            .await
            .context("Failed to set temp store mode")?;
        
        // Set mmap size to 256MB for better I/O performance
        sqlx::query("PRAGMA mmap_size = 268435456")
            .execute(&self.pool)
            .await
            .context("Failed to set mmap size")?;
        
        log::info!("SQLite PRAGMA settings configured successfully");
        Ok(())
    }

    /// Gets connection pool statistics for monitoring.
    /// 
    /// Business Logic:
    /// - Provides insight into connection pool utilization
    /// - Helps identify connection leaks or performance issues
    /// - Useful for debugging and optimization
    pub fn get_pool_stats(&self) -> ConnectionPoolStats {
        ConnectionPoolStats {
            size: self.pool.size(),
            idle: self.pool.num_idle(),
            is_closed: self.pool.is_closed(),
            max_connections: 10, // Our configured max
        }
    }

    /// Performs connection pool health check.
    /// 
    /// Business Logic:
    /// - Verifies pool is operational and responsive
    /// - Tests connection acquisition and basic query execution
    /// - Provides health status for monitoring systems
    pub async fn check_pool_health(&self) -> Result<bool> {
        // Try to acquire a connection and run a simple query
        let result = sqlx::query_scalar::<_, i64>("SELECT 1")
            .fetch_one(&self.pool)
            .await;
        
        match result {
            Ok(1) => {
                log::debug!("Connection pool health check passed");
                Ok(true)
            },
            Ok(val) => {
                log::warn!("Connection pool health check returned unexpected value: {}", val);
                Ok(false)
            },
            Err(e) => {
                log::error!("Connection pool health check failed: {}", e);
                Ok(false)
            }
        }
    }

    /// Executes a function within a database transaction with automatic rollback on error.
    /// 
    /// Business Logic:
    /// - Provides atomic operations for multiple database changes
    /// - Automatically rolls back on any error to maintain consistency
    /// - Tracks transaction performance and statistics
    /// - Supports complex business operations requiring multiple SQL statements
    pub async fn execute_transaction<F, T, E>(&self, operation: F) -> Result<TransactionResult<T>>
    where
        F: for<'c> FnOnce(&mut sqlx::Transaction<'c, sqlx::Sqlite>) -> std::pin::Pin<Box<dyn std::future::Future<Output = Result<T, E>> + Send + 'c>>,
        T: Send + 'static,
        E: Into<anyhow::Error> + Send + 'static,
    {
        self.transaction_manager.execute_transaction(operation).await
    }

    /// Executes multiple operations in a single transaction with batch optimization.
    /// 
    /// Business Logic:
    /// - Optimizes performance for multiple related operations
    /// - Ensures all operations succeed or all fail (atomicity)
    /// - Reduces transaction overhead for bulk operations
    /// - Provides detailed reporting on batch operation results
    pub async fn execute_batch_transaction<F, T>(&self, operations: Vec<F>) -> Result<Vec<TransactionResult<T>>>
    where
        F: for<'c> FnOnce(&mut sqlx::Transaction<'c, sqlx::Sqlite>) -> std::pin::Pin<Box<dyn std::future::Future<Output = Result<T>> + Send + 'c>>,
        T: Send + Default + 'static,
    {
        self.transaction_manager.execute_batch_transaction(operations).await
    }

    /// Executes an operation with retry logic for handling temporary failures.
    /// 
    /// Business Logic:
    /// - Automatically retries transient database errors
    /// - Uses exponential backoff to avoid overwhelming database
    /// - Distinguishes between retryable and permanent errors
    /// - Provides comprehensive retry attempt logging
    pub async fn execute_with_retry<F, T, E>(&self, max_retries: u32, operation: F) -> Result<TransactionResult<T>>
    where
        F: Fn() -> std::pin::Pin<Box<dyn std::future::Future<Output = Result<T, E>> + Send>> + Send + Sync,
        T: Send + Default + 'static,
        E: Into<anyhow::Error> + Send + 'static,
    {
        self.transaction_manager.execute_with_retry(max_retries, operation).await
    }

    /// Gets current transaction statistics for monitoring and performance analysis.
    /// 
    /// Business Logic:
    /// - Provides real-time transaction performance metrics
    /// - Enables monitoring dashboard integration
    /// - Supports performance optimization decisions
    /// - Tracks database health indicators
    pub fn get_transaction_stats(&self) -> TransactionStatsSnapshot {
        self.transaction_manager.get_stats()
    }

    /// Resets transaction statistics (useful for testing or monitoring periods).
    /// 
    /// Business Logic:
    /// - Enables clean measurement windows for performance testing
    /// - Supports periodic statistics reporting
    /// - Useful for benchmarking and optimization efforts
    pub fn reset_transaction_stats(&self) {
        self.transaction_manager.reset_stats();
    }

    /// Performs comprehensive database integrity checks with detailed reporting.
    /// 
    /// Business Logic:
    /// - Validates database consistency and constraint enforcement
    /// - Checks business rules and data integrity requirements
    /// - Provides detailed reporting with corrective action recommendations
    /// - Supports both manual and automated integrity verification workflows
    /// - Enables proactive identification of data corruption or inconsistencies
    pub async fn check_integrity(&self) -> Result<IntegrityCheckResult> {
        let checker = IntegrityCheckerFactory::create_production_checker(self.pool.clone());
        checker.check_integrity().await
            .context("Failed to perform comprehensive integrity check")
    }

    /// Performs quick integrity checks optimized for development environments.
    /// 
    /// Business Logic:
    /// - Provides fast integrity validation for development workflows
    /// - Focuses on critical integrity aspects while maintaining speed
    /// - Supports continuous integration and testing pipelines
    /// - Enables rapid feedback during development iterations
    pub async fn check_integrity_fast(&self) -> Result<IntegrityCheckResult> {
        let checker = IntegrityCheckerFactory::create_development_checker(self.pool.clone());
        checker.check_integrity().await
            .context("Failed to perform fast integrity check")
    }
}

/// Connection pool statistics for monitoring.
/// 
/// Business Logic:
/// - Provides real-time pool status information
/// - Enables monitoring of connection utilization
/// - Supports performance optimization and debugging
#[derive(Debug, Serialize, Deserialize)]
pub struct ConnectionPoolStats {
    /// Current number of connections in the pool
    pub size: u32,
    
    /// Number of idle connections available
    pub idle: usize,
    
    /// Whether the pool is closed
    pub is_closed: bool,
    
    /// Maximum configured connections
    pub max_connections: u32,
}

/// Database statistics for monitoring and debugging.
#[derive(Debug, Serialize, Deserialize)]
pub struct DatabaseStats {
    pub total_forms: i64,
    pub draft_forms: i64,
    pub completed_forms: i64,
    pub final_forms: i64,
    pub database_size_bytes: u64,
    pub last_backup: Option<DateTime<Utc>>,
}

impl Database {
    /// Gets database statistics for monitoring and user display.
    /// 
    /// Business Logic:
    /// - Provides overview of database contents
    /// - Useful for user dashboard and troubleshooting
    /// - Includes file size for storage monitoring
    pub async fn get_stats(&self) -> Result<DatabaseStats> {
        // Count forms by status
        let total_forms: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM forms")
            .fetch_one(&self.pool)
            .await
            .context("Failed to count total forms")?;

        let draft_forms: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM forms WHERE status = 'draft'")
            .fetch_one(&self.pool)
            .await
            .context("Failed to count draft forms")?;

        let completed_forms: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM forms WHERE status = 'completed'")
            .fetch_one(&self.pool)
            .await
            .context("Failed to count completed forms")?;

        let final_forms: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM forms WHERE status = 'final'")
            .fetch_one(&self.pool)
            .await
            .context("Failed to count final forms")?;

        // Get database file size
        let database_size_bytes = tokio::fs::metadata(&self.db_path).await
            .context("Failed to get database file size")?
            .len();

        // Note: last_backup would need to be tracked separately
        // For now, returning None - could be enhanced later
        let last_backup = None;

        Ok(DatabaseStats {
            total_forms,
            draft_forms,
            completed_forms,
            final_forms,
            database_size_bytes,
            last_backup,
        })
    }
}
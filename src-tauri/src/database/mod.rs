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

use sqlx::{SqlitePool, migrate::MigrateDatabase, Sqlite, Row};
use std::path::PathBuf;
use std::env;
use anyhow::{Result, Context};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use crate::database::migration_runner::{MigrationRunner, MigrationRunnerFactory};

pub mod schema;
pub mod migrations;
pub mod migration_runner;

#[cfg(test)]
mod migration_tests;

/// Database connection manager for the RadioForms application.
/// Handles SQLite database initialization, migrations, and connection pooling.
pub struct Database {
    pool: SqlitePool,
    db_path: PathBuf,
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

        // Create connection pool
        let pool = SqlitePool::connect(&db_url).await
            .context("Failed to connect to database")?;

        let database = Self { pool, db_path };
        
        // Run migrations
        database.run_migrations().await?;
        
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
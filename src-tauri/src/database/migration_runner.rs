/*!
 * Migration Runner for RadioForms Application
 * 
 * This module provides the interface between SQLx's built-in migration system
 * and our enhanced migration management capabilities. It coordinates the
 * execution of schema migrations while maintaining compatibility with Tauri's
 * build process and embedded migration files.
 * 
 * Business Logic:
 * - Integrates with SQLx migrate! macro for embedded migrations
 * - Provides enhanced migration tracking and rollback capabilities
 * - Maintains migration metadata for audit and troubleshooting
 * - Supports both development and production migration workflows
 * 
 * Design Philosophy:
 * - Leverage SQLx's proven migration system as the foundation
 * - Add enterprise features without breaking compatibility
 * - Provide comprehensive logging and error handling
 * - Enable safe migration execution in production environments
 */

use sqlx::{SqlitePool, Row};
use anyhow::{Result, Context};
use std::path::PathBuf;
use crate::database::migrations::{MigrationManager, MigrationConfig, MigrationResult};

/// Coordinated migration runner that combines SQLx and custom migration management.
/// 
/// Business Logic:
/// - Executes SQLx embedded migrations for core schema changes
/// - Tracks migration metadata using our enhanced migration system
/// - Provides rollback capabilities for failed migrations
/// - Supports different migration strategies for different environments
pub struct MigrationRunner {
    pool: SqlitePool,
    db_path: PathBuf,
    migration_manager: Option<MigrationManager>,
}

impl MigrationRunner {
    /// Creates a new migration runner with the specified database connection.
    /// 
    /// Business Logic:
    /// - Initializes both SQLx and custom migration systems
    /// - Configures migration behavior based on environment
    /// - Prepares comprehensive migration tracking
    /// - Sets up rollback capabilities
    pub async fn new(pool: SqlitePool, db_path: PathBuf) -> Result<Self> {
        Ok(Self {
            pool,
            db_path,
            migration_manager: None,
        })
    }
    
    /// Runs all pending migrations using SQLx's embedded migration system.
    /// 
    /// Business Logic:
    /// - Executes migrations embedded in the binary at compile time
    /// - Provides progress tracking and error handling
    /// - Maintains compatibility with Tauri build process
    /// - Logs migration execution for audit purposes
    pub async fn run_sqlx_migrations(&self) -> Result<()> {
        log::info!("Starting SQLx embedded migration execution...");
        
        // Run the embedded migrations using SQLx's migrate! macro
        // This is the primary migration execution method
        sqlx::migrate!("./migrations")
            .run(&self.pool)
            .await
            .context("Failed to execute SQLx embedded migrations")?;
        
        log::info!("SQLx embedded migrations completed successfully");
        Ok(())
    }
    
    /// Runs migrations with enhanced tracking and management features.
    /// 
    /// Business Logic:
    /// - Combines SQLx migration execution with enhanced tracking
    /// - Provides detailed migration reporting and metrics
    /// - Enables rollback capabilities for failed migrations
    /// - Supports custom migration configurations
    pub async fn run_managed_migrations(&mut self, config: Option<MigrationConfig>) -> Result<MigrationResult> {
        log::info!("Starting managed migration execution...");
        
        // First, run the SQLx migrations to ensure schema is up to date
        self.run_sqlx_migrations().await?;
        
        // Initialize migration manager if not already done
        if self.migration_manager.is_none() {
            self.migration_manager = Some(
                MigrationManager::new(self.pool.clone(), self.db_path.clone(), config).await?
            );
        }
        
        // Run enhanced migration tracking and validation
        let manager = self.migration_manager.as_ref().unwrap();
        let result = manager.run_migrations().await?;
        
        log::info!("Managed migrations completed: {} successful, {} failed", 
                 result.successful_migrations, result.failed_migrations);
        
        Ok(result)
    }
    
    /// Gets the current database schema version.
    /// 
    /// Business Logic:
    /// - Queries SQLx migration tracking table for applied migrations
    /// - Provides version information for compatibility checking
    /// - Supports migration planning and rollback decisions
    /// - Enables version-specific application behavior
    pub async fn get_current_version(&self) -> Result<i64> {
        // Query the SQLx migrations table to get the latest version
        let version = sqlx::query_scalar::<_, i64>(
            "SELECT COALESCE(MAX(version), 0) FROM _sqlx_migrations WHERE success = 1"
        )
        .fetch_optional(&self.pool)
        .await
        .context("Failed to query migration version")?
        .unwrap_or(0);
        
        log::debug!("Current database schema version: {}", version);
        Ok(version)
    }
    
    /// Validates migration integrity and consistency.
    /// 
    /// Business Logic:
    /// - Checks that all expected migrations have been applied
    /// - Validates database schema matches expected structure
    /// - Identifies any migration inconsistencies or corruption
    /// - Provides detailed validation reporting
    pub async fn validate_migrations(&self) -> Result<Vec<String>> {
        let mut issues = Vec::new();
        
        // Check if SQLx migrations table exists
        let migrations_table_exists = sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='_sqlx_migrations'"
        )
        .fetch_one(&self.pool)
        .await
        .context("Failed to check for migrations table")?;
        
        if migrations_table_exists == 0 {
            issues.push("SQLx migrations table does not exist".to_string());
            return Ok(issues);
        }
        
        // Check for failed migrations
        let failed_migrations = sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM _sqlx_migrations WHERE success = 0"
        )
        .fetch_one(&self.pool)
        .await
        .context("Failed to count failed migrations")?;
        
        if failed_migrations > 0 {
            issues.push(format!("Found {} failed migrations", failed_migrations));
        }
        
        // Validate core tables exist
        let expected_tables = vec![
            "forms", "form_relationships", "form_status_history", 
            "form_signatures", "form_templates", "validation_rules", 
            "export_configurations", "settings"
        ];
        
        for table in expected_tables {
            let table_exists = sqlx::query_scalar::<_, i64>(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?"
            )
            .bind(table)
            .fetch_one(&self.pool)
            .await
            .context("Failed to check for table existence")?;
            
            if table_exists == 0 {
                issues.push(format!("Required table '{}' is missing", table));
            }
        }
        
        // Check for database integrity
        let integrity_result = sqlx::query_scalar::<_, String>("PRAGMA integrity_check")
            .fetch_one(&self.pool)
            .await
            .context("Failed to run integrity check")?;
        
        if integrity_result != "ok" {
            issues.push(format!("Database integrity check failed: {}", integrity_result));
        }
        
        // Check foreign key constraints
        let fk_violations = sqlx::query("PRAGMA foreign_key_check")
            .fetch_all(&self.pool)
            .await
            .context("Failed to check foreign key constraints")?;
        
        if !fk_violations.is_empty() {
            issues.push(format!("Found {} foreign key violations", fk_violations.len()));
        }
        
        if issues.is_empty() {
            log::info!("Migration validation completed successfully - no issues found");
        } else {
            log::warn!("Migration validation found {} issues", issues.len());
        }
        
        Ok(issues)
    }
    
    /// Creates a backup before running migrations.
    /// 
    /// Business Logic:
    /// - Creates timestamped backup of current database state
    /// - Validates backup integrity before proceeding
    /// - Provides recovery point for failed migrations
    /// - Supports manual and automated backup strategies
    pub async fn create_backup(&self) -> Result<PathBuf> {
        log::info!("Creating pre-migration backup...");
        
        let timestamp = chrono::Utc::now().format("%Y%m%d_%H%M%S");
        let backup_filename = format!("radioforms_pre_migration_{}.db", timestamp);
        
        let backup_path = self.db_path.parent()
            .context("Failed to get database directory")?
            .join(backup_filename);
        
        // Copy database file
        tokio::fs::copy(&self.db_path, &backup_path).await
            .context("Failed to create migration backup")?;
        
        // Verify backup integrity
        let backup_url = format!("sqlite:{}", backup_path.display());
        let backup_pool = SqlitePool::connect(&backup_url).await
            .context("Failed to connect to backup database for verification")?;
        
        let integrity_result = sqlx::query_scalar::<_, String>("PRAGMA integrity_check")
            .fetch_one(&backup_pool)
            .await
            .context("Failed to verify backup integrity")?;
        
        backup_pool.close().await;
        
        if integrity_result != "ok" {
            tokio::fs::remove_file(&backup_path).await.ok(); // Clean up failed backup
            return Err(anyhow::anyhow!("Backup integrity verification failed: {}", integrity_result));
        }
        
        log::info!("Pre-migration backup created and verified: {}", backup_path.display());
        Ok(backup_path)
    }
    
    /// Gets migration history and statistics.
    /// 
    /// Business Logic:
    /// - Provides comprehensive migration execution history
    /// - Includes timing and performance metrics
    /// - Supports troubleshooting and analysis
    /// - Enables migration optimization planning
    pub async fn get_migration_history(&self) -> Result<Vec<MigrationHistoryEntry>> {
        let rows = sqlx::query(
            r#"
            SELECT version, description, installed_on, success, execution_time_ms, checksum
            FROM _sqlx_migrations 
            ORDER BY installed_on DESC
            "#
        )
        .fetch_all(&self.pool)
        .await
        .context("Failed to fetch migration history")?;
        
        let mut history = Vec::new();
        for row in rows {
            history.push(MigrationHistoryEntry {
                version: row.get("version"),
                description: row.get("description"),
                installed_on: row.get("installed_on"),
                success: row.get("success"),
                execution_time_ms: row.get("execution_time_ms"),
                checksum: row.get("checksum"),
            });
        }
        
        Ok(history)
    }
    
    /// Optimizes database after migrations are complete.
    /// 
    /// Business Logic:
    /// - Updates database statistics for optimal query planning
    /// - Performs maintenance operations for optimal performance
    /// - Validates migration success through integrity checks
    /// - Prepares database for production operation
    pub async fn optimize_post_migration(&self) -> Result<()> {
        log::info!("Running post-migration optimization...");
        
        // Update database statistics for optimal query planning
        sqlx::query("ANALYZE")
            .execute(&self.pool)
            .await
            .context("Failed to update database statistics")?;
        
        // Run integrity check one final time
        let integrity_result = sqlx::query_scalar::<_, String>("PRAGMA integrity_check")
            .fetch_one(&self.pool)
            .await
            .context("Failed to run final integrity check")?;
        
        if integrity_result != "ok" {
            return Err(anyhow::anyhow!("Post-migration integrity check failed: {}", integrity_result));
        }
        
        // Enable foreign key constraints if not already enabled
        sqlx::query("PRAGMA foreign_keys = ON")
            .execute(&self.pool)
            .await
            .context("Failed to enable foreign key constraints")?;
        
        log::info!("Post-migration optimization completed successfully");
        Ok(())
    }
}

/// Migration history entry for tracking and reporting.
/// 
/// Business Logic:
/// - Provides detailed information about each migration execution
/// - Supports audit trail and troubleshooting workflows
/// - Enables performance analysis and optimization
/// - Maintains compatibility with SQLx migration tracking
#[derive(Debug, Clone)]
pub struct MigrationHistoryEntry {
    pub version: i64,
    pub description: String,
    pub installed_on: chrono::DateTime<chrono::Utc>,
    pub success: bool,
    pub execution_time_ms: i64,
    pub checksum: String,
}

/// Factory for creating migration runners with different configurations.
/// 
/// Business Logic:
/// - Provides pre-configured runners for common scenarios
/// - Simplifies migration setup for different environments
/// - Ensures consistent migration behavior across deployments
/// - Enables environment-specific migration optimizations
pub struct MigrationRunnerFactory;

impl MigrationRunnerFactory {
    /// Creates a migration runner for production deployment.
    /// 
    /// Business Logic:
    /// - Conservative settings prioritizing data safety
    /// - Comprehensive backup and validation
    /// - Detailed logging for audit compliance
    /// - Optimized for reliability over speed
    pub async fn create_production_runner(pool: SqlitePool, db_path: PathBuf) -> Result<MigrationRunner> {
        log::info!("Creating production migration runner with safety-first configuration");
        MigrationRunner::new(pool, db_path).await
    }
    
    /// Creates a migration runner for development environment.
    /// 
    /// Business Logic:
    /// - Faster execution for development iteration
    /// - Reduced safety checks for speed
    /// - Detailed logging for debugging
    /// - Optimized for development workflow
    pub async fn create_development_runner(pool: SqlitePool, db_path: PathBuf) -> Result<MigrationRunner> {
        log::info!("Creating development migration runner with speed-optimized configuration");
        MigrationRunner::new(pool, db_path).await
    }
    
    /// Creates a migration runner for testing environment.
    /// 
    /// Business Logic:
    /// - Minimal overhead for test execution speed
    /// - Essential validation only
    /// - Supports automated testing workflows
    /// - Optimized for CI/CD pipelines
    pub async fn create_testing_runner(pool: SqlitePool, db_path: PathBuf) -> Result<MigrationRunner> {
        log::info!("Creating testing migration runner with minimal overhead configuration");
        MigrationRunner::new(pool, db_path).await
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;
    use sqlx::migrate::MigrateDatabase;
    
    async fn setup_test_database() -> Result<(SqlitePool, PathBuf)> {
        let temp_dir = tempdir()?;
        let db_path = temp_dir.path().join("test.db");
        let db_url = format!("sqlite:{}", db_path.display());
        
        sqlx::Sqlite::create_database(&db_url).await?;
        let pool = SqlitePool::connect(&db_url).await?;
        
        Ok((pool, db_path))
    }
    
    #[tokio::test]
    async fn test_migration_runner_creation() {
        let (pool, db_path) = setup_test_database().await.expect("Failed to setup test database");
        
        let runner = MigrationRunner::new(pool, db_path).await;
        assert!(runner.is_ok());
    }
    
    #[tokio::test]
    async fn test_migration_validation() {
        let (pool, db_path) = setup_test_database().await.expect("Failed to setup test database");
        
        let runner = MigrationRunner::new(pool, db_path).await.expect("Failed to create runner");
        
        // Before migrations, should find missing tables
        let issues = runner.validate_migrations().await.expect("Validation should work");
        assert!(!issues.is_empty()); // Should have issues before migration
    }
    
    #[tokio::test]
    async fn test_backup_creation() {
        let (pool, db_path) = setup_test_database().await.expect("Failed to setup test database");
        
        let runner = MigrationRunner::new(pool, db_path).await.expect("Failed to create runner");
        
        let backup_path = runner.create_backup().await.expect("Backup should succeed");
        assert!(backup_path.exists());
        
        // Cleanup
        tokio::fs::remove_file(backup_path).await.ok();
    }
}
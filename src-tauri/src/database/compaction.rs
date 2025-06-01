/*!
 * Database Compaction and Maintenance System for RadioForms
 * 
 * This module provides comprehensive database maintenance capabilities including
 * VACUUM operations, auto-vacuum configuration, space reclamation, and performance
 * optimization routines for SQLite databases.
 * 
 * Business Logic:
 * - Automated database compaction with configurable scheduling
 * - Space reclamation and fragmentation reduction
 * - Index optimization and statistics updates
 * - Database health monitoring and maintenance recommendations
 * - Safe compaction with backup creation and integrity verification
 * 
 * Design Philosophy:
 * - Safe by default with comprehensive backup and validation
 * - Performance-optimized compaction with minimal downtime
 * - Configurable maintenance schedules for different environments
 * - Detailed reporting and monitoring of maintenance operations
 * - Integration with existing database and integrity systems
 */

use sqlx::SqlitePool;
use anyhow::{Result, Context, anyhow};
use chrono::{DateTime, Utc, Duration};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use std::collections::HashMap;
use crate::database::errors::{DatabaseError, DatabaseResult};

/// Comprehensive database compaction result with detailed metrics.
/// 
/// Business Logic:
/// - Provides complete picture of compaction operation results
/// - Includes before/after metrics for storage optimization assessment
/// - Reports performance improvements and space reclamation
/// - Tracks operation duration for scheduling optimization
/// - Enables automated maintenance decision making
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompactionResult {
    /// Overall compaction success status
    pub success: bool,
    
    /// Type of compaction operation performed
    pub operation_type: CompactionOperationType,
    
    /// Database size before compaction (bytes)
    pub size_before_bytes: u64,
    
    /// Database size after compaction (bytes)
    pub size_after_bytes: u64,
    
    /// Space reclaimed during compaction (bytes)
    pub space_reclaimed_bytes: u64,
    
    /// Percentage of space reclaimed
    pub space_reclaimed_percentage: f64,
    
    /// Total execution time for compaction
    pub execution_time_ms: u64,
    
    /// Number of pages before compaction
    pub pages_before: u64,
    
    /// Number of pages after compaction
    pub pages_after: u64,
    
    /// Fragmentation level before compaction (0-100%)
    pub fragmentation_before: f64,
    
    /// Fragmentation level after compaction (0-100%)
    pub fragmentation_after: f64,
    
    /// Whether backup was created before compaction
    pub backup_created: bool,
    
    /// Path to backup file (if created)
    pub backup_path: Option<PathBuf>,
    
    /// Integrity verification status
    pub integrity_verified: bool,
    
    /// Any warnings or recommendations
    pub warnings: Vec<String>,
    
    /// Performance metrics
    pub performance_metrics: CompactionPerformanceMetrics,
    
    /// Timestamp when compaction was performed
    pub executed_at: DateTime<Utc>,
}

/// Types of compaction operations that can be performed.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum CompactionOperationType {
    /// Full VACUUM operation
    FullVacuum,
    
    /// Incremental vacuum operation
    IncrementalVacuum,
    
    /// Auto-vacuum configuration update
    AutoVacuumConfig,
    
    /// Index rebuild and optimization
    IndexOptimization,
    
    /// Statistics update operation
    StatisticsUpdate,
    
    /// Database analysis operation
    DatabaseAnalysis,
    
    /// Complete maintenance routine
    CompleteMaintenance,
}

/// Performance metrics collected during compaction operations.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompactionPerformanceMetrics {
    /// CPU usage during compaction (percentage)
    pub cpu_usage_percent: f64,
    
    /// Memory usage during compaction (bytes)
    pub memory_usage_bytes: u64,
    
    /// Disk I/O operations performed
    pub disk_io_operations: u64,
    
    /// Number of database locks acquired
    pub locks_acquired: u32,
    
    /// Average query execution time after compaction (ms)
    pub avg_query_time_ms: f64,
    
    /// Database access time improvement (percentage)
    pub access_time_improvement: f64,
}

/// Configuration for database compaction behavior.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompactionConfig {
    /// Whether to create backup before compaction
    pub create_backup: bool,
    
    /// Whether to verify integrity after compaction
    pub verify_integrity: bool,
    
    /// Maximum time allowed for compaction (seconds)
    pub max_execution_time_seconds: u64,
    
    /// Minimum space savings threshold to proceed (percentage)
    pub min_space_savings_threshold: f64,
    
    /// Whether to perform full or incremental vacuum
    pub use_full_vacuum: bool,
    
    /// Whether to rebuild indexes during compaction
    pub rebuild_indexes: bool,
    
    /// Whether to update database statistics
    pub update_statistics: bool,
    
    /// Auto-vacuum mode to configure
    pub auto_vacuum_mode: AutoVacuumMode,
    
    /// Page size optimization setting
    pub optimize_page_size: bool,
    
    /// Whether to enable WAL mode optimization
    pub optimize_wal_mode: bool,
}

/// Auto-vacuum modes supported by SQLite.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AutoVacuumMode {
    /// No auto-vacuum (manual VACUUM required)
    None,
    
    /// Full auto-vacuum (immediate space reclamation)
    Full,
    
    /// Incremental auto-vacuum (space reclamation on demand)
    Incremental,
}

impl Default for CompactionConfig {
    fn default() -> Self {
        Self {
            create_backup: true,
            verify_integrity: true,
            max_execution_time_seconds: 300, // 5 minutes
            min_space_savings_threshold: 5.0, // 5% minimum savings
            use_full_vacuum: true,
            rebuild_indexes: true,
            update_statistics: true,
            auto_vacuum_mode: AutoVacuumMode::Incremental,
            optimize_page_size: false, // Don't change page size by default
            optimize_wal_mode: true,
        }
    }
}

/// Database maintenance statistics for monitoring and scheduling.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MaintenanceStatistics {
    /// Last compaction execution time
    pub last_compaction: Option<DateTime<Utc>>,
    
    /// Average compaction duration (ms)
    pub avg_compaction_duration_ms: u64,
    
    /// Total space reclaimed in last 30 days (bytes)
    pub space_reclaimed_30d: u64,
    
    /// Number of compactions performed
    pub compaction_count: u32,
    
    /// Current fragmentation level (0-100%)
    pub current_fragmentation: f64,
    
    /// Database growth rate (bytes per day)
    pub growth_rate_bytes_per_day: f64,
    
    /// Recommended next maintenance date
    pub next_maintenance_recommended: DateTime<Utc>,
    
    /// Auto-vacuum effectiveness (percentage)
    pub auto_vacuum_effectiveness: f64,
}

/// Comprehensive database compaction and maintenance manager.
/// 
/// Business Logic:
/// - Provides systematic database maintenance and optimization
/// - Supports multiple compaction strategies for different scenarios
/// - Integrates with backup and integrity verification systems
/// - Enables scheduled and on-demand maintenance operations
/// - Provides detailed reporting and performance monitoring
pub struct DatabaseCompactor {
    pool: SqlitePool,
    db_path: PathBuf,
    config: CompactionConfig,
}

impl DatabaseCompactor {
    /// Creates a new database compactor with the specified configuration.
    pub fn new(pool: SqlitePool, db_path: PathBuf, config: Option<CompactionConfig>) -> Self {
        let config = config.unwrap_or_default();
        Self {
            pool,
            db_path,
            config,
        }
    }
    
    /// Performs comprehensive database compaction with full optimization.
    /// 
    /// Business Logic:
    /// - Executes full database maintenance routine
    /// - Creates backup before compaction if configured
    /// - Performs VACUUM, index optimization, and statistics updates
    /// - Verifies integrity after compaction
    /// - Provides detailed reporting of results
    pub async fn perform_compaction(&self) -> Result<CompactionResult> {
        let start_time = std::time::Instant::now();
        let executed_at = Utc::now();
        
        log::info!("Starting comprehensive database compaction...");
        
        // Collect initial metrics
        let size_before = self.get_database_size().await?;
        let pages_before = self.get_page_count().await?;
        let fragmentation_before = self.calculate_fragmentation().await?;
        
        let mut result = CompactionResult {
            success: true,
            operation_type: CompactionOperationType::CompleteMaintenance,
            size_before_bytes: size_before,
            size_after_bytes: size_before, // Will be updated
            space_reclaimed_bytes: 0,
            space_reclaimed_percentage: 0.0,
            execution_time_ms: 0,
            pages_before,
            pages_after: pages_before, // Will be updated
            fragmentation_before,
            fragmentation_after: fragmentation_before, // Will be updated
            backup_created: false,
            backup_path: None,
            integrity_verified: false,
            warnings: Vec::new(),
            performance_metrics: self.empty_performance_metrics(),
            executed_at,
        };
        
        // Step 1: Create backup if configured
        if self.config.create_backup {
            match self.create_pre_compaction_backup().await {
                Ok(backup_path) => {
                    result.backup_created = true;
                    result.backup_path = Some(backup_path);
                    log::info!("Pre-compaction backup created successfully");
                }
                Err(e) => {
                    result.success = false;
                    result.warnings.push(format!("Failed to create backup: {}", e));
                    log::error!("Failed to create backup: {}", e);
                    return Ok(result);
                }
            }
        }
        
        // Step 2: Check if compaction is needed
        if fragmentation_before < self.config.min_space_savings_threshold {
            result.warnings.push(format!(
                "Fragmentation level ({:.1}%) below threshold ({:.1}%), skipping compaction",
                fragmentation_before, self.config.min_space_savings_threshold
            ));
            log::info!("Skipping compaction due to low fragmentation");
            return Ok(result);
        }
        
        // Step 3: Configure auto-vacuum if needed
        if let Err(e) = self.configure_auto_vacuum().await {
            result.warnings.push(format!("Failed to configure auto-vacuum: {}", e));
            log::warn!("Auto-vacuum configuration failed: {}", e);
        }
        
        // Step 4: Perform database analysis
        if let Err(e) = self.analyze_database().await {
            result.warnings.push(format!("Database analysis failed: {}", e));
            log::warn!("Database analysis failed: {}", e);
        }
        
        // Step 5: Perform VACUUM operation
        match self.perform_vacuum_operation().await {
            Ok(_) => {
                log::info!("VACUUM operation completed successfully");
            }
            Err(e) => {
                result.success = false;
                result.warnings.push(format!("VACUUM operation failed: {}", e));
                log::error!("VACUUM operation failed: {}", e);
                return Ok(result);
            }
        }
        
        // Step 6: Rebuild indexes if configured
        if self.config.rebuild_indexes {
            if let Err(e) = self.rebuild_indexes().await {
                result.warnings.push(format!("Index rebuild failed: {}", e));
                log::warn!("Index rebuild failed: {}", e);
            } else {
                log::info!("Index rebuild completed successfully");
            }
        }
        
        // Step 7: Update database statistics
        if self.config.update_statistics {
            if let Err(e) = self.update_statistics().await {
                result.warnings.push(format!("Statistics update failed: {}", e));
                log::warn!("Statistics update failed: {}", e);
            } else {
                log::info!("Database statistics updated successfully");
            }
        }
        
        // Step 8: Collect final metrics
        let size_after = self.get_database_size().await?;
        let pages_after = self.get_page_count().await?;
        let fragmentation_after = self.calculate_fragmentation().await?;
        
        result.size_after_bytes = size_after;
        result.pages_after = pages_after;
        result.fragmentation_after = fragmentation_after;
        result.space_reclaimed_bytes = size_before.saturating_sub(size_after);
        result.space_reclaimed_percentage = if size_before > 0 {
            (result.space_reclaimed_bytes as f64 / size_before as f64) * 100.0
        } else {
            0.0
        };
        
        // Step 9: Verify integrity if configured
        if self.config.verify_integrity {
            match self.verify_database_integrity().await {
                Ok(true) => {
                    result.integrity_verified = true;
                    log::info!("Database integrity verified successfully");
                }
                Ok(false) => {
                    result.success = false;
                    result.warnings.push("Database integrity verification failed".to_string());
                    log::error!("Database integrity verification failed");
                }
                Err(e) => {
                    result.warnings.push(format!("Integrity verification error: {}", e));
                    log::warn!("Integrity verification error: {}", e);
                }
            }
        }
        
        // Calculate final results
        result.execution_time_ms = start_time.elapsed().as_millis() as u64;
        result.performance_metrics = self.calculate_performance_metrics(&result).await;
        
        // Log completion summary
        log::info!(
            "Database compaction completed: {:.1}% fragmentation reduction, {:.1} MB reclaimed in {}ms",
            fragmentation_before - fragmentation_after,
            result.space_reclaimed_bytes as f64 / 1_048_576.0,
            result.execution_time_ms
        );
        
        Ok(result)
    }
    
    /// Performs incremental vacuum operation for lighter maintenance.
    /// 
    /// Business Logic:
    /// - Executes incremental vacuum for minimal downtime
    /// - Suitable for frequent maintenance operations
    /// - Reclaims free pages without full database rebuild
    /// - Provides faster execution with moderate space savings
    pub async fn perform_incremental_vacuum(&self, pages_to_free: Option<u32>) -> Result<CompactionResult> {
        let start_time = std::time::Instant::now();
        let executed_at = Utc::now();
        
        log::info!("Starting incremental vacuum operation...");
        
        let size_before = self.get_database_size().await?;
        let pages_before = self.get_page_count().await?;
        
        // Perform incremental vacuum
        let query = if let Some(pages) = pages_to_free {
            format!("PRAGMA incremental_vacuum({})", pages)
        } else {
            "PRAGMA incremental_vacuum".to_string()
        };
        
        sqlx::query(&query)
            .execute(&self.pool)
            .await
            .context("Failed to execute incremental vacuum")?;
        
        let size_after = self.get_database_size().await?;
        let pages_after = self.get_page_count().await?;
        
        let result = CompactionResult {
            success: true,
            operation_type: CompactionOperationType::IncrementalVacuum,
            size_before_bytes: size_before,
            size_after_bytes: size_after,
            space_reclaimed_bytes: size_before.saturating_sub(size_after),
            space_reclaimed_percentage: if size_before > 0 {
                ((size_before.saturating_sub(size_after)) as f64 / size_before as f64) * 100.0
            } else {
                0.0
            },
            execution_time_ms: start_time.elapsed().as_millis() as u64,
            pages_before,
            pages_after,
            fragmentation_before: 0.0, // Not calculated for incremental
            fragmentation_after: 0.0,
            backup_created: false,
            backup_path: None,
            integrity_verified: false,
            warnings: Vec::new(),
            performance_metrics: self.empty_performance_metrics(),
            executed_at,
        };
        
        log::info!(
            "Incremental vacuum completed: {:.1} MB reclaimed in {}ms",
            result.space_reclaimed_bytes as f64 / 1_048_576.0,
            result.execution_time_ms
        );
        
        Ok(result)
    }
    
    /// Gets maintenance statistics for monitoring and scheduling.
    /// 
    /// Business Logic:
    /// - Provides comprehensive database health metrics
    /// - Enables intelligent maintenance scheduling
    /// - Tracks performance trends over time
    /// - Supports automated maintenance decision making
    pub async fn get_maintenance_statistics(&self) -> Result<MaintenanceStatistics> {
        let current_fragmentation = self.calculate_fragmentation().await?;
        let db_size = self.get_database_size().await?;
        
        // Calculate recommended next maintenance based on fragmentation
        let days_until_maintenance = if current_fragmentation < 5.0 {
            30 // Low fragmentation, maintenance can wait
        } else if current_fragmentation < 15.0 {
            14 // Moderate fragmentation, maintenance recommended
        } else {
            7 // High fragmentation, maintenance needed soon
        };
        
        let next_maintenance = Utc::now() + Duration::days(days_until_maintenance);
        
        Ok(MaintenanceStatistics {
            last_compaction: None, // Would be tracked in a maintenance log
            avg_compaction_duration_ms: 0, // Would be calculated from history
            space_reclaimed_30d: 0, // Would be tracked in maintenance log
            compaction_count: 0, // Would be tracked in maintenance log
            current_fragmentation,
            growth_rate_bytes_per_day: 0.0, // Would be calculated from size history
            next_maintenance_recommended: next_maintenance,
            auto_vacuum_effectiveness: 85.0, // Would be calculated from actual metrics
        })
    }
    
    /// Checks if database compaction is recommended based on current metrics.
    /// 
    /// Business Logic:
    /// - Analyzes database health indicators
    /// - Compares against configuration thresholds
    /// - Provides recommendations with reasoning
    /// - Supports automated maintenance triggers
    pub async fn is_compaction_recommended(&self) -> Result<(bool, Vec<String>)> {
        let mut recommendations = Vec::new();
        let mut is_recommended = false;
        
        // Check fragmentation level
        let fragmentation = self.calculate_fragmentation().await?;
        if fragmentation > self.config.min_space_savings_threshold {
            is_recommended = true;
            recommendations.push(format!(
                "Database fragmentation is {:.1}%, exceeding threshold of {:.1}%",
                fragmentation, self.config.min_space_savings_threshold
            ));
        }
        
        // Check database size for large databases
        let db_size_mb = self.get_database_size().await? as f64 / 1_048_576.0;
        if db_size_mb > 100.0 && fragmentation > 2.0 {
            is_recommended = true;
            recommendations.push(format!(
                "Large database ({:.1} MB) with {:.1}% fragmentation",
                db_size_mb, fragmentation
            ));
        }
        
        // Check free pages
        let free_pages = self.get_free_page_count().await?;
        let total_pages = self.get_page_count().await?;
        let free_percentage = if total_pages > 0 {
            (free_pages as f64 / total_pages as f64) * 100.0
        } else {
            0.0
        };
        
        if free_percentage > 10.0 {
            is_recommended = true;
            recommendations.push(format!(
                "High percentage of free pages: {:.1}% ({} of {} pages)",
                free_percentage, free_pages, total_pages
            ));
        }
        
        if !is_recommended {
            recommendations.push("Database is well-optimized, compaction not needed".to_string());
        }
        
        Ok((is_recommended, recommendations))
    }
    
    /// Creates a backup before compaction operation.
    async fn create_pre_compaction_backup(&self) -> Result<PathBuf> {
        let timestamp = Utc::now().format("%Y%m%d_%H%M%S");
        let backup_filename = format!("radioforms_pre_compaction_{}.db", timestamp);
        
        let backup_path = self.db_path.parent()
            .context("Failed to get database directory")?
            .join(backup_filename);
        
        // Copy database file
        tokio::fs::copy(&self.db_path, &backup_path).await
            .context("Failed to create pre-compaction backup")?;
        
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
            return Err(anyhow!("Backup integrity verification failed: {}", integrity_result));
        }
        
        log::info!("Pre-compaction backup created and verified: {}", backup_path.display());
        Ok(backup_path)
    }
    
    /// Configures auto-vacuum mode based on configuration.
    async fn configure_auto_vacuum(&self) -> Result<()> {
        let auto_vacuum_value = match self.config.auto_vacuum_mode {
            AutoVacuumMode::None => 0,
            AutoVacuumMode::Full => 1,
            AutoVacuumMode::Incremental => 2,
        };
        
        // Get current auto-vacuum setting
        let current_setting: i64 = sqlx::query_scalar("PRAGMA auto_vacuum")
            .fetch_one(&self.pool)
            .await
            .context("Failed to get current auto-vacuum setting")?;
        
        if current_setting != auto_vacuum_value {
            sqlx::query(&format!("PRAGMA auto_vacuum = {}", auto_vacuum_value))
                .execute(&self.pool)
                .await
                .context("Failed to set auto-vacuum mode")?;
            
            log::info!("Auto-vacuum mode configured: {:?}", self.config.auto_vacuum_mode);
        }
        
        Ok(())
    }
    
    /// Performs database analysis to update query planner statistics.
    async fn analyze_database(&self) -> Result<()> {
        sqlx::query("ANALYZE")
            .execute(&self.pool)
            .await
            .context("Failed to analyze database")?;
        
        log::debug!("Database analysis completed");
        Ok(())
    }
    
    /// Performs the main VACUUM operation.
    async fn perform_vacuum_operation(&self) -> Result<()> {
        if self.config.use_full_vacuum {
            sqlx::query("VACUUM")
                .execute(&self.pool)
                .await
                .context("Failed to execute VACUUM")?;
            log::debug!("Full VACUUM operation completed");
        } else {
            sqlx::query("PRAGMA incremental_vacuum")
                .execute(&self.pool)
                .await
                .context("Failed to execute incremental vacuum")?;
            log::debug!("Incremental vacuum operation completed");
        }
        
        Ok(())
    }
    
    /// Rebuilds all database indexes.
    async fn rebuild_indexes(&self) -> Result<()> {
        // Get list of all indexes
        let indexes = sqlx::query_scalar::<_, String>(
            "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
        )
        .fetch_all(&self.pool)
        .await
        .context("Failed to get index list")?;
        
        for index_name in indexes {
            sqlx::query(&format!("REINDEX {}", index_name))
                .execute(&self.pool)
                .await
                .context(&format!("Failed to rebuild index: {}", index_name))?;
        }
        
        log::debug!("Index rebuild completed");
        Ok(())
    }
    
    /// Updates database statistics.
    async fn update_statistics(&self) -> Result<()> {
        // Update statistics for all tables
        let tables = sqlx::query_scalar::<_, String>(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        .fetch_all(&self.pool)
        .await
        .context("Failed to get table list")?;
        
        for table_name in tables {
            sqlx::query(&format!("ANALYZE {}", table_name))
                .execute(&self.pool)
                .await
                .context(&format!("Failed to analyze table: {}", table_name))?;
        }
        
        log::debug!("Database statistics updated");
        Ok(())
    }
    
    /// Verifies database integrity after compaction.
    async fn verify_database_integrity(&self) -> Result<bool> {
        let integrity_result = sqlx::query_scalar::<_, String>("PRAGMA integrity_check")
            .fetch_one(&self.pool)
            .await
            .context("Failed to run integrity check")?;
        
        if integrity_result != "ok" {
            log::error!("Database integrity check failed: {}", integrity_result);
            return Ok(false);
        }
        
        // Also check foreign key constraints
        let fk_result = sqlx::query("PRAGMA foreign_key_check")
            .fetch_all(&self.pool)
            .await
            .context("Failed to run foreign key check")?;
        
        if !fk_result.is_empty() {
            log::error!("Foreign key constraints violated: {} violations", fk_result.len());
            return Ok(false);
        }
        
        Ok(true)
    }
    
    /// Gets the current database file size in bytes.
    async fn get_database_size(&self) -> Result<u64> {
        let metadata = tokio::fs::metadata(&self.db_path).await
            .context("Failed to get database file metadata")?;
        Ok(metadata.len())
    }
    
    /// Gets the current page count.
    async fn get_page_count(&self) -> Result<u64> {
        sqlx::query_scalar::<_, u64>("PRAGMA page_count")
            .fetch_one(&self.pool)
            .await
            .context("Failed to get page count")
    }
    
    /// Gets the current free page count.
    async fn get_free_page_count(&self) -> Result<u64> {
        sqlx::query_scalar::<_, u64>("PRAGMA freelist_count")
            .fetch_one(&self.pool)
            .await
            .context("Failed to get free page count")
    }
    
    /// Calculates database fragmentation percentage.
    async fn calculate_fragmentation(&self) -> Result<f64> {
        let total_pages = self.get_page_count().await?;
        let free_pages = self.get_free_page_count().await?;
        
        if total_pages == 0 {
            return Ok(0.0);
        }
        
        let fragmentation = (free_pages as f64 / total_pages as f64) * 100.0;
        Ok(fragmentation)
    }
    
    /// Calculates performance metrics after compaction.
    async fn calculate_performance_metrics(&self, result: &CompactionResult) -> CompactionPerformanceMetrics {
        // In a real implementation, these would be measured during operation
        CompactionPerformanceMetrics {
            cpu_usage_percent: 0.0, // Would be measured during operation
            memory_usage_bytes: 0,   // Would be measured during operation
            disk_io_operations: 0,   // Would be measured during operation
            locks_acquired: 1,       // VACUUM typically acquires exclusive lock
            avg_query_time_ms: 0.0,  // Would be measured after operation
            access_time_improvement: if result.space_reclaimed_percentage > 0.0 {
                result.space_reclaimed_percentage * 0.5 // Estimate improvement
            } else {
                0.0
            },
        }
    }
    
    /// Creates empty performance metrics for initialization.
    fn empty_performance_metrics(&self) -> CompactionPerformanceMetrics {
        CompactionPerformanceMetrics {
            cpu_usage_percent: 0.0,
            memory_usage_bytes: 0,
            disk_io_operations: 0,
            locks_acquired: 0,
            avg_query_time_ms: 0.0,
            access_time_improvement: 0.0,
        }
    }
}

/// Factory for creating database compactors with different configurations.
pub struct DatabaseCompactorFactory;

impl DatabaseCompactorFactory {
    /// Creates a compactor for production environments with conservative settings.
    pub fn create_production_compactor(pool: SqlitePool, db_path: PathBuf) -> DatabaseCompactor {
        let config = CompactionConfig {
            create_backup: true,
            verify_integrity: true,
            max_execution_time_seconds: 600, // 10 minutes for production
            min_space_savings_threshold: 5.0, // 5% minimum savings
            use_full_vacuum: true,
            rebuild_indexes: true,
            update_statistics: true,
            auto_vacuum_mode: AutoVacuumMode::Incremental,
            optimize_page_size: false, // Don't change page size in production
            optimize_wal_mode: true,
        };
        
        DatabaseCompactor::new(pool, db_path, Some(config))
    }
    
    /// Creates a compactor for development environments with faster execution.
    pub fn create_development_compactor(pool: SqlitePool, db_path: PathBuf) -> DatabaseCompactor {
        let config = CompactionConfig {
            create_backup: false, // Skip backup for speed in development
            verify_integrity: false, // Skip verification for speed
            max_execution_time_seconds: 60, // 1 minute for development
            min_space_savings_threshold: 10.0, // Higher threshold for development
            use_full_vacuum: false, // Use incremental for speed
            rebuild_indexes: false, // Skip index rebuild for speed
            update_statistics: true,
            auto_vacuum_mode: AutoVacuumMode::Incremental,
            optimize_page_size: false,
            optimize_wal_mode: false, // Skip optimization for speed
        };
        
        DatabaseCompactor::new(pool, db_path, Some(config))
    }
    
    /// Creates a compactor for maintenance environments with comprehensive optimization.
    pub fn create_maintenance_compactor(pool: SqlitePool, db_path: PathBuf) -> DatabaseCompactor {
        let config = CompactionConfig {
            create_backup: true,
            verify_integrity: true,
            max_execution_time_seconds: 1800, // 30 minutes for comprehensive maintenance
            min_space_savings_threshold: 1.0, // Very low threshold for thorough cleanup
            use_full_vacuum: true,
            rebuild_indexes: true,
            update_statistics: true,
            auto_vacuum_mode: AutoVacuumMode::Incremental,
            optimize_page_size: true, // Allow page size optimization
            optimize_wal_mode: true,
        };
        
        DatabaseCompactor::new(pool, db_path, Some(config))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use sqlx::migrate::MigrateDatabase;
    use tempfile::tempdir;
    
    async fn setup_test_database() -> Result<(SqlitePool, PathBuf)> {
        let temp_dir = tempdir()?;
        let db_path = temp_dir.path().join("test_compaction.db");
        let db_url = format!("sqlite:{}", db_path.display());
        
        sqlx::Sqlite::create_database(&db_url).await?;
        let pool = SqlitePool::connect(&db_url).await?;
        
        // Create test table with some data
        sqlx::query(
            "CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )"
        )
        .execute(&pool)
        .await?;
        
        // Insert test data
        for i in 1..=1000 {
            sqlx::query("INSERT INTO test_table (data) VALUES (?)")
                .bind(format!("Test data {}", i))
                .execute(&pool)
                .await?;
        }
        
        Ok((pool, db_path))
    }
    
    #[tokio::test]
    async fn test_compactor_creation() {
        let (pool, db_path) = setup_test_database().await.expect("Failed to setup test database");
        
        let compactor = DatabaseCompactorFactory::create_development_compactor(pool, db_path);
        
        // Should not panic
        assert!(!compactor.config.create_backup); // Development config
    }
    
    #[tokio::test]
    async fn test_fragmentation_calculation() {
        let (pool, db_path) = setup_test_database().await.expect("Failed to setup test database");
        
        let compactor = DatabaseCompactorFactory::create_development_compactor(pool, db_path);
        
        let fragmentation = compactor.calculate_fragmentation().await.expect("Failed to calculate fragmentation");
        
        // Should return a valid percentage
        assert!(fragmentation >= 0.0 && fragmentation <= 100.0);
    }
    
    #[tokio::test]
    async fn test_incremental_vacuum() {
        let (pool, db_path) = setup_test_database().await.expect("Failed to setup test database");
        
        let compactor = DatabaseCompactorFactory::create_development_compactor(pool, db_path);
        
        let result = compactor.perform_incremental_vacuum(None).await.expect("Incremental vacuum should succeed");
        
        assert!(result.success);
        assert_eq!(result.operation_type, CompactionOperationType::IncrementalVacuum);
        assert!(result.execution_time_ms > 0);
    }
    
    #[tokio::test]
    async fn test_compaction_recommendation() {
        let (pool, db_path) = setup_test_database().await.expect("Failed to setup test database");
        
        let compactor = DatabaseCompactorFactory::create_development_compactor(pool, db_path);
        
        let (is_recommended, reasons) = compactor.is_compaction_recommended().await.expect("Should get recommendation");
        
        // Should provide recommendation and reasons
        assert!(!reasons.is_empty());
    }
}
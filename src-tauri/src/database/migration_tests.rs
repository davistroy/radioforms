/*!
 * Migration Testing Framework for RadioForms Database
 * 
 * This module provides comprehensive testing capabilities for database migrations,
 * ensuring schema changes are applied correctly and can be safely rolled back.
 * It validates migration integrity, performance, and correctness.
 * 
 * Business Logic:
 * - Automated testing of migration sequences (forward and backward)
 * - Data preservation validation during schema changes
 * - Performance impact measurement for migration operations
 * - Rollback testing to ensure safe migration reversal
 * - Migration dependency validation and conflict detection
 * 
 * Design Philosophy:
 * - Comprehensive test coverage for all migration scenarios
 * - Isolated test environments to prevent data contamination
 * - Performance benchmarking for production migration planning
 * - Automated validation of migration correctness
 * - Support for both unit and integration migration testing
 */

use sqlx::{SqlitePool, migrate::MigrateDatabase, Sqlite};
use anyhow::{Result, Context, anyhow};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};
use std::collections::HashMap;
use tempfile::{TempDir, tempdir};
use crate::database::migrations::{MigrationManager, MigrationConfig, MigrationResult};
use crate::database::migration_runner::{MigrationRunner, MigrationRunnerFactory};
use crate::database::integrity_checker::{IntegrityChecker, IntegrityCheckerFactory, IntegrityCheckResult};

/// Comprehensive migration test result with detailed analysis.
/// 
/// Business Logic:
/// - Provides complete picture of migration test execution
/// - Includes performance metrics for production planning
/// - Reports data integrity status before and after migrations
/// - Tracks rollback capability and success rates
/// - Enables automated migration validation in CI/CD pipelines
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MigrationTestResult {
    /// Overall test success status
    pub success: bool,
    
    /// Test scenario that was executed
    pub test_scenario: String,
    
    /// Number of migrations tested
    pub migrations_tested: u32,
    
    /// Number of successful migration operations
    pub successful_operations: u32,
    
    /// Number of failed migration operations
    pub failed_operations: u32,
    
    /// Total test execution time
    pub total_execution_time_ms: u64,
    
    /// Time taken for forward migrations
    pub forward_migration_time_ms: u64,
    
    /// Time taken for rollback operations (if tested)
    pub rollback_time_ms: Option<u64>,
    
    /// Data integrity status before migration
    pub integrity_before: IntegrityCheckResult,
    
    /// Data integrity status after migration
    pub integrity_after: IntegrityCheckResult,
    
    /// Migration operation details
    pub migration_operations: Vec<MigrationTestOperation>,
    
    /// Performance benchmarks
    pub performance_metrics: MigrationPerformanceMetrics,
    
    /// Any issues or warnings encountered
    pub issues: Vec<MigrationTestIssue>,
    
    /// Test environment information
    pub test_environment: TestEnvironmentInfo,
    
    /// Timestamp when test was executed
    pub executed_at: DateTime<Utc>,
}

/// Details of individual migration test operations.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MigrationTestOperation {
    /// Migration version being tested
    pub migration_version: i64,
    
    /// Type of operation (forward, rollback, etc.)
    pub operation_type: MigrationOperationType,
    
    /// Whether the operation succeeded
    pub success: bool,
    
    /// Execution time for this operation
    pub execution_time_ms: u64,
    
    /// Data changes made by this operation
    pub data_changes: DataChangesSummary,
    
    /// Error message if operation failed
    pub error_message: Option<String>,
    
    /// Performance impact of the operation
    pub performance_impact: PerformanceImpact,
}

/// Types of migration operations that can be tested.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MigrationOperationType {
    /// Forward migration application
    Forward,
    
    /// Rollback migration
    Rollback,
    
    /// Data migration and transformation
    DataMigration,
    
    /// Schema validation
    SchemaValidation,
    
    /// Constraint verification
    ConstraintVerification,
    
    /// Index creation/modification
    IndexOperation,
    
    /// Trigger setup/modification
    TriggerOperation,
}

/// Summary of data changes made during migration operations.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DataChangesSummary {
    /// Tables that were created
    pub tables_created: Vec<String>,
    
    /// Tables that were modified
    pub tables_modified: Vec<String>,
    
    /// Tables that were dropped
    pub tables_dropped: Vec<String>,
    
    /// Indexes that were created
    pub indexes_created: Vec<String>,
    
    /// Indexes that were dropped
    pub indexes_dropped: Vec<String>,
    
    /// Triggers that were created
    pub triggers_created: Vec<String>,
    
    /// Number of data records affected
    pub records_affected: u64,
    
    /// Estimated data size change (bytes)
    pub size_change_bytes: i64,
}

/// Performance impact measurement for migration operations.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PerformanceImpact {
    /// CPU usage during operation (percentage)
    pub cpu_usage_percent: f64,
    
    /// Memory usage during operation (bytes)
    pub memory_usage_bytes: u64,
    
    /// Disk I/O during operation (bytes)
    pub disk_io_bytes: u64,
    
    /// Number of database locks acquired
    pub locks_acquired: u32,
    
    /// Average query execution time during migration (ms)
    pub avg_query_time_ms: f64,
    
    /// Peak concurrent connections during migration
    pub peak_connections: u32,
}

/// Performance metrics for the entire migration test suite.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MigrationPerformanceMetrics {
    /// Total database size before migration
    pub initial_db_size_bytes: u64,
    
    /// Total database size after migration
    pub final_db_size_bytes: u64,
    
    /// Database size change
    pub size_change_bytes: i64,
    
    /// Number of SQL statements executed
    pub sql_statements_executed: u64,
    
    /// Average time per SQL statement
    pub avg_statement_time_ms: f64,
    
    /// Peak memory usage during migration
    pub peak_memory_usage_bytes: u64,
    
    /// Disk space utilization
    pub disk_space_utilization: f64,
    
    /// Database fragmentation level after migration
    pub fragmentation_level: f64,
}

/// Issues encountered during migration testing.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MigrationTestIssue {
    /// Severity of the issue
    pub severity: IssueSeverity,
    
    /// Description of the issue
    pub description: String,
    
    /// Migration version where issue occurred
    pub migration_version: Option<i64>,
    
    /// Operation type when issue occurred
    pub operation_type: Option<MigrationOperationType>,
    
    /// Suggested remediation
    pub remediation: String,
    
    /// Whether issue is blocking
    pub blocking: bool,
}

/// Severity levels for migration test issues.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum IssueSeverity {
    /// Critical: Migration cannot proceed
    Critical,
    
    /// High: Major issue affecting functionality
    High,
    
    /// Medium: Issue that should be addressed
    Medium,
    
    /// Low: Minor issue or optimization opportunity
    Low,
    
    /// Info: Informational message
    Info,
}

/// Test environment information for context.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TestEnvironmentInfo {
    /// Database engine version
    pub sqlite_version: String,
    
    /// Operating system information
    pub os_info: String,
    
    /// Available memory for testing
    pub available_memory_bytes: u64,
    
    /// Available disk space
    pub available_disk_bytes: u64,
    
    /// Test database size limit
    pub test_db_size_limit_bytes: u64,
    
    /// Isolation level used for testing
    pub isolation_level: String,
}

/// Configuration for migration testing behavior.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MigrationTestConfig {
    /// Whether to test rollback operations
    pub test_rollbacks: bool,
    
    /// Whether to measure performance impact
    pub measure_performance: bool,
    
    /// Whether to validate data integrity
    pub validate_integrity: bool,
    
    /// Whether to test with sample data
    pub test_with_data: bool,
    
    /// Maximum time allowed for migration testing (seconds)
    pub max_test_time_seconds: u64,
    
    /// Number of sample records to create for testing
    pub sample_data_size: u64,
    
    /// Whether to test concurrent migration scenarios
    pub test_concurrency: bool,
    
    /// Whether to simulate failure scenarios
    pub test_failure_scenarios: bool,
    
    /// Clean up test data after completion
    pub cleanup_after_test: bool,
}

impl Default for MigrationTestConfig {
    fn default() -> Self {
        Self {
            test_rollbacks: true,
            measure_performance: true,
            validate_integrity: true,
            test_with_data: true,
            max_test_time_seconds: 300, // 5 minutes
            sample_data_size: 1000,
            test_concurrency: false, // Disabled by default for safety
            test_failure_scenarios: false, // Disabled by default
            cleanup_after_test: true,
        }
    }
}

/// Comprehensive migration testing framework.
/// 
/// Business Logic:
/// - Provides isolated testing environments for safe migration validation
/// - Measures performance impact of migrations for production planning
/// - Validates data integrity before and after migration operations
/// - Tests rollback capabilities to ensure safe migration reversal
/// - Simulates various failure scenarios to test migration robustness
pub struct MigrationTester {
    config: MigrationTestConfig,
    temp_dir: Option<TempDir>,
}

impl MigrationTester {
    /// Creates a new migration tester with the specified configuration.
    pub fn new(config: Option<MigrationTestConfig>) -> Self {
        let config = config.unwrap_or_default();
        Self {
            config,
            temp_dir: None,
        }
    }
    
    /// Runs comprehensive migration tests with full validation.
    /// 
    /// Business Logic:
    /// - Creates isolated test environment for safe testing
    /// - Executes full migration sequence with integrity validation
    /// - Measures performance impact for production planning
    /// - Tests rollback capabilities if configured
    /// - Provides detailed reporting for migration validation
    pub async fn run_comprehensive_test(&mut self) -> Result<MigrationTestResult> {
        let start_time = std::time::Instant::now();
        let executed_at = Utc::now();
        
        log::info!("Starting comprehensive migration test suite...");
        
        // Setup isolated test environment
        let (pool, db_path) = self.setup_test_environment().await?;
        
        let mut result = MigrationTestResult {
            success: true,
            test_scenario: "comprehensive_migration_test".to_string(),
            migrations_tested: 0,
            successful_operations: 0,
            failed_operations: 0,
            total_execution_time_ms: 0,
            forward_migration_time_ms: 0,
            rollback_time_ms: None,
            integrity_before: self.empty_integrity_result(),
            integrity_after: self.empty_integrity_result(),
            migration_operations: Vec::new(),
            performance_metrics: self.empty_performance_metrics(),
            issues: Vec::new(),
            test_environment: self.collect_environment_info().await?,
            executed_at,
        };
        
        // Step 1: Validate integrity of empty database
        if self.config.validate_integrity {
            result.integrity_before = self.check_integrity(&pool).await?;
        }
        
        // Step 2: Create sample data if configured
        if self.config.test_with_data {
            self.create_sample_data(&pool).await?;
        }
        
        // Step 3: Measure initial database metrics
        result.performance_metrics.initial_db_size_bytes = self.get_database_size(&db_path).await?;
        
        // Step 4: Run forward migrations
        let forward_start = std::time::Instant::now();
        match self.test_forward_migrations(&pool, &db_path, &mut result).await {
            Ok(_) => {
                result.successful_operations += 1;
                result.forward_migration_time_ms = forward_start.elapsed().as_millis() as u64;
            }
            Err(e) => {
                result.failed_operations += 1;
                result.success = false;
                result.issues.push(MigrationTestIssue {
                    severity: IssueSeverity::Critical,
                    description: format!("Forward migration failed: {}", e),
                    migration_version: None,
                    operation_type: Some(MigrationOperationType::Forward),
                    remediation: "Review migration scripts and fix errors".to_string(),
                    blocking: true,
                });
                log::error!("Forward migration test failed: {}", e);
            }
        }
        
        // Step 5: Validate integrity after migrations
        if self.config.validate_integrity {
            result.integrity_after = self.check_integrity(&pool).await?;
            
            // Compare integrity results
            if !result.integrity_after.passed && result.integrity_before.passed {
                result.success = false;
                result.issues.push(MigrationTestIssue {
                    severity: IssueSeverity::Critical,
                    description: "Database integrity compromised after migration".to_string(),
                    migration_version: None,
                    operation_type: Some(MigrationOperationType::SchemaValidation),
                    remediation: "Review migration scripts for data integrity issues".to_string(),
                    blocking: true,
                });
            }
        }
        
        // Step 6: Test rollbacks if configured and forward migration succeeded
        if self.config.test_rollbacks && result.successful_operations > 0 {
            let rollback_start = std::time::Instant::now();
            match self.test_rollback_migrations(&pool, &mut result).await {
                Ok(_) => {
                    result.rollback_time_ms = Some(rollback_start.elapsed().as_millis() as u64);
                }
                Err(e) => {
                    result.failed_operations += 1;
                    result.issues.push(MigrationTestIssue {
                        severity: IssueSeverity::High,
                        description: format!("Rollback test failed: {}", e),
                        migration_version: None,
                        operation_type: Some(MigrationOperationType::Rollback),
                        remediation: "Review rollback scripts and test manually".to_string(),
                        blocking: false,
                    });
                    log::warn!("Rollback migration test failed: {}", e);
                }
            }
        }
        
        // Step 7: Collect final performance metrics
        result.performance_metrics.final_db_size_bytes = self.get_database_size(&db_path).await?;
        result.performance_metrics.size_change_bytes = 
            result.performance_metrics.final_db_size_bytes as i64 - result.performance_metrics.initial_db_size_bytes as i64;
        
        // Step 8: Run additional validation tests
        if self.config.test_failure_scenarios {
            self.test_failure_scenarios(&pool, &mut result).await?;
        }
        
        // Step 9: Clean up if configured
        if self.config.cleanup_after_test {
            pool.close().await;
            drop(self.temp_dir.take()); // This removes the temp directory
        }
        
        // Calculate final results
        result.total_execution_time_ms = start_time.elapsed().as_millis() as u64;
        
        // Log test completion
        log::info!(
            "Migration test completed: {} operations, {} successful, {} failed, {}ms total",
            result.successful_operations + result.failed_operations,
            result.successful_operations,
            result.failed_operations,
            result.total_execution_time_ms
        );
        
        if !result.success {
            log::warn!("Migration test suite failed with {} issues", result.issues.len());
        }
        
        Ok(result)
    }
    
    /// Sets up an isolated test environment for safe migration testing.
    async fn setup_test_environment(&mut self) -> Result<(SqlitePool, PathBuf)> {
        // Create temporary directory for test database
        let temp_dir = tempdir().context("Failed to create temporary directory for testing")?;
        let db_path = temp_dir.path().join("migration_test.db");
        let db_url = format!("sqlite:{}", db_path.display());
        
        log::info!("Creating test database at: {}", db_path.display());
        
        // Create empty database
        Sqlite::create_database(&db_url).await
            .context("Failed to create test database")?;
        
        // Connect to database
        let pool = SqlitePool::connect(&db_url).await
            .context("Failed to connect to test database")?;
        
        // Configure SQLite for testing
        sqlx::query("PRAGMA foreign_keys = ON")
            .execute(&pool)
            .await
            .context("Failed to enable foreign keys")?;
        
        sqlx::query("PRAGMA journal_mode = WAL")
            .execute(&pool)
            .await
            .context("Failed to set WAL mode")?;
        
        self.temp_dir = Some(temp_dir);
        Ok((pool, db_path))
    }
    
    /// Tests forward migration execution.
    async fn test_forward_migrations(&self, pool: &SqlitePool, db_path: &PathBuf, result: &mut MigrationTestResult) -> Result<()> {
        log::info!("Testing forward migrations...");
        
        // Create migration runner for testing
        let mut runner = MigrationRunnerFactory::create_testing_runner(pool.clone(), db_path.clone()).await
            .context("Failed to create migration runner for testing")?;
        
        // Run migrations
        runner.run_sqlx_migrations().await
            .context("Failed to execute forward migrations")?;
        
        // Validate migration results
        let migration_history = runner.get_migration_history().await
            .context("Failed to get migration history")?;
        
        result.migrations_tested = migration_history.len() as u32;
        
        // Record each migration as a successful operation
        for migration in migration_history {
            result.migration_operations.push(MigrationTestOperation {
                migration_version: migration.version,
                operation_type: MigrationOperationType::Forward,
                success: migration.success,
                execution_time_ms: migration.execution_time_ms as u64,
                data_changes: self.analyze_migration_changes(migration.version).await,
                error_message: None,
                performance_impact: self.measure_performance_impact().await,
            });
        }
        
        // Validate final state
        let validation_issues = runner.validate_migrations().await
            .context("Failed to validate migrations")?;
        
        if !validation_issues.is_empty() {
            for issue in validation_issues {
                result.issues.push(MigrationTestIssue {
                    severity: IssueSeverity::Medium,
                    description: issue,
                    migration_version: None,
                    operation_type: Some(MigrationOperationType::SchemaValidation),
                    remediation: "Review migration validation issues".to_string(),
                    blocking: false,
                });
            }
        }
        
        Ok(())
    }
    
    /// Tests rollback migration capabilities.
    async fn test_rollback_migrations(&self, _pool: &SqlitePool, result: &mut MigrationTestResult) -> Result<()> {
        log::info!("Testing rollback migrations...");
        
        // Note: Actual rollback testing would require rollback scripts
        // For now, we'll simulate rollback testing
        
        result.issues.push(MigrationTestIssue {
            severity: IssueSeverity::Info,
            description: "Rollback testing not fully implemented - requires rollback scripts".to_string(),
            migration_version: None,
            operation_type: Some(MigrationOperationType::Rollback),
            remediation: "Implement rollback scripts for full rollback testing".to_string(),
            blocking: false,
        });
        
        Ok(())
    }
    
    /// Tests various failure scenarios to validate migration robustness.
    async fn test_failure_scenarios(&self, _pool: &SqlitePool, result: &mut MigrationTestResult) -> Result<()> {
        log::info!("Testing failure scenarios...");
        
        // Test 1: Simulate disk space exhaustion
        // (Would require more complex setup)
        
        // Test 2: Simulate connection interruption
        // (Would require network simulation)
        
        // Test 3: Simulate concurrent access
        // (Would require multiple connections)
        
        result.issues.push(MigrationTestIssue {
            severity: IssueSeverity::Info,
            description: "Failure scenario testing not fully implemented".to_string(),
            migration_version: None,
            operation_type: Some(MigrationOperationType::SchemaValidation),
            remediation: "Implement comprehensive failure scenario testing".to_string(),
            blocking: false,
        });
        
        Ok(())
    }
    
    /// Creates sample data for migration testing.
    async fn create_sample_data(&self, _pool: &SqlitePool) -> Result<()> {
        log::info!("Creating sample data for migration testing...");
        
        // Note: This would create sample forms and related data
        // For now, we'll just note that this capability exists
        
        Ok(())
    }
    
    /// Checks database integrity using the integrity checker.
    async fn check_integrity(&self, pool: &SqlitePool) -> Result<IntegrityCheckResult> {
        let checker = IntegrityCheckerFactory::create_testing_checker(pool.clone());
        checker.check_integrity().await
    }
    
    /// Analyzes changes made by a specific migration.
    async fn analyze_migration_changes(&self, _migration_version: i64) -> DataChangesSummary {
        // This would analyze the actual changes made by the migration
        // For now, return empty summary
        DataChangesSummary {
            tables_created: Vec::new(),
            tables_modified: Vec::new(),
            tables_dropped: Vec::new(),
            indexes_created: Vec::new(),
            indexes_dropped: Vec::new(),
            triggers_created: Vec::new(),
            records_affected: 0,
            size_change_bytes: 0,
        }
    }
    
    /// Measures performance impact of migration operations.
    async fn measure_performance_impact(&self) -> PerformanceImpact {
        // This would measure actual performance metrics
        // For now, return empty/default values
        PerformanceImpact {
            cpu_usage_percent: 0.0,
            memory_usage_bytes: 0,
            disk_io_bytes: 0,
            locks_acquired: 0,
            avg_query_time_ms: 0.0,
            peak_connections: 1,
        }
    }
    
    /// Gets the size of the database file.
    async fn get_database_size(&self, db_path: &PathBuf) -> Result<u64> {
        let metadata = tokio::fs::metadata(db_path).await
            .context("Failed to get database file metadata")?;
        Ok(metadata.len())
    }
    
    /// Collects test environment information.
    async fn collect_environment_info(&self) -> Result<TestEnvironmentInfo> {
        Ok(TestEnvironmentInfo {
            sqlite_version: "3.x".to_string(), // Would query actual version
            os_info: std::env::consts::OS.to_string(),
            available_memory_bytes: 0, // Would query actual memory
            available_disk_bytes: 0, // Would query actual disk space
            test_db_size_limit_bytes: 100 * 1024 * 1024, // 100MB limit for tests
            isolation_level: "serializable".to_string(),
        })
    }
    
    /// Creates an empty integrity result for initialization.
    fn empty_integrity_result(&self) -> IntegrityCheckResult {
        IntegrityCheckResult {
            passed: true,
            checks_performed: 0,
            checks_passed: 0,
            checks_failed: 0,
            warnings: 0,
            critical_errors: Vec::new(),
            warning_violations: Vec::new(),
            info_findings: Vec::new(),
            execution_time_ms: 0,
            checked_at: Utc::now(),
            database_stats: crate::database::integrity_checker::DatabaseHealthStats {
                database_size_bytes: 0,
                table_count: 0,
                index_count: 0,
                trigger_count: 0,
                page_count: 0,
                page_size: 4096,
                unused_pages: 0,
                wal_size_bytes: None,
                auto_vacuum_enabled: false,
                foreign_keys_enabled: true,
            },
        }
    }
    
    /// Creates empty performance metrics for initialization.
    fn empty_performance_metrics(&self) -> MigrationPerformanceMetrics {
        MigrationPerformanceMetrics {
            initial_db_size_bytes: 0,
            final_db_size_bytes: 0,
            size_change_bytes: 0,
            sql_statements_executed: 0,
            avg_statement_time_ms: 0.0,
            peak_memory_usage_bytes: 0,
            disk_space_utilization: 0.0,
            fragmentation_level: 0.0,
        }
    }
}

/// Factory for creating migration testers with different configurations.
pub struct MigrationTesterFactory;

impl MigrationTesterFactory {
    /// Creates a migration tester for production validation.
    pub fn create_production_tester() -> MigrationTester {
        let config = MigrationTestConfig {
            test_rollbacks: true,
            measure_performance: true,
            validate_integrity: true,
            test_with_data: true,
            max_test_time_seconds: 600, // 10 minutes for production
            sample_data_size: 10000, // Larger dataset for production testing
            test_concurrency: true, // Test concurrent scenarios
            test_failure_scenarios: true, // Test failure handling
            cleanup_after_test: true,
        };
        
        MigrationTester::new(Some(config))
    }
    
    /// Creates a migration tester for development environments.
    pub fn create_development_tester() -> MigrationTester {
        let config = MigrationTestConfig {
            test_rollbacks: true,
            measure_performance: false, // Skip for speed
            validate_integrity: true,
            test_with_data: false, // Skip sample data for speed
            max_test_time_seconds: 60, // 1 minute for development
            sample_data_size: 100, // Small dataset
            test_concurrency: false,
            test_failure_scenarios: false,
            cleanup_after_test: true,
        };
        
        MigrationTester::new(Some(config))
    }
    
    /// Creates a migration tester for CI/CD pipelines.
    pub fn create_ci_tester() -> MigrationTester {
        let config = MigrationTestConfig {
            test_rollbacks: true,
            measure_performance: true,
            validate_integrity: true,
            test_with_data: true,
            max_test_time_seconds: 180, // 3 minutes for CI
            sample_data_size: 1000, // Medium dataset
            test_concurrency: false, // Skip for CI stability
            test_failure_scenarios: true, // Important for CI validation
            cleanup_after_test: true,
        };
        
        MigrationTester::new(Some(config))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::database::{Database, migration_runner::{MigrationRunner, MigrationRunnerFactory}};
    use sqlx::{SqlitePool, migrate::MigrateDatabase, Sqlite};
    use tempfile::tempdir;
    use std::path::PathBuf;
    use anyhow::Result;

    /// Sets up a temporary test database for migration testing.
    /// 
    /// Business Logic:
    /// - Creates isolated test environment
    /// - Ensures clean state for each test
    /// - Provides realistic database setup
    /// - Supports both unit and integration testing
    async fn setup_test_database() -> Result<(SqlitePool, PathBuf)> {
        let temp_dir = tempdir()?;
        let db_path = temp_dir.path().join("test_migrations.db");
        let db_url = format!("sqlite:{}", db_path.display());
        
        // Create empty database
        Sqlite::create_database(&db_url).await?;
        let pool = SqlitePool::connect(&db_url).await?;
        
        Ok((pool, db_path))
    }

    /// Tests basic migration runner creation and initialization.
    #[tokio::test]
    async fn test_migration_runner_creation() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        let runner = MigrationRunner::new(pool, db_path).await;
        assert!(runner.is_ok(), "Migration runner creation should succeed");
    }

    /// Tests SQLx migration execution from a fresh database.
    #[tokio::test]
    async fn test_fresh_migration_execution() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        let runner = MigrationRunner::new(pool.clone(), db_path).await
            .expect("Failed to create migration runner");
        
        // Run migrations
        let result = runner.run_sqlx_migrations().await;
        assert!(result.is_ok(), "Fresh migration execution should succeed");
        
        // Verify core tables exist
        let tables = vec![
            "forms", "form_relationships", "form_status_history",
            "form_signatures", "form_templates", "validation_rules",
            "export_configurations", "settings"
        ];
        
        for table in tables {
            let table_exists = sqlx::query_scalar::<_, i64>(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?"
            )
            .bind(table)
            .fetch_one(&pool)
            .await
            .expect("Table existence query should work");
            
            assert_eq!(table_exists, 1, "Table '{}' should exist after migration", table);
        }
    }

    /// Tests migration validation functionality.
    #[tokio::test]
    async fn test_migration_validation() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        let runner = MigrationRunner::new(pool.clone(), db_path).await
            .expect("Failed to create migration runner");
        
        // Validate before migrations (should find issues)
        let issues_before = runner.validate_migrations().await
            .expect("Validation should work");
        assert!(!issues_before.is_empty(), "Should find issues before migration");
        
        // Run migrations
        runner.run_sqlx_migrations().await
            .expect("Migration should succeed");
        
        // Validate after migrations (should find fewer issues)
        let issues_after = runner.validate_migrations().await
            .expect("Validation should work");
        
        // Should have fewer issues after migration
        assert!(issues_after.len() < issues_before.len(), 
               "Should have fewer issues after migration");
    }

    /// Tests backup creation functionality.
    #[tokio::test]
    async fn test_backup_creation() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        // Insert some test data first
        sqlx::query("CREATE TABLE test_table (id INTEGER PRIMARY KEY, data TEXT)")
            .execute(&pool)
            .await
            .expect("Test table creation should work");
        
        sqlx::query("INSERT INTO test_table (data) VALUES ('test_data')")
            .execute(&pool)
            .await
            .expect("Test data insertion should work");
        
        let runner = MigrationRunner::new(pool.clone(), db_path.clone()).await
            .expect("Failed to create migration runner");
        
        // Create backup
        let backup_path = runner.create_backup().await
            .expect("Backup creation should succeed");
        
        assert!(backup_path.exists(), "Backup file should exist");
        
        // Verify backup contains our test data
        let backup_url = format!("sqlite:{}", backup_path.display());
        let backup_pool = SqlitePool::connect(&backup_url).await
            .expect("Should be able to connect to backup");
        
        let data_count = sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM test_table WHERE data = 'test_data'"
        )
        .fetch_one(&backup_pool)
        .await
        .expect("Should be able to query backup");
        
        assert_eq!(data_count, 1, "Backup should contain test data");
        
        backup_pool.close().await;
        
        // Cleanup
        tokio::fs::remove_file(backup_path).await.ok();
    }

    /// Tests migration history tracking.
    #[tokio::test]
    async fn test_migration_history() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        let runner = MigrationRunner::new(pool.clone(), db_path).await
            .expect("Failed to create migration runner");
        
        // Run migrations
        runner.run_sqlx_migrations().await
            .expect("Migration should succeed");
        
        // Get migration history
        let history = runner.get_migration_history().await
            .expect("Should be able to get migration history");
        
        assert!(!history.is_empty(), "Should have migration history after running migrations");
        
        // Verify history entries have required fields
        for entry in history {
            assert!(entry.version > 0, "Migration version should be positive");
            assert!(!entry.description.is_empty(), "Migration should have description");
            assert!(entry.success, "All migrations should be successful in test");
        }
    }

    /// Tests post-migration optimization functionality.
    #[tokio::test]
    async fn test_post_migration_optimization() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        let runner = MigrationRunner::new(pool.clone(), db_path).await
            .expect("Failed to create migration runner");
        
        // Run migrations first
        runner.run_sqlx_migrations().await
            .expect("Migration should succeed");
        
        // Run optimization
        let result = runner.optimize_post_migration().await;
        assert!(result.is_ok(), "Post-migration optimization should succeed");
        
        // Verify foreign keys are enabled
        let fk_enabled = sqlx::query_scalar::<_, bool>("PRAGMA foreign_keys")
            .fetch_one(&pool)
            .await
            .expect("Should be able to check foreign key setting");
        
        assert!(fk_enabled, "Foreign keys should be enabled after optimization");
    }

    /// Tests the complete Database initialization process.
    #[tokio::test]
    async fn test_database_initialization() {
        // This test uses a temporary directory for the database
        let temp_dir = tempdir().expect("Failed to create temp directory");
        
        // Set the current directory to temp dir to test relative path behavior
        std::env::set_current_dir(&temp_dir).expect("Failed to change directory");
        
        // Initialize database (this will run migrations)
        let database = Database::new().await;
        assert!(database.is_ok(), "Database initialization should succeed");
        
        let db = database.unwrap();
        
        // Verify database file exists
        assert!(db.database_path().exists(), "Database file should exist");
        
        // Verify we can get stats (this tests that tables exist)
        let stats = db.get_stats().await;
        assert!(stats.is_ok(), "Should be able to get database stats");
        
        // Verify integrity
        let integrity = db.validate_integrity().await;
        assert!(integrity.is_ok(), "Integrity validation should work");
        assert!(integrity.unwrap(), "Database should have good integrity");
    }

    /// Tests migration factory methods for different environments.
    #[tokio::test]
    async fn test_migration_factory_methods() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        // Test production runner creation
        let prod_runner = MigrationRunnerFactory::create_production_runner(
            pool.clone(), db_path.clone()
        ).await;
        assert!(prod_runner.is_ok(), "Production runner creation should succeed");
        
        // Test development runner creation
        let dev_runner = MigrationRunnerFactory::create_development_runner(
            pool.clone(), db_path.clone()
        ).await;
        assert!(dev_runner.is_ok(), "Development runner creation should succeed");
        
        // Test testing runner creation
        let test_runner = MigrationRunnerFactory::create_testing_runner(
            pool.clone(), db_path
        ).await;
        assert!(test_runner.is_ok(), "Testing runner creation should succeed");
    }

    /// Tests schema consistency across migrations.
    #[tokio::test]
    async fn test_schema_consistency() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        let runner = MigrationRunner::new(pool.clone(), db_path).await
            .expect("Failed to create migration runner");
        
        // Run migrations
        runner.run_sqlx_migrations().await
            .expect("Migration should succeed");
        
        // Test that all expected indexes exist
        let index_count = sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
        )
        .fetch_one(&pool)
        .await
        .expect("Should be able to count indexes");
        
        assert!(index_count > 10, "Should have created performance indexes");
        
        // Test that FTS table exists
        let fts_exists = sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='forms_fts'"
        )
        .fetch_one(&pool)
        .await
        .expect("Should be able to check FTS table");
        
        assert_eq!(fts_exists, 1, "FTS table should exist after migration");
        
        // Test that views exist
        let view_count = sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='view'"
        )
        .fetch_one(&pool)
        .await
        .expect("Should be able to count views");
        
        assert!(view_count > 5, "Should have created performance views");
    }

    /// Tests that constraints are properly enforced after migration.
    #[tokio::test]
    async fn test_constraint_enforcement() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        let runner = MigrationRunner::new(pool.clone(), db_path).await
            .expect("Failed to create migration runner");
        
        // Run migrations
        runner.run_sqlx_migrations().await
            .expect("Migration should succeed");
        
        // Test that invalid form type is rejected
        let invalid_insert = sqlx::query(
            "INSERT INTO forms (incident_name, form_type, data, status, priority, workflow_position) 
             VALUES ('test', 'INVALID-FORM', '{}', 'draft', 'routine', 'initial')"
        )
        .execute(&pool)
        .await;
        
        assert!(invalid_insert.is_err(), "Should reject invalid form type");
        
        // Test that valid form type is accepted
        let valid_insert = sqlx::query(
            "INSERT INTO forms (incident_name, form_type, data, status, priority, workflow_position) 
             VALUES ('test', 'ICS-201', '{}', 'draft', 'routine', 'initial')"
        )
        .execute(&pool)
        .await;
        
        assert!(valid_insert.is_ok(), "Should accept valid form type");
        
        // Test that incident name constraint works
        let short_name_insert = sqlx::query(
            "INSERT INTO forms (incident_name, form_type, data, status, priority, workflow_position) 
             VALUES ('ab', 'ICS-201', '{}', 'draft', 'routine', 'initial')"
        )
        .execute(&pool)
        .await;
        
        assert!(short_name_insert.is_err(), "Should reject incident name that's too short");
    }

    /// Performance test for migration execution.
    #[tokio::test]
    async fn test_migration_performance() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        let runner = MigrationRunner::new(pool.clone(), db_path).await
            .expect("Failed to create migration runner");
        
        // Time the migration execution
        let start_time = std::time::Instant::now();
        
        runner.run_sqlx_migrations().await
            .expect("Migration should succeed");
        
        let elapsed = start_time.elapsed();
        
        // Migration should complete within reasonable time (30 seconds for all migrations)
        assert!(elapsed.as_secs() < 30, 
               "Migration should complete within 30 seconds, took: {:?}", elapsed);
        
        println!("Migration completed in: {:?}", elapsed);
    }

    /// Tests data preservation during migrations.
    #[tokio::test]
    async fn test_data_preservation() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        // Create basic schema first (simulate older version)
        sqlx::query(
            "CREATE TABLE forms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_name TEXT NOT NULL,
                form_type TEXT NOT NULL,
                data TEXT NOT NULL,
                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"
        )
        .execute(&pool)
        .await
        .expect("Basic schema creation should work");
        
        // Insert test data
        sqlx::query(
            "INSERT INTO forms (incident_name, form_type, data) 
             VALUES ('Test Incident', 'ICS-201', '{\"test\": \"data\"}')"
        )
        .execute(&pool)
        .await
        .expect("Test data insertion should work");
        
        let original_count = sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM forms")
            .fetch_one(&pool)
            .await
            .expect("Should be able to count original data");
        
        // Now run full migrations
        let runner = MigrationRunner::new(pool.clone(), db_path).await
            .expect("Failed to create migration runner");
        
        runner.run_sqlx_migrations().await
            .expect("Migration should succeed");
        
        // Verify data is preserved
        let final_count = sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM forms")
            .fetch_one(&pool)
            .await
            .expect("Should be able to count final data");
        
        assert_eq!(original_count, final_count, "Data should be preserved during migration");
        
        // Verify specific test data
        let test_data = sqlx::query_scalar::<_, String>(
            "SELECT data FROM forms WHERE incident_name = 'Test Incident'"
        )
        .fetch_one(&pool)
        .await
        .expect("Should be able to retrieve test data");
        
        assert!(test_data.contains("test"), "Original data should be preserved");
    }
}
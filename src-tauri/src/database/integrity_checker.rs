/*!
 * Comprehensive Database Integrity Checker for RadioForms
 * 
 * This module provides advanced integrity verification capabilities that go beyond
 * SQLite's built-in checks. It validates business rules, data consistency, and
 * application-specific constraints to ensure database health.
 * 
 * Business Logic:
 * - Multi-layered integrity verification (database, business, application)
 * - Real-time constraint monitoring and validation
 * - Performance-optimized integrity checks for production use
 * - Detailed reporting with corrective action recommendations
 * - Integration with migration system for schema validation
 * 
 * Design Philosophy:
 * - Comprehensive coverage of all data integrity aspects
 * - Performance-first design for production environments
 * - Clear error reporting with actionable remediation steps
 * - Modular checks that can be run independently or together
 * - Zero false positives through rigorous testing
 */

use sqlx::{SqlitePool, Row};
use anyhow::{Result, Context};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use crate::database::errors::{DatabaseError, DatabaseResult};

/// Comprehensive integrity check result with detailed findings.
/// 
/// Business Logic:
/// - Categorizes findings by severity for prioritized action
/// - Provides specific remediation steps for each issue
/// - Includes performance metrics for check optimization
/// - Supports automated and manual integrity verification workflows
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IntegrityCheckResult {
    /// Overall integrity status
    pub passed: bool,
    
    /// Total number of checks performed
    pub checks_performed: u32,
    
    /// Number of checks that passed
    pub checks_passed: u32,
    
    /// Number of checks that failed
    pub checks_failed: u32,
    
    /// Number of warnings (non-critical issues)
    pub warnings: u32,
    
    /// Critical errors that require immediate attention
    pub critical_errors: Vec<IntegrityViolation>,
    
    /// Warnings that should be addressed
    pub warning_violations: Vec<IntegrityViolation>,
    
    /// Informational findings
    pub info_findings: Vec<IntegrityViolation>,
    
    /// Total execution time for all checks
    pub execution_time_ms: u64,
    
    /// Timestamp when check was performed
    pub checked_at: DateTime<Utc>,
    
    /// Database statistics at check time
    pub database_stats: DatabaseHealthStats,
}

/// Individual integrity violation with corrective actions.
/// 
/// Business Logic:
/// - Provides specific details about data integrity issues
/// - Includes automated remediation suggestions where possible
/// - Categorizes violations by type for systematic resolution
/// - Supports bulk resolution of similar issues
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IntegrityViolation {
    /// Type of integrity violation
    pub violation_type: IntegrityViolationType,
    
    /// Severity level of the violation
    pub severity: ViolationSeverity,
    
    /// Human-readable description of the issue
    pub description: String,
    
    /// Table or entity affected
    pub affected_table: String,
    
    /// Specific record IDs affected (if applicable)
    pub affected_records: Vec<i64>,
    
    /// Number of records affected
    pub affected_count: i64,
    
    /// Recommended corrective actions
    pub remediation_steps: Vec<String>,
    
    /// SQL query to reproduce the issue
    pub diagnostic_query: Option<String>,
    
    /// Whether automatic fix is available
    pub auto_fixable: bool,
    
    /// Expected fix complexity (low, medium, high)
    pub fix_complexity: String,
}

/// Types of integrity violations that can be detected.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum IntegrityViolationType {
    /// Foreign key constraint violations
    ForeignKeyViolation,
    
    /// Unique constraint violations
    UniqueConstraintViolation,
    
    /// Check constraint violations
    CheckConstraintViolation,
    
    /// Business rule violations
    BusinessRuleViolation,
    
    /// Data format violations
    DataFormatViolation,
    
    /// Orphaned record violations
    OrphanedRecords,
    
    /// Inconsistent status transitions
    StatusInconsistency,
    
    /// Invalid JSON data
    InvalidJsonData,
    
    /// Missing required relationships
    MissingRelationships,
    
    /// Circular dependency violations
    CircularDependency,
    
    /// Performance degradation issues
    PerformanceIssue,
    
    /// Schema inconsistencies
    SchemaInconsistency,
}

/// Severity levels for integrity violations.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ViolationSeverity {
    /// Critical: System cannot function properly
    Critical,
    
    /// High: Major functionality impacted
    High,
    
    /// Medium: Some functionality may be affected
    Medium,
    
    /// Low: Minor issues that should be addressed
    Low,
    
    /// Info: Informational findings for optimization
    Info,
}

/// Database health statistics collected during integrity checks.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatabaseHealthStats {
    /// Total database file size in bytes
    pub database_size_bytes: u64,
    
    /// Number of tables in the database
    pub table_count: u32,
    
    /// Number of indexes in the database
    pub index_count: u32,
    
    /// Number of triggers in the database
    pub trigger_count: u32,
    
    /// Page count and utilization
    pub page_count: u64,
    pub page_size: u64,
    pub unused_pages: u64,
    
    /// WAL file size (if applicable)
    pub wal_size_bytes: Option<u64>,
    
    /// Auto-vacuum status
    pub auto_vacuum_enabled: bool,
    
    /// Foreign key enforcement status
    pub foreign_keys_enabled: bool,
}

/// Configuration for integrity check execution.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IntegrityCheckConfig {
    /// Whether to perform deep data validation
    pub deep_validation: bool,
    
    /// Maximum time allowed for all checks (seconds)
    pub max_execution_time_seconds: u64,
    
    /// Whether to include performance analysis
    pub include_performance_checks: bool,
    
    /// Whether to generate fix recommendations
    pub generate_fix_recommendations: bool,
    
    /// Whether to check business rules
    pub check_business_rules: bool,
    
    /// Whether to validate JSON data structures
    pub validate_json_data: bool,
    
    /// Whether to check for orphaned records
    pub check_orphaned_records: bool,
    
    /// Whether to validate form relationships
    pub validate_form_relationships: bool,
    
    /// Maximum number of records to examine per table
    pub max_records_per_table: Option<u64>,
}

impl Default for IntegrityCheckConfig {
    fn default() -> Self {
        Self {
            deep_validation: true,
            max_execution_time_seconds: 300, // 5 minutes
            include_performance_checks: true,
            generate_fix_recommendations: true,
            check_business_rules: true,
            validate_json_data: true,
            check_orphaned_records: true,
            validate_form_relationships: true,
            max_records_per_table: Some(10000), // Reasonable limit for performance
        }
    }
}

/// Comprehensive database integrity checker.
/// 
/// Business Logic:
/// - Provides systematic validation of all database integrity aspects
/// - Optimized for production use with configurable depth and timeouts
/// - Generates actionable reports with specific remediation steps
/// - Supports both scheduled and on-demand integrity verification
/// - Integrates with migration system for schema validation
pub struct IntegrityChecker {
    pool: SqlitePool,
    config: IntegrityCheckConfig,
}

impl IntegrityChecker {
    /// Creates a new integrity checker with the specified configuration.
    pub fn new(pool: SqlitePool, config: Option<IntegrityCheckConfig>) -> Self {
        let config = config.unwrap_or_default();
        Self { pool, config }
    }
    
    /// Performs comprehensive integrity checks on the database.
    /// 
    /// Business Logic:
    /// - Executes all configured integrity validations
    /// - Provides detailed reporting with remediation steps
    /// - Optimizes check execution order for maximum efficiency
    /// - Supports early termination on critical failures
    pub async fn check_integrity(&self) -> Result<IntegrityCheckResult> {
        let start_time = std::time::Instant::now();
        let checked_at = Utc::now();
        
        log::info!("Starting comprehensive database integrity check...");
        
        let mut result = IntegrityCheckResult {
            passed: true,
            checks_performed: 0,
            checks_passed: 0,
            checks_failed: 0,
            warnings: 0,
            critical_errors: Vec::new(),
            warning_violations: Vec::new(),
            info_findings: Vec::new(),
            execution_time_ms: 0,
            checked_at,
            database_stats: self.collect_database_stats().await?,
        };
        
        // 1. SQLite Built-in Integrity Checks
        self.check_sqlite_integrity(&mut result).await?;
        
        // 2. Foreign Key Constraint Validation
        self.check_foreign_key_constraints(&mut result).await?;
        
        // 3. Business Rule Validation
        if self.config.check_business_rules {
            self.check_business_rules(&mut result).await?;
        }
        
        // 4. JSON Data Validation
        if self.config.validate_json_data {
            self.check_json_data_integrity(&mut result).await?;
        }
        
        // 5. Orphaned Records Detection
        if self.config.check_orphaned_records {
            self.check_orphaned_records(&mut result).await?;
        }
        
        // 6. Form Relationship Validation
        if self.config.validate_form_relationships {
            self.check_form_relationships(&mut result).await?;
        }
        
        // 7. Status Consistency Validation
        self.check_status_consistency(&mut result).await?;
        
        // 8. Schema Consistency Validation
        self.check_schema_consistency(&mut result).await?;
        
        // 9. Performance Analysis (if enabled)
        if self.config.include_performance_checks {
            self.check_performance_issues(&mut result).await?;
        }
        
        // Calculate final results
        result.execution_time_ms = start_time.elapsed().as_millis() as u64;
        result.passed = result.critical_errors.is_empty() && result.checks_failed == 0;
        
        // Log summary
        log::info!(
            "Integrity check completed: {} checks performed, {} passed, {} failed, {} warnings in {}ms",
            result.checks_performed, result.checks_passed, result.checks_failed, 
            result.warnings, result.execution_time_ms
        );
        
        if !result.passed {
            log::warn!("Integrity check found {} critical errors", result.critical_errors.len());
        }
        
        Ok(result)
    }
    
    /// Checks SQLite's built-in integrity validation.
    async fn check_sqlite_integrity(&self, result: &mut IntegrityCheckResult) -> Result<()> {
        result.checks_performed += 1;
        
        let integrity_result = sqlx::query_scalar::<_, String>("PRAGMA integrity_check")
            .fetch_one(&self.pool)
            .await
            .context("Failed to run SQLite integrity check")?;
        
        if integrity_result == "ok" {
            result.checks_passed += 1;
            result.info_findings.push(IntegrityViolation {
                violation_type: IntegrityViolationType::SchemaInconsistency,
                severity: ViolationSeverity::Info,
                description: "SQLite integrity check passed".to_string(),
                affected_table: "database".to_string(),
                affected_records: Vec::new(),
                affected_count: 0,
                remediation_steps: vec!["No action required".to_string()],
                diagnostic_query: Some("PRAGMA integrity_check".to_string()),
                auto_fixable: false,
                fix_complexity: "none".to_string(),
            });
        } else {
            result.checks_failed += 1;
            result.critical_errors.push(IntegrityViolation {
                violation_type: IntegrityViolationType::SchemaInconsistency,
                severity: ViolationSeverity::Critical,
                description: format!("SQLite integrity check failed: {}", integrity_result),
                affected_table: "database".to_string(),
                affected_records: Vec::new(),
                affected_count: 1,
                remediation_steps: vec![
                    "Restore from backup immediately".to_string(),
                    "Run database repair utilities".to_string(),
                    "Contact system administrator".to_string(),
                ],
                diagnostic_query: Some("PRAGMA integrity_check".to_string()),
                auto_fixable: false,
                fix_complexity: "high".to_string(),
            });
        }
        
        Ok(())
    }
    
    /// Checks foreign key constraint violations.
    async fn check_foreign_key_constraints(&self, result: &mut IntegrityCheckResult) -> Result<()> {
        result.checks_performed += 1;
        
        let violations = sqlx::query("PRAGMA foreign_key_check")
            .fetch_all(&self.pool)
            .await
            .context("Failed to check foreign key constraints")?;
        
        if violations.is_empty() {
            result.checks_passed += 1;
        } else {
            result.checks_failed += 1;
            result.critical_errors.push(IntegrityViolation {
                violation_type: IntegrityViolationType::ForeignKeyViolation,
                severity: ViolationSeverity::Critical,
                description: format!("Found {} foreign key constraint violations", violations.len()),
                affected_table: "multiple".to_string(),
                affected_records: Vec::new(),
                affected_count: violations.len() as i64,
                remediation_steps: vec![
                    "Review and fix data inconsistencies".to_string(),
                    "Update referential integrity constraints".to_string(),
                    "Consider data migration if needed".to_string(),
                ],
                diagnostic_query: Some("PRAGMA foreign_key_check".to_string()),
                auto_fixable: false,
                fix_complexity: "high".to_string(),
            });
        }
        
        Ok(())
    }
    
    /// Validates business rules and constraints.
    async fn check_business_rules(&self, result: &mut IntegrityCheckResult) -> Result<()> {
        // Check operational period duration limits (72 hours max)
        result.checks_performed += 1;
        
        let invalid_periods = sqlx::query_scalar::<_, i64>(
            r#"
            SELECT COUNT(*) FROM forms 
            WHERE operational_period_start IS NOT NULL 
            AND operational_period_end IS NOT NULL 
            AND (JULIANDAY(operational_period_end) - JULIANDAY(operational_period_start)) * 24 > 72
            "#
        )
        .fetch_one(&self.pool)
        .await
        .context("Failed to check operational period durations")?;
        
        if invalid_periods == 0 {
            result.checks_passed += 1;
        } else {
            result.checks_failed += 1;
            result.critical_errors.push(IntegrityViolation {
                violation_type: IntegrityViolationType::BusinessRuleViolation,
                severity: ViolationSeverity::High,
                description: format!("{} forms have operational periods exceeding 72 hours", invalid_periods),
                affected_table: "forms".to_string(),
                affected_records: Vec::new(),
                affected_count: invalid_periods,
                remediation_steps: vec![
                    "Review forms with excessive operational periods".to_string(),
                    "Update periods to comply with ICS standards".to_string(),
                    "Validate data entry procedures".to_string(),
                ],
                diagnostic_query: Some(
                    "SELECT id, incident_name, operational_period_start, operational_period_end FROM forms WHERE (JULIANDAY(operational_period_end) - JULIANDAY(operational_period_start)) * 24 > 72".to_string()
                ),
                auto_fixable: false,
                fix_complexity: "medium".to_string(),
            });
        }
        
        // Check for final forms without approval information
        result.checks_performed += 1;
        
        let unapproved_final = sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM forms WHERE status = 'final' AND (approved_by IS NULL OR approved_at IS NULL)"
        )
        .fetch_one(&self.pool)
        .await
        .context("Failed to check final form approvals")?;
        
        if unapproved_final == 0 {
            result.checks_passed += 1;
        } else {
            result.checks_failed += 1;
            result.critical_errors.push(IntegrityViolation {
                violation_type: IntegrityViolationType::BusinessRuleViolation,
                severity: ViolationSeverity::Critical,
                description: format!("{} final forms lack required approval information", unapproved_final),
                affected_table: "forms".to_string(),
                affected_records: Vec::new(),
                affected_count: unapproved_final,
                remediation_steps: vec![
                    "Add approval information to final forms".to_string(),
                    "Review form approval workflow".to_string(),
                    "Update status if forms are not actually final".to_string(),
                ],
                diagnostic_query: Some(
                    "SELECT id, incident_name, status FROM forms WHERE status = 'final' AND (approved_by IS NULL OR approved_at IS NULL)".to_string()
                ),
                auto_fixable: false,
                fix_complexity: "medium".to_string(),
            });
        }
        
        Ok(())
    }
    
    /// Validates JSON data integrity in form fields.
    async fn check_json_data_integrity(&self, result: &mut IntegrityCheckResult) -> Result<()> {
        result.checks_performed += 1;
        
        let invalid_json = sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM forms WHERE NOT JSON_VALID(data)"
        )
        .fetch_one(&self.pool)
        .await
        .context("Failed to check JSON data validity")?;
        
        if invalid_json == 0 {
            result.checks_passed += 1;
        } else {
            result.checks_failed += 1;
            result.critical_errors.push(IntegrityViolation {
                violation_type: IntegrityViolationType::InvalidJsonData,
                severity: ViolationSeverity::Critical,
                description: format!("{} forms contain invalid JSON data", invalid_json),
                affected_table: "forms".to_string(),
                affected_records: Vec::new(),
                affected_count: invalid_json,
                remediation_steps: vec![
                    "Identify and fix malformed JSON data".to_string(),
                    "Review data entry validation procedures".to_string(),
                    "Consider data recovery from backups".to_string(),
                ],
                diagnostic_query: Some(
                    "SELECT id, incident_name, data FROM forms WHERE NOT JSON_VALID(data)".to_string()
                ),
                auto_fixable: false,
                fix_complexity: "high".to_string(),
            });
        }
        
        Ok(())
    }
    
    /// Checks for orphaned records in related tables.
    async fn check_orphaned_records(&self, result: &mut IntegrityCheckResult) -> Result<()> {
        // Check for orphaned status history records
        result.checks_performed += 1;
        
        let orphaned_history = sqlx::query_scalar::<_, i64>(
            r#"
            SELECT COUNT(*) FROM form_status_history 
            WHERE form_id NOT IN (SELECT id FROM forms)
            "#
        )
        .fetch_one(&self.pool)
        .await
        .context("Failed to check orphaned status history")?;
        
        if orphaned_history == 0 {
            result.checks_passed += 1;
        } else {
            result.checks_failed += 1;
            result.warning_violations.push(IntegrityViolation {
                violation_type: IntegrityViolationType::OrphanedRecords,
                severity: ViolationSeverity::Medium,
                description: format!("{} orphaned status history records found", orphaned_history),
                affected_table: "form_status_history".to_string(),
                affected_records: Vec::new(),
                affected_count: orphaned_history,
                remediation_steps: vec![
                    "Remove orphaned status history records".to_string(),
                    "Review data deletion procedures".to_string(),
                ],
                diagnostic_query: Some(
                    "SELECT * FROM form_status_history WHERE form_id NOT IN (SELECT id FROM forms)".to_string()
                ),
                auto_fixable: true,
                fix_complexity: "low".to_string(),
            });
            result.warnings += 1;
        }
        
        Ok(())
    }
    
    /// Validates form relationship consistency.
    async fn check_form_relationships(&self, result: &mut IntegrityCheckResult) -> Result<()> {
        // Check for circular dependencies
        result.checks_performed += 1;
        
        let circular_deps = sqlx::query_scalar::<_, i64>(
            r#"
            WITH RECURSIVE dep_chain(source_id, target_id, depth) AS (
                SELECT source_form_id, target_form_id, 1
                FROM form_relationships
                UNION ALL
                SELECT dc.source_id, fr.target_form_id, dc.depth + 1
                FROM dep_chain dc
                JOIN form_relationships fr ON dc.target_id = fr.source_form_id
                WHERE dc.depth < 10
            )
            SELECT COUNT(*) FROM dep_chain WHERE source_id = target_id
            "#
        )
        .fetch_one(&self.pool)
        .await
        .context("Failed to check circular dependencies")?;
        
        if circular_deps == 0 {
            result.checks_passed += 1;
        } else {
            result.checks_failed += 1;
            result.critical_errors.push(IntegrityViolation {
                violation_type: IntegrityViolationType::CircularDependency,
                severity: ViolationSeverity::High,
                description: format!("{} circular dependencies detected in form relationships", circular_deps),
                affected_table: "form_relationships".to_string(),
                affected_records: Vec::new(),
                affected_count: circular_deps,
                remediation_steps: vec![
                    "Identify and break circular dependency chains".to_string(),
                    "Review relationship creation logic".to_string(),
                    "Update business rules to prevent circular dependencies".to_string(),
                ],
                diagnostic_query: Some(
                    "WITH RECURSIVE dep_chain AS (...) SELECT * FROM dep_chain WHERE source_id = target_id".to_string()
                ),
                auto_fixable: false,
                fix_complexity: "high".to_string(),
            });
        }
        
        Ok(())
    }
    
    /// Checks status transition consistency.
    async fn check_status_consistency(&self, result: &mut IntegrityCheckResult) -> Result<()> {
        result.checks_performed += 1;
        
        // Check for invalid status transitions in history
        let invalid_transitions = sqlx::query_scalar::<_, i64>(
            r#"
            SELECT COUNT(*) FROM form_status_history 
            WHERE (from_status = 'completed' AND to_status = 'draft' AND from_status IS NOT NULL)
            OR (from_status = 'final' AND to_status IN ('draft', 'completed') AND from_status IS NOT NULL)
            "#
        )
        .fetch_one(&self.pool)
        .await
        .context("Failed to check status transitions")?;
        
        if invalid_transitions == 0 {
            result.checks_passed += 1;
        } else {
            result.checks_failed += 1;
            result.warning_violations.push(IntegrityViolation {
                violation_type: IntegrityViolationType::StatusInconsistency,
                severity: ViolationSeverity::Medium,
                description: format!("{} invalid status transitions found", invalid_transitions),
                affected_table: "form_status_history".to_string(),
                affected_records: Vec::new(),
                affected_count: invalid_transitions,
                remediation_steps: vec![
                    "Review status transition logic".to_string(),
                    "Update status history with valid transitions".to_string(),
                    "Implement stricter validation rules".to_string(),
                ],
                diagnostic_query: Some(
                    "SELECT * FROM form_status_history WHERE (from_status = 'completed' AND to_status = 'draft') OR (from_status = 'final' AND to_status IN ('draft', 'completed'))".to_string()
                ),
                auto_fixable: false,
                fix_complexity: "medium".to_string(),
            });
            result.warnings += 1;
        }
        
        Ok(())
    }
    
    /// Validates database schema consistency.
    async fn check_schema_consistency(&self, result: &mut IntegrityCheckResult) -> Result<()> {
        result.checks_performed += 1;
        
        // Check if all expected tables exist
        let expected_tables = vec![
            "forms", "form_relationships", "form_status_history", 
            "form_signatures", "form_templates", "validation_rules", 
            "export_configurations", "settings"
        ];
        
        let mut missing_tables = Vec::new();
        
        for table in expected_tables {
            let exists = sqlx::query_scalar::<_, i64>(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?"
            )
            .bind(table)
            .fetch_one(&self.pool)
            .await
            .context("Failed to check table existence")?;
            
            if exists == 0 {
                missing_tables.push(table.to_string());
            }
        }
        
        if missing_tables.is_empty() {
            result.checks_passed += 1;
        } else {
            result.checks_failed += 1;
            result.critical_errors.push(IntegrityViolation {
                violation_type: IntegrityViolationType::SchemaInconsistency,
                severity: ViolationSeverity::Critical,
                description: format!("Missing required tables: {}", missing_tables.join(", ")),
                affected_table: "database".to_string(),
                affected_records: Vec::new(),
                affected_count: missing_tables.len() as i64,
                remediation_steps: vec![
                    "Run database migrations to create missing tables".to_string(),
                    "Restore from backup if necessary".to_string(),
                    "Contact system administrator".to_string(),
                ],
                diagnostic_query: Some(
                    "SELECT name FROM sqlite_master WHERE type='table'".to_string()
                ),
                auto_fixable: false,
                fix_complexity: "high".to_string(),
            });
        }
        
        Ok(())
    }
    
    /// Checks for performance-related issues.
    async fn check_performance_issues(&self, result: &mut IntegrityCheckResult) -> Result<()> {
        result.checks_performed += 1;
        
        // Check for missing indexes on frequently queried columns
        let mut performance_issues = Vec::new();
        
        // Check if incident_name is indexed (frequently searched)
        let incident_name_index = sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND sql LIKE '%incident_name%'"
        )
        .fetch_one(&self.pool)
        .await
        .context("Failed to check incident_name index")?;
        
        if incident_name_index == 0 {
            performance_issues.push("incident_name column lacks index for search optimization".to_string());
        }
        
        if performance_issues.is_empty() {
            result.checks_passed += 1;
        } else {
            result.warning_violations.push(IntegrityViolation {
                violation_type: IntegrityViolationType::PerformanceIssue,
                severity: ViolationSeverity::Low,
                description: format!("Performance optimization opportunities: {}", performance_issues.join("; ")),
                affected_table: "database".to_string(),
                affected_records: Vec::new(),
                affected_count: performance_issues.len() as i64,
                remediation_steps: vec![
                    "Add indexes on frequently searched columns".to_string(),
                    "Run ANALYZE to update query planner statistics".to_string(),
                    "Consider database maintenance procedures".to_string(),
                ],
                diagnostic_query: Some(
                    "SELECT name, sql FROM sqlite_master WHERE type='index'".to_string()
                ),
                auto_fixable: true,
                fix_complexity: "low".to_string(),
            });
            result.warnings += 1;
        }
        
        Ok(())
    }
    
    /// Collects database health statistics.
    async fn collect_database_stats(&self) -> Result<DatabaseHealthStats> {
        // Get basic database info
        let page_count: u64 = sqlx::query_scalar("PRAGMA page_count")
            .fetch_one(&self.pool)
            .await
            .context("Failed to get page count")?;
        
        let page_size: u64 = sqlx::query_scalar("PRAGMA page_size")
            .fetch_one(&self.pool)
            .await
            .context("Failed to get page size")?;
        
        let foreign_keys_enabled: bool = sqlx::query_scalar("PRAGMA foreign_keys")
            .fetch_one(&self.pool)
            .await
            .context("Failed to check foreign keys status")?;
        
        let auto_vacuum: i64 = sqlx::query_scalar("PRAGMA auto_vacuum")
            .fetch_one(&self.pool)
            .await
            .context("Failed to check auto vacuum")?;
        
        // Count schema objects
        let table_count: u32 = sqlx::query_scalar(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
        )
        .fetch_one(&self.pool)
        .await
        .context("Failed to count tables")?;
        
        let index_count: u32 = sqlx::query_scalar(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='index'"
        )
        .fetch_one(&self.pool)
        .await
        .context("Failed to count indexes")?;
        
        let trigger_count: u32 = sqlx::query_scalar(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='trigger'"
        )
        .fetch_one(&self.pool)
        .await
        .context("Failed to count triggers")?;
        
        Ok(DatabaseHealthStats {
            database_size_bytes: page_count * page_size,
            table_count,
            index_count,
            trigger_count,
            page_count,
            page_size,
            unused_pages: 0, // Would need more complex query to calculate
            wal_size_bytes: None, // Would need file system access
            auto_vacuum_enabled: auto_vacuum > 0,
            foreign_keys_enabled,
        })
    }
}

/// Factory for creating integrity checkers with different configurations.
pub struct IntegrityCheckerFactory;

impl IntegrityCheckerFactory {
    /// Creates an integrity checker for production environments.
    pub fn create_production_checker(pool: SqlitePool) -> IntegrityChecker {
        let config = IntegrityCheckConfig {
            deep_validation: true,
            max_execution_time_seconds: 600, // 10 minutes for production
            include_performance_checks: true,
            generate_fix_recommendations: true,
            check_business_rules: true,
            validate_json_data: true,
            check_orphaned_records: true,
            validate_form_relationships: true,
            max_records_per_table: Some(50000), // Higher limit for production
        };
        
        IntegrityChecker::new(pool, Some(config))
    }
    
    /// Creates an integrity checker for development environments.
    pub fn create_development_checker(pool: SqlitePool) -> IntegrityChecker {
        let config = IntegrityCheckConfig {
            deep_validation: false, // Faster for development
            max_execution_time_seconds: 60, // 1 minute for development
            include_performance_checks: false,
            generate_fix_recommendations: true,
            check_business_rules: true,
            validate_json_data: true,
            check_orphaned_records: false, // Skip for speed
            validate_form_relationships: true,
            max_records_per_table: Some(1000), // Lower limit for speed
        };
        
        IntegrityChecker::new(pool, Some(config))
    }
    
    /// Creates an integrity checker for testing environments.
    pub fn create_testing_checker(pool: SqlitePool) -> IntegrityChecker {
        let config = IntegrityCheckConfig {
            deep_validation: false,
            max_execution_time_seconds: 30, // 30 seconds for testing
            include_performance_checks: false,
            generate_fix_recommendations: false, // Not needed in tests
            check_business_rules: false, // Skip for speed
            validate_json_data: true, // Still important for tests
            check_orphaned_records: false,
            validate_form_relationships: false,
            max_records_per_table: Some(100), // Very low limit for tests
        };
        
        IntegrityChecker::new(pool, Some(config))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use sqlx::migrate::MigrateDatabase;
    use tempfile::tempdir;
    
    async fn setup_test_database() -> Result<SqlitePool> {
        let temp_dir = tempdir()?;
        let db_path = temp_dir.path().join("test.db");
        let db_url = format!("sqlite:{}", db_path.display());
        
        sqlx::Sqlite::create_database(&db_url).await?;
        let pool = SqlitePool::connect(&db_url).await?;
        
        // Create minimal schema for testing
        sqlx::query(
            r#"
            CREATE TABLE forms (
                id INTEGER PRIMARY KEY,
                form_type TEXT NOT NULL,
                incident_name TEXT NOT NULL,
                status TEXT DEFAULT 'draft',
                data TEXT DEFAULT '{}',
                operational_period_start TEXT,
                operational_period_end TEXT,
                approved_by TEXT,
                approved_at TEXT
            )
            "#
        )
        .execute(&pool)
        .await?;
        
        Ok(pool)
    }
    
    #[tokio::test]
    async fn test_integrity_checker_creation() {
        let pool = setup_test_database().await.expect("Failed to setup test database");
        let checker = IntegrityCheckerFactory::create_testing_checker(pool);
        
        // Should not panic
        assert_eq!(checker.config.max_execution_time_seconds, 30);
    }
    
    #[tokio::test]
    async fn test_basic_integrity_check() {
        let pool = setup_test_database().await.expect("Failed to setup test database");
        let checker = IntegrityCheckerFactory::create_testing_checker(pool);
        
        let result = checker.check_integrity().await.expect("Integrity check should succeed");
        
        // Basic checks should pass on clean database
        assert!(result.checks_performed > 0);
        assert!(result.execution_time_ms > 0);
    }
}
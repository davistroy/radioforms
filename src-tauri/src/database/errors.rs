/*!
 * Database Error Handling and Custom Error Types for RadioForms
 * 
 * This module provides comprehensive error handling for all database operations
 * with specific error types for different failure scenarios. Following CLAUDE.md
 * principles for production-ready error handling.
 * 
 * Business Logic:
 * - Specific error types for different failure categories
 * - Detailed error context and metadata for debugging
 * - Integration with SQLx error types for comprehensive coverage
 * - User-friendly error messages for frontend display
 * - Comprehensive error recovery and retry logic support
 * 
 * Design Philosophy:
 * - Fail fast with clear error classification
 * - Provide actionable error messages for users
 * - Support automated error recovery where possible
 * - Complete error context for debugging and monitoring
 * - Type-safe error handling throughout the application
 */

use sqlx::Error as SqlxError;
use serde::{Deserialize, Serialize};
use std::fmt;
use chrono::{DateTime, Utc};

/// Comprehensive database error type covering all possible failure scenarios.
/// 
/// Business Logic:
/// - Categorizes errors by type for appropriate handling
/// - Includes detailed context for debugging and recovery
/// - Supports user-friendly error messages for frontend display
/// - Enables automated retry logic for transient errors
/// - Provides comprehensive error metadata for monitoring
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum DatabaseError {
    /// Connection-related errors (pool exhaustion, timeouts, etc.)
    Connection {
        message: String,
        details: Option<String>,
        is_retryable: bool,
        occurred_at: DateTime<Utc>,
    },
    
    /// Transaction errors (rollback, deadlock, isolation failures)
    Transaction {
        message: String,
        transaction_id: Option<String>,
        operation: String,
        is_retryable: bool,
        occurred_at: DateTime<Utc>,
    },
    
    /// Data validation errors (constraint violations, invalid data)
    Validation {
        message: String,
        field: Option<String>,
        value: Option<String>,
        constraint: Option<String>,
        occurred_at: DateTime<Utc>,
    },
    
    /// Data integrity errors (foreign key violations, unique constraints)
    Integrity {
        message: String,
        table: Option<String>,
        column: Option<String>,
        constraint_name: Option<String>,
        occurred_at: DateTime<Utc>,
    },
    
    /// Data not found errors (specific records don't exist)
    NotFound {
        message: String,
        entity_type: String,
        entity_id: String,
        occurred_at: DateTime<Utc>,
    },
    
    /// Concurrency errors (optimistic locking failures, version conflicts)
    Concurrency {
        message: String,
        entity_type: String,
        entity_id: String,
        expected_version: Option<i64>,
        actual_version: Option<i64>,
        occurred_at: DateTime<Utc>,
    },
    
    /// Migration errors (schema changes, version mismatches)
    Migration {
        message: String,
        migration_name: Option<String>,
        version: Option<String>,
        rollback_available: bool,
        occurred_at: DateTime<Utc>,
    },
    
    /// Backup/restore errors (file operations, corruption)
    Backup {
        message: String,
        operation: String, // "backup" or "restore"
        file_path: Option<String>,
        occurred_at: DateTime<Utc>,
    },
    
    /// Performance errors (slow queries, resource exhaustion)
    Performance {
        message: String,
        operation: String,
        duration_ms: u64,
        threshold_ms: u64,
        occurred_at: DateTime<Utc>,
    },
    
    /// Security errors (permission denied, unauthorized access)
    Security {
        message: String,
        operation: String,
        user: Option<String>,
        occurred_at: DateTime<Utc>,
    },
    
    /// Configuration errors (invalid settings, missing parameters)
    Configuration {
        message: String,
        parameter: Option<String>,
        expected_type: Option<String>,
        occurred_at: DateTime<Utc>,
    },
    
    /// Internal database errors (corruption, disk issues)
    Internal {
        message: String,
        error_code: Option<String>,
        recovery_hint: Option<String>,
        occurred_at: DateTime<Utc>,
    },
    
    /// Serialization errors (JSON parsing, data conversion)
    Serialization {
        message: String,
        data_type: String,
        field: Option<String>,
        occurred_at: DateTime<Utc>,
    },
    
    /// Business logic errors (invalid state transitions, rule violations)
    BusinessLogic {
        message: String,
        rule: String,
        entity_type: String,
        entity_id: Option<String>,
        occurred_at: DateTime<Utc>,
    },
}

impl DatabaseError {
    /// Creates a new connection error with comprehensive context.
    pub fn connection(message: impl Into<String>, details: Option<String>, is_retryable: bool) -> Self {
        Self::Connection {
            message: message.into(),
            details,
            is_retryable,
            occurred_at: Utc::now(),
        }
    }
    
    /// Creates a new transaction error with operation context.
    pub fn transaction(message: impl Into<String>, operation: impl Into<String>, is_retryable: bool) -> Self {
        Self::Transaction {
            message: message.into(),
            transaction_id: None,
            operation: operation.into(),
            is_retryable,
            occurred_at: Utc::now(),
        }
    }
    
    /// Creates a new validation error with field context.
    pub fn validation(message: impl Into<String>, field: Option<String>, value: Option<String>) -> Self {
        Self::Validation {
            message: message.into(),
            field,
            value,
            constraint: None,
            occurred_at: Utc::now(),
        }
    }
    
    /// Creates a new integrity error with constraint context.
    pub fn integrity(message: impl Into<String>, table: Option<String>, constraint: Option<String>) -> Self {
        Self::Integrity {
            message: message.into(),
            table,
            column: None,
            constraint_name: constraint,
            occurred_at: Utc::now(),
        }
    }
    
    /// Creates a new not found error with entity context.
    pub fn not_found(entity_type: impl Into<String>, entity_id: impl Into<String>) -> Self {
        let entity_type = entity_type.into();
        let entity_id = entity_id.into();
        Self::NotFound {
            message: format!("{} not found with ID: {}", entity_type, entity_id),
            entity_type,
            entity_id,
            occurred_at: Utc::now(),
        }
    }
    
    /// Creates a new concurrency error with version context.
    pub fn concurrency(
        entity_type: impl Into<String>, 
        entity_id: impl Into<String>,
        expected_version: Option<i64>,
        actual_version: Option<i64>
    ) -> Self {
        let entity_type = entity_type.into();
        let entity_id = entity_id.into();
        let message = match (expected_version, actual_version) {
            (Some(expected), Some(actual)) => {
                format!("{} {} was modified by another user. Expected version: {}, actual version: {}", 
                       entity_type, entity_id, expected, actual)
            },
            _ => {
                format!("{} {} was modified by another user", entity_type, entity_id)
            }
        };
        
        Self::Concurrency {
            message,
            entity_type,
            entity_id,
            expected_version,
            actual_version,
            occurred_at: Utc::now(),
        }
    }
    
    /// Creates a new business logic error with rule context.
    pub fn business_logic(
        message: impl Into<String>,
        rule: impl Into<String>,
        entity_type: impl Into<String>,
        entity_id: Option<String>
    ) -> Self {
        Self::BusinessLogic {
            message: message.into(),
            rule: rule.into(),
            entity_type: entity_type.into(),
            entity_id,
            occurred_at: Utc::now(),
        }
    }
    
    /// Creates a new serialization error with data context.
    pub fn serialization(message: impl Into<String>, data_type: impl Into<String>, field: Option<String>) -> Self {
        Self::Serialization {
            message: message.into(),
            data_type: data_type.into(),
            field,
            occurred_at: Utc::now(),
        }
    }
    
    /// Determines if this error is retryable (transient vs permanent).
    /// 
    /// Business Logic:
    /// - Connection errors may be retryable depending on cause
    /// - Transaction errors (deadlocks) are often retryable
    /// - Validation and integrity errors are never retryable
    /// - Performance errors may be retryable with backoff
    pub fn is_retryable(&self) -> bool {
        match self {
            Self::Connection { is_retryable, .. } => *is_retryable,
            Self::Transaction { is_retryable, .. } => *is_retryable,
            Self::Performance { .. } => true, // Retry with backoff
            Self::Internal { .. } => false, // Usually permanent
            Self::Validation { .. } => false, // Never retryable
            Self::Integrity { .. } => false, // Never retryable
            Self::NotFound { .. } => false, // Entity doesn't exist
            Self::Concurrency { .. } => true, // Retry with updated version
            Self::Migration { .. } => false, // Usually requires manual intervention
            Self::Backup { .. } => true, // May succeed on retry
            Self::Security { .. } => false, // Permission issue
            Self::Configuration { .. } => false, // Setup issue
            Self::Serialization { .. } => false, // Data format issue
            Self::BusinessLogic { .. } => false, // Rule violation
        }
    }
    
    /// Gets the error category for monitoring and metrics.
    pub fn category(&self) -> &'static str {
        match self {
            Self::Connection { .. } => "connection",
            Self::Transaction { .. } => "transaction",
            Self::Validation { .. } => "validation",
            Self::Integrity { .. } => "integrity",
            Self::NotFound { .. } => "not_found",
            Self::Concurrency { .. } => "concurrency",
            Self::Migration { .. } => "migration",
            Self::Backup { .. } => "backup",
            Self::Performance { .. } => "performance",
            Self::Security { .. } => "security",
            Self::Configuration { .. } => "configuration",
            Self::Internal { .. } => "internal",
            Self::Serialization { .. } => "serialization",
            Self::BusinessLogic { .. } => "business_logic",
        }
    }
    
    /// Gets the error severity level for alerting and logging.
    pub fn severity(&self) -> ErrorSeverity {
        match self {
            Self::Internal { .. } => ErrorSeverity::Critical,
            Self::Migration { .. } => ErrorSeverity::Critical,
            Self::Security { .. } => ErrorSeverity::High,
            Self::Integrity { .. } => ErrorSeverity::High,
            Self::Configuration { .. } => ErrorSeverity::High,
            Self::Transaction { .. } => ErrorSeverity::Medium,
            Self::Connection { .. } => ErrorSeverity::Medium,
            Self::Performance { .. } => ErrorSeverity::Medium,
            Self::Backup { .. } => ErrorSeverity::Medium,
            Self::Concurrency { .. } => ErrorSeverity::Low,
            Self::Validation { .. } => ErrorSeverity::Low,
            Self::NotFound { .. } => ErrorSeverity::Low,
            Self::Serialization { .. } => ErrorSeverity::Low,
            Self::BusinessLogic { .. } => ErrorSeverity::Low,
        }
    }
    
    /// Gets a user-friendly error message for frontend display.
    pub fn user_message(&self) -> String {
        match self {
            Self::Connection { .. } => {
                "Unable to connect to the database. Please check your connection and try again.".to_string()
            },
            Self::Transaction { .. } => {
                "The operation could not be completed due to a database conflict. Please try again.".to_string()
            },
            Self::Validation { message, field, .. } => {
                if let Some(field) = field {
                    format!("Invalid value for {}: {}", field, message)
                } else {
                    format!("Invalid data: {}", message)
                }
            },
            Self::Integrity { .. } => {
                "This operation would violate data consistency rules. Please check your data and try again.".to_string()
            },
            Self::NotFound { entity_type, .. } => {
                format!("The requested {} was not found.", entity_type)
            },
            Self::Concurrency { .. } => {
                "This record was modified by another user. Please refresh and try again.".to_string()
            },
            Self::Migration { .. } => {
                "A database update is required. Please contact your administrator.".to_string()
            },
            Self::Backup { operation, .. } => {
                format!("The {} operation failed. Please try again or contact support.", operation)
            },
            Self::Performance { .. } => {
                "The operation is taking longer than expected. Please try again.".to_string()
            },
            Self::Security { .. } => {
                "You do not have permission to perform this operation.".to_string()
            },
            Self::Configuration { .. } => {
                "The application is not properly configured. Please contact your administrator.".to_string()
            },
            Self::Internal { recovery_hint, .. } => {
                match recovery_hint {
                    Some(hint) => format!("An internal error occurred. {}", hint),
                    None => "An internal error occurred. Please contact support.".to_string(),
                }
            },
            Self::Serialization { data_type, .. } => {
                format!("Unable to process {} data. The data may be corrupted.", data_type)
            },
            Self::BusinessLogic { message, .. } => {
                message.clone()
            },
        }
    }
    
    /// Gets technical details for logging and debugging.
    pub fn technical_details(&self) -> String {
        match self {
            Self::Connection { message, details, .. } => {
                match details {
                    Some(details) => format!("{}: {}", message, details),
                    None => message.clone(),
                }
            },
            Self::Transaction { message, operation, transaction_id, .. } => {
                match transaction_id {
                    Some(id) => format!("{} (operation: {}, tx_id: {})", message, operation, id),
                    None => format!("{} (operation: {})", message, operation),
                }
            },
            Self::Validation { message, field, value, constraint, .. } => {
                let mut details = vec![message.clone()];
                if let Some(field) = field {
                    details.push(format!("field: {}", field));
                }
                if let Some(value) = value {
                    details.push(format!("value: {}", value));
                }
                if let Some(constraint) = constraint {
                    details.push(format!("constraint: {}", constraint));
                }
                details.join(", ")
            },
            Self::Integrity { message, table, column, constraint_name, .. } => {
                let mut details = vec![message.clone()];
                if let Some(table) = table {
                    details.push(format!("table: {}", table));
                }
                if let Some(column) = column {
                    details.push(format!("column: {}", column));
                }
                if let Some(constraint) = constraint_name {
                    details.push(format!("constraint: {}", constraint));
                }
                details.join(", ")
            },
            _ => self.to_string(),
        }
    }
}

/// Error severity levels for monitoring and alerting.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ErrorSeverity {
    Low,
    Medium,
    High,
    Critical,
}

impl fmt::Display for ErrorSeverity {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Low => write!(f, "LOW"),
            Self::Medium => write!(f, "MEDIUM"),
            Self::High => write!(f, "HIGH"),
            Self::Critical => write!(f, "CRITICAL"),
        }
    }
}

impl fmt::Display for DatabaseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[{}] {}", self.category().to_uppercase(), self.technical_details())
    }
}

impl std::error::Error for DatabaseError {}

/// Converts SQLx errors to our custom database error types.
/// 
/// Business Logic:
/// - Maps SQLx error types to appropriate DatabaseError variants
/// - Extracts relevant context from SQLx errors
/// - Determines retryability based on error characteristics
/// - Provides comprehensive error classification
impl From<SqlxError> for DatabaseError {
    fn from(error: SqlxError) -> Self {
        match &error {
            SqlxError::Configuration(msg) => Self::Configuration {
                message: msg.to_string(),
                parameter: None,
                expected_type: None,
                occurred_at: Utc::now(),
            },
            SqlxError::Database(db_err) => {
                let message = db_err.message().to_string();
                
                // Check for specific SQLite error patterns
                if message.contains("UNIQUE constraint failed") {
                    Self::Integrity {
                        message: "Duplicate value violates uniqueness constraint".to_string(),
                        table: extract_table_from_constraint(&message),
                        column: extract_column_from_constraint(&message),
                        constraint_name: Some("UNIQUE".to_string()),
                        occurred_at: Utc::now(),
                    }
                } else if message.contains("FOREIGN KEY constraint failed") {
                    Self::Integrity {
                        message: "Foreign key constraint violation".to_string(),
                        table: extract_table_from_constraint(&message),
                        column: None,
                        constraint_name: Some("FOREIGN KEY".to_string()),
                        occurred_at: Utc::now(),
                    }
                } else if message.contains("CHECK constraint failed") {
                    Self::Validation {
                        message: "Data validation check failed".to_string(),
                        field: None,
                        value: None,
                        constraint: Some("CHECK".to_string()),
                        occurred_at: Utc::now(),
                    }
                } else if message.contains("NOT NULL constraint failed") {
                    Self::Validation {
                        message: "Required field cannot be empty".to_string(),
                        field: extract_column_from_constraint(&message),
                        value: None,
                        constraint: Some("NOT NULL".to_string()),
                        occurred_at: Utc::now(),
                    }
                } else {
                    Self::Internal {
                        message,
                        error_code: db_err.code().map(|c| c.to_string()),
                        recovery_hint: Some("Check data integrity and retry".to_string()),
                        occurred_at: Utc::now(),
                    }
                }
            },
            SqlxError::Io(_) => Self::Connection {
                message: "I/O error during database operation".to_string(),
                details: Some(error.to_string()),
                is_retryable: true,
                occurred_at: Utc::now(),
            },
            SqlxError::Protocol(msg) => Self::Connection {
                message: format!("Database protocol error: {}", msg),
                details: None,
                is_retryable: false,
                occurred_at: Utc::now(),
            },
            SqlxError::RowNotFound => Self::NotFound {
                message: "Record not found".to_string(),
                entity_type: "record".to_string(),
                entity_id: "unknown".to_string(),
                occurred_at: Utc::now(),
            },
            SqlxError::TypeNotFound { type_name } => Self::Configuration {
                message: format!("Database type not found: {}", type_name),
                parameter: Some("type_name".to_string()),
                expected_type: Some(type_name.clone()),
                occurred_at: Utc::now(),
            },
            SqlxError::ColumnIndexOutOfBounds { index, len } => Self::Internal {
                message: format!("Column index {} out of bounds (length: {})", index, len),
                error_code: Some("COLUMN_INDEX_OUT_OF_BOUNDS".to_string()),
                recovery_hint: Some("Check query column mapping".to_string()),
                occurred_at: Utc::now(),
            },
            SqlxError::ColumnNotFound(column) => Self::Internal {
                message: format!("Column not found: {}", column),
                error_code: Some("COLUMN_NOT_FOUND".to_string()),
                recovery_hint: Some("Check database schema".to_string()),
                occurred_at: Utc::now(),
            },
            SqlxError::ColumnDecode { index, source } => Self::Serialization {
                message: format!("Failed to decode column {}: {}", index, source),
                data_type: "database_column".to_string(),
                field: Some(format!("column_{}", index)),
                occurred_at: Utc::now(),
            },
            SqlxError::Decode(source) => Self::Serialization {
                message: format!("Data decoding error: {}", source),
                data_type: "query_result".to_string(),
                field: None,
                occurred_at: Utc::now(),
            },
            SqlxError::PoolTimedOut => Self::Connection {
                message: "Database connection pool timed out".to_string(),
                details: Some("All connections are busy".to_string()),
                is_retryable: true,
                occurred_at: Utc::now(),
            },
            SqlxError::PoolClosed => Self::Connection {
                message: "Database connection pool is closed".to_string(),
                details: Some("Pool has been shut down".to_string()),
                is_retryable: false,
                occurred_at: Utc::now(),
            },
            SqlxError::WorkerCrashed => Self::Internal {
                message: "Database worker process crashed".to_string(),
                error_code: Some("WORKER_CRASHED".to_string()),
                recovery_hint: Some("Restart the application".to_string()),
                occurred_at: Utc::now(),
            },
            SqlxError::Migrate(migrate_err) => Self::Migration {
                message: format!("Migration error: {}", migrate_err),
                migration_name: None,
                version: None,
                rollback_available: false,
                occurred_at: Utc::now(),
            },
            _ => Self::Internal {
                message: error.to_string(),
                error_code: None,
                recovery_hint: Some("Check logs for more details".to_string()),
                occurred_at: Utc::now(),
            },
        }
    }
}

/// Extracts table name from SQLite constraint error messages.
fn extract_table_from_constraint(message: &str) -> Option<String> {
    // SQLite error format: "UNIQUE constraint failed: table_name.column_name"
    if let Some(start) = message.find(": ") {
        let constraint_part = &message[start + 2..];
        if let Some(dot_pos) = constraint_part.find('.') {
            return Some(constraint_part[..dot_pos].to_string());
        }
    }
    None
}

/// Extracts column name from SQLite constraint error messages.
fn extract_column_from_constraint(message: &str) -> Option<String> {
    // SQLite error format: "UNIQUE constraint failed: table_name.column_name"
    if let Some(start) = message.find(": ") {
        let constraint_part = &message[start + 2..];
        if let Some(dot_pos) = constraint_part.find('.') {
            return Some(constraint_part[dot_pos + 1..].to_string());
        }
    }
    None
}

/// Result type alias for database operations.
pub type DatabaseResult<T> = Result<T, DatabaseError>;

/// Error context for collecting additional error information.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ErrorContext {
    pub operation: String,
    pub entity_type: Option<String>,
    pub entity_id: Option<String>,
    pub user: Option<String>,
    pub session_id: Option<String>,
    pub request_id: Option<String>,
    pub additional_data: std::collections::HashMap<String, String>,
}

impl ErrorContext {
    pub fn new(operation: impl Into<String>) -> Self {
        Self {
            operation: operation.into(),
            entity_type: None,
            entity_id: None,
            user: None,
            session_id: None,
            request_id: None,
            additional_data: std::collections::HashMap::new(),
        }
    }
    
    pub fn with_entity(mut self, entity_type: impl Into<String>, entity_id: impl Into<String>) -> Self {
        self.entity_type = Some(entity_type.into());
        self.entity_id = Some(entity_id.into());
        self
    }
    
    pub fn with_user(mut self, user: impl Into<String>) -> Self {
        self.user = Some(user.into());
        self
    }
    
    pub fn with_session(mut self, session_id: impl Into<String>) -> Self {
        self.session_id = Some(session_id.into());
        self
    }
    
    pub fn with_data(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.additional_data.insert(key.into(), value.into());
        self
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_creation() {
        let error = DatabaseError::not_found("Form", "123");
        assert_eq!(error.category(), "not_found");
        assert!(!error.is_retryable());
        assert_eq!(error.severity(), ErrorSeverity::Low);
    }

    #[test]
    fn test_concurrency_error() {
        let error = DatabaseError::concurrency("Form", "123", Some(5), Some(7));
        assert_eq!(error.category(), "concurrency");
        assert!(error.is_retryable());
        assert!(error.to_string().contains("Expected version: 5"));
    }

    #[test]
    fn test_user_message() {
        let error = DatabaseError::validation("Invalid email format", Some("email".to_string()), None);
        assert!(error.user_message().contains("Invalid value for email"));
    }

    #[test]
    fn test_extract_table_from_constraint() {
        let message = "UNIQUE constraint failed: forms.incident_number";
        assert_eq!(extract_table_from_constraint(message), Some("forms".to_string()));
    }

    #[test]
    fn test_extract_column_from_constraint() {
        let message = "UNIQUE constraint failed: forms.incident_number";
        assert_eq!(extract_column_from_constraint(message), Some("incident_number".to_string()));
    }
}
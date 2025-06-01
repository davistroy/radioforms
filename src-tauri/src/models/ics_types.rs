/*!
 * ICS Form Type Definitions
 * 
 * This module contains comprehensive data type definitions for all 20 ICS forms
 * based on detailed analysis of FEMA ICS specifications. These types ensure
 * type safety and proper validation for all form operations.
 * 
 * Business Logic:
 * - Type-safe representation of all ICS form field types
 * - Comprehensive validation support for ICS compliance
 * - Form relationship management and dependency tracking
 * - Support for multi-format exports including ICS-DES
 * 
 * Design Philosophy:
 * - Zero technical debt - fully implemented, not placeholder types
 * - Comprehensive documentation for all structures
 * - Type safety prevents invalid form data
 * - Clear separation of concerns between form types
 */

use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc, NaiveDate, NaiveTime};
use std::collections::HashMap;

/// Universal header structure present in all ICS forms.
/// 
/// Business Logic:
/// - Provides consistent identification across all form types
/// - Supports incident management tracking and coordination
/// - Enables proper form routing and archival processes
/// 
/// Used by all 20 ICS forms for consistent metadata management.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ICSFormHeader {
    /// Name of the incident this form relates to (required for all forms)
    pub incident_name: String,
    
    /// Operational period this form covers (used by most forms)
    /// Format: "From: YYYY-MM-DD HHMM To: YYYY-MM-DD HHMM"
    pub operational_period: Option<DateTimeRange>,
    
    /// Incident number for cross-referencing (optional but recommended)
    /// Format: State-Year-Number (e.g., "CA-2025-123456")
    pub incident_number: Option<String>,
    
    /// Form version for tracking template updates
    pub form_version: Option<String>,
    
    /// When the form was prepared
    pub prepared_date_time: DateTime<Utc>,
    
    /// Page number information for multi-page forms
    pub page_info: Option<PageInfo>,
}

/// Date and time range for operational periods.
/// 
/// Business Logic:
/// - Supports ICS operational period concept (typically 12-24 hour periods)
/// - Validates that end time is after start time
/// - Used across multiple forms for time-bounded operations
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct DateTimeRange {
    /// Start of the operational period
    pub from: DateTime<Utc>,
    
    /// End of the operational period
    pub to: DateTime<Utc>,
}

impl DateTimeRange {
    /// Creates a new DateTimeRange with validation.
    /// 
    /// Business Logic:
    /// - Ensures start time is before end time
    /// - Validates operational period duration is reasonable (max 72 hours)
    /// - Prevents creation of invalid time ranges
    pub fn new(from: DateTime<Utc>, to: DateTime<Utc>) -> anyhow::Result<Self> {
        if from >= to {
            return Err(anyhow::anyhow!("Start time must be before end time"));
        }
        
        let duration = to - from;
        if duration.num_hours() > 72 {
            return Err(anyhow::anyhow!("Operational period cannot exceed 72 hours"));
        }
        
        Ok(Self { from, to })
    }
    
    /// Gets the duration of this time range in hours.
    pub fn duration_hours(&self) -> i64 {
        (self.to - self.from).num_hours()
    }
}

/// Page numbering information for forms.
/// 
/// Business Logic:
/// - Supports both simple page numbering and IAP page numbering
/// - Enables proper document assembly and cross-referencing
/// - Required for forms that commonly span multiple pages
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct PageInfo {
    /// Simple page number (e.g., "1 of 3")
    pub page_number: Option<String>,
    
    /// IAP-specific page numbering for Incident Action Plans
    pub iap_page_number: Option<String>,
}

/// Universal footer structure for form preparation and approval.
/// 
/// Business Logic:
/// - Tracks who prepared and approved each form
/// - Supports digital signature workflows
/// - Provides audit trail for form accountability
/// - Required for ICS compliance and legal documentation
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ICSFormFooter {
    /// Person who prepared the form (required)
    pub prepared_by: PreparedBy,
    
    /// Person who approved the form (if applicable)
    pub approved_by: Option<ApprovedBy>,
}

/// Preparation information for forms.
/// 
/// Business Logic:
/// - Identifies the person responsible for form accuracy
/// - Links to ICS organizational position for accountability
/// - Supports both manual and digital signature processes
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct PreparedBy {
    /// Full name of the preparer
    pub name: String,
    
    /// ICS position/title of the preparer
    pub position_title: String,
    
    /// Digital signature data (if applicable)
    pub signature: Option<DigitalSignature>,
    
    /// When the form was prepared (if different from header timestamp)
    pub date_time: Option<DateTime<Utc>>,
}

/// Approval information for forms requiring approval.
/// 
/// Business Logic:
/// - Documents formal approval of form content
/// - Required for certain forms (ICS-202, 215, etc.)
/// - Supports approval workflow tracking
/// - Links to organizational authority structure
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ApprovedBy {
    /// Full name of the approver
    pub name: String,
    
    /// ICS position/title of the approver (if applicable)
    pub position_title: Option<String>,
    
    /// Digital signature data (if applicable)
    pub signature: Option<DigitalSignature>,
    
    /// When the form was approved
    pub date_time: Option<DateTime<Utc>>,
}

/// Digital signature information.
/// 
/// Business Logic:
/// - Supports various signature types for different deployment scenarios
/// - Provides non-repudiation for critical forms
/// - Integrates with digital signature infrastructure
/// - Maintains audit trail for signature verification
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct DigitalSignature {
    /// The actual signature data (varies by type)
    pub signature_data: Vec<u8>,
    
    /// Type of signature used
    pub signature_type: SignatureType,
    
    /// When the signature was applied
    pub timestamp: DateTime<Utc>,
}

/// Types of signatures supported by the system.
/// 
/// Business Logic:
/// - Digital: PKI-based cryptographic signature
/// - Electronic: Simple electronic acceptance (name/pin)
/// - Handwritten: Scanned or drawn signature image
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum SignatureType {
    /// PKI-based cryptographic digital signature
    Digital,
    
    /// Electronic signature (name + PIN or similar)
    Electronic,
    
    /// Handwritten signature (image data)
    Handwritten,
}

/// Person with position information used throughout ICS forms.
/// 
/// Business Logic:
/// - Standard person identification pattern used across all forms
/// - Links individuals to ICS organizational positions
/// - Supports agency affiliation tracking
/// - Enables contact information management
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct PersonPosition {
    /// Full name of the person
    pub name: String,
    
    /// ICS position or job title
    pub position: String,
    
    /// Agency or organization affiliation (optional)
    pub agency: Option<String>,
    
    /// Contact information (phone, radio, etc.)
    pub contact_info: Option<String>,
}

/// Field type enumeration for form field definitions.
/// 
/// Business Logic:
/// - Defines all field types found across ICS forms
/// - Enables proper validation and input controls
/// - Supports specialized field types (radio frequencies, coordinates)
/// - Provides metadata for UI generation
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum FieldType {
    /// Single-line or multi-line text field
    Text {
        max_length: Option<usize>,
        multiline: bool,
    },
    
    /// Numeric field with optional constraints
    Number {
        min: Option<f64>,
        max: Option<f64>,
        decimal_places: Option<u8>,
    },
    
    /// Date field (YYYY-MM-DD format)
    Date,
    
    /// Time field (HH:MM format)
    Time,
    
    /// Combined date and time field
    DateTime,
    
    /// Boolean checkbox or yes/no field
    Boolean,
    
    /// Enumerated values (dropdown or radio buttons)
    Enum {
        options: Vec<String>,
        allow_multiple: bool,
    },
    
    /// Currency amount (USD)
    Currency,
    
    /// Percentage value (0-100)
    Percentage,
    
    /// Geographic coordinates in various formats
    Coordinates {
        format: CoordinateFormat,
    },
    
    /// Radio frequency in MHz
    FrequencyMHz,
    
    /// Radio tone/NAC identifier
    RadioTone,
}

/// Coordinate format types supported by ICS forms.
/// 
/// Business Logic:
/// - Different coordinate systems used in emergency management
/// - Supports interoperability with various mapping systems
/// - Enables accurate location reporting and resource deployment
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum CoordinateFormat {
    /// Decimal degrees latitude/longitude
    LatitudeLongitude,
    
    /// Universal Transverse Mercator coordinate system
    UTM,
    
    /// US National Grid coordinate system
    USNationalGrid,
    
    /// Legal land description (township, range, section)
    LegalDescription,
}

/// Validation rule definition for form fields.
/// 
/// Business Logic:
/// - Defines validation requirements for ICS compliance
/// - Supports complex business rules and cross-field validation
/// - Enables real-time validation feedback
/// - Provides clear error messaging for users
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationRule {
    /// Unique identifier for the validation rule
    pub rule_id: String,
    
    /// Type of validation to perform
    pub rule_type: ValidationType,
    
    /// Fields this rule applies to
    pub fields: Vec<String>,
    
    /// Condition that triggers the validation
    pub condition: ValidationCondition,
    
    /// Error message to display when validation fails
    pub error_message: String,
    
    /// Severity level of validation failure
    pub severity: ValidationSeverity,
}

/// Types of validation that can be performed.
/// 
/// Business Logic:
/// - Required: Field must have a value
/// - Format: Field must match a specific pattern
/// - Range: Numeric field must be within specified bounds
/// - CrossField: Validation depends on other field values
/// - BusinessRule: Complex ICS-specific business logic
/// - Conditional: Validation only applies under certain conditions
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ValidationType {
    Required,
    Format,
    Range,
    CrossField,
    BusinessRule,
    Conditional,
}

/// Conditions for when validation rules apply.
/// 
/// Business Logic:
/// - Always: Rule always applies
/// - FieldEquals: Rule applies when another field has specific value
/// - FieldNotEmpty: Rule applies when another field is not empty
/// - FormStatus: Rule applies based on form status
/// - Custom: Complex conditional logic
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ValidationCondition {
    Always,
    FieldEquals { field: String, value: String },
    FieldNotEmpty { field: String },
    FormStatus { status: String },
    Custom { expression: String },
}

/// Validation severity levels.
/// 
/// Business Logic:
/// - Error: Prevents form submission/completion
/// - Warning: Allows submission but shows warning
/// - Info: Informational message only
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ValidationSeverity {
    Error,
    Warning,
    Info,
}

/// Form relationship definitions for tracking dependencies.
/// 
/// Business Logic:
/// - Models relationships between ICS forms
/// - Supports workflow management and data consistency
/// - Enables automatic form updates when related data changes
/// - Provides foundation for Incident Action Plan assembly
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FormRelationship {
    /// Source form ID
    pub form_id: String,
    
    /// Related form ID
    pub related_form_id: String,
    
    /// Type of relationship
    pub relationship_type: RelationshipType,
    
    /// How critical this dependency is
    pub dependency_strength: DependencyStrength,
}

/// Types of relationships between forms.
/// 
/// Business Logic:
/// - Feeds: Data from one form feeds another (ICS-203 → ICS-207)
/// - Requires: Form cannot be completed without another (ICS-204 → ICS-205)
/// - Updates: Form provides status updates to another (ICS-210 → ICS-219)
/// - References: Form references data from another
/// - Supersedes: New form replaces old version
/// - Extends: Additional pages of the same form
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RelationshipType {
    Feeds,
    Requires,
    Updates,
    References,
    Supersedes,
    Extends,
}

/// Strength of dependency between forms.
/// 
/// Business Logic:
/// - Required: Cannot function without the related form
/// - Recommended: Works better with the related form
/// - Optional: May reference the related form
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum DependencyStrength {
    Required,
    Recommended,
    Optional,
}

/// Enhanced form status enumeration for complex workflows.
/// 
/// Business Logic:
/// - Extends basic Draft/Completed/Final with workflow states
/// - Supports approval processes and transmission tracking
/// - Enables proper lifecycle management for all form types
/// - Provides audit trail for form state changes
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum EnhancedFormStatus {
    /// Form is being created or edited
    Draft,
    
    /// Form is actively being worked on
    InProgress,
    
    /// Form is complete but awaiting approval
    PendingApproval,
    
    /// Form has been approved by appropriate authority
    Approved,
    
    /// Form has been published/distributed
    Published,
    
    /// Form has been transmitted via radio or other means
    Transmitted,
    
    /// Form has been received by intended recipient
    Received,
    
    /// Reply has been sent (for message forms)
    Replied,
    
    /// Form process is complete
    Completed,
    
    /// Form has been replaced by newer version
    Superseded,
    
    /// Form has been archived for historical record
    Archived,
    
    /// Form has been cancelled/voided
    Cancelled,
}

/// Form lifecycle tracking information.
/// 
/// Business Logic:
/// - Tracks complete history of form state changes
/// - Provides audit trail for accountability
/// - Enables workflow process analysis
/// - Supports automated workflow triggers
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FormLifecycle {
    /// Current status of the form
    pub status: EnhancedFormStatus,
    
    /// When the form was initially created
    pub created_at: DateTime<Utc>,
    
    /// When the form was last updated
    pub updated_at: DateTime<Utc>,
    
    /// Complete history of status changes
    pub status_history: Vec<StatusChange>,
    
    /// Current position in the workflow process
    pub workflow_position: WorkflowPosition,
}

/// Record of a status change event.
/// 
/// Business Logic:
/// - Documents who changed the status and when
/// - Provides reason for status change
/// - Enables accountability and audit capabilities
/// - Supports workflow analysis and optimization
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StatusChange {
    /// Previous status
    pub from_status: EnhancedFormStatus,
    
    /// New status
    pub to_status: EnhancedFormStatus,
    
    /// When the change occurred
    pub timestamp: DateTime<Utc>,
    
    /// Who made the change
    pub changed_by: String,
    
    /// Reason for the change (optional)
    pub reason: Option<String>,
}

/// Workflow position within ICS process.
/// 
/// Business Logic:
/// - Maps to standard ICS planning process phases
/// - Enables workflow automation and routing
/// - Provides context for form validation requirements
/// - Supports process metrics and analysis
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum WorkflowPosition {
    /// Initial form creation phase
    Initial,
    
    /// Planning process phase
    Planning,
    
    /// Approval/review phase
    Approval,
    
    /// Distribution/publication phase
    Distribution,
    
    /// Implementation/execution phase
    Implementation,
    
    /// Archive/historical record phase
    Archive,
}

/// Export configuration for different output formats.
/// 
/// Business Logic:
/// - Configures how forms are exported to different formats
/// - Supports PDF, JSON, ICS-DES, and other formats
/// - Enables customization of export parameters
/// - Provides format-specific configuration options
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExportConfiguration {
    /// Output format type
    pub format: ExportFormat,
    
    /// Template to use for formatted exports (optional)
    pub template: Option<String>,
    
    /// Field filters for selective export
    pub filters: Vec<FieldFilter>,
    
    /// ICS-DES specific configuration
    pub ics_des_config: Option<IcsDESConfig>,
}

/// Supported export formats.
/// 
/// Business Logic:
/// - PDF: FEMA-compliant form layouts
/// - JSON: Machine-readable structured data
/// - IcsDES: Radio transmission format
/// - CSV: Tabular data export
/// - XML: Structured markup format
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ExportFormat {
    PDF,
    JSON,
    IcsDES,
    CSV,
    XML,
}

/// Field filter for selective export.
/// 
/// Business Logic:
/// - Allows including/excluding specific fields
/// - Supports sensitive information filtering
/// - Enables format-specific field selection
/// - Provides export customization capability
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FieldFilter {
    /// Field name or pattern
    pub field_pattern: String,
    
    /// Whether to include or exclude the field
    pub include: bool,
    
    /// Transformation to apply to the field value
    pub transform: Option<FieldTransform>,
}

/// Field value transformation for export.
/// 
/// Business Logic:
/// - Redact: Replace with placeholder text
/// - Truncate: Limit to specified length
/// - Format: Apply formatting rules
/// - Encrypt: Apply encryption for sensitive data
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum FieldTransform {
    Redact { placeholder: String },
    Truncate { max_length: usize },
    Format { pattern: String },
    Encrypt { method: String },
}

/// ICS-DES format configuration for radio transmission.
/// 
/// Business Logic:
/// - Configures format parameters for radio compatibility
/// - Ensures message fits within transmission constraints
/// - Provides error detection and correction options
/// - Supports various radio system requirements
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IcsDESConfig {
    /// Maximum line length for radio transmission (typically 69 chars)
    pub max_line_length: usize,
    
    /// Prefix for each line (e.g., "ICS213:")
    pub line_prefix: String,
    
    /// Whether to include field separators
    pub field_separators: bool,
    
    /// Whether to include metadata in transmission
    pub include_metadata: bool,
    
    /// Error correction method
    pub error_correction: Option<ErrorCorrectionMethod>,
}

/// Error correction methods for radio transmission.
/// 
/// Business Logic:
/// - Checksum: Simple checksum verification
/// - CRC: Cyclic redundancy check
/// - Hamming: Forward error correction
/// - None: No error correction
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ErrorCorrectionMethod {
    Checksum,
    CRC,
    Hamming,
    None,
}
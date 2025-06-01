/*!
 * Form Template Schema Definitions
 * 
 * This module defines the complete JSON schema structure for ICS form templates.
 * The schema supports all field types, validation rules, and metadata required
 * for dynamic form generation and validation.
 * 
 * Business Logic:
 * - Comprehensive field type support for all ICS forms
 * - Hierarchical section and field organization
 * - Flexible validation rule definitions
 * - Conditional logic and dependencies
 * - Template versioning and metadata
 * 
 * Design Philosophy:
 * - JSON-first design for maximum flexibility
 * - Type-safe Rust structures with serde
 * - Comprehensive validation support
 * - Extensible field type system
 * - Production-ready template loading
 */

use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use std::collections::HashMap;

/// Root template structure for ICS form definitions.
/// 
/// Business Logic:
/// - Defines complete form structure and behavior
/// - Includes metadata for template management
/// - Supports versioning and compatibility checking
/// - Contains all sections, fields, and validation rules
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FormTemplate {
    /// Unique identifier for this template
    pub template_id: String,
    
    /// ICS form type (ICS-201, ICS-202, etc.)
    pub form_type: String,
    
    /// Template version for compatibility tracking
    pub version: String,
    
    /// Human-readable form title
    pub title: String,
    
    /// Detailed form description
    pub description: String,
    
    /// Template metadata and configuration
    pub metadata: TemplateMetadata,
    
    /// Form sections containing fields
    pub sections: Vec<FormSection>,
    
    /// Global validation rules
    pub validation_rules: Vec<ValidationRule>,
    
    /// Conditional logic rules
    pub conditional_logic: Vec<ConditionalRule>,
    
    /// Default values for fields
    pub defaults: HashMap<String, FieldValue>,
}

/// Template metadata and configuration information.
/// 
/// Business Logic:
/// - Provides template management information
/// - Supports version tracking and compatibility
/// - Includes authoring and modification tracking
/// - Contains template-specific configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TemplateMetadata {
    /// When this template was created
    pub created_at: DateTime<Utc>,
    
    /// When this template was last modified
    pub updated_at: DateTime<Utc>,
    
    /// Template author information
    pub author: String,
    
    /// Template compatibility version
    pub compatibility_version: String,
    
    /// Minimum application version required
    pub min_app_version: String,
    
    /// Template-specific tags for categorization
    pub tags: Vec<String>,
    
    /// Template status (draft, published, deprecated)
    pub status: TemplateStatus,
    
    /// Additional metadata as key-value pairs
    pub custom_metadata: HashMap<String, String>,
}

/// Form section containing related fields.
/// 
/// Business Logic:
/// - Organizes fields into logical groups
/// - Supports nested sections for complex forms
/// - Provides section-level validation and display rules
/// - Enables conditional section visibility
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FormSection {
    /// Unique section identifier within the form
    pub section_id: String,
    
    /// Display title for the section
    pub title: String,
    
    /// Optional section description
    pub description: Option<String>,
    
    /// Display order within the form
    pub order: u32,
    
    /// Whether this section is required
    pub required: bool,
    
    /// Whether this section is repeatable
    pub repeatable: bool,
    
    /// Maximum number of repetitions (if repeatable)
    pub max_repetitions: Option<u32>,
    
    /// Fields contained in this section
    pub fields: Vec<FormField>,
    
    /// Nested subsections
    pub subsections: Vec<FormSection>,
    
    /// Section-specific validation rules
    pub validation_rules: Vec<ValidationRule>,
    
    /// Conditional visibility rules
    pub conditional_display: Option<ConditionalRule>,
}

/// Individual form field definition.
/// 
/// Business Logic:
/// - Defines field behavior and validation
/// - Supports all ICS form field types
/// - Includes display and interaction configuration
/// - Provides field-level help and validation messages
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FormField {
    /// Unique field identifier within the form
    pub field_id: String,
    
    /// Display label for the field
    pub label: String,
    
    /// Field data type and configuration
    pub field_type: FieldType,
    
    /// Whether this field is required
    pub required: bool,
    
    /// Default value for the field
    pub default_value: Option<FieldValue>,
    
    /// Field placeholder text
    pub placeholder: Option<String>,
    
    /// Help text for the field
    pub help_text: Option<String>,
    
    /// Field validation rules
    pub validation_rules: Vec<ValidationRule>,
    
    /// Conditional visibility rules
    pub conditional_display: Option<ConditionalRule>,
    
    /// Display order within the section
    pub order: u32,
    
    /// Whether the field is readonly
    pub readonly: bool,
    
    /// CSS classes for styling
    pub css_classes: Vec<String>,
    
    /// Field-specific attributes
    pub attributes: HashMap<String, String>,
}

/// Field type definitions supporting all ICS form requirements.
/// 
/// Business Logic:
/// - Comprehensive support for all ICS field types
/// - Type-specific validation and display rules
/// - Flexible configuration for each type
/// - Extensible for future field types
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum FieldType {
    /// Single-line text input
    Text {
        max_length: Option<u32>,
        min_length: Option<u32>,
        pattern: Option<String>,
    },
    
    /// Multi-line text area
    Textarea {
        max_length: Option<u32>,
        rows: Option<u32>,
        cols: Option<u32>,
    },
    
    /// Numeric input
    Number {
        min: Option<f64>,
        max: Option<f64>,
        step: Option<f64>,
        decimal_places: Option<u32>,
    },
    
    /// Date picker
    Date {
        min_date: Option<String>,
        max_date: Option<String>,
        format: Option<String>,
    },
    
    /// Time picker
    Time {
        format: Option<String>,
        min_time: Option<String>,
        max_time: Option<String>,
    },
    
    /// Date and time picker
    DateTime {
        min_datetime: Option<String>,
        max_datetime: Option<String>,
        format: Option<String>,
    },
    
    /// Dropdown selection
    Select {
        options: Vec<SelectOption>,
        multiple: bool,
        searchable: bool,
    },
    
    /// Radio button group
    Radio {
        options: Vec<SelectOption>,
        inline: bool,
    },
    
    /// Checkbox group
    Checkbox {
        options: Vec<SelectOption>,
        inline: bool,
    },
    
    /// Single checkbox (boolean)
    BooleanCheckbox {
        default_checked: bool,
    },
    
    /// Email input with validation
    Email {
        max_length: Option<u32>,
    },
    
    /// Phone number input
    Phone {
        format: Option<String>,
        country_code: Option<String>,
    },
    
    /// Geographic coordinates
    Coordinates {
        format: CoordinateFormat,
        precision: Option<u32>,
    },
    
    /// Radio frequency
    RadioFrequency {
        min_frequency: Option<f64>,
        max_frequency: Option<f64>,
        unit: FrequencyUnit,
    },
    
    /// File upload
    File {
        allowed_types: Vec<String>,
        max_size_mb: Option<u32>,
        multiple: bool,
    },
    
    /// Signature field
    Signature {
        width: Option<u32>,
        height: Option<u32>,
    },
    
    /// ICS organizational position
    IcsPosition {
        allowed_positions: Vec<String>,
    },
    
    /// Person information
    PersonInfo {
        required_fields: Vec<PersonField>,
    },
    
    /// Address information
    Address {
        country: Option<String>,
        required_fields: Vec<AddressField>,
    },
    
    /// Table/grid input
    Table {
        columns: Vec<TableColumn>,
        min_rows: Option<u32>,
        max_rows: Option<u32>,
    },
    
    /// Custom field type for extensibility
    Custom {
        custom_type: String,
        configuration: HashMap<String, FieldValue>,
    },
}

/// Select option for dropdown, radio, and checkbox fields.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SelectOption {
    pub value: String,
    pub label: String,
    pub disabled: bool,
    pub group: Option<String>,
}

/// Coordinate format enumeration.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CoordinateFormat {
    DecimalDegrees,
    DegreesMinutesSeconds,
    Utm,
    Mgrs,
}

/// Frequency unit enumeration.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "uppercase")]
pub enum FrequencyUnit {
    Hz,
    Khz,
    Mhz,
    Ghz,
}

/// Person field requirements.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum PersonField {
    Name,
    Position,
    Agency,
    Phone,
    Email,
    RadioCallsign,
}

/// Address field requirements.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum AddressField {
    Street,
    City,
    State,
    PostalCode,
    Country,
}

/// Table column definition.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TableColumn {
    pub column_id: String,
    pub title: String,
    pub field_type: FieldType,
    pub required: bool,
    pub width: Option<String>,
}

/// Field value that can hold any supported data type.
/// 
/// Business Logic:
/// - Type-safe storage for all field values
/// - JSON serialization support
/// - Validation-friendly structure
/// - Extensible for new value types
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(untagged)]
pub enum FieldValue {
    String(String),
    Number(f64),
    Boolean(bool),
    Array(Vec<FieldValue>),
    Object(HashMap<String, FieldValue>),
    Null,
}

/// Validation rule definition.
/// 
/// Business Logic:
/// - Flexible validation rule system
/// - Support for all common validation patterns
/// - Custom error messages
/// - Conditional validation rules
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationRule {
    /// Unique rule identifier
    pub rule_id: String,
    
    /// Rule type and configuration
    pub rule_type: ValidationRuleType,
    
    /// Error message for validation failure
    pub error_message: String,
    
    /// Warning message (non-blocking)
    pub warning_message: Option<String>,
    
    /// Fields this rule applies to
    pub target_fields: Vec<String>,
    
    /// Conditional application of this rule
    pub condition: Option<ConditionalRule>,
}

/// Validation rule types.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum ValidationRuleType {
    Required,
    MinLength { min: u32 },
    MaxLength { max: u32 },
    Pattern { regex: String },
    Range { min: f64, max: f64 },
    Email,
    Phone,
    Url,
    Date,
    Time,
    DateTime,
    Coordinates,
    RadioFrequency,
    Custom { validator: String, config: HashMap<String, FieldValue> },
}

/// Conditional logic rule.
/// 
/// Business Logic:
/// - Supports complex conditional logic
/// - Field visibility and requirement rules
/// - Dynamic form behavior
/// - Validation rule conditions
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConditionalRule {
    /// Rule identifier
    pub rule_id: String,
    
    /// Condition expression
    pub condition: Condition,
    
    /// Actions to perform when condition is true
    pub actions: Vec<ConditionalAction>,
}

/// Condition expression for conditional logic.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum Condition {
    FieldEquals { field: String, value: FieldValue },
    FieldNotEquals { field: String, value: FieldValue },
    FieldEmpty { field: String },
    FieldNotEmpty { field: String },
    FieldGreaterThan { field: String, value: f64 },
    FieldLessThan { field: String, value: f64 },
    FieldContains { field: String, value: String },
    And { conditions: Vec<Condition> },
    Or { conditions: Vec<Condition> },
    Not { condition: Box<Condition> },
}

/// Actions to perform based on conditions.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum ConditionalAction {
    ShowField { field: String },
    HideField { field: String },
    RequireField { field: String },
    UnrequireField { field: String },
    SetFieldValue { field: String, value: FieldValue },
    ShowSection { section: String },
    HideSection { section: String },
}

/// Template status enumeration.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TemplateStatus {
    Draft,
    Published,
    Deprecated,
    Archived,
}
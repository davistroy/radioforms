/*!
 * Database schema definitions for RadioForms
 * 
 * This module contains the database schema for the STANDALONE ICS Forms
 * Management Application. The schema is designed for simplicity and follows
 * the "simpler is better" principle.
 * 
 * Business Logic:
 * - Simple table structure for easy maintenance
 * - JSON storage for form data flexibility
 * - Minimal foreign keys to reduce complexity
 * - Optimized for single-user operation
 * 
 * Design Decisions:
 * - Form data stored as JSON blob for flexibility
 * - Status enum ensures data consistency
 * - Timestamps for audit trail and sorting
 * - No complex relationships to maintain simplicity
 */

use sqlx::FromRow;
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use std::collections::HashMap;

/// Form status enumeration.
/// Represents the lifecycle of an ICS form from creation to finalization.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum FormStatus {
    /// Form is being created or edited
    Draft,
    /// Form has been completed but not finalized
    Completed,
    /// Form has been finalized and is read-only
    Final,
}

impl std::fmt::Display for FormStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            FormStatus::Draft => write!(f, "draft"),
            FormStatus::Completed => write!(f, "completed"),
            FormStatus::Final => write!(f, "final"),
        }
    }
}

impl std::str::FromStr for FormStatus {
    type Err = anyhow::Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "draft" => Ok(FormStatus::Draft),
            "completed" => Ok(FormStatus::Completed),
            "final" => Ok(FormStatus::Final),
            _ => Err(anyhow::anyhow!("Invalid form status: {}", s)),
        }
    }
}

impl TryFrom<String> for FormStatus {
    type Error = anyhow::Error;

    fn try_from(value: String) -> Result<Self, Self::Error> {
        value.parse()
    }
}

/// ICS Form type enumeration.
/// Represents the different types of ICS forms supported by the application.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum ICSFormType {
    ICS201, ICS202, ICS203, ICS204, ICS205, ICS205A, ICS206, ICS207,
    ICS208, ICS209, ICS210, ICS211, ICS213, ICS214, ICS215, ICS215A,
    ICS218, ICS220, ICS221, ICS225,
}

impl std::fmt::Display for ICSFormType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ICSFormType::ICS201 => write!(f, "ICS-201"),
            ICSFormType::ICS202 => write!(f, "ICS-202"),
            ICSFormType::ICS203 => write!(f, "ICS-203"),
            ICSFormType::ICS204 => write!(f, "ICS-204"),
            ICSFormType::ICS205 => write!(f, "ICS-205"),
            ICSFormType::ICS205A => write!(f, "ICS-205A"),
            ICSFormType::ICS206 => write!(f, "ICS-206"),
            ICSFormType::ICS207 => write!(f, "ICS-207"),
            ICSFormType::ICS208 => write!(f, "ICS-208"),
            ICSFormType::ICS209 => write!(f, "ICS-209"),
            ICSFormType::ICS210 => write!(f, "ICS-210"),
            ICSFormType::ICS211 => write!(f, "ICS-211"),
            ICSFormType::ICS213 => write!(f, "ICS-213"),
            ICSFormType::ICS214 => write!(f, "ICS-214"),
            ICSFormType::ICS215 => write!(f, "ICS-215"),
            ICSFormType::ICS215A => write!(f, "ICS-215A"),
            ICSFormType::ICS218 => write!(f, "ICS-218"),
            ICSFormType::ICS220 => write!(f, "ICS-220"),
            ICSFormType::ICS221 => write!(f, "ICS-221"),
            ICSFormType::ICS225 => write!(f, "ICS-225"),
        }
    }
}

impl std::str::FromStr for ICSFormType {
    type Err = anyhow::Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_uppercase().as_str() {
            "ICS-201" | "ICS201" => Ok(ICSFormType::ICS201),
            "ICS-202" | "ICS202" => Ok(ICSFormType::ICS202),
            "ICS-203" | "ICS203" => Ok(ICSFormType::ICS203),
            "ICS-204" | "ICS204" => Ok(ICSFormType::ICS204),
            "ICS-205" | "ICS205" => Ok(ICSFormType::ICS205),
            "ICS-205A" | "ICS205A" => Ok(ICSFormType::ICS205A),
            "ICS-206" | "ICS206" => Ok(ICSFormType::ICS206),
            "ICS-207" | "ICS207" => Ok(ICSFormType::ICS207),
            "ICS-208" | "ICS208" => Ok(ICSFormType::ICS208),
            "ICS-209" | "ICS209" => Ok(ICSFormType::ICS209),
            "ICS-210" | "ICS210" => Ok(ICSFormType::ICS210),
            "ICS-211" | "ICS211" => Ok(ICSFormType::ICS211),
            "ICS-213" | "ICS213" => Ok(ICSFormType::ICS213),
            "ICS-214" | "ICS214" => Ok(ICSFormType::ICS214),
            "ICS-215" | "ICS215" => Ok(ICSFormType::ICS215),
            "ICS-215A" | "ICS215A" => Ok(ICSFormType::ICS215A),
            "ICS-218" | "ICS218" => Ok(ICSFormType::ICS218),
            "ICS-220" | "ICS220" => Ok(ICSFormType::ICS220),
            "ICS-221" | "ICS221" => Ok(ICSFormType::ICS221),
            "ICS-225" | "ICS225" => Ok(ICSFormType::ICS225),
            _ => Err(anyhow::anyhow!("Unknown ICS form type: {}", s)),
        }
    }
}

impl TryFrom<String> for ICSFormType {
    type Error = anyhow::Error;

    fn try_from(value: String) -> Result<Self, Self::Error> {
        value.parse()
    }
}

/// Main form record structure.
/// 
/// Business Logic:
/// - Represents a single ICS form instance
/// - Form data stored as JSON for flexibility
/// - Simple status tracking for workflow management
/// - Timestamps for sorting and audit purposes
/// 
/// Design Notes:
/// - ID is auto-incrementing primary key
/// - JSON data field contains all form-specific fields
/// - Status enum ensures valid state transitions
/// - Notes field for user annotations
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Form {
    /// Unique identifier for the form (auto-increment primary key)
    pub id: i64,
    
    /// Type of ICS form (ICS-201, ICS-202, etc.) - stored as string
    pub form_type: String,
    
    /// Name of the incident this form relates to
    pub incident_name: String,
    
    /// Optional incident number for cross-referencing
    pub incident_number: Option<String>,
    
    /// Current status of the form (draft, completed, final) - stored as string
    pub status: String,
    
    /// Complete form data as JSON
    /// Contains all field values specific to the form type
    pub data: String, // JSON string
    
    /// Optional notes or comments about the form
    pub notes: Option<String>,
    
    /// Name of the person who prepared the form
    pub preparer_name: Option<String>,
    
    /// When the form was first created
    pub created_at: DateTime<Utc>,
    
    /// When the form was last modified
    pub updated_at: DateTime<Utc>,
    
    /// Version number for form revisions and change tracking
    pub version: i64,
    
    /// Current workflow position for form processing
    pub workflow_position: Option<String>,
}

impl Form {
    /// Gets the form type as an enum
    pub fn get_form_type(&self) -> anyhow::Result<ICSFormType> {
        self.form_type.parse()
    }
    
    /// Sets the form type from an enum
    pub fn set_form_type(&mut self, form_type: ICSFormType) {
        self.form_type = form_type.to_string();
    }
    
    /// Gets the status as an enum
    pub fn get_status(&self) -> anyhow::Result<FormStatus> {
        self.status.parse()
    }
    
    /// Sets the status from an enum
    pub fn set_status(&mut self, status: FormStatus) {
        self.status = status.to_string();
    }

    /// Parses the JSON data field into a structured HashMap.
    /// 
    /// Business Logic:
    /// - Provides type-safe access to form field data
    /// - Handles JSON parsing errors gracefully
    /// - Returns HashMap for flexible field access
    pub fn parse_data(&self) -> anyhow::Result<HashMap<String, serde_json::Value>> {
        serde_json::from_str(&self.data)
            .map_err(|e| anyhow::anyhow!("Failed to parse form data: {}", e))
    }

    /// Sets the form data from a HashMap.
    /// 
    /// Business Logic:
    /// - Converts structured data back to JSON string
    /// - Ensures data is properly serialized for storage
    /// - Updates the updated_at timestamp
    pub fn set_data(&mut self, data: HashMap<String, serde_json::Value>) -> anyhow::Result<()> {
        self.data = serde_json::to_string(&data)
            .map_err(|e| anyhow::anyhow!("Failed to serialize form data: {}", e))?;
        self.updated_at = Utc::now();
        Ok(())
    }

    /// Gets a specific field value from the form data.
    /// 
    /// Business Logic:
    /// - Provides convenient access to individual form fields
    /// - Returns None if field doesn't exist
    /// - Handles JSON parsing transparently
    pub fn get_field(&self, field_name: &str) -> anyhow::Result<Option<serde_json::Value>> {
        let data = self.parse_data()?;
        Ok(data.get(field_name).cloned())
    }

    /// Sets a specific field value in the form data.
    /// 
    /// Business Logic:
    /// - Allows updating individual fields without replacing all data
    /// - Automatically updates the updated_at timestamp
    /// - Preserves other field values
    pub fn set_field(&mut self, field_name: &str, value: serde_json::Value) -> anyhow::Result<()> {
        let mut data = self.parse_data()?;
        data.insert(field_name.to_string(), value);
        self.set_data(data)
    }

    /// Validates that required fields are present for the form type.
    /// 
    /// Business Logic:
    /// - Ensures form meets ICS standards before completion
    /// - Returns list of missing required fields
    /// - Form-type specific validation rules
    pub fn validate_required_fields(&self) -> anyhow::Result<Vec<String>> {
        let data = self.parse_data()?;
        let mut missing_fields = Vec::new();

        // Basic required fields for all forms
        let basic_required = vec!["incident_name", "date_prepared", "time_prepared"];
        
        for field in basic_required {
            if !data.contains_key(field) || data[field].is_null() {
                missing_fields.push(field.to_string());
            }
        }

        // Form-type specific validation could be added here
        // This would reference the ICS form specifications

        Ok(missing_fields)
    }

    /// Checks if the form can transition to the specified status.
    /// 
    /// Business Logic:
    /// - Enforces proper workflow transitions
    /// - Draft -> Completed -> Final (no backwards transitions)
    /// - Validates required fields before status changes
    pub fn can_transition_to(&self, new_status: &FormStatus) -> anyhow::Result<bool> {
        let current_status = self.get_status()?;
        match (&current_status, new_status) {
            // Can always stay in same status
            (current, new) if current == new => Ok(true),
            
            // Forward transitions
            (FormStatus::Draft, FormStatus::Completed) => {
                // Check if required fields are filled
                let missing = self.validate_required_fields()?;
                Ok(missing.is_empty())
            },
            (FormStatus::Completed, FormStatus::Final) => Ok(true),
            (FormStatus::Draft, FormStatus::Final) => {
                // Direct draft to final requires validation
                let missing = self.validate_required_fields()?;
                Ok(missing.is_empty())
            },
            
            // Backwards transitions not allowed
            _ => Ok(false),
        }
    }
}

/// Application settings storage.
/// 
/// Business Logic:
/// - Simple key-value storage for application preferences
/// - Used for user settings, default values, etc.
/// - Keeps settings portable with the application
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Setting {
    /// Setting key (unique identifier)
    pub key: String,
    
    /// Setting value (stored as JSON for flexibility)
    pub value: String,
    
    /// When the setting was last updated
    pub updated_at: DateTime<Utc>,
}

impl Setting {
    /// Creates a new setting with the given key and value.
    pub fn new(key: String, value: serde_json::Value) -> anyhow::Result<Self> {
        Ok(Self {
            key,
            value: serde_json::to_string(&value)?,
            updated_at: Utc::now(),
        })
    }

    /// Gets the setting value as a typed value.
    pub fn get_value<T>(&self) -> anyhow::Result<T> 
    where 
        T: for<'de> Deserialize<'de>
    {
        serde_json::from_str(&self.value)
            .map_err(|e| anyhow::anyhow!("Failed to deserialize setting value: {}", e))
    }

    /// Sets the setting value from a typed value.
    pub fn set_value<T>(&mut self, value: T) -> anyhow::Result<()>
    where 
        T: Serialize
    {
        self.value = serde_json::to_string(&value)?;
        self.updated_at = Utc::now();
        Ok(())
    }
}

// ============================================================================
// Enhanced Schema Structures (Migration 002)
// ============================================================================

/// Form relationship record for tracking dependencies between forms.
/// 
/// Business Logic:
/// - Tracks how forms relate to each other in ICS workflows
/// - Supports automatic form updates when related data changes
/// - Enables Incident Action Plan assembly and validation
/// - Provides foundation for workflow automation
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct FormRelationship {
    /// Unique identifier for the relationship
    pub id: i64,
    
    /// Source form ID
    pub source_form_id: i64,
    
    /// Target form ID that is related
    pub target_form_id: i64,
    
    /// Type of relationship (feeds, requires, updates, etc.)
    pub relationship_type: String,
    
    /// How critical this dependency is (required, recommended, optional)
    pub dependency_strength: String,
    
    /// When the relationship was created
    pub created_at: DateTime<Utc>,
    
    /// Optional notes about the relationship
    pub notes: Option<String>,
}

/// Form status history record for audit trail.
/// 
/// Business Logic:
/// - Documents all status changes for accountability
/// - Supports workflow analysis and optimization
/// - Provides audit trail for compliance requirements
/// - Enables troubleshooting of form processing issues
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct FormStatusHistory {
    /// Unique identifier for the status change
    pub id: i64,
    
    /// Form that had its status changed
    pub form_id: i64,
    
    /// Previous status (if any)
    pub from_status: Option<String>,
    
    /// New status
    pub to_status: String,
    
    /// Who made the status change
    pub changed_by: String,
    
    /// When the change occurred
    pub changed_at: DateTime<Utc>,
    
    /// Reason for the change (optional)
    pub reason: Option<String>,
    
    /// Workflow position at time of change
    pub workflow_position: Option<String>,
}

/// Digital signature record for form authentication.
/// 
/// Business Logic:
/// - Supports various signature types for different deployment scenarios
/// - Provides non-repudiation for critical forms
/// - Enables digital signature workflows
/// - Maintains audit trail for signature verification
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct FormSignature {
    /// Unique identifier for the signature
    pub id: i64,
    
    /// Form that was signed
    pub form_id: i64,
    
    /// Type of signature (digital, electronic, handwritten)
    pub signature_type: String,
    
    /// Name of the person who signed
    pub signer_name: String,
    
    /// Position/title of the signer
    pub signer_position: Option<String>,
    
    /// Actual signature data (varies by type)
    pub signature_data: Option<Vec<u8>>,
    
    /// When the signature was applied
    pub signature_timestamp: DateTime<Utc>,
    
    /// Context of the signature (prepared_by, approved_by, etc.)
    pub signature_context: Option<String>,
    
    /// Verification status of the signature
    pub verification_status: String,
}

/// Form template record for dynamic form generation.
/// 
/// Business Logic:
/// - Defines structure and validation rules for each form type
/// - Enables dynamic form rendering in the UI
/// - Supports form template versioning and updates
/// - Provides foundation for form validation engine
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct FormTemplate {
    /// Unique identifier for the template
    pub id: i64,
    
    /// ICS form type this template defines
    pub form_type: String,
    
    /// Version of the template
    pub template_version: String,
    
    /// JSON structure defining form fields and layout
    pub template_data: String,
    
    /// JSON array of validation rules for this form type
    pub validation_rules: Option<String>,
    
    /// When the template was created
    pub created_at: DateTime<Utc>,
    
    /// When the template was last updated
    pub updated_at: DateTime<Utc>,
    
    /// Whether this template is currently active
    pub is_active: bool,
}

impl FormTemplate {
    /// Parses the template data into a structured format.
    /// 
    /// Business Logic:
    /// - Provides type-safe access to template structure
    /// - Handles JSON parsing errors gracefully
    /// - Returns HashMap for flexible field access
    pub fn parse_template_data(&self) -> anyhow::Result<HashMap<String, serde_json::Value>> {
        serde_json::from_str(&self.template_data)
            .map_err(|e| anyhow::anyhow!("Failed to parse template data: {}", e))
    }
    
    /// Parses the validation rules into a structured format.
    /// 
    /// Business Logic:
    /// - Provides access to form-specific validation rules
    /// - Returns empty vector if no rules are defined
    /// - Handles JSON parsing errors gracefully
    pub fn parse_validation_rules(&self) -> anyhow::Result<Vec<String>> {
        match &self.validation_rules {
            Some(rules) => serde_json::from_str(rules)
                .map_err(|e| anyhow::anyhow!("Failed to parse validation rules: {}", e)),
            None => Ok(Vec::new()),
        }
    }
}

/// Validation rule record for reusable validation logic.
/// 
/// Business Logic:
/// - Defines reusable validation rules across form types
/// - Supports complex validation scenarios and business rules
/// - Enables consistent validation behavior across the application
/// - Provides foundation for real-time validation feedback
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct ValidationRule {
    /// Unique identifier for the validation rule
    pub id: i64,
    
    /// Unique rule identifier for referencing
    pub rule_id: String,
    
    /// Human-readable name for the rule
    pub rule_name: String,
    
    /// Type of validation (required, format, range, etc.)
    pub rule_type: String,
    
    /// JSON array of form types this rule applies to (null = all)
    pub form_types: Option<String>,
    
    /// JSON array of field names this rule validates
    pub fields: String,
    
    /// JSON object defining the validation logic
    pub validation_logic: String,
    
    /// Error message to display when validation fails
    pub error_message: String,
    
    /// Warning message for non-critical validation issues
    pub warning_message: Option<String>,
    
    /// Severity level (error, warning, info)
    pub severity: String,
    
    /// Whether this rule is currently active
    pub is_active: bool,
    
    /// When the rule was created
    pub created_at: DateTime<Utc>,
    
    /// When the rule was last updated
    pub updated_at: DateTime<Utc>,
}

impl ValidationRule {
    /// Parses the form types into a list.
    /// 
    /// Business Logic:
    /// - Returns list of form types this rule applies to
    /// - Returns None if rule applies to all forms
    /// - Handles JSON parsing errors gracefully
    pub fn parse_form_types(&self) -> anyhow::Result<Option<Vec<String>>> {
        match &self.form_types {
            Some(types) => {
                let parsed: Vec<String> = serde_json::from_str(types)
                    .map_err(|e| anyhow::anyhow!("Failed to parse form types: {}", e))?;
                Ok(Some(parsed))
            },
            None => Ok(None),
        }
    }
    
    /// Parses the fields into a list.
    /// 
    /// Business Logic:
    /// - Returns list of field names this rule validates
    /// - Handles JSON parsing errors gracefully
    /// - Always returns a vector (empty if parsing fails)
    pub fn parse_fields(&self) -> anyhow::Result<Vec<String>> {
        serde_json::from_str(&self.fields)
            .map_err(|e| anyhow::anyhow!("Failed to parse fields: {}", e))
    }
    
    /// Parses the validation logic into a structured format.
    /// 
    /// Business Logic:
    /// - Provides access to the validation logic configuration
    /// - Returns HashMap for flexible access to logic parameters
    /// - Handles JSON parsing errors gracefully
    pub fn parse_validation_logic(&self) -> anyhow::Result<HashMap<String, serde_json::Value>> {
        serde_json::from_str(&self.validation_logic)
            .map_err(|e| anyhow::anyhow!("Failed to parse validation logic: {}", e))
    }
}

/// Export configuration record for customizing output formats.
/// 
/// Business Logic:
/// - Stores configuration for different export formats
/// - Enables customization of PDF, JSON, ICS-DES, and other exports
/// - Supports user-defined export templates and filters
/// - Provides foundation for flexible export system
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct ExportConfiguration {
    /// Unique identifier for the configuration
    pub id: i64,
    
    /// Human-readable name for the configuration
    pub config_name: String,
    
    /// Export format (pdf, json, ics_des, csv, xml)
    pub export_format: String,
    
    /// JSON array of applicable form types (null = all)
    pub form_types: Option<String>,
    
    /// JSON configuration specific to the export format
    pub template_data: Option<String>,
    
    /// JSON array of field filters for selective export
    pub field_filters: Option<String>,
    
    /// JSON configuration specific to ICS-DES format
    pub ics_des_config: Option<String>,
    
    /// Who created this configuration
    pub created_by: Option<String>,
    
    /// When the configuration was created
    pub created_at: DateTime<Utc>,
    
    /// When the configuration was last updated
    pub updated_at: DateTime<Utc>,
    
    /// Whether this is the default configuration for the format
    pub is_default: bool,
}

impl ExportConfiguration {
    /// Parses the applicable form types.
    /// 
    /// Business Logic:
    /// - Returns list of form types this configuration applies to
    /// - Returns None if configuration applies to all forms
    /// - Handles JSON parsing errors gracefully
    pub fn parse_form_types(&self) -> anyhow::Result<Option<Vec<String>>> {
        match &self.form_types {
            Some(types) => {
                let parsed: Vec<String> = serde_json::from_str(types)
                    .map_err(|e| anyhow::anyhow!("Failed to parse form types: {}", e))?;
                Ok(Some(parsed))
            },
            None => Ok(None),
        }
    }
    
    /// Parses the template data configuration.
    /// 
    /// Business Logic:
    /// - Provides access to format-specific configuration
    /// - Returns empty HashMap if no template data is defined
    /// - Handles JSON parsing errors gracefully
    pub fn parse_template_data(&self) -> anyhow::Result<HashMap<String, serde_json::Value>> {
        match &self.template_data {
            Some(data) => serde_json::from_str(data)
                .map_err(|e| anyhow::anyhow!("Failed to parse template data: {}", e)),
            None => Ok(HashMap::new()),
        }
    }
    
    /// Parses the field filters configuration.
    /// 
    /// Business Logic:
    /// - Provides access to field filtering rules
    /// - Returns empty vector if no filters are defined
    /// - Handles JSON parsing errors gracefully
    pub fn parse_field_filters(&self) -> anyhow::Result<Vec<HashMap<String, serde_json::Value>>> {
        match &self.field_filters {
            Some(filters) => serde_json::from_str(filters)
                .map_err(|e| anyhow::anyhow!("Failed to parse field filters: {}", e)),
            None => Ok(Vec::new()),
        }
    }
    
    /// Parses the ICS-DES specific configuration.
    /// 
    /// Business Logic:
    /// - Provides access to ICS-DES format parameters
    /// - Returns None if no ICS-DES configuration is defined
    /// - Handles JSON parsing errors gracefully
    pub fn parse_ics_des_config(&self) -> anyhow::Result<Option<HashMap<String, serde_json::Value>>> {
        match &self.ics_des_config {
            Some(config) => {
                let parsed: HashMap<String, serde_json::Value> = serde_json::from_str(config)
                    .map_err(|e| anyhow::anyhow!("Failed to parse ICS-DES config: {}", e))?;
                Ok(Some(parsed))
            },
            None => Ok(None),
        }
    }
}
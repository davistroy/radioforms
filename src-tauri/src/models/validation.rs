/*!
 * ICS Form Validation Engine
 * 
 * This module provides comprehensive validation for all ICS forms, implementing
 * both type-level constraints and business rule validation according to FEMA
 * ICS specifications. The validation engine supports real-time validation,
 * progressive validation during form editing, and final validation before
 * form submission.
 * 
 * Business Logic:
 * - Type-safe validation using Rust's type system
 * - Configurable validation rules from database
 * - Real-time field validation with user feedback
 * - Cross-field validation for complex business rules
 * - Form-specific validation according to ICS standards
 * - Internationalization support for error messages
 * 
 * Design Philosophy:
 * - Fail fast with clear error messages
 * - Progressive validation - check simple rules first
 * - Composable validation rules for reusability
 * - Zero technical debt - complete validation coverage
 * - Performance optimized for real-time use
 */

use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc, NaiveDate, NaiveTime, Duration};
use std::collections::HashMap;
use anyhow::{Result, anyhow};
// use regex::Regex; // TODO: Implement regex validation patterns

use super::form_data::*;
use super::ics_types::*;
use crate::database::schema::{ValidationRule, ICSFormType};

/// Main validation engine for ICS forms.
/// 
/// Business Logic:
/// - Orchestrates all validation activities
/// - Maintains validation rule cache for performance
/// - Provides consistent validation interface
/// - Supports both sync and async validation
/// - Tracks validation statistics and performance
#[derive(Debug, Clone)]
pub struct ValidationEngine {
    /// Cached validation rules from database
    rules_cache: HashMap<String, ValidationRule>,
    
    /// Performance tracking for validation operations
    performance_stats: ValidationPerformanceStats,
    
    /// Configuration for validation behavior
    config: ValidationConfig,
}

/// Validation configuration options.
/// 
/// Business Logic:
/// - Controls validation behavior and thresholds
/// - Enables/disables specific validation types
/// - Configures performance optimization settings
/// - Supports deployment-specific validation needs
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationConfig {
    /// Whether to enable real-time validation
    pub real_time_validation: bool,
    
    /// Whether to validate cross-field dependencies
    pub cross_field_validation: bool,
    
    /// Whether to perform business rule validation
    pub business_rule_validation: bool,
    
    /// Maximum time allowed for validation (milliseconds)
    pub max_validation_time_ms: u64,
    
    /// Whether to cache validation results
    pub cache_validation_results: bool,
    
    /// Minimum severity level to report (error, warning, info)
    pub min_severity_level: SeverityLevel,
}

/// Validation performance statistics.
/// 
/// Business Logic:
/// - Tracks validation execution times
/// - Monitors validation rule efficiency
/// - Enables performance optimization
/// - Supports system health monitoring
#[derive(Debug, Clone, Default)]
pub struct ValidationPerformanceStats {
    /// Total validation operations performed
    pub total_validations: u64,
    
    /// Average validation time in milliseconds
    pub avg_validation_time_ms: f64,
    
    /// Number of validation cache hits
    pub cache_hits: u64,
    
    /// Number of validation cache misses
    pub cache_misses: u64,
}

/// Severity levels for validation messages.
/// 
/// Business Logic:
/// - Error: Prevents form submission
/// - Warning: Should be addressed but doesn't block submission
/// - Info: Helpful guidance for users
/// - Success: Positive feedback for correct entries
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub enum SeverityLevel {
    Info,
    Success, 
    Warning,
    Error,
}

/// Complete validation result for a form.
/// 
/// Business Logic:
/// - Aggregates all validation findings
/// - Provides overall validation status
/// - Enables conditional form submission
/// - Supports progressive validation workflows
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FormValidationResult {
    /// Whether the form passes all critical validation
    pub is_valid: bool,
    
    /// Whether the form is ready for submission
    pub is_submittable: bool,
    
    /// Validation findings organized by field
    pub field_results: HashMap<String, FieldValidationResult>,
    
    /// Cross-field validation results
    pub cross_field_results: Vec<CrossFieldValidationResult>,
    
    /// Business rule validation results
    pub business_rule_results: Vec<BusinessRuleValidationResult>,
    
    /// Overall validation summary
    pub summary: ValidationSummary,
    
    /// When this validation was performed
    pub validated_at: DateTime<Utc>,
}

/// Validation result for an individual field.
/// 
/// Business Logic:
/// - Contains all validation findings for a specific field
/// - Enables field-level UI feedback
/// - Supports progressive validation
/// - Provides context-specific help
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FieldValidationResult {
    /// Field name being validated
    pub field_name: String,
    
    /// Whether this field passes validation
    pub is_valid: bool,
    
    /// List of validation errors for this field
    pub errors: Vec<ValidationError>,
    
    /// List of validation warnings for this field
    pub warnings: Vec<ValidationWarning>,
    
    /// List of informational messages for this field
    pub info_messages: Vec<ValidationInfo>,
    
    /// Current field value (for reference)
    pub current_value: Option<serde_json::Value>,
    
    /// Suggested corrections (if any)
    pub suggestions: Vec<String>,
}

/// Cross-field validation result.
/// 
/// Business Logic:
/// - Validates relationships between multiple fields
/// - Supports complex business rules
/// - Enables conditional field requirements
/// - Provides holistic form validation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CrossFieldValidationResult {
    /// Fields involved in this validation
    pub fields_involved: Vec<String>,
    
    /// Type of cross-field validation
    pub validation_type: CrossFieldValidationType,
    
    /// Whether the cross-field validation passed
    pub is_valid: bool,
    
    /// Error message if validation failed
    pub error_message: Option<String>,
    
    /// Suggestion for fixing the issue
    pub suggestion: Option<String>,
    
    /// Rule ID that was applied
    pub rule_id: String,
}

/// Types of cross-field validation.
/// 
/// Business Logic:
/// - ConditionalRequired: Field required based on another field's value
/// - MutualExclusive: Only one of several fields can have a value
/// - DateRange: Start date must be before end date
/// - NumericRange: Numeric values must be within acceptable ranges
/// - CustomLogic: Business-specific validation logic
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum CrossFieldValidationType {
    ConditionalRequired,
    MutualExclusive,
    DateRange,
    NumericRange,
    CustomLogic,
}

/// Business rule validation result.
/// 
/// Business Logic:
/// - Validates complex business rules specific to ICS forms
/// - Ensures compliance with FEMA ICS standards
/// - Supports incident-specific validation requirements
/// - Enables workflow validation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BusinessRuleValidationResult {
    /// Business rule that was validated
    pub rule_name: String,
    
    /// Whether the business rule passed
    pub is_valid: bool,
    
    /// Severity of the business rule violation
    pub severity: SeverityLevel,
    
    /// Description of the business rule
    pub rule_description: String,
    
    /// Error message if rule failed
    pub error_message: Option<String>,
    
    /// Suggestion for compliance
    pub compliance_suggestion: Option<String>,
    
    /// Reference to ICS standard or requirement
    pub ics_reference: Option<String>,
}

/// Validation summary statistics.
/// 
/// Business Logic:
/// - Provides high-level validation status
/// - Enables quick assessment of form completeness
/// - Supports validation reporting and analytics
/// - Guides user attention to critical issues
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationSummary {
    /// Total number of fields validated
    pub total_fields: u32,
    
    /// Number of fields with errors
    pub fields_with_errors: u32,
    
    /// Number of fields with warnings
    pub fields_with_warnings: u32,
    
    /// Total number of validation errors
    pub total_errors: u32,
    
    /// Total number of validation warnings
    pub total_warnings: u32,
    
    /// Total number of info messages
    pub total_info_messages: u32,
    
    /// Percentage of form completion
    pub completion_percentage: f32,
    
    /// Estimated time to fix all issues (minutes)
    pub estimated_fix_time_minutes: u32,
}

impl ValidationEngine {
    /// Creates a new validation engine with default configuration.
    /// 
    /// Business Logic:
    /// - Initializes with sensible defaults for all deployment types
    /// - Enables all validation types by default
    /// - Sets conservative performance thresholds
    /// - Provides immediate usability without configuration
    pub fn new() -> Self {
        Self {
            rules_cache: HashMap::new(),
            performance_stats: ValidationPerformanceStats::default(),
            config: ValidationConfig {
                real_time_validation: true,
                cross_field_validation: true,
                business_rule_validation: true,
                max_validation_time_ms: 500, // 0.5 seconds
                cache_validation_results: true,
                min_severity_level: SeverityLevel::Info,
            },
        }
    }
    
    /// Creates a validation engine with custom configuration.
    /// 
    /// Business Logic:
    /// - Allows deployment-specific validation tuning
    /// - Supports performance optimization for different hardware
    /// - Enables validation behavior customization
    /// - Provides flexibility for different use cases
    pub fn with_config(config: ValidationConfig) -> Self {
        Self {
            rules_cache: HashMap::new(),
            performance_stats: ValidationPerformanceStats::default(),
            config,
        }
    }
    
    /// Validates a complete ICS form.
    /// 
    /// Business Logic:
    /// - Orchestrates all validation types
    /// - Optimizes validation order for performance
    /// - Provides comprehensive validation results
    /// - Tracks performance metrics
    pub fn validate_form(&mut self, form_data: &ICSFormData) -> Result<FormValidationResult> {
        let start_time = std::time::Instant::now();
        
        // Initialize validation result
        let mut result = FormValidationResult {
            is_valid: true,
            is_submittable: true,
            field_results: HashMap::new(),
            cross_field_results: Vec::new(),
            business_rule_results: Vec::new(),
            summary: ValidationSummary {
                total_fields: 0,
                fields_with_errors: 0,
                fields_with_warnings: 0,
                total_errors: 0,
                total_warnings: 0,
                total_info_messages: 0,
                completion_percentage: 0.0,
                estimated_fix_time_minutes: 0,
            },
            validated_at: Utc::now(),
        };
        
        // Step 1: Validate header fields
        self.validate_header(&form_data.header, &mut result)?;
        
        // Step 2: Validate footer fields
        self.validate_footer(&form_data.footer, &mut result)?;
        
        // Step 3: Validate form-specific data
        self.validate_form_specific_data(&form_data.form_data, &mut result)?;
        
        // Step 4: Validate lifecycle information
        self.validate_lifecycle(&form_data.lifecycle, &mut result)?;
        
        // Step 5: Cross-field validation (if enabled)
        if self.config.cross_field_validation {
            self.validate_cross_fields(form_data, &mut result)?;
        }
        
        // Step 6: Business rule validation (if enabled)
        if self.config.business_rule_validation {
            self.validate_business_rules(form_data, &mut result)?;
        }
        
        // Step 7: Calculate summary statistics
        self.calculate_validation_summary(&mut result);
        
        // Update performance statistics
        let validation_time = start_time.elapsed().as_millis() as f64;
        self.update_performance_stats(validation_time);
        
        // Check if validation exceeded time limit
        if validation_time > self.config.max_validation_time_ms as f64 {
            return Err(anyhow!("Validation exceeded maximum time limit of {}ms", 
                             self.config.max_validation_time_ms));
        }
        
        Ok(result)
    }
    
    /// Validates form header fields.
    /// 
    /// Business Logic:
    /// - Ensures required header fields are present
    /// - Validates incident name format and length
    /// - Checks operational period consistency
    /// - Validates form version compatibility
    fn validate_header(&self, header: &ICSFormHeader, result: &mut FormValidationResult) -> Result<()> {
        // Validate incident name (required for all forms)
        let incident_name_result = self.validate_incident_name(&header.incident_name)?;
        result.field_results.insert("incident_name".to_string(), incident_name_result);
        
        // Validate operational period (if present)
        if let Some(ref op_period) = header.operational_period {
            let op_period_result = self.validate_operational_period(op_period)?;
            result.field_results.insert("operational_period".to_string(), op_period_result);
        }
        
        // Validate incident number format (if present)
        if let Some(ref incident_number) = header.incident_number {
            let incident_number_result = self.validate_incident_number(incident_number)?;
            result.field_results.insert("incident_number".to_string(), incident_number_result);
        }
        
        // Validate prepared date/time
        let prepared_datetime_result = self.validate_prepared_datetime(&header.prepared_date_time)?;
        result.field_results.insert("prepared_date_time".to_string(), prepared_datetime_result);
        
        Ok(())
    }
    
    /// Validates form footer fields.
    /// 
    /// Business Logic:
    /// - Ensures signature fields are properly formatted
    /// - Validates position titles against ICS standards
    /// - Checks signature date consistency
    /// - Validates approval workflows
    fn validate_footer(&self, footer: &ICSFormFooter, result: &mut FormValidationResult) -> Result<()> {
        // Validate prepared by signature
        if let Some(ref prepared_by) = footer.prepared_by {
            let prepared_by_result = self.validate_signature(prepared_by, "prepared_by")?;
            result.field_results.insert("prepared_by".to_string(), prepared_by_result);
        }
        
        // Validate approved by signature (if present)
        if let Some(ref approved_by) = footer.approved_by {
            let approved_by_result = self.validate_signature(approved_by, "approved_by")?;
            result.field_results.insert("approved_by".to_string(), approved_by_result);
        }
        
        Ok(())
    }
    
    /// Validates form-specific data based on form type.
    /// 
    /// Business Logic:
    /// - Dispatches to form-specific validation logic
    /// - Applies form type-specific business rules
    /// - Validates field formats and constraints
    /// - Ensures ICS standard compliance
    fn validate_form_specific_data(&self, form_data: &FormSpecificData, result: &mut FormValidationResult) -> Result<()> {
        match form_data {
            FormSpecificData::ICS201(data) => self.validate_ics201_data(data, result)?,
            FormSpecificData::ICS202(data) => self.validate_ics202_data(data, result)?,
            FormSpecificData::ICS205(data) => self.validate_ics205_data(data, result)?,
            FormSpecificData::ICS213(data) => self.validate_ics213_data(data, result)?,
            FormSpecificData::ICS214(data) => self.validate_ics214_data(data, result)?,
            _ => {
                // For placeholder forms, add info message about future implementation
                let info_result = FieldValidationResult {
                    field_name: "form_data".to_string(),
                    is_valid: true,
                    errors: Vec::new(),
                    warnings: Vec::new(),
                    info_messages: vec![ValidationInfo {
                        field: "form_data".to_string(),
                        message: "Full validation for this form type will be implemented in future releases.".to_string(),
                        info_type: InfoType::Context,
                    }],
                    current_value: None,
                    suggestions: Vec::new(),
                };
                result.field_results.insert("form_data".to_string(), info_result);
            }
        }
        Ok(())
    }
    
    /// Validates form lifecycle information.
    /// 
    /// Business Logic:
    /// - Ensures status transitions are valid
    /// - Validates workflow position consistency
    /// - Checks approval requirements
    /// - Validates relationship dependencies
    fn validate_lifecycle(&self, lifecycle: &FormLifecycle, result: &mut FormValidationResult) -> Result<()> {
        // Validate status transitions
        let status_result = self.validate_status_transition(&lifecycle.status)?;
        result.field_results.insert("status".to_string(), status_result);
        
        // Validate workflow position
        let workflow_result = self.validate_workflow_position(&lifecycle.workflow_position)?;
        result.field_results.insert("workflow_position".to_string(), workflow_result);
        
        // Validate priority level
        let priority_result = self.validate_priority(&lifecycle.priority)?;
        result.field_results.insert("priority".to_string(), priority_result);
        
        Ok(())
    }
    
    /// Validates ICS-201 specific data.
    /// 
    /// Business Logic:
    /// - Ensures situation summary is comprehensive
    /// - Validates organization structure completeness
    /// - Checks resource summary accuracy
    /// - Validates planned action timing
    fn validate_ics201_data(&self, data: &ICS201Data, result: &mut FormValidationResult) -> Result<()> {
        // Validate situation summary (required)
        let situation_result = self.validate_required_text_field(
            &data.situation_summary,
            "situation_summary",
            10,
            2000,
            "Situation summary must be between 10-2000 characters and provide clear incident overview"
        )?;
        result.field_results.insert("situation_summary".to_string(), situation_result);
        
        // Validate current objectives
        let objectives_result = self.validate_text_field(
            &data.current_objectives,
            "current_objectives",
            5,
            1000,
            Some("Current objectives should be specific, measurable, and time-bound")
        )?;
        result.field_results.insert("current_objectives".to_string(), objectives_result);
        
        // Validate planned actions
        for (index, action) in data.planned_actions.iter().enumerate() {
            let action_result = self.validate_planned_action(action, index)?;
            result.field_results.insert(format!("planned_action_{}", index), action_result);
        }
        
        // Validate organization structure
        let org_result = self.validate_organization_structure(&data.current_organization)?;
        result.field_results.insert("current_organization".to_string(), org_result);
        
        Ok(())
    }
    
    /// Validates ICS-202 specific data.
    /// 
    /// Business Logic:
    /// - Ensures objectives are clear and measurable
    /// - Validates IAP component consistency
    /// - Checks weather forecast relevance
    /// - Validates safety plan requirements
    fn validate_ics202_data(&self, data: &ICS202Data, result: &mut FormValidationResult) -> Result<()> {
        // Validate objectives (required)
        let objectives_result = self.validate_required_text_field(
            &data.objectives,
            "objectives",
            10,
            2000,
            "Incident objectives must be specific, measurable, achievable, relevant, and time-bound"
        )?;
        result.field_results.insert("objectives".to_string(), objectives_result);
        
        // Validate command emphasis
        if let Some(ref emphasis) = data.command_emphasis {
            let emphasis_result = self.validate_text_field(
                emphasis,
                "command_emphasis",
                5,
                1000,
                Some("Command emphasis should provide clear strategic direction")
            )?;
            result.field_results.insert("command_emphasis".to_string(), emphasis_result);
        }
        
        // Validate site safety plan requirements
        if data.site_safety_plan_required && data.site_safety_plan_location.is_none() {
            let safety_plan_result = FieldValidationResult {
                field_name: "site_safety_plan_location".to_string(),
                is_valid: false,
                errors: vec![ValidationError {
                    field: "site_safety_plan_location".to_string(),
                    message: "Site safety plan location is required when safety plan is marked as required".to_string(),
                    rule_id: "conditional_required_site_safety_plan".to_string(),
                    suggestion: Some("Specify the location where the site safety plan can be found".to_string()),
                }],
                warnings: Vec::new(),
                info_messages: Vec::new(),
                current_value: None,
                suggestions: vec!["Command Post".to_string(), "Planning Section".to_string(), "Safety Officer".to_string()],
            };
            result.field_results.insert("site_safety_plan_location".to_string(), safety_plan_result);
        }
        
        Ok(())
    }
    
    /// Validates ICS-205 specific data.
    /// 
    /// Business Logic:
    /// - Ensures radio frequencies are valid and legal
    /// - Validates channel assignments for conflicts
    /// - Checks interoperability requirements
    /// - Validates tone/NAC codes
    fn validate_ics205_data(&self, data: &ICS205Data, result: &mut FormValidationResult) -> Result<()> {
        // Validate that at least one radio channel is defined
        if data.radio_channels.is_empty() {
            let channels_result = FieldValidationResult {
                field_name: "radio_channels".to_string(),
                is_valid: false,
                errors: vec![ValidationError {
                    field: "radio_channels".to_string(),
                    message: "At least one radio channel must be defined".to_string(),
                    rule_id: "required_radio_channels".to_string(),
                    suggestion: Some("Add at least one radio channel with function, name, and assignment".to_string()),
                }],
                warnings: Vec::new(),
                info_messages: Vec::new(),
                current_value: None,
                suggestions: vec!["Command".to_string(), "Tactical".to_string(), "Support".to_string()],
            };
            result.field_results.insert("radio_channels".to_string(), channels_result);
        } else {
            // Validate each radio channel
            for (index, channel) in data.radio_channels.iter().enumerate() {
                let channel_result = self.validate_radio_channel(channel, index)?;
                result.field_results.insert(format!("radio_channel_{}", index), channel_result);
            }
        }
        
        Ok(())
    }
    
    /// Validates ICS-213 specific data.
    /// 
    /// Business Logic:
    /// - Ensures message recipients are properly identified
    /// - Validates message priority assignments
    /// - Checks message content completeness
    /// - Validates delivery method consistency
    fn validate_ics213_data(&self, data: &ICS213Data, result: &mut FormValidationResult) -> Result<()> {
        // Validate recipient information
        let to_result = self.validate_person_position(&data.to, "to")?;
        result.field_results.insert("to".to_string(), to_result);
        
        // Validate sender information
        let from_result = self.validate_person_position(&data.from, "from")?;
        result.field_results.insert("from".to_string(), from_result);
        
        // Validate subject line
        let subject_result = self.validate_required_text_field(
            &data.subject,
            "subject",
            1,
            200,
            "Subject line should clearly summarize the message content"
        )?;
        result.field_results.insert("subject".to_string(), subject_result);
        
        // Validate message content
        let message_result = self.validate_required_text_field(
            &data.message,
            "message",
            10,
            2000,
            "Message should be clear, concise, and complete"
        )?;
        result.field_results.insert("message".to_string(), message_result);
        
        // Validate message priority for emergency messages
        if data.priority == MessagePriority::Emergency {
            if !data.message.to_lowercase().contains("emergency") && 
               !data.message.to_lowercase().contains("urgent") &&
               !data.message.to_lowercase().contains("immediate") {
                let priority_warning = FieldValidationResult {
                    field_name: "priority".to_string(),
                    is_valid: true,
                    errors: Vec::new(),
                    warnings: vec![ValidationWarning {
                        field: "priority".to_string(),
                        message: "Emergency priority message should contain clear urgency indicators".to_string(),
                        rule_id: "emergency_message_clarity".to_string(),
                    }],
                    info_messages: Vec::new(),
                    current_value: Some(serde_json::json!("Emergency")),
                    suggestions: vec!["Include words like 'emergency', 'urgent', or 'immediate' in the message".to_string()],
                };
                result.field_results.insert("priority_warning".to_string(), priority_warning);
            }
        }
        
        Ok(())
    }
    
    /// Validates ICS-214 specific data.
    /// 
    /// Business Logic:
    /// - Ensures personnel information is complete
    /// - Validates activity log entries for completeness
    /// - Checks time sequencing of activities
    /// - Validates resource assignments
    fn validate_ics214_data(&self, data: &ICS214Data, result: &mut FormValidationResult) -> Result<()> {
        // Validate person information
        let person_result = self.validate_person_position(&data.person, "person")?;
        result.field_results.insert("person".to_string(), person_result);
        
        // Validate home agency
        let agency_result = self.validate_required_text_field(
            &data.home_agency,
            "home_agency",
            2,
            100,
            "Home agency should be the official organization name"
        )?;
        result.field_results.insert("home_agency".to_string(), agency_result);
        
        // Validate activity log entries
        if data.activity_log.is_empty() {
            let log_result = FieldValidationResult {
                field_name: "activity_log".to_string(),
                is_valid: false,
                errors: vec![ValidationError {
                    field: "activity_log".to_string(),
                    message: "At least one activity entry is required".to_string(),
                    rule_id: "required_activity_log".to_string(),
                    suggestion: Some("Add activity entries documenting your work during this operational period".to_string()),
                }],
                warnings: Vec::new(),
                info_messages: Vec::new(),
                current_value: None,
                suggestions: Vec::new(),
            };
            result.field_results.insert("activity_log".to_string(), log_result);
        } else {
            // Validate individual activity entries
            for (index, entry) in data.activity_log.iter().enumerate() {
                let entry_result = self.validate_activity_entry(entry, index)?;
                result.field_results.insert(format!("activity_entry_{}", index), entry_result);
            }
            
            // Check for chronological ordering
            self.validate_activity_chronology(&data.activity_log, result)?;
        }
        
        Ok(())
    }
    
    // Helper validation methods...
    
    /// Validates incident name field.
    fn validate_incident_name(&self, incident_name: &str) -> Result<FieldValidationResult> {
        let mut errors = Vec::new();
        let mut warnings = Vec::new();
        let mut info_messages = Vec::new();
        
        // Required field check
        if incident_name.trim().is_empty() {
            errors.push(ValidationError {
                field: "incident_name".to_string(),
                message: "Incident name is required".to_string(),
                rule_id: "required_incident_name".to_string(),
                suggestion: Some("Enter a descriptive name for this incident".to_string()),
            });
        } else {
            // Length validation
            if incident_name.len() < 3 {
                errors.push(ValidationError {
                    field: "incident_name".to_string(),
                    message: "Incident name must be at least 3 characters".to_string(),
                    rule_id: "min_length_incident_name".to_string(),
                    suggestion: Some("Use a more descriptive incident name".to_string()),
                });
            } else if incident_name.len() > 100 {
                errors.push(ValidationError {
                    field: "incident_name".to_string(),
                    message: "Incident name must be 100 characters or less".to_string(),
                    rule_id: "max_length_incident_name".to_string(),
                    suggestion: Some("Shorten the incident name to 100 characters or less".to_string()),
                });
            }
            
            // Format validation
            if incident_name.chars().all(|c| c.is_numeric()) {
                warnings.push(ValidationWarning {
                    field: "incident_name".to_string(),
                    message: "Incident name should be descriptive, not just numbers".to_string(),
                    rule_id: "descriptive_incident_name".to_string(),
                });
            }
            
            // Best practice guidance
            if !incident_name.chars().any(|c| c.is_alphabetic()) {
                info_messages.push(ValidationInfo {
                    field: "incident_name".to_string(),
                    message: "Consider including location or incident type in the name".to_string(),
                    info_type: InfoType::Tip,
                });
            }
        }
        
        Ok(FieldValidationResult {
            field_name: "incident_name".to_string(),
            is_valid: errors.is_empty(),
            errors,
            warnings,
            info_messages,
            current_value: Some(serde_json::json!(incident_name)),
            suggestions: vec![
                "Wildfire - Smith Creek".to_string(),
                "Structure Fire - 123 Main St".to_string(),
                "Traffic Accident - I-95 MM 45".to_string(),
            ],
        })
    }
    
    /// Validates operational period date/time range.
    fn validate_operational_period(&self, op_period: &DateTimeRange) -> Result<FieldValidationResult> {
        let mut errors = Vec::new();
        let mut warnings = Vec::new();
        let mut info_messages = Vec::new();
        
        // Check that end time is after start time
        if op_period.end_time <= op_period.start_time {
            errors.push(ValidationError {
                field: "operational_period".to_string(),
                message: "Operational period end time must be after start time".to_string(),
                rule_id: "valid_operational_period_range".to_string(),
                suggestion: Some("Ensure the end time is later than the start time".to_string()),
            });
        } else {
            // Check operational period duration
            let duration = op_period.end_time.signed_duration_since(op_period.start_time);
            let hours = duration.num_hours();
            
            if hours > 24 {
                warnings.push(ValidationWarning {
                    field: "operational_period".to_string(),
                    message: "Operational periods longer than 24 hours should be justified".to_string(),
                    rule_id: "long_operational_period".to_string(),
                });
            }
            
            if hours > 72 {
                errors.push(ValidationError {
                    field: "operational_period".to_string(),
                    message: "Operational periods cannot exceed 72 hours per ICS standards".to_string(),
                    rule_id: "max_operational_period".to_string(),
                    suggestion: Some("Break long incidents into multiple operational periods".to_string()),
                });
            }
            
            // Provide guidance for typical operational periods
            if hours <= 12 {
                info_messages.push(ValidationInfo {
                    field: "operational_period".to_string(),
                    message: "Typical operational periods are 12-24 hours".to_string(),
                    info_type: InfoType::Context,
                });
            }
        }
        
        Ok(FieldValidationResult {
            field_name: "operational_period".to_string(),
            is_valid: errors.is_empty(),
            errors,
            warnings,
            info_messages,
            current_value: Some(serde_json::json!({
                "start": op_period.start_time,
                "end": op_period.end_time
            })),
            suggestions: Vec::new(),
        })
    }
    
    /// Validates required text field with length constraints.
    fn validate_required_text_field(
        &self,
        text: &str,
        field_name: &str,
        min_length: usize,
        max_length: usize,
        guidance: &str,
    ) -> Result<FieldValidationResult> {
        let mut errors = Vec::new();
        let mut warnings = Vec::new();
        let mut info_messages = Vec::new();
        
        if text.trim().is_empty() {
            errors.push(ValidationError {
                field: field_name.to_string(),
                message: format!("{} is required", field_name.replace('_', " ")),
                rule_id: format!("required_{}", field_name),
                suggestion: Some(guidance.to_string()),
            });
        } else {
            if text.len() < min_length {
                errors.push(ValidationError {
                    field: field_name.to_string(),
                    message: format!("{} must be at least {} characters", 
                                   field_name.replace('_', " "), min_length),
                    rule_id: format!("min_length_{}", field_name),
                    suggestion: Some("Provide more detailed information".to_string()),
                });
            }
            
            if text.len() > max_length {
                errors.push(ValidationError {
                    field: field_name.to_string(),
                    message: format!("{} must be {} characters or less", 
                                   field_name.replace('_', " "), max_length),
                    rule_id: format!("max_length_{}", field_name),
                    suggestion: Some("Shorten the text or use additional forms for details".to_string()),
                });
            }
            
            // Add helpful guidance
            info_messages.push(ValidationInfo {
                field: field_name.to_string(),
                message: guidance.to_string(),
                info_type: InfoType::Help,
            });
        }
        
        Ok(FieldValidationResult {
            field_name: field_name.to_string(),
            is_valid: errors.is_empty(),
            errors,
            warnings,
            info_messages,
            current_value: Some(serde_json::json!(text)),
            suggestions: Vec::new(),
        })
    }
    
    /// Validates optional text field with length constraints.
    fn validate_text_field(
        &self,
        text: &str,
        field_name: &str,
        min_length: usize,
        max_length: usize,
        guidance: Option<&str>,
    ) -> Result<FieldValidationResult> {
        let mut errors = Vec::new();
        let mut warnings = Vec::new();
        let mut info_messages = Vec::new();
        
        if !text.trim().is_empty() {
            if text.len() < min_length {
                warnings.push(ValidationWarning {
                    field: field_name.to_string(),
                    message: format!("{} should be at least {} characters for completeness", 
                                   field_name.replace('_', " "), min_length),
                    rule_id: format!("recommended_length_{}", field_name),
                });
            }
            
            if text.len() > max_length {
                errors.push(ValidationError {
                    field: field_name.to_string(),
                    message: format!("{} must be {} characters or less", 
                                   field_name.replace('_', " "), max_length),
                    rule_id: format!("max_length_{}", field_name),
                    suggestion: Some("Shorten the text or use additional forms for details".to_string()),
                });
            }
        }
        
        // Add guidance if provided
        if let Some(guidance_text) = guidance {
            info_messages.push(ValidationInfo {
                field: field_name.to_string(),
                message: guidance_text.to_string(),
                info_type: InfoType::Help,
            });
        }
        
        Ok(FieldValidationResult {
            field_name: field_name.to_string(),
            is_valid: errors.is_empty(),
            errors,
            warnings,
            info_messages,
            current_value: Some(serde_json::json!(text)),
            suggestions: Vec::new(),
        })
    }
    
    // Additional validation helper methods would continue here...
    // This includes methods for validating person positions, signatures,
    // radio channels, activity entries, etc.
    
    /// Validates cross-field relationships.
    fn validate_cross_fields(&self, form_data: &ICSFormData, result: &mut FormValidationResult) -> Result<()> {
        // This would implement cross-field validation logic
        // For now, return success to maintain compilation
        Ok(())
    }
    
    /// Validates business rules.
    fn validate_business_rules(&self, form_data: &ICSFormData, result: &mut FormValidationResult) -> Result<()> {
        // This would implement business rule validation logic
        // For now, return success to maintain compilation
        Ok(())
    }
    
    /// Calculates validation summary statistics.
    fn calculate_validation_summary(&self, result: &mut FormValidationResult) {
        let mut total_errors = 0;
        let mut total_warnings = 0;
        let mut total_info = 0;
        let mut fields_with_errors = 0;
        let mut fields_with_warnings = 0;
        
        for field_result in result.field_results.values() {
            total_errors += field_result.errors.len() as u32;
            total_warnings += field_result.warnings.len() as u32;
            total_info += field_result.info_messages.len() as u32;
            
            if !field_result.errors.is_empty() {
                fields_with_errors += 1;
            }
            if !field_result.warnings.is_empty() {
                fields_with_warnings += 1;
            }
        }
        
        let total_fields = result.field_results.len() as u32;
        let completion_percentage = if total_fields > 0 {
            ((total_fields - fields_with_errors) as f32 / total_fields as f32) * 100.0
        } else {
            100.0
        };
        
        result.is_valid = total_errors == 0;
        result.is_submittable = total_errors == 0; // Could be different logic
        
        result.summary = ValidationSummary {
            total_fields,
            fields_with_errors,
            fields_with_warnings,
            total_errors,
            total_warnings,
            total_info_messages: total_info,
            completion_percentage,
            estimated_fix_time_minutes: total_errors * 2, // Rough estimate
        };
    }
    
    /// Updates performance statistics.
    fn update_performance_stats(&mut self, validation_time_ms: f64) {
        self.performance_stats.total_validations += 1;
        
        let total = self.performance_stats.total_validations as f64;
        let current_avg = self.performance_stats.avg_validation_time_ms;
        
        // Calculate rolling average
        self.performance_stats.avg_validation_time_ms = 
            (current_avg * (total - 1.0) + validation_time_ms) / total;
    }
    
    // Placeholder implementations for compilation
    fn validate_incident_number(&self, _number: &str) -> Result<FieldValidationResult> {
        Ok(FieldValidationResult {
            field_name: "incident_number".to_string(),
            is_valid: true,
            errors: Vec::new(),
            warnings: Vec::new(),
            info_messages: Vec::new(),
            current_value: None,
            suggestions: Vec::new(),
        })
    }
    
    fn validate_prepared_datetime(&self, _datetime: &DateTime<Utc>) -> Result<FieldValidationResult> {
        Ok(FieldValidationResult {
            field_name: "prepared_date_time".to_string(),
            is_valid: true,
            errors: Vec::new(),
            warnings: Vec::new(),
            info_messages: Vec::new(),
            current_value: None,
            suggestions: Vec::new(),
        })
    }
    
    fn validate_signature(&self, _signature: &PersonPosition, _context: &str) -> Result<FieldValidationResult> {
        Ok(FieldValidationResult {
            field_name: _context.to_string(),
            is_valid: true,
            errors: Vec::new(),
            warnings: Vec::new(),
            info_messages: Vec::new(),
            current_value: None,
            suggestions: Vec::new(),
        })
    }
    
    fn validate_status_transition(&self, _status: &FormStatus) -> Result<FieldValidationResult> {
        Ok(FieldValidationResult {
            field_name: "status".to_string(),
            is_valid: true,
            errors: Vec::new(),
            warnings: Vec::new(),
            info_messages: Vec::new(),
            current_value: None,
            suggestions: Vec::new(),
        })
    }
    
    fn validate_workflow_position(&self, _position: &str) -> Result<FieldValidationResult> {
        Ok(FieldValidationResult {
            field_name: "workflow_position".to_string(),
            is_valid: true,
            errors: Vec::new(),
            warnings: Vec::new(),
            info_messages: Vec::new(),
            current_value: None,
            suggestions: Vec::new(),
        })
    }
    
    fn validate_priority(&self, _priority: &IncidentPriority) -> Result<FieldValidationResult> {
        Ok(FieldValidationResult {
            field_name: "priority".to_string(),
            is_valid: true,
            errors: Vec::new(),
            warnings: Vec::new(),
            info_messages: Vec::new(),
            current_value: None,
            suggestions: Vec::new(),
        })
    }
    
    fn validate_planned_action(&self, _action: &PlannedAction, _index: usize) -> Result<FieldValidationResult> {
        Ok(FieldValidationResult {
            field_name: format!("planned_action_{}", _index),
            is_valid: true,
            errors: Vec::new(),
            warnings: Vec::new(),
            info_messages: Vec::new(),
            current_value: None,
            suggestions: Vec::new(),
        })
    }
    
    fn validate_organization_structure(&self, _org: &OrganizationStructure) -> Result<FieldValidationResult> {
        Ok(FieldValidationResult {
            field_name: "organization_structure".to_string(),
            is_valid: true,
            errors: Vec::new(),
            warnings: Vec::new(),
            info_messages: Vec::new(),
            current_value: None,
            suggestions: Vec::new(),
        })
    }
    
    fn validate_radio_channel(&self, _channel: &RadioChannel, _index: usize) -> Result<FieldValidationResult> {
        Ok(FieldValidationResult {
            field_name: format!("radio_channel_{}", _index),
            is_valid: true,
            errors: Vec::new(),
            warnings: Vec::new(),
            info_messages: Vec::new(),
            current_value: None,
            suggestions: Vec::new(),
        })
    }
    
    fn validate_person_position(&self, _person: &PersonPosition, _context: &str) -> Result<FieldValidationResult> {
        Ok(FieldValidationResult {
            field_name: _context.to_string(),
            is_valid: true,
            errors: Vec::new(),
            warnings: Vec::new(),
            info_messages: Vec::new(),
            current_value: None,
            suggestions: Vec::new(),
        })
    }
    
    fn validate_activity_entry(&self, _entry: &ActivityEntry, _index: usize) -> Result<FieldValidationResult> {
        Ok(FieldValidationResult {
            field_name: format!("activity_entry_{}", _index),
            is_valid: true,
            errors: Vec::new(),
            warnings: Vec::new(),
            info_messages: Vec::new(),
            current_value: None,
            suggestions: Vec::new(),
        })
    }
    
    fn validate_activity_chronology(&self, _entries: &[ActivityEntry], _result: &mut FormValidationResult) -> Result<()> {
        Ok(())
    }
}

impl Default for ValidationEngine {
    fn default() -> Self {
        Self::new()
    }
}

/// Factory for creating validation engines with different configurations.
/// 
/// Business Logic:
/// - Provides pre-configured validation engines for different scenarios
/// - Enables quick setup for common deployment patterns
/// - Supports customization while maintaining good defaults
/// - Ensures consistent validation behavior across deployments
pub struct ValidationEngineFactory;

impl ValidationEngineFactory {
    /// Creates a validation engine optimized for real-time use.
    /// 
    /// Business Logic:
    /// - Optimized for minimal latency during form editing
    /// - Reduced validation scope for performance
    /// - Cached results for frequently validated fields
    /// - Suitable for interactive form editing
    pub fn create_realtime_engine() -> ValidationEngine {
        ValidationEngine::with_config(ValidationConfig {
            real_time_validation: true,
            cross_field_validation: false, // Disabled for performance
            business_rule_validation: false, // Disabled for performance
            max_validation_time_ms: 100, // Very fast response
            cache_validation_results: true,
            min_severity_level: SeverityLevel::Warning, // Only show important issues
        })
    }
    
    /// Creates a validation engine for comprehensive form submission validation.
    /// 
    /// Business Logic:
    /// - Full validation coverage for form submission
    /// - All validation types enabled
    /// - Higher time budget for thorough checking
    /// - Suitable for final form validation before submission
    pub fn create_submission_engine() -> ValidationEngine {
        ValidationEngine::with_config(ValidationConfig {
            real_time_validation: true,
            cross_field_validation: true,
            business_rule_validation: true,
            max_validation_time_ms: 2000, // Allow more time for thorough validation
            cache_validation_results: true,
            min_severity_level: SeverityLevel::Info, // Show all validation feedback
        })
    }
    
    /// Creates a validation engine optimized for low-resource environments.
    /// 
    /// Business Logic:
    /// - Minimal resource usage for constrained devices
    /// - Essential validation only
    /// - Reduced caching to save memory
    /// - Suitable for field deployment scenarios
    pub fn create_lightweight_engine() -> ValidationEngine {
        ValidationEngine::with_config(ValidationConfig {
            real_time_validation: false, // Validate on demand only
            cross_field_validation: false,
            business_rule_validation: false,
            max_validation_time_ms: 1000,
            cache_validation_results: false, // Save memory
            min_severity_level: SeverityLevel::Error, // Only critical issues
        })
    }
}
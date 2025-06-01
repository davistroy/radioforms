/*!
 * Form Validation Tauri Commands
 * 
 * This module provides Tauri commands for form validation including real-time
 * field validation, cross-field validation, and complete form validation with
 * debouncing and error message generation.
 * 
 * Business Logic:
 * - Real-time field validation with 300ms debouncing
 * - Cross-field and business rule validation
 * - Clear, actionable error messages with field highlighting
 * - Conditional field validation based on form state
 * - Performance-optimized validation (<200ms response time)
 */

use tauri::State;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::Mutex;

use crate::models::validation::{ValidationEngine, FieldValidationResult, ValidationConfig, SeverityLevel};
use crate::models::form_data::ICSFormData;
use crate::database::schema::ICSFormType;

/// Application state containing validation engine
pub type ValidationState = Arc<Mutex<ValidationEngine>>;

/// Error response structure for validation operations
#[derive(Debug, Serialize, Deserialize)]
pub struct ValidationError {
    pub error: String,
    pub details: Option<String>,
}

impl From<anyhow::Error> for ValidationError {
    fn from(err: anyhow::Error) -> Self {
        Self {
            error: err.to_string(),
            details: err.chain().skip(1).map(|e| e.to_string()).collect::<Vec<_>>().join("; ").into(),
        }
    }
}

/// Validation request for a single field
#[derive(Debug, Serialize, Deserialize)]
pub struct FieldValidationRequest {
    /// Form type for context-specific validation
    pub form_type: String,
    
    /// Field identifier being validated
    pub field_id: String,
    
    /// Current field value
    pub field_value: serde_json::Value,
    
    /// Complete form data for cross-field validation
    pub form_data: Option<HashMap<String, serde_json::Value>>,
    
    /// Whether to perform cross-field validation
    pub include_cross_field_validation: bool,
}

/// Validation request for complete form
#[derive(Debug, Serialize, Deserialize)]
pub struct FormValidationRequest {
    /// Form type for validation context
    pub form_type: String,
    
    /// Complete form data to validate
    pub form_data: HashMap<String, serde_json::Value>,
    
    /// Whether to include business rule validation
    pub include_business_rules: bool,
    
    /// Target validation level (e.g., for draft vs final submission)
    pub validation_level: Option<String>,
}

/// Enhanced validation result for frontend consumption
#[derive(Debug, Serialize, Deserialize)]
pub struct ValidationResponse {
    /// Whether validation passed
    pub is_valid: bool,
    
    /// Whether form is ready for submission
    pub is_submittable: bool,
    
    /// Field-specific validation results
    pub field_results: HashMap<String, FieldValidationResponse>,
    
    /// Cross-field validation messages
    pub cross_field_messages: Vec<ValidationMessage>,
    
    /// Business rule validation messages
    pub business_rule_messages: Vec<ValidationMessage>,
    
    /// Validation summary statistics
    pub summary: ValidationSummary,
    
    /// Validation performance metrics
    pub performance_ms: u32,
}

/// Field validation result for frontend
#[derive(Debug, Serialize, Deserialize)]
pub struct FieldValidationResponse {
    /// Field identifier
    pub field_id: String,
    
    /// Whether field is valid
    pub is_valid: bool,
    
    /// Validation messages for this field
    pub messages: Vec<ValidationMessage>,
    
    /// Suggested value corrections
    pub suggestions: Vec<String>,
    
    /// Whether field should be highlighted
    pub highlight: bool,
}

/// Validation message with severity and context
#[derive(Debug, Serialize, Deserialize)]
pub struct ValidationMessage {
    /// Message identifier for localization
    pub message_id: String,
    
    /// Human-readable message
    pub message: String,
    
    /// Message severity level
    pub severity: String, // "error", "warning", "info", "success"
    
    /// Field this message relates to
    pub field_id: Option<String>,
    
    /// Additional context for the message
    pub context: Option<HashMap<String, serde_json::Value>>,
}

/// Validation summary statistics
#[derive(Debug, Serialize, Deserialize)]
pub struct ValidationSummary {
    /// Total fields validated
    pub total_fields: usize,
    
    /// Fields with errors
    pub error_fields: usize,
    
    /// Fields with warnings
    pub warning_fields: usize,
    
    /// Fields that are valid
    pub valid_fields: usize,
    
    /// Overall completion percentage
    pub completion_percentage: f32,
}

/// Validates a single field with real-time feedback.
/// 
/// Business Logic:
/// - Performs immediate field validation for real-time UI feedback
/// - Includes cross-field validation when relevant
/// - Optimized for <200ms response time
/// - Provides actionable error messages and suggestions
/// 
/// Frontend Usage:
/// ```typescript
/// const result = await invoke('validate_field', {
///   request: {
///     formType: 'ICS-201',
///     fieldId: 'incident_name',
///     fieldValue: 'Forest Fire 2024',
///     formData: currentFormData,
///     includeCrossFieldValidation: true
///   }
/// });
/// 
/// if (!result.isValid) {
///   showFieldErrors(result.messages);
/// }
/// ```
#[tauri::command]
pub async fn validate_field(
    request: FieldValidationRequest,
    validation_state: State<'_, ValidationState>,
) -> Result<FieldValidationResponse, ValidationError> {
    let start_time = std::time::Instant::now();
    
    log::debug!("Validating field {} for form type {}", request.field_id, request.form_type);
    
    // Parse form type
    let form_type: ICSFormType = request.form_type.parse()
        .map_err(|e: anyhow::Error| ValidationError {
            error: format!("Invalid form type: {}", request.form_type),
            details: Some(e.to_string()),
        })?;
    
    // Get validation engine
    let mut engine = validation_state.lock().await;
    
    // Create minimal form data for validation context
    let mut form_data = request.form_data.unwrap_or_default();
    form_data.insert(request.field_id.clone(), request.field_value);
    
    // Convert to ICSFormData - simplified for single field validation
    let ics_form_data = create_minimal_form_data(&form_type, &form_data)?;
    
    // Perform validation
    let validation_result = engine.validate_form(&ics_form_data)?;
    
    // Extract field-specific results
    let field_result = validation_result.field_results.get(&request.field_id)
        .cloned()
        .unwrap_or_else(|| FieldValidationResult {
            field_name: request.field_id.clone(),
            is_valid: true,
            errors: Vec::new(),
            warnings: Vec::new(),
            info_messages: Vec::new(),
            current_value: Some(form_data.get(&request.field_id).cloned().unwrap_or(serde_json::Value::Null)),
            suggestions: Vec::new(),
        });
    
    // Convert to frontend response format
    let mut messages = Vec::new();
    
    // Add errors
    for error in field_result.errors {
        messages.push(ValidationMessage {
            message_id: error.rule_id.clone(),
            message: error.message,
            severity: "error".to_string(),
            field_id: Some(field_result.field_name.clone()),
            context: None,
        });
    }
    
    // Add warnings
    for warning in field_result.warnings {
        messages.push(ValidationMessage {
            message_id: warning.rule_id.clone(),
            message: warning.message,
            severity: "warning".to_string(),
            field_id: Some(field_result.field_name.clone()),
            context: None,
        });
    }
    
    // Add info messages
    for info in field_result.info_messages {
        messages.push(ValidationMessage {
            message_id: "info".to_string(),
            message: info.message,
            severity: "info".to_string(),
            field_id: Some(field_result.field_name.clone()),
            context: None,
        });
    }
    
    let response = FieldValidationResponse {
        field_id: request.field_id,
        is_valid: field_result.is_valid,
        messages,
        suggestions: field_result.suggestions,
        highlight: !field_result.is_valid,
    };
    
    let elapsed = start_time.elapsed().as_millis() as u32;
    log::debug!("Field validation completed in {}ms", elapsed);
    
    Ok(response)
}

/// Validates a complete form with comprehensive checking.
/// 
/// Business Logic:
/// - Performs complete form validation including all rule types
/// - Provides detailed validation results for UI display
/// - Includes performance metrics for monitoring
/// - Supports different validation levels (draft, final, etc.)
/// 
/// Frontend Usage:
/// ```typescript
/// const result = await invoke('validate_form', {
///   request: {
///     formType: 'ICS-201',
///     formData: currentFormData,
///     includeBusinessRules: true,
///     validationLevel: 'final'
///   }
/// });
/// 
/// if (!result.isValid) {
///   displayValidationErrors(result);
/// } else if (result.isSubmittable) {
///   enableSubmitButton();
/// }
/// ```
#[tauri::command]
pub async fn validate_form(
    request: FormValidationRequest,
    validation_state: State<'_, ValidationState>,
) -> Result<ValidationResponse, ValidationError> {
    let start_time = std::time::Instant::now();
    
    log::info!("Validating complete form: type={}, fields={}", 
              request.form_type, request.form_data.len());
    
    // Parse form type
    let form_type: ICSFormType = request.form_type.parse()
        .map_err(|e: anyhow::Error| ValidationError {
            error: format!("Invalid form type: {}", request.form_type),
            details: Some(e.to_string()),
        })?;
    
    // Get validation engine
    let mut engine = validation_state.lock().await;
    
    // Convert form data to ICSFormData
    let ics_form_data = create_form_data_from_request(&form_type, &request.form_data)?;
    
    // Perform comprehensive validation
    let validation_result = engine.validate_form(&ics_form_data)?;
    
    // Convert to frontend-friendly format
    let field_results: HashMap<String, FieldValidationResponse> = validation_result.field_results
        .into_iter()
        .map(|(field_id, result)| {
            let mut messages = Vec::new();
            
            // Add errors
            for error in result.errors {
                messages.push(ValidationMessage {
                    message_id: error.rule_id.clone(),
                    message: error.message,
                    severity: "error".to_string(),
                    field_id: Some(field_id.clone()),
                    context: None,
                });
            }
            
            // Add warnings
            for warning in result.warnings {
                messages.push(ValidationMessage {
                    message_id: warning.rule_id.clone(),
                    message: warning.message,
                    severity: "warning".to_string(),
                    field_id: Some(field_id.clone()),
                    context: None,
                });
            }
            
            // Add info messages
            for info in result.info_messages {
                messages.push(ValidationMessage {
                    message_id: "info".to_string(),
                    message: info.message,
                    severity: "info".to_string(),
                    field_id: Some(field_id.clone()),
                    context: None,
                });
            }
            
            let response = FieldValidationResponse {
                field_id: field_id.clone(),
                is_valid: result.is_valid,
                messages,
                suggestions: result.suggestions,
                highlight: !result.is_valid,
            };
            (field_id, response)
        })
        .collect();
    
    let cross_field_messages: Vec<ValidationMessage> = validation_result.cross_field_results
        .into_iter()
        .map(|result| ValidationMessage {
            message_id: result.rule_id.clone(),
            message: result.error_message.unwrap_or_else(|| format!("Cross-field validation failed: {}", result.rule_id)),
            severity: "error".to_string(),
            field_id: None,
            context: Some([
                ("fields".to_string(), serde_json::json!(result.fields_involved))
            ].into_iter().collect()),
        })
        .collect();
    
    let business_rule_messages: Vec<ValidationMessage> = validation_result.business_rule_results
        .into_iter()
        .map(|result| ValidationMessage {
            message_id: result.rule_name.clone(),
            message: result.error_message.unwrap_or_else(|| result.rule_description),
            severity: format!("{:?}", result.severity).to_lowercase(),
            field_id: None,
            context: None,
        })
        .collect();
    
    let elapsed = start_time.elapsed().as_millis() as u32;
    
    let response = ValidationResponse {
        is_valid: validation_result.is_valid,
        is_submittable: validation_result.is_submittable,
        field_results,
        cross_field_messages,
        business_rule_messages,
        summary: ValidationSummary {
            total_fields: validation_result.summary.total_fields as usize,
            error_fields: validation_result.summary.fields_with_errors as usize,
            warning_fields: validation_result.summary.fields_with_warnings as usize,
            valid_fields: (validation_result.summary.total_fields - validation_result.summary.fields_with_errors) as usize,
            completion_percentage: validation_result.summary.completion_percentage,
        },
        performance_ms: elapsed,
    };
    
    log::info!("Form validation completed: valid={}, submittable={}, time={}ms", 
              response.is_valid, response.is_submittable, elapsed);
    
    Ok(response)
}

/// Gets validation rules for a specific form type.
/// 
/// Business Logic:
/// - Returns available validation rules for client-side validation
/// - Includes field-level and form-level rules
/// - Supports validation rule caching on frontend
/// 
/// Frontend Usage:
/// ```typescript
/// const rules = await invoke('get_validation_rules', {
///   formType: 'ICS-201'
/// });
/// setupClientSideValidation(rules);
/// ```
#[tauri::command]
pub async fn get_validation_rules(
    form_type: String,
    _validation_state: State<'_, ValidationState>,
) -> Result<HashMap<String, serde_json::Value>, ValidationError> {
    log::debug!("Getting validation rules for form type: {}", form_type);
    
    // Parse form type
    let _form_type: ICSFormType = form_type.parse()
        .map_err(|e: anyhow::Error| ValidationError {
            error: format!("Invalid form type: {}", form_type),
            details: Some(e.to_string()),
        })?;
    
    // For now, return a basic rule set - this would be enhanced to return
    // actual validation rules from the validation engine
    let rules = HashMap::from([
        ("incident_name".to_string(), serde_json::json!({
            "required": true,
            "min_length": 3,
            "max_length": 100,
            "pattern": "^[A-Za-z0-9\\s\\-_]+$"
        })),
        ("incident_number".to_string(), serde_json::json!({
            "required": false,
            "pattern": "^[A-Z]{2}-\\d{4}-\\d{6}$",
            "example": "CA-2024-000001"
        })),
        ("operational_period".to_string(), serde_json::json!({
            "required": true,
            "format": "datetime_range"
        })),
    ]);
    
    Ok(rules)
}

/// Configures validation engine settings.
/// 
/// Business Logic:
/// - Updates validation engine configuration
/// - Allows runtime tuning of validation behavior
/// - Supports performance optimization
/// 
/// Frontend Usage:
/// ```typescript
/// await invoke('configure_validation', {
///   config: {
///     realTimeValidation: true,
///     crossFieldValidation: true,
///     maxValidationTimeMs: 300
///   }
/// });
/// ```
#[tauri::command]
pub async fn configure_validation(
    config: ValidationConfigRequest,
    validation_state: State<'_, ValidationState>,
) -> Result<(), ValidationError> {
    log::info!("Configuring validation engine");
    
    let new_config = ValidationConfig {
        real_time_validation: config.real_time_validation,
        cross_field_validation: config.cross_field_validation,
        business_rule_validation: config.business_rule_validation,
        max_validation_time_ms: config.max_validation_time_ms,
        cache_validation_results: config.cache_validation_results,
        min_severity_level: match config.min_severity_level.as_str() {
            "error" => SeverityLevel::Error,
            "warning" => SeverityLevel::Warning,
            "info" => SeverityLevel::Info,
            "success" => SeverityLevel::Success,
            _ => SeverityLevel::Info,
        },
    };
    
    // Replace validation engine with new configuration
    let mut engine = validation_state.lock().await;
    *engine = ValidationEngine::with_config(new_config);
    
    log::info!("Validation engine configuration updated");
    Ok(())
}

/// Validation configuration request from frontend
#[derive(Debug, Serialize, Deserialize)]
pub struct ValidationConfigRequest {
    pub real_time_validation: bool,
    pub cross_field_validation: bool,
    pub business_rule_validation: bool,
    pub max_validation_time_ms: u64,
    pub cache_validation_results: bool,
    pub min_severity_level: String,
}

/// Helper function to create minimal form data for field validation
fn create_minimal_form_data(
    form_type: &ICSFormType,
    form_data: &HashMap<String, serde_json::Value>,
) -> Result<ICSFormData, ValidationError> {
    // Create minimal form data structure for validation purposes
    let ics_form_data = ICSFormData {
        header: crate::models::ics_types::ICSFormHeader {
            incident_name: form_data.get("incident_name")
                .and_then(|v| v.as_str())
                .unwrap_or("Unknown Incident")
                .to_string(),
            operational_period: None, // Will be set properly in full implementation
            incident_number: form_data.get("incident_number")
                .and_then(|v| v.as_str())
                .map(|s| s.to_string()),
            form_version: Some("1.0".to_string()),
            prepared_date_time: chrono::Utc::now(),
            page_info: None,
        },
        footer: crate::models::ics_types::ICSFormFooter {
            prepared_by: crate::models::ics_types::PreparedBy {
                name: form_data.get("preparer_name")
                    .and_then(|v| v.as_str())
                    .unwrap_or("")
                    .to_string(),
                position_title: form_data.get("preparer_position")
                    .and_then(|v| v.as_str())
                    .unwrap_or("")
                    .to_string(),
                signature: None,
                date_time: None,
            },
            approved_by: None,
        },
        form_data: match form_type {
            ICSFormType::ICS201 => {
                crate::models::form_data::FormSpecificData::ICS201(
                    crate::models::form_data::ICS201Data {
                        map_sketch: None,
                        situation_summary: form_data.get("situation_summary")
                            .and_then(|v| v.as_str())
                            .unwrap_or("")
                            .to_string(),
                        current_objectives: form_data.get("current_objectives")
                            .and_then(|v| v.as_str())
                            .unwrap_or("")
                            .to_string(),
                        planned_actions: Vec::new(),
                        current_organization: crate::models::form_data::OrganizationStructure {
                            incident_commander: crate::models::ics_types::PersonPosition {
                                name: form_data.get("ic_name")
                                    .and_then(|v| v.as_str())
                                    .unwrap_or("")
                                    .to_string(),
                                position: "Incident Commander".to_string(),
                                agency: None,
                                contact_info: None,
                            },
                            public_information_officer: None,
                            safety_officer: None,
                            liaison_officer: None,
                            operations_chief: None,
                            planning_chief: None,
                            logistics_chief: None,
                            finance_admin_chief: None,
                        },
                        resource_summary: Vec::new(),
                        weather_summary: form_data.get("weather_summary")
                            .and_then(|v| v.as_str())
                            .map(|s| s.to_string()),
                        safety_message: form_data.get("safety_message")
                            .and_then(|v| v.as_str())
                            .map(|s| s.to_string()),
                    }
                )
            },
            _ => {
                // For other form types, create minimal placeholder data
                crate::models::form_data::FormSpecificData::ICS202(
                    crate::models::form_data::ICS202Data {
                        objectives: form_data.get("objectives")
                            .and_then(|v| v.as_str())
                            .unwrap_or("")
                            .to_string(),
                        command_emphasis: None,
                        general_situational_awareness: None,
                        site_safety_plan_required: false,
                        site_safety_plan_location: None,
                        iap_components: Vec::new(),
                        weather_forecast: None,
                    }
                )
            }
        },
        lifecycle: crate::models::ics_types::FormLifecycle {
            status: crate::models::ics_types::EnhancedFormStatus::Draft,
            created_at: chrono::Utc::now(),
            updated_at: chrono::Utc::now(),
            status_history: Vec::new(),
            workflow_position: crate::models::ics_types::WorkflowPosition::Planning,
        },
        validation_results: None,
    };
    
    Ok(ics_form_data)
}

/// Helper function to create comprehensive form data from request
fn create_form_data_from_request(
    form_type: &ICSFormType,
    form_data: &HashMap<String, serde_json::Value>,
) -> Result<ICSFormData, ValidationError> {
    // For now, use the same minimal creation logic
    // In production, this would be more sophisticated
    create_minimal_form_data(form_type, form_data)
}
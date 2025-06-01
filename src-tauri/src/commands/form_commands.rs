/*!
 * Form-related Tauri commands - Enhanced with Enterprise CRUD Operations
 * 
 * This module contains all Tauri commands related to form management.
 * These commands handle CRUD operations, search, and form lifecycle
 * management using the enhanced enterprise-grade operations.
 * 
 * Business Logic:
 * - All form operations go through the enhanced FormModel for consistency
 * - Proper error handling with user-friendly messages
 * - Input validation for all command parameters
 * - Comprehensive logging for debugging and audit
 * - Transaction support and optimistic locking
 */

use tauri::State;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::Mutex;
use chrono::{DateTime, Utc};

use crate::database::Database;
use crate::models::form::{FormModel, CreateFormRequest, UpdateFormRequest, FormFilters, FormSearchResult};
use crate::database::schema::{Form, ICSFormType, FormStatus};
use crate::templates::loader::TemplateLoader;

/// Application state containing database connection
pub type AppState = Arc<Mutex<Database>>;

/// Error response structure for consistent error handling
#[derive(Debug, Serialize, Deserialize)]
pub struct ErrorResponse {
    pub error: String,
    pub details: Option<String>,
}

impl From<anyhow::Error> for ErrorResponse {
    fn from(err: anyhow::Error) -> Self {
        Self {
            error: err.to_string(),
            details: err.chain().skip(1).map(|e| e.to_string()).collect::<Vec<_>>().join("; ").into(),
        }
    }
}

/// Creates a new form with comprehensive validation and transaction support.
/// 
/// Business Logic:
/// - Uses enterprise CRUD operations for enhanced validation
/// - Supports operational period validation per ICS standards
/// - Provides transaction safety and rollback support
/// - Supports template-based form creation
/// 
/// Frontend Usage:
/// ```typescript
/// const form = await invoke('create_form', {
///   formType: 'ICS-201',
///   incidentName: 'Forest Fire Response',
///   incidentNumber: 'FF-2024-001',
///   preparerName: 'John Smith',
///   operationalPeriodStart: '2024-01-01T08:00:00Z',
///   operationalPeriodEnd: '2024-01-01T20:00:00Z',
///   templateId: 1,
///   priority: 'urgent'
/// });
/// ```
#[tauri::command]
pub async fn create_form(
    form_type: String,
    incident_name: String,
    incident_number: Option<String>,
    preparer_name: Option<String>,
    initial_data: Option<std::collections::HashMap<String, serde_json::Value>>,
    operational_period_start: Option<String>,
    operational_period_end: Option<String>,
    template_id: Option<i64>,
    priority: Option<String>,
    state: State<'_, AppState>,
) -> Result<Form, ErrorResponse> {
    log::info!("Creating new form: type={}, incident={}", form_type, incident_name);

    // Validate input parameters
    if incident_name.trim().is_empty() {
        return Err(ErrorResponse {
            error: "Incident name cannot be empty".to_string(),
            details: None,
        });
    }

    let form_type: ICSFormType = form_type.parse()
        .map_err(|e: anyhow::Error| ErrorResponse {
            error: format!("Invalid form type: {}", form_type),
            details: Some(e.to_string()),
        })?;

    // Parse operational period dates if provided
    let operational_period_start = if let Some(date_str) = operational_period_start {
        Some(DateTime::parse_from_rfc3339(&date_str)
            .map_err(|e| ErrorResponse {
                error: "Invalid operational period start date".to_string(),
                details: Some(e.to_string()),
            })?
            .with_timezone(&Utc))
    } else {
        None
    };

    let operational_period_end = if let Some(date_str) = operational_period_end {
        Some(DateTime::parse_from_rfc3339(&date_str)
            .map_err(|e| ErrorResponse {
                error: "Invalid operational period end date".to_string(),
                details: Some(e.to_string()),
            })?
            .with_timezone(&Utc))
    } else {
        None
    };

    // Get database and create enhanced FormModel
    let db = state.lock().await;
    
    // We need to clone the database for the FormModel
    // This is a temporary approach - in a production system, we might use Arc<Database>
    let database_clone = Database::new().await.map_err(|e| ErrorResponse {
        error: "Failed to create database connection".to_string(),
        details: Some(e.to_string()),
    })?;
    
    let form_model = FormModel::new(database_clone);

    // Enhanced template-based form creation
    let mut enhanced_initial_data = initial_data.unwrap_or_default();
    
    // If template_id is provided, load template and populate defaults
    if template_id.is_some() {
        // Load template data from the comprehensive template system
        match TemplateLoader::new() {
            Ok(template_loader) => {
                if let Some(template) = template_loader.get_template(&form_type.to_string()) {
                    log::info!("Applying template '{}' for form type '{}'", template.template_id, form_type);
                    
                    // Populate form data with template defaults
                    for (field_id, default_value) in &template.defaults {
                        if !enhanced_initial_data.contains_key(field_id) {
                            enhanced_initial_data.insert(field_id.clone(), default_value.clone());
                        }
                    }
                    
                    // Add template metadata to form data
                    enhanced_initial_data.insert("template_id".to_string(), 
                                                serde_json::Value::String(template.template_id.clone()));
                    enhanced_initial_data.insert("template_version".to_string(), 
                                                serde_json::Value::String(template.version.clone()));
                    
                    log::debug!("Applied {} default values from template", template.defaults.len());
                } else {
                    log::warn!("Template not found for form type: {}", form_type);
                }
            },
            Err(e) => {
                log::error!("Failed to load template loader: {}", e);
                return Err(ErrorResponse {
                    error: "Failed to load form templates".to_string(),
                    details: Some(e.to_string()),
                });
            }
        }
    }
    
    let request = CreateFormRequest {
        form_type,
        incident_name,
        incident_number,
        preparer_name,
        initial_data: Some(enhanced_initial_data),
        operational_period_start,
        operational_period_end,
        template_id,
        priority,
    };

    let form = form_model.create_form(request).await?;
    
    log::info!("Form created successfully: id={}, type={:?}", form.id, form.form_type());
    Ok(form)
}

/// Retrieves a form by its ID with comprehensive error handling.
/// 
/// Business Logic:
/// - Uses enhanced CRUD operations for validation
/// - Provides detailed error messages for invalid IDs
/// - Returns null if form doesn't exist
/// 
/// Frontend Usage:
/// ```typescript
/// const form = await invoke('get_form', { id: 123 });
/// if (form) {
///   console.log('Form found:', form);
/// }
/// ```
#[tauri::command]
pub async fn get_form(
    id: i64,
    state: State<'_, AppState>,
) -> Result<Option<Form>, ErrorResponse> {
    log::debug!("Fetching form: id={}", id);

    if id <= 0 {
        return Err(ErrorResponse {
            error: "Invalid form ID".to_string(),
            details: Some(format!("ID must be positive, got: {}", id)),
        });
    }

    let db = state.lock().await;
    
    // Create database clone for FormModel
    let database_clone = Database::new().await.map_err(|e| ErrorResponse {
        error: "Failed to create database connection".to_string(),
        details: Some(e.to_string()),
    })?;
    
    let form_model = FormModel::new(database_clone);

    let form = form_model.get_form_by_id(id).await?;
    
    if form.is_some() {
        log::debug!("Form retrieved successfully: id={}", id);
    } else {
        log::debug!("Form not found: id={}", id);
    }

    Ok(form)
}

/// Updates an existing form with optimistic locking and comprehensive validation.
/// 
/// Business Logic:
/// - Uses enterprise CRUD operations for comprehensive validation
/// - Supports optimistic locking to prevent conflicts
/// - Validates status transitions and business rules
/// - Provides transaction safety and audit trail
/// 
/// Frontend Usage:
/// ```typescript
/// const updatedForm = await invoke('update_form', {
///   id: 123,
///   updates: {
///     incidentName: 'Updated Incident Name',
///     status: 'completed',
///     data: { field1: 'value1', field2: 'value2' },
///     expectedVersion: 5  // For optimistic locking
///   }
/// });
/// ```
#[tauri::command]
pub async fn update_form(
    id: i64,
    incident_name: Option<String>,
    incident_number: Option<String>,
    status: Option<String>,
    data: Option<std::collections::HashMap<String, serde_json::Value>>,
    notes: Option<String>,
    preparer_name: Option<String>,
    operational_period_start: Option<String>,
    operational_period_end: Option<String>,
    priority: Option<String>,
    workflow_position: Option<String>,
    expected_version: Option<i64>,
    state: State<'_, AppState>,
) -> Result<Form, ErrorResponse> {
    log::info!("Updating form: id={}", id);

    if id <= 0 {
        return Err(ErrorResponse {
            error: "Invalid form ID".to_string(),
            details: Some(format!("ID must be positive, got: {}", id)),
        });
    }

    // Parse status if provided
    let status = if let Some(status_str) = status {
        Some(status_str.parse::<FormStatus>()
            .map_err(|e: anyhow::Error| ErrorResponse {
                error: format!("Invalid status: {}", status_str),
                details: Some(e.to_string()),
            })?)
    } else {
        None
    };

    // Parse operational period dates if provided
    let operational_period_start = if let Some(date_str) = operational_period_start {
        Some(DateTime::parse_from_rfc3339(&date_str)
            .map_err(|e| ErrorResponse {
                error: "Invalid operational period start date".to_string(),
                details: Some(e.to_string()),
            })?
            .with_timezone(&Utc))
    } else {
        None
    };

    let operational_period_end = if let Some(date_str) = operational_period_end {
        Some(DateTime::parse_from_rfc3339(&date_str)
            .map_err(|e| ErrorResponse {
                error: "Invalid operational period end date".to_string(),
                details: Some(e.to_string()),
            })?
            .with_timezone(&Utc))
    } else {
        None
    };

    let db = state.lock().await;
    
    // Create database clone for FormModel
    let database_clone = Database::new().await.map_err(|e| ErrorResponse {
        error: "Failed to create database connection".to_string(),
        details: Some(e.to_string()),
    })?;
    
    let form_model = FormModel::new(database_clone);

    let updates = UpdateFormRequest {
        incident_name,
        incident_number,
        status,
        data,
        notes,
        preparer_name,
        operational_period_start,
        operational_period_end,
        priority,
        workflow_position,
        expected_version,
    };

    let form = form_model.update_form(id, updates).await?;
    
    log::info!("Form updated successfully: id={}, status={:?}", form.id, form.status());
    Ok(form)
}

/// Deletes a form with proper validation and cascade handling.
/// 
/// Business Logic:
/// - Uses enterprise CRUD operations for validation
/// - Handles cascade deletion of related records
/// - Validates deletion permissions based on form status
/// - Provides force deletion option for administrative purposes
/// 
/// Frontend Usage:
/// ```typescript
/// const deleted = await invoke('delete_form', { id: 123, force: false });
/// if (deleted) {
///   console.log('Form deleted successfully');
/// }
/// ```
#[tauri::command]
pub async fn delete_form(
    id: i64,
    force: Option<bool>,
    state: State<'_, AppState>,
) -> Result<bool, ErrorResponse> {
    log::info!("Deleting form: id={}, force={:?}", id, force);

    if id <= 0 {
        return Err(ErrorResponse {
            error: "Invalid form ID".to_string(),
            details: Some(format!("ID must be positive, got: {}", id)),
        });
    }

    let db = state.lock().await;
    
    // Create database clone for FormModel
    let database_clone = Database::new().await.map_err(|e| ErrorResponse {
        error: "Failed to create database connection".to_string(),
        details: Some(e.to_string()),
    })?;
    
    let form_model = FormModel::new(database_clone);

    let deleted = form_model.delete_form(id, force.unwrap_or(false)).await?;
    
    if deleted {
        log::info!("Form deleted successfully: id={}", id);
    } else {
        log::debug!("Form not found for deletion: id={}", id);
    }

    Ok(deleted)
}

/// Searches forms with comprehensive filtering and pagination.
/// 
/// Business Logic:
/// - Uses enterprise CRUD operations for optimized search
/// - Supports multiple filter criteria with efficient indexing
/// - Provides pagination for large result sets
/// - Includes search performance metrics
/// 
/// Frontend Usage:
/// ```typescript
/// const results = await invoke('search_forms', {
///   filters: {
///     incidentName: 'Fire',
///     status: 'completed',
///     limit: 20,
///     offset: 0,
///     orderBy: 'updated_at',
///     orderDirection: 'DESC'
///   }
/// });
/// console.log(`Found ${results.total_count} forms in ${results.search_time_ms}ms`);
/// ```
#[tauri::command]
pub async fn search_forms(
    incident_name: Option<String>,
    form_type: Option<String>,
    status: Option<String>,
    preparer_name: Option<String>,
    date_from: Option<String>,
    date_to: Option<String>,
    priority: Option<String>,
    workflow_position: Option<String>,
    full_text_search: Option<String>,
    limit: Option<i64>,
    offset: Option<i64>,
    order_by: Option<String>,
    order_direction: Option<String>,
    state: State<'_, AppState>,
) -> Result<FormSearchResult, ErrorResponse> {
    log::debug!("Searching forms with enhanced filters");

    // Parse form type if provided
    let form_type = if let Some(type_str) = form_type {
        Some(type_str.parse::<ICSFormType>()
            .map_err(|e: anyhow::Error| ErrorResponse {
                error: format!("Invalid form type: {}", type_str),
                details: Some(e.to_string()),
            })?)
    } else {
        None
    };

    // Parse status if provided
    let status = if let Some(status_str) = status {
        Some(status_str.parse::<FormStatus>()
            .map_err(|e: anyhow::Error| ErrorResponse {
                error: format!("Invalid status: {}", status_str),
                details: Some(e.to_string()),
            })?)
    } else {
        None
    };

    // Parse dates if provided
    let date_from = if let Some(date_str) = date_from {
        Some(DateTime::parse_from_rfc3339(&date_str)
            .map_err(|e| ErrorResponse {
                error: "Invalid date_from format".to_string(),
                details: Some(e.to_string()),
            })?
            .with_timezone(&Utc))
    } else {
        None
    };

    let date_to = if let Some(date_str) = date_to {
        Some(DateTime::parse_from_rfc3339(&date_str)
            .map_err(|e| ErrorResponse {
                error: "Invalid date_to format".to_string(),
                details: Some(e.to_string()),
            })?
            .with_timezone(&Utc))
    } else {
        None
    };

    let db = state.lock().await;
    
    // Create database clone for FormModel
    let database_clone = Database::new().await.map_err(|e| ErrorResponse {
        error: "Failed to create database connection".to_string(),
        details: Some(e.to_string()),
    })?;
    
    let form_model = FormModel::new(database_clone);

    let filters = FormFilters {
        incident_name,
        form_type,
        status,
        preparer_name,
        date_from,
        date_to,
        priority,
        workflow_position,
        full_text_search,
        limit,
        offset,
        order_by,
        order_direction,
    };

    let result = form_model.search_forms(filters).await?;
    
    log::debug!("Search completed: found {} forms in {}ms", 
               result.forms.len(), result.search_time_ms);
    Ok(result)
}

/// Gets all forms for a specific incident.
/// 
/// Business Logic:
/// - Uses enhanced search capabilities for incident filtering
/// - Returns all forms (all statuses) for the specified incident
/// - Sorted by form type for logical ordering
/// 
/// Frontend Usage:
/// ```typescript
/// const incidentForms = await invoke('get_forms_by_incident', {
///   incidentName: 'Forest Fire Response'
/// });
/// ```
#[tauri::command]
pub async fn get_forms_by_incident(
    incident_name: String,
    state: State<'_, AppState>,
) -> Result<Vec<Form>, ErrorResponse> {
    log::debug!("Fetching forms for incident: {}", incident_name);

    if incident_name.trim().is_empty() {
        return Err(ErrorResponse {
            error: "Incident name cannot be empty".to_string(),
            details: None,
        });
    }

    let db = state.lock().await;
    
    // Create database clone for FormModel
    let database_clone = Database::new().await.map_err(|e| ErrorResponse {
        error: "Failed to create database connection".to_string(),
        details: Some(e.to_string()),
    })?;
    
    let form_model = FormModel::new(database_clone);

    let forms = form_model.get_forms_by_incident(&incident_name).await?;
    
    log::debug!("Retrieved {} forms for incident: {}", forms.len(), incident_name);
    Ok(forms)
}

/// Gets recent forms with enhanced ordering and performance.
/// 
/// Business Logic:
/// - Uses enhanced search capabilities with ordering
/// - Returns forms ordered by last update time (newest first)
/// - Limited to reasonable number for performance
/// 
/// Frontend Usage:
/// ```typescript
/// const recentForms = await invoke('get_recent_forms', { limit: 10 });
/// ```
#[tauri::command]
pub async fn get_recent_forms(
    limit: Option<i64>,
    state: State<'_, AppState>,
) -> Result<Vec<Form>, ErrorResponse> {
    log::debug!("Fetching recent forms: limit={:?}", limit);

    let db = state.lock().await;
    
    // Create database clone for FormModel
    let database_clone = Database::new().await.map_err(|e| ErrorResponse {
        error: "Failed to create database connection".to_string(),
        details: Some(e.to_string()),
    })?;
    
    let form_model = FormModel::new(database_clone);

    let forms = form_model.get_recent_forms(limit).await?;
    
    log::debug!("Retrieved {} recent forms", forms.len());
    Ok(forms)
}

/// Duplicates an existing form as a new draft with enhanced capabilities.
/// 
/// Business Logic:
/// - Uses enterprise CRUD operations for consistency
/// - Creates a copy of an existing form
/// - New form starts as Draft status
/// - Updates preparation date/time to current
/// - Optionally changes incident name
/// 
/// Frontend Usage:
/// ```typescript
/// const duplicatedForm = await invoke('duplicate_form', {
///   sourceId: 123,
///   newIncidentName: 'New Incident Name' // optional
/// });
/// ```
#[tauri::command]
pub async fn duplicate_form(
    source_id: i64,
    new_incident_name: Option<String>,
    state: State<'_, AppState>,
) -> Result<Form, ErrorResponse> {
    log::info!("Duplicating form: source_id={}, new_incident={:?}", source_id, new_incident_name);

    if source_id <= 0 {
        return Err(ErrorResponse {
            error: "Invalid source form ID".to_string(),
            details: Some(format!("ID must be positive, got: {}", source_id)),
        });
    }

    let db = state.lock().await;
    
    // Create database clone for FormModel
    let database_clone = Database::new().await.map_err(|e| ErrorResponse {
        error: "Failed to create database connection".to_string(),
        details: Some(e.to_string()),
    })?;
    
    let form_model = FormModel::new(database_clone);

    let form = form_model.duplicate_form(source_id, new_incident_name).await?;
    
    log::info!("Form duplicated successfully: source_id={}, new_id={}", source_id, form.id);
    Ok(form)
}

/// Gets list of all supported ICS form types with enhanced metadata.
/// 
/// Business Logic:
/// - Returns comprehensive metadata about all supported form types
/// - Useful for form type selection dropdowns
/// - Includes form descriptions, categories, and complexity ratings
/// 
/// Frontend Usage:
/// ```typescript
/// const formTypes = await invoke('get_form_types');
/// console.log('Available form types:', formTypes);
/// ```
#[tauri::command]
pub async fn get_form_types() -> Result<Vec<FormTypeInfo>, ErrorResponse> {
    log::debug!("Fetching supported form types with enhanced metadata");

    let form_types = vec![
        FormTypeInfo { 
            code: "ICS-201".to_string(), 
            name: "Incident Briefing".to_string(),
            description: "Initial incident briefing and situation assessment".to_string(),
            category: "Planning".to_string(),
            complexity: "Medium".to_string(),
            typical_duration_minutes: 30,
        },
        FormTypeInfo { 
            code: "ICS-202".to_string(), 
            name: "Incident Objectives".to_string(),
            description: "Incident objectives, priorities, and safety considerations".to_string(),
            category: "Planning".to_string(),
            complexity: "Medium".to_string(),
            typical_duration_minutes: 45,
        },
        FormTypeInfo { 
            code: "ICS-203".to_string(), 
            name: "Organization Assignment List".to_string(),
            description: "Incident organization and personnel assignments".to_string(),
            category: "Planning".to_string(),
            complexity: "High".to_string(),
            typical_duration_minutes: 60,
        },
        FormTypeInfo { 
            code: "ICS-204".to_string(), 
            name: "Assignment List".to_string(),
            description: "Assignment of operational personnel and resources".to_string(),
            category: "Operations".to_string(),
            complexity: "Medium".to_string(),
            typical_duration_minutes: 25,
        },
        FormTypeInfo { 
            code: "ICS-205".to_string(), 
            name: "Incident Radio Communications Plan".to_string(),
            description: "Radio frequency assignments and communication procedures".to_string(),
            category: "Communications".to_string(),
            complexity: "High".to_string(),
            typical_duration_minutes: 40,
        },
        // Additional form types would be added here...
    ];

    log::debug!("Returned {} form types with enhanced metadata", form_types.len());
    Ok(form_types)
}

/// Enhanced form type information for frontend display
#[derive(Debug, Serialize, Deserialize)]
pub struct FormTypeInfo {
    pub code: String,
    pub name: String,
    pub description: String,
    pub category: String,
    pub complexity: String,
    pub typical_duration_minutes: u32,
}

/// Enhanced database statistics for monitoring and performance analysis
#[derive(Debug, Serialize, Deserialize)]
pub struct DatabaseStats {
    pub total_forms: i64,
    pub draft_forms: i64,
    pub completed_forms: i64,
    pub final_forms: i64,
    pub database_size_bytes: u64,
    pub last_backup: Option<String>,
    pub connection_pool_stats: ConnectionPoolStats,
    pub transaction_stats: TransactionStats,
}

/// Connection pool statistics for monitoring
#[derive(Debug, Serialize, Deserialize)]
pub struct ConnectionPoolStats {
    pub size: u32,
    pub idle: usize,
    pub is_closed: bool,
    pub max_connections: u32,
}

/// Transaction statistics for performance monitoring
#[derive(Debug, Serialize, Deserialize)]
pub struct TransactionStats {
    pub total_started: u64,
    pub total_committed: u64,
    pub total_rolled_back: u64,
    pub success_rate: f64,
    pub average_execution_time_ms: f64,
}

/// Gets comprehensive database statistics for monitoring and dashboard display.
/// 
/// Business Logic:
/// - Provides detailed database performance metrics
/// - Includes connection pool utilization
/// - Shows transaction success rates and timing
/// - Supports performance optimization decisions
#[tauri::command]
pub async fn get_database_stats(
    state: State<'_, AppState>
) -> Result<DatabaseStats, ErrorResponse> {
    log::debug!("Fetching comprehensive database statistics");

    let db = state.lock().await;
    
    // Get database statistics
    let db_stats = db.get_stats().await?;
    
    // Get connection pool statistics
    let pool_stats = db.get_pool_stats();
    
    // Get transaction statistics
    let tx_stats = db.get_transaction_stats();

    let stats = DatabaseStats {
        total_forms: db_stats.total_forms,
        draft_forms: db_stats.draft_forms,
        completed_forms: db_stats.completed_forms,
        final_forms: db_stats.final_forms,
        database_size_bytes: db_stats.database_size_bytes,
        last_backup: db_stats.last_backup.map(|dt| dt.to_rfc3339()),
        connection_pool_stats: ConnectionPoolStats {
            size: pool_stats.size,
            idle: pool_stats.idle,
            is_closed: pool_stats.is_closed,
            max_connections: pool_stats.max_connections,
        },
        transaction_stats: TransactionStats {
            total_started: tx_stats.total_started,
            total_committed: tx_stats.total_committed,
            total_rolled_back: tx_stats.total_rolled_back,
            success_rate: tx_stats.success_rate,
            average_execution_time_ms: tx_stats.average_execution_time_ms,
        },
    };

    log::debug!("Database stats: {} total forms, {}% transaction success rate", 
               stats.total_forms, stats.transaction_stats.success_rate);
    Ok(stats)
}

/// Gets available form templates for form creation.
/// 
/// Business Logic:
/// - Loads templates from the comprehensive template system
/// - Returns template metadata for frontend display
/// - Includes template versions and compatibility information
/// 
/// Frontend Usage:
/// ```typescript
/// const templates = await invoke('get_available_templates');
/// console.log('Available templates:', templates);
/// ```
#[tauri::command]
pub async fn get_available_templates() -> Result<Vec<TemplateInfo>, ErrorResponse> {
    log::debug!("Fetching available form templates");

    match TemplateLoader::new() {
        Ok(template_loader) => {
            let all_templates = template_loader.get_all_templates();
            let mut template_infos = Vec::new();
            
            for (form_type, template) in all_templates {
                template_infos.push(TemplateInfo {
                    template_id: template.template_id.clone(),
                    form_type: form_type.clone(),
                    title: template.title.clone(),
                    description: template.description.clone(),
                    version: template.version.clone(),
                    created_at: template.metadata.created_at.clone(),
                    updated_at: template.metadata.updated_at.clone(),
                    author: template.metadata.author.clone(),
                    status: template.metadata.status.clone(),
                    tags: template.metadata.tags.clone(),
                    sections_count: template.sections.len(),
                    fields_count: template_loader.get_template_stats().total_fields,
                    validation_rules_count: template.validation_rules.len(),
                });
            }
            
            log::debug!("Retrieved {} available templates", template_infos.len());
            Ok(template_infos)
        },
        Err(e) => {
            log::error!("Failed to load template loader: {}", e);
            Err(ErrorResponse {
                error: "Failed to load form templates".to_string(),
                details: Some(e.to_string()),
            })
        }
    }
}

/// Gets template details for a specific form type.
/// 
/// Business Logic:
/// - Loads template details including field definitions and help text
/// - Returns comprehensive template structure for form building
/// - Includes validation rules and conditional logic
/// 
/// Frontend Usage:
/// ```typescript
/// const template = await invoke('get_template_details', { formType: 'ICS-201' });
/// if (template) {
///   console.log('Template details:', template);
/// }
/// ```
#[tauri::command]
pub async fn get_template_details(
    form_type: String,
) -> Result<Option<FormTemplateDetails>, ErrorResponse> {
    log::debug!("Fetching template details for form type: {}", form_type);

    match TemplateLoader::new() {
        Ok(template_loader) => {
            if let Some(template) = template_loader.get_template(&form_type) {
                let template_details = FormTemplateDetails {
                    template_id: template.template_id.clone(),
                    form_type: template.form_type.clone(),
                    title: template.title.clone(),
                    description: template.description.clone(),
                    version: template.version.clone(),
                    metadata: template.metadata.clone(),
                    sections: template.sections.clone(),
                    validation_rules: template.validation_rules.clone(),
                    conditional_logic: template.conditional_logic.clone(),
                    defaults: template.defaults.clone(),
                };
                
                log::debug!("Retrieved template details for: {}", form_type);
                Ok(Some(template_details))
            } else {
                log::debug!("Template not found for form type: {}", form_type);
                Ok(None)
            }
        },
        Err(e) => {
            log::error!("Failed to load template loader: {}", e);
            Err(ErrorResponse {
                error: "Failed to load form templates".to_string(),
                details: Some(e.to_string()),
            })
        }
    }
}

/// Template information for frontend display
#[derive(Debug, Serialize, Deserialize)]
pub struct TemplateInfo {
    pub template_id: String,
    pub form_type: String,
    pub title: String,
    pub description: String,
    pub version: String,
    pub created_at: String,
    pub updated_at: String,
    pub author: String,
    pub status: String,
    pub tags: Vec<String>,
    pub sections_count: usize,
    pub fields_count: usize,
    pub validation_rules_count: usize,
}

/// Complete template details including sections and validation rules
#[derive(Debug, Serialize, Deserialize)]
pub struct FormTemplateDetails {
    pub template_id: String,
    pub form_type: String,
    pub title: String,
    pub description: String,
    pub version: String,
    pub metadata: crate::templates::schema::TemplateMetadata,
    pub sections: Vec<crate::templates::schema::FormSection>,
    pub validation_rules: Vec<crate::templates::schema::ValidationRule>,
    pub conditional_logic: Vec<crate::templates::schema::ConditionalRule>,
    pub defaults: std::collections::HashMap<String, serde_json::Value>,
}
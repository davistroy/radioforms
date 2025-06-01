/*!
 * Form-related Tauri commands
 * 
 * This module contains all Tauri commands related to form management.
 * These commands handle CRUD operations, search, and form lifecycle
 * management.
 * 
 * Business Logic:
 * - All form operations go through the FormModel for consistency
 * - Proper error handling with user-friendly messages
 * - Input validation for all command parameters
 * - Comprehensive logging for debugging and audit
 */

use tauri::State;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::Mutex;

use crate::database::Database;
use crate::models::{FormModel, CreateFormRequest, UpdateFormRequest, FormFilters, Form, FormSearchResult, ICSFormType, FormStatus};

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

/// Creates a new form with the specified data.
/// 
/// Business Logic:
/// - Validates all required fields are present
/// - Sets initial form status to Draft
/// - Creates form with current timestamp
/// - Returns the created form with assigned ID
/// 
/// Frontend Usage:
/// ```typescript
/// const form = await invoke('create_form', {
///   formType: 'ICS-201',
///   incidentName: 'Forest Fire Response',
///   incidentNumber: 'FF-2024-001',
///   preparerName: 'John Smith'
/// });
/// ```
#[tauri::command]
pub async fn create_form(
    form_type: String,
    incident_name: String,
    incident_number: Option<String>,
    preparer_name: Option<String>,
    initial_data: Option<std::collections::HashMap<String, serde_json::Value>>,
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
        .map_err(|e| ErrorResponse {
            error: format!("Invalid form type: {}", form_type),
            details: Some(e.to_string()),
        })?;

    let db = state.lock().await;
    let form_model = FormModel::new(db.pool().clone());

    let request = CreateFormRequest {
        form_type,
        incident_name,
        incident_number,
        preparer_name,
        initial_data,
    };

    let form = form_model.create_form(request).await?;
    
    log::info!("Form created successfully: id={}, type={}", form.id, form.form_type);
    Ok(form)
}

/// Retrieves a form by its ID.
/// 
/// Business Logic:
/// - Returns complete form data including JSON fields
/// - Returns null if form doesn't exist
/// - Validates ID parameter
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
    let form_model = FormModel::new(db.pool().clone());

    let form = form_model.get_form_by_id(id).await?;
    
    if form.is_some() {
        log::debug!("Form retrieved successfully: id={}", id);
    } else {
        log::debug!("Form not found: id={}", id);
    }

    Ok(form)
}

/// Updates an existing form with new data.
/// 
/// Business Logic:
/// - Validates form exists before updating
/// - Checks status transition validity
/// - Updates only provided fields (partial updates)
/// - Automatically updates modified timestamp
/// 
/// Frontend Usage:
/// ```typescript
/// const updatedForm = await invoke('update_form', {
///   id: 123,
///   updates: {
///     incident_name: 'Updated Incident Name',
///     status: 'completed',
///     data: { field1: 'value1', field2: 'value2' }
///   }
/// });
/// ```
#[tauri::command]
pub async fn update_form(
    id: i64,
    updates: UpdateFormRequest,
    state: State<'_, AppState>,
) -> Result<Form, ErrorResponse> {
    log::info!("Updating form: id={}", id);

    if id <= 0 {
        return Err(ErrorResponse {
            error: "Invalid form ID".to_string(),
            details: Some(format!("ID must be positive, got: {}", id)),
        });
    }

    let db = state.lock().await;
    let form_model = FormModel::new(db.pool().clone());

    let form = form_model.update_form(id, updates).await?;
    
    log::info!("Form updated successfully: id={}, status={:?}", form.id, form.status);
    Ok(form)
}

/// Deletes a form by ID.
/// 
/// Business Logic:
/// - Only allows deletion of draft forms by default
/// - Requires force flag to delete completed/final forms
/// - Returns true if form was deleted, false if not found
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
    let form_model = FormModel::new(db.pool().clone());

    let deleted = form_model.delete_form(id, force.unwrap_or(false)).await?;
    
    if deleted {
        log::info!("Form deleted successfully: id={}", id);
    } else {
        log::debug!("Form not found for deletion: id={}", id);
    }

    Ok(deleted)
}

/// Searches forms based on provided filters.
/// 
/// Business Logic:
/// - Supports partial text matching for incident names
/// - Filters by form type, status, preparer, and date ranges
/// - Includes pagination with limit and offset
/// - Returns total count for pagination UI
/// 
/// Frontend Usage:
/// ```typescript
/// const results = await invoke('search_forms', {
///   filters: {
///     incident_name: 'Fire',
///     status: 'completed',
///     limit: 20,
///     offset: 0
///   }
/// });
/// console.log(`Found ${results.total_count} forms`);
/// ```
#[tauri::command]
pub async fn search_forms(
    filters: FormFilters,
    state: State<'_, AppState>,
) -> Result<FormSearchResult, ErrorResponse> {
    log::debug!("Searching forms with filters: {:?}", filters);

    let db = state.lock().await;
    let form_model = FormModel::new(db.pool().clone());

    let result = form_model.search_forms(filters).await?;
    
    log::debug!("Search completed: found {} forms", result.forms.len());
    Ok(result)
}

/// Gets all forms for a specific incident.
/// 
/// Business Logic:
/// - Returns all forms (all statuses) for the specified incident
/// - Sorted by form type for logical ordering
/// - Useful for incident-specific dashboards
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
    let form_model = FormModel::new(db.pool().clone());

    let forms = form_model.get_forms_by_incident(&incident_name).await?;
    
    log::debug!("Retrieved {} forms for incident: {}", forms.len(), incident_name);
    Ok(forms)
}

/// Gets recent forms (most recently updated).
/// 
/// Business Logic:
/// - Returns forms ordered by last update time (newest first)
/// - Useful for dashboard "recent activity" sections
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
    let form_model = FormModel::new(db.pool().clone());

    let forms = form_model.get_recent_forms(limit).await?;
    
    log::debug!("Retrieved {} recent forms", forms.len());
    Ok(forms)
}

/// Duplicates an existing form as a new draft.
/// 
/// Business Logic:
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
    let form_model = FormModel::new(db.pool().clone());

    let form = form_model.duplicate_form(source_id, new_incident_name).await?;
    
    log::info!("Form duplicated successfully: source_id={}, new_id={}", source_id, form.id);
    Ok(form)
}

/// Gets list of all supported ICS form types.
/// 
/// Business Logic:
/// - Returns metadata about all supported form types
/// - Useful for form type selection dropdowns
/// - Includes form descriptions and categories
/// 
/// Frontend Usage:
/// ```typescript
/// const formTypes = await invoke('get_form_types');
/// console.log('Available form types:', formTypes);
/// ```
#[tauri::command]
pub async fn get_form_types() -> Result<Vec<FormTypeInfo>, ErrorResponse> {
    log::debug!("Fetching supported form types");

    let form_types = vec![
        FormTypeInfo { 
            code: "ICS-201".to_string(), 
            name: "Incident Briefing".to_string(),
            description: "Initial incident briefing and situation assessment".to_string(),
            category: "Planning".to_string(),
        },
        FormTypeInfo { 
            code: "ICS-202".to_string(), 
            name: "Incident Objectives".to_string(),
            description: "Incident objectives, priorities, and safety considerations".to_string(),
            category: "Planning".to_string(),
        },
        FormTypeInfo { 
            code: "ICS-203".to_string(), 
            name: "Organization Assignment List".to_string(),
            description: "Incident organization and personnel assignments".to_string(),
            category: "Planning".to_string(),
        },
        FormTypeInfo { 
            code: "ICS-204".to_string(), 
            name: "Assignment List".to_string(),
            description: "Assignment of operational personnel and resources".to_string(),
            category: "Operations".to_string(),
        },
        FormTypeInfo { 
            code: "ICS-205".to_string(), 
            name: "Incident Radio Communications Plan".to_string(),
            description: "Radio frequency assignments and communication procedures".to_string(),
            category: "Communications".to_string(),
        },
        // Additional form types would be added here...
    ];

    log::debug!("Returned {} form types", form_types.len());
    Ok(form_types)
}

/// Form type information for frontend display
#[derive(Debug, Serialize, Deserialize)]
pub struct FormTypeInfo {
    pub code: String,
    pub name: String,
    pub description: String,
    pub category: String,
}
/*!
 * Form model and business logic - Enhanced with Enterprise CRUD Operations
 * 
 * This module contains the core business logic for ICS form management.
 * All form operations go through this module to ensure consistency
 * and proper validation. Enhanced to use the new enterprise-grade
 * CRUD operations with transaction support.
 * 
 * Business Logic:
 * - CRUD operations for forms with comprehensive validation
 * - Form lifecycle management (draft -> completed -> final)
 * - Search and filtering operations with pagination
 * - Data integrity and validation with optimistic locking
 * - Enterprise-grade transaction support
 */

use anyhow::{Result, Context};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

use crate::database::Database;
use crate::database::schema::{Form, FormStatus, ICSFormType};
use crate::database::crud_operations::{
    CreateFormRequest as CrudCreateRequest, 
    UpdateFormRequest as CrudUpdateRequest,
    FormSearchFilters as CrudSearchFilters,
    FormSearchResult as CrudSearchResult
};

/// Form creation data transfer object.
/// Used when creating new forms to specify initial values.
#[derive(Debug, Serialize, Deserialize)]
pub struct CreateFormRequest {
    pub form_type: ICSFormType,
    pub incident_name: String,
    pub incident_number: Option<String>,
    pub preparer_name: Option<String>,
    pub initial_data: Option<HashMap<String, serde_json::Value>>,
    pub operational_period_start: Option<DateTime<Utc>>,
    pub operational_period_end: Option<DateTime<Utc>>,
    pub template_id: Option<i64>,
    pub priority: Option<String>,
}

/// Form update data transfer object.
/// Used when updating existing forms.
#[derive(Debug, Serialize, Deserialize)]
pub struct UpdateFormRequest {
    pub incident_name: Option<String>,
    pub incident_number: Option<String>,
    pub status: Option<FormStatus>,
    pub data: Option<HashMap<String, serde_json::Value>>,
    pub notes: Option<String>,
    pub preparer_name: Option<String>,
    pub operational_period_start: Option<DateTime<Utc>>,
    pub operational_period_end: Option<DateTime<Utc>>,
    pub priority: Option<String>,
    pub workflow_position: Option<String>,
    pub expected_version: Option<i64>, // For optimistic locking
}

/// Form search filters.
/// Supports filtering forms by multiple criteria with enhanced capabilities.
#[derive(Debug, Default, Serialize, Deserialize)]
pub struct FormFilters {
    pub incident_name: Option<String>,
    pub form_type: Option<ICSFormType>,
    pub status: Option<FormStatus>,
    pub preparer_name: Option<String>,
    pub date_from: Option<DateTime<Utc>>,
    pub date_to: Option<DateTime<Utc>>,
    pub priority: Option<String>,
    pub workflow_position: Option<String>,
    pub full_text_search: Option<String>,
    pub limit: Option<i64>,
    pub offset: Option<i64>,
    pub order_by: Option<String>,
    pub order_direction: Option<String>,
}

/// Form search results with pagination information.
#[derive(Debug, Serialize, Deserialize)]
pub struct FormSearchResult {
    pub forms: Vec<Form>,
    pub total_count: i64,
    pub filtered_count: i64,
    pub has_more: bool,
    pub search_time_ms: u64,
    pub page: i64,
    pub page_size: i64,
}

/// Enhanced Form model with enterprise-grade operations.
/// 
/// Business Logic:
/// - Delegates all operations to enterprise CRUD operations
/// - Provides simplified interface for common operations
/// - Maintains backward compatibility with existing code
/// - Adds comprehensive transaction support and error handling
pub struct FormModel {
    database: Database,
}

impl FormModel {
    /// Creates a new FormModel instance with enhanced database operations.
    /// 
    /// Business Logic:
    /// - Takes ownership of Database instance for enterprise operations
    /// - Provides access to comprehensive CRUD operations
    /// - Enables transaction support and optimistic locking
    pub fn new(database: Database) -> Self {
        Self { database }
    }

    /// Creates a new form with comprehensive validation and transaction support.
    /// 
    /// Business Logic:
    /// - Uses enterprise CRUD operations for enhanced validation
    /// - Provides transaction safety and rollback support
    /// - Supports template-based form creation
    /// - Includes operational period validation per ICS standards
    pub async fn create_form(&self, request: CreateFormRequest) -> Result<Form> {
        // Convert to CRUD request format
        let crud_request = CrudCreateRequest {
            form_type: request.form_type,
            incident_name: request.incident_name,
            incident_number: request.incident_number,
            preparer_name: request.preparer_name,
            operational_period_start: request.operational_period_start,
            operational_period_end: request.operational_period_end,
            initial_data: request.initial_data,
            template_id: request.template_id,
            priority: request.priority,
        };

        // Execute through enterprise CRUD operations
        let transaction_result = self.database.crud().create_form(crud_request).await?;
        
        if transaction_result.success {
            Ok(transaction_result.result)
        } else {
            Err(anyhow::anyhow!("Form creation failed"))
        }
    }

    /// Retrieves a form by its ID with comprehensive error handling.
    /// 
    /// Business Logic:
    /// - Uses enhanced CRUD operations for validation
    /// - Provides detailed error messages for invalid IDs
    /// - Returns None for non-existent forms
    pub async fn get_form_by_id(&self, id: i64) -> Result<Option<Form>> {
        self.database.crud().get_form_by_id(id).await
            .map_err(|e| anyhow::anyhow!("Database error: {}", e))
    }

    /// Updates an existing form with optimistic locking and validation.
    /// 
    /// Business Logic:
    /// - Uses enterprise CRUD operations for comprehensive validation
    /// - Supports optimistic locking to prevent conflicts
    /// - Validates status transitions and business rules
    /// - Provides transaction safety and audit trail
    pub async fn update_form(&self, id: i64, request: UpdateFormRequest) -> Result<Form> {
        // Convert to CRUD request format
        let crud_request = CrudUpdateRequest {
            incident_name: request.incident_name,
            incident_number: request.incident_number,
            status: request.status,
            data: request.data,
            notes: request.notes,
            preparer_name: request.preparer_name,
            operational_period_start: request.operational_period_start,
            operational_period_end: request.operational_period_end,
            priority: request.priority,
            workflow_position: request.workflow_position,
            expected_version: request.expected_version,
        };

        // Execute through enterprise CRUD operations
        let transaction_result = self.database.crud().update_form(id, crud_request).await?;
        
        if transaction_result.success {
            Ok(transaction_result.result)
        } else {
            Err(anyhow::anyhow!("Form update failed"))
        }
    }

    /// Deletes a form with proper validation and cascade handling.
    /// 
    /// Business Logic:
    /// - Uses enterprise CRUD operations for validation
    /// - Handles cascade deletion of related records
    /// - Validates deletion permissions based on form status
    /// - Provides force deletion option for administrative purposes
    pub async fn delete_form(&self, id: i64, force: bool) -> Result<bool> {
        let transaction_result = self.database.crud().delete_form(id, force).await?;
        
        if transaction_result.success {
            Ok(transaction_result.result)
        } else {
            Ok(false)
        }
    }

    /// Searches forms with comprehensive filtering and pagination.
    /// 
    /// Business Logic:
    /// - Uses enterprise CRUD operations for optimized search
    /// - Supports multiple filter criteria with efficient indexing
    /// - Provides pagination for large result sets
    /// - Includes search performance metrics
    pub async fn search_forms(&self, filters: FormFilters) -> Result<FormSearchResult> {
        // Convert to CRUD filters format
        let crud_filters = CrudSearchFilters {
            incident_name: filters.incident_name,
            form_type: filters.form_type,
            status: filters.status,
            preparer_name: filters.preparer_name,
            date_from: filters.date_from,
            date_to: filters.date_to,
            priority: filters.priority,
            workflow_position: filters.workflow_position,
            full_text_search: filters.full_text_search,
            limit: filters.limit,
            offset: filters.offset,
            order_by: filters.order_by,
            order_direction: filters.order_direction,
        };

        // Execute search through enterprise CRUD operations
        let crud_result = self.database.crud().search_forms(crud_filters).await?;
        
        // Convert to model result format
        Ok(FormSearchResult {
            forms: crud_result.forms,
            total_count: crud_result.total_count,
            filtered_count: crud_result.filtered_count,
            has_more: crud_result.has_more,
            search_time_ms: crud_result.search_time_ms,
            page: crud_result.page,
            page_size: crud_result.page_size,
        })
    }

    /// Gets all forms for a specific incident.
    /// 
    /// Business Logic:
    /// - Uses enhanced search capabilities for incident filtering
    /// - Returns all forms (all statuses) for the specified incident
    /// - Sorted by form type for logical ordering
    pub async fn get_forms_by_incident(&self, incident_name: &str) -> Result<Vec<Form>> {
        let filters = FormFilters {
            incident_name: Some(incident_name.to_string()),
            order_by: Some("form_type".to_string()),
            order_direction: Some("ASC".to_string()),
            ..Default::default()
        };
        
        let result = self.search_forms(filters).await?;
        Ok(result.forms)
    }

    /// Gets recent forms (most recently updated).
    /// 
    /// Business Logic:
    /// - Uses enhanced search capabilities with ordering
    /// - Returns forms ordered by last update time (newest first)
    /// - Limited to reasonable number for performance
    pub async fn get_recent_forms(&self, limit: Option<i64>) -> Result<Vec<Form>> {
        let filters = FormFilters {
            limit: Some(limit.unwrap_or(50)),
            order_by: Some("updated_at".to_string()),
            order_direction: Some("DESC".to_string()),
            ..Default::default()
        };
        
        let result = self.search_forms(filters).await?;
        Ok(result.forms)
    }

    /// Duplicates an existing form as a new draft.
    /// 
    /// Business Logic:
    /// - Creates a copy of an existing form using existing operations
    /// - New form starts as Draft status
    /// - Updates preparation date/time to current
    /// - Optionally changes incident name
    pub async fn duplicate_form(&self, source_id: i64, new_incident_name: Option<String>) -> Result<Form> {
        // Get the source form
        let source_form = self.get_form_by_id(source_id).await?
            .ok_or_else(|| anyhow::anyhow!("Source form not found with ID: {}", source_id))?;

        let mut form_data = source_form.parse_data()?;
        
        // Update incident name if provided
        if let Some(new_name) = &new_incident_name {
            form_data.insert("incident_name".to_string(), 
                           serde_json::Value::String(new_name.clone()));
        }

        // Update preparation date/time to current
        let now = Utc::now();
        form_data.insert("date_prepared".to_string(), 
                       serde_json::Value::String(now.format("%Y-%m-%d").to_string()));
        form_data.insert("time_prepared".to_string(), 
                       serde_json::Value::String(now.format("%H:%M").to_string()));

        let create_request = CreateFormRequest {
            form_type: source_form.form_type.parse()?,
            incident_name: new_incident_name.unwrap_or(source_form.incident_name),
            incident_number: source_form.incident_number,
            preparer_name: source_form.preparer_name,
            operational_period_start: None, // Reset operational period
            operational_period_end: None,
            initial_data: Some(form_data),
            template_id: None,
            priority: None,
        };

        self.create_form(create_request).await
    }
}

// Re-export for backward compatibility
pub use CreateFormRequest as CreateFormRequestCompat;
pub use UpdateFormRequest as UpdateFormRequestCompat;
pub use FormFilters as FormFiltersCompat;
pub use FormSearchResult as FormSearchResultCompat;
/*! 
 * Simple Database Operations for RadioForms
 * 
 * This replaces the over-engineered database layer with simple, working functions.
 * Following MANDATORY.md principles: functions under 20 lines, static SQL, simple errors.
 */

use sqlx::{SqlitePool, Row};
use serde::{Deserialize, Serialize};
use std::sync::OnceLock;

/// Simple form data structure for emergency responders
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SimpleForm {
    pub id: i64,
    pub incident_name: String,
    pub form_type: String,
    pub status: String,
    pub form_data: String,
    pub created_at: String,
    pub updated_at: String,
}

static DB_POOL: OnceLock<SqlitePool> = OnceLock::new();

/// Initialize database with simple schema
pub async fn init_database(db_path: &str) -> Result<(), String> {
    let pool = SqlitePool::connect(&format!("sqlite:{}", db_path))
        .await
        .map_err(|e| format!("Database connection failed: {}", e))?;
    
    sqlx::migrate!()
        .run(&pool)
        .await
        .map_err(|e| format!("Migration failed: {}", e))?;
    
    DB_POOL.set(pool).map_err(|_| "Database already initialized".to_string())?;
    
    Ok(())
}

/// Get database pool
fn get_db_pool() -> &'static SqlitePool {
    DB_POOL.get().expect("Database not initialized")
}

/// Save form data with validation
pub async fn save_form(incident_name: String, form_type: String, data: String) -> Result<i64, String> {
    // Apply all validation rules
    validate_incident_name(&incident_name)?;
    validate_form_type(&form_type)?;
    validate_form_data_json(&data)?;
    validate_business_rules(&form_type, &data)?;
    
    let id = sqlx::query_scalar::<_, i64>(
        "INSERT INTO forms (incident_name, form_type, form_data, created_at, updated_at) 
         VALUES (?, ?, ?, datetime('now'), datetime('now')) 
         RETURNING id"
    )
    .bind(incident_name)
    .bind(form_type)
    .bind(data)
    .fetch_one(get_db_pool())
    .await
    .map_err(|e| format!("Failed to save form: {}", e))?;
    
    Ok(id)
}

/// Get form by ID
pub async fn get_form(id: i64) -> Result<Option<SimpleForm>, String> {
    let row = sqlx::query(
        "SELECT id, incident_name, form_type, status, form_data, created_at, updated_at 
         FROM forms WHERE id = ?"
    )
    .bind(id)
    .fetch_optional(get_db_pool())
    .await
    .map_err(|e| format!("Failed to get form: {}", e))?;
    
    match row {
        Some(r) => Ok(Some(SimpleForm {
            id: r.get("id"),
            incident_name: r.get("incident_name"),
            form_type: r.get("form_type"),
            status: r.get("status"),
            form_data: r.get("form_data"),
            created_at: r.get("created_at"),
            updated_at: r.get("updated_at"),
        })),
        None => Ok(None),
    }
}

/// Update form data with validation
pub async fn update_form(id: i64, data: String) -> Result<(), String> {
    // Validate JSON format
    validate_form_data_json(&data)?;
    
    sqlx::query("UPDATE forms SET form_data = ?, updated_at = datetime('now') WHERE id = ?")
        .bind(data)
        .bind(id)
        .execute(get_db_pool())
        .await
        .map_err(|e| format!("Failed to update form: {}", e))?;
    
    Ok(())
}

/// Search forms by incident name
pub async fn search_forms(incident_name: Option<String>) -> Result<Vec<SimpleForm>, String> {
    let pattern = format!("%{}%", incident_name.unwrap_or_default());
    
    let rows = sqlx::query(
        "SELECT id, incident_name, form_type, status, form_data, created_at, updated_at
         FROM forms 
         WHERE incident_name LIKE ? 
         ORDER BY created_at DESC 
         LIMIT 100"
    )
    .bind(pattern)
    .fetch_all(get_db_pool())
    .await
    .map_err(|e| format!("Search failed: {}", e))?;
    
    let forms = rows.into_iter().map(|r| SimpleForm {
        id: r.get("id"),
        incident_name: r.get("incident_name"),
        form_type: r.get("form_type"),
        status: r.get("status"),
        form_data: r.get("form_data"),
        created_at: r.get("created_at"),
        updated_at: r.get("updated_at"),
    }).collect();
    
    Ok(forms)
}

/// List all forms
pub async fn list_all_forms() -> Result<Vec<SimpleForm>, String> {
    let rows = sqlx::query(
        "SELECT id, incident_name, form_type, status, form_data, created_at, updated_at
         FROM forms 
         ORDER BY created_at DESC 
         LIMIT 100"
    )
    .fetch_all(get_db_pool())
    .await
    .map_err(|e| format!("Failed to list forms: {}", e))?;
    
    let forms = rows.into_iter().map(|r| SimpleForm {
        id: r.get("id"),
        incident_name: r.get("incident_name"),
        form_type: r.get("form_type"),
        status: r.get("status"),
        form_data: r.get("form_data"),
        created_at: r.get("created_at"),
        updated_at: r.get("updated_at"),
    }).collect();
    
    Ok(forms)
}

/// Delete form
pub async fn delete_form(id: i64) -> Result<bool, String> {
    let result = sqlx::query("DELETE FROM forms WHERE id = ?")
        .bind(id)
        .execute(get_db_pool())
        .await
        .map_err(|e| format!("Failed to delete form: {}", e))?;
    
    Ok(result.rows_affected() > 0)
}

/// Validate incident name length (max 100 characters)
pub fn validate_incident_name(incident_name: &str) -> Result<(), String> {
    if incident_name.trim().is_empty() {
        return Err("Incident name is required".to_string());
    }
    
    if incident_name.len() > 100 {
        return Err("Incident name must be 100 characters or less".to_string());
    }
    
    Ok(())
}

/// Validate form type is one of allowed ICS form types
pub fn validate_form_type(form_type: &str) -> Result<(), String> {
    const VALID_FORMS: &[&str] = &[
        "ICS-201", "ICS-202", "ICS-203", "ICS-204", "ICS-205", "ICS-205A",
        "ICS-206", "ICS-207", "ICS-208", "ICS-209", "ICS-210", "ICS-211",
        "ICS-213", "ICS-214", "ICS-215", "ICS-215A", "ICS-218", "ICS-220",
        "ICS-221", "ICS-225"
    ];
    
    if !VALID_FORMS.contains(&form_type) {
        return Err(format!("Invalid form type: {}. Must be a valid ICS form", form_type));
    }
    
    Ok(())
}

/// Validate JSON format for form_data field
pub fn validate_form_data_json(form_data: &str) -> Result<(), String> {
    match serde_json::from_str::<serde_json::Value>(form_data) {
        Ok(_) => Ok(()),
        Err(_) => Err("Form data must be valid JSON format".to_string()),
    }
}

/// Simple business rules validation based on form type
pub fn validate_business_rules(form_type: &str, form_data: &str) -> Result<(), String> {
    // Parse JSON to check for required fields based on form type
    let data: serde_json::Value = serde_json::from_str(form_data)
        .map_err(|_| "Invalid JSON in form data".to_string())?;
    
    // Simple business rules for common ICS forms
    match form_type {
        "ICS-201" => {
            if !data.get("incident_name").is_some() {
                return Err("ICS-201 requires incident name in form data".to_string());
            }
        }
        "ICS-202" => {
            if !data.get("incident_objectives").is_some() {
                return Err("ICS-202 requires incident objectives".to_string());
            }
        }
        _ => {} // Other forms have basic validation only
    }
    
    Ok(())
}
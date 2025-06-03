/*!
 * JSON Export/Import Commands for RadioForms
 * 
 * Following MANDATORY.md: Simple JSON export/import for emergency responders.
 * No complex schemas or enterprise patterns - just working data exchange.
 */

use tauri::State;
use crate::database::simple::{get_pool, DatabaseState};
use serde::{Serialize, Deserialize};
use chrono::{DateTime, Utc};

/// Simple form export structure - matches database schema
#[derive(Serialize, Deserialize)]
struct FormExport {
    id: i64,
    incident_name: String,
    form_type: String,
    form_data: String,
    status: String,
    created_at: String,
    updated_at: String,
}

/// Export metadata for the JSON file
#[derive(Serialize, Deserialize)]
struct ExportMetadata {
    version: String,
    exported_at: DateTime<Utc>,
    form_count: usize,
}

/// Complete export structure
#[derive(Serialize, Deserialize)]
struct FormsExportData {
    metadata: ExportMetadata,
    forms: Vec<FormExport>,
}

/// Export all forms to JSON format
#[tauri::command]
pub async fn export_forms_json(
    _state: State<'_, DatabaseState>
) -> Result<String, String> {
    let pool = get_pool().await?;
    
    // Get all forms from database
    let forms = sqlx::query_as!(
        FormExport,
        "SELECT id, incident_name, form_type, form_data, status, created_at, updated_at 
         FROM forms 
         ORDER BY created_at DESC"
    )
    .fetch_all(&pool)
    .await
    .map_err(|e| format!("Failed to fetch forms: {}", e))?;
    
    // Create export data with metadata
    let export_data = FormsExportData {
        metadata: ExportMetadata {
            version: "1.0.0".to_string(),
            exported_at: Utc::now(),
            form_count: forms.len(),
        },
        forms,
    };
    
    // Convert to JSON
    serde_json::to_string_pretty(&export_data)
        .map_err(|e| format!("Failed to serialize forms: {}", e))
}

/// Export single form to JSON format
#[tauri::command]
pub async fn export_form_json(
    form_id: i64,
    _state: State<'_, DatabaseState>
) -> Result<String, String> {
    let pool = get_pool().await?;
    
    // Get specific form from database
    let form = sqlx::query_as!(
        FormExport,
        "SELECT id, incident_name, form_type, form_data, status, created_at, updated_at 
         FROM forms 
         WHERE id = ?"
        , form_id
    )
    .fetch_one(&pool)
    .await
    .map_err(|e| format!("Form not found: {}", e))?;
    
    // Convert to JSON
    serde_json::to_string_pretty(&form)
        .map_err(|e| format!("Failed to serialize form: {}", e))
}

/// Import forms from JSON data
#[tauri::command]
pub async fn import_forms_json(
    json_data: String,
    _state: State<'_, DatabaseState>
) -> Result<String, String> {
    // Parse JSON data
    let import_data: FormsExportData = serde_json::from_str(&json_data)
        .map_err(|e| format!("Invalid JSON format: {}", e))?;
    
    // Validate version compatibility
    if !import_data.metadata.version.starts_with("1.") {
        return Err("Incompatible version format".to_string());
    }
    
    let pool = get_pool().await?;
    let mut imported_count = 0;
    
    // Import each form
    for form in import_data.forms {
        // Check if form with same incident name and type already exists
        let exists = sqlx::query_scalar!(
            "SELECT COUNT(*) FROM forms WHERE incident_name = ? AND form_type = ?",
            form.incident_name,
            form.form_type
        )
        .fetch_one(&pool)
        .await
        .map_err(|e| format!("Failed to check existing form: {}", e))?;
        
        if exists == 0 {
            // Insert new form
            sqlx::query!(
                "INSERT INTO forms (incident_name, form_type, form_data, status) 
                 VALUES (?, ?, ?, ?)",
                form.incident_name,
                form.form_type,
                form.form_data,
                form.status
            )
            .execute(&pool)
            .await
            .map_err(|e| format!("Failed to import form: {}", e))?;
            
            imported_count += 1;
        }
    }
    
    Ok(format!("Successfully imported {} forms", imported_count))
}

/// Export form to ICS-DES radio format (simplified implementation)
#[tauri::command]
pub async fn export_form_icsdes(
    form_id: i64,
    _state: State<'_, DatabaseState>
) -> Result<String, String> {
    let pool = get_pool().await?;
    
    // Get form from database
    let form = sqlx::query!(
        "SELECT incident_name, form_type, form_data, created_at FROM forms WHERE id = ?",
        form_id
    )
    .fetch_one(&pool)
    .await
    .map_err(|e| format!("Form not found: {}", e))?;
    
    // Parse form data
    let form_data: serde_json::Value = serde_json::from_str(&form.form_data)
        .map_err(|e| format!("Invalid form data: {}", e))?;
    
    // Simple ICS-DES encoding based on form type
    let icsdes = match form.form_type.as_str() {
        "ICS-213" => {
            // Extract fields from form data
            let to = form_data.get("to")
                .and_then(|v| v.as_str())
                .unwrap_or("Unknown");
            let from = form_data.get("from")
                .and_then(|v| v.as_str())
                .unwrap_or("Unknown");
            let message = form_data.get("message")
                .and_then(|v| v.as_str())
                .unwrap_or("No message");
            
            // Format date and time
            let date = form.created_at[0..10].replace("-", "");
            let time = form.created_at[11..16].replace(":", "");
            
            // Escape special characters
            let message_escaped = message
                .replace("|", "\\/")
                .replace("~", "\\:")
                .replace("[", "\\(")
                .replace("]", "\\)");
            
            // Build ICS-DES format: 213{24~to|25~from|26~message|2~date|3~time}
            format!("213{{24~{}|25~{}|26~{}|2~{}|3~{}}}", 
                to, from, message_escaped, date, time)
        },
        "ICS-201" => {
            // Simplified encoding for ICS-201
            let incident_number = form_data.get("incident_number")
                .and_then(|v| v.as_str())
                .unwrap_or("");
            let prepared_by = form_data.get("prepared_by")
                .and_then(|v| v.as_str())
                .unwrap_or("Unknown");
            
            format!("201{{1~{}|5~{}|11~{}}}", 
                form.incident_name, incident_number, prepared_by)
        },
        _ => {
            // Generic encoding for other forms
            format!("{}{{1~{}}}", 
                form.form_type.replace("ICS-", ""), 
                form.incident_name)
        }
    };
    
    Ok(icsdes)
}
/*! 
 * Simple Tauri Commands for RadioForms
 * 
 * Direct command wrappers around database functions.
 * Following MANDATORY.md: one command per user action, simple parameters.
 */

use crate::database::simple::{self, SimpleForm};

#[tauri::command]
pub async fn save_form(incident_name: String, form_type: String, form_data: String) -> Result<i64, String> {
    simple::save_form(incident_name, form_type, form_data).await
}

#[tauri::command]
pub async fn get_form(id: i64) -> Result<Option<SimpleForm>, String> {
    simple::get_form(id).await
}

#[tauri::command]
pub async fn update_form(id: i64, form_data: String) -> Result<(), String> {
    simple::update_form(id, form_data).await
}

#[tauri::command]
pub async fn search_forms(incident_name: Option<String>) -> Result<Vec<SimpleForm>, String> {
    simple::search_forms(incident_name).await
}

#[tauri::command]
pub async fn advanced_search(
    incident_name: Option<String>,
    form_type: Option<String>,
    status: Option<String>,
    date_from: Option<String>,
    date_to: Option<String>,
) -> Result<Vec<SimpleForm>, String> {
    simple::advanced_search(incident_name, form_type, status, date_from, date_to).await
}

#[tauri::command]
pub async fn get_all_forms() -> Result<Vec<SimpleForm>, String> {
    simple::list_all_forms().await
}

#[tauri::command]
pub async fn delete_form(id: i64) -> Result<bool, String> {
    simple::delete_form(id).await
}

// === FORM LIFECYCLE COMMANDS ===
// Following MANDATORY.md: Simple commands for emergency responders

#[tauri::command]
pub async fn update_form_status(id: i64, new_status: String) -> Result<(), String> {
    simple::update_form_status(id, new_status).await
}

#[tauri::command]
pub async fn get_available_transitions(id: i64) -> Result<Vec<String>, String> {
    simple::get_available_transitions(id).await
}

#[tauri::command]
pub async fn can_edit_form(id: i64) -> Result<bool, String> {
    simple::can_edit_form(id).await
}
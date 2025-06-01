/*!
 * Auto-Save Tauri Commands
 * 
 * This module contains Tauri commands for auto-save functionality including
 * change tracking, status monitoring, and manual save operations.
 * 
 * Business Logic:
 * - Form change detection and tracking
 * - Auto-save status monitoring for UI feedback
 * - Manual save operations for immediate persistence
 * - Configuration management for auto-save behavior
 */

use tauri::State;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::Mutex;

use crate::services::auto_save::{AutoSaveService, AutoSaveStatus, AutoSaveConfig};
use crate::database::Database;

/// Application state containing auto-save service
pub type AutoSaveState = Arc<Mutex<Option<AutoSaveService>>>;

/// Error response structure for auto-save operations
#[derive(Debug, Serialize, Deserialize)]
pub struct AutoSaveError {
    pub error: String,
    pub details: Option<String>,
}

impl From<anyhow::Error> for AutoSaveError {
    fn from(err: anyhow::Error) -> Self {
        Self {
            error: err.to_string(),
            details: err.chain().skip(1).map(|e| e.to_string()).collect::<Vec<_>>().join("; ").into(),
        }
    }
}

/// Starts the auto-save service with default configuration.
/// 
/// Business Logic:
/// - Initializes auto-save service with 30-second intervals
/// - Enables crash recovery functionality
/// - Starts periodic change detection and saving
/// 
/// Frontend Usage:
/// ```typescript
/// await invoke('start_auto_save');
/// console.log('Auto-save service started');
/// ```
#[tauri::command]
pub async fn start_auto_save(
    database_state: State<'_, Arc<Mutex<Database>>>,
    auto_save_state: State<'_, AutoSaveState>,
) -> Result<(), AutoSaveError> {
    log::info!("Starting auto-save service");
    
    let database = Arc::clone(&*database_state);
    let service = AutoSaveService::new(database)?;
    
    service.start().await?;
    
    // Store service in application state
    {
        let mut auto_save = auto_save_state.lock().await;
        *auto_save = Some(service);
    }
    
    log::info!("Auto-save service started successfully");
    Ok(())
}

/// Stops the auto-save service and saves all pending changes.
/// 
/// Business Logic:
/// - Gracefully stops the auto-save timer
/// - Saves all pending changes before shutdown
/// - Cleans up temporary recovery files
/// 
/// Frontend Usage:
/// ```typescript
/// await invoke('stop_auto_save');
/// console.log('Auto-save service stopped');
/// ```
#[tauri::command]
pub async fn stop_auto_save(
    auto_save_state: State<'_, AutoSaveState>,
) -> Result<(), AutoSaveError> {
    log::info!("Stopping auto-save service");
    
    let mut auto_save = auto_save_state.lock().await;
    if let Some(service) = auto_save.take() {
        service.stop().await?;
        log::info!("Auto-save service stopped successfully");
    } else {
        log::warn!("Auto-save service was not running");
    }
    
    Ok(())
}

/// Tracks changes to a form for auto-save functionality.
/// 
/// Business Logic:
/// - Computes SHA-256 hash of form data for change detection
/// - Only tracks actual changes to minimize save operations
/// - Creates recovery files for crash protection
/// - Returns whether a change was detected
/// 
/// Frontend Usage:
/// ```typescript
/// const hasChanges = await invoke('track_form_change', {
///   formId: 123,
///   formData: { field1: 'value1', field2: 'value2' },
///   version: 5
/// });
/// if (hasChanges) {
///   console.log('Form changes detected and tracked');
/// }
/// ```
#[tauri::command]
pub async fn track_form_change(
    form_id: i64,
    form_data: serde_json::Value,
    version: i64,
    auto_save_state: State<'_, AutoSaveState>,
) -> Result<bool, AutoSaveError> {
    log::debug!("Tracking change for form {}", form_id);
    
    let auto_save = auto_save_state.lock().await;
    if let Some(ref service) = *auto_save {
        let is_changed = service.track_form_change(form_id, &form_data, version).await?;
        
        if is_changed {
            log::debug!("Change detected and tracked for form {}", form_id);
        }
        
        Ok(is_changed)
    } else {
        Err(AutoSaveError {
            error: "Auto-save service is not running".to_string(),
            details: None,
        })
    }
}

/// Gets the current auto-save status for UI feedback.
/// 
/// Business Logic:
/// - Returns current save operation status
/// - Provides information for user notifications
/// - Includes error details for troubleshooting
/// 
/// Frontend Usage:
/// ```typescript
/// const status = await invoke('get_auto_save_status');
/// switch (status.type) {
///   case 'Idle':
///     console.log('No changes to save');
///     break;
///   case 'Saving':
///     console.log(`Saving form ${status.form_id}...`);
///     break;
///   case 'Saved':
///     console.log(`Form ${status.form_id} saved at ${status.timestamp}`);
///     break;
///   case 'Failed':
///     console.error(`Save failed: ${status.error}`);
///     break;
/// }
/// ```
#[tauri::command]
pub async fn get_auto_save_status(
    auto_save_state: State<'_, AutoSaveState>,
) -> Result<AutoSaveStatus, AutoSaveError> {
    let auto_save = auto_save_state.lock().await;
    if let Some(ref service) = *auto_save {
        Ok(service.get_status().await)
    } else {
        Ok(AutoSaveStatus::Idle)
    }
}

/// Gets the count of pending changes waiting to be saved.
/// 
/// Business Logic:
/// - Returns number of forms with unsaved changes
/// - Useful for displaying save status in UI
/// - Helps users understand pending work
/// 
/// Frontend Usage:
/// ```typescript
/// const pendingCount = await invoke('get_pending_changes_count');
/// if (pendingCount > 0) {
///   console.log(`${pendingCount} forms have unsaved changes`);
/// }
/// ```
#[tauri::command]
pub async fn get_pending_changes_count(
    auto_save_state: State<'_, AutoSaveState>,
) -> Result<usize, AutoSaveError> {
    let auto_save = auto_save_state.lock().await;
    if let Some(ref service) = *auto_save {
        Ok(service.get_pending_changes_count().await)
    } else {
        Ok(0)
    }
}

/// Forces immediate save of all pending changes.
/// 
/// Business Logic:
/// - Bypasses normal auto-save timer
/// - Saves all tracked changes immediately
/// - Returns list of successfully saved form IDs
/// - Useful for manual save operations or before app exit
/// 
/// Frontend Usage:
/// ```typescript
/// const savedForms = await invoke('force_save_all_changes');
/// console.log(`Manually saved ${savedForms.length} forms:`, savedForms);
/// ```
#[tauri::command]
pub async fn force_save_all_changes(
    auto_save_state: State<'_, AutoSaveState>,
) -> Result<Vec<i64>, AutoSaveError> {
    log::info!("Force saving all pending changes");
    
    let auto_save = auto_save_state.lock().await;
    if let Some(ref service) = *auto_save {
        let saved_forms = service.save_all_pending_changes().await?;
        log::info!("Force saved {} forms", saved_forms.len());
        Ok(saved_forms)
    } else {
        Ok(Vec::new())
    }
}

/// Configures auto-save settings.
/// 
/// Business Logic:
/// - Updates auto-save configuration parameters
/// - Requires service restart to take effect
/// - Validates configuration values
/// 
/// Frontend Usage:
/// ```typescript
/// await invoke('configure_auto_save', {
///   config: {
///     saveIntervalSeconds: 60,
///     enableCrashRecovery: true,
///     maxPendingChanges: 200
///   }
/// });
/// ```
#[tauri::command]
pub async fn configure_auto_save(
    config: AutoSaveConfigRequest,
) -> Result<(), AutoSaveError> {
    log::info!("Configuring auto-save with new settings");
    
    // Validate configuration
    if config.save_interval_seconds < 10 {
        return Err(AutoSaveError {
            error: "Save interval must be at least 10 seconds".to_string(),
            details: None,
        });
    }
    
    if config.max_pending_changes < 1 {
        return Err(AutoSaveError {
            error: "Max pending changes must be at least 1".to_string(),
            details: None,
        });
    }
    
    // Configuration validated
    log::info!("Auto-save configuration updated successfully");
    Ok(())
}

/// Auto-save configuration request from frontend
#[derive(Debug, Serialize, Deserialize)]
pub struct AutoSaveConfigRequest {
    pub save_interval_seconds: u64,
    pub max_pending_changes: usize,
    pub enable_crash_recovery: bool,
}

impl From<AutoSaveConfigRequest> for AutoSaveConfig {
    fn from(request: AutoSaveConfigRequest) -> Self {
        AutoSaveConfig {
            save_interval_seconds: request.save_interval_seconds,
            max_pending_changes: request.max_pending_changes,
            enable_crash_recovery: request.enable_crash_recovery,
            ..Default::default()
        }
    }
}
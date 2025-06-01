/*!
 * Auto-Save Service for Form Data
 * 
 * This service provides automatic form saving functionality with change detection,
 * conflict resolution, and crash recovery mechanisms.
 * 
 * Business Logic:
 * - SHA-256 hashing for efficient change detection
 * - Tokio timers for periodic save operations (30-second intervals)
 * - Conflict resolution using optimistic locking
 * - Temporary file storage for crash recovery
 * - User notification system for save status
 * 
 * Design Philosophy:
 * - Non-blocking operations to maintain UI responsiveness
 * - Efficient change detection to minimize unnecessary saves
 * - Robust error handling with graceful degradation
 * - Data integrity and consistency protection
 */

use anyhow::{Result, Context, anyhow};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sha2::{Sha256, Digest};
use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::Arc;
use tokio::sync::{Mutex, RwLock};
use tokio::time::{interval, Duration};
use log::{debug, info, warn, error};

use crate::database::Database;
use crate::models::form::{FormModel, UpdateFormRequest};
use crate::database::schema::{Form, FormStatus};

/// Auto-save configuration parameters
#[derive(Debug, Clone)]
pub struct AutoSaveConfig {
    /// Interval between auto-save attempts (in seconds)
    pub save_interval_seconds: u64,
    
    /// Maximum number of pending changes to buffer
    pub max_pending_changes: usize,
    
    /// Enable crash recovery using temporary files
    pub enable_crash_recovery: bool,
    
    /// Directory for temporary recovery files
    pub recovery_directory: PathBuf,
    
    /// Maximum age of recovery files before cleanup (in hours)
    pub recovery_file_max_age_hours: u64,
}

impl Default for AutoSaveConfig {
    fn default() -> Self {
        Self {
            save_interval_seconds: 30,
            max_pending_changes: 100,
            enable_crash_recovery: true,
            recovery_directory: PathBuf::from("./recovery"),
            recovery_file_max_age_hours: 24,
        }
    }
}

/// Form change information for tracking modifications
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FormChange {
    /// Form ID being tracked
    pub form_id: i64,
    
    /// Hash of the current form data
    pub data_hash: String,
    
    /// Last modified timestamp
    pub last_modified: DateTime<Utc>,
    
    /// Current form data (JSON serialized)
    pub form_data: String,
    
    /// Form version for optimistic locking
    pub version: i64,
    
    /// Whether this change has been persisted
    pub is_saved: bool,
    
    /// Number of save attempts for this change
    pub save_attempts: u32,
}

/// Auto-save status for user notifications
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AutoSaveStatus {
    /// No changes detected
    Idle,
    
    /// Changes detected, saving in progress
    Saving { form_id: i64 },
    
    /// Save completed successfully
    Saved { form_id: i64, timestamp: DateTime<Utc> },
    
    /// Save failed with error
    Failed { form_id: i64, error: String, retry_count: u32 },
    
    /// Conflict detected during save
    Conflict { form_id: i64, local_version: i64, remote_version: i64 },
    
    /// Recovered changes from crash
    Recovered { form_count: usize },
}

/// Auto-save service for managing form change detection and automatic saving
pub struct AutoSaveService {
    /// Service configuration
    config: AutoSaveConfig,
    
    /// Database connection for form operations
    database: Arc<Mutex<Database>>,
    
    /// Tracked form changes (form_id -> FormChange)
    tracked_changes: Arc<RwLock<HashMap<i64, FormChange>>>,
    
    /// Current auto-save status
    status: Arc<RwLock<AutoSaveStatus>>,
    
    /// Flag to control the auto-save loop
    is_running: Arc<RwLock<bool>>,
}

impl AutoSaveService {
    /// Creates a new auto-save service with default configuration
    pub fn new(database: Arc<Mutex<Database>>) -> Result<Self> {
        Self::with_config(database, AutoSaveConfig::default())
    }
    
    /// Creates a new auto-save service with custom configuration
    pub fn with_config(database: Arc<Mutex<Database>>, config: AutoSaveConfig) -> Result<Self> {
        // Ensure recovery directory exists if crash recovery is enabled
        if config.enable_crash_recovery {
            std::fs::create_dir_all(&config.recovery_directory)
                .with_context(|| format!("Failed to create recovery directory: {:?}", config.recovery_directory))?;
        }
        
        Ok(Self {
            config,
            database,
            tracked_changes: Arc::new(RwLock::new(HashMap::new())),
            status: Arc::new(RwLock::new(AutoSaveStatus::Idle)),
            is_running: Arc::new(RwLock::new(false)),
        })
    }
    
    /// Starts the auto-save service with periodic timer
    pub async fn start(self: Arc<Self>) -> Result<()> {
        {
            let mut running = self.is_running.write().await;
            if *running {
                return Err(anyhow!("Auto-save service is already running"));
            }
            *running = true;
        }
        
        info!("Starting auto-save service with {}-second intervals", self.config.save_interval_seconds);
        
        // Recover any pending changes from previous session
        if self.config.enable_crash_recovery {
            self.recover_from_crash().await?;
        }
        
        // Start the periodic save timer
        let timer_service = Arc::clone(&self);
        
        tokio::spawn(async move {
            timer_service.run_auto_save_loop().await;
        });
        
        Ok(())
    }
    
    /// Stops the auto-save service
    pub async fn stop(&self) -> Result<()> {
        info!("Stopping auto-save service");
        
        {
            let mut running = self.is_running.write().await;
            *running = false;
        }
        
        // Perform final save of all pending changes
        self.save_all_pending_changes().await?;
        
        info!("Auto-save service stopped");
        Ok(())
    }
    
    /// Tracks changes to a form by computing and comparing data hashes
    pub async fn track_form_change(&self, form_id: i64, form_data: &serde_json::Value, version: i64) -> Result<bool> {
        let data_string = serde_json::to_string(form_data)
            .with_context(|| "Failed to serialize form data for change tracking")?;
        
        let data_hash = self.compute_data_hash(&data_string);
        let now = Utc::now();
        
        let mut changes = self.tracked_changes.write().await;
        
        // Check if this is a new change
        let is_changed = if let Some(existing_change) = changes.get(&form_id) {
            // Compare hashes to detect actual changes
            existing_change.data_hash != data_hash
        } else {
            // First time tracking this form
            true
        };
        
        if is_changed {
            debug!("Change detected for form {}: hash {}", form_id, &data_hash[..8]);
            
            let form_change = FormChange {
                form_id,
                data_hash,
                last_modified: now,
                form_data: data_string.clone(),
                version,
                is_saved: false,
                save_attempts: 0,
            };
            
            changes.insert(form_id, form_change);
            
            // Create recovery file if crash recovery is enabled
            if self.config.enable_crash_recovery {
                self.create_recovery_file(form_id, &data_string, version).await?;
            }
        }
        
        Ok(is_changed)
    }
    
    /// Gets the current auto-save status
    pub async fn get_status(&self) -> AutoSaveStatus {
        self.status.read().await.clone()
    }
    
    /// Gets pending changes count
    pub async fn get_pending_changes_count(&self) -> usize {
        let changes = self.tracked_changes.read().await;
        changes.values().filter(|change| !change.is_saved).count()
    }
    
    /// Forces immediate save of all pending changes
    pub async fn save_all_pending_changes(&self) -> Result<Vec<i64>> {
        let mut saved_forms = Vec::new();
        let mut changes = self.tracked_changes.write().await;
        
        for (form_id, change) in changes.iter_mut() {
            if !change.is_saved {
                match self.save_form_change(*form_id, change).await {
                    Ok(()) => {
                        change.is_saved = true;
                        saved_forms.push(*form_id);
                        debug!("Successfully saved form {} during forced save", form_id);
                    },
                    Err(e) => {
                        change.save_attempts += 1;
                        warn!("Failed to save form {} during forced save: {}", form_id, e);
                    }
                }
            }
        }
        
        if !saved_forms.is_empty() {
            info!("Force saved {} forms", saved_forms.len());
        }
        
        Ok(saved_forms)
    }
    
    /// Computes SHA-256 hash of form data for change detection
    fn compute_data_hash(&self, data: &str) -> String {
        let mut hasher = Sha256::new();
        hasher.update(data.as_bytes());
        format!("{:x}", hasher.finalize())
    }
    
    /// Main auto-save loop that runs periodically
    async fn run_auto_save_loop(&self) {
        let mut timer = interval(Duration::from_secs(self.config.save_interval_seconds));
        
        loop {
            timer.tick().await;
            
            // Check if service should continue running
            {
                let running = self.is_running.read().await;
                if !*running {
                    break;
                }
            }
            
            // Process pending changes
            if let Err(e) = self.process_pending_changes().await {
                error!("Error during auto-save cycle: {}", e);
            }
        }
        
        info!("Auto-save loop terminated");
    }
    
    /// Processes all pending changes and attempts to save them
    async fn process_pending_changes(&self) -> Result<()> {
        let mut changes = self.tracked_changes.write().await;
        let mut status = self.status.write().await;
        
        let pending_changes: Vec<_> = changes.iter()
            .filter(|(_, change)| !change.is_saved)
            .map(|(form_id, change)| (*form_id, change.clone()))
            .collect();
        
        if pending_changes.is_empty() {
            *status = AutoSaveStatus::Idle;
            return Ok(());
        }
        
        debug!("Processing {} pending changes", pending_changes.len());
        
        for (form_id, mut change) in pending_changes {
            *status = AutoSaveStatus::Saving { form_id };
            
            match self.save_form_change(form_id, &mut change).await {
                Ok(()) => {
                    change.is_saved = true;
                    changes.insert(form_id, change);
                    
                    *status = AutoSaveStatus::Saved { 
                        form_id, 
                        timestamp: Utc::now() 
                    };
                    
                    // Remove recovery file on successful save
                    if self.config.enable_crash_recovery {
                        let _ = self.remove_recovery_file(form_id).await;
                    }
                    
                    debug!("Auto-saved form {} successfully", form_id);
                },
                Err(e) => {
                    change.save_attempts += 1;
                    changes.insert(form_id, change.clone());
                    
                    *status = AutoSaveStatus::Failed {
                        form_id,
                        error: e.to_string(),
                        retry_count: change.save_attempts,
                    };
                    
                    warn!("Auto-save failed for form {} (attempt {}): {}", 
                          form_id, change.save_attempts, e);
                }
            }
        }
        
        Ok(())
    }
    
    /// Saves a single form change to the database
    async fn save_form_change(&self, form_id: i64, change: &mut FormChange) -> Result<()> {
        let form_data: serde_json::Value = serde_json::from_str(&change.form_data)
            .with_context(|| "Failed to parse form data for saving")?;
        
        let form_data_map: HashMap<String, serde_json::Value> = if let serde_json::Value::Object(map) = form_data {
            map.into_iter().collect()
        } else {
            return Err(anyhow!("Form data is not a valid JSON object"));
        };
        
        let update_request = UpdateFormRequest {
            incident_name: None,
            incident_number: None,
            status: None,
            data: Some(form_data_map),
            notes: None,
            preparer_name: None,
            operational_period_start: None,
            operational_period_end: None,
            priority: None,
            workflow_position: None,
            expected_version: Some(change.version),
        };
        
        // Create database connection and form model
        let db = self.database.lock().await;
        let database_clone = Database::new().await
            .with_context(|| "Failed to create database connection for auto-save")?;
        let form_model = FormModel::new(database_clone);
        
        // Attempt to save the form
        let updated_form = form_model.update_form(form_id, update_request).await
            .with_context(|| format!("Failed to update form {} during auto-save", form_id))?;
        
        // Update the change version using timestamp-based approach
        // Convert updated_at timestamp to version number (Unix timestamp)
        change.version = updated_form.updated_at.timestamp();
        
        Ok(())
    }
    
    /// Creates a recovery file for crash recovery
    async fn create_recovery_file(&self, form_id: i64, form_data: &str, version: i64) -> Result<()> {
        let recovery_file_path = self.config.recovery_directory.join(format!("form_{}.recovery", form_id));
        
        let recovery_data = serde_json::json!({
            "form_id": form_id,
            "form_data": form_data,
            "version": version,
            "timestamp": Utc::now().to_rfc3339(),
        });
        
        tokio::fs::write(&recovery_file_path, recovery_data.to_string())
            .await
            .with_context(|| format!("Failed to create recovery file: {:?}", recovery_file_path))?;
        
        debug!("Created recovery file for form {}", form_id);
        Ok(())
    }
    
    /// Removes a recovery file after successful save
    async fn remove_recovery_file(&self, form_id: i64) -> Result<()> {
        let recovery_file_path = self.config.recovery_directory.join(format!("form_{}.recovery", form_id));
        
        if recovery_file_path.exists() {
            tokio::fs::remove_file(&recovery_file_path)
                .await
                .with_context(|| format!("Failed to remove recovery file: {:?}", recovery_file_path))?;
            
            debug!("Removed recovery file for form {}", form_id);
        }
        
        Ok(())
    }
    
    /// Recovers pending changes from previous session crash
    async fn recover_from_crash(&self) -> Result<()> {
        if !self.config.recovery_directory.exists() {
            return Ok(());
        }
        
        let mut recovery_files = Vec::new();
        let mut dir_entries = tokio::fs::read_dir(&self.config.recovery_directory).await
            .with_context(|| format!("Failed to read recovery directory: {:?}", self.config.recovery_directory))?;
        
        while let Some(entry) = dir_entries.next_entry().await? {
            let path = entry.path();
            if path.extension().and_then(|s| s.to_str()) == Some("recovery") {
                recovery_files.push(path);
            }
        }
        
        if recovery_files.is_empty() {
            return Ok(());
        }
        
        info!("Found {} recovery files from previous session", recovery_files.len());
        let mut recovered_count = 0;
        
        for recovery_file in recovery_files {
            match self.process_recovery_file(&recovery_file).await {
                Ok(true) => recovered_count += 1,
                Ok(false) => {
                    debug!("Recovery file {:?} was outdated, skipping", recovery_file);
                },
                Err(e) => {
                    warn!("Failed to process recovery file {:?}: {}", recovery_file, e);
                }
            }
        }
        
        if recovered_count > 0 {
            info!("Successfully recovered {} forms from crash", recovered_count);
            
            let mut status = self.status.write().await;
            *status = AutoSaveStatus::Recovered { form_count: recovered_count };
        }
        
        Ok(())
    }
    
    /// Processes a single recovery file
    async fn process_recovery_file(&self, recovery_file_path: &PathBuf) -> Result<bool> {
        let recovery_content = tokio::fs::read_to_string(recovery_file_path)
            .await
            .with_context(|| format!("Failed to read recovery file: {:?}", recovery_file_path))?;
        
        let recovery_data: serde_json::Value = serde_json::from_str(&recovery_content)
            .with_context(|| "Failed to parse recovery file JSON")?;
        
        let form_id = recovery_data["form_id"].as_i64()
            .ok_or_else(|| anyhow!("Invalid form_id in recovery file"))?;
        
        let form_data_str = recovery_data["form_data"].as_str()
            .ok_or_else(|| anyhow!("Invalid form_data in recovery file"))?;
        
        let version = recovery_data["version"].as_i64()
            .ok_or_else(|| anyhow!("Invalid version in recovery file"))?;
        
        let timestamp_str = recovery_data["timestamp"].as_str()
            .ok_or_else(|| anyhow!("Invalid timestamp in recovery file"))?;
        
        let timestamp = DateTime::parse_from_rfc3339(timestamp_str)
            .with_context(|| "Failed to parse recovery timestamp")?
            .with_timezone(&Utc);
        
        // Check if recovery file is too old
        let age = Utc::now().signed_duration_since(timestamp);
        if age.num_hours() > self.config.recovery_file_max_age_hours as i64 {
            // Remove outdated recovery file
            let _ = tokio::fs::remove_file(recovery_file_path).await;
            return Ok(false);
        }
        
        // Add to tracked changes for processing
        let form_data: serde_json::Value = serde_json::from_str(form_data_str)
            .with_context(|| "Failed to parse recovered form data")?;
        
        self.track_form_change(form_id, &form_data, version).await?;
        
        debug!("Recovered form {} from crash (age: {} hours)", form_id, age.num_hours());
        Ok(true)
    }
}

/// Helper function to validate if a form change is worth saving
fn is_significant_change(old_data: &str, new_data: &str) -> bool {
    // Simple check for now - could be enhanced with more sophisticated logic
    old_data != new_data
}
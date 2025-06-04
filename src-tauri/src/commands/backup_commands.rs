/*! 
 * Simple Database Backup Commands for RadioForms
 * 
 * Following MANDATORY.md: Simple file copying for single-user app with 2,000 forms max.
 * No complex enterprise backup patterns - just working data protection.
 */

use tauri::State;
use crate::database::simple::{get_pool, DatabaseState};
use std::path::Path;
use std::fs;
use chrono::{DateTime, Utc};
use serde::{Serialize, Deserialize};

/// Simple backup metadata
#[derive(Serialize, Deserialize)]
struct BackupMetadata {
    version: String,
    created_at: DateTime<Utc>,
    form_count: i64,
    checksum: String,
}

/// Create a manual backup to specified location
#[tauri::command]
pub async fn create_backup(
    backup_path: String,
    _state: State<'_, DatabaseState>
) -> Result<String, String> {
    let pool = get_pool().await?;
    
    // Get form count for metadata - OPTIMIZED: Use simple query instead of macro
    let form_count: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM forms")
        .fetch_one(&pool)
        .await
        .map_err(|e| format!("Failed to count forms: {}", e))?;
    
    // Source database file
    let db_source = "radioforms.db";
    
    // Check if source exists
    if !Path::new(db_source).exists() {
        return Err("Database file not found".to_string());
    }
    
    // Copy database file
    fs::copy(db_source, &backup_path)
        .map_err(|e| format!("Failed to copy database: {}", e))?;
    
    // Calculate simple checksum (file size for simplicity)
    let metadata = fs::metadata(&backup_path)
        .map_err(|e| format!("Failed to read backup metadata: {}", e))?;
    let checksum = format!("{}", metadata.len());
    
    // Create metadata file
    let backup_meta = BackupMetadata {
        version: "1.0.0".to_string(),
        created_at: Utc::now(),
        form_count,
        checksum: checksum.clone(),
    };
    
    let meta_path = format!("{}.meta", backup_path);
    let meta_json = serde_json::to_string_pretty(&backup_meta)
        .map_err(|e| format!("Failed to serialize metadata: {}", e))?;
    
    fs::write(meta_path, meta_json)
        .map_err(|e| format!("Failed to write metadata: {}", e))?;
    
    Ok(format!("Backup created successfully with {} forms (checksum: {})", form_count, checksum))
}

/// Restore database from backup file
#[tauri::command]
pub async fn restore_backup(
    backup_path: String,
    _state: State<'_, DatabaseState>
) -> Result<String, String> {
    // Check if backup file exists
    if !Path::new(&backup_path).exists() {
        return Err("Backup file not found".to_string());
    }
    
    // Check metadata file
    let meta_path = format!("{}.meta", backup_path);
    let metadata = if Path::new(&meta_path).exists() {
        let meta_content = fs::read_to_string(&meta_path)
            .map_err(|e| format!("Failed to read metadata: {}", e))?;
        
        let meta: BackupMetadata = serde_json::from_str(&meta_content)
            .map_err(|e| format!("Invalid metadata format: {}", e))?;
        
        // Verify checksum
        let backup_metadata = fs::metadata(&backup_path)
            .map_err(|e| format!("Failed to read backup file: {}", e))?;
        let current_checksum = format!("{}", backup_metadata.len());
        
        if current_checksum != meta.checksum {
            return Err("Backup file integrity check failed".to_string());
        }
        
        Some(meta)
    } else {
        None
    };
    
    // Create backup of current database before restore
    let current_db = "radioforms.db";
    if Path::new(current_db).exists() {
        let backup_current = format!("{}.backup.{}", current_db, Utc::now().timestamp());
        fs::copy(current_db, backup_current)
            .map_err(|e| format!("Failed to backup current database: {}", e))?;
    }
    
    // Restore from backup
    fs::copy(&backup_path, current_db)
        .map_err(|e| format!("Failed to restore from backup: {}", e))?;
    
    let message = if let Some(meta) = metadata {
        format!("Database restored successfully from backup created on {} with {} forms", 
               meta.created_at.format("%Y-%m-%d %H:%M:%S"), meta.form_count)
    } else {
        "Database restored successfully (no metadata available)".to_string()
    };
    
    Ok(message)
}

/// List available backup files in a directory
#[tauri::command]
pub async fn list_backups(
    directory_path: String
) -> Result<Vec<String>, String> {
    if !Path::new(&directory_path).exists() {
        return Err("Directory not found".to_string());
    }
    
    let mut backups = Vec::new();
    
    let entries = fs::read_dir(&directory_path)
        .map_err(|e| format!("Failed to read directory: {}", e))?;
    
    for entry in entries {
        let entry = entry.map_err(|e| format!("Failed to read entry: {}", e))?;
        let path = entry.path();
        
        if let Some(extension) = path.extension() {
            if extension == "db" {
                if let Some(filename) = path.file_name() {
                    if let Some(filename_str) = filename.to_str() {
                        // Check if metadata file exists
                        let meta_path = path.with_extension("db.meta");
                        let has_metadata = meta_path.exists();
                        
                        let display_name = if has_metadata {
                            format!("{} (with metadata)", filename_str)
                        } else {
                            filename_str.to_string()
                        };
                        
                        backups.push(display_name);
                    }
                }
            }
        }
    }
    
    backups.sort();
    Ok(backups)
}

/// Get backup information
#[tauri::command]
pub async fn get_backup_info(
    backup_path: String
) -> Result<String, String> {
    if !Path::new(&backup_path).exists() {
        return Err("Backup file not found".to_string());
    }
    
    let meta_path = format!("{}.meta", backup_path);
    
    if Path::new(&meta_path).exists() {
        let meta_content = fs::read_to_string(&meta_path)
            .map_err(|e| format!("Failed to read metadata: {}", e))?;
        
        let meta: BackupMetadata = serde_json::from_str(&meta_content)
            .map_err(|e| format!("Invalid metadata format: {}", e))?;
        
        Ok(format!("Created: {}\nForms: {}\nVersion: {}\nChecksum: {}", 
                  meta.created_at.format("%Y-%m-%d %H:%M:%S"),
                  meta.form_count,
                  meta.version,
                  meta.checksum))
    } else {
        let metadata = fs::metadata(&backup_path)
            .map_err(|e| format!("Failed to read file info: {}", e))?;
        
        Ok(format!("File size: {} bytes\nNo metadata available", metadata.len()))
    }
}
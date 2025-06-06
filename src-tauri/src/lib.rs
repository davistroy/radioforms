/*!
 * RadioForms - STANDALONE ICS Forms Management Application
 * 
 * This is the main library entry point for the RadioForms Tauri application.
 * The application provides a complete solution for managing FEMA ICS forms
 * in a portable, standalone desktop application.
 * 
 * Business Logic:
 * - Single executable + single database file deployment
 * - SQLite database for complete portability
 * - All form operations through comprehensive business logic layer
 * - Real-time validation and ICS compliance checking
 * 
 * Architecture:
 * - Tauri framework for native desktop integration
 * - Rust backend for performance and safety
 * - React frontend for modern UI/UX
 * - SQLite for reliable data storage
 */

// Simple imports for the simplified application

// Import all modules
mod database;
mod models;
mod commands;
mod services;
mod utils;
pub mod templates;

use commands::*;

/// Initialize logging for the application.
/// 
/// Business Logic:
/// - Logs to both console and file for debugging
/// - Different log levels for development vs production
/// - Includes timestamp and module information
fn init_logging() {
    env_logger::Builder::from_default_env()
        .filter_level(log::LevelFilter::Info)
        .init();
    
    log::info!("RadioForms application starting...");
}

/// Main application entry point.
/// 
/// Business Logic:
/// - Initializes database connection with portable path handling
/// - Sets up all Tauri commands for frontend communication
/// - Configures plugins for file system and dialog access
/// - Manages application state throughout lifecycle
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // Initialize logging
    init_logging();

    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .setup(|_app| {
            // Simple database initialization with graceful error handling
            let db_path = "radioforms.db";
            match tauri::async_runtime::block_on(async {
                database::simple::init_database(db_path).await
            }) {
                Ok(()) => {
                    log::info!("Database initialized successfully");
                    log::info!("RadioForms application initialized successfully");
                    Ok(())
                }
                Err(e) => {
                    log::error!("Failed to initialize database: {}", e);
                    // Return setup error instead of crashing
                    // Convert String error to std::error::Error
                    Err(Box::new(std::io::Error::new(
                        std::io::ErrorKind::Other,
                        e
                    )))
                }
            }
        })
        .invoke_handler(tauri::generate_handler![
            save_form, get_form, update_form, 
            search_forms, advanced_search, get_all_forms, delete_form,
            update_form_status, get_available_transitions, can_edit_form,
            export_forms_json, export_form_json, import_forms_json, export_form_icsdes,
            create_backup, restore_backup, list_backups, get_backup_info,
            greet
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

/// Simple greet command for testing Tauri communication.
/// This will be removed once the application is fully implemented.
#[tauri::command]
fn greet(name: &str) -> String {
    log::debug!("Greet command called with name: {}", name);
    format!("Hello, {}! Welcome to RadioForms!", name)
}

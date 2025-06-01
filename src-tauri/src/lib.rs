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

use std::sync::Arc;
use tokio::sync::Mutex;
use tauri::Manager;

// Import all modules
mod database;
mod models;
mod commands;
mod utils;

use database::Database;
use commands::*;

/// Application state type for sharing database connection
pub type AppState = Arc<Mutex<Database>>;

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
        .setup(|app| {
            // Initialize database connection
            tauri::async_runtime::block_on(async {
                match Database::new().await {
                    Ok(database) => {
                        log::info!("Database initialized successfully at: {:?}", database.database_path());
                        
                        // Store database in application state
                        let state = Arc::new(Mutex::new(database));
                        app.manage(state);
                    },
                    Err(e) => {
                        log::error!("Failed to initialize database: {}", e);
                        std::process::exit(1);
                    }
                }
            });

            log::info!("RadioForms application initialized successfully");
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            // Form management commands
            create_form,
            get_form,
            update_form,
            delete_form,
            search_forms,
            get_forms_by_incident,
            get_recent_forms,
            duplicate_form,
            get_form_types,
            get_database_stats,
            
            // Keep the original greet command for testing
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

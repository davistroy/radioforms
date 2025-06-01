/*!
 * Tauri commands for RadioForms application
 * 
 * This module contains all Tauri commands that can be invoked from the
 * frontend. These commands provide the bridge between the React frontend
 * and the Rust backend.
 * 
 * Business Logic:
 * - All commands are thoroughly documented
 * - Proper error handling with user-friendly messages
 * - Input validation for all parameters
 * - Comprehensive logging for debugging
 * 
 * Design Philosophy:
 * - Keep commands simple and focused
 * - Business logic in models, not in commands
 * - Consistent error handling patterns
 */

pub mod form_commands;
pub mod settings_commands;
pub mod export_commands;
pub mod auto_save_commands;

// Re-export all commands for easy registration
pub use form_commands::*;
pub use settings_commands::*;
pub use export_commands::*;
pub use auto_save_commands::*;
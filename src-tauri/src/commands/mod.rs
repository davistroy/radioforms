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

pub mod simple_commands;
pub mod export_commands;

#[cfg(test)]
pub mod integration_tests;

// Re-export simple commands
pub use simple_commands::*;
// Re-export export commands
pub use export_commands::*;
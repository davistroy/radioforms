/*!
 * Data models for RadioForms application
 * 
 * This module contains all data models and business logic for the
 * STANDALONE ICS Forms Management Application.
 * 
 * Business Logic:
 * - Simple model structure for easy maintenance
 * - Type-safe operations with comprehensive error handling
 * - Form validation according to ICS standards
 * - Support for all 20 ICS form types
 * 
 * Design Philosophy:
 * - Keep models simple and focused
 * - Business logic in models, not in UI components
 * - Comprehensive documentation for all operations
 */

pub mod form;
pub mod validation;
pub mod export;

// Re-export commonly used types
pub use crate::database::schema::{Form, FormStatus, ICSFormType, Setting};
pub use form::*;
pub use validation::*;
pub use export::*;
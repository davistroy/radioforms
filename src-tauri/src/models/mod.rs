/*!
 * Data models for RadioForms application
 * 
 * This module contains all data models and business logic for the
 * STANDALONE ICS Forms Management Application.
 * 
 * Business Logic:
 * - Type-safe model structures for all 20 ICS forms
 * - Comprehensive validation according to ICS standards
 * - Support for complex form relationships and workflows
 * - Multi-format export capabilities including ICS-DES
 * 
 * Design Philosophy:
 * - Keep models simple and focused
 * - Business logic in models, not in UI components
 * - Comprehensive documentation for all operations
 * - Zero technical debt - complete implementations only
 */

pub mod form;
pub mod validation;
pub mod export;
pub mod ics_types;
pub mod form_data;
pub mod serde_tests;

// Re-export commonly used types
pub use crate::database::schema::{Form, FormStatus, ICSFormType, Setting};
pub use form::*;
pub use validation::*;
pub use export::*;
pub use ics_types::*;
pub use form_data::*;
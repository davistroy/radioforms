/*!
 * Utility modules for RadioForms application
 * 
 * This module contains various utility functions and helpers used
 * throughout the application for common operations like serialization,
 * data validation, file handling, and performance optimization.
 * 
 * Business Logic:
 * - Reusable utility functions for common operations
 * - Performance optimization helpers
 * - Data validation and transformation utilities
 * - Cross-cutting concerns and shared functionality
 * 
 * Design Philosophy:
 * - Keep utilities focused and single-purpose
 * - Provide comprehensive error handling
 * - Optimize for common use cases
 * - Zero dependencies on business logic
 */

pub mod serialization;

// Re-export commonly used utilities
pub use serialization::{
    safe_to_json, 
    safe_from_json, 
    serialize_optimized, 
    merge_json_objects,
    validate_form_json,
    SerializationMetrics,
};
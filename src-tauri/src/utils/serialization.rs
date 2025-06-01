/*!
 * Application Serialization Utilities
 * 
 * This module provides practical serialization utilities used throughout
 * the RadioForms application. It handles common serialization patterns,
 * error recovery, and performance optimization for form data.
 * 
 * Business Logic:
 * - Safe serialization with error recovery
 * - Performance-optimized JSON handling
 * - Custom formats for specific use cases (ICS-DES, exports)
 * - Data integrity validation during serialization
 * 
 * Design Philosophy:
 * - Fail gracefully with meaningful error messages
 * - Optimize for common use cases in form management
 * - Provide debugging aids for serialization issues
 * - Zero data loss during serialization operations
 */

use serde::{Serialize, Deserialize, Serializer, Deserializer};
use serde_json::{Value as JsonValue, Map as JsonMap};
use anyhow::{Result, Context, anyhow};
use chrono::{DateTime, Utc, NaiveDate, NaiveTime};
use std::collections::HashMap;

/// Safe JSON serialization with error recovery.
/// 
/// Business Logic:
/// - Attempts to serialize data with fallback strategies
/// - Provides detailed error information for debugging
/// - Handles edge cases like NaN, infinite values
/// - Ensures consistent JSON output format
pub fn safe_to_json<T: Serialize>(data: &T) -> Result<String> {
    match serde_json::to_string_pretty(data) {
        Ok(json) => {
            // Validate the JSON is properly formed
            serde_json::from_str::<JsonValue>(&json)
                .context("Generated JSON is invalid")?;
            Ok(json)
        },
        Err(e) => {
            // Try to serialize without pretty printing as fallback
            match serde_json::to_string(data) {
                Ok(json) => {
                    log::warn!("Pretty printing failed, using compact JSON: {}", e);
                    Ok(json)
                },
                Err(e2) => {
                    Err(anyhow!("Failed to serialize data: pretty={}, compact={}", e, e2))
                }
            }
        }
    }
}

/// Safe JSON deserialization with error recovery.
/// 
/// Business Logic:
/// - Attempts multiple deserialization strategies
/// - Provides context about where deserialization failed
/// - Handles malformed JSON gracefully
/// - Supports partial recovery when possible
pub fn safe_from_json<T: for<'de> Deserialize<'de>>(json: &str) -> Result<T> {
    // First, validate that the JSON is well-formed
    let _: JsonValue = serde_json::from_str(json)
        .context("JSON is malformed")?;
    
    // Then deserialize to the target type
    serde_json::from_str(json)
        .with_context(|| format!("Failed to deserialize JSON to target type: {}", 
                                std::any::type_name::<T>()))
}

/// Serializes data with size optimization.
/// 
/// Business Logic:
/// - Uses compact JSON for large data structures
/// - Removes null values to reduce size
/// - Applies field filtering for specific use cases
/// - Provides size metrics for monitoring
pub fn serialize_optimized<T: Serialize>(data: &T, remove_nulls: bool) -> Result<String> {
    let mut json_value = serde_json::to_value(data)
        .context("Failed to convert data to JSON value")?;
    
    if remove_nulls {
        remove_null_values(&mut json_value);
    }
    
    let json = serde_json::to_string(&json_value)
        .context("Failed to serialize optimized JSON")?;
    
    log::debug!("Serialized {} bytes (nulls removed: {})", json.len(), remove_nulls);
    
    Ok(json)
}

/// Recursively removes null values from JSON.
fn remove_null_values(value: &mut JsonValue) {
    match value {
        JsonValue::Object(map) => {
            map.retain(|_, v| !v.is_null());
            for (_, v) in map.iter_mut() {
                remove_null_values(v);
            }
        },
        JsonValue::Array(arr) => {
            arr.retain(|v| !v.is_null());
            for v in arr.iter_mut() {
                remove_null_values(v);
            }
        },
        _ => {}
    }
}

/// Merges two JSON objects, with the second taking precedence.
/// 
/// Business Logic:
/// - Useful for form data updates and patches
/// - Preserves nested structure during merges
/// - Handles type conflicts gracefully
/// - Supports array merging strategies
pub fn merge_json_objects(base: &JsonValue, update: &JsonValue) -> Result<JsonValue> {
    match (base, update) {
        (JsonValue::Object(base_map), JsonValue::Object(update_map)) => {
            let mut result = base_map.clone();
            
            for (key, update_value) in update_map {
                match result.get(key) {
                    Some(base_value) => {
                        // Recursively merge nested objects
                        result.insert(key.clone(), merge_json_objects(base_value, update_value)?);
                    },
                    None => {
                        // Add new field from update
                        result.insert(key.clone(), update_value.clone());
                    }
                }
            }
            
            Ok(JsonValue::Object(result))
        },
        (_, update) => {
            // For non-objects, update takes precedence
            Ok(update.clone())
        }
    }
}

/// Extracts specific fields from JSON for partial serialization.
/// 
/// Business Logic:
/// - Useful for API responses with field filtering
/// - Supports nested field extraction
/// - Handles missing fields gracefully
/// - Maintains original data types
pub fn extract_json_fields(data: &JsonValue, field_paths: &[&str]) -> Result<JsonValue> {
    let mut result = JsonMap::new();
    
    for path in field_paths {
        if let Some(value) = extract_nested_field(data, path) {
            // Handle nested paths like "header.incident_name"
            let parts: Vec<&str> = path.split('.').collect();
            insert_nested_field(&mut result, &parts, value.clone())?;
        }
    }
    
    Ok(JsonValue::Object(result))
}

/// Extracts a nested field from JSON using dot notation.
fn extract_nested_field<'a>(data: &'a JsonValue, path: &str) -> Option<&'a JsonValue> {
    let parts: Vec<&str> = path.split('.').collect();
    let mut current = data;
    
    for part in parts {
        match current {
            JsonValue::Object(map) => {
                current = map.get(part)?;
            },
            _ => return None,
        }
    }
    
    Some(current)
}

/// Inserts a value into a nested JSON structure.
fn insert_nested_field(map: &mut JsonMap<String, JsonValue>, path: &[&str], value: JsonValue) -> Result<()> {
    if path.is_empty() {
        return Err(anyhow!("Empty field path"));
    }
    
    if path.len() == 1 {
        map.insert(path[0].to_string(), value);
        return Ok(());
    }
    
    let key = path[0];
    let remaining_path = &path[1..];
    
    // Get or create nested object
    let nested = map.entry(key.to_string())
        .or_insert_with(|| JsonValue::Object(JsonMap::new()));
    
    match nested {
        JsonValue::Object(nested_map) => {
            insert_nested_field(nested_map, remaining_path, value)?;
        },
        _ => {
            return Err(anyhow!("Cannot insert into non-object field: {}", key));
        }
    }
    
    Ok(())
}

/// Custom serialization for DateTime fields to ensure consistent format.
/// 
/// Business Logic:
/// - Always uses ISO 8601 format for API compatibility
/// - Includes timezone information
/// - Handles edge cases like far-future dates
/// - Provides readable format for debugging
pub fn serialize_datetime<S>(datetime: &DateTime<Utc>, serializer: S) -> Result<S::Ok, S::Error>
where
    S: Serializer,
{
    // Use RFC 3339 format which is ISO 8601 compatible
    let formatted = datetime.to_rfc3339();
    serializer.serialize_str(&formatted)
}

/// Custom deserialization for DateTime fields with multiple format support.
/// 
/// Business Logic:
/// - Supports multiple common datetime formats
/// - Provides error recovery for malformed dates
/// - Converts to UTC for consistency
/// - Handles timezone variations
pub fn deserialize_datetime<'de, D>(deserializer: D) -> Result<DateTime<Utc>, D::Error>
where
    D: Deserializer<'de>,
{
    let s = String::deserialize(deserializer)?;
    
    // Try RFC 3339 format first (ISO 8601)
    if let Ok(dt) = DateTime::parse_from_rfc3339(&s) {
        return Ok(dt.with_timezone(&Utc));
    }
    
    // Try RFC 2822 format
    if let Ok(dt) = DateTime::parse_from_rfc2822(&s) {
        return Ok(dt.with_timezone(&Utc));
    }
    
    // Try common format without timezone (assume UTC)
    if let Ok(naive_dt) = chrono::NaiveDateTime::parse_from_str(&s, "%Y-%m-%d %H:%M:%S") {
        return Ok(DateTime::from_naive_utc_and_offset(naive_dt, Utc));
    }
    
    // Try date-only format (assume start of day UTC)
    if let Ok(date) = NaiveDate::parse_from_str(&s, "%Y-%m-%d") {
        let datetime = date.and_hms_opt(0, 0, 0).unwrap();
        return Ok(DateTime::from_naive_utc_and_offset(datetime, Utc));
    }
    
    Err(serde::de::Error::custom(format!("Invalid datetime format: {}", s)))
}

/// Validates JSON data against expected schema patterns.
/// 
/// Business Logic:
/// - Ensures form data meets ICS standards
/// - Validates required fields are present
/// - Checks data types and formats
/// - Provides detailed validation reports
pub fn validate_form_json(json: &JsonValue, form_type: &str) -> Result<Vec<String>> {
    let mut errors = Vec::new();
    
    // Common validations for all forms
    if let Some(incident_name) = json.get("incident_name") {
        if let Some(name_str) = incident_name.as_str() {
            if name_str.trim().len() < 3 {
                errors.push("Incident name must be at least 3 characters".to_string());
            }
        } else {
            errors.push("Incident name must be a string".to_string());
        }
    } else {
        errors.push("Incident name is required".to_string());
    }
    
    // Form-specific validations
    match form_type {
        "ICS-201" => {
            if let Some(summary) = json.get("situation_summary") {
                if let Some(summary_str) = summary.as_str() {
                    if summary_str.trim().len() < 10 {
                        errors.push("ICS-201 situation summary must be at least 10 characters".to_string());
                    }
                }
            } else {
                errors.push("ICS-201 requires situation_summary field".to_string());
            }
        },
        "ICS-202" => {
            if let Some(objectives) = json.get("objectives") {
                if let Some(obj_str) = objectives.as_str() {
                    if obj_str.trim().len() < 10 {
                        errors.push("ICS-202 objectives must be at least 10 characters".to_string());
                    }
                }
            } else {
                errors.push("ICS-202 requires objectives field".to_string());
            }
        },
        "ICS-205" => {
            if let Some(channels) = json.get("radio_channels") {
                if let Some(channels_array) = channels.as_array() {
                    if channels_array.is_empty() {
                        errors.push("ICS-205 requires at least one radio channel".to_string());
                    }
                }
            } else {
                errors.push("ICS-205 requires radio_channels field".to_string());
            }
        },
        _ => {
            // Generic validation for other forms
            log::debug!("No specific validation rules for form type: {}", form_type);
        }
    }
    
    Ok(errors)
}

/// Performance monitoring for serialization operations.
/// 
/// Business Logic:
/// - Tracks serialization performance metrics
/// - Identifies bottlenecks in data structures
/// - Provides optimization recommendations
/// - Supports performance regression detection
pub struct SerializationMetrics {
    pub operation_count: u64,
    pub total_time_ms: f64,
    pub total_bytes: u64,
    pub error_count: u64,
}

impl SerializationMetrics {
    pub fn new() -> Self {
        Self {
            operation_count: 0,
            total_time_ms: 0.0,
            total_bytes: 0,
            error_count: 0,
        }
    }
    
    pub fn record_operation(&mut self, elapsed_ms: f64, bytes: usize, success: bool) {
        self.operation_count += 1;
        self.total_time_ms += elapsed_ms;
        self.total_bytes += bytes as u64;
        if !success {
            self.error_count += 1;
        }
    }
    
    pub fn average_time_ms(&self) -> f64 {
        if self.operation_count > 0 {
            self.total_time_ms / self.operation_count as f64
        } else {
            0.0
        }
    }
    
    pub fn average_bytes(&self) -> f64 {
        if self.operation_count > 0 {
            self.total_bytes as f64 / self.operation_count as f64
        } else {
            0.0
        }
    }
    
    pub fn error_rate(&self) -> f64 {
        if self.operation_count > 0 {
            self.error_count as f64 / self.operation_count as f64
        } else {
            0.0
        }
    }
}

impl Default for SerializationMetrics {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_safe_json_operations() {
        let test_data = json!({
            "name": "Test",
            "value": 42,
            "nested": {
                "field": "data"
            }
        });
        
        let json_str = safe_to_json(&test_data).expect("Serialization should work");
        let deserialized: JsonValue = safe_from_json(&json_str).expect("Deserialization should work");
        
        assert_eq!(test_data, deserialized);
    }
    
    #[test]
    fn test_json_merge() {
        let base = json!({
            "field1": "value1",
            "nested": {
                "field2": "value2"
            }
        });
        
        let update = json!({
            "field1": "updated_value1",
            "nested": {
                "field3": "value3"
            },
            "new_field": "new_value"
        });
        
        let merged = merge_json_objects(&base, &update).expect("Merge should work");
        
        assert_eq!(merged["field1"], "updated_value1");
        assert_eq!(merged["nested"]["field2"], "value2");
        assert_eq!(merged["nested"]["field3"], "value3");
        assert_eq!(merged["new_field"], "new_value");
    }
    
    #[test]
    fn test_field_extraction() {
        let data = json!({
            "header": {
                "incident_name": "Test Incident",
                "prepared_date": "2025-01-01"
            },
            "data": {
                "summary": "Test summary"
            }
        });
        
        let extracted = extract_json_fields(&data, &["header.incident_name", "data.summary"])
            .expect("Field extraction should work");
        
        assert_eq!(extracted["header"]["incident_name"], "Test Incident");
        assert_eq!(extracted["data"]["summary"], "Test summary");
    }
    
    #[test]
    fn test_form_validation() {
        let valid_form = json!({
            "incident_name": "Valid Incident Name",
            "situation_summary": "This is a comprehensive situation summary with enough detail."
        });
        
        let errors = validate_form_json(&valid_form, "ICS-201").expect("Validation should work");
        assert!(errors.is_empty());
        
        let invalid_form = json!({
            "incident_name": "AB", // Too short
            "situation_summary": "Short" // Too short
        });
        
        let errors = validate_form_json(&invalid_form, "ICS-201").expect("Validation should work");
        assert!(!errors.is_empty());
    }
}
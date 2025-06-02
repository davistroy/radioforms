/*! 
 * Simple Tests for Database Functions
 * 
 * Following MANDATORY.md: simple tests for core validation functions.
 * Tests the basic validation logic that emergency responders depend on.
 */

#[cfg(test)]
mod tests {
    use super::super::simple::*;

    #[test]
    fn test_validate_incident_name_valid() {
        // Test valid incident names
        assert!(validate_incident_name("Fire Response 2025").is_ok());
        assert!(validate_incident_name("Test Incident").is_ok());
        assert!(validate_incident_name("A").is_ok()); // Single character should be valid
    }

    #[test]
    fn test_validate_incident_name_empty() {
        // Test empty incident names
        assert!(validate_incident_name("").is_err());
        assert!(validate_incident_name("   ").is_err()); // Only whitespace
    }

    #[test]
    fn test_validate_incident_name_too_long() {
        // Test incident names that are too long (>100 characters)
        let long_name = "A".repeat(101);
        assert!(validate_incident_name(&long_name).is_err());
    }

    #[test]
    fn test_validate_form_type_valid() {
        // Test valid ICS form types
        assert!(validate_form_type("ICS-201").is_ok());
        assert!(validate_form_type("ICS-202").is_ok());
        assert!(validate_form_type("ICS-205A").is_ok());
        assert!(validate_form_type("ICS-225").is_ok());
    }

    #[test]
    fn test_validate_form_type_invalid() {
        // Test invalid form types
        assert!(validate_form_type("ICS-999").is_err());
        assert!(validate_form_type("INVALID").is_err());
        assert!(validate_form_type("").is_err());
        assert!(validate_form_type("ics-201").is_err()); // Case sensitive
    }

    #[test]
    fn test_validate_form_data_json_valid() {
        // Test valid JSON
        assert!(validate_form_data_json("{}").is_ok());
        assert!(validate_form_data_json(r#"{"test": "value"}"#).is_ok());
        assert!(validate_form_data_json(r#"{"field1": "value1", "field2": 123}"#).is_ok());
    }

    #[test]
    fn test_validate_form_data_json_invalid() {
        // Test invalid JSON
        assert!(validate_form_data_json("invalid json").is_err());
        assert!(validate_form_data_json("{").is_err());
        assert!(validate_form_data_json(r#"{"incomplete": }"#).is_err());
        assert!(validate_form_data_json("").is_err());
    }

    #[test]
    fn test_validate_business_rules_ics_201() {
        // Test ICS-201 business rules
        let valid_data = r#"{"incident_name": "Test Fire"}"#;
        assert!(validate_business_rules("ICS-201", valid_data).is_ok());

        let invalid_data = r#"{"other_field": "value"}"#;
        assert!(validate_business_rules("ICS-201", invalid_data).is_err());
    }

    #[test]
    fn test_validate_business_rules_ics_202() {
        // Test ICS-202 business rules
        let valid_data = r#"{"incident_objectives": "Contain fire"}"#;
        assert!(validate_business_rules("ICS-202", valid_data).is_ok());

        let invalid_data = r#"{"other_field": "value"}"#;
        assert!(validate_business_rules("ICS-202", invalid_data).is_err());
    }

    #[test]
    fn test_validate_business_rules_other_forms() {
        // Test other form types (should pass basic validation)
        let data = r#"{"any_field": "any_value"}"#;
        assert!(validate_business_rules("ICS-203", data).is_ok());
        assert!(validate_business_rules("ICS-204", data).is_ok());
        assert!(validate_business_rules("ICS-225", data).is_ok());
    }

    #[test]
    fn test_validate_business_rules_invalid_json() {
        // Test with invalid JSON
        assert!(validate_business_rules("ICS-201", "invalid json").is_err());
    }
}
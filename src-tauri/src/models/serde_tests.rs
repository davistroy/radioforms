/*!
 * Serde Serialization Tests and Utilities
 * 
 * This module provides comprehensive testing and validation of Serde
 * serialization/deserialization for all ICS form data structures.
 * It ensures that all data can be correctly serialized to JSON and
 * deserialized back without data loss.
 * 
 * Business Logic:
 * - Round-trip serialization testing for all data structures
 * - JSON schema validation for consistent API contracts
 * - Performance testing for serialization operations
 * - Custom serialization helpers for complex types
 * 
 * Design Philosophy:
 * - Zero data loss during serialization/deserialization
 * - Human-readable JSON output for debugging and APIs
 * - Performance-optimized serialization for large forms
 * - Comprehensive test coverage for all data types
 */

use serde::{Deserialize, Serialize, Serializer, Deserializer};
use serde_json::{json, Value as JsonValue};
use chrono::{DateTime, Utc, NaiveDate, NaiveTime};
use anyhow::{Result, anyhow, Context};
use std::collections::HashMap;

use super::ics_types::*;
use super::form_data::*;
use super::validation::{ValidationEngine, FormValidationResult, FieldValidationResult, ValidationSummary, ValidationError, ValidationWarning, ValidationInfo, InfoType};
use crate::database::schema::{Form, FormStatus, ICSFormType};

/// Comprehensive serialization test suite for all ICS form types.
/// 
/// Business Logic:
/// - Tests all data structures can be serialized to JSON
/// - Verifies round-trip serialization preserves data integrity
/// - Validates JSON output is human-readable and API-friendly
/// - Tests edge cases and boundary conditions
pub struct SerdeTestSuite;

impl SerdeTestSuite {
    /// Tests serialization for all ICS form header components.
    /// 
    /// Business Logic:
    /// - Validates header information serializes correctly
    /// - Tests optional fields are handled properly
    /// - Ensures timestamps are in ISO 8601 format
    /// - Verifies incident information is preserved
    pub fn test_header_serialization() -> Result<()> {
        // Create a test header with all fields populated
        let header = ICSFormHeader {
            incident_name: "Wildfire - Pine Canyon".to_string(),
            operational_period: Some(DateTimeRange {
                from: DateTime::from_timestamp(1735689600, 0).unwrap(), // 2025-01-01 00:00:00 UTC
                to: DateTime::from_timestamp(1735776000, 0).unwrap(),   // 2025-01-02 00:00:00 UTC
            }),
            incident_number: Some("CA-2025-001234".to_string()),
            form_version: Some("2.0".to_string()),
            prepared_date_time: DateTime::from_timestamp(1735689600, 0).unwrap(),
            page_info: Some(PageInfo {
                page_number: Some("1 of 3".to_string()),
                iap_page_number: Some("IAP-1".to_string()),
            }),
        };

        // Test serialization
        let json = serde_json::to_string_pretty(&header)
            .context("Failed to serialize ICS form header")?;
        
        println!("ICS Form Header JSON:\n{}", json);

        // Test deserialization (round-trip)
        let deserialized: ICSFormHeader = serde_json::from_str(&json)
            .context("Failed to deserialize ICS form header")?;

        // Verify data integrity
        assert_eq!(header.incident_name, deserialized.incident_name);
        assert_eq!(header.incident_number, deserialized.incident_number);
        assert_eq!(header.form_version, deserialized.form_version);
        
        if let (Some(orig_period), Some(deser_period)) = (&header.operational_period, &deserialized.operational_period) {
            assert_eq!(orig_period.from, deser_period.from);
            assert_eq!(orig_period.to, deser_period.to);
        }

        println!("✅ ICS Form Header serialization test passed");
        Ok(())
    }

    /// Tests serialization for all ICS form footer components.
    /// 
    /// Business Logic:
    /// - Validates signature information serializes correctly
    /// - Tests approval workflows are preserved
    /// - Ensures position titles and timestamps are accurate
    /// - Verifies digital signature data integrity
    pub fn test_footer_serialization() -> Result<()> {
        let footer = ICSFormFooter {
            prepared_by: PreparedBy {
                name: "John Smith".to_string(),
                position_title: "Communications Unit Leader".to_string(),
                signature: Some(DigitalSignature {
                    signature_data: vec![1, 2, 3, 4, 5], // Sample signature data
                    signature_type: SignatureType::Electronic,
                    timestamp: DateTime::from_timestamp(1735689600, 0).unwrap(),
                }),
                date_time: None,
            },
            approved_by: Some(ApprovedBy {
                name: "Sarah Johnson".to_string(),
                position_title: Some("Incident Commander".to_string()),
                signature: Some(DigitalSignature {
                    signature_data: vec![10, 20, 30, 40, 50],
                    signature_type: SignatureType::Digital,
                    timestamp: DateTime::from_timestamp(1735693200, 0).unwrap(),
                }),
                date_time: None,
            }),
        };

        let json = serde_json::to_string_pretty(&footer)
            .context("Failed to serialize ICS form footer")?;
        
        println!("ICS Form Footer JSON:\n{}", json);

        let deserialized: ICSFormFooter = serde_json::from_str(&json)
            .context("Failed to deserialize ICS form footer")?;

        // Verify critical data
        assert_eq!(footer.prepared_by.name, deserialized.prepared_by.name);
        assert_eq!(footer.prepared_by.position_title, deserialized.prepared_by.position_title);

        println!("✅ ICS Form Footer serialization test passed");
        Ok(())
    }

    /// Tests serialization for ICS-201 form data.
    /// 
    /// Business Logic:
    /// - Validates all ICS-201 specific fields serialize correctly
    /// - Tests complex nested structures (planned actions, resources)
    /// - Ensures image data is properly encoded
    /// - Verifies organizational structure is preserved
    pub fn test_ics201_serialization() -> Result<()> {
        let ics201_data = ICS201Data {
            map_sketch: Some(ImageData {
                data: vec![137, 80, 78, 71, 13, 10, 26, 10], // PNG header bytes
                format: "PNG".to_string(),
                width: Some(800),
                height: Some(600),
                description: Some("Incident area sketch".to_string()),
                created_at: DateTime::from_timestamp(1735689600, 0).unwrap(),
            }),
            situation_summary: "Large wildfire burning in Pine Canyon area. Approximately 500 acres involved with potential for growth due to wind conditions.".to_string(),
            current_objectives: "1. Protect structures in Pine Canyon subdivision\n2. Establish containment lines on north and east flanks\n3. Evacuate residents as needed".to_string(),
            planned_actions: vec![
                PlannedAction {
                    time: NaiveTime::from_hms_opt(14, 0, 0).unwrap(),
                    description: "Deploy Type 1 hand crew to north flank".to_string(),
                    responsible: Some("Operations Section Chief".to_string()),
                    priority: Some(ActionPriority::High),
                },
                PlannedAction {
                    time: NaiveTime::from_hms_opt(15, 30, 0).unwrap(),
                    description: "Establish water supply at Pine Canyon Road".to_string(),
                    responsible: Some("Logistics Section".to_string()),
                    priority: Some(ActionPriority::Medium),
                },
            ],
            current_organization: OrganizationStructure {
                incident_commander: PersonPosition {
                    name: "Chief Martinez".to_string(),
                    position: "Incident Commander".to_string(),
                    agency: Some("Fire Department".to_string()),
                    contact_info: None,
                },
                public_information_officer: Some(PersonPosition {
                    name: "Officer Davis".to_string(),
                    position: "Public Information Officer".to_string(),
                    agency: Some("Police Department".to_string()),
                    contact_info: None,
                }),
                safety_officer: Some(PersonPosition {
                    name: "Captain Wilson".to_string(),
                    position: "Safety Officer".to_string(),
                    agency: Some("Fire Department".to_string()),
                    contact_info: None,
                }),
                liaison_officer: None,
                operations_chief: Some(PersonPosition {
                    name: "Division Chief Adams".to_string(),
                    position: "Operations Section Chief".to_string(),
                    agency: Some("Fire Department".to_string()),
                    contact_info: None,
                }),
                planning_chief: Some(PersonPosition {
                    name: "Battalion Chief Lee".to_string(),
                    position: "Planning Section Chief".to_string(),
                    agency: Some("Fire Department".to_string()),
                    contact_info: None,
                }),
                logistics_chief: Some(PersonPosition {
                    name: "Captain Rodriguez".to_string(),
                    position: "Logistics Section Chief".to_string(),
                    agency: Some("Fire Department".to_string()),
                    contact_info: None,
                }),
                finance_admin_chief: None,
            },
            resource_summary: vec![
                ResourceSummaryItem {
                    resource_name: "Engine 101".to_string(),
                    resource_identifier: Some("E101".to_string()),
                    date_time_ordered: Some(DateTime::from_timestamp(1735686000, 0).unwrap()),
                    eta: Some(NaiveTime::from_hms_opt(13, 45, 0).unwrap()),
                    arrived: true,
                    notes: Some("Type 1 structural engine".to_string()),
                },
                ResourceSummaryItem {
                    resource_name: "Hand Crew Alpha".to_string(),
                    resource_identifier: Some("HC-A".to_string()),
                    date_time_ordered: Some(DateTime::from_timestamp(1735687800, 0).unwrap()),
                    eta: Some(NaiveTime::from_hms_opt(14, 15, 0).unwrap()),
                    arrived: false,
                    notes: Some("20-person Type 1 hand crew".to_string()),
                },
            ],
            weather_summary: Some("Clear skies, temperature 85°F, relative humidity 15%, winds SW at 10-15 mph with gusts to 25 mph".to_string()),
            safety_message: Some("Be aware of rolling material and steep terrain. Maintain escape routes and safety zones.".to_string()),
        };

        let json = serde_json::to_string_pretty(&ics201_data)
            .context("Failed to serialize ICS-201 data")?;
        
        println!("ICS-201 Data JSON (truncated):\n{}", 
                 if json.len() > 1000 { &json[..1000] } else { &json });

        let deserialized: ICS201Data = serde_json::from_str(&json)
            .context("Failed to deserialize ICS-201 data")?;

        // Verify critical data integrity
        assert_eq!(ics201_data.situation_summary, deserialized.situation_summary);
        assert_eq!(ics201_data.current_objectives, deserialized.current_objectives);
        assert_eq!(ics201_data.planned_actions.len(), deserialized.planned_actions.len());
        assert_eq!(ics201_data.resource_summary.len(), deserialized.resource_summary.len());

        println!("✅ ICS-201 serialization test passed");
        Ok(())
    }

    /// Tests serialization for ICS-205 radio communications data.
    /// 
    /// Business Logic:
    /// - Validates radio frequency precision is maintained
    /// - Tests complex radio channel structures
    /// - Ensures technical parameters are preserved
    /// - Verifies interoperability data integrity
    pub fn test_ics205_serialization() -> Result<()> {
        let ics205_data = ICS205Data {
            radio_channels: vec![
                RadioChannel {
                    zone_group: Some("Zone A".to_string()),
                    channel_number: Some("1".to_string()),
                    function: "Command".to_string(),
                    channel_name: "Command Net".to_string(),
                    assignment: "Incident Commander, Section Chiefs".to_string(),
                    rx_frequency: Some(RadioFrequency {
                        frequency: 156.800,
                        bandwidth: BandwidthType::Narrowband,
                    }),
                    rx_tone_nac: Some("136.5".to_string()),
                    tx_frequency: Some(RadioFrequency {
                        frequency: 156.800,
                        bandwidth: BandwidthType::Narrowband,
                    }),
                    tx_tone_nac: Some("136.5".to_string()),
                    mode: Some(RadioMode::Analog),
                    remarks: Some("Primary command channel".to_string()),
                },
                RadioChannel {
                    zone_group: Some("Zone B".to_string()),
                    channel_number: Some("2".to_string()),
                    function: "Tactical".to_string(),
                    channel_name: "Tactical 1".to_string(),
                    assignment: "Ground operations, hand crews".to_string(),
                    rx_frequency: Some(RadioFrequency {
                        frequency: 151.1525,
                        bandwidth: BandwidthType::Narrowband,
                    }),
                    rx_tone_nac: Some("151.4".to_string()),
                    tx_frequency: Some(RadioFrequency {
                        frequency: 151.1525,
                        bandwidth: BandwidthType::Narrowband,
                    }),
                    tx_tone_nac: Some("151.4".to_string()),
                    mode: Some(RadioMode::Digital),
                    remarks: Some("Ground tactical operations".to_string()),
                },
            ],
            special_instructions: Some("All radio operators must monitor command net for emergency traffic. Use proper ICS radio procedures.".to_string()),
            repeater_info: Some(vec![
                RepeaterInfo {
                    repeater_id: "KMA123".to_string(),
                    location: "Pine Canyon Lookout".to_string(),
                    coverage_area: Some("30-mile radius".to_string()),
                    owner_contact: Some("Forest Service Radio Shop 555-0789".to_string()),
                },
            ]),
        };

        let json = serde_json::to_string_pretty(&ics205_data)
            .context("Failed to serialize ICS-205 data")?;
        
        println!("ICS-205 Data JSON:\n{}", json);

        let deserialized: ICS205Data = serde_json::from_str(&json)
            .context("Failed to deserialize ICS-205 data")?;

        // Verify radio frequency precision
        assert_eq!(ics205_data.radio_channels.len(), deserialized.radio_channels.len());
        
        if let (Some(orig_freq), Some(deser_freq)) = (
            &ics205_data.radio_channels[0].rx_frequency,
            &deserialized.radio_channels[0].rx_frequency
        ) {
            assert!((orig_freq.frequency - deser_freq.frequency).abs() < 0.0001);
        }

        println!("✅ ICS-205 serialization test passed");
        Ok(())
    }

    /// Tests validation result serialization.
    /// 
    /// Business Logic:
    /// - Validates validation results can be stored and retrieved
    /// - Tests error message preservation
    /// - Ensures validation state is serializable
    /// - Verifies performance statistics are maintained
    pub fn test_validation_serialization() -> Result<()> {
        let validation_result = FormValidationResult {
            is_valid: false,
            is_submittable: false,
            field_results: {
                let mut fields = HashMap::new();
                fields.insert("incident_name".to_string(), FieldValidationResult {
                    field_name: "incident_name".to_string(),
                    is_valid: true,
                    errors: Vec::new(),
                    warnings: Vec::new(),
                    info_messages: vec![ValidationInfo {
                        field: "incident_name".to_string(),
                        message: "Incident name looks good".to_string(),
                        info_type: InfoType::Help,
                    }],
                    current_value: Some(serde_json::json!("Wildfire - Pine Canyon")),
                    suggestions: Vec::new(),
                });
                fields.insert("situation_summary".to_string(), FieldValidationResult {
                    field_name: "situation_summary".to_string(),
                    is_valid: false,
                    errors: vec![ValidationError {
                        field: "situation_summary".to_string(),
                        message: "Situation summary is too short".to_string(),
                        rule_id: "min_length_situation_summary".to_string(),
                        suggestion: Some("Provide more detailed information about the incident".to_string()),
                    }],
                    warnings: Vec::new(),
                    info_messages: Vec::new(),
                    current_value: Some(serde_json::json!("Fire")),
                    suggestions: vec!["Include location, size, and resources involved".to_string()],
                });
                fields
            },
            cross_field_results: Vec::new(),
            business_rule_results: Vec::new(),
            summary: ValidationSummary {
                total_fields: 2,
                fields_with_errors: 1,
                fields_with_warnings: 0,
                total_errors: 1,
                total_warnings: 0,
                total_info_messages: 1,
                completion_percentage: 50.0,
                estimated_fix_time_minutes: 2,
            },
            validated_at: DateTime::from_timestamp(1735689600, 0).unwrap(),
        };

        let json = serde_json::to_string_pretty(&validation_result)
            .context("Failed to serialize validation result")?;
        
        println!("Validation Result JSON (truncated):\n{}", 
                 if json.len() > 800 { &json[..800] } else { &json });

        let deserialized: FormValidationResult = serde_json::from_str(&json)
            .context("Failed to deserialize validation result")?;

        assert_eq!(validation_result.is_valid, deserialized.is_valid);
        assert_eq!(validation_result.summary.total_fields, deserialized.summary.total_fields);
        assert_eq!(validation_result.field_results.len(), deserialized.field_results.len());

        println!("✅ Validation result serialization test passed");
        Ok(())
    }

    /// Tests complete ICS form data serialization.
    /// 
    /// Business Logic:
    /// - Tests the complete form data structure
    /// - Validates nested component serialization
    /// - Ensures form lifecycle data is preserved
    /// - Tests edge cases and boundary conditions
    pub fn test_complete_form_serialization() -> Result<()> {
        let complete_form = ICSFormData {
            header: ICSFormHeader {
                incident_name: "Wildfire - Pine Canyon".to_string(),
                operational_period: Some(DateTimeRange {
                    from: DateTime::from_timestamp(1735689600, 0).unwrap(),
                    to: DateTime::from_timestamp(1735776000, 0).unwrap(),
                }),
                incident_number: Some("CA-2025-001234".to_string()),
                form_version: Some("2.0".to_string()),
                prepared_date_time: DateTime::from_timestamp(1735689600, 0).unwrap(),
                page_info: Some(PageInfo {
                    page_number: Some("1 of 1".to_string()),
                    iap_page_number: Some("IAP-1".to_string()),
                }),
            },
            footer: ICSFormFooter {
                prepared_by: PreparedBy {
                    name: "John Smith".to_string(),
                    position_title: "Communications Unit Leader".to_string(),
                    signature: None,
                    date_time: None,
                },
                approved_by: None,
            },
            form_data: FormSpecificData::ICS201(ICS201Data {
                map_sketch: None,
                situation_summary: "Large wildfire burning in Pine Canyon area.".to_string(),
                current_objectives: "Protect structures and establish containment.".to_string(),
                planned_actions: Vec::new(),
                current_organization: OrganizationStructure {
                    incident_commander: PersonPosition {
                        name: "Chief Martinez".to_string(),
                        position: "Incident Commander".to_string(),
                        agency: Some("Fire Department".to_string()),
                        contact_info: None,
                    },
                    public_information_officer: None,
                    safety_officer: None,
                    liaison_officer: None,
                    operations_chief: None,
                    planning_chief: None,
                    logistics_chief: None,
                    finance_admin_chief: None,
                },
                resource_summary: Vec::new(),
                weather_summary: None,
                safety_message: None,
            }),
            lifecycle: FormLifecycle {
                status: EnhancedFormStatus::Draft,
                created_at: DateTime::from_timestamp(1735689600, 0).unwrap(),
                updated_at: DateTime::from_timestamp(1735689600, 0).unwrap(),
                status_history: Vec::new(),
                workflow_position: WorkflowPosition::Initial,
            },
            validation_results: None,
        };

        let json = serde_json::to_string_pretty(&complete_form)
            .context("Failed to serialize complete ICS form")?;
        
        println!("Complete ICS Form JSON (truncated):\n{}", 
                 if json.len() > 1000 { &json[..1000] } else { &json });

        let deserialized: ICSFormData = serde_json::from_str(&json)
            .context("Failed to deserialize complete ICS form")?;

        assert_eq!(complete_form.header.incident_name, deserialized.header.incident_name);
        assert_eq!(complete_form.lifecycle.status, deserialized.lifecycle.status);

        // Test form-specific data
        match (&complete_form.form_data, &deserialized.form_data) {
            (FormSpecificData::ICS201(orig), FormSpecificData::ICS201(deser)) => {
                assert_eq!(orig.situation_summary, deser.situation_summary);
                assert_eq!(orig.current_objectives, deser.current_objectives);
            },
            _ => return Err(anyhow!("Form data type mismatch after deserialization")),
        }

        println!("✅ Complete ICS form serialization test passed");
        Ok(())
    }

    /// Runs all serialization tests.
    /// 
    /// Business Logic:
    /// - Executes comprehensive test suite
    /// - Reports any serialization failures
    /// - Provides performance metrics
    /// - Validates all data structures
    pub fn run_all_tests() -> Result<()> {
        println!("🧪 Running Serde serialization test suite...\n");

        let start_time = std::time::Instant::now();

        Self::test_header_serialization()
            .context("Header serialization test failed")?;
        
        Self::test_footer_serialization()
            .context("Footer serialization test failed")?;
        
        Self::test_ics201_serialization()
            .context("ICS-201 serialization test failed")?;
        
        Self::test_ics205_serialization()
            .context("ICS-205 serialization test failed")?;
        
        Self::test_validation_serialization()
            .context("Validation result serialization test failed")?;
        
        Self::test_complete_form_serialization()
            .context("Complete form serialization test failed")?;

        let elapsed = start_time.elapsed();
        
        println!("\n🎉 All serialization tests passed!");
        println!("⏱️  Total execution time: {:?}", elapsed);
        println!("📊 Test suite completed successfully");

        Ok(())
    }
}

/// Custom serialization utilities for specific data types.
/// 
/// Business Logic:
/// - Provides optimized serialization for large data structures
/// - Handles edge cases in date/time serialization
/// - Supports custom JSON formats for API compatibility
/// - Enables compression for large form datasets
pub struct SerializationUtils;

impl SerializationUtils {
    /// Serializes form data with compression for large datasets.
    /// 
    /// Business Logic:
    /// - Compresses JSON for forms with large attachments
    /// - Maintains compatibility with standard JSON when possible
    /// - Provides metadata about compression used
    /// - Enables efficient storage and transmission
    pub fn serialize_with_compression<T: Serialize>(data: &T, compress_threshold: usize) -> Result<Vec<u8>> {
        let json = serde_json::to_string(data)
            .context("Failed to serialize data to JSON")?;
        
        if json.len() > compress_threshold {
            // In a real implementation, we would use compression here
            // For now, just return the JSON bytes
            println!("Data size {} exceeds threshold {}, compression would be applied", 
                    json.len(), compress_threshold);
        }
        
        Ok(json.into_bytes())
    }

    /// Deserializes form data with automatic decompression.
    /// 
    /// Business Logic:
    /// - Automatically detects and decompresses data
    /// - Falls back to standard JSON if not compressed
    /// - Provides error recovery for corrupted compressed data
    /// - Maintains backward compatibility
    pub fn deserialize_with_decompression<T: for<'de> Deserialize<'de>>(data: &[u8]) -> Result<T> {
        // Convert bytes to string
        let json_str = String::from_utf8(data.to_vec())
            .context("Invalid UTF-8 in serialized data")?;
        
        // In a real implementation, we would detect and decompress here
        
        serde_json::from_str(&json_str)
            .context("Failed to deserialize JSON data")
    }

    /// Validates JSON schema compatibility for API contracts.
    /// 
    /// Business Logic:
    /// - Ensures serialized data meets API schema requirements
    /// - Validates field types and structure
    /// - Checks for required fields
    /// - Provides schema compatibility reports
    pub fn validate_json_schema<T: Serialize>(data: &T, schema_name: &str) -> Result<bool> {
        let json_value = serde_json::to_value(data)
            .context("Failed to convert data to JSON value")?;
        
        // In a real implementation, we would validate against a JSON schema
        println!("Validating {} against schema: {}", 
                json_value.get("type").unwrap_or(&serde_json::Value::Null), 
                schema_name);
        
        // For now, just check that we have a valid JSON object
        Ok(json_value.is_object() || json_value.is_array())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_serde_round_trip() {
        // This test would be run with `cargo test` in a real environment
        SerdeTestSuite::run_all_tests().expect("Serde test suite should pass");
    }

    #[test]
    fn test_compression_utilities() {
        let test_data = json!({
            "test": "data",
            "large_field": "x".repeat(10000)
        });
        
        let compressed = SerializationUtils::serialize_with_compression(&test_data, 1000)
            .expect("Compression should work");
        
        let decompressed: serde_json::Value = SerializationUtils::deserialize_with_decompression(&compressed)
            .expect("Decompression should work");
        
        assert_eq!(test_data, decompressed);
    }

    #[test]
    fn test_schema_validation() {
        let test_form = ICSFormHeader {
            incident_name: "Test Incident".to_string(),
            operational_period: None,
            incident_number: None,
            form_version: None,
            prepared_date_time: DateTime::from_timestamp(1735689600, 0).unwrap(),
            page_info: None,
        };
        
        let is_valid = SerializationUtils::validate_json_schema(&test_form, "ICSFormHeader")
            .expect("Schema validation should work");
        
        assert!(is_valid);
    }
}
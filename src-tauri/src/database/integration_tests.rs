/*!
 * Integration Tests for Database Operations
 * 
 * Following MANDATORY.md: Simple integration tests for emergency responder workflows.
 * Tests the complete database workflow from initialization to form management.
 * These tests verify that all components work together for the core use cases.
 */

#[cfg(test)]
mod integration_tests {
    use super::super::simple::*;
    use tempfile::NamedTempFile;
    use tokio::runtime::Runtime;

    /// Test complete form lifecycle: create, read, update, delete
    #[test]
    fn test_complete_form_lifecycle() {
        let rt = Runtime::new().unwrap();
        rt.block_on(async {
            // Create temporary database
            let temp_file = NamedTempFile::new().unwrap();
            let db_path = temp_file.path().to_str().unwrap();
            
            // Initialize database
            init_database(db_path).await.expect("Database initialization failed");
            
            // Test 1: Save a form
            let form_id = save_form(
                "Test Emergency Response".to_string(),
                "ICS-201".to_string(),
                r#"{"incident_name": "Test Emergency Response", "location": "Main Street"}"#.to_string()
            ).await.expect("Failed to save form");
            
            assert!(form_id > 0, "Form ID should be positive");
            
            // Test 2: Read the form back
            let retrieved_form = get_form(form_id).await.expect("Failed to get form");
            assert!(retrieved_form.is_some(), "Form should exist");
            
            let form = retrieved_form.unwrap();
            assert_eq!(form.incident_name, "Test Emergency Response");
            assert_eq!(form.form_type, "ICS-201");
            assert_eq!(form.status, "draft"); // Default status
            
            // Test 3: Update the form
            let updated_data = r#"{"incident_name": "Test Emergency Response", "location": "Updated Location"}"#;
            update_form(form_id, updated_data.to_string()).await.expect("Failed to update form");
            
            let updated_form = get_form(form_id).await.expect("Failed to get updated form");
            assert!(updated_form.is_some());
            assert!(updated_form.unwrap().form_data.contains("Updated Location"));
            
            // Test 4: Delete the form
            let deleted = delete_form(form_id).await.expect("Failed to delete form");
            assert!(deleted, "Form should be deleted");
            
            let deleted_form = get_form(form_id).await.expect("Failed to check deleted form");
            assert!(deleted_form.is_none(), "Form should not exist after deletion");
        });
    }

    /// Test search functionality with multiple forms
    #[test]
    fn test_search_workflow() {
        let rt = Runtime::new().unwrap();
        rt.block_on(async {
            let temp_file = NamedTempFile::new().unwrap();
            let db_path = temp_file.path().to_str().unwrap();
            
            init_database(db_path).await.expect("Database initialization failed");
            
            // Create multiple forms for different incidents
            let fire_id = save_form(
                "Fire Response Alpha".to_string(),
                "ICS-201".to_string(),
                r#"{"incident_name": "Fire Response Alpha"}"#.to_string()
            ).await.expect("Failed to save fire form");
            
            let medical_id = save_form(
                "Medical Emergency Beta".to_string(),
                "ICS-202".to_string(),
                r#"{"incident_objectives": "Stabilize patient"}"#.to_string()
            ).await.expect("Failed to save medical form");
            
            let search_id = save_form(
                "Search and Rescue Gamma".to_string(),
                "ICS-201".to_string(),
                r#"{"incident_name": "Search and Rescue Gamma"}"#.to_string()
            ).await.expect("Failed to save search form");
            
            // Test search by incident name
            let fire_results = search_forms(Some("Fire".to_string())).await.expect("Fire search failed");
            assert_eq!(fire_results.len(), 1);
            assert_eq!(fire_results[0].id, fire_id);
            
            let medical_results = search_forms(Some("Medical".to_string())).await.expect("Medical search failed");
            assert_eq!(medical_results.len(), 1);
            assert_eq!(medical_results[0].id, medical_id);
            
            // Test search with no results
            let no_results = search_forms(Some("NonExistent".to_string())).await.expect("No results search failed");
            assert_eq!(no_results.len(), 0);
            
            // Test list all forms
            let all_forms = list_all_forms().await.expect("List all failed");
            assert_eq!(all_forms.len(), 3);
            
            // Verify all forms are returned
            let form_ids: Vec<i64> = all_forms.iter().map(|f| f.id).collect();
            assert!(form_ids.contains(&fire_id));
            assert!(form_ids.contains(&medical_id));
            assert!(form_ids.contains(&search_id));
        });
    }

    /// Test form status transitions
    #[test]
    fn test_status_transitions() {
        let rt = Runtime::new().unwrap();
        rt.block_on(async {
            let temp_file = NamedTempFile::new().unwrap();
            let db_path = temp_file.path().to_str().unwrap();
            
            init_database(db_path).await.expect("Database initialization failed");
            
            // Create a form (starts as draft)
            let form_id = save_form(
                "Status Test Incident".to_string(),
                "ICS-201".to_string(),
                r#"{"incident_name": "Status Test Incident"}"#.to_string()
            ).await.expect("Failed to save form");
            
            // Test initial status
            let form = get_form(form_id).await.expect("Failed to get form").unwrap();
            assert_eq!(form.status, "draft");
            
            // Test valid status transitions
            update_form_status(form_id, "completed".to_string()).await.expect("Failed to update to completed");
            let form = get_form(form_id).await.expect("Failed to get form").unwrap();
            assert_eq!(form.status, "completed");
            
            update_form_status(form_id, "final".to_string()).await.expect("Failed to update to final");
            let form = get_form(form_id).await.expect("Failed to get form").unwrap();
            assert_eq!(form.status, "final");
            
            update_form_status(form_id, "archived".to_string()).await.expect("Failed to update to archived");
            let form = get_form(form_id).await.expect("Failed to get form").unwrap();
            assert_eq!(form.status, "archived");
            
            // Test invalid status
            let invalid_result = update_form_status(form_id, "invalid_status".to_string()).await;
            assert!(invalid_result.is_err(), "Invalid status should fail");
        });
    }

    /// Test form validation during save workflow
    #[test]
    fn test_validation_integration() {
        let rt = Runtime::new().unwrap();
        rt.block_on(async {
            let temp_file = NamedTempFile::new().unwrap();
            let db_path = temp_file.path().to_str().unwrap();
            
            init_database(db_path).await.expect("Database initialization failed");
            
            // Test invalid incident name (empty)
            let result = save_form(
                "".to_string(),
                "ICS-201".to_string(),
                r#"{"incident_name": "Test"}"#.to_string()
            ).await;
            assert!(result.is_err(), "Empty incident name should fail");
            
            // Test invalid form type
            let result = save_form(
                "Valid Incident".to_string(),
                "INVALID-FORM".to_string(),
                r#"{"incident_name": "Valid Incident"}"#.to_string()
            ).await;
            assert!(result.is_err(), "Invalid form type should fail");
            
            // Test invalid JSON
            let result = save_form(
                "Valid Incident".to_string(),
                "ICS-201".to_string(),
                "invalid json".to_string()
            ).await;
            assert!(result.is_err(), "Invalid JSON should fail");
            
            // Test ICS-201 business rule validation
            let result = save_form(
                "Valid Incident".to_string(),
                "ICS-201".to_string(),
                r#"{"wrong_field": "value"}"#.to_string()
            ).await;
            assert!(result.is_err(), "ICS-201 without incident_name field should fail");
            
            // Test valid form saves successfully
            let result = save_form(
                "Valid Incident".to_string(),
                "ICS-201".to_string(),
                r#"{"incident_name": "Valid Incident"}"#.to_string()
            ).await;
            assert!(result.is_ok(), "Valid form should save successfully");
        });
    }

    /// Test concurrent form operations (emergency responder might use multiple devices)
    #[test]
    fn test_concurrent_operations() {
        let rt = Runtime::new().unwrap();
        rt.block_on(async {
            let temp_file = NamedTempFile::new().unwrap();
            let db_path = temp_file.path().to_str().unwrap();
            
            init_database(db_path).await.expect("Database initialization failed");
            
            // Create forms concurrently (simulating multiple emergency responders)
            let handles = vec![
                tokio::spawn(save_form(
                    "Concurrent Incident 1".to_string(),
                    "ICS-201".to_string(),
                    r#"{"incident_name": "Concurrent Incident 1"}"#.to_string()
                )),
                tokio::spawn(save_form(
                    "Concurrent Incident 2".to_string(),
                    "ICS-202".to_string(),
                    r#"{"incident_objectives": "Handle emergency"}"#.to_string()
                )),
                tokio::spawn(save_form(
                    "Concurrent Incident 3".to_string(),
                    "ICS-201".to_string(),
                    r#"{"incident_name": "Concurrent Incident 3"}"#.to_string()
                )),
            ];
            
            // Wait for all forms to be saved
            let mut form_ids = Vec::new();
            for handle in handles {
                let form_id = handle.await.expect("Task failed").expect("Save failed");
                form_ids.push(form_id);
            }
            
            // Verify all forms were saved with unique IDs
            assert_eq!(form_ids.len(), 3);
            form_ids.sort();
            form_ids.dedup();
            assert_eq!(form_ids.len(), 3, "All form IDs should be unique");
            
            // Verify all forms can be retrieved
            for form_id in form_ids {
                let form = get_form(form_id).await.expect("Failed to get form");
                assert!(form.is_some(), "All forms should be retrievable");
            }
        });
    }

    /// Test edge cases and error recovery
    #[test]
    fn test_error_recovery() {
        let rt = Runtime::new().unwrap();
        rt.block_on(async {
            let temp_file = NamedTempFile::new().unwrap();
            let db_path = temp_file.path().to_str().unwrap();
            
            init_database(db_path).await.expect("Database initialization failed");
            
            // Test operations on non-existent form
            let non_existent_result = get_form(99999).await.expect("Get non-existent form failed");
            assert!(non_existent_result.is_none());
            
            let update_result = update_form(99999, r#"{"test": "data"}"#.to_string()).await;
            // Update of non-existent form should complete without error (SQLite behavior)
            assert!(update_result.is_ok());
            
            let delete_result = delete_form(99999).await.expect("Delete non-existent form failed");
            assert!(!delete_result, "Deleting non-existent form should return false");
            
            // Test extremely long incident name
            let long_name = "A".repeat(200);
            let long_name_result = save_form(
                long_name,
                "ICS-201".to_string(),
                r#"{"incident_name": "Test"}"#.to_string()
            ).await;
            assert!(long_name_result.is_err(), "Extremely long incident name should fail");
        });
    }
}
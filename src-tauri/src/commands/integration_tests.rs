/*!
 * Integration Tests for Tauri Commands
 * 
 * Following MANDATORY.md: Simple integration tests for command interface.
 * Tests that frontend can communicate with backend through Tauri commands.
 * These tests verify the complete request/response cycle emergency responders use.
 */

#[cfg(test)]
mod integration_tests {
    use super::super::simple_commands::*;
    use super::super::super::database::simple;
    use tempfile::NamedTempFile;
    use tokio::runtime::Runtime;

    /// Test complete save and get form workflow through commands
    #[test]
    fn test_command_save_and_get_workflow() {
        let rt = Runtime::new().unwrap();
        rt.block_on(async {
            // Initialize database for testing
            let temp_file = NamedTempFile::new().unwrap();
            let db_path = temp_file.path().to_str().unwrap();
            simple::init_database(db_path).await.expect("Database init failed");
            
            // Test save command
            let form_id = save_form(
                "Command Test Incident".to_string(),
                "ICS-201".to_string(),
                r#"{"incident_name": "Command Test Incident", "location": "Test Location"}"#.to_string()
            ).await.expect("Save command failed");
            
            assert!(form_id > 0, "Command should return valid form ID");
            
            // Test get command
            let retrieved_form = get_form(form_id).await.expect("Get command failed");
            assert!(retrieved_form.is_some(), "Get command should return form");
            
            let form = retrieved_form.unwrap();
            assert_eq!(form.incident_name, "Command Test Incident");
            assert_eq!(form.form_type, "ICS-201");
            assert!(form.form_data.contains("Test Location"));
        });
    }

    /// Test search command workflow
    #[test]
    fn test_command_search_workflow() {
        let rt = Runtime::new().unwrap();
        rt.block_on(async {
            let temp_file = NamedTempFile::new().unwrap();
            let db_path = temp_file.path().to_str().unwrap();
            simple::init_database(db_path).await.expect("Database init failed");
            
            // Create test forms
            let _fire_id = save_form(
                "Fire Emergency Alpha".to_string(),
                "ICS-201".to_string(),
                r#"{"incident_name": "Fire Emergency Alpha"}"#.to_string()
            ).await.expect("Save fire form failed");
            
            let _medical_id = save_form(
                "Medical Emergency Beta".to_string(),
                "ICS-202".to_string(),
                r#"{"incident_objectives": "Patient care"}"#.to_string()
            ).await.expect("Save medical form failed");
            
            // Test search command
            let search_results = search_forms(Some("Fire".to_string())).await.expect("Search command failed");
            assert_eq!(search_results.len(), 1);
            assert_eq!(search_results[0].incident_name, "Fire Emergency Alpha");
            
            // Test search with no results
            let no_results = search_forms(Some("NonExistent".to_string())).await.expect("Search command failed");
            assert_eq!(no_results.len(), 0);
            
            // Test get all forms
            let all_forms = get_all_forms().await.expect("Get all command failed");
            assert_eq!(all_forms.len(), 2);
        });
    }

    /// Test update command workflow
    #[test]
    fn test_command_update_workflow() {
        let rt = Runtime::new().unwrap();
        rt.block_on(async {
            let temp_file = NamedTempFile::new().unwrap();
            let db_path = temp_file.path().to_str().unwrap();
            simple::init_database(db_path).await.expect("Database init failed");
            
            // Create form
            let form_id = save_form(
                "Update Test Incident".to_string(),
                "ICS-201".to_string(),
                r#"{"incident_name": "Update Test Incident", "status": "initial"}"#.to_string()
            ).await.expect("Save failed");
            
            // Test update command
            update_form(
                form_id,
                r#"{"incident_name": "Update Test Incident", "status": "updated"}"#.to_string()
            ).await.expect("Update command failed");
            
            // Verify update
            let updated_form = get_form(form_id).await.expect("Get after update failed");
            assert!(updated_form.is_some());
            assert!(updated_form.unwrap().form_data.contains("updated"));
        });
    }

    /// Test status management commands
    #[test]
    fn test_command_status_workflow() {
        let rt = Runtime::new().unwrap();
        rt.block_on(async {
            let temp_file = NamedTempFile::new().unwrap();
            let db_path = temp_file.path().to_str().unwrap();
            simple::init_database(db_path).await.expect("Database init failed");
            
            // Create form
            let form_id = save_form(
                "Status Test Incident".to_string(),
                "ICS-201".to_string(),
                r#"{"incident_name": "Status Test Incident"}"#.to_string()
            ).await.expect("Save failed");
            
            // Test status update command
            update_form_status(form_id, "completed".to_string()).await.expect("Status update failed");
            
            // Test get available transitions
            let transitions = get_available_transitions(form_id).await.expect("Get transitions failed");
            assert!(transitions.contains(&"final".to_string()));
            assert!(transitions.contains(&"archived".to_string()));
            
            // Test can edit check
            let can_edit = can_edit_form(form_id).await.expect("Can edit check failed");
            assert!(can_edit, "Should be able to edit completed form");
        });
    }

    /// Test delete command workflow
    #[test]
    fn test_command_delete_workflow() {
        let rt = Runtime::new().unwrap();
        rt.block_on(async {
            let temp_file = NamedTempFile::new().unwrap();
            let db_path = temp_file.path().to_str().unwrap();
            simple::init_database(db_path).await.expect("Database init failed");
            
            // Create form
            let form_id = save_form(
                "Delete Test Incident".to_string(),
                "ICS-201".to_string(),
                r#"{"incident_name": "Delete Test Incident"}"#.to_string()
            ).await.expect("Save failed");
            
            // Verify form exists
            let form_before = get_form(form_id).await.expect("Get before delete failed");
            assert!(form_before.is_some());
            
            // Test delete command
            let deleted = delete_form(form_id).await.expect("Delete command failed");
            assert!(deleted, "Delete should return true");
            
            // Verify form is gone
            let form_after = get_form(form_id).await.expect("Get after delete failed");
            assert!(form_after.is_none(), "Form should not exist after delete");
        });
    }

    /// Test validation through commands
    #[test]
    fn test_command_validation_workflow() {
        let rt = Runtime::new().unwrap();
        rt.block_on(async {
            let temp_file = NamedTempFile::new().unwrap();
            let db_path = temp_file.path().to_str().unwrap();
            simple::init_database(db_path).await.expect("Database init failed");
            
            // Test save with invalid data through command
            let invalid_result = save_form(
                "".to_string(), // Empty incident name
                "ICS-201".to_string(),
                r#"{"incident_name": "Test"}"#.to_string()
            ).await;
            assert!(invalid_result.is_err(), "Command should reject invalid data");
            
            // Test save with invalid form type
            let invalid_form_type = save_form(
                "Valid Incident".to_string(),
                "INVALID-TYPE".to_string(),
                r#"{"incident_name": "Valid Incident"}"#.to_string()
            ).await;
            assert!(invalid_form_type.is_err(), "Command should reject invalid form type");
            
            // Test save with invalid JSON
            let invalid_json = save_form(
                "Valid Incident".to_string(),
                "ICS-201".to_string(),
                "invalid json".to_string()
            ).await;
            assert!(invalid_json.is_err(), "Command should reject invalid JSON");
        });
    }

    /// Test error handling in commands
    #[test]
    fn test_command_error_handling() {
        let rt = Runtime::new().unwrap();
        rt.block_on(async {
            let temp_file = NamedTempFile::new().unwrap();
            let db_path = temp_file.path().to_str().unwrap();
            simple::init_database(db_path).await.expect("Database init failed");
            
            // Test operations on non-existent forms
            let non_existent_form = get_form(99999).await.expect("Get non-existent should not error");
            assert!(non_existent_form.is_none());
            
            let delete_non_existent = delete_form(99999).await.expect("Delete non-existent should not error");
            assert!(!delete_non_existent);
            
            // Test invalid status updates
            let invalid_status = update_form_status(99999, "invalid_status".to_string()).await;
            assert!(invalid_status.is_err(), "Invalid status should error");
        });
    }
}
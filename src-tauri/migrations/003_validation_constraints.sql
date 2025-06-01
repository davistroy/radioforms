-- RadioForms Database Validation Constraints - Migration 003
-- 
-- This migration adds comprehensive database-level validation constraints
-- to ensure data integrity at the storage level. These constraints work
-- in conjunction with the Rust validation engine to provide multiple
-- layers of data protection.
-- 
-- Business Logic:
-- - Database constraints as final data integrity check
-- - Prevent invalid data from being stored even if validation is bypassed
-- - Support for complex business rules at the database level
-- - Consistent constraint enforcement across all data access patterns

-- Add CHECK constraints to forms table
-- These constraints provide last-line defense against invalid data

-- Incident name must be between 3-100 characters and not just whitespace
ALTER TABLE forms ADD CONSTRAINT chk_incident_name_valid 
    CHECK (LENGTH(TRIM(incident_name)) >= 3 AND LENGTH(incident_name) <= 100);

-- Form type must be valid ICS form identifier
ALTER TABLE forms ADD CONSTRAINT chk_form_type_valid 
    CHECK (form_type IN (
        'ICS-201', 'ICS-202', 'ICS-203', 'ICS-204', 'ICS-205', 'ICS-205A',
        'ICS-206', 'ICS-207', 'ICS-208', 'ICS-209', 'ICS-210', 'ICS-211',
        'ICS-213', 'ICS-214', 'ICS-215', 'ICS-215A', 'ICS-218', 'ICS-220',
        'ICS-221', 'ICS-225'
    ));

-- Status must be valid form status
ALTER TABLE forms ADD CONSTRAINT chk_status_valid 
    CHECK (status IN ('draft', 'completed', 'final'));

-- Priority must be valid priority level  
ALTER TABLE forms ADD CONSTRAINT chk_priority_valid 
    CHECK (priority IN ('routine', 'urgent', 'emergency'));

-- Workflow position must be valid
ALTER TABLE forms ADD CONSTRAINT chk_workflow_position_valid 
    CHECK (workflow_position IN (
        'initial', 'in_progress', 'review', 'approval', 'final', 'archived'
    ));

-- Data field must contain valid JSON
ALTER TABLE forms ADD CONSTRAINT chk_data_valid_json 
    CHECK (JSON_VALID(data));

-- Operational period validation (end must be after start)
ALTER TABLE forms ADD CONSTRAINT chk_operational_period_valid 
    CHECK (
        operational_period_start IS NULL OR 
        operational_period_end IS NULL OR 
        operational_period_end > operational_period_start
    );

-- Operational period duration cannot exceed 72 hours (ICS standard)
ALTER TABLE forms ADD CONSTRAINT chk_operational_period_duration 
    CHECK (
        operational_period_start IS NULL OR 
        operational_period_end IS NULL OR 
        (JULIANDAY(operational_period_end) - JULIANDAY(operational_period_start)) * 24 <= 72
    );

-- Approved forms must have approval information
ALTER TABLE forms ADD CONSTRAINT chk_approval_consistency 
    CHECK (
        status != 'final' OR 
        (approved_by IS NOT NULL AND approved_at IS NOT NULL)
    );

-- Page info must be valid JSON if present
ALTER TABLE forms ADD CONSTRAINT chk_page_info_valid_json 
    CHECK (page_info IS NULL OR JSON_VALID(page_info));

-- Validation results must be valid JSON if present
ALTER TABLE forms ADD CONSTRAINT chk_validation_results_valid_json 
    CHECK (validation_results IS NULL OR JSON_VALID(validation_results));

-- Form relationships constraints
ALTER TABLE form_relationships ADD CONSTRAINT chk_relationship_type_valid 
    CHECK (relationship_type IN (
        'feeds', 'requires', 'updates', 'references', 'supersedes', 'extends', 'depends_on'
    ));

ALTER TABLE form_relationships ADD CONSTRAINT chk_dependency_strength_valid 
    CHECK (dependency_strength IN ('required', 'recommended', 'optional'));

-- Prevent self-referential relationships
ALTER TABLE form_relationships ADD CONSTRAINT chk_no_self_reference 
    CHECK (source_form_id != target_form_id);

-- Form status history constraints
ALTER TABLE form_status_history ADD CONSTRAINT chk_status_history_from_valid 
    CHECK (from_status IS NULL OR from_status IN ('draft', 'completed', 'final'));

ALTER TABLE form_status_history ADD CONSTRAINT chk_status_history_to_valid 
    CHECK (to_status IN ('draft', 'completed', 'final'));

-- Status transitions must be valid (no backwards transitions except draft)
ALTER TABLE form_status_history ADD CONSTRAINT chk_status_transition_valid 
    CHECK (
        from_status IS NULL OR -- Initial status
        (from_status = 'draft' AND to_status IN ('completed', 'final')) OR
        (from_status = 'completed' AND to_status = 'final') OR
        (from_status = to_status) -- Same status allowed
    );

-- Digital signatures constraints
ALTER TABLE form_signatures ADD CONSTRAINT chk_signature_type_valid 
    CHECK (signature_type IN ('digital', 'electronic', 'handwritten', 'pin', 'biometric'));

ALTER TABLE form_signatures ADD CONSTRAINT chk_signer_name_not_empty 
    CHECK (LENGTH(TRIM(signer_name)) >= 1);

ALTER TABLE form_signatures ADD CONSTRAINT chk_signature_context_valid 
    CHECK (signature_context IS NULL OR signature_context IN (
        'prepared_by', 'approved_by', 'reviewed_by', 'authorized_by', 'witnessed_by'
    ));

ALTER TABLE form_signatures ADD CONSTRAINT chk_verification_status_valid 
    CHECK (verification_status IN ('valid', 'invalid', 'pending', 'expired'));

-- Form templates constraints
ALTER TABLE form_templates ADD CONSTRAINT chk_template_form_type_valid 
    CHECK (form_type IN (
        'ICS-201', 'ICS-202', 'ICS-203', 'ICS-204', 'ICS-205', 'ICS-205A',
        'ICS-206', 'ICS-207', 'ICS-208', 'ICS-209', 'ICS-210', 'ICS-211',
        'ICS-213', 'ICS-214', 'ICS-215', 'ICS-215A', 'ICS-218', 'ICS-220',
        'ICS-221', 'ICS-225'
    ));

ALTER TABLE form_templates ADD CONSTRAINT chk_template_data_valid_json 
    CHECK (JSON_VALID(template_data));

ALTER TABLE form_templates ADD CONSTRAINT chk_validation_rules_valid_json 
    CHECK (validation_rules IS NULL OR JSON_VALID(validation_rules));

-- Template version must follow semantic versioning pattern
ALTER TABLE form_templates ADD CONSTRAINT chk_template_version_format 
    CHECK (template_version GLOB '[0-9]*.[0-9]*' OR template_version GLOB '[0-9]*.[0-9]*.[0-9]*');

-- Validation rules constraints
ALTER TABLE validation_rules ADD CONSTRAINT chk_validation_rule_id_not_empty 
    CHECK (LENGTH(TRIM(rule_id)) >= 1);

ALTER TABLE validation_rules ADD CONSTRAINT chk_validation_rule_name_not_empty 
    CHECK (LENGTH(TRIM(rule_name)) >= 1);

ALTER TABLE validation_rules ADD CONSTRAINT chk_validation_rule_type_valid 
    CHECK (rule_type IN (
        'required', 'format', 'range', 'cross_field', 'business_rule', 
        'conditional', 'length', 'pattern', 'numeric', 'date', 'email', 'phone'
    ));

ALTER TABLE validation_rules ADD CONSTRAINT chk_validation_form_types_valid_json 
    CHECK (form_types IS NULL OR JSON_VALID(form_types));

ALTER TABLE validation_rules ADD CONSTRAINT chk_validation_fields_valid_json 
    CHECK (JSON_VALID(fields));

ALTER TABLE validation_rules ADD CONSTRAINT chk_validation_logic_valid_json 
    CHECK (JSON_VALID(validation_logic));

ALTER TABLE validation_rules ADD CONSTRAINT chk_validation_severity_valid 
    CHECK (severity IN ('error', 'warning', 'info', 'success'));

-- Export configurations constraints
ALTER TABLE export_configurations ADD CONSTRAINT chk_export_format_valid 
    CHECK (export_format IN ('pdf', 'json', 'ics_des', 'csv', 'xml', 'html', 'text'));

ALTER TABLE export_configurations ADD CONSTRAINT chk_export_form_types_valid_json 
    CHECK (form_types IS NULL OR JSON_VALID(form_types));

ALTER TABLE export_configurations ADD CONSTRAINT chk_export_template_data_valid_json 
    CHECK (template_data IS NULL OR JSON_VALID(template_data));

ALTER TABLE export_configurations ADD CONSTRAINT chk_export_field_filters_valid_json 
    CHECK (field_filters IS NULL OR JSON_VALID(field_filters));

ALTER TABLE export_configurations ADD CONSTRAINT chk_export_ics_des_config_valid_json 
    CHECK (ics_des_config IS NULL OR JSON_VALID(ics_des_config));

-- Settings table constraints
ALTER TABLE settings ADD CONSTRAINT chk_settings_key_not_empty 
    CHECK (LENGTH(TRIM(key)) >= 1);

ALTER TABLE settings ADD CONSTRAINT chk_settings_value_valid_json 
    CHECK (JSON_VALID(value));

-- Create triggers for automatic data validation and normalization

-- Trigger to normalize incident numbers for search consistency
CREATE TRIGGER trg_normalize_incident_number 
    BEFORE INSERT ON forms
    WHEN NEW.incident_number IS NOT NULL
BEGIN
    UPDATE forms SET incident_number_normalized = UPPER(TRIM(NEW.incident_number))
    WHERE rowid = NEW.rowid;
END;

CREATE TRIGGER trg_normalize_incident_number_update 
    BEFORE UPDATE ON forms
    WHEN NEW.incident_number IS NOT NULL
BEGIN
    UPDATE forms SET incident_number_normalized = UPPER(TRIM(NEW.incident_number))
    WHERE rowid = NEW.rowid;
END;

-- Trigger to automatically update timestamps
CREATE TRIGGER trg_forms_update_timestamp 
    BEFORE UPDATE ON forms
BEGIN
    UPDATE forms SET updated_at = CURRENT_TIMESTAMP WHERE rowid = NEW.rowid;
END;

CREATE TRIGGER trg_form_templates_update_timestamp 
    BEFORE UPDATE ON form_templates
BEGIN
    UPDATE form_templates SET updated_at = CURRENT_TIMESTAMP WHERE rowid = NEW.rowid;
END;

CREATE TRIGGER trg_validation_rules_update_timestamp 
    BEFORE UPDATE ON validation_rules
BEGIN
    UPDATE validation_rules SET updated_at = CURRENT_TIMESTAMP WHERE rowid = NEW.rowid;
END;

CREATE TRIGGER trg_export_configurations_update_timestamp 
    BEFORE UPDATE ON export_configurations
BEGIN
    UPDATE export_configurations SET updated_at = CURRENT_TIMESTAMP WHERE rowid = NEW.rowid;
END;

CREATE TRIGGER trg_settings_update_timestamp 
    BEFORE UPDATE ON settings
BEGIN
    UPDATE settings SET updated_at = CURRENT_TIMESTAMP WHERE rowid = NEW.rowid;
END;

-- Trigger to maintain status history
CREATE TRIGGER trg_form_status_history 
    AFTER UPDATE OF status ON forms
    WHEN OLD.status != NEW.status
BEGIN
    INSERT INTO form_status_history (
        form_id, from_status, to_status, changed_by, changed_at, workflow_position
    ) VALUES (
        NEW.id, OLD.status, NEW.status, 
        COALESCE(NEW.preparer_name, 'system'), 
        CURRENT_TIMESTAMP,
        NEW.workflow_position
    );
END;

-- Trigger to validate form data based on form type
CREATE TRIGGER trg_validate_form_data_structure 
    BEFORE INSERT ON forms
    WHEN NEW.data IS NOT NULL
BEGIN
    SELECT CASE
        -- Validate that ICS-201 forms have required situation_summary
        WHEN NEW.form_type = 'ICS-201' AND 
             (JSON_EXTRACT(NEW.data, '$.situation_summary') IS NULL OR
              LENGTH(TRIM(JSON_EXTRACT(NEW.data, '$.situation_summary'))) < 10)
        THEN RAISE(ABORT, 'ICS-201 forms require situation_summary with at least 10 characters')
        
        -- Validate that ICS-202 forms have required objectives
        WHEN NEW.form_type = 'ICS-202' AND 
             (JSON_EXTRACT(NEW.data, '$.objectives') IS NULL OR
              LENGTH(TRIM(JSON_EXTRACT(NEW.data, '$.objectives'))) < 10)
        THEN RAISE(ABORT, 'ICS-202 forms require objectives with at least 10 characters')
        
        -- Validate that ICS-205 forms have at least one radio channel
        WHEN NEW.form_type = 'ICS-205' AND 
             (JSON_EXTRACT(NEW.data, '$.radio_channels') IS NULL OR
              JSON_ARRAY_LENGTH(JSON_EXTRACT(NEW.data, '$.radio_channels')) = 0)
        THEN RAISE(ABORT, 'ICS-205 forms require at least one radio channel')
        
        -- Validate that ICS-213 forms have required message fields
        WHEN NEW.form_type = 'ICS-213' AND 
             (JSON_EXTRACT(NEW.data, '$.message') IS NULL OR
              LENGTH(TRIM(JSON_EXTRACT(NEW.data, '$.message'))) < 1)
        THEN RAISE(ABORT, 'ICS-213 forms require message content')
        
        -- Validate that ICS-214 forms have required activity log
        WHEN NEW.form_type = 'ICS-214' AND 
             (JSON_EXTRACT(NEW.data, '$.activity_log') IS NULL OR
              JSON_ARRAY_LENGTH(JSON_EXTRACT(NEW.data, '$.activity_log')) = 0)
        THEN RAISE(ABORT, 'ICS-214 forms require at least one activity log entry')
        
        ELSE 1 -- All validations passed
    END;
END;

-- Trigger to validate radio frequencies in ICS-205 forms
CREATE TRIGGER trg_validate_radio_frequencies 
    BEFORE INSERT ON forms
    WHEN NEW.form_type = 'ICS-205' AND NEW.data IS NOT NULL
BEGIN
    SELECT CASE
        WHEN EXISTS (
            SELECT 1 FROM json_each(JSON_EXTRACT(NEW.data, '$.radio_channels')) 
            WHERE JSON_EXTRACT(value, '$.rx_frequency.frequency') IS NOT NULL
            AND (
                JSON_EXTRACT(value, '$.rx_frequency.frequency') < 30.0 OR
                JSON_EXTRACT(value, '$.rx_frequency.frequency') > 3000.0
            )
        )
        THEN RAISE(ABORT, 'Radio frequencies must be between 30.0 and 3000.0 MHz')
        
        WHEN EXISTS (
            SELECT 1 FROM json_each(JSON_EXTRACT(NEW.data, '$.radio_channels')) 
            WHERE JSON_EXTRACT(value, '$.tx_frequency.frequency') IS NOT NULL
            AND (
                JSON_EXTRACT(value, '$.tx_frequency.frequency') < 30.0 OR
                JSON_EXTRACT(value, '$.tx_frequency.frequency') > 3000.0
            )
        )
        THEN RAISE(ABORT, 'Radio frequencies must be between 30.0 and 3000.0 MHz')
        
        ELSE 1 -- All validations passed
    END;
END;

-- Trigger to prevent circular dependencies in form relationships
CREATE TRIGGER trg_prevent_circular_relationships 
    BEFORE INSERT ON form_relationships
BEGIN
    SELECT CASE
        WHEN EXISTS (
            WITH RECURSIVE relationship_chain(source, target, depth) AS (
                -- Base case: direct relationship from target to source (would create immediate cycle)
                SELECT target_form_id, source_form_id, 1 
                FROM form_relationships 
                WHERE source_form_id = NEW.target_form_id
                
                UNION ALL
                
                -- Recursive case: follow chain of relationships
                SELECT fr.target_form_id, rc.target, rc.depth + 1
                FROM form_relationships fr
                JOIN relationship_chain rc ON fr.source_form_id = rc.target
                WHERE rc.depth < 10 -- Prevent infinite recursion
            )
            SELECT 1 FROM relationship_chain 
            WHERE source = NEW.source_form_id AND target = NEW.target_form_id
        )
        THEN RAISE(ABORT, 'Cannot create relationship: would result in circular dependency')
        
        ELSE 1 -- No circular dependency detected
    END;
END;

-- Trigger to enforce business rules for form approval workflow
CREATE TRIGGER trg_form_approval_workflow 
    BEFORE UPDATE OF status ON forms
    WHEN NEW.status = 'final'
BEGIN
    SELECT CASE
        -- Final forms must have approval information
        WHEN NEW.approved_by IS NULL OR NEW.approved_at IS NULL
        THEN RAISE(ABORT, 'Final forms must have approval information (approved_by and approved_at)')
        
        -- Final forms cannot be modified after approval (except for status changes)
        WHEN OLD.status = 'final' AND (
            OLD.incident_name != NEW.incident_name OR
            OLD.form_type != NEW.form_type OR
            OLD.data != NEW.data
        )
        THEN RAISE(ABORT, 'Final forms cannot be modified after approval')
        
        ELSE 1 -- All approval workflow rules passed
    END;
END;

-- Update application settings to indicate validation constraints are active
INSERT OR REPLACE INTO settings (key, value) VALUES 
    ('database_constraints_version', '3'),
    ('validation_constraints_enabled', 'true'),
    ('constraint_enforcement_level', '"strict"'),
    ('automatic_validation_triggers', 'true'),
    ('circular_dependency_prevention', 'true'),
    ('form_type_validation', 'true'),
    ('radio_frequency_validation', 'true'),
    ('approval_workflow_enforcement', 'true');

-- Create indexes to support constraint checking performance
CREATE INDEX idx_forms_status_approval ON forms(status, approved_by, approved_at);
CREATE INDEX idx_relationships_circular_check ON form_relationships(source_form_id, target_form_id);
CREATE INDEX idx_forms_type_data_validation ON forms(form_type, JSON_VALID(data));
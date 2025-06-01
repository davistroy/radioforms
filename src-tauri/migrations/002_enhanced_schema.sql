-- RadioForms Enhanced Database Schema - Migration 002
-- 
-- This migration enhances the database schema to support comprehensive
-- ICS form data structures while maintaining the "simpler is better" principle.
-- 
-- Business Logic:
-- - Extends existing simple schema with enhanced metadata
-- - Adds form relationship tracking capabilities
-- - Supports comprehensive validation and lifecycle management
-- - Maintains JSON storage for flexibility with enhanced structure
-- - Adds support for digital signatures and approval workflows

-- Add new columns to forms table for enhanced functionality
ALTER TABLE forms ADD COLUMN form_version TEXT;
ALTER TABLE forms ADD COLUMN incident_number_normalized TEXT; -- For better searching
ALTER TABLE forms ADD COLUMN operational_period_start DATETIME;
ALTER TABLE forms ADD COLUMN operational_period_end DATETIME;
ALTER TABLE forms ADD COLUMN approved_by TEXT; -- JSON for approval information
ALTER TABLE forms ADD COLUMN approved_at DATETIME;
ALTER TABLE forms ADD COLUMN page_info TEXT; -- JSON for page numbering
ALTER TABLE forms ADD COLUMN validation_results TEXT; -- JSON for validation state
ALTER TABLE forms ADD COLUMN workflow_position TEXT DEFAULT 'initial';
ALTER TABLE forms ADD COLUMN priority TEXT DEFAULT 'routine'; -- routine, urgent, emergency

-- Form relationships table for tracking dependencies and connections
-- Simple approach: store relationships as separate records
CREATE TABLE form_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_form_id INTEGER NOT NULL,
    target_form_id INTEGER NOT NULL,
    relationship_type TEXT NOT NULL, -- feeds, requires, updates, references, supersedes, extends
    dependency_strength TEXT NOT NULL DEFAULT 'optional', -- required, recommended, optional
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    
    FOREIGN KEY (source_form_id) REFERENCES forms (id) ON DELETE CASCADE,
    FOREIGN KEY (target_form_id) REFERENCES forms (id) ON DELETE CASCADE,
    
    -- Prevent duplicate relationships
    UNIQUE(source_form_id, target_form_id, relationship_type)
);

-- Form status history table for audit trail
-- Tracks all status changes for accountability and workflow analysis
CREATE TABLE form_status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_id INTEGER NOT NULL,
    from_status TEXT,
    to_status TEXT NOT NULL,
    changed_by TEXT NOT NULL,
    changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    workflow_position TEXT,
    
    FOREIGN KEY (form_id) REFERENCES forms (id) ON DELETE CASCADE
);

-- Digital signatures table for form approval tracking
-- Supports various signature types while maintaining simplicity
CREATE TABLE form_signatures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_id INTEGER NOT NULL,
    signature_type TEXT NOT NULL, -- digital, electronic, handwritten
    signer_name TEXT NOT NULL,
    signer_position TEXT,
    signature_data BLOB, -- Actual signature data (varies by type)
    signature_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    signature_context TEXT, -- prepared_by, approved_by, reviewed_by
    verification_status TEXT DEFAULT 'valid', -- valid, invalid, pending
    
    FOREIGN KEY (form_id) REFERENCES forms (id) ON DELETE CASCADE
);

-- Form templates table for storing form type definitions
-- Supports dynamic form generation and validation
CREATE TABLE form_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_type TEXT NOT NULL UNIQUE,
    template_version TEXT NOT NULL DEFAULT '1.0',
    template_data TEXT NOT NULL, -- JSON structure defining form fields
    validation_rules TEXT, -- JSON array of validation rules
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Validation rules table for storing reusable validation logic
-- Enables complex validation scenarios while keeping them maintainable
CREATE TABLE validation_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL UNIQUE,
    rule_name TEXT NOT NULL,
    rule_type TEXT NOT NULL, -- required, format, range, cross_field, business_rule, conditional
    form_types TEXT, -- JSON array of form types this rule applies to
    fields TEXT NOT NULL, -- JSON array of field names
    validation_logic TEXT NOT NULL, -- JSON object defining the validation
    error_message TEXT NOT NULL,
    warning_message TEXT,
    severity TEXT NOT NULL DEFAULT 'error', -- error, warning, info
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Export configurations table for storing export settings
-- Supports multiple export formats with custom configurations
CREATE TABLE export_configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_name TEXT NOT NULL,
    export_format TEXT NOT NULL, -- pdf, json, ics_des, csv, xml
    form_types TEXT, -- JSON array of applicable form types (null = all)
    template_data TEXT, -- JSON configuration for the export format
    field_filters TEXT, -- JSON array of field filters
    ics_des_config TEXT, -- JSON configuration specific to ICS-DES format
    created_by TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_default BOOLEAN NOT NULL DEFAULT FALSE
);

-- Enhanced indexes for performance optimization
-- These indexes support the enhanced functionality while maintaining performance

-- Improved incident name search (case-insensitive)
CREATE INDEX idx_forms_incident_name_lower ON forms(LOWER(incident_name));

-- Normalized incident number for exact matches
CREATE INDEX idx_forms_incident_number_norm ON forms(incident_number_normalized) 
    WHERE incident_number_normalized IS NOT NULL;

-- Operational period searches
CREATE INDEX idx_forms_op_period_start ON forms(operational_period_start) 
    WHERE operational_period_start IS NOT NULL;
CREATE INDEX idx_forms_op_period_end ON forms(operational_period_end) 
    WHERE operational_period_end IS NOT NULL;

-- Approval status and workflow position
CREATE INDEX idx_forms_approved_at ON forms(approved_at) WHERE approved_at IS NOT NULL;
CREATE INDEX idx_forms_workflow_position ON forms(workflow_position);
CREATE INDEX idx_forms_priority ON forms(priority);

-- Form relationships indexes
CREATE INDEX idx_relationships_source ON form_relationships(source_form_id);
CREATE INDEX idx_relationships_target ON form_relationships(target_form_id);
CREATE INDEX idx_relationships_type ON form_relationships(relationship_type);

-- Status history indexes for audit queries
CREATE INDEX idx_status_history_form ON form_status_history(form_id);
CREATE INDEX idx_status_history_timestamp ON form_status_history(changed_at);
CREATE INDEX idx_status_history_status ON form_status_history(to_status);

-- Signature verification indexes
CREATE INDEX idx_signatures_form ON form_signatures(form_id);
CREATE INDEX idx_signatures_signer ON form_signatures(signer_name);
CREATE INDEX idx_signatures_timestamp ON form_signatures(signature_timestamp);

-- Template and validation rule indexes
CREATE INDEX idx_templates_form_type ON form_templates(form_type);
CREATE INDEX idx_templates_active ON form_templates(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_validation_rules_type ON validation_rules(rule_type);
CREATE INDEX idx_validation_rules_active ON validation_rules(is_active) WHERE is_active = TRUE;

-- Full-text search support for message content and notes
-- This enables efficient searching of form content
CREATE VIRTUAL TABLE forms_fts USING fts5(
    incident_name,
    form_type,
    notes,
    preparer_name,
    data,
    content='forms',
    content_rowid='id'
);

-- Triggers to maintain FTS index
CREATE TRIGGER forms_fts_insert AFTER INSERT ON forms BEGIN
    INSERT INTO forms_fts(rowid, incident_name, form_type, notes, preparer_name, data)
    VALUES (new.id, new.incident_name, new.form_type, new.notes, new.preparer_name, new.data);
END;

CREATE TRIGGER forms_fts_delete AFTER DELETE ON forms BEGIN
    INSERT INTO forms_fts(forms_fts, rowid, incident_name, form_type, notes, preparer_name, data)
    VALUES ('delete', old.id, old.incident_name, old.form_type, old.notes, old.preparer_name, old.data);
END;

CREATE TRIGGER forms_fts_update AFTER UPDATE ON forms BEGIN
    INSERT INTO forms_fts(forms_fts, rowid, incident_name, form_type, notes, preparer_name, data)
    VALUES ('delete', old.id, old.incident_name, old.form_type, old.notes, old.preparer_name, old.data);
    INSERT INTO forms_fts(rowid, incident_name, form_type, notes, preparer_name, data)
    VALUES (new.id, new.incident_name, new.form_type, new.notes, new.preparer_name, new.data);
END;

-- Insert default form templates for each ICS form type
-- These provide the foundation for dynamic form generation
INSERT INTO form_templates (form_type, template_version, template_data, validation_rules) VALUES
('ICS-201', '1.0', json('{"fields": [
    {"name": "incident_name", "type": "text", "required": true, "label": "Incident Name", "max_length": 100},
    {"name": "situation_summary", "type": "textarea", "required": true, "label": "Situation Summary", "max_length": 2000},
    {"name": "current_objectives", "type": "textarea", "required": false, "label": "Current Objectives", "max_length": 1000},
    {"name": "map_sketch_description", "type": "text", "required": false, "label": "Map/Sketch Description", "max_length": 500},
    {"name": "weather_summary", "type": "text", "required": false, "label": "Weather Summary", "max_length": 500},
    {"name": "safety_message", "type": "text", "required": false, "label": "Safety Message", "max_length": 500}
]}'), json('["required_incident_name", "required_situation_summary"]')),

('ICS-202', '1.0', json('{"fields": [
    {"name": "incident_name", "type": "text", "required": true, "label": "Incident Name", "max_length": 100},
    {"name": "objectives", "type": "textarea", "required": true, "label": "Incident Objectives", "max_length": 2000},
    {"name": "command_emphasis", "type": "textarea", "required": false, "label": "Command Emphasis", "max_length": 1000},
    {"name": "site_safety_plan_required", "type": "boolean", "required": true, "label": "Site Safety Plan Required", "default": false},
    {"name": "site_safety_plan_location", "type": "text", "required": false, "label": "Site Safety Plan Location", "max_length": 200},
    {"name": "weather_forecast", "type": "text", "required": false, "label": "Weather Forecast", "max_length": 500}
]}'), json('["required_incident_name", "required_objectives"]')),

('ICS-205', '1.0', json('{"fields": [
    {"name": "incident_name", "type": "text", "required": true, "label": "Incident Name", "max_length": 100},
    {"name": "radio_channels", "type": "repeatable", "required": true, "label": "Radio Channels", "fields": [
        {"name": "function", "type": "text", "required": true, "label": "Function", "max_length": 50},
        {"name": "channel_name", "type": "text", "required": true, "label": "Channel Name", "max_length": 50},
        {"name": "assignment", "type": "text", "required": true, "label": "Assignment", "max_length": 100},
        {"name": "rx_frequency", "type": "frequency", "required": false, "label": "RX Frequency (MHz)"},
        {"name": "tx_frequency", "type": "frequency", "required": false, "label": "TX Frequency (MHz)"},
        {"name": "mode", "type": "enum", "required": false, "label": "Mode", "options": ["Analog", "Digital", "Mixed"]}
    ]},
    {"name": "special_instructions", "type": "textarea", "required": false, "label": "Special Instructions", "max_length": 1000}
]}'), json('["required_incident_name", "required_radio_channels"]')),

('ICS-213', '1.0', json('{"fields": [
    {"name": "to_name", "type": "text", "required": true, "label": "To (Name)", "max_length": 100},
    {"name": "to_position", "type": "text", "required": true, "label": "To (Position)", "max_length": 100},
    {"name": "from_name", "type": "text", "required": true, "label": "From (Name)", "max_length": 100},
    {"name": "from_position", "type": "text", "required": true, "label": "From (Position)", "max_length": 100},
    {"name": "subject", "type": "text", "required": true, "label": "Subject", "max_length": 200},
    {"name": "message", "type": "textarea", "required": true, "label": "Message", "max_length": 2000},
    {"name": "priority", "type": "enum", "required": true, "label": "Priority", "options": ["Emergency", "Urgent", "Routine"], "default": "Routine"},
    {"name": "delivery_method", "type": "enum", "required": false, "label": "Delivery Method", "options": ["Radio", "Phone", "Runner", "Email", "Fax"]}
]}'), json('["required_to_name", "required_from_name", "required_subject", "required_message"]')),

('ICS-214', '1.0', json('{"fields": [
    {"name": "person_name", "type": "text", "required": true, "label": "Person Name", "max_length": 100},
    {"name": "person_position", "type": "text", "required": true, "label": "ICS Position", "max_length": 100},
    {"name": "home_agency", "type": "text", "required": true, "label": "Home Agency", "max_length": 100},
    {"name": "activity_log", "type": "repeatable", "required": true, "label": "Activity Log", "fields": [
        {"name": "date_time", "type": "datetime", "required": true, "label": "Date/Time"},
        {"name": "notable_activities", "type": "textarea", "required": true, "label": "Notable Activities", "max_length": 500},
        {"name": "location", "type": "text", "required": false, "label": "Location", "max_length": 100}
    ]}
]}'), json('["required_person_name", "required_person_position", "required_home_agency"]'));

-- Insert default validation rules
INSERT INTO validation_rules (rule_id, rule_name, rule_type, form_types, fields, validation_logic, error_message, severity) VALUES
('required_incident_name', 'Incident Name Required', 'required', json('null'), json('["incident_name"]'), 
 json('{"min_length": 1, "max_length": 100}'), 'Incident name is required and must be between 1-100 characters', 'error'),

('required_situation_summary', 'Situation Summary Required', 'required', json('["ICS-201"]'), json('["situation_summary"]'), 
 json('{"min_length": 10, "max_length": 2000}'), 'Situation summary is required and must be between 10-2000 characters', 'error'),

('required_objectives', 'Objectives Required', 'required', json('["ICS-202"]'), json('["objectives"]'), 
 json('{"min_length": 10, "max_length": 2000}'), 'Incident objectives are required and must be between 10-2000 characters', 'error'),

('valid_frequency', 'Valid Radio Frequency', 'format', json('["ICS-205"]'), json('["rx_frequency", "tx_frequency"]'), 
 json('{"pattern": "^[0-9]{1,3}\\.[0-9]{3}$", "min_value": 30.0, "max_value": 3000.0}'), 'Frequency must be in format XXX.XXX and between 30.0-3000.0 MHz', 'error'),

('operational_period_valid', 'Valid Operational Period', 'cross_field', json('null'), json('["operational_period_start", "operational_period_end"]'), 
 json('{"condition": "end_after_start", "max_duration_hours": 72}'), 'Operational period end must be after start and duration cannot exceed 72 hours', 'error');

-- Insert default export configurations
INSERT INTO export_configurations (config_name, export_format, template_data, is_default) VALUES
('Default PDF Export', 'pdf', json('{"page_size": "letter", "orientation": "portrait", "margins": {"top": 0.5, "bottom": 0.5, "left": 0.5, "right": 0.5}, "font_family": "Arial", "font_size": 10}'), TRUE),
('Default JSON Export', 'json', json('{"include_metadata": true, "pretty_print": true, "include_validation": false}'), TRUE),
('Default ICS-DES Export', 'ics_des', json('{"max_line_length": 69, "line_prefix": "ICS", "field_separators": true, "include_metadata": true, "error_correction": "checksum"}'), TRUE);

-- Update application settings with enhanced configuration
INSERT OR REPLACE INTO settings (key, value) VALUES 
    ('enhanced_schema_version', '2'),
    ('form_templates_enabled', 'true'),
    ('validation_enabled', 'true'),
    ('digital_signatures_enabled', 'true'),
    ('full_text_search_enabled', 'true'),
    ('auto_save_interval', '30'),
    ('max_operational_period_hours', '72'),
    ('default_export_format', '"pdf"'),
    ('enable_form_relationships', 'true'),
    ('enable_workflow_tracking', 'true');
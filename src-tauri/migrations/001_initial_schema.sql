-- RadioForms Initial Database Schema
-- 
-- This migration creates the initial database schema for the STANDALONE
-- ICS Forms Management Application.
-- 
-- Business Logic:
-- - Simple schema design following "simpler is better" principle
-- - JSON storage for form data flexibility
-- - Proper indexing for search performance
-- - Single-user operation optimization

-- Main forms table
-- Stores all ICS form instances with their data as JSON
CREATE TABLE forms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_type TEXT NOT NULL,
    incident_name TEXT NOT NULL,
    incident_number TEXT,
    status TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft', 'completed', 'final')),
    data TEXT NOT NULL, -- JSON blob containing all form field data
    notes TEXT,
    preparer_name TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Application settings table
-- Simple key-value storage for application preferences
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL, -- JSON value for flexibility
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance optimization
-- These indexes support the most common query patterns

-- Search by incident name (most common search)
CREATE INDEX idx_forms_incident_name ON forms(incident_name);

-- Search by form type
CREATE INDEX idx_forms_type ON forms(form_type);

-- Search by status
CREATE INDEX idx_forms_status ON forms(status);

-- Sort by creation date (newest first)
CREATE INDEX idx_forms_created_at ON forms(created_at DESC);

-- Sort by update date (for "recently modified")
CREATE INDEX idx_forms_updated_at ON forms(updated_at DESC);

-- Combined index for common filter combinations
CREATE INDEX idx_forms_type_status ON forms(form_type, status);

-- Preparer search index
CREATE INDEX idx_forms_preparer ON forms(preparer_name) WHERE preparer_name IS NOT NULL;

-- Incident number search (when provided)
CREATE INDEX idx_forms_incident_number ON forms(incident_number) WHERE incident_number IS NOT NULL;

-- Insert default application settings
INSERT INTO settings (key, value) VALUES 
    ('app_version', '"1.0.0"'),
    ('last_backup', 'null'),
    ('auto_save_interval', '30'),
    ('theme', '"auto"'),
    ('default_preparer_name', '""');

-- Add helpful database metadata
INSERT INTO settings (key, value) VALUES 
    ('schema_version', '1'),
    ('created_at', json_quote(datetime('now')));
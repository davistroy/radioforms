-- Simple database schema for RadioForms
-- This replaces all complex migrations with one simple schema

CREATE TABLE forms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_name TEXT NOT NULL,
    form_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    form_data TEXT NOT NULL DEFAULT '{}',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Simple indexes for actual search needs
CREATE INDEX idx_forms_incident_name ON forms(incident_name);
CREATE INDEX idx_forms_status ON forms(status);
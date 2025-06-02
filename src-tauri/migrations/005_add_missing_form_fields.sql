-- Migration: Add missing form fields for SQLx 0.8 compatibility
-- Adds version and workflow_position fields to forms table

-- Add version field for form revisions and change tracking
ALTER TABLE forms ADD COLUMN version INTEGER DEFAULT 1 NOT NULL;

-- Add workflow_position field for form processing state
ALTER TABLE forms ADD COLUMN workflow_position TEXT;

-- Update existing records to have version 1
UPDATE forms SET version = 1 WHERE version IS NULL;

-- Create index on version for performance
CREATE INDEX idx_forms_version ON forms(version);

-- Create index on workflow_position for filtering
CREATE INDEX idx_forms_workflow_position ON forms(workflow_position);
-- Rollback script for Migration 004: Performance Indexes and Optimization
-- 
-- This script safely removes all performance optimizations added in migration 004
-- while preserving data integrity and core functionality.
--
-- Business Logic:
-- - Remove performance indexes to restore original structure
-- - Drop FTS tables and triggers to free up space
-- - Remove performance monitoring tables
-- - Preserve all data during rollback
-- - Restore settings to pre-optimization state

-- Remove FTS triggers first to prevent errors
DROP TRIGGER IF EXISTS trg_forms_fts_insert;
DROP TRIGGER IF EXISTS trg_forms_fts_delete;  
DROP TRIGGER IF EXISTS trg_forms_fts_update;

-- Drop FTS virtual table
DROP TABLE IF EXISTS forms_fts;

-- Remove performance monitoring triggers
DROP TRIGGER IF EXISTS trg_log_slow_queries;

-- Drop performance views
DROP VIEW IF EXISTS view_recent_forms;
DROP VIEW IF EXISTS view_forms_by_status;
DROP VIEW IF EXISTS view_incident_progress;
DROP VIEW IF EXISTS view_form_dependencies;
DROP VIEW IF EXISTS view_validation_summary;
DROP VIEW IF EXISTS view_table_statistics;
DROP VIEW IF EXISTS view_index_usage;

-- Drop performance monitoring table
DROP TABLE IF EXISTS query_performance_log;

-- Remove all performance optimization indexes
-- Core search indexes
DROP INDEX IF EXISTS idx_forms_core_search;
DROP INDEX IF EXISTS idx_forms_date_search;
DROP INDEX IF EXISTS idx_forms_updated_search;
DROP INDEX IF EXISTS idx_forms_preparer_search;
DROP INDEX IF EXISTS idx_forms_status_workflow;
DROP INDEX IF EXISTS idx_forms_operational_period;
DROP INDEX IF EXISTS idx_forms_priority_search;
DROP INDEX IF EXISTS idx_forms_approval_search;

-- Form relationships indexes
DROP INDEX IF EXISTS idx_relationships_source;
DROP INDEX IF EXISTS idx_relationships_target;
DROP INDEX IF EXISTS idx_relationships_bidirectional;

-- Status history indexes
DROP INDEX IF EXISTS idx_status_history_form;
DROP INDEX IF EXISTS idx_status_history_user;

-- Digital signatures indexes
DROP INDEX IF EXISTS idx_signatures_form;
DROP INDEX IF EXISTS idx_signatures_signer;

-- Form templates indexes
DROP INDEX IF EXISTS idx_templates_type_version;

-- Validation rules indexes
DROP INDEX IF EXISTS idx_validation_rules_form_type;
DROP INDEX IF EXISTS idx_validation_rules_type;

-- Export configurations indexes
DROP INDEX IF EXISTS idx_export_configs_format;

-- Settings indexes
DROP INDEX IF EXISTS idx_settings_key;

-- Compound indexes
DROP INDEX IF EXISTS idx_incident_timeline;
DROP INDEX IF EXISTS idx_form_type_analysis;
DROP INDEX IF EXISTS idx_approval_workflow;
DROP INDEX IF EXISTS idx_user_activity;
DROP INDEX IF EXISTS idx_operational_readiness;

-- Cross-form analysis indexes
DROP INDEX IF EXISTS idx_incident_number_normalized;
DROP INDEX IF EXISTS idx_forms_page_info;
DROP INDEX IF EXISTS idx_forms_validation_errors;

-- Performance log indexes
DROP INDEX IF EXISTS idx_performance_log_type_time;

-- Remove performance-related settings
DELETE FROM settings WHERE key IN (
    'database_performance_version',
    'performance_indexes_enabled',
    'full_text_search_enabled',
    'performance_views_enabled',
    'query_performance_logging',
    'index_optimization_level',
    'fts_synchronization',
    'last_performance_optimization',
    'expected_query_performance',
    'performance_targets'
);

-- Restore pre-optimization settings
INSERT OR REPLACE INTO settings (key, value) VALUES 
    ('database_performance_version', '3'),
    ('performance_optimization_level', '"basic"'),
    ('rollback_from_version_4', '"' || datetime('now') || '"');

-- Log rollback completion
INSERT OR REPLACE INTO settings (key, value) VALUES 
    ('migration_004_rollback_completed', '"' || datetime('now') || '"'),
    ('rollback_reason', '"Manual rollback or migration failure"');

-- Final cleanup - run VACUUM to reclaim space from dropped indexes
VACUUM;

-- Final integrity check after rollback
PRAGMA integrity_check;

-- Note: This rollback script preserves all data while removing performance optimizations
-- The database will still function normally but with reduced query performance
-- Re-running migration 004 will restore all optimizations
/*!
 * Migration Testing Framework for RadioForms
 * 
 * This module provides comprehensive testing for the database migration system,
 * ensuring that all migrations execute correctly and that the database schema
 * evolves properly across versions.
 * 
 * Business Logic:
 * - Test migration execution from fresh database
 * - Validate schema consistency after each migration
 * - Test rollback functionality for reversible migrations
 * - Verify data integrity during migration processes
 * - Test migration performance and timing
 * 
 * Design Philosophy:
 * - Comprehensive coverage of migration scenarios
 * - Fast execution for CI/CD pipeline integration
 * - Clear reporting of migration issues
 * - Support for both automated and manual testing
 */

#[cfg(test)]
mod tests {
    use super::*;
    use crate::database::{Database, migration_runner::{MigrationRunner, MigrationRunnerFactory}};
    use sqlx::{SqlitePool, migrate::MigrateDatabase, Sqlite};
    use tempfile::tempdir;
    use std::path::PathBuf;
    use anyhow::Result;

    /// Sets up a temporary test database for migration testing.
    /// 
    /// Business Logic:
    /// - Creates isolated test environment
    /// - Ensures clean state for each test
    /// - Provides realistic database setup
    /// - Supports both unit and integration testing
    async fn setup_test_database() -> Result<(SqlitePool, PathBuf)> {
        let temp_dir = tempdir()?;
        let db_path = temp_dir.path().join("test_migrations.db");
        let db_url = format!("sqlite:{}", db_path.display());
        
        // Create empty database
        Sqlite::create_database(&db_url).await?;
        let pool = SqlitePool::connect(&db_url).await?;
        
        Ok((pool, db_path))
    }

    /// Tests basic migration runner creation and initialization.
    #[tokio::test]
    async fn test_migration_runner_creation() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        let runner = MigrationRunner::new(pool, db_path).await;
        assert!(runner.is_ok(), "Migration runner creation should succeed");
    }

    /// Tests SQLx migration execution from a fresh database.
    #[tokio::test]
    async fn test_fresh_migration_execution() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        let runner = MigrationRunner::new(pool.clone(), db_path).await
            .expect("Failed to create migration runner");
        
        // Run migrations
        let result = runner.run_sqlx_migrations().await;
        assert!(result.is_ok(), "Fresh migration execution should succeed");
        
        // Verify core tables exist
        let tables = vec![
            "forms", "form_relationships", "form_status_history",
            "form_signatures", "form_templates", "validation_rules",
            "export_configurations", "settings"
        ];
        
        for table in tables {
            let table_exists = sqlx::query_scalar::<_, i64>(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?"
            )
            .bind(table)
            .fetch_one(&pool)
            .await
            .expect("Table existence query should work");
            
            assert_eq!(table_exists, 1, "Table '{}' should exist after migration", table);
        }
    }

    /// Tests migration validation functionality.
    #[tokio::test]
    async fn test_migration_validation() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        let runner = MigrationRunner::new(pool.clone(), db_path).await
            .expect("Failed to create migration runner");
        
        // Validate before migrations (should find issues)
        let issues_before = runner.validate_migrations().await
            .expect("Validation should work");
        assert!(!issues_before.is_empty(), "Should find issues before migration");
        
        // Run migrations
        runner.run_sqlx_migrations().await
            .expect("Migration should succeed");
        
        // Validate after migrations (should find fewer issues)
        let issues_after = runner.validate_migrations().await
            .expect("Validation should work");
        
        // Should have fewer issues after migration
        assert!(issues_after.len() < issues_before.len(), 
               "Should have fewer issues after migration");
    }

    /// Tests backup creation functionality.
    #[tokio::test]
    async fn test_backup_creation() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        // Insert some test data first
        sqlx::query("CREATE TABLE test_table (id INTEGER PRIMARY KEY, data TEXT)")
            .execute(&pool)
            .await
            .expect("Test table creation should work");
        
        sqlx::query("INSERT INTO test_table (data) VALUES ('test_data')")
            .execute(&pool)
            .await
            .expect("Test data insertion should work");
        
        let runner = MigrationRunner::new(pool.clone(), db_path.clone()).await
            .expect("Failed to create migration runner");
        
        // Create backup
        let backup_path = runner.create_backup().await
            .expect("Backup creation should succeed");
        
        assert!(backup_path.exists(), "Backup file should exist");
        
        // Verify backup contains our test data
        let backup_url = format!("sqlite:{}", backup_path.display());
        let backup_pool = SqlitePool::connect(&backup_url).await
            .expect("Should be able to connect to backup");
        
        let data_count = sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM test_table WHERE data = 'test_data'"
        )
        .fetch_one(&backup_pool)
        .await
        .expect("Should be able to query backup");
        
        assert_eq!(data_count, 1, "Backup should contain test data");
        
        backup_pool.close().await;
        
        // Cleanup
        tokio::fs::remove_file(backup_path).await.ok();
    }

    /// Tests migration history tracking.
    #[tokio::test]
    async fn test_migration_history() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        let runner = MigrationRunner::new(pool.clone(), db_path).await
            .expect("Failed to create migration runner");
        
        // Run migrations
        runner.run_sqlx_migrations().await
            .expect("Migration should succeed");
        
        // Get migration history
        let history = runner.get_migration_history().await
            .expect("Should be able to get migration history");
        
        assert!(!history.is_empty(), "Should have migration history after running migrations");
        
        // Verify history entries have required fields
        for entry in history {
            assert!(entry.version > 0, "Migration version should be positive");
            assert!(!entry.description.is_empty(), "Migration should have description");
            assert!(entry.success, "All migrations should be successful in test");
        }
    }

    /// Tests post-migration optimization functionality.
    #[tokio::test]
    async fn test_post_migration_optimization() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        let runner = MigrationRunner::new(pool.clone(), db_path).await
            .expect("Failed to create migration runner");
        
        // Run migrations first
        runner.run_sqlx_migrations().await
            .expect("Migration should succeed");
        
        // Run optimization
        let result = runner.optimize_post_migration().await;
        assert!(result.is_ok(), "Post-migration optimization should succeed");
        
        // Verify foreign keys are enabled
        let fk_enabled = sqlx::query_scalar::<_, bool>("PRAGMA foreign_keys")
            .fetch_one(&pool)
            .await
            .expect("Should be able to check foreign key setting");
        
        assert!(fk_enabled, "Foreign keys should be enabled after optimization");
    }

    /// Tests the complete Database initialization process.
    #[tokio::test]
    async fn test_database_initialization() {
        // This test uses a temporary directory for the database
        let temp_dir = tempdir().expect("Failed to create temp directory");
        
        // Set the current directory to temp dir to test relative path behavior
        std::env::set_current_dir(&temp_dir).expect("Failed to change directory");
        
        // Initialize database (this will run migrations)
        let database = Database::new().await;
        assert!(database.is_ok(), "Database initialization should succeed");
        
        let db = database.unwrap();
        
        // Verify database file exists
        assert!(db.database_path().exists(), "Database file should exist");
        
        // Verify we can get stats (this tests that tables exist)
        let stats = db.get_stats().await;
        assert!(stats.is_ok(), "Should be able to get database stats");
        
        // Verify integrity
        let integrity = db.validate_integrity().await;
        assert!(integrity.is_ok(), "Integrity validation should work");
        assert!(integrity.unwrap(), "Database should have good integrity");
    }

    /// Tests migration factory methods for different environments.
    #[tokio::test]
    async fn test_migration_factory_methods() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        // Test production runner creation
        let prod_runner = MigrationRunnerFactory::create_production_runner(
            pool.clone(), db_path.clone()
        ).await;
        assert!(prod_runner.is_ok(), "Production runner creation should succeed");
        
        // Test development runner creation
        let dev_runner = MigrationRunnerFactory::create_development_runner(
            pool.clone(), db_path.clone()
        ).await;
        assert!(dev_runner.is_ok(), "Development runner creation should succeed");
        
        // Test testing runner creation
        let test_runner = MigrationRunnerFactory::create_testing_runner(
            pool.clone(), db_path
        ).await;
        assert!(test_runner.is_ok(), "Testing runner creation should succeed");
    }

    /// Tests schema consistency across migrations.
    #[tokio::test]
    async fn test_schema_consistency() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        let runner = MigrationRunner::new(pool.clone(), db_path).await
            .expect("Failed to create migration runner");
        
        // Run migrations
        runner.run_sqlx_migrations().await
            .expect("Migration should succeed");
        
        // Test that all expected indexes exist
        let index_count = sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
        )
        .fetch_one(&pool)
        .await
        .expect("Should be able to count indexes");
        
        assert!(index_count > 10, "Should have created performance indexes");
        
        // Test that FTS table exists
        let fts_exists = sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='forms_fts'"
        )
        .fetch_one(&pool)
        .await
        .expect("Should be able to check FTS table");
        
        assert_eq!(fts_exists, 1, "FTS table should exist after migration");
        
        // Test that views exist
        let view_count = sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='view'"
        )
        .fetch_one(&pool)
        .await
        .expect("Should be able to count views");
        
        assert!(view_count > 5, "Should have created performance views");
    }

    /// Tests that constraints are properly enforced after migration.
    #[tokio::test]
    async fn test_constraint_enforcement() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        let runner = MigrationRunner::new(pool.clone(), db_path).await
            .expect("Failed to create migration runner");
        
        // Run migrations
        runner.run_sqlx_migrations().await
            .expect("Migration should succeed");
        
        // Test that invalid form type is rejected
        let invalid_insert = sqlx::query(
            "INSERT INTO forms (incident_name, form_type, data, status, priority, workflow_position) 
             VALUES ('test', 'INVALID-FORM', '{}', 'draft', 'routine', 'initial')"
        )
        .execute(&pool)
        .await;
        
        assert!(invalid_insert.is_err(), "Should reject invalid form type");
        
        // Test that valid form type is accepted
        let valid_insert = sqlx::query(
            "INSERT INTO forms (incident_name, form_type, data, status, priority, workflow_position) 
             VALUES ('test', 'ICS-201', '{}', 'draft', 'routine', 'initial')"
        )
        .execute(&pool)
        .await;
        
        assert!(valid_insert.is_ok(), "Should accept valid form type");
        
        // Test that incident name constraint works
        let short_name_insert = sqlx::query(
            "INSERT INTO forms (incident_name, form_type, data, status, priority, workflow_position) 
             VALUES ('ab', 'ICS-201', '{}', 'draft', 'routine', 'initial')"
        )
        .execute(&pool)
        .await;
        
        assert!(short_name_insert.is_err(), "Should reject incident name that's too short");
    }

    /// Performance test for migration execution.
    #[tokio::test]
    async fn test_migration_performance() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        let runner = MigrationRunner::new(pool.clone(), db_path).await
            .expect("Failed to create migration runner");
        
        // Time the migration execution
        let start_time = std::time::Instant::now();
        
        runner.run_sqlx_migrations().await
            .expect("Migration should succeed");
        
        let elapsed = start_time.elapsed();
        
        // Migration should complete within reasonable time (30 seconds for all migrations)
        assert!(elapsed.as_secs() < 30, 
               "Migration should complete within 30 seconds, took: {:?}", elapsed);
        
        println!("Migration completed in: {:?}", elapsed);
    }

    /// Tests data preservation during migrations.
    #[tokio::test]
    async fn test_data_preservation() {
        let (pool, db_path) = setup_test_database().await
            .expect("Failed to setup test database");
        
        // Create basic schema first (simulate older version)
        sqlx::query(
            "CREATE TABLE forms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_name TEXT NOT NULL,
                form_type TEXT NOT NULL,
                data TEXT NOT NULL,
                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"
        )
        .execute(&pool)
        .await
        .expect("Basic schema creation should work");
        
        // Insert test data
        sqlx::query(
            "INSERT INTO forms (incident_name, form_type, data) 
             VALUES ('Test Incident', 'ICS-201', '{\"test\": \"data\"}')"
        )
        .execute(&pool)
        .await
        .expect("Test data insertion should work");
        
        let original_count = sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM forms")
            .fetch_one(&pool)
            .await
            .expect("Should be able to count original data");
        
        // Now run full migrations
        let runner = MigrationRunner::new(pool.clone(), db_path).await
            .expect("Failed to create migration runner");
        
        runner.run_sqlx_migrations().await
            .expect("Migration should succeed");
        
        // Verify data is preserved
        let final_count = sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM forms")
            .fetch_one(&pool)
            .await
            .expect("Should be able to count final data");
        
        assert_eq!(original_count, final_count, "Data should be preserved during migration");
        
        // Verify specific test data
        let test_data = sqlx::query_scalar::<_, String>(
            "SELECT data FROM forms WHERE incident_name = 'Test Incident'"
        )
        .fetch_one(&pool)
        .await
        .expect("Should be able to retrieve test data");
        
        assert!(test_data.contains("test"), "Original data should be preserved");
    }
}
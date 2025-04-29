# **Revised Database Design Document for ICS Forms Management Application (SQLite)**  
*(Version 1.1 – April 29, 2025)*

---

## 1. **Project Overview**
This database supports a forms-driven application that enables multiple users to create, manage, export, and archive FEMA ICS forms locally in an offline-first environment. The design incorporates enhanced version tracking, migration support, and improved data integrity mechanisms.

---

## 2. **General Design Requirements**

| Requirement | Design Decision |
|:------------|:----------------|
| **Database** | SQLite |
| **Naming** | snake_case (strictly enforced) |
| **Primary Keys** | INTEGER PRIMARY KEY AUTOINCREMENT |
| **Foreign Keys** | Yes (explicitly enforced with constraint definitions) |
| **Timestamps** | `created_at`, `updated_at` per form |
| **User Tracking** | Add `created_by` (User Name/Call Sign) field |
| **Attachments** | Stored externally in filesystem, referenced in DB |
| **Audit Trails** | Comprehensive version tracking and audit logging |
| **Access Controls** | Role-based access control framework for future multi-user scenarios |
| **Templates/Pre-fill** | Supported through template system |
| **Versioning** | Robust version tracking system with full history |
| **Backup Strategy** | Automatic backups with rotation policy |
| **Data Compression** | Optional compression for large deployments |
| **Concurrency** | Support for concurrent access with proper locking mechanisms |
| **Data Integrity** | Periodic integrity checks beyond startup validation |

---

## 3. **Core Tables**

| Table | Purpose |
|:------|:--------|
| `forms` | Master list of all form instances |
| `form_versions` | Version history for all forms |
| `users` | User profiles (for future expansion) |
| `ics201`, `ics202`, ..., `ics221` | Per-form tables |
| `*_items` | Child tables for repeatable sections |
| `attachments` | Files linked to forms (maps, signatures, etc.) |
| `audit_logs` | Comprehensive audit trail |
| `migrations` | Database migration tracking |

---

## 4. **Master Table: `forms`**

| Field | Type | Description |
|:------|:----|:------------|
| form_id | INTEGER PRIMARY KEY AUTOINCREMENT |
| form_type | TEXT NOT NULL | e.g., "ICS-201", "ICS-214", etc. |
| form_name | TEXT NOT NULL | Full human-readable name |
| current_version | TEXT NOT NULL | Current version of form |
| status | TEXT NOT NULL | Draft, Completed, Submitted, Archived |
| created_by | TEXT NOT NULL | User Name/Call Sign from App Settings |
| created_at | DATETIME NOT NULL | When created |
| updated_at | DATETIME NOT NULL | Last updated |
| is_template | BOOLEAN DEFAULT FALSE | Whether this is a template form |
| incident_id | INTEGER | FK to incidents table |

**Foreign Key Constraints:**
```sql
FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
```

**Indexes:**
```sql
CREATE INDEX idx_forms_type ON forms(form_type);
CREATE INDEX idx_forms_status ON forms(status);
CREATE INDEX idx_forms_created_at ON forms(created_at);
CREATE INDEX idx_forms_updated_at ON forms(updated_at);
CREATE INDEX idx_forms_created_by ON forms(created_by);
CREATE INDEX idx_forms_incident_id ON forms(incident_id);
```

---

## 5. **Version History: `form_versions`**

| Field | Type | Description |
|:------|:----|:------------|
| version_id | INTEGER PRIMARY KEY AUTOINCREMENT |
| form_id | INTEGER NOT NULL | FK to forms(form_id) |
| version | TEXT NOT NULL | Version identifier (e.g., "1.0", "1.1") |
| data | TEXT NOT NULL | JSON representation of form data |
| created_by | TEXT NOT NULL | User who created this version |
| created_at | DATETIME NOT NULL | When version was created |
| notes | TEXT | Optional version notes |

**Foreign Key Constraints:**
```sql
FOREIGN KEY (form_id) REFERENCES forms(form_id) ON DELETE CASCADE
```

**Indexes:**
```sql
CREATE INDEX idx_form_versions_form_id ON form_versions(form_id);
CREATE INDEX idx_form_versions_created_at ON form_versions(created_at);
```

---

## 6. **Incident Management: `incidents`**

| Field | Type | Description |
|:------|:----|:------------|
| incident_id | INTEGER PRIMARY KEY AUTOINCREMENT |
| incident_name | TEXT NOT NULL | Name of the incident |
| start_date | DATETIME NOT NULL | When incident started |
| end_date | DATETIME | When incident ended (if applicable) |
| description | TEXT | Optional description |
| status | TEXT NOT NULL | Active, Closed, Archived |
| created_by | TEXT NOT NULL | User who created the incident |
| created_at | DATETIME NOT NULL | When created |
| updated_at | DATETIME NOT NULL | Last updated |

**Indexes:**
```sql
CREATE INDEX idx_incidents_name ON incidents(incident_name);
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_dates ON incidents(start_date, end_date);
```

---

## 7. **Attachment Management: `attachments`**

| Field | Type | Description |
|:------|:----|:------------|
| attachment_id | INTEGER PRIMARY KEY AUTOINCREMENT |
| form_id | INTEGER NOT NULL | FK to forms(form_id) |
| section | TEXT NOT NULL | Section of the form (e.g., "MapSketch", "Signature") |
| file_path | TEXT NOT NULL | Relative path to the stored file |
| file_name | TEXT NOT NULL | Original filename |
| file_type | TEXT NOT NULL | MIME type or file extension |
| file_size | INTEGER NOT NULL | Size in bytes |
| md5_hash | TEXT | File checksum for integrity checking |
| description | TEXT | Optional notes about the attachment |
| created_by | TEXT NOT NULL | User who added the attachment |
| created_at | DATETIME NOT NULL | When added |

**Foreign Key Constraints:**
```sql
FOREIGN KEY (form_id) REFERENCES forms(form_id) ON DELETE CASCADE
```

**Indexes:**
```sql
CREATE INDEX idx_attachments_form_id ON attachments(form_id);
CREATE INDEX idx_attachments_file_type ON attachments(file_type);
```

**Note:**  
- Images (e.g., signatures, maps/sketches) are **saved externally** in the filesystem.
- The **file path** is stored relative to a base application directory.
- Cross-platform path handling is implemented in the application layer.
- File integrity is verified using MD5 checksums.

---

## 8. **Audit Logging: `audit_logs`**

| Field | Type | Description |
|:------|:----|:------------|
| log_id | INTEGER PRIMARY KEY AUTOINCREMENT |
| entity_type | TEXT NOT NULL | Type of entity (e.g., "form", "attachment") |
| entity_id | INTEGER NOT NULL | ID of the affected entity |
| action | TEXT NOT NULL | Action performed (e.g., "create", "update", "delete") |
| user | TEXT NOT NULL | User who performed the action |
| timestamp | DATETIME NOT NULL | When the action occurred |
| details | TEXT | JSON with additional details |

**Indexes:**
```sql
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_user ON audit_logs(user);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
```

---

## 9. **Migration Management: `migrations`**

| Field | Type | Description |
|:------|:----|:------------|
| migration_id | INTEGER PRIMARY KEY AUTOINCREMENT |
| version | TEXT NOT NULL | Migration version identifier |
| applied_at | DATETIME NOT NULL | When migration was applied |
| description | TEXT | Description of the migration |
| checksum | TEXT | Checksum of migration script for integrity |

**Indexes:**
```sql
CREATE INDEX idx_migrations_version ON migrations(version);
```

---

## 10. **Example of a Specific Form Schema: ICS-214**

### 10.1 Overview of ICS-214 Activity Log

The ICS-214 Activity Log records details of notable activities chronologically for individuals, units, or resources during incident operations. It provides:

1. Documentation of key activities during incident response
2. Reference material for after-action reports
3. Record of resource utilization
4. Individual/unit activity history

This schema implementation aligns with the detailed specifications in ICS-214-Analysis.md and implements all required validation rules and relationships.

### 10.2 Parent Table: `ics214`

| Field | Type | Description | Field ID in Analysis |
|:------|:----|:------------|:---------------------|
| ics214_id | INTEGER PRIMARY KEY AUTOINCREMENT | Unique identifier for this form instance | - |
| form_id | INTEGER NOT NULL | FK to forms(form_id) | - |
| incident_name | TEXT NOT NULL | Name assigned to the incident | ics214_incident_name |
| operational_period_start | DATETIME NOT NULL | Start of time interval for which form applies | ics214_operational_period |
| operational_period_end | DATETIME NOT NULL | End of time interval for which form applies | ics214_operational_period |
| name | TEXT NOT NULL | Name of individual completing the log | ics214_name |
| ics_position | TEXT NOT NULL | ICS position of individual completing the log | ics214_ics_position |
| home_agency | TEXT NOT NULL | Agency and unit of the individual | ics214_home_agency |
| prepared_by_name | TEXT NOT NULL | Name of person preparing the form | ics214_prepared_by |
| prepared_by_position | TEXT NOT NULL | Position/title of person preparing the form | ics214_prepared_by |
| prepared_by_signature | TEXT | File path to signature image | ics214_prepared_by |
| prepared_datetime | DATETIME NOT NULL | Date and time the form was prepared | ics214_prepared_date_time |
| page_number | TEXT | Page number information (e.g., "Page 1 of 3") | ics214_page_number |
| form_version | TEXT | Version of the ICS 214 form being used | ics214_form_version |

**Foreign Key Constraints:**
```sql
FOREIGN KEY (form_id) REFERENCES forms(form_id) ON DELETE CASCADE
```

**Indexes:**
```sql
CREATE INDEX idx_ics214_form_id ON ics214(form_id);
CREATE INDEX idx_ics214_incident_name ON ics214(incident_name);
CREATE INDEX idx_ics214_operational_period ON ics214(operational_period_start, operational_period_end);
CREATE INDEX idx_ics214_name ON ics214(name);
```

---

### 10.3 Child Table 1: `ics214_activity_log_items`

This table implements the chronological activity log that forms the core of the ICS-214 form.

| Field | Type | Description | Field ID in Analysis |
|:------|:----|:------------|:---------------------|
| activity_id | INTEGER PRIMARY KEY AUTOINCREMENT | Unique identifier for this activity entry | - |
| ics214_id | INTEGER NOT NULL | FK to ics214(ics214_id) | - |
| activity_datetime | DATETIME NOT NULL | When the activity occurred | ics214_activity_datetime |
| notable_activities | TEXT NOT NULL | Description of the activity | ics214_notable_activities |
| entry_order | INTEGER NOT NULL | Sequence number to maintain chronological order | - |

**Foreign Key Constraints:**
```sql
FOREIGN KEY (ics214_id) REFERENCES ics214(ics214_id) ON DELETE CASCADE
```

**Indexes:**
```sql
CREATE INDEX idx_ics214_activity_log_ics214_id ON ics214_activity_log_items(ics214_id);
CREATE INDEX idx_ics214_activity_datetime ON ics214_activity_log_items(activity_datetime);
CREATE INDEX idx_ics214_activity_entry_order ON ics214_activity_log_items(entry_order);
```

**Business Rules Implemented:**
* Activities are always stored in chronological order
* The entry_order field ensures activities can be displayed in the original order entered
* Both date/time and activity description are required for each entry

---

### 10.4 Child Table 2: `ics214_resources_assigned`

This table tracks resources assigned to the individual or unit completing the activity log.

| Field | Type | Description | Field ID in Analysis |
|:------|:----|:------------|:---------------------|
| resource_id | INTEGER PRIMARY KEY AUTOINCREMENT | Unique identifier for this resource entry | - |
| ics214_id | INTEGER NOT NULL | FK to ics214(ics214_id) | - |
| resource_name | TEXT NOT NULL | Name of the resource | ics214_resource_name |
| resource_position | TEXT | ICS position of the resource | ics214_resource_position |
| resource_home_agency | TEXT | Agency and unit of the resource | ics214_resource_home_agency |
| entry_order | INTEGER NOT NULL | Sequence number to maintain display order | - |

**Foreign Key Constraints:**
```sql
FOREIGN KEY (ics214_id) REFERENCES ics214(ics214_id) ON DELETE CASCADE
```

**Indexes:**
```sql
CREATE INDEX idx_ics214_resources_ics214_id ON ics214_resources_assigned(ics214_id);
CREATE INDEX idx_ics214_resources_name ON ics214_resources_assigned(resource_name);
CREATE INDEX idx_ics214_resources_entry_order ON ics214_resources_assigned(entry_order);
```

**Business Rules Implemented:**
* Resources are optional in the ICS-214 form
* Resource name is required when a resource is added
* The entry_order field preserves the original order of resource entries

---

## 11. **Common Field Guidelines Across Forms**

| Guideline | Detail |
|:----------|:-------|
| `form_id` | Link to forms(form_id) with explicit foreign key constraint |
| `created_by` | Store username/callsign from app settings |
| `created_at`, `updated_at` | Consistent timestamps in ISO 8601 format |
| Image fields | Store file paths only (no blobs/base64) with validation |
| Complex data (repeating items) | Use child tables with proper indexes |
| Foreign keys | Always explicitly defined with appropriate cascade actions |
| Naming conventions | Strict adherence to snake_case |

---

## 12. **Database Initialization**

The application initializes the database with the following important settings:

```sql
-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Enable WAL mode for better performance and reliability
PRAGMA journal_mode = WAL;

-- Set synchronous mode for better reliability
PRAGMA synchronous = NORMAL;

-- Set temp store to memory for better performance
PRAGMA temp_store = MEMORY;

-- Set page size for optimal performance
PRAGMA page_size = 4096;

-- Set cache size
PRAGMA cache_size = -2000; -- 2MB cache
```

### 12.1 **Platform-Specific WAL Mode Considerations**

Write-Ahead Logging (WAL) mode significantly improves database reliability, but implementation requires platform-specific considerations:

#### Windows
- WAL files require shared read access on Windows networks
- File locking may cause issues with some network storage configurations
- Implementation requires careful handling of file permissions in User Account Control (UAC) contexts

#### macOS
- Default filesystem (APFS) fully supports WAL mode
- Time Machine may need to be configured to exclude WAL files from backup to prevent inconsistent states
- Apple sandbox restrictions in certain contexts may require specific entitlements

#### Linux
- Various filesystem support considerations:
  - ext4, XFS, Btrfs: Full support for WAL mode
  - NFS: Potential file locking issues require specific mount options
  - Older filesystems may have limited support
- Shared memory settings may need adjustment for optimal performance

#### Implementation Requirements
- The application must detect the operating system during initialization
- Platform-specific WAL settings must be applied based on detected environment
- File path handling must account for platform-specific separators (backslash vs. forward slash)
- Error handling must include platform-specific recovery procedures for WAL corruption
- Diagnostic tools must report WAL mode status and potential configuration issues

---

## 13. **Backup Strategy**

### 13.1 **Backup Implementation Overview**

The database backup strategy implements a multi-tier approach to ensure data safety while optimizing storage utilization:

1. **Automatic Backup Trigger Points**:
   - Application close (highest priority)
   - Scheduled intervals during long sessions (every 30 minutes)
   - Before database schema migrations
   - After bulk operations (importing multiple forms)
   - User-initiated manual backups

2. **Backup Storage Architecture**:
   - Default location: `/backups` subdirectory in application directory
   - User-configurable alternate location support
   - Hierarchical storage organization by date (YYYY/MM/DD folders)
   - Standardized naming convention: `incident_name_YYYYMMDD_HHMMSS.db`

3. **Rotation Policy Implementation**:
   - Daily tier: Retains most recent 10 daily backups
       - Full backup of entire database
       - Highest priority for quick recovery
   - Weekly tier: Retains 4 weekly backups (Monday at midnight)
       - Full backup with manifest file listing forms
       - Medium priority for historical access
   - Monthly tier: Retains 3 monthly backups (1st day of month)
       - Full backup with integrity verification report
       - Compressed by default
       - Lowest priority for long-term archiving

4. **Integrity Mechanisms**:
   - SQLite `.backup` API for consistent database state
   - MD5 checksum generation and verification
   - PRAGMA integrity_check before and after backup
   - Verification of random sample of form data between source and backup
   - Validation of backup restoration in temp environment

### 13.2 **Implementation Code Example**

```python
def create_backup(self, db_path, backup_type="auto"):
    """Create a database backup with appropriate naming and storage.
    
    Args:
        db_path: Path to the source database
        backup_type: Type of backup ("auto", "manual", "daily", "weekly", "monthly")
    
    Returns:
        Path to the created backup file or None if failed
    """
    # Get backup directory based on configuration
    backup_dir = self._get_backup_directory()
    
    # Create date-based directory structure
    now = datetime.now()
    date_path = os.path.join(backup_dir, 
                             str(now.year),
                             f"{now.month:02d}",
                             f"{now.day:02d}")
    os.makedirs(date_path, exist_ok=True)
    
    # Generate backup filename
    db_name = os.path.basename(db_path)
    base_name, ext = os.path.splitext(db_name)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{base_name}_{timestamp}_{backup_type}{ext}"
    backup_path = os.path.join(date_path, backup_filename)
    
    # Create the backup using SQLite API
    try:
        # Verify source database integrity first
        source_conn = sqlite3.connect(db_path)
        cursor = source_conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()[0]
        
        if integrity_result != "ok":
            self.logger.error(f"Source database failed integrity check: {integrity_result}")
            raise ValueError("Cannot backup corrupted database")
            
        # Create backup
        backup_conn = sqlite3.connect(backup_path)
        source_conn.backup(backup_conn)
        
        # Verify backup integrity
        backup_cursor = backup_conn.cursor()
        backup_cursor.execute("PRAGMA integrity_check")
        backup_integrity = backup_cursor.fetchone()[0]
        
        if backup_integrity != "ok":
            self.logger.error(f"Backup failed integrity check: {backup_integrity}")
            os.remove(backup_path)
            raise ValueError("Backup verification failed")
            
        # Close connections
        backup_conn.close()
        source_conn.close()
        
        # Generate and store MD5 checksum
        checksum = self._calculate_md5(backup_path)
        with open(f"{backup_path}.md5", "w") as f:
            f.write(checksum)
            
        # Apply rotation policy
        self._apply_rotation_policy(backup_type)
        
        return backup_path
        
    except Exception as e:
        self.logger.error(f"Backup failed: {str(e)}")
        if os.path.exists(backup_path):
            os.remove(backup_path)
        return None
```

### 13.3 **Recovery Procedure Implementation**

The recovery process follows these steps:

1. **Backup Selection**:
   - Present user with sorted list of available backups
   - Display backup metadata (timestamp, type, size, verification status)
   - Allow filtering by date range or backup type

2. **Pre-Restoration Verification**:
   - Checksum verification against stored MD5
   - PRAGMA integrity_check on backup file
   - Verification of critical tables and record counts

3. **Restoration Process**:
   - Create backup of current database (recovery point)
   - Close all database connections
   - Copy selected backup to database location
   - Verify restored database integrity
   - Reconnect application to restored database

4. **Post-Restoration Verification**:
   - Validate form count matches expectation
   - Verify random sample of forms from different types
   - Generate restoration report (success/failure, validation results)

5. **Failure Handling**:
   - Automatic rollback to pre-restoration state on failure
   - Detailed error logging for troubleshooting
   - Option to attempt alternative backup if available

---

## 14. **Database Migration Support**

### 14.1 **Migration Implementation Timeline**

The application implements database schema evolution in phases:

#### Initial Release (Version 1.0.0)
* **Core Migration Framework**: Basic infrastructure for database schema updates
* **Schema Version Tracking**: Migration table with version history
* **Initialization Scripts**: Initial database schema creation scripts
* **Manual Migration Execution**: Developer-triggered migrations during development

#### Phase 1 Update (Version 1.1.0)
* **Automatic Migration Detection**: Application detects schema version mismatches on startup
* **Forward Migration Execution**: Ability to update database to latest schema version
* **Migration Integrity Verification**: Checksum validation of migration scripts
* **Transactional Migrations**: Ensure migrations are atomic (all-or-nothing)
* **Versioned Migration Scripts**: Migrations tied to application versions

#### Phase 2 Update (Version 1.2.0)
* **Rollback Support**: Ability to revert specific migrations
* **Advanced Schema Diff Detection**: Automated identification of schema changes
* **Migration Generation Tools**: Helper utilities to generate migration scripts
* **Data Migration Support**: Tools for moving data between schema versions
* **Migration Dry-Run Mode**: Preview migration changes without applying them

### 14.2 **Migration Implementation Details**

#### Migration Naming and Organization

Migrations follow a standardized naming convention:
```
V[version_number]__[description].sql
```

Example: `V1.0.1__add_status_column_to_forms.sql`

Migrations are stored in a dedicated `/migrations` directory in the application package and are executed in version order.

#### Migration Script Structure

Each migration script includes:
```sql
-- Migration: Add status column to forms table
-- Version: 1.0.1
-- Created: 2025-04-29
-- Author: Development Team

-- Description:
-- This migration adds a status column to the forms table to track form workflow state

-- Apply Migration
BEGIN TRANSACTION;

ALTER TABLE forms ADD COLUMN status TEXT NOT NULL DEFAULT 'Draft';
CREATE INDEX idx_forms_status ON forms(status);

-- Update migration record
INSERT INTO migrations (version, applied_at, description, checksum) 
VALUES ('1.0.1', datetime('now'), 'Add status column to forms table', 'fd5a91cb84e4160cc8149cd9a4e772a0');

COMMIT;

-- Rollback Migration (for version 1.2.0+)
/*
BEGIN TRANSACTION;

DROP INDEX IF EXISTS idx_forms_status;
ALTER TABLE forms DROP COLUMN status;

DELETE FROM migrations WHERE version = '1.0.1';

COMMIT;
*/
```

#### Migration Service Implementation

The migration service follows this algorithm:
1. On application startup, connect to database
2. Query the migrations table for applied migrations
3. Scan the migrations directory for available migration scripts
4. Compare available vs. applied migrations to identify pending migrations
5. Sort pending migrations by version number
6. For each pending migration:
   a. Calculate and verify script checksum
   b. Begin transaction
   c. Execute migration SQL
   d. Record migration in migrations table
   e. Commit transaction
7. If any migration fails, roll back transaction and halt startup with error

### 14.3 **Migration Error Handling**

Migration errors are treated as critical and require resolution before the application can operate:

1. **Schema Validation Failure**: If database schema doesn't match expected state
   - Event: `DB-C-001` critical error
   - Resolution: Guided recovery procedure using backups
   
2. **Migration Script Error**: If a SQL error occurs during migration
   - Event: `DB-C-002` critical error
   - Resolution: Developer analysis required
   
3. **Migration Integrity Error**: If a migration script checksum doesn't match
   - Event: `DB-C-003` critical error
   - Resolution: Manual verification and correction
   
4. **Migration Version Conflict**: If migrations are applied out of sequence
   - Event: `DB-C-004` critical error
   - Resolution: Database restoration from backup

### 14.4 **Migration Example Code**

```python
def run_migrations(self):
    """Run any pending database migrations"""
    # Get current database version
    current_version = self._get_current_version()
    self.logger.info(f"Current database version: {current_version}")
    
    # Get available migrations
    available_migrations = self._get_available_migrations()
    
    # Filter pending migrations
    pending_migrations = [
        m for m in available_migrations
        if self._compare_versions(m["version"], current_version) > 0
    ]
    
    if not pending_migrations:
        self.logger.info("No pending migrations")
        return
    
    # Sort by version
    pending_migrations.sort(key=lambda m: m["version"])
    
    for migration in pending_migrations:
        self.logger.info(f"Applying migration: {migration['version']} - {migration['description']}")
        
        try:
            # Verify migration script integrity
            script_content = self._read_migration_script(migration["path"])
            actual_checksum = self._calculate_checksum(script_content)
            
            if migration.get("checksum") and migration["checksum"] != actual_checksum:
                raise ValueError(f"Migration checksum verification failed: {migration['version']}")
            
            # Begin transaction
            self.connection.execute("BEGIN TRANSACTION")
            
            # Execute migration
            self.connection.executescript(script_content)
            
            # Add migration record if not already added by script
            self._verify_migration_recorded(migration["version"])
            
            # Commit transaction
            self.connection.execute("COMMIT")
            
            self.logger.info(f"Migration applied successfully: {migration['version']}")
            
        except Exception as e:
            # Roll back transaction
            self.connection.execute("ROLLBACK")
            self.logger.error(f"Migration failed: {str(e)}")
            
            # Create error event
            event_code = "DB-C-002"
            event_details = {
                "migration_version": migration["version"],
                "error": str(e)
            }
            
            self.error_handler.handle_error(
                event_code,
                "Migration Error",
                f"Database migration {migration['version']} failed: {str(e)}",
                event_details
            )
            
            raise RuntimeError(f"Migration {migration['version']} failed: {str(e)}")
```

---

## 15. **Entity-Relationship Structure (Extended)**

```
forms
 ├── form_versions
 ├── [ics form table] (e.g., ics214)
 │    ├── [repeating item table] (e.g., ics214_activity_log_items)
 │    └── [resource table] (e.g., ics214_resources_assigned)
 ├── attachments
 └── audit_logs

incidents
 └── forms

migrations
```

---

## 16. **Data Integrity Measures**

1. **Foreign Key Constraints**: Explicitly enforced for all relationships
2. **Transaction Management**: All critical operations use transactions
3. **Integrity Checks**: Periodic database integrity validation
4. **Checksum Verification**: For attachments and migrations
5. **WAL Mode**: Prevents corruption during unexpected shutdowns
6. **Concurrency Control**: Proper locking for multi-user scenarios

---

## 17. **Performance Optimizations**

1. **Indexing Strategy**: Carefully designed indexes for common queries
2. **Query Optimization**: Prepared statements and optimized queries
3. **Pagination**: Limit and offset for large result sets
4. **Caching**: Efficient data caching for frequently accessed data
5. **Compression**: Optional for large deployments
6. **Connection Pooling**: For concurrent access scenarios

---

## 18. **Security Considerations**

1. **Data Encryption**: Framework for encrypting sensitive data at rest
2. **Digital Signatures**: Support for form validation through signatures
3. **Role-Based Access**: Framework for future multi-user scenarios
4. **Audit Logging**: Comprehensive tracking of all data modifications
5. **Secure Deletion**: Options for securely removing sensitive data

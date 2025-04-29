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

### Parent Table: `ics214`

| Field | Type | Description |
|:------|:----|:------------|
| ics214_id | INTEGER PRIMARY KEY AUTOINCREMENT |
| form_id | INTEGER NOT NULL | FK to forms(form_id) |
| incident_name | TEXT NOT NULL |
| operational_period_start | DATETIME NOT NULL |
| operational_period_end | DATETIME NOT NULL |
| name | TEXT NOT NULL |
| ics_position | TEXT NOT NULL |
| home_agency | TEXT NOT NULL |
| prepared_by_name | TEXT NOT NULL |
| prepared_by_position | TEXT NOT NULL |
| prepared_by_signature | TEXT | File path to signature image |
| prepared_datetime | DATETIME NOT NULL |
| page_number | INTEGER |

**Foreign Key Constraints:**
```sql
FOREIGN KEY (form_id) REFERENCES forms(form_id) ON DELETE CASCADE
```

---

### Child Table 1: `ics214_activity_log_items`

| Field | Type | Description |
|:------|:----|:------------|
| activity_id | INTEGER PRIMARY KEY AUTOINCREMENT |
| ics214_id | INTEGER NOT NULL | FK to ics214(ics214_id) |
| activity_datetime | DATETIME NOT NULL |
| notable_activities | TEXT NOT NULL |

**Foreign Key Constraints:**
```sql
FOREIGN KEY (ics214_id) REFERENCES ics214(ics214_id) ON DELETE CASCADE
```

**Indexes:**
```sql
CREATE INDEX idx_ics214_activity_log_ics214_id ON ics214_activity_log_items(ics214_id);
CREATE INDEX idx_ics214_activity_datetime ON ics214_activity_log_items(activity_datetime);
```

---

### Child Table 2: `ics214_resources_assigned`

| Field | Type | Description |
|:------|:----|:------------|
| resource_id | INTEGER PRIMARY KEY AUTOINCREMENT |
| ics214_id | INTEGER NOT NULL | FK to ics214(ics214_id) |
| resource_name | TEXT NOT NULL |
| resource_position | TEXT |
| resource_home_agency | TEXT |

**Foreign Key Constraints:**
```sql
FOREIGN KEY (ics214_id) REFERENCES ics214(ics214_id) ON DELETE CASCADE
```

**Indexes:**
```sql
CREATE INDEX idx_ics214_resources_ics214_id ON ics214_resources_assigned(ics214_id);
```

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

---

## 13. **Backup Strategy**

The database backup strategy includes:

1. **Automatic Backup**: Created whenever the application is closed
2. **Rotation Policy**: Keeps up to 10 daily backups, 4 weekly backups, and 3 monthly backups
3. **Integrity Verification**: All backups are verified for integrity
4. **Compression**: Optional compression for large databases
5. **Recovery Procedure**: Documented process for restoring from backup

```sql
-- Example backup command
.backup FILENAME
```

---

## 14. **Database Migration Support**

The application supports schema evolution through migrations:

1. **Migration Tracking**: All migrations are recorded in the `migrations` table
2. **Version Control**: Each migration has a version number and description
3. **Integrity Checking**: Migrations are validated using checksums
4. **Rollback Support**: All migrations include rollback procedures
5. **Safety Measures**: Transactions ensure migrations are atomic

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
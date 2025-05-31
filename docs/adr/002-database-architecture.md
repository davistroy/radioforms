# ADR-002: SQLite Database Architecture for Offline-First Operation

## Status
Accepted

## Context
RadioForms is designed as an offline-first application for emergency management scenarios where internet connectivity may be unreliable or unavailable. The application needs to store and manage ICS form data with the following requirements:

- **Offline operation**: No cloud or network dependencies
- **Data integrity**: Reliable storage during emergency situations
- **Performance**: Fast read/write operations for real-time form management
- **Portability**: Single-file deployment with embedded database
- **Backup capability**: Easy data export and backup procedures
- **Concurrent access**: Multiple forms and operations simultaneously
- **ACID compliance**: Data consistency and reliability

## Decision
We will use SQLite with Write-Ahead Logging (WAL) mode as the primary database solution for RadioForms.

### Database Technology: SQLite
- **Engine**: SQLite 3.38+ with WAL mode enabled
- **Location**: Local file in application directory (user-configurable)
- **Schema**: Relational design with JSON fields for form data
- **Backup**: File-based backup with rotation policies

### Connection Management
- **Pattern**: Connection pooling with context managers
- **Transactions**: Explicit transaction handling for data integrity
- **Error handling**: Comprehensive exception handling with rollback
- **Thread safety**: Thread-safe operations for UI responsiveness

### Data Storage Strategy
- **Forms table**: Metadata and form lifecycle information
- **JSON storage**: Complete form data as JSON for flexibility
- **Indexing**: Strategic indexes on frequently queried fields
- **Versioning**: Timestamp-based versioning for audit trails

## Architecture Details

### Database Schema
```sql
-- Main forms table
CREATE TABLE forms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_type TEXT NOT NULL,
    form_number TEXT NOT NULL,
    incident_name TEXT,
    title TEXT,
    data TEXT,  -- JSON blob containing form data
    status TEXT DEFAULT 'draft',
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

-- Indexes for performance
CREATE INDEX idx_forms_incident ON forms(incident_name);
CREATE INDEX idx_forms_type ON forms(form_type);
CREATE INDEX idx_forms_created ON forms(created_at);
CREATE INDEX idx_forms_status ON forms(status);
CREATE UNIQUE INDEX idx_forms_number ON forms(form_number);
```

### Connection Management Pattern
```python
class DatabaseManager:
    """Manages SQLite database connections with WAL mode."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._setup_database()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper cleanup."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            yield conn
        finally:
            conn.close()
    
    @contextmanager
    def get_transaction(self):
        """Get transactional connection with rollback support."""
        with self.get_connection() as conn:
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
```

## Rationale

### Why SQLite?
1. **Offline-first**: Embedded database with no server dependencies
2. **Reliability**: ACID compliance and proven stability
3. **Performance**: Excellent performance for single-user applications
4. **Simplicity**: No installation or configuration required
5. **Portability**: Single file can be easily backed up and transferred
6. **Mature ecosystem**: Well-supported by Python and tooling

### Why WAL Mode?
1. **Concurrency**: Allows simultaneous readers during writes
2. **Performance**: Better write performance than rollback journaling
3. **Reliability**: Reduces chances of database corruption
4. **Atomic operations**: Ensures data consistency

### Why JSON Storage for Form Data?
1. **Flexibility**: Form structures can evolve without schema migrations
2. **Simplicity**: Direct mapping from Python objects to storage
3. **Completeness**: Preserves all form data including optional fields
4. **Version tolerance**: Backward compatibility with form versions

## Alternatives Considered

### 1. Pure File-based Storage
- **Pros**: Simple implementation, no database dependencies
- **Cons**: No ACID properties, difficult querying, no indexing
- **Rejected**: Insufficient for reliability requirements

### 2. Cloud Database (PostgreSQL/MySQL + Cloud)
- **Pros**: Powerful querying, multi-user support, remote access
- **Cons**: Requires internet connectivity, complex deployment
- **Rejected**: Violates offline-first requirement

### 3. NoSQL Document Database (MongoDB, etc.)
- **Pros**: Natural fit for form data, flexible schema
- **Cons**: Additional dependency, larger deployment size
- **Rejected**: Unnecessary complexity for single-user application

### 4. In-Memory Database (Redis, etc.)
- **Pros**: Extremely fast operations
- **Cons**: Data persistence challenges, memory limitations
- **Rejected**: Insufficient durability for critical emergency data

## Implementation Guidelines

### Connection Patterns
```python
# Always use context managers for connections
with db_manager.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM forms WHERE id = ?", (form_id,))
    return cursor.fetchone()

# Use transactions for multi-step operations
with db_manager.get_transaction() as conn:
    cursor = conn.cursor()
    cursor.execute("INSERT INTO forms (...) VALUES (...)", values)
    form_id = cursor.lastrowid
    cursor.execute("UPDATE forms SET updated_at = ? WHERE id = ?", 
                  (datetime.now(), form_id))
```

### Error Handling
```python
try:
    with db_manager.get_transaction() as conn:
        # Database operations
        pass
except sqlite3.IntegrityError as e:
    raise DatabaseError(f"Data integrity violation: {e}")
except sqlite3.OperationalError as e:
    raise DatabaseError(f"Database operation failed: {e}")
except Exception as e:
    logger.error(f"Unexpected database error: {e}")
    raise DatabaseError(f"Database operation failed")
```

### Performance Optimizations
- Use prepared statements for repeated queries
- Batch operations when possible
- Maintain appropriate indexes
- Use EXPLAIN QUERY PLAN for optimization
- Regular VACUUM operations for maintenance

## Consequences

### Positive
- **Reliability**: ACID compliance ensures data integrity
- **Simplicity**: No external dependencies or complex setup
- **Performance**: Fast operations suitable for real-time use
- **Portability**: Single file deployment and backup
- **Offline capability**: Fully functional without network access

### Negative
- **Single-user limitation**: Not designed for concurrent multi-user access
- **File size growth**: Database file can grow large over time
- **Limited query capabilities**: Not as powerful as full SQL databases
- **Backup complexity**: WAL mode requires special backup procedures

### Mitigation Strategies
- **Size management**: Implement data archiving and cleanup procedures
- **Backup procedures**: Automated backup creation with proper WAL handling
- **Monitoring**: Database size and performance monitoring
- **Migration path**: Design allows future migration to client-server if needed

## Performance Characteristics

### Expected Performance (on typical hardware)
- **Form save**: < 50ms for typical ICS-213 form
- **Form load**: < 20ms for single form retrieval
- **Form list**: < 100ms for 1000+ forms with pagination
- **Database startup**: < 500ms for database initialization
- **Backup creation**: < 2 seconds for typical database

### Scalability Limits
- **Maximum forms**: 50,000+ forms (limited by available storage)
- **Maximum database size**: 281TB (SQLite theoretical limit)
- **Practical limit**: 10GB database size for optimal performance
- **Concurrent operations**: Single writer, multiple readers

## Monitoring and Maintenance

### Regular Maintenance Tasks
- **VACUUM**: Monthly database optimization
- **ANALYZE**: Update query planner statistics
- **Backup**: Daily automated backups with rotation
- **Size monitoring**: Alert when database approaches size limits

### Performance Monitoring
- Query execution time logging
- Database file size tracking
- WAL file size monitoring
- Connection pool usage statistics

## Migration Considerations

### Future Migration Paths
1. **Client-Server Migration**: Design allows future migration to PostgreSQL
2. **Cloud Integration**: Could add cloud sync while maintaining local storage
3. **Multi-user Support**: Architecture supports future multi-user enhancements
4. **Replication**: WAL mode supports future replication scenarios

### Data Portability
- JSON export functionality for data migration
- Standard SQL schema for easy data extraction
- Documented format for third-party integration
- Backup files are standard SQLite format

## References
- [SQLite Documentation](https://sqlite.org/docs.html)
- [SQLite WAL Mode](https://sqlite.org/wal.html)
- [Python SQLite3 Module](https://docs.python.org/3/library/sqlite3.html)
- [CLAUDE.md Project Guidelines](../CLAUDE.md)
- [Database Performance Best Practices](https://sqlite.org/optoverview.html)
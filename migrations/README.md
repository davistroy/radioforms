# Database Migrations

This directory contains database migration scripts for the RadioForms application. These scripts are managed by Alembic, which handles the evolution of the database schema over time.

## Overview

- Migrations are stored in `versions/` and track changes to the database schema
- Each migration has a unique identifier and a descriptive name
- Migrations can be applied incrementally to update the database schema
- Migrations can be reversed to downgrade the schema if needed

## Directory Structure

- `env.py` - Environment configuration for Alembic
- `script.py.mako` - Template for new migration scripts
- `versions/` - Migration script files

## Usage

### Creating a New Migration

To create a new migration automatically based on model changes:

```bash
alembic revision --autogenerate -m "Description of changes"
```

This command will:
1. Compare the current database schema with the SQLAlchemy model definitions
2. Generate a new migration script in the `versions/` directory
3. Record the detected changes as Python code in the migration script

You can also create an empty migration and fill in the changes manually:

```bash
alembic revision -m "Description of changes"
```

### Applying Migrations

To apply all pending migrations to the latest version:

```bash
alembic upgrade head
```

To apply migrations up to a specific version:

```bash
alembic upgrade <revision_id>
```

### Downgrading

To downgrade to a previous version:

```bash
alembic downgrade <revision_id>
```

To downgrade one version:

```bash
alembic downgrade -1
```

### Viewing Migration Information

To see the current version:

```bash
alembic current
```

To see migration history:

```bash
alembic history
```

## Migration Script Structure

Each migration script includes two main functions:

- `upgrade()` - Code to apply the migration
- `downgrade()` - Code to reverse the migration

Example migration script:

```python
"""Description of changes

Revision ID: abc123def456
Revises: previous_revision_id
Create Date: 2025-05-02 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123def456'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None

def upgrade():
    # Create a new table
    op.create_table('example_table',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    # Drop the table created in upgrade()
    op.drop_table('example_table')
```

## Best Practices

1. **Descriptive Names**: Use clear, descriptive names for migration scripts
2. **Small Changes**: Keep migrations focused on specific changes
3. **Test Migrations**: Test both upgrade and downgrade operations
4. **Review Generated Migrations**: Always review auto-generated migrations before applying them
5. **Version Control**: Commit migration scripts to version control

## Troubleshooting

### Migration Conflicts

If you encounter conflicts between migrations, you may need to:
1. Identify the conflicting changes
2. Create a new migration that resolves the conflicts
3. Apply the resolution migration

### Failed Migrations

If a migration fails:
1. Check the error message for details
2. Fix the issue in a new migration or by modifying the failed migration
3. Run the migration again

For complex issues, you may need to:
1. Manually correct the database schema
2. Mark the migration as completed using `alembic stamp <revision_id>`

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

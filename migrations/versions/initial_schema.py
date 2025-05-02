"""Initial schema

Revision ID: 001
Create Date: 2025-05-02 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create incidents table
    op.create_table('incidents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('incident_number', sa.String(50)),
        sa.Column('type', sa.String(50)),
        sa.Column('location', sa.String(100)),
        sa.Column('start_date', sa.String(20)),
        sa.Column('end_date', sa.String(20)),
        sa.Column('status', sa.String(20)),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('incident_id')
    )
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('callsign', sa.String(20)),
        sa.Column('position', sa.String(50)),
        sa.Column('email', sa.String(100)),
        sa.Column('phone', sa.String(20)),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Create operational_periods table
    op.create_table('operational_periods',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('op_period_id', sa.String(36), nullable=False),
        sa.Column('incident_id', sa.String(36), nullable=False),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('op_period_id'),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.incident_id'])
    )
    
    # Create forms table
    op.create_table('forms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('form_id', sa.String(36), nullable=False),
        sa.Column('incident_id', sa.String(36)),
        sa.Column('op_period_id', sa.String(36)),
        sa.Column('form_type', sa.String(20), nullable=False),
        sa.Column('state', sa.String(20)),
        sa.Column('title', sa.String(150)),
        sa.Column('data', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('created_by', sa.String(36)),
        sa.Column('updated_by', sa.String(36)),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('form_id'),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.incident_id']),
        sa.ForeignKeyConstraint(['op_period_id'], ['operational_periods.op_period_id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.user_id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.user_id'])
    )
    
    # Create form_versions table
    op.create_table('form_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('version_id', sa.String(36), nullable=False),
        sa.Column('form_id', sa.String(36), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('created_by', sa.String(36)),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('version_id'),
        sa.ForeignKeyConstraint(['form_id'], ['forms.form_id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.user_id'])
    )
    
    # Create attachments table
    op.create_table('attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('attachment_id', sa.String(36), nullable=False),
        sa.Column('form_id', sa.String(36), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('content_type', sa.String(100), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('path', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('attachment_id'),
        sa.ForeignKeyConstraint(['form_id'], ['forms.form_id'])
    )
    
    # Create settings table
    op.create_table('settings',
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('key')
    )

def downgrade():
    # Drop tables in reverse dependency order
    op.drop_table('attachments')
    op.drop_table('form_versions')
    op.drop_table('forms')
    op.drop_table('operational_periods')
    op.drop_table('users')
    op.drop_table('incidents')
    op.drop_table('settings')

# RadioForms Refactoring Instructions for Cline AI

This document provides step-by-step coding instructions for refactoring the RadioForms application to improve its architecture. Each step is designed to be executable by Cline AI and builds sequentially toward the improved architecture.

## Phase 1: Database Layer Refactoring

### Step 1: Set up SQLAlchemy and Alembic
```
Install SQLAlchemy and Alembic packages and set up the initial configuration.

1. Run: pip install sqlalchemy alembic
2. Create a file at radioforms/database/orm_models.py
3. Create a file at radioforms/database/repositories.py
4. Initialize Alembic with: alembic init migrations
5. Configure Alembic in alembic.ini to point to your project
```

### Step 2: Create SQLAlchemy Models
```python
# Create the following code in radioforms/database/orm_models.py

import datetime
import json
from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class Incident(Base):
    __tablename__ = 'incidents'
    
    id = Column(Integer, primary_key=True)
    incident_id = Column(String(36), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    incident_number = Column(String(50))
    type = Column(String(50))
    location = Column(String(100))
    start_date = Column(String(20))
    end_date = Column(String(20))
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    forms = relationship("Form", back_populates="incident", cascade="all, delete-orphan")
    op_periods = relationship("OperationalPeriod", back_populates="incident", cascade="all, delete-orphan")

class OperationalPeriod(Base):
    __tablename__ = 'operational_periods'
    
    id = Column(Integer, primary_key=True)
    op_period_id = Column(String(36), unique=True, nullable=False)
    incident_id = Column(String(36), ForeignKey('incidents.incident_id'), nullable=False)
    number = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    incident = relationship("Incident", back_populates="op_periods")
    forms = relationship("Form", back_populates="op_period")

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(36), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    callsign = Column(String(20))
    position = Column(String(50))
    email = Column(String(100))
    phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    created_forms = relationship("Form", foreign_keys="Form.created_by", back_populates="creator")
    updated_forms = relationship("Form", foreign_keys="Form.updated_by", back_populates="updater")

class Form(Base):
    __tablename__ = 'forms'
    
    id = Column(Integer, primary_key=True)
    form_id = Column(String(36), unique=True, nullable=False)
    incident_id = Column(String(36), ForeignKey('incidents.incident_id'))
    op_period_id = Column(String(36), ForeignKey('operational_periods.op_period_id'))
    form_type = Column(String(20), nullable=False)
    state = Column(String(20), default='draft')
    title = Column(String(150))
    data = Column(Text, nullable=False)  # JSON data
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    created_by = Column(String(36), ForeignKey('users.user_id'))
    updated_by = Column(String(36), ForeignKey('users.user_id'))
    
    incident = relationship("Incident", back_populates="forms")
    op_period = relationship("OperationalPeriod", back_populates="forms")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_forms")
    updater = relationship("User", foreign_keys=[updated_by], back_populates="updated_forms")
    versions = relationship("FormVersion", back_populates="form", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="form", cascade="all, delete-orphan")

class FormVersion(Base):
    __tablename__ = 'form_versions'
    
    id = Column(Integer, primary_key=True)
    version_id = Column(String(36), unique=True, nullable=False)
    form_id = Column(String(36), ForeignKey('forms.form_id'), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)  # JSON data
    created_at = Column(DateTime, default=datetime.datetime.now)
    created_by = Column(String(36), ForeignKey('users.user_id'))
    
    form = relationship("Form", back_populates="versions")

class Attachment(Base):
    __tablename__ = 'attachments'
    
    id = Column(Integer, primary_key=True)
    attachment_id = Column(String(36), unique=True, nullable=False)
    form_id = Column(String(36), ForeignKey('forms.form_id'), nullable=False)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    size = Column(Integer, nullable=False)
    path = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    form = relationship("Form", back_populates="attachments")

class Setting(Base):
    __tablename__ = 'settings'
    
    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
```

### Step 3: Create Repository Pattern Implementation
```python
# Create the following code in radioforms/database/repositories.py

import json
import uuid
import datetime
from typing import Dict, Any, List, Optional, Tuple, Union, cast
from sqlalchemy.orm import Session

from radioforms.database.orm_models import (
    Base, Incident, OperationalPeriod, User, Form, FormVersion, 
    Attachment, Setting
)

class BaseRepository:
    """Base repository with common functionality"""
    
    def __init__(self, session: Session):
        self.session = session

class FormRepository(BaseRepository):
    """Repository for Form entities"""
    
    def get_by_id(self, form_id: str) -> Optional[Form]:
        """Get a form by ID"""
        return self.session.query(Form).filter(Form.form_id == form_id).first()
    
    def get_all(self) -> List[Form]:
        """Get all forms"""
        return self.session.query(Form).all()
    
    def get_by_incident(self, incident_id: str) -> List[Form]:
        """Get forms for an incident"""
        return self.session.query(Form).filter(Form.incident_id == incident_id).all()
    
    def create(self, form_data: Dict[str, Any]) -> Form:
        """Create a new form"""
        # Ensure form_id exists
        if 'form_id' not in form_data:
            form_data['form_id'] = str(uuid.uuid4())
            
        # Ensure timestamps exist
        now = datetime.datetime.now()
        if 'created_at' not in form_data:
            form_data['created_at'] = now
        if 'updated_at' not in form_data:
            form_data['updated_at'] = now
            
        # JSON encode data field if it's a dict
        if 'data' in form_data and isinstance(form_data['data'], dict):
            form_data['data'] = json.dumps(form_data['data'])
            
        form = Form(**form_data)
        self.session.add(form)
        self.session.commit()
        return form
    
    def update(self, form_id: str, form_data: Dict[str, Any]) -> Optional[Form]:
        """Update an existing form"""
        form = self.get_by_id(form_id)
        if not form:
            return None
            
        # Update timestamp
        form_data['updated_at'] = datetime.datetime.now()
        
        # JSON encode data field if it's a dict
        if 'data' in form_data and isinstance(form_data['data'], dict):
            form_data['data'] = json.dumps(form_data['data'])
            
        # Update attributes
        for key, value in form_data.items():
            if hasattr(form, key):
                setattr(form, key, value)
                
        self.session.commit()
        return form
    
    def delete(self, form_id: str) -> bool:
        """Delete a form"""
        form = self.get_by_id(form_id)
        if not form:
            return False
            
        self.session.delete(form)
        self.session.commit()
        return True
    
    def find_with_content(self, form_id: str, version: Optional[int] = None) -> Optional[Tuple[Form, Dict[str, Any]]]:
        """Get a form with its content"""
        form = self.get_by_id(form_id)
        if not form:
            return None
            
        # Get content from versions or form data
        content_dict = {}
        
        if version is not None:
            # Get specific version
            version_obj = (self.session.query(FormVersion)
                          .filter(FormVersion.form_id == form_id, 
                                  FormVersion.version == version)
                          .first())
            
            if version_obj:
                try:
                    content_dict = json.loads(version_obj.content)
                except json.JSONDecodeError:
                    content_dict = {}
        else:
            # Get form data
            try:
                content_dict = json.loads(form.data)
            except json.JSONDecodeError:
                content_dict = {}
                
        return form, content_dict
    
    def create_version(self, form_id: str, content: Union[str, Dict[str, Any]], 
                      created_by: Optional[str] = None) -> Optional[FormVersion]:
        """Create a new version of a form"""
        form = self.get_by_id(form_id)
        if not form:
            return None
            
        # Get current max version
        max_version = (self.session.query(FormVersion)
                      .filter(FormVersion.form_id == form_id)
                      .order_by(FormVersion.version.desc())
                      .first())
                      
        new_version_num = 1 if max_version is None else max_version.version + 1
        
        # Prepare content
        if isinstance(content, dict):
            content_str = json.dumps(content)
        else:
            content_str = content
            
        # Create version
        version = FormVersion(
            version_id=str(uuid.uuid4()),
            form_id=form_id,
            version=new_version_num,
            content=content_str,
            created_at=datetime.datetime.now(),
            created_by=created_by
        )
        
        self.session.add(version)
        self.session.commit()
        return version

# Add similar repositories for Incident, User, Attachment, etc.
```

### Step 4: Create Database Manager with SQLAlchemy
```python
# Create a new file at radioforms/database/db_manager_sqlalchemy.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import os
import logging

from radioforms.database.orm_models import Base

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager using SQLAlchemy"""
    
    def __init__(self, db_url=None):
        """Initialize database manager"""
        self.db_url = db_url or 'sqlite:///radioforms.db'
        self.engine = None
        self.session_factory = None
        self._session = None
        
    def init_db(self):
        """Initialize the database connection and create tables"""
        try:
            # Create engine
            self.engine = create_engine(self.db_url)
            
            # Create session factory
            self.session_factory = sessionmaker(bind=self.engine)
            
            # Create tables
            Base.metadata.create_all(self.engine)
            
            logger.info(f"Database initialized at {self.db_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            return False
            
    def get_session(self):
        """Get a session for database operations"""
        if not self.session_factory:
            self.init_db()
            
        if not self._session:
            self._session = self.session_factory()
            
        return self._session
        
    def close(self):
        """Close database connection"""
        if self._session:
            self._session.close()
            self._session = None
            
        logger.debug("Database connection closed")
```

### Step 5: Create Migration Script
```python
# Create a new file at migrations/versions/initial_schema.py

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
```

## Phase 2: Form Model Refactoring

### Step 6: Create Base Form Dataclass
```python
# Create a new file at radioforms/models/dataclass_forms.py

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union
import uuid
import json

class FormState(Enum):
    """Represents the possible states of a form"""
    DRAFT = "draft"
    APPROVED = "approved"
    TRANSMITTED = "transmitted"
    RECEIVED = "received"
    REPLIED = "replied"
    RETURNED = "returned"
    ARCHIVED = "archived"

@dataclass
class BaseForm:
    """Base class for all form models"""
    form_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    form_type: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    state: FormState = field(default=FormState.DRAFT)
    title: str = ""
    incident_id: Optional[str] = None
    creator_id: Optional[str] = None
    
    def validate(self) -> Dict[str, str]:
        """Validate form data and return dictionary of errors"""
        errors = {}
        
        if not self.title:
            errors["title"] = "Title is required"
            
        return errors
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        
        # Handle special types
        data["state"] = self.state.value
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseForm':
        """Create from dictionary"""
        # Make a copy to avoid modifying the original
        data_copy = data.copy()
        
        # Handle special types
        if "state" in data_copy:
            try:
                data_copy["state"] = FormState(data_copy["state"])
            except ValueError:
                data_copy["state"] = FormState.DRAFT
                
        if "created_at" in data_copy and isinstance(data_copy["created_at"], str):
            try:
                data_copy["created_at"] = datetime.fromisoformat(data_copy["created_at"])
            except ValueError:
                data_copy["created_at"] = datetime.now()
                
        if "updated_at" in data_copy and isinstance(data_copy["updated_at"], str):
            try:
                data_copy["updated_at"] = datetime.fromisoformat(data_copy["updated_at"])
            except ValueError:
                data_copy["updated_at"] = datetime.now()
                
        return cls(**data_copy)
```

### Step 7: Create ICS-213 Form Dataclass
```python
# Add the following to radioforms/models/dataclass_forms.py

@dataclass
class ICS213Form(BaseForm):
    """ICS-213 General Message form model"""
    form_type: str = "ICS-213"
    
    # Message information
    to: str = ""
    to_position: str = ""
    from_field: str = ""
    from_position: str = ""
    subject: str = ""
    message: str = ""
    message_date: datetime = field(default_factory=datetime.now)
    
    # Sender information
    sender_name: str = ""
    sender_position: str = ""
    sender_signature: str = ""
    sender_date: Optional[datetime] = None
    
    # Recipient information
    recipient_name: str = ""
    recipient_position: str = ""
    recipient_signature: str = ""
    recipient_date: Optional[datetime] = None
    reply: str = ""
    
    # Reference information
    incident_name: str = ""
    priority: str = "Routine"  # Routine, Priority, or Immediate
    
    def __post_init__(self):
        """Initialize after dataclass init"""
        if not self.title and self.subject:
            self.title = self.subject
            
        if not self.sender_date:
            self.sender_date = self.created_at
    
    def validate(self) -> Dict[str, str]:
        """Validate form data and return dictionary of errors"""
        errors = super().validate()
        
        # Required fields
        if not self.to:
            errors["to"] = "To field is required"
            
        if not self.from_field:
            errors["from_field"] = "From field is required"
            
        if not self.subject:
            errors["subject"] = "Subject is required"
            
        if not self.message:
            errors["message"] = "Message content is required"
            
        # Field length validations
        max_lengths = {
            "to": 100,
            "to_position": 100,
            "from_field": 100,
            "from_position": 100,
            "subject": 150,
            "message": 2000,
            "sender_name": 100,
            "sender_position": 100,
            "recipient_name": 100,
            "recipient_position": 100,
            "reply": 1000,
            "incident_name": 100
        }
        
        for field, max_length in max_lengths.items():
            value = getattr(self, field)
            if value and len(str(value)) > max_length:
                errors[field] = f"{field.replace('_', ' ').title()} cannot exceed {max_length} characters"
        
        # State-specific validations
        if self.state == FormState.APPROVED and not self.sender_signature:
            errors["sender_signature"] = "Approved messages must have a sender signature"
            
        if self.state == FormState.REPLIED and not self.reply:
            errors["reply"] = "Replied messages must include reply content"
            
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = super().to_dict()
        
        # Handle date fields
        if self.message_date:
            data["message_date"] = self.message_date.isoformat()
            
        if self.sender_date:
            data["sender_date"] = self.sender_date.isoformat()
            
        if self.recipient_date:
            data["recipient_date"] = self.recipient_date.isoformat()
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ICS213Form':
        """Create from dictionary"""
        # Make a copy to avoid modifying the original
        data_copy = data.copy()
        
        # Handle date fields
        for date_field in ["message_date", "sender_date", "recipient_date"]:
            if date_field in data_copy and isinstance(data_copy[date_field], str):
                try:
                    data_copy[date_field] = datetime.fromisoformat(data_copy[date_field])
                except ValueError:
                    if date_field == "message_date":
                        data_copy[date_field] = datetime.now()
                    else:
                        data_copy[date_field] = None
                        
        return super().from_dict.__func__(cls, data_copy)
    
    # State transition methods
    def approve(self, approver_name: str, approver_position: str, approver_signature: str) -> bool:
        """
        Approve the form.
        
        Args:
            approver_name: Name of the approver
            approver_position: Position of the approver
            approver_signature: Signature of the approver
            
        Returns:
            True if the state was changed, False if not
        """
        if self.state != FormState.DRAFT:
            return False
            
        # Set approver information
        self.sender_name = approver_name
        self.sender_position = approver_position
        self.sender_signature = approver_signature
        self.sender_date = datetime.now()
        
        # Update state
        self.state = FormState.APPROVED
        self.updated_at = datetime.now()
        return True
        
    def transmit(self) -> bool:
        """
        Mark the form as transmitted.
        
        Returns:
            True if the state was changed, False if not
        """
        if self.state not in [FormState.DRAFT, FormState.APPROVED]:
            return False
            
        self.state = FormState.TRANSMITTED
        self.updated_at = datetime.now()
        return True
        
    def receive(self, recipient_name: str, recipient_position: str) -> bool:
        """
        Mark the form as received.
        
        Args:
            recipient_name: Name of the recipient
            recipient_position: Position of the recipient
            
        Returns:
            True if the state was changed, False if not
        """
        if self.state != FormState.TRANSMITTED:
            return False
            
        self.recipient_name = recipient_name
        self.recipient_position = recipient_position
        self.recipient_date = datetime.now()
        
        self.state = FormState.RECEIVED
        self.updated_at = datetime.now()
        return True
```

### Step 8: Create ICS-214 Form Dataclass
```python
# Add the following to radioforms/models/dataclass_forms.py

@dataclass
class ActivityLogEntry:
    """Activity log entry for ICS-214 form"""
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    time: datetime = field(default_factory=datetime.now)
    activity: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "entry_id": self.entry_id,
            "time": self.time.isoformat() if self.time else None,
            "activity": self.activity
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActivityLogEntry':
        """Create from dictionary"""
        entry_id = data.get("entry_id", str(uuid.uuid4()))
        
        # Parse time
        time = None
        if "time" in data and data["time"]:
            try:
                time = datetime.fromisoformat(data["time"])

```
## Phase 3: Update PRD, TDD, and all other relevant documentation

### Step 1: Analyze all documentation
```
1. Find all documentation files in the project
2. Analyze each and identify an updates required
```
### Step 2: Update documentation
```
1. Update all documents based on the analysis from Step 1
```
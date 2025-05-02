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

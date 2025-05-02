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

class IncidentRepository(BaseRepository):
    """Repository for Incident entities"""
    
    def get_by_id(self, incident_id: str) -> Optional[Incident]:
        """Get an incident by ID"""
        return self.session.query(Incident).filter(Incident.incident_id == incident_id).first()
    
    def get_all(self) -> List[Incident]:
        """Get all incidents"""
        return self.session.query(Incident).all()
    
    def create(self, incident_data: Dict[str, Any]) -> Incident:
        """Create a new incident"""
        # Ensure incident_id exists
        if 'incident_id' not in incident_data:
            incident_data['incident_id'] = str(uuid.uuid4())
            
        # Ensure timestamps exist
        now = datetime.datetime.now()
        if 'created_at' not in incident_data:
            incident_data['created_at'] = now
        if 'updated_at' not in incident_data:
            incident_data['updated_at'] = now
            
        incident = Incident(**incident_data)
        self.session.add(incident)
        self.session.commit()
        return incident
    
    def update(self, incident_id: str, incident_data: Dict[str, Any]) -> Optional[Incident]:
        """Update an existing incident"""
        incident = self.get_by_id(incident_id)
        if not incident:
            return None
            
        # Update timestamp
        incident_data['updated_at'] = datetime.datetime.now()
        
        # Update attributes
        for key, value in incident_data.items():
            if hasattr(incident, key):
                setattr(incident, key, value)
                
        self.session.commit()
        return incident
    
    def delete(self, incident_id: str) -> bool:
        """Delete an incident"""
        incident = self.get_by_id(incident_id)
        if not incident:
            return False
            
        self.session.delete(incident)
        self.session.commit()
        return True
        
class UserRepository(BaseRepository):
    """Repository for User entities"""
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        return self.session.query(User).filter(User.user_id == user_id).first()
    
    def get_all(self) -> List[User]:
        """Get all users"""
        return self.session.query(User).all()
    
    def create(self, user_data: Dict[str, Any]) -> User:
        """Create a new user"""
        # Ensure user_id exists
        if 'user_id' not in user_data:
            user_data['user_id'] = str(uuid.uuid4())
            
        # Ensure timestamps exist
        now = datetime.datetime.now()
        if 'created_at' not in user_data:
            user_data['created_at'] = now
        if 'updated_at' not in user_data:
            user_data['updated_at'] = now
            
        user = User(**user_data)
        self.session.add(user)
        self.session.commit()
        return user
    
    def update(self, user_id: str, user_data: Dict[str, Any]) -> Optional[User]:
        """Update an existing user"""
        user = self.get_by_id(user_id)
        if not user:
            return None
            
        # Update timestamp
        user_data['updated_at'] = datetime.datetime.now()
        
        # Update attributes
        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
                
        self.session.commit()
        return user
    
    def delete(self, user_id: str) -> bool:
        """Delete a user"""
        user = self.get_by_id(user_id)
        if not user:
            return False
            
        self.session.delete(user)
        self.session.commit()
        return True

class AttachmentRepository(BaseRepository):
    """Repository for Attachment entities"""
    
    def get_by_id(self, attachment_id: str) -> Optional[Attachment]:
        """Get an attachment by ID"""
        return self.session.query(Attachment).filter(Attachment.attachment_id == attachment_id).first()
    
    def get_by_form(self, form_id: str) -> List[Attachment]:
        """Get all attachments for a form"""
        return self.session.query(Attachment).filter(Attachment.form_id == form_id).all()
    
    def create(self, attachment_data: Dict[str, Any]) -> Attachment:
        """Create a new attachment"""
        # Ensure attachment_id exists
        if 'attachment_id' not in attachment_data:
            attachment_data['attachment_id'] = str(uuid.uuid4())
            
        # Ensure timestamps exist
        now = datetime.datetime.now()
        if 'created_at' not in attachment_data:
            attachment_data['created_at'] = now
        if 'updated_at' not in attachment_data:
            attachment_data['updated_at'] = now
            
        attachment = Attachment(**attachment_data)
        self.session.add(attachment)
        self.session.commit()
        return attachment
    
    def delete(self, attachment_id: str) -> bool:
        """Delete an attachment"""
        attachment = self.get_by_id(attachment_id)
        if not attachment:
            return False
            
        self.session.delete(attachment)
        self.session.commit()
        return True

class OperationalPeriodRepository(BaseRepository):
    """Repository for OperationalPeriod entities"""
    
    def get_by_id(self, op_period_id: str) -> Optional[OperationalPeriod]:
        """Get an operational period by ID"""
        return self.session.query(OperationalPeriod).filter(OperationalPeriod.op_period_id == op_period_id).first()
    
    def get_by_incident(self, incident_id: str) -> List[OperationalPeriod]:
        """Get all operational periods for an incident"""
        return self.session.query(OperationalPeriod).filter(OperationalPeriod.incident_id == incident_id).all()
    
    def create(self, op_period_data: Dict[str, Any]) -> OperationalPeriod:
        """Create a new operational period"""
        # Ensure op_period_id exists
        if 'op_period_id' not in op_period_data:
            op_period_data['op_period_id'] = str(uuid.uuid4())
            
        # Ensure timestamps exist
        now = datetime.datetime.now()
        if 'created_at' not in op_period_data:
            op_period_data['created_at'] = now
        if 'updated_at' not in op_period_data:
            op_period_data['updated_at'] = now
            
        op_period = OperationalPeriod(**op_period_data)
        self.session.add(op_period)
        self.session.commit()
        return op_period
    
    def update(self, op_period_id: str, op_period_data: Dict[str, Any]) -> Optional[OperationalPeriod]:
        """Update an existing operational period"""
        op_period = self.get_by_id(op_period_id)
        if not op_period:
            return None
            
        # Update timestamp
        op_period_data['updated_at'] = datetime.datetime.now()
        
        # Update attributes
        for key, value in op_period_data.items():
            if hasattr(op_period, key):
                setattr(op_period, key, value)
                
        self.session.commit()
        return op_period
    
    def delete(self, op_period_id: str) -> bool:
        """Delete an operational period"""
        op_period = self.get_by_id(op_period_id)
        if not op_period:
            return False
            
        self.session.delete(op_period)
        self.session.commit()
        return True

class SettingRepository(BaseRepository):
    """Repository for application settings"""
    
    def get(self, key: str) -> Optional[str]:
        """Get a setting value by key"""
        setting = self.session.query(Setting).filter(Setting.key == key).first()
        return setting.value if setting else None
    
    def set(self, key: str, value: str) -> Setting:
        """Set a setting value"""
        setting = self.session.query(Setting).filter(Setting.key == key).first()
        
        if setting:
            setting.value = value
            setting.updated_at = datetime.datetime.now()
        else:
            setting = Setting(key=key, value=value)
            self.session.add(setting)
            
        self.session.commit()
        return setting
    
    def delete(self, key: str) -> bool:
        """Delete a setting"""
        setting = self.session.query(Setting).filter(Setting.key == key).first()
        if not setting:
            return False
            
        self.session.delete(setting)
        self.session.commit()
        return True
        
    def get_all(self) -> Dict[str, str]:
        """Get all settings as a dictionary"""
        settings = self.session.query(Setting).all()
        return {setting.key: setting.value for setting in settings}

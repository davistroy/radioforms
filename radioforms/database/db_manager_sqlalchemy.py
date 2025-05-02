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

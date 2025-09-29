# backend/app/models/base.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime
from ..database import Base

class TimestampMixin:
    """Mixin class to add timestamp fields"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BaseModel(Base, TimestampMixin):
    """Base model class with common fields"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, nullable=True)  # Company ID for multi-tenant support
    created_by = Column(Integer, nullable=True)  # User ID who created
    updated_by = Column(Integer, nullable=True)  # User ID who updated
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
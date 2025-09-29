# backend/app/models/gst_state_codes.py
from sqlalchemy import Column, Integer, String, Boolean
from .base import BaseModel

class GSTStateCode(BaseModel):
    """GST State Codes for Indian states"""
    __tablename__ = "gst_state_code"
    
    code = Column(String(2), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<GSTStateCode(code='{self.code}', name='{self.name}')>"
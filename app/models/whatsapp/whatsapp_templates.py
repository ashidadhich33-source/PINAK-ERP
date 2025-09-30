"""
WhatsApp Template Categories and Components
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..base import Base


class WhatsAppTemplateCategory(Base):
    """Categories for WhatsApp templates"""
    __tablename__ = "whatsapp_template_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class WhatsAppTemplateLanguage(Base):
    """Supported languages for WhatsApp templates"""
    __tablename__ = "whatsapp_template_languages"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), nullable=False, unique=True)  # en, hi, ta, etc.
    name = Column(String(50), nullable=False)  # English, Hindi, Tamil, etc.
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class WhatsAppTemplateComponent(Base):
    """Template components for structured messages"""
    __tablename__ = "whatsapp_template_components"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("whatsapp_templates.id"), nullable=False)
    
    # Component details
    component_type = Column(String(20), nullable=False)  # header, body, footer, button
    position = Column(Integer, nullable=False)  # Order in template
    
    # Content
    text = Column(Text, nullable=True)
    button_text = Column(String(50), nullable=True)
    button_url = Column(String(500), nullable=True)
    button_type = Column(String(20), nullable=True)  # url, phone_number
    
    # Variables
    variable_count = Column(Integer, default=0)
    variable_names = Column(Text, nullable=True)  # JSON array of variable names
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    template = relationship("WhatsAppTemplate")
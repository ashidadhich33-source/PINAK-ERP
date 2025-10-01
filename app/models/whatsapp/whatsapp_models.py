# backend/app/models/whatsapp/whatsapp_models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date, Numeric, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
from ..base import BaseModel

class WhatsAppTemplate(BaseModel):
    """WhatsApp Template model for managing WhatsApp templates"""
    __tablename__ = "whatsapp_template"
    
    template_name = Column(String(100), nullable=False)
    template_content = Column(Text, nullable=False)
    template_type = Column(String(50), nullable=False)  # text, image, document, etc.
    category = Column(String(50), nullable=False)  # marketing, transactional, etc.
    status = Column(String(20), default='draft')  # draft, pending, approved, rejected
    language = Column(String(10), default='en')
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="whatsapp_templates")
    campaigns = relationship("WhatsAppCampaign", back_populates="template")
    
    def __repr__(self):
        return f"<WhatsAppTemplate(template_name='{self.template_name}', status='{self.status}')>"

class WhatsAppCampaign(BaseModel):
    """WhatsApp Campaign model for managing WhatsApp campaigns"""
    __tablename__ = "whatsapp_campaign"
    
    campaign_name = Column(String(100), nullable=False)
    template_id = Column(Integer, ForeignKey('whatsapp_template.id'), nullable=False)
    target_audience = Column(String(50), nullable=False)  # all, specific, segment
    scheduled_time = Column(DateTime, nullable=True)
    status = Column(String(20), default='draft')  # draft, scheduled, running, completed, cancelled
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    read_count = Column(Integer, default=0)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    template = relationship("WhatsAppTemplate", back_populates="campaigns")
    company = relationship("Company", back_populates="whatsapp_campaigns")
    messages = relationship("WhatsAppMessage", back_populates="campaign")
    
    def __repr__(self):
        return f"<WhatsAppCampaign(campaign_name='{self.campaign_name}', status='{self.status}')>"

class WhatsAppMessage(BaseModel):
    """WhatsApp Message model for managing WhatsApp messages"""
    __tablename__ = "whatsapp_message"
    
    campaign_id = Column(Integer, ForeignKey('whatsapp_campaign.id'), nullable=True)
    contact_id = Column(Integer, ForeignKey('whatsapp_contact.id'), nullable=False)
    message_type = Column(String(20), nullable=False)  # text, image, document, etc.
    message_content = Column(Text, nullable=False)
    status = Column(String(20), default='pending')  # pending, sent, delivered, read, failed
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    campaign = relationship("WhatsAppCampaign", back_populates="messages")
    contact = relationship("WhatsAppContact", back_populates="messages")
    company = relationship("Company", back_populates="whatsapp_messages")
    
    def __repr__(self):
        return f"<WhatsAppMessage(message_type='{self.message_type}', status='{self.status}')>"

class WhatsAppContact(BaseModel):
    """WhatsApp Contact model for managing WhatsApp contacts"""
    __tablename__ = "whatsapp_contact"
    
    phone_number = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    tags = Column(Text, nullable=True)  # JSON array of tags
    status = Column(String(20), default='active')  # active, blocked, unsubscribed
    last_contacted = Column(DateTime, nullable=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="whatsapp_contacts")
    messages = relationship("WhatsAppMessage", back_populates="contact")
    groups = relationship("WhatsAppGroup", secondary="whatsapp_contact_groups", back_populates="contacts")
    
    def __repr__(self):
        return f"<WhatsAppContact(phone_number='{self.phone_number}', name='{self.name}')>"

class WhatsAppGroup(BaseModel):
    """WhatsApp Group model for managing WhatsApp groups"""
    __tablename__ = "whatsapp_group"
    
    group_name = Column(String(100), nullable=False)
    group_description = Column(Text, nullable=True)
    group_type = Column(String(20), default='static')  # static, dynamic
    criteria = Column(Text, nullable=True)  # JSON criteria for dynamic groups
    member_count = Column(Integer, default=0)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="whatsapp_groups")
    contacts = relationship("WhatsAppContact", secondary="whatsapp_contact_groups", back_populates="groups")
    
    def __repr__(self):
        return f"<WhatsAppGroup(group_name='{self.group_name}', member_count={self.member_count})>"

class WhatsAppIntegration(BaseModel):
    """WhatsApp Integration model for managing WhatsApp integrations"""
    __tablename__ = "whatsapp_integration"
    
    integration_name = Column(String(100), nullable=False)
    api_key = Column(String(255), nullable=False)
    api_secret = Column(String(255), nullable=False)
    webhook_url = Column(String(255), nullable=True)
    status = Column(String(20), default='active')  # active, inactive, error
    last_sync = Column(DateTime, nullable=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="whatsapp_integrations")
    
    def __repr__(self):
        return f"<WhatsAppIntegration(integration_name='{self.integration_name}', status='{self.status}')>"

# Association table for many-to-many relationship between contacts and groups
whatsapp_contact_groups = Table(
    'whatsapp_contact_groups',
    BaseModel.metadata,
    Column('contact_id', Integer, ForeignKey('whatsapp_contact.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('whatsapp_group.id'), primary_key=True)
)
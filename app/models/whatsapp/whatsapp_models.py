"""
WhatsApp Business API Models for POS Integration
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from ..base import Base


class WhatsAppMessageStatus(PyEnum):
    """WhatsApp message delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    REJECTED = "rejected"


class WhatsAppTemplateStatus(PyEnum):
    """WhatsApp template approval status"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISABLED = "disabled"


class WhatsAppCampaignStatus(PyEnum):
    """WhatsApp campaign status"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class WhatsAppTemplate(Base):
    """WhatsApp message templates for business communication"""
    __tablename__ = "whatsapp_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    category = Column(String(50), nullable=False)  # TRANSACTIONAL, MARKETING, UTILITY
    language = Column(String(10), nullable=False, default="en")
    status = Column(Enum(WhatsAppTemplateStatus), default=WhatsAppTemplateStatus.DRAFT)
    
    # Template content
    header_text = Column(Text, nullable=True)
    body_text = Column(Text, nullable=False)
    footer_text = Column(Text, nullable=True)
    button_text = Column(String(50), nullable=True)
    button_url = Column(String(500), nullable=True)
    
    # WhatsApp Business API fields
    whatsapp_template_id = Column(String(100), nullable=True)  # ID from WhatsApp Business Manager
    whatsapp_template_name = Column(String(100), nullable=True)
    
    # Template variables (JSON format for dynamic content)
    variables = Column(JSON, nullable=True)
    
    # Approval and usage tracking
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String(100), nullable=True)
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(String(100), nullable=False)
    
    # Relationships
    messages = relationship("WhatsAppMessage", back_populates="template")
    campaigns = relationship("WhatsAppCampaign", back_populates="template")


class WhatsAppMessage(Base):
    """Individual WhatsApp messages sent to customers"""
    __tablename__ = "whatsapp_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("whatsapp_templates.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    phone_number = Column(String(20), nullable=False)
    
    # Message content
    message_type = Column(String(20), nullable=False)  # template, text, media
    content = Column(Text, nullable=False)
    media_url = Column(String(500), nullable=True)
    media_type = Column(String(20), nullable=True)  # image, document, video
    
    # WhatsApp API fields
    whatsapp_message_id = Column(String(100), nullable=True)
    status = Column(Enum(WhatsAppMessageStatus), default=WhatsAppMessageStatus.PENDING)
    error_message = Column(Text, nullable=True)
    
    # Context (what triggered this message)
    context_type = Column(String(50), nullable=True)  # pos_transaction, loyalty_points, marketing, etc.
    context_id = Column(Integer, nullable=True)  # ID of the related record
    
    # Delivery tracking
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    template = relationship("WhatsAppTemplate", back_populates="messages")
    customer = relationship("Customer", back_populates="whatsapp_messages")


class WhatsAppCustomer(Base):
    """Customer WhatsApp preferences and opt-in status"""
    __tablename__ = "whatsapp_customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, unique=True)
    phone_number = Column(String(20), nullable=False)
    
    # Opt-in preferences
    transactional_opt_in = Column(Boolean, default=True)  # Receipts, invoices, loyalty updates
    marketing_opt_in = Column(Boolean, default=False)  # Promotions, offers
    utility_opt_in = Column(Boolean, default=True)  # Account updates, notifications
    
    # WhatsApp Business API fields
    whatsapp_id = Column(String(100), nullable=True)  # WhatsApp user ID
    profile_name = Column(String(100), nullable=True)
    
    # Opt-in tracking
    transactional_opted_in_at = Column(DateTime, nullable=True)
    marketing_opted_in_at = Column(DateTime, nullable=True)
    utility_opted_in_at = Column(DateTime, nullable=True)
    
    # Opt-out tracking
    transactional_opted_out_at = Column(DateTime, nullable=True)
    marketing_opted_out_at = Column(DateTime, nullable=True)
    utility_opted_out_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="whatsapp_preferences")
    opt_ins = relationship("WhatsAppOptIn", back_populates="whatsapp_customer")


class WhatsAppCampaign(Base):
    """WhatsApp marketing campaigns"""
    __tablename__ = "whatsapp_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    template_id = Column(Integer, ForeignKey("whatsapp_templates.id"), nullable=False)
    
    # Campaign settings
    status = Column(Enum(WhatsAppCampaignStatus), default=WhatsAppCampaignStatus.DRAFT)
    target_audience = Column(JSON, nullable=True)  # Customer segments, filters
    
    # Scheduling
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Campaign variables
    variables = Column(JSON, nullable=True)  # Dynamic content for each recipient
    
    # Statistics
    total_recipients = Column(Integer, default=0)
    messages_sent = Column(Integer, default=0)
    messages_delivered = Column(Integer, default=0)
    messages_read = Column(Integer, default=0)
    messages_failed = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(String(100), nullable=False)
    
    # Relationships
    template = relationship("WhatsAppTemplate", back_populates="campaigns")


class WhatsAppOptIn(Base):
    """Customer opt-in/opt-out history tracking"""
    __tablename__ = "whatsapp_opt_ins"
    
    id = Column(Integer, primary_key=True, index=True)
    whatsapp_customer_id = Column(Integer, ForeignKey("whatsapp_customers.id"), nullable=False)
    
    # Opt-in details
    opt_type = Column(String(20), nullable=False)  # transactional, marketing, utility
    action = Column(String(10), nullable=False)  # opt_in, opt_out
    method = Column(String(20), nullable=False)  # pos, web, api, manual
    
    # Context
    context_data = Column(JSON, nullable=True)  # Additional context about the opt-in/out
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    created_by = Column(String(100), nullable=True)
    
    # Relationships
    whatsapp_customer = relationship("WhatsAppCustomer", back_populates="opt_ins")
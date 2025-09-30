"""
WhatsApp Pydantic Schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class WhatsAppTemplateStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISABLED = "disabled"


class WhatsAppMessageStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    REJECTED = "rejected"


class WhatsAppCampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


# Template Schemas
class WhatsAppTemplateCreate(BaseModel):
    name: str = Field(..., description="Template name")
    category: str = Field(..., description="Template category")
    language: str = Field(default="en", description="Template language code")
    header_text: Optional[str] = Field(None, description="Header text content")
    body_text: str = Field(..., description="Body text content")
    footer_text: Optional[str] = Field(None, description="Footer text content")
    button_text: Optional[str] = Field(None, description="Button text")
    button_url: Optional[str] = Field(None, description="Button URL")
    variables: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Template variables")


class WhatsAppTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Template name")
    category: Optional[str] = Field(None, description="Template category")
    language: Optional[str] = Field(None, description="Template language code")
    header_text: Optional[str] = Field(None, description="Header text content")
    body_text: Optional[str] = Field(None, description="Body text content")
    footer_text: Optional[str] = Field(None, description="Footer text content")
    button_text: Optional[str] = Field(None, description="Button text")
    button_url: Optional[str] = Field(None, description="Button URL")
    variables: Optional[Dict[str, Any]] = Field(None, description="Template variables")


class WhatsAppTemplateSubmit(BaseModel):
    submitted_by: Optional[str] = Field(None, description="User who submitted the template")


class WhatsAppTemplateApprove(BaseModel):
    approved_by: Optional[str] = Field(None, description="User who approved the template")


class WhatsAppTemplateResponse(BaseModel):
    id: int
    name: str
    category: str
    language: str
    status: WhatsAppTemplateStatus
    header_text: Optional[str]
    body_text: str
    footer_text: Optional[str]
    button_text: Optional[str]
    button_url: Optional[str]
    variables: Dict[str, Any]
    whatsapp_template_id: Optional[str]
    whatsapp_template_name: Optional[str]
    usage_count: int
    last_used: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: str

    class Config:
        from_attributes = True


# Message Schemas
class WhatsAppMessageSend(BaseModel):
    to: str = Field(..., description="Recipient phone number")
    message_type: str = Field(..., description="Message type (template, text, image, document, video, audio)")
    template_name: Optional[str] = Field(None, description="Template name for template messages")
    language_code: Optional[str] = Field("en", description="Language code for template messages")
    content: Optional[str] = Field(None, description="Message content")
    media_url: Optional[str] = Field(None, description="Media URL for media messages")
    components: Optional[List[Dict[str, Any]]] = Field(None, description="Template components")


class WhatsAppMessageResponse(BaseModel):
    id: int
    template_id: Optional[int]
    customer_id: Optional[int]
    phone_number: str
    message_type: str
    content: str
    media_url: Optional[str]
    media_type: Optional[str]
    whatsapp_message_id: Optional[str]
    status: WhatsAppMessageStatus
    error_message: Optional[str]
    context_type: Optional[str]
    context_id: Optional[int]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WhatsAppMessageStatusUpdate(BaseModel):
    status: WhatsAppMessageStatus
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    error_message: Optional[str] = None


# Campaign Schemas
class WhatsAppCampaignCreate(BaseModel):
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    template_id: int = Field(..., description="Template ID to use")
    target_audience: Dict[str, Any] = Field(..., description="Target audience criteria")
    variables: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Campaign variables")
    scheduled_at: Optional[datetime] = Field(None, description="When to start the campaign")


class WhatsAppCampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    target_audience: Optional[Dict[str, Any]] = Field(None, description="Target audience criteria")
    variables: Optional[Dict[str, Any]] = Field(None, description="Campaign variables")
    scheduled_at: Optional[datetime] = Field(None, description="When to start the campaign")


class WhatsAppCampaignResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    template_id: int
    status: WhatsAppCampaignStatus
    target_audience: Dict[str, Any]
    variables: Dict[str, Any]
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    total_recipients: int
    messages_sent: int
    messages_delivered: int
    messages_read: int
    messages_failed: int
    created_at: datetime
    updated_at: datetime
    created_by: str

    class Config:
        from_attributes = True


# Integration Schemas
class POSReceiptRequest(BaseModel):
    customer_id: int = Field(..., description="Customer ID")
    transaction_id: int = Field(..., description="POS transaction ID")
    store_name: str = Field(..., description="Store name")
    total_amount: float = Field(..., description="Total amount")
    items_count: int = Field(..., description="Number of items")
    customer_name: str = Field(..., description="Customer name")
    date: str = Field(..., description="Transaction date")
    payment_method: str = Field(..., description="Payment method")


class LoyaltyPointsRequest(BaseModel):
    customer_id: int = Field(..., description="Customer ID")
    points_earned: int = Field(..., description="Points earned")
    points_redeemed: int = Field(..., description="Points redeemed")
    current_balance: int = Field(..., description="Current points balance")
    transaction_id: Optional[int] = Field(None, description="Transaction ID")


class InvoiceRequest(BaseModel):
    customer_id: int = Field(..., description="Customer ID")
    invoice_number: str = Field(..., description="Invoice number")
    customer_name: str = Field(..., description="Customer name")
    total_amount: float = Field(..., description="Total amount")
    due_date: str = Field(..., description="Due date")
    company_name: str = Field(..., description="Company name")
    pdf_url: str = Field(..., description="PDF URL")
    invoice_id: Optional[int] = Field(None, description="Invoice ID")


class MarketingMessageRequest(BaseModel):
    customer_id: int = Field(..., description="Customer ID")
    campaign_id: int = Field(..., description="Campaign ID")
    customer_name: str = Field(..., description="Customer name")
    offer_title: str = Field(..., description="Offer title")
    offer_description: str = Field(..., description="Offer description")
    discount_percentage: int = Field(..., description="Discount percentage")
    valid_until: str = Field(..., description="Valid until date")
    store_name: str = Field(..., description="Store name")


class OptInRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number")
    opt_type: str = Field(..., description="Opt-in type (transactional, marketing, utility)")
    customer_id: Optional[int] = Field(None, description="Customer ID")


class OptOutRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number")
    opt_type: str = Field(..., description="Opt-out type (transactional, marketing, utility)")


# Setup Schemas
class WhatsAppSetupRequest(BaseModel):
    access_token: str = Field(..., description="WhatsApp access token")
    phone_number_id: str = Field(..., description="WhatsApp phone number ID")
    business_account_id: str = Field(..., description="WhatsApp business account ID")
    webhook_verify_token: str = Field(default="erp_webhook_token", description="Webhook verification token")


class WhatsAppSetupResponse(BaseModel):
    success: bool
    message: str
    templates_created: int = 0
    templates_skipped: int = 0
    errors: List[str] = []
    next_steps: List[str] = []


# Webhook Schemas
class WhatsAppWebhookData(BaseModel):
    object: str
    entry: List[Dict[str, Any]]


class WhatsAppWebhookVerification(BaseModel):
    mode: str
    token: str
    challenge: str
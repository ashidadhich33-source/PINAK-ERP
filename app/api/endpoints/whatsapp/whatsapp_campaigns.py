# backend/app/api/endpoints/whatsapp_campaigns.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.whatsapp.whatsapp_models import WhatsAppCampaign
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class WhatsAppCampaignCreate(BaseModel):
    campaign_name: str
    template_id: int
    target_audience: str
    scheduled_time: Optional[datetime] = None
    company_id: int

class WhatsAppCampaignResponse(BaseModel):
    id: int
    campaign_name: str
    template_id: int
    target_audience: str
    scheduled_time: Optional[datetime]
    status: str
    total_recipients: int
    sent_count: int
    delivered_count: int
    read_count: int

    class Config:
        from_attributes = True

@router.post("/campaigns", response_model=WhatsAppCampaignResponse)
async def create_whatsapp_campaign(
    campaign_data: WhatsAppCampaignCreate,
    current_user: User = Depends(require_permission("whatsapp.create")),
    db: Session = Depends(get_db)
):
    """Create a new WhatsApp campaign"""
    
    # Create WhatsApp campaign
    whatsapp_campaign = WhatsAppCampaign(
        campaign_name=campaign_data.campaign_name,
        template_id=campaign_data.template_id,
        target_audience=campaign_data.target_audience,
        scheduled_time=campaign_data.scheduled_time,
        company_id=campaign_data.company_id,
        created_by=current_user.id
    )
    
    db.add(whatsapp_campaign)
    db.commit()
    db.refresh(whatsapp_campaign)
    
    return whatsapp_campaign

@router.get("/campaigns", response_model=List[WhatsAppCampaignResponse])
async def get_whatsapp_campaigns(
    company_id: int,
    current_user: User = Depends(require_permission("whatsapp.view")),
    db: Session = Depends(get_db)
):
    """Get WhatsApp campaigns for a company"""
    
    campaigns = db.query(WhatsAppCampaign).filter(
        WhatsAppCampaign.company_id == company_id
    ).all()
    
    return campaigns

@router.get("/campaigns/{campaign_id}", response_model=WhatsAppCampaignResponse)
async def get_whatsapp_campaign(
    campaign_id: int,
    current_user: User = Depends(require_permission("whatsapp.view")),
    db: Session = Depends(get_db)
):
    """Get a specific WhatsApp campaign"""
    
    campaign = db.query(WhatsAppCampaign).filter(WhatsAppCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="WhatsApp campaign not found")
    
    return campaign

@router.put("/campaigns/{campaign_id}/start")
async def start_whatsapp_campaign(
    campaign_id: int,
    current_user: User = Depends(require_permission("whatsapp.update")),
    db: Session = Depends(get_db)
):
    """Start a WhatsApp campaign"""
    
    campaign = db.query(WhatsAppCampaign).filter(WhatsAppCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="WhatsApp campaign not found")
    
    if campaign.status == "running":
        raise HTTPException(status_code=400, detail="Campaign is already running")
    
    # Start the campaign
    campaign.status = "running"
    campaign.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "WhatsApp campaign started successfully"}

@router.put("/campaigns/{campaign_id}/stop")
async def stop_whatsapp_campaign(
    campaign_id: int,
    current_user: User = Depends(require_permission("whatsapp.update")),
    db: Session = Depends(get_db)
):
    """Stop a WhatsApp campaign"""
    
    campaign = db.query(WhatsAppCampaign).filter(WhatsAppCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="WhatsApp campaign not found")
    
    if campaign.status != "running":
        raise HTTPException(status_code=400, detail="Campaign is not running")
    
    # Stop the campaign
    campaign.status = "completed"
    campaign.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "WhatsApp campaign stopped successfully"}
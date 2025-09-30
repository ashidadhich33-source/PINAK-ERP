"""
WhatsApp Campaign Management API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.deps import get_db, get_current_user
from app.models.whatsapp.whatsapp_models import WhatsAppCampaignStatus
from app.services.whatsapp.whatsapp_campaign_service import WhatsAppCampaignService
from app.schemas.whatsapp_schema import (
    WhatsAppCampaignCreate,
    WhatsAppCampaignResponse,
    WhatsAppCampaignUpdate
)

router = APIRouter(prefix="/whatsapp/campaigns", tags=["WhatsApp Campaigns"])

# Service instance
campaign_service = WhatsAppCampaignService()


@router.post("/", response_model=WhatsAppCampaignResponse)
async def create_campaign(
    campaign_data: WhatsAppCampaignCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new WhatsApp marketing campaign"""
    try:
        result = campaign_service.create_campaign(
            db=db,
            name=campaign_data.name,
            description=campaign_data.description,
            template_id=campaign_data.template_id,
            target_audience=campaign_data.target_audience,
            variables=campaign_data.variables,
            scheduled_at=campaign_data.scheduled_at,
            created_by=current_user.get("user_id", "system")
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result["campaign"]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating campaign: {str(e)}"
        )


@router.get("/", response_model=List[WhatsAppCampaignResponse])
async def get_campaigns(
    status: Optional[WhatsAppCampaignStatus] = None,
    created_by: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get WhatsApp campaigns with optional filters"""
    try:
        campaigns = campaign_service.get_campaigns(
            db=db,
            status=status,
            created_by=created_by
        )
        
        return campaigns
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting campaigns: {str(e)}"
        )


@router.get("/{campaign_id}", response_model=WhatsAppCampaignResponse)
async def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific WhatsApp campaign"""
    try:
        from app.models.whatsapp.whatsapp_models import WhatsAppCampaign
        
        campaign = db.query(WhatsAppCampaign).filter(
            WhatsAppCampaign.id == campaign_id
        ).first()
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return campaign
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting campaign: {str(e)}"
        )


@router.put("/{campaign_id}", response_model=WhatsAppCampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_data: WhatsAppCampaignUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a WhatsApp campaign"""
    try:
        from app.models.whatsapp.whatsapp_models import WhatsAppCampaign
        from datetime import datetime
        
        campaign = db.query(WhatsAppCampaign).filter(
            WhatsAppCampaign.id == campaign_id
        ).first()
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        if campaign.status not in [WhatsAppCampaignStatus.DRAFT, WhatsAppCampaignStatus.PAUSED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft or paused campaigns can be updated"
            )
        
        # Update campaign fields
        for field, value in campaign_data.dict(exclude_unset=True).items():
            setattr(campaign, field, value)
        
        campaign.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(campaign)
        
        return campaign
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating campaign: {str(e)}"
        )


@router.post("/{campaign_id}/start")
async def start_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Start a WhatsApp campaign"""
    try:
        result = campaign_service.start_campaign(
            db=db,
            campaign_id=campaign_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting campaign: {str(e)}"
        )


@router.post("/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Pause a running campaign"""
    try:
        result = campaign_service.pause_campaign(
            db=db,
            campaign_id=campaign_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error pausing campaign: {str(e)}"
        )


@router.post("/{campaign_id}/resume")
async def resume_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Resume a paused campaign"""
    try:
        result = campaign_service.resume_campaign(
            db=db,
            campaign_id=campaign_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resuming campaign: {str(e)}"
        )


@router.get("/{campaign_id}/statistics")
async def get_campaign_statistics(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get campaign statistics"""
    try:
        result = campaign_service.get_campaign_statistics(
            db=db,
            campaign_id=campaign_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result["statistics"]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting campaign statistics: {str(e)}"
        )


@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a WhatsApp campaign"""
    try:
        from app.models.whatsapp.whatsapp_models import WhatsAppCampaign
        
        campaign = db.query(WhatsAppCampaign).filter(
            WhatsAppCampaign.id == campaign_id
        ).first()
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        if campaign.status == WhatsAppCampaignStatus.RUNNING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete running campaigns"
            )
        
        db.delete(campaign)
        db.commit()
        
        return {"message": "Campaign deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting campaign: {str(e)}"
        )
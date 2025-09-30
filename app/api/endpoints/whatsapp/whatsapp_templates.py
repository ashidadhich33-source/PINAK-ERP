"""
WhatsApp Template Management API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.deps import get_db, get_current_user
from app.models.whatsapp.whatsapp_models import WhatsAppTemplateStatus
from app.services.whatsapp.whatsapp_template_service import WhatsAppTemplateService
from app.schemas.whatsapp_schema import (
    WhatsAppTemplateCreate,
    WhatsAppTemplateUpdate,
    WhatsAppTemplateResponse,
    WhatsAppTemplateSubmit,
    WhatsAppTemplateApprove
)

router = APIRouter(prefix="/whatsapp/templates", tags=["WhatsApp Templates"])

# Service instance
template_service = WhatsAppTemplateService()


@router.post("/", response_model=WhatsAppTemplateResponse)
async def create_template(
    template_data: WhatsAppTemplateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new WhatsApp template"""
    try:
        result = template_service.create_template(
            db=db,
            name=template_data.name,
            category=template_data.category,
            language=template_data.language,
            header_text=template_data.header_text,
            body_text=template_data.body_text,
            footer_text=template_data.footer_text,
            button_text=template_data.button_text,
            button_url=template_data.button_url,
            variables=template_data.variables,
            created_by=current_user.get("user_id", "system")
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result["template"]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating template: {str(e)}"
        )


@router.get("/", response_model=List[WhatsAppTemplateResponse])
async def get_templates(
    status: Optional[WhatsAppTemplateStatus] = None,
    category: Optional[str] = None,
    language: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get WhatsApp templates with optional filters"""
    try:
        templates = template_service.get_templates(
            db=db,
            status=status,
            category=category,
            language=language
        )
        
        return templates
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting templates: {str(e)}"
        )


@router.get("/{template_id}", response_model=WhatsAppTemplateResponse)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific WhatsApp template"""
    try:
        template = db.query(WhatsAppTemplate).filter(
            WhatsAppTemplate.id == template_id
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        return template
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting template: {str(e)}"
        )


@router.put("/{template_id}", response_model=WhatsAppTemplateResponse)
async def update_template(
    template_id: int,
    template_data: WhatsAppTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a WhatsApp template"""
    try:
        template = db.query(WhatsAppTemplate).filter(
            WhatsAppTemplate.id == template_id
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        if template.status != WhatsAppTemplateStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft templates can be updated"
            )
        
        # Update template fields
        for field, value in template_data.dict(exclude_unset=True).items():
            setattr(template, field, value)
        
        template.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(template)
        
        return template
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating template: {str(e)}"
        )


@router.post("/{template_id}/submit", response_model=dict)
async def submit_template(
    template_id: int,
    submit_data: WhatsAppTemplateSubmit,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Submit template for approval"""
    try:
        result = template_service.submit_template_for_approval(
            db=db,
            template_id=template_id,
            submitted_by=current_user.get("user_id", "system")
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
            detail=f"Error submitting template: {str(e)}"
        )


@router.post("/{template_id}/approve", response_model=dict)
async def approve_template(
    template_id: int,
    approve_data: WhatsAppTemplateApprove,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Approve a template"""
    try:
        result = template_service.approve_template(
            db=db,
            template_id=template_id,
            approved_by=current_user.get("user_id", "system")
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
            detail=f"Error approving template: {str(e)}"
        )


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a WhatsApp template"""
    try:
        template = db.query(WhatsAppTemplate).filter(
            WhatsAppTemplate.id == template_id
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        if template.status == WhatsAppTemplateStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete approved templates"
            )
        
        db.delete(template)
        db.commit()
        
        return {"message": "Template deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting template: {str(e)}"
        )


@router.get("/{template_id}/usage")
async def get_template_usage(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get template usage statistics"""
    try:
        template = db.query(WhatsAppTemplate).filter(
            WhatsAppTemplate.id == template_id
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        return {
            "template_id": template.id,
            "template_name": template.name,
            "usage_count": template.usage_count,
            "last_used": template.last_used.isoformat() if template.last_used else None,
            "status": template.status.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting template usage: {str(e)}"
        )
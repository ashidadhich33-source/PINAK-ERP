# backend/app/api/endpoints/whatsapp_templates.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.whatsapp.whatsapp_models import WhatsAppTemplate
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class WhatsAppTemplateCreate(BaseModel):
    template_name: str
    template_content: str
    template_type: str
    category: str
    language: str = "en"
    company_id: int

class WhatsAppTemplateResponse(BaseModel):
    id: int
    template_name: str
    template_content: str
    template_type: str
    category: str
    status: str
    language: str

    class Config:
        from_attributes = True

@router.post("/templates", response_model=WhatsAppTemplateResponse)
async def create_whatsapp_template(
    template_data: WhatsAppTemplateCreate,
    current_user: User = Depends(require_permission("whatsapp.create")),
    db: Session = Depends(get_db)
):
    """Create a new WhatsApp template"""
    
    # Create WhatsApp template
    whatsapp_template = WhatsAppTemplate(
        template_name=template_data.template_name,
        template_content=template_data.template_content,
        template_type=template_data.template_type,
        category=template_data.category,
        language=template_data.language,
        company_id=template_data.company_id,
        created_by=current_user.id
    )
    
    db.add(whatsapp_template)
    db.commit()
    db.refresh(whatsapp_template)
    
    return whatsapp_template

@router.get("/templates", response_model=List[WhatsAppTemplateResponse])
async def get_whatsapp_templates(
    company_id: int,
    current_user: User = Depends(require_permission("whatsapp.view")),
    db: Session = Depends(get_db)
):
    """Get WhatsApp templates for a company"""
    
    templates = db.query(WhatsAppTemplate).filter(
        WhatsAppTemplate.company_id == company_id
    ).all()
    
    return templates

@router.get("/templates/{template_id}", response_model=WhatsAppTemplateResponse)
async def get_whatsapp_template(
    template_id: int,
    current_user: User = Depends(require_permission("whatsapp.view")),
    db: Session = Depends(get_db)
):
    """Get a specific WhatsApp template"""
    
    template = db.query(WhatsAppTemplate).filter(WhatsAppTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="WhatsApp template not found")
    
    return template

@router.put("/templates/{template_id}", response_model=WhatsAppTemplateResponse)
async def update_whatsapp_template(
    template_id: int,
    template_data: WhatsAppTemplateCreate,
    current_user: User = Depends(require_permission("whatsapp.update")),
    db: Session = Depends(get_db)
):
    """Update a WhatsApp template"""
    
    template = db.query(WhatsAppTemplate).filter(WhatsAppTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="WhatsApp template not found")
    
    # Update template fields
    template.template_name = template_data.template_name
    template.template_content = template_data.template_content
    template.template_type = template_data.template_type
    template.category = template_data.category
    template.language = template_data.language
    template.updated_by = current_user.id
    
    db.commit()
    db.refresh(template)
    
    return template

@router.delete("/templates/{template_id}")
async def delete_whatsapp_template(
    template_id: int,
    current_user: User = Depends(require_permission("whatsapp.delete")),
    db: Session = Depends(get_db)
):
    """Delete a WhatsApp template"""
    
    template = db.query(WhatsAppTemplate).filter(WhatsAppTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="WhatsApp template not found")
    
    # Soft delete
    template.is_active = False
    template.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "WhatsApp template deleted successfully"}
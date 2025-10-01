# backend/app/api/endpoints/whatsapp_contacts.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.whatsapp.whatsapp_models import WhatsAppContact
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class WhatsAppContactCreate(BaseModel):
    phone_number: str
    name: Optional[str] = None
    email: Optional[str] = None
    tags: Optional[str] = None
    company_id: int

class WhatsAppContactResponse(BaseModel):
    id: int
    phone_number: str
    name: Optional[str]
    email: Optional[str]
    tags: Optional[str]
    status: str
    last_contacted: Optional[datetime]

    class Config:
        from_attributes = True

@router.post("/contacts", response_model=WhatsAppContactResponse)
async def create_whatsapp_contact(
    contact_data: WhatsAppContactCreate,
    current_user: User = Depends(require_permission("whatsapp.create")),
    db: Session = Depends(get_db)
):
    """Create a new WhatsApp contact"""
    
    # Check if contact already exists
    existing_contact = db.query(WhatsAppContact).filter(
        WhatsAppContact.phone_number == contact_data.phone_number,
        WhatsAppContact.company_id == contact_data.company_id
    ).first()
    
    if existing_contact:
        raise HTTPException(
            status_code=400,
            detail="Contact with this phone number already exists"
        )
    
    # Create WhatsApp contact
    whatsapp_contact = WhatsAppContact(
        phone_number=contact_data.phone_number,
        name=contact_data.name,
        email=contact_data.email,
        tags=contact_data.tags,
        company_id=contact_data.company_id,
        created_by=current_user.id
    )
    
    db.add(whatsapp_contact)
    db.commit()
    db.refresh(whatsapp_contact)
    
    return whatsapp_contact

@router.get("/contacts", response_model=List[WhatsAppContactResponse])
async def get_whatsapp_contacts(
    company_id: int,
    current_user: User = Depends(require_permission("whatsapp.view")),
    db: Session = Depends(get_db)
):
    """Get WhatsApp contacts for a company"""
    
    contacts = db.query(WhatsAppContact).filter(
        WhatsAppContact.company_id == company_id
    ).all()
    
    return contacts

@router.get("/contacts/{contact_id}", response_model=WhatsAppContactResponse)
async def get_whatsapp_contact(
    contact_id: int,
    current_user: User = Depends(require_permission("whatsapp.view")),
    db: Session = Depends(get_db)
):
    """Get a specific WhatsApp contact"""
    
    contact = db.query(WhatsAppContact).filter(WhatsAppContact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="WhatsApp contact not found")
    
    return contact

@router.put("/contacts/{contact_id}", response_model=WhatsAppContactResponse)
async def update_whatsapp_contact(
    contact_id: int,
    contact_data: WhatsAppContactCreate,
    current_user: User = Depends(require_permission("whatsapp.update")),
    db: Session = Depends(get_db)
):
    """Update a WhatsApp contact"""
    
    contact = db.query(WhatsAppContact).filter(WhatsAppContact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="WhatsApp contact not found")
    
    # Update contact fields
    contact.phone_number = contact_data.phone_number
    contact.name = contact_data.name
    contact.email = contact_data.email
    contact.tags = contact_data.tags
    contact.updated_by = current_user.id
    
    db.commit()
    db.refresh(contact)
    
    return contact

@router.delete("/contacts/{contact_id}")
async def delete_whatsapp_contact(
    contact_id: int,
    current_user: User = Depends(require_permission("whatsapp.delete")),
    db: Session = Depends(get_db)
):
    """Delete a WhatsApp contact"""
    
    contact = db.query(WhatsAppContact).filter(WhatsAppContact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="WhatsApp contact not found")
    
    # Soft delete
    contact.is_active = False
    contact.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "WhatsApp contact deleted successfully"}
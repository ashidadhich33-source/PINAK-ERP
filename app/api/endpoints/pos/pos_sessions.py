# backend/app/api/endpoints/pos_sessions.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.pos.pos_models import POSSession
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class POSSessionCreate(BaseModel):
    session_name: str
    opening_cash: Decimal
    staff_id: int
    company_id: int

class POSSessionResponse(BaseModel):
    id: int
    session_name: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    opening_cash: Decimal
    closing_cash: Optional[Decimal]
    total_sales: Decimal
    total_transactions: int

    class Config:
        from_attributes = True

@router.post("/sessions", response_model=POSSessionResponse)
async def create_pos_session(
    session_data: POSSessionCreate,
    current_user: User = Depends(require_permission("pos.create")),
    db: Session = Depends(get_db)
):
    """Create a new POS session"""
    
    # Create POS session
    pos_session = POSSession(
        session_name=session_data.session_name,
        opening_cash=session_data.opening_cash,
        staff_id=session_data.staff_id,
        company_id=session_data.company_id,
        created_by=current_user.id
    )
    
    db.add(pos_session)
    db.commit()
    db.refresh(pos_session)
    
    return pos_session

@router.get("/sessions", response_model=List[POSSessionResponse])
async def get_pos_sessions(
    company_id: int,
    current_user: User = Depends(require_permission("pos.view")),
    db: Session = Depends(get_db)
):
    """Get POS sessions for a company"""
    
    sessions = db.query(POSSession).filter(
        POSSession.company_id == company_id
    ).all()
    
    return sessions

@router.get("/sessions/{session_id}", response_model=POSSessionResponse)
async def get_pos_session(
    session_id: int,
    current_user: User = Depends(require_permission("pos.view")),
    db: Session = Depends(get_db)
):
    """Get a specific POS session"""
    
    session = db.query(POSSession).filter(POSSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="POS session not found")
    
    return session

@router.put("/sessions/{session_id}/close")
async def close_pos_session(
    session_id: int,
    closing_cash: Decimal,
    current_user: User = Depends(require_permission("pos.update")),
    db: Session = Depends(get_db)
):
    """Close a POS session"""
    
    session = db.query(POSSession).filter(POSSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="POS session not found")
    
    if session.status == "closed":
        raise HTTPException(status_code=400, detail="Session is already closed")
    
    # Close the session
    session.end_time = datetime.utcnow()
    session.closing_cash = closing_cash
    session.status = "closed"
    session.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "POS session closed successfully"}
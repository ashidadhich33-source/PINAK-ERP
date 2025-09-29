# backend/app/api/endpoints/pos/pos_real_time_integration.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import datetime, date
import json

from ...database import get_db
from ...models.company import Company
from ...models.user import User
from ...core.security import get_current_user, require_permission
from ...services.pos.pos_real_time_integration_service import POSRealTimeIntegrationService

router = APIRouter()

# Initialize service
pos_real_time_service = POSRealTimeIntegrationService()

# Pydantic schemas for POS Real-time Integration
class POSTransactionCreateRequest(BaseModel):
    company_id: int
    session_id: int
    transaction_number: str
    transaction_date: datetime
    customer_id: Optional[int] = None
    staff_id: int
    subtotal: Decimal
    discount_amount: Optional[Decimal] = 0
    tax_amount: Optional[Decimal] = 0
    total_amount: Decimal
    payment_method: str
    items: List[dict]
    applied_discounts: Optional[List[dict]] = []

class POSRealTimeResponse(BaseModel):
    success: bool
    transaction_id: Optional[int] = None
    transaction_number: Optional[str] = None
    integration_results: dict
    message: str

class POSAnalyticsResponse(BaseModel):
    sessions: dict
    transactions: dict
    customers: dict
    inventory: dict
    last_updated: datetime

# POS Real-time Integration Endpoints
@router.post("/transactions", response_model=POSRealTimeResponse)
async def create_pos_transaction_with_real_time_integrations(
    transaction_data: POSTransactionCreateRequest,
    current_user: User = Depends(require_permission("pos.create")),
    db: Session = Depends(get_db)
):
    """Create POS transaction with real-time integrations"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, transaction_data.company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Create POS transaction with real-time integrations
        result = pos_real_time_service.create_pos_transaction_with_real_time_integrations(
            db, transaction_data.dict()
        )
        
        return POSRealTimeResponse(
            success=result['success'],
            transaction_id=result['transaction_id'],
            transaction_number=result['transaction_number'],
            integration_results=result['integration_results'],
            message=result['message']
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create POS transaction: {str(e)}"
        )

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.websocket"))
):
    """WebSocket endpoint for real-time POS updates"""
    
    try:
        # Connect WebSocket
        await pos_real_time_service.connect_websocket(websocket, session_id)
        
        # Send initial connection message
        await websocket.send_json({
            'type': 'connection_established',
            'session_id': session_id,
            'company_id': company_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()
                
                # Handle different message types
                if data.get('type') == 'ping':
                    await websocket.send_json({
                        'type': 'pong',
                        'timestamp': datetime.utcnow().isoformat()
                    })
                elif data.get('type') == 'get_analytics':
                    # Send real-time analytics
                    analytics = pos_real_time_service.get_real_time_pos_analytics(
                        db, company_id, session_id
                    )
                    await websocket.send_json({
                        'type': 'analytics_update',
                        'data': analytics,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                elif data.get('type') == 'get_inventory':
                    # Send real-time inventory data
                    inventory_data = pos_real_time_service.get_real_time_inventory_data(
                        db, company_id
                    )
                    await websocket.send_json({
                        'type': 'inventory_update',
                        'data': inventory_data,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                elif data.get('type') == 'get_customers':
                    # Send real-time customer data
                    customer_data = pos_real_time_service.get_real_time_customer_data(
                        db, company_id
                    )
                    await websocket.send_json({
                        'type': 'customer_update',
                        'data': customer_data,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket message handling: {str(e)}")
                await websocket.send_json({
                    'type': 'error',
                    'message': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                })
    
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}")
    finally:
        # Disconnect WebSocket
        await pos_real_time_service.disconnect_websocket(websocket, session_id)

@router.get("/analytics", response_model=POSAnalyticsResponse)
async def get_real_time_pos_analytics(
    company_id: int = Query(...),
    session_id: Optional[int] = Query(None),
    current_user: User = Depends(require_permission("pos.analytics")),
    db: Session = Depends(get_db)
):
    """Get real-time POS analytics"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get real-time POS analytics
        analytics = pos_real_time_service.get_real_time_pos_analytics(db, company_id, session_id)
        
        return POSAnalyticsResponse(
            sessions=analytics['sessions'],
            transactions=analytics['transactions'],
            customers=analytics['customers'],
            inventory=analytics['inventory'],
            last_updated=analytics['last_updated']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get real-time POS analytics: {str(e)}"
        )

@router.get("/inventory/real-time")
async def get_real_time_inventory_data(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.inventory")),
    db: Session = Depends(get_db)
):
    """Get real-time inventory data for POS"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get real-time inventory data
        inventory_data = pos_real_time_service.get_real_time_inventory_data(db, company_id)
        
        return {
            "inventory_data": inventory_data,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get real-time inventory data: {str(e)}"
        )

@router.get("/customers/real-time")
async def get_real_time_customer_data(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.customers")),
    db: Session = Depends(get_db)
):
    """Get real-time customer data for POS"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get real-time customer data
        customer_data = pos_real_time_service.get_real_time_customer_data(db, company_id)
        
        return {
            "customer_data": customer_data,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get real-time customer data: {str(e)}"
        )

@router.get("/sessions/active")
async def get_active_pos_sessions(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.sessions")),
    db: Session = Depends(get_db)
):
    """Get active POS sessions"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get active sessions
        active_sessions = pos_real_time_service.pos_sessions
        
        return {
            "active_sessions": [
                {
                    "session_id": session_id,
                    "connected_at": session_data['connected_at'],
                    "last_activity": session_data['last_activity'],
                    "status": "active"
                }
                for session_id, session_data in active_sessions.items()
            ],
            "total_active": len(active_sessions),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get active POS sessions: {str(e)}"
        )

@router.post("/broadcast")
async def broadcast_to_pos_sessions(
    message: dict,
    company_id: int = Query(...),
    session_id: Optional[int] = Query(None),
    current_user: User = Depends(require_permission("pos.broadcast")),
    db: Session = Depends(get_db)
):
    """Broadcast message to POS sessions"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Broadcast message
        if session_id:
            await pos_real_time_service.broadcast_to_session(session_id, message)
        else:
            await pos_real_time_service.broadcast_to_all(message)
        
        return {
            "success": True,
            "message": "Broadcast sent successfully",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to broadcast message: {str(e)}"
        )

@router.get("/integration-status")
async def get_pos_real_time_integration_status(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.view")),
    db: Session = Depends(get_db)
):
    """Get POS real-time integration status"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get integration status
        integrations = company_service.get_company_integrations(db, company_id)
        
        return {
            "pos_real_time_integration": {
                "websocket_connections": len(pos_real_time_service.active_connections),
                "active_sessions": len(pos_real_time_service.pos_sessions),
                "inventory_integration": integrations.get('inventory', {}).get('status', 'unknown'),
                "customer_integration": integrations.get('customers', {}).get('status', 'unknown'),
                "accounting_integration": integrations.get('accounting', {}).get('status', 'unknown'),
                "discount_integration": integrations.get('discounts', {}).get('status', 'unknown'),
                "loyalty_integration": integrations.get('loyalty', {}).get('status', 'unknown'),
                "sales_integration": integrations.get('sales', {}).get('status', 'unknown')
            },
            "real_time_features": {
                "live_inventory_updates": "enabled",
                "live_customer_updates": "enabled",
                "live_discount_calculation": "enabled",
                "live_loyalty_points": "enabled",
                "live_accounting_entries": "enabled",
                "live_sales_integration": "enabled"
            },
            "last_checked": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get POS real-time integration status: {str(e)}"
        )

@router.get("/workflow-automation")
async def get_pos_workflow_automation(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.automation")),
    db: Session = Depends(get_db)
):
    """Get POS workflow automation status"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get workflow automation status
        return {
            "pos_workflow_automation": {
                "real_time_inventory": "enabled",
                "real_time_customers": "enabled",
                "real_time_discounts": "enabled",
                "real_time_loyalty": "enabled",
                "real_time_accounting": "enabled",
                "real_time_sales": "enabled",
                "websocket_updates": "enabled"
            },
            "automation_rules": [
                "Auto-update inventory in real-time",
                "Auto-update customer analytics",
                "Auto-apply discounts in real-time",
                "Auto-earn loyalty points",
                "Auto-create journal entries",
                "Auto-create sales records",
                "Auto-send WebSocket updates"
            ],
            "real_time_capabilities": [
                "Live stock updates",
                "Live customer data",
                "Live discount calculation",
                "Live loyalty points",
                "Live accounting entries",
                "Live sales integration",
                "Live WebSocket communication"
            ],
            "last_updated": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get POS workflow automation: {str(e)}"
        )
# backend/app/api/endpoints/enhanced_purchase.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import datetime, date
import tempfile
import os

from ...database import get_db
from ...models.company import Company
from ...models.user import User
from ...core.security import get_current_user, require_permission
from ...services.enhanced_purchase_service import enhanced_purchase_service

router = APIRouter()

# Pydantic schemas for Excel Import
class ExcelImportCreateRequest(BaseModel):
    import_name: str
    file_name: str
    
    @validator('import_name')
    def validate_import_name(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Import name must be at least 3 characters')
        return v

class ExcelImportResponse(BaseModel):
    id: int
    company_id: int
    import_name: str
    file_name: str
    total_rows: int
    processed_rows: int
    success_rows: int
    error_rows: int
    import_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Direct Stock Inward
class DirectStockInwardCreateRequest(BaseModel):
    inward_date: date
    inward_type: str = 'opening_stock'
    reference_number: Optional[str] = None
    reference_date: Optional[date] = None
    notes: Optional[str] = None

class DirectStockInwardItemCreateRequest(BaseModel):
    item_id: int
    variant_id: Optional[int] = None
    quantity: Decimal
    unit_cost: Decimal
    location_id: Optional[int] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    notes: Optional[str] = None

class DirectStockInwardResponse(BaseModel):
    id: int
    company_id: int
    inward_number: str
    inward_date: date
    inward_type: str
    reference_number: Optional[str] = None
    reference_date: Optional[date] = None
    total_quantity: Decimal
    total_value: Decimal
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Purchase Return
class PurchaseReturnCreateRequest(BaseModel):
    supplier_id: int
    return_date: date
    return_reason: Optional[str] = None
    return_type: str = 'defective'
    original_bill_id: Optional[int] = None
    notes: Optional[str] = None

class PurchaseReturnItemCreateRequest(BaseModel):
    item_id: int
    variant_id: Optional[int] = None
    original_bill_item_id: Optional[int] = None
    quantity: Decimal
    unit_price: Decimal
    total_amount: Decimal
    gst_rate: Optional[Decimal] = None
    return_reason: Optional[str] = None
    notes: Optional[str] = None

class PurchaseReturnResponse(BaseModel):
    id: int
    company_id: int
    return_number: str
    return_date: date
    supplier_id: int
    original_bill_id: Optional[int] = None
    original_bill_number: Optional[str] = None
    original_bill_date: Optional[date] = None
    return_reason: Optional[str] = None
    return_type: str
    total_quantity: Decimal
    total_amount: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    total_gst_amount: Decimal
    net_amount: Decimal
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Excel Import Endpoints
@router.post("/excel-import", response_model=ExcelImportResponse)
async def import_purchase_excel(
    file: UploadFile = File(...),
    import_name: str = Query(...),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Import purchase data from Excel file"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="File must be an Excel file (.xlsx or .xls)"
        )
    
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Import Excel data
        import_record = enhanced_purchase_service.import_purchase_excel(
            db=db,
            company_id=company_id,
            file_path=tmp_file_path,
            file_name=file.filename,
            import_name=import_name,
            user_id=current_user.id
        )
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        return import_record
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import Excel file: {str(e)}"
        )

@router.get("/excel-import/{import_id}/items")
async def get_excel_import_items(
    import_id: int,
    company_id: int = Query(...),
    processing_status: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("purchase.view")),
    db: Session = Depends(get_db)
):
    """Get Excel import items"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    items = enhanced_purchase_service.get_excel_import_items(
        db=db,
        company_id=company_id,
        import_id=import_id,
        processing_status=processing_status
    )
    
    return {
        "import_id": import_id,
        "items": [
            {
                "id": item.id,
                "row_number": item.row_number,
                "item_name": item.item_name,
                "item_code": item.item_code,
                "barcode": item.barcode,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_amount": item.total_amount,
                "gst_rate": item.gst_rate,
                "hsn_code": item.hsn_code,
                "supplier_name": item.supplier_name,
                "supplier_code": item.supplier_code,
                "bill_number": item.bill_number,
                "bill_date": item.bill_date,
                "processing_status": item.processing_status,
                "error_message": item.error_message,
                "matched_item_id": item.matched_item_id,
                "matched_supplier_id": item.matched_supplier_id
            }
            for item in items
        ],
        "total_items": len(items)
    }

@router.post("/excel-import/{import_id}/match-items")
async def match_excel_items(
    import_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Match Excel import items to master data"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        result = enhanced_purchase_service.match_excel_items_to_master_data(
            db=db,
            company_id=company_id,
            import_id=import_id,
            user_id=current_user.id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to match items: {str(e)}"
        )

# Direct Stock Inward Endpoints
@router.post("/direct-stock-inward", response_model=DirectStockInwardResponse)
async def create_direct_stock_inward(
    inward_data: DirectStockInwardCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create direct stock inward"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        inward = enhanced_purchase_service.create_direct_stock_inward(
            db=db,
            company_id=company_id,
            inward_date=inward_data.inward_date,
            inward_type=inward_data.inward_type,
            reference_number=inward_data.reference_number,
            reference_date=inward_data.reference_date,
            notes=inward_data.notes,
            user_id=current_user.id
        )
        
        return inward
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create direct stock inward: {str(e)}"
        )

@router.post("/direct-stock-inward/{inward_id}/items")
async def add_items_to_direct_inward(
    inward_id: int,
    items: List[DirectStockInwardItemCreateRequest],
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Add items to direct stock inward"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        # Convert Pydantic models to dictionaries
        items_data = [item.dict() for item in items]
        
        inward_items = enhanced_purchase_service.add_items_to_direct_inward(
            db=db,
            company_id=company_id,
            inward_id=inward_id,
            items=items_data,
            user_id=current_user.id
        )
        
        return {
            "message": "Items added to direct stock inward successfully",
            "items_count": len(inward_items)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add items to direct stock inward: {str(e)}"
        )

@router.post("/direct-stock-inward/{inward_id}/process")
async def process_direct_stock_inward(
    inward_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Process direct stock inward"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        success = enhanced_purchase_service.process_direct_stock_inward(
            db=db,
            company_id=company_id,
            inward_id=inward_id,
            user_id=current_user.id
        )
        
        if success:
            return {"message": "Direct stock inward processed successfully"}
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to process direct stock inward"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process direct stock inward: {str(e)}"
        )

# Purchase Return Endpoints
@router.post("/purchase-returns", response_model=PurchaseReturnResponse)
async def create_purchase_return(
    return_data: PurchaseReturnCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create purchase return"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        purchase_return = enhanced_purchase_service.create_purchase_return(
            db=db,
            company_id=company_id,
            supplier_id=return_data.supplier_id,
            return_date=return_data.return_date,
            return_reason=return_data.return_reason,
            return_type=return_data.return_type,
            original_bill_id=return_data.original_bill_id,
            notes=return_data.notes,
            user_id=current_user.id
        )
        
        return purchase_return
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create purchase return: {str(e)}"
        )

@router.post("/purchase-returns/{return_id}/items")
async def add_items_to_purchase_return(
    return_id: int,
    items: List[PurchaseReturnItemCreateRequest],
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Add items to purchase return"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        # Convert Pydantic models to dictionaries
        items_data = [item.dict() for item in items]
        
        return_items = enhanced_purchase_service.add_items_to_purchase_return(
            db=db,
            company_id=company_id,
            return_id=return_id,
            items=items_data,
            user_id=current_user.id
        )
        
        return {
            "message": "Items added to purchase return successfully",
            "items_count": len(return_items)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add items to purchase return: {str(e)}"
        )

@router.post("/purchase-returns/{return_id}/process")
async def process_purchase_return(
    return_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Process purchase return"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        success = enhanced_purchase_service.process_purchase_return(
            db=db,
            company_id=company_id,
            return_id=return_id,
            user_id=current_user.id
        )
        
        if success:
            return {"message": "Purchase return processed successfully"}
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to process purchase return"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process purchase return: {str(e)}"
        )

# Purchase Analytics Endpoints
@router.get("/analytics")
async def get_purchase_analytics(
    company_id: int = Query(...),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("purchase.view")),
    db: Session = Depends(get_db)
):
    """Get purchase analytics"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    analytics = enhanced_purchase_service.get_purchase_analytics(
        db=db,
        company_id=company_id,
        from_date=from_date,
        to_date=to_date
    )
    
    return analytics

# Bill Matching Endpoints
@router.post("/bill-matching")
async def create_bill_matching(
    import_id: int = Query(...),
    supplier_id: int = Query(...),
    bill_number: str = Query(...),
    bill_date: date = Query(...),
    bill_amount: Decimal = Query(...),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create bill matching"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        bill_matching = enhanced_purchase_service.create_bill_matching(
            db=db,
            company_id=company_id,
            import_id=import_id,
            supplier_id=supplier_id,
            bill_number=bill_number,
            bill_date=bill_date,
            bill_amount=bill_amount,
            user_id=current_user.id
        )
        
        return {
            "message": "Bill matching created successfully",
            "matching_id": bill_matching.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create bill matching: {str(e)}"
        )

@router.post("/bill-matching/{matching_id}/items")
async def add_items_to_bill_matching(
    matching_id: int,
    import_item_ids: List[int],
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Add items to bill matching"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        matching_items = enhanced_purchase_service.add_items_to_bill_matching(
            db=db,
            company_id=company_id,
            matching_id=matching_id,
            import_item_ids=import_item_ids,
            user_id=current_user.id
        )
        
        return {
            "message": "Items added to bill matching successfully",
            "items_count": len(matching_items)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add items to bill matching: {str(e)}"
        )

# Excel Template Endpoint
@router.get("/excel-template")
async def download_excel_template(
    current_user: User = Depends(require_permission("purchase.view"))
):
    """Download Excel template for purchase import"""
    
    # This would generate and return an Excel template file
    # For now, return template structure
    template_structure = {
        "columns": [
            "item_name",
            "item_code", 
            "barcode",
            "quantity",
            "unit_price",
            "total_amount",
            "gst_rate",
            "hsn_code",
            "supplier_name",
            "supplier_code",
            "bill_number",
            "bill_date"
        ],
        "sample_data": [
            {
                "item_name": "Sample Item 1",
                "item_code": "ITEM001",
                "barcode": "1234567890123",
                "quantity": 10,
                "unit_price": 100.00,
                "total_amount": 1000.00,
                "gst_rate": 18.00,
                "hsn_code": "1234",
                "supplier_name": "Supplier 1",
                "supplier_code": "SUP001",
                "bill_number": "BILL001",
                "bill_date": "2024-01-01"
            }
        ],
        "instructions": [
            "Fill in all required columns",
            "Ensure date format is YYYY-MM-DD",
            "Use decimal numbers for prices and quantities",
            "GST rate should be in percentage (e.g., 18.00 for 18%)",
            "Save file as Excel (.xlsx) format"
        ]
    }
    
    return template_structure
# backend/app/api/endpoints/purchases.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from typing import Optional, List
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import datetime, date

from ...database import get_db
from ...models.enhanced_purchase import PurchaseOrder, PurchaseOrderItem, PurchaseInvoice, PurchaseInvoiceItem
from ...models.customer import Supplier
from ...models.item import Item
from ...models.user import User
from ...core.security import get_current_user, require_permission
from ...services.stock_service import StockService
from ...services.gst_service import GSTService

router = APIRouter()

# Pydantic schemas
class PurchaseOrderItemRequest(BaseModel):
    item_id: int
    quantity: Decimal
    unit_price: Decimal
    remarks: Optional[str] = None

    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than zero')
        return v

    @validator('unit_price')
    def unit_price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Unit price must be greater than zero')
        return v

class PurchaseOrderRequest(BaseModel):
    supplier_id: int
    expected_date: Optional[date] = None
    items: List[PurchaseOrderItemRequest]
    discount_amount: Decimal = 0
    remarks: Optional[str] = None

    @validator('items')
    def items_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Order must have at least one item')
        return v

class PurchaseInvoiceItemRequest(BaseModel):
    item_id: int
    quantity: Decimal
    unit_price: Decimal
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None

    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than zero')
        return v

    @validator('unit_price')
    def unit_price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Unit price must be greater than zero')
        return v

class PurchaseInvoiceRequest(BaseModel):
    supplier_id: int
    supplier_invoice_number: Optional[str] = None
    order_id: Optional[int] = None
    due_date: Optional[date] = None
    items: List[PurchaseInvoiceItemRequest]
    discount_amount: Decimal = 0
    remarks: Optional[str] = None

    @validator('items')
    def items_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Invoice must have at least one item')
        return v

class PurchaseOrderItemResponse(BaseModel):
    id: int
    item_id: int
    item_code: str
    item_name: str
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    received_quantity: Decimal
    pending_quantity: Decimal

    class Config:
        from_attributes = True

class PurchaseOrderResponse(BaseModel):
    id: int
    order_number: str
    order_date: datetime
    expected_date: Optional[date]
    supplier_id: int
    supplier_name: str
    status: str
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    remarks: Optional[str]
    items: List[PurchaseOrderItemResponse] = []

    class Config:
        from_attributes = True

class PurchaseInvoiceItemResponse(BaseModel):
    id: int
    item_id: int
    item_code: str
    item_name: str
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal
    tax_rate: Decimal
    tax_amount: Decimal

    class Config:
        from_attributes = True

class PurchaseInvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    supplier_invoice_number: Optional[str]
    invoice_date: datetime
    due_date: Optional[date]
    supplier_id: int
    supplier_name: str
    supplier_gst: Optional[str]
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    balance_amount: Decimal
    status: str
    items: List[PurchaseInvoiceItemResponse] = []

    class Config:
        from_attributes = True

# Helper functions
def generate_purchase_order_number(db: Session) -> str:
    """Generate unique purchase order number"""
    today = datetime.now()
    prefix = f"PO{today.strftime('%Y%m%d')}"
    
    last_order = db.query(PurchaseOrder).filter(
        PurchaseOrder.order_number.like(f"{prefix}%")
    ).order_by(desc(PurchaseOrder.order_number)).first()
    
    if last_order:
        try:
            last_seq = int(last_order.order_number[-4:])
            next_seq = last_seq + 1
        except:
            next_seq = 1
    else:
        next_seq = 1
    
    return f"{prefix}{next_seq:04d}"

def generate_purchase_invoice_number(db: Session) -> str:
    """Generate unique purchase invoice number"""
    today = datetime.now()
    prefix = f"PI{today.strftime('%Y%m%d')}"
    
    last_invoice = db.query(PurchaseInvoice).filter(
        PurchaseInvoice.invoice_number.like(f"{prefix}%")
    ).order_by(desc(PurchaseInvoice.invoice_number)).first()
    
    if last_invoice:
        try:
            last_seq = int(last_invoice.invoice_number[-4:])
            next_seq = last_seq + 1
        except:
            next_seq = 1
    else:
        next_seq = 1
    
    return f"{prefix}{next_seq:04d}"

# Purchase Order endpoints
@router.get("/orders", response_model=List[PurchaseOrderResponse])
async def get_purchase_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    supplier_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("purchases.view")),
    db: Session = Depends(get_db)
):
    """Get purchase orders with filtering"""
    
    query = db.query(PurchaseOrder)
    
    # Apply filters
    if search:
        search_filter = or_(
            PurchaseOrder.order_number.ilike(f"%{search}%"),
            PurchaseOrder.supplier_name.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    if supplier_id:
        query = query.filter(PurchaseOrder.supplier_id == supplier_id)
    
    if status:
        query = query.filter(PurchaseOrder.status == status)
    
    if date_from:
        query = query.filter(PurchaseOrder.order_date >= datetime.combine(date_from, datetime.min.time()))
    
    if date_to:
        query = query.filter(PurchaseOrder.order_date <= datetime.combine(date_to, datetime.max.time()))
    
    orders = query.order_by(desc(PurchaseOrder.order_date)).offset(skip).limit(limit).all()
    
    return [PurchaseOrderResponse.from_orm(order) for order in orders]

@router.get("/orders/{order_id}", response_model=PurchaseOrderResponse)
async def get_purchase_order(
    order_id: int,
    current_user: User = Depends(require_permission("purchases.view")),
    db: Session = Depends(get_db)
):
    """Get purchase order by ID"""
    
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )
    
    return PurchaseOrderResponse.from_orm(order)

@router.post("/orders", response_model=PurchaseOrderResponse)
async def create_purchase_order(
    order_data: PurchaseOrderRequest,
    current_user: User = Depends(require_permission("purchases.create")),
    db: Session = Depends(get_db)
):
    """Create new purchase order"""
    
    # Validate supplier
    supplier = db.query(Supplier).filter(Supplier.id == order_data.supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supplier not found"
        )
    
    # Validate items
    for item_data in order_data.items:
        item = db.query(Item).filter(Item.id == item_data.item_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Item with ID {item_data.item_id} not found"
            )
    
    # Generate order number
    order_number = generate_purchase_order_number(db)
    
    # Create purchase order
    db_order = PurchaseOrder(
        order_number=order_number,
        supplier_id=order_data.supplier_id,
        supplier_name=supplier.name,
        expected_date=order_data.expected_date,
        discount_amount=order_data.discount_amount,
        remarks=order_data.remarks,
        created_by=current_user.id
    )
    
    db.add(db_order)
    db.flush()  # Get order ID
    
    # Create order items
    gst_service = GSTService()
    
    for item_data in order_data.items:
        item = db.query(Item).filter(Item.id == item_data.item_id).first()
        
        # Calculate line total and tax
        line_total = item_data.quantity * item_data.unit_price
        
        # Calculate tax based on item's GST rate
        tax_rate = item.gst_rate or Decimal('0')
        tax_calculation = gst_service.calculate_tax(line_total, tax_rate, True)
        
        order_item = PurchaseOrderItem(
            order_id=db_order.id,
            item_id=item.id,
            item_code=item.barcode,
            item_name=item.name,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            line_total=line_total,
            tax_rate=tax_rate,
            tax_amount=tax_calculation['tax_amount'],
            pending_quantity=item_data.quantity
        )
        
        db.add(order_item)
    
    # Calculate order totals
    db_order.subtotal = sum(item.line_total for item in db_order.order_items)
    db_order.tax_amount = sum(item.tax_amount for item in db_order.order_items)
    db_order.total_amount = db_order.subtotal - db_order.discount_amount + db_order.tax_amount
    
    db.commit()
    db.refresh(db_order)
    
    return PurchaseOrderResponse.from_orm(db_order)

@router.put("/orders/{order_id}/status")
async def update_purchase_order_status(
    order_id: int,
    new_status: str = Query(..., regex="^(pending|confirmed|received|cancelled)$"),
    current_user: User = Depends(require_permission("purchases.edit")),
    db: Session = Depends(get_db)
):
    """Update purchase order status"""
    
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )
    
    order.status = new_status
    order.updated_by = current_user.id
    
    db.commit()
    
    return {"message": f"Purchase order status updated to {new_status}"}

# Purchase Invoice endpoints
@router.get("/invoices", response_model=List[PurchaseInvoiceResponse])
async def get_purchase_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    supplier_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("purchases.view")),
    db: Session = Depends(get_db)
):
    """Get purchase invoices with filtering"""
    
    query = db.query(PurchaseInvoice)
    
    # Apply filters
    if search:
        search_filter = or_(
            PurchaseInvoice.invoice_number.ilike(f"%{search}%"),
            PurchaseInvoice.supplier_invoice_number.ilike(f"%{search}%"),
            PurchaseInvoice.supplier_name.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    if supplier_id:
        query = query.filter(PurchaseInvoice.supplier_id == supplier_id)
    
    if status:
        query = query.filter(PurchaseInvoice.status == status)
    
    if date_from:
        query = query.filter(PurchaseInvoice.invoice_date >= datetime.combine(date_from, datetime.min.time()))
    
    if date_to:
        query = query.filter(PurchaseInvoice.invoice_date <= datetime.combine(date_to, datetime.max.time()))
    
    invoices = query.order_by(desc(PurchaseInvoice.invoice_date)).offset(skip).limit(limit).all()
    
    return [PurchaseInvoiceResponse.from_orm(invoice) for invoice in invoices]

@router.get("/invoices/{invoice_id}", response_model=PurchaseInvoiceResponse)
async def get_purchase_invoice(
    invoice_id: int,
    current_user: User = Depends(require_permission("purchases.view")),
    db: Session = Depends(get_db)
):
    """Get purchase invoice by ID"""
    
    invoice = db.query(PurchaseInvoice).filter(PurchaseInvoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase invoice not found"
        )
    
    return PurchaseInvoiceResponse.from_orm(invoice)

@router.post("/invoices", response_model=PurchaseInvoiceResponse)
async def create_purchase_invoice(
    invoice_data: PurchaseInvoiceRequest,
    current_user: User = Depends(require_permission("purchases.create")),
    db: Session = Depends(get_db)
):
    """Create new purchase invoice"""
    
    # Validate supplier
    supplier = db.query(Supplier).filter(Supplier.id == invoice_data.supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supplier not found"
        )
    
    # Validate items
    for item_data in invoice_data.items:
        item = db.query(Item).filter(Item.id == item_data.item_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Item with ID {item_data.item_id} not found"
            )
    
    # Generate invoice number
    invoice_number = generate_purchase_invoice_number(db)
    
    # Create purchase invoice
    db_invoice = PurchaseInvoice(
        invoice_number=invoice_number,
        supplier_invoice_number=invoice_data.supplier_invoice_number,
        supplier_id=invoice_data.supplier_id,
        supplier_name=supplier.name,
        supplier_gst=supplier.gst_number,
        due_date=invoice_data.due_date,
        discount_amount=invoice_data.discount_amount,
        created_by=current_user.id
    )
    
    db.add(db_invoice)
    db.flush()  # Get invoice ID
    
    # Create invoice items and update stock
    stock_service = StockService()
    gst_service = GSTService()
    
    for item_data in invoice_data.items:
        item = db.query(Item).filter(Item.id == item_data.item_id).first()
        
        # Calculate line total and tax
        line_total = item_data.quantity * item_data.unit_price
        
        # Calculate tax based on item's GST rate
        tax_rate = item.gst_rate or Decimal('0')
        tax_calculation = gst_service.calculate_tax(line_total, tax_rate, True)
        
        invoice_item = PurchaseInvoiceItem(
            invoice_id=db_invoice.id,
            item_id=item.id,
            item_code=item.barcode,
            item_name=item.name,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            line_total=line_total,
            tax_rate=tax_rate,
            tax_amount=tax_calculation['tax_amount']
        )
        
        db.add(invoice_item)
        
        # Update stock - increase quantity
        if item.track_inventory:
            stock_service.add_stock_movement(
                db=db,
                item_id=item.id,
                location_id=None,  # Use main location
                movement_type="in",
                quantity=item_data.quantity,
                unit_cost=item_data.unit_price,
                reference_type="purchase_invoice",
                reference_id=db_invoice.id,
                reference_number=invoice_number,
                remarks=f"Purchase from {supplier.name}",
                batch_number=item_data.batch_number
            )
        
        # Update item costs
        if item_data.unit_price > 0:
            item.purchase_rate = item_data.unit_price
            item.landed_cost = item_data.unit_price  # Simplified - in reality would include freight, etc.
    
    # Calculate invoice totals
    db_invoice.subtotal = sum(item.line_total for item in db_invoice.invoice_items)
    db_invoice.tax_amount = sum(item.tax_amount for item in db_invoice.invoice_items)
    db_invoice.total_amount = db_invoice.subtotal - db_invoice.discount_amount + db_invoice.tax_amount
    db_invoice.balance_amount = db_invoice.total_amount
    
    # Update supplier statistics
    supplier.total_purchase_amount += db_invoice.total_amount
    supplier.total_orders += 1
    supplier.last_purchase_date = db_invoice.invoice_date
    
    if not supplier.first_purchase_date:
        supplier.first_purchase_date = db_invoice.invoice_date
    
    db.commit()
    db.refresh(db_invoice)
    
    return PurchaseInvoiceResponse.from_orm(db_invoice)

@router.put("/invoices/{invoice_id}/payment-status")
async def update_purchase_invoice_payment_status(
    invoice_id: int,
    paid_amount: Decimal = Query(..., ge=0),
    current_user: User = Depends(require_permission("purchases.edit")),
    db: Session = Depends(get_db)
):
    """Update purchase invoice payment status"""
    
    invoice = db.query(PurchaseInvoice).filter(PurchaseInvoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase invoice not found"
        )
    
    if paid_amount > invoice.total_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Paid amount cannot exceed total amount"
        )
    
    invoice.paid_amount = paid_amount
    invoice.balance_amount = invoice.total_amount - paid_amount
    
    # Determine status
    if paid_amount >= invoice.total_amount:
        invoice.status = "paid"
    elif paid_amount > 0:
        invoice.status = "partial"
    else:
        invoice.status = "pending"
    
    invoice.updated_by = current_user.id
    
    db.commit()
    
    return {"message": f"Purchase invoice payment updated. Status: {invoice.status}"}

# Analytics endpoints
@router.get("/analytics/supplier-performance")
async def get_supplier_performance(
    period_days: int = Query(30, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(require_permission("purchases.view")),
    db: Session = Depends(get_db)
):
    """Get supplier performance analytics"""
    
    from datetime import timedelta
    from sqlalchemy import func
    
    start_date = datetime.now() - timedelta(days=period_days)
    
    supplier_performance = db.query(
        PurchaseInvoice.supplier_id,
        PurchaseInvoice.supplier_name,
        func.count(PurchaseInvoice.id).label('invoice_count'),
        func.sum(PurchaseInvoice.total_amount).label('total_amount'),
        func.avg(PurchaseInvoice.total_amount).label('average_bill'),
        func.max(PurchaseInvoice.invoice_date).label('last_purchase')
    ).filter(
        PurchaseInvoice.invoice_date >= start_date
    ).group_by(
        PurchaseInvoice.supplier_id,
        PurchaseInvoice.supplier_name
    ).order_by(
        func.sum(PurchaseInvoice.total_amount).desc()
    ).limit(limit).all()
    
    return {
        "period_days": period_days,
        "suppliers": [
            {
                "supplier_id": row.supplier_id,
                "supplier_name": row.supplier_name,
                "invoice_count": row.invoice_count,
                "total_amount": float(row.total_amount),
                "average_bill": float(row.average_bill),
                "last_purchase": row.last_purchase
            }
            for row in supplier_performance
        ]
    }

@router.get("/analytics/monthly-trends")
async def get_monthly_purchase_trends(
    months: int = Query(6, ge=1, le=24),
    current_user: User = Depends(require_permission("purchases.view")),
    db: Session = Depends(get_db)
):
    """Get monthly purchase trends"""
    
    from datetime import timedelta
    from sqlalchemy import func, extract
    
    start_date = datetime.now() - timedelta(days=months * 30)
    
    monthly_data = db.query(
        extract('year', PurchaseInvoice.invoice_date).label('year'),
        extract('month', PurchaseInvoice.invoice_date).label('month'),
        func.count(PurchaseInvoice.id).label('invoice_count'),
        func.sum(PurchaseInvoice.total_amount).label('total_amount'),
        func.sum(PurchaseInvoice.tax_amount).label('total_tax')
    ).filter(
        PurchaseInvoice.invoice_date >= start_date
    ).group_by(
        extract('year', PurchaseInvoice.invoice_date),
        extract('month', PurchaseInvoice.invoice_date)
    ).order_by(
        extract('year', PurchaseInvoice.invoice_date),
        extract('month', PurchaseInvoice.invoice_date)
    ).all()
    
    return {
        "months": months,
        "monthly_data": [
            {
                "year": int(row.year),
                "month": int(row.month),
                "month_name": datetime(int(row.year), int(row.month), 1).strftime('%B'),
                "invoice_count": row.invoice_count,
                "total_amount": float(row.total_amount or 0),
                "total_tax": float(row.total_tax or 0)
            }
            for row in monthly_data
        ]
    }

@router.get("/analytics/pending-payments")
async def get_pending_payments(
    current_user: User = Depends(require_permission("purchases.view")),
    db: Session = Depends(get_db)
):
    """Get pending payment summary"""
    
    pending_invoices = db.query(PurchaseInvoice).filter(
        PurchaseInvoice.balance_amount > 0
    ).order_by(PurchaseInvoice.due_date).all()
    
    total_pending = sum(invoice.balance_amount for invoice in pending_invoices)
    overdue_invoices = [
        invoice for invoice in pending_invoices 
        if invoice.due_date and invoice.due_date < date.today()
    ]
    overdue_amount = sum(invoice.balance_amount for invoice in overdue_invoices)
    
    return {
        "summary": {
            "total_pending_invoices": len(pending_invoices),
            "total_pending_amount": float(total_pending),
            "overdue_invoices": len(overdue_invoices),
            "overdue_amount": float(overdue_amount)
        },
        "pending_invoices": [
            {
                "invoice_id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "supplier_name": invoice.supplier_name,
                "invoice_date": invoice.invoice_date,
                "due_date": invoice.due_date,
                "total_amount": float(invoice.total_amount),
                "balance_amount": float(invoice.balance_amount),
                "days_overdue": (date.today() - invoice.due_date).days if invoice.due_date and invoice.due_date < date.today() else 0
            }
            for invoice in pending_invoices[:50]  # Limit to 50 for performance
        ]
    }
# backend/app/api/endpoints/sales/enhanced_sales_production.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import datetime, date, timedelta
import json
import logging

from ...database import get_db
from ...models.core import Company, User
from ...models.sales import SaleChallan, SaleChallanItem, SaleOrder, SaleOrderItem, SaleInvoice, SaleInvoiceItem
from ...models.customers import Customer
from ...models.inventory import Item
from ...core.security import get_current_user, require_permission
from ...services.sales.enhanced_sales_service import enhanced_sales_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Enhanced Pydantic Schemas for Production
class SaleOrderCreateRequest(BaseModel):
    order_number: str
    order_date: date
    customer_id: int
    staff_id: Optional[int] = None
    order_type: str = 'standard'
    notes: Optional[str] = None
    items: List[dict]
    
    @validator('order_number')
    def validate_order_number(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Order number must be at least 3 characters')
        return v
    
    @validator('order_date')
    def validate_order_date(cls, v):
        if v > date.today():
            raise ValueError('Order date cannot be in the future')
        return v

class SaleInvoiceCreateRequest(BaseModel):
    invoice_number: str
    invoice_date: date
    customer_id: int
    staff_id: Optional[int] = None
    discount_percent: Optional[Decimal] = None
    notes: Optional[str] = None
    items: List[dict]
    
    @validator('invoice_number')
    def validate_invoice_number(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Invoice number must be at least 3 characters')
        return v
    
    @validator('discount_percent')
    def validate_discount_percent(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Discount percent must be between 0 and 100')
        return v

class SalesExportRequest(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    customer_id: Optional[int] = None
    format: str = 'excel'  # excel, pdf, csv
    
    @validator('format')
    def validate_format(cls, v):
        if v not in ['excel', 'pdf', 'csv']:
            raise ValueError('Format must be excel, pdf, or csv')
        return v

class SaleOrderResponse(BaseModel):
    id: int
    order_number: str
    order_date: date
    customer_id: int
    staff_id: Optional[int] = None
    order_type: str
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class SaleInvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    invoice_date: date
    customer_id: int
    staff_id: Optional[int] = None
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    payment_status: str
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

# Enhanced Business Logic Functions
async def _validate_inventory_availability(items: List[dict], db: Session) -> bool:
    """Validate if all items are available in inventory"""
    try:
        for item in items:
            # Check if item exists and has sufficient stock
            stock_item = db.query(Item).filter(Item.id == item['item_id']).first()
            if not stock_item or stock_item.quantity < item['quantity']:
                return False
        return True
    except Exception as e:
        logger.error(f"Inventory validation error: {str(e)}")
        return False

def _calculate_totals(items: List[dict]) -> dict:
    """Calculate sale totals"""
    subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
    tax_amount = subtotal * Decimal('0.18')  # 18% GST
    total_amount = subtotal + tax_amount
    
    return {
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'total_amount': total_amount
    }

def _apply_discounts(totals: dict, discount_percent: Optional[Decimal] = None) -> dict:
    """Apply discounts to totals"""
    if discount_percent:
        discount_amount = totals['subtotal'] * (discount_percent / 100)
        totals['discount_amount'] = discount_amount
        totals['total_amount'] = totals['subtotal'] + totals['tax_amount'] - discount_amount
    else:
        totals['discount_amount'] = Decimal('0')
    
    return totals

# Enhanced API Endpoints for Production
@router.post("/orders", response_model=SaleOrderResponse)
async def create_sale_order(
    order_data: SaleOrderCreateRequest,
    current_user: User = Depends(require_permission("sales.create")),
    db: Session = Depends(get_db)
):
    """Create a new sales order with comprehensive validation"""
    try:
        # Validate business rules
        if not await _validate_inventory_availability(order_data.items, db):
            raise HTTPException(status_code=400, detail="Insufficient inventory")
        
        # Create sales order
        order = SaleOrder(
            order_number=order_data.order_number,
            order_date=order_data.order_date,
            customer_id=order_data.customer_id,
            staff_id=order_data.staff_id,
            order_type=order_data.order_type,
            notes=order_data.notes,
            created_by=current_user.id
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        # Create order items
        for item_data in order_data.items:
            order_item = SaleOrderItem(
                order_id=order.id,
                item_id=item_data['item_id'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['quantity'] * item_data['unit_price'],
                remarks=item_data.get('remarks', '')
            )
            db.add(order_item)
        
        db.commit()
        
        logger.info(f"Sales order created: {order.order_number} by user {current_user.id}")
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating sales order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/invoices", response_model=SaleInvoiceResponse)
async def create_sale_invoice(
    invoice_data: SaleInvoiceCreateRequest,
    current_user: User = Depends(require_permission("sales.create")),
    db: Session = Depends(get_db)
):
    """Create a new sales invoice with comprehensive calculations"""
    try:
        # Calculate totals
        totals = _calculate_totals(invoice_data.items)
        totals = _apply_discounts(totals, invoice_data.discount_percent)
        
        # Create sales invoice
        invoice = SaleInvoice(
            invoice_number=invoice_data.invoice_number,
            invoice_date=invoice_data.invoice_date,
            customer_id=invoice_data.customer_id,
            staff_id=invoice_data.staff_id,
            subtotal=totals['subtotal'],
            tax_amount=totals['tax_amount'],
            discount_amount=totals['discount_amount'],
            total_amount=totals['total_amount'],
            payment_status='pending',
            notes=invoice_data.notes,
            created_by=current_user.id
        )
        
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        # Create invoice items
        for item_data in invoice_data.items:
            invoice_item = SaleInvoiceItem(
                invoice_id=invoice.id,
                item_id=item_data['item_id'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['quantity'] * item_data['unit_price'],
                remarks=item_data.get('remarks', '')
            )
            db.add(invoice_item)
        
        db.commit()
        
        logger.info(f"Sales invoice created: {invoice.invoice_number} by user {current_user.id}")
        return invoice
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating sales invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_sales_dashboard(
    current_user: User = Depends(require_permission("sales.dashboard")),
    db: Session = Depends(get_db)
):
    """Get comprehensive sales dashboard data"""
    try:
        today = date.today()
        this_month = today.replace(day=1)
        
        # Today's sales
        today_sales = db.query(func.sum(SaleInvoice.total_amount)).filter(
            func.date(SaleInvoice.invoice_date) == today
        ).scalar() or 0
        
        # This month's sales
        month_sales = db.query(func.sum(SaleInvoice.total_amount)).filter(
            SaleInvoice.invoice_date >= this_month
        ).scalar() or 0
        
        # Pending invoices
        pending_invoices = db.query(SaleInvoice).filter(
            SaleInvoice.payment_status == 'pending'
        ).count()
        
        # Recent sales
        recent_sales = db.query(SaleInvoice).order_by(
            SaleInvoice.created_at.desc()
        ).limit(5).all()
        
        # Top customers
        top_customers = db.query(
            Customer.name,
            func.sum(SaleInvoice.total_amount).label('total_amount')
        ).join(SaleInvoice).filter(
            SaleInvoice.invoice_date >= this_month
        ).group_by(Customer.id, Customer.name).order_by(
            func.sum(SaleInvoice.total_amount).desc()
        ).limit(5).all()
        
        return {
            'today_sales': float(today_sales),
            'month_sales': float(month_sales),
            'pending_invoices': pending_invoices,
            'recent_sales': [
                {
                    'id': sale.id,
                    'invoice_number': sale.invoice_number,
                    'customer_name': sale.customer.name if sale.customer else 'Unknown',
                    'total_amount': float(sale.total_amount),
                    'invoice_date': sale.invoice_date
                }
                for sale in recent_sales
            ],
            'top_customers': [
                {
                    'name': customer.name,
                    'total_amount': float(customer.total_amount)
                }
                for customer in top_customers
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting sales dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk-create")
async def bulk_create_sales(
    sales_data: List[dict],
    current_user: User = Depends(require_permission("sales.create")),
    db: Session = Depends(get_db)
):
    """Create multiple sales records at once with comprehensive validation"""
    try:
        created_sales = []
        
        for sale_data in sales_data:
            # Validate each sale
            if not await _validate_inventory_availability(sale_data.get('items', []), db):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Insufficient inventory for sale {sale_data.get('challan_number', 'Unknown')}"
                )
            
            # Create sale challan
            challan = SaleChallan(
                challan_number=sale_data['challan_number'],
                challan_date=sale_data['challan_date'],
                customer_id=sale_data['customer_id'],
                staff_id=sale_data.get('staff_id'),
                challan_type=sale_data.get('challan_type', 'delivery'),
                delivery_address=sale_data.get('delivery_address'),
                delivery_date=sale_data.get('delivery_date'),
                delivery_time=sale_data.get('delivery_time'),
                contact_person=sale_data.get('contact_person'),
                contact_phone=sale_data.get('contact_phone'),
                notes=sale_data.get('notes'),
                created_by=current_user.id
            )
            
            db.add(challan)
            db.flush()  # Get the ID
            
            # Create challan items
            for item_data in sale_data.get('items', []):
                challan_item = SaleChallanItem(
                    challan_id=challan.id,
                    item_id=item_data['item_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total_price=item_data['quantity'] * item_data['unit_price'],
                    remarks=item_data.get('remarks', '')
                )
                db.add(challan_item)
            
            created_sales.append(challan)
        
        db.commit()
        
        logger.info(f"Bulk sales created: {len(created_sales)} sales by user {current_user.id}")
        return {
            'success': True,
            'created_count': len(created_sales),
            'sales': [{'id': sale.id, 'challan_number': sale.challan_number} for sale in created_sales]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error in bulk sales creation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export")
async def export_sales_data(
    export_request: SalesExportRequest,
    current_user: User = Depends(require_permission("sales.export")),
    db: Session = Depends(get_db)
):
    """Export sales data to PDF/Excel with comprehensive filtering"""
    try:
        # Get sales data based on filters
        query = db.query(SaleInvoice)
        
        if export_request.start_date:
            query = query.filter(SaleInvoice.invoice_date >= export_request.start_date)
        if export_request.end_date:
            query = query.filter(SaleInvoice.invoice_date <= export_request.end_date)
        if export_request.customer_id:
            query = query.filter(SaleInvoice.customer_id == export_request.customer_id)
        
        sales_data = query.all()
        
        if export_request.format == 'excel':
            # Generate Excel file
            import pandas as pd
            from io import BytesIO
            
            data = []
            for sale in sales_data:
                data.append({
                    'Invoice Number': sale.invoice_number,
                    'Date': sale.invoice_date,
                    'Customer': sale.customer.name if sale.customer else 'Unknown',
                    'Subtotal': float(sale.subtotal),
                    'Tax Amount': float(sale.tax_amount),
                    'Discount Amount': float(sale.discount_amount),
                    'Total Amount': float(sale.total_amount),
                    'Status': sale.payment_status
                })
            
            df = pd.DataFrame(data)
            output = BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)
            
            logger.info(f"Sales data exported to Excel by user {current_user.id}")
            return {
                'success': True,
                'file_content': output.getvalue(),
                'filename': f'sales_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            }
        
        elif export_request.format == 'pdf':
            # Generate PDF file
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from io import BytesIO
            
            output = BytesIO()
            p = canvas.Canvas(output, pagesize=letter)
            
            # Add content to PDF
            y = 750
            p.drawString(100, y, "Sales Export Report")
            p.drawString(100, y-20, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            y -= 50
            
            for sale in sales_data:
                p.drawString(100, y, f"{sale.invoice_number} - {sale.customer.name if sale.customer else 'Unknown'} - ₹{sale.total_amount}")
                y -= 20
                if y < 50:
                    p.showPage()
                    y = 750
            
            p.save()
            output.seek(0)
            
            logger.info(f"Sales data exported to PDF by user {current_user.id}")
            return {
                'success': True,
                'file_content': output.getvalue(),
                'filename': f'sales_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            }
        
        elif export_request.format == 'csv':
            # Generate CSV file
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Invoice Number', 'Date', 'Customer', 'Subtotal', 'Tax Amount', 'Discount Amount', 'Total Amount', 'Status'])
            
            # Write data
            for sale in sales_data:
                writer.writerow([
                    sale.invoice_number,
                    sale.invoice_date,
                    sale.customer.name if sale.customer else 'Unknown',
                    sale.subtotal,
                    sale.tax_amount,
                    sale.discount_amount,
                    sale.total_amount,
                    sale.payment_status
                ])
            
            output.seek(0)
            
            logger.info(f"Sales data exported to CSV by user {current_user.id}")
            return {
                'success': True,
                'file_content': output.getvalue(),
                'filename': f'sales_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
        
    except Exception as e:
        logger.error(f"Error exporting sales data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced Analytics Endpoints
@router.get("/analytics/trends")
async def get_sales_trends(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("sales.analytics")),
    db: Session = Depends(get_db)
):
    """Get sales trends and analytics"""
    try:
        # Set default date range if not provided
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        # Get daily sales trends
        daily_sales = db.query(
            func.date(SaleInvoice.invoice_date).label('date'),
            func.sum(SaleInvoice.total_amount).label('amount'),
            func.count(SaleInvoice.id).label('count')
        ).filter(
            SaleInvoice.invoice_date >= start_date,
            SaleInvoice.invoice_date <= end_date
        ).group_by(func.date(SaleInvoice.invoice_date)).all()
        
        # Get sales by customer
        customer_sales = db.query(
            Customer.name,
            func.sum(SaleInvoice.total_amount).label('total_amount'),
            func.count(SaleInvoice.id).label('invoice_count')
        ).join(SaleInvoice).filter(
            SaleInvoice.invoice_date >= start_date,
            SaleInvoice.invoice_date <= end_date
        ).group_by(Customer.id, Customer.name).order_by(
            func.sum(SaleInvoice.total_amount).desc()
        ).limit(10).all()
        
        return {
            'daily_sales': [
                {
                    'date': str(sale.date),
                    'amount': float(sale.amount),
                    'count': sale.count
                }
                for sale in daily_sales
            ],
            'customer_sales': [
                {
                    'customer_name': customer.name,
                    'total_amount': float(customer.total_amount),
                    'invoice_count': customer.invoice_count
                }
                for customer in customer_sales
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting sales trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/performance")
async def get_sales_performance(
    current_user: User = Depends(require_permission("sales.analytics")),
    db: Session = Depends(get_db)
):
    """Get sales performance metrics"""
    try:
        today = date.today()
        this_month = today.replace(day=1)
        last_month = (this_month - timedelta(days=1)).replace(day=1)
        
        # Current month performance
        current_month_sales = db.query(func.sum(SaleInvoice.total_amount)).filter(
            SaleInvoice.invoice_date >= this_month
        ).scalar() or 0
        
        # Last month performance
        last_month_sales = db.query(func.sum(SaleInvoice.total_amount)).filter(
            SaleInvoice.invoice_date >= last_month,
            SaleInvoice.invoice_date < this_month
        ).scalar() or 0
        
        # Growth calculation
        growth_percentage = 0
        if last_month_sales > 0:
            growth_percentage = ((current_month_sales - last_month_sales) / last_month_sales) * 100
        
        # Average order value
        avg_order_value = db.query(func.avg(SaleInvoice.total_amount)).filter(
            SaleInvoice.invoice_date >= this_month
        ).scalar() or 0
        
        return {
            'current_month_sales': float(current_month_sales),
            'last_month_sales': float(last_month_sales),
            'growth_percentage': float(growth_percentage),
            'average_order_value': float(avg_order_value)
        }
        
    except Exception as e:
        logger.error(f"Error getting sales performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
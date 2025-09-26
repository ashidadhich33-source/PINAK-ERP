# backend/app/api/endpoints/reports.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract, desc
from typing import Optional, List
from datetime import datetime, date, timedelta
import io
import pandas as pd

from ...database import get_db
from ...models.sales import SalesInvoice, SalesInvoiceItem
from ...models.sales import PurchaseInvoice, PurchaseInvoiceItem
from ...models.item import Item
from ...models.stock import StockItem, StockMovement
from ...models.customer import Customer, Supplier
from ...models.payment import Payment
from ...models.user import User
from ...core.security import get_current_user, require_permission
from ...services.stock_service import StockService
from ...services.gst_service import GSTService

router = APIRouter()

# Sales Reports
@router.get("/sales/summary")
async def get_sales_summary_report(
    date_from: date = Query(...),
    date_to: date = Query(...),
    customer_id: Optional[int] = Query(None),
    cashier_id: Optional[int] = Query(None),
    current_user: User = Depends(require_permission("reports.sales")),
    db: Session = Depends(get_db)
):
    """Get sales summary report"""
    
    query = db.query(SalesInvoice).filter(
        and_(
            SalesInvoice.invoice_date >= datetime.combine(date_from, datetime.min.time()),
            SalesInvoice.invoice_date <= datetime.combine(date_to, datetime.max.time()),
            SalesInvoice.status != 'cancelled'
        )
    )
    
    if customer_id:
        query = query.filter(SalesInvoice.customer_id == customer_id)
    
    if cashier_id:
        query = query.filter(SalesInvoice.cashier_id == cashier_id)
    
    invoices = query.all()
    
    # Calculate summary
    total_invoices = len(invoices)
    total_amount = sum(invoice.total_amount for invoice in invoices)
    total_tax = sum(invoice.tax_amount for invoice in invoices)
    total_discount = sum(invoice.discount_amount for invoice in invoices)
    
    paid_invoices = [inv for inv in invoices if inv.payment_status == 'paid']
    pending_invoices = [inv for inv in invoices if inv.payment_status == 'pending']
    partial_invoices = [inv for inv in invoices if inv.payment_status == 'partial']
    
    pos_sales = [inv for inv in invoices if inv.is_pos_sale]
    regular_sales = [inv for inv in invoices if not inv.is_pos_sale]
    
    return {
        "period": {"from": date_from, "to": date_to},
        "summary": {
            "total_invoices": total_invoices,
            "total_amount": float(total_amount),
            "total_tax": float(total_tax),
            "total_discount": float(total_discount),
            "average_invoice_value": float(total_amount / total_invoices) if total_invoices > 0 else 0
        },
        "payment_status": {
            "paid": {"count": len(paid_invoices), "amount": float(sum(inv.paid_amount for inv in paid_invoices))},
            "pending": {"count": len(pending_invoices), "amount": float(sum(inv.balance_amount for inv in pending_invoices))},
            "partial": {"count": len(partial_invoices), "amount": float(sum(inv.balance_amount for inv in partial_invoices))}
        },
        "sale_types": {
            "pos_sales": {"count": len(pos_sales), "amount": float(sum(inv.total_amount for inv in pos_sales))},
            "regular_sales": {"count": len(regular_sales), "amount": float(sum(inv.total_amount for inv in regular_sales))}
        }
    }

@router.get("/sales/detailed")
async def get_detailed_sales_report(
    date_from: date = Query(...),
    date_to: date = Query(...),
    customer_id: Optional[int] = Query(None),
    export_format: str = Query("json", regex="^(json|excel)$"),
    current_user: User = Depends(require_permission("reports.sales")),
    db: Session = Depends(get_db)
):
    """Get detailed sales report with line items"""
    
    query = db.query(SalesInvoice).filter(
        and_(
            SalesInvoice.invoice_date >= datetime.combine(date_from, datetime.min.time()),
            SalesInvoice.invoice_date <= datetime.combine(date_to, datetime.max.time()),
            SalesInvoice.status != 'cancelled'
        )
    )
    
    if customer_id:
        query = query.filter(SalesInvoice.customer_id == customer_id)
    
    invoices = query.order_by(SalesInvoice.invoice_date).all()
    
    detailed_data = []
    for invoice in invoices:
        for item in invoice.invoice_items:
            detailed_data.append({
                "invoice_date": invoice.invoice_date,
                "invoice_number": invoice.invoice_number,
                "customer_name": invoice.customer_name,
                "customer_mobile": invoice.customer_mobile,
                "item_code": item.item_code,
                "item_name": item.item_name,
                "hsn_code": item.hsn_code,
                "quantity": float(item.quantity),
                "unit_price": float(item.unit_price),
                "line_total": float(item.line_total),
                "discount_amount": float(item.discount_amount),
                "tax_amount": float(item.tax_amount),
                "cgst_amount": float(item.cgst_amount),
                "sgst_amount": float(item.sgst_amount),
                "igst_amount": float(item.igst_amount),
                "payment_status": invoice.payment_status,
                "is_pos_sale": invoice.is_pos_sale
            })
    
    if export_format == "excel":
        # Create Excel file
        df = pd.DataFrame(detailed_data)
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sales Report', index=False)
        
        output.seek(0)
        filename = f"sales_detailed_{date_from}_{date_to}.xlsx"
        
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    return {
        "period": {"from": date_from, "to": date_to},
        "total_records": len(detailed_data),
        "data": detailed_data
    }

@router.get("/sales/top-customers")
async def get_top_customers_report(
    date_from: date = Query(...),
    date_to: date = Query(...),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_permission("reports.sales")),
    db: Session = Depends(get_db)
):
    """Get top customers by sales amount"""
    
    top_customers = db.query(
        SalesInvoice.customer_id,
        SalesInvoice.customer_name,
        func.count(SalesInvoice.id).label('invoice_count'),
        func.sum(SalesInvoice.total_amount).label('total_amount'),
        func.sum(SalesInvoice.tax_amount).label('total_tax'),
        func.avg(SalesInvoice.total_amount).label('average_invoice'),
        func.max(SalesInvoice.invoice_date).label('last_purchase')
    ).filter(
        and_(
            SalesInvoice.invoice_date >= datetime.combine(date_from, datetime.min.time()),
            SalesInvoice.invoice_date <= datetime.combine(date_to, datetime.max.time()),
            SalesInvoice.status != 'cancelled'
        )
    ).group_by(
        SalesInvoice.customer_id,
        SalesInvoice.customer_name
    ).order_by(
        func.sum(SalesInvoice.total_amount).desc()
    ).limit(limit).all()
    
    return {
        "period": {"from": date_from, "to": date_to},
        "customers": [
            {
                "customer_id": row.customer_id,
                "customer_name": row.customer_name,
                "invoice_count": row.invoice_count,
                "total_amount": float(row.total_amount),
                "total_tax": float(row.total_tax),
                "average_invoice": float(row.average_invoice),
                "last_purchase": row.last_purchase
            }
            for row in top_customers
        ]
    }

@router.get("/sales/top-items")
async def get_top_selling_items_report(
    date_from: date = Query(...),
    date_to: date = Query(...),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_permission("reports.sales")),
    db: Session = Depends(get_db)
):
    """Get top selling items by quantity and value"""
    
    top_items = db.query(
        SalesInvoiceItem.item_id,
        SalesInvoiceItem.item_name,
        SalesInvoiceItem.item_code,
        func.sum(SalesInvoiceItem.quantity).label('total_quantity'),
        func.sum(SalesInvoiceItem.line_total).label('total_amount'),
        func.count(SalesInvoiceItem.id).label('transaction_count'),
        func.avg(SalesInvoiceItem.unit_price).label('average_price')
    ).join(
        SalesInvoice, SalesInvoiceItem.invoice_id == SalesInvoice.id
    ).filter(
        and_(
            SalesInvoice.invoice_date >= datetime.combine(date_from, datetime.min.time()),
            SalesInvoice.invoice_date <= datetime.combine(date_to, datetime.max.time()),
            SalesInvoice.status != 'cancelled'
        )
    ).group_by(
        SalesInvoiceItem.item_id,
        SalesInvoiceItem.item_name,
        SalesInvoiceItem.item_code
    ).order_by(
        func.sum(SalesInvoiceItem.quantity).desc()
    ).limit(limit).all()
    
    return {
        "period": {"from": date_from, "to": date_to},
        "items": [
            {
                "item_id": row.item_id,
                "item_name": row.item_name,
                "item_code": row.item_code,
                "total_quantity": float(row.total_quantity),
                "total_amount": float(row.total_amount),
                "transaction_count": row.transaction_count,
                "average_price": float(row.average_price)
            }
            for row in top_items
        ]
    }

# Stock Reports
@router.get("/stock/valuation")
async def get_stock_valuation_report(
    location_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    export_format: str = Query("json", regex="^(json|excel)$"),
    current_user: User = Depends(require_permission("reports.stock")),
    db: Session = Depends(get_db)
):
    """Get stock valuation report"""
    
    stock_service = StockService()
    
    if location_id:
        # Get stock for specific location
        query = db.query(Item, StockItem).join(
            StockItem, and_(
                Item.id == StockItem.item_id,
                StockItem.location_id == location_id
            )
        ).filter(
            and_(
                Item.track_inventory == True,
                Item.status == 'active',
                StockItem.quantity > 0
            )
        )
    else:
        # Get stock for main location
        main_location = stock_service.get_main_location(db)
        query = db.query(Item, StockItem).join(
            StockItem, and_(
                Item.id == StockItem.item_id,
                StockItem.location_id == main_location.id
            )
        ).filter(
            and_(
                Item.track_inventory == True,
                Item.status == 'active',
                StockItem.quantity > 0
            )
        )
    
    if category_id:
        query = query.filter(Item.category_id == category_id)
    
    items_stock = query.all()
    
    valuation_data = []
    total_quantity = 0
    total_value = 0
    
    for item, stock in items_stock:
        unit_cost = stock.average_cost or item.landed_cost or item.purchase_rate or 0
        item_value = stock.quantity * unit_cost
        
        valuation_data.append({
            "item_code": item.barcode,
            "item_name": item.name,
            "category": item.category.display_name if item.category else "",
            "brand": item.brand or "",
            "uom": item.uom,
            "current_stock": float(stock.quantity),
            "unit_cost": float(unit_cost),
            "total_value": float(item_value),
            "last_movement_date": stock.last_movement_date,
            "min_stock_level": float(item.min_stock_level),
            "status": "Low Stock" if stock.quantity <= item.min_stock_level else "Normal"
        })
        
        total_quantity += stock.quantity
        total_value += item_value
    
    if export_format == "excel":
        df = pd.DataFrame(valuation_data)
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Stock Valuation', index=False)
        
        output.seek(0)
        filename = f"stock_valuation_{datetime.now().strftime('%Y%m%d')}.xlsx"
        
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    return {
        "summary": {
            "total_items": len(valuation_data),
            "total_quantity": float(total_quantity),
            "total_value": float(total_value)
        },
        "items": valuation_data
    }

@router.get("/stock/movements")
async def get_stock_movement_report(
    date_from: date = Query(...),
    date_to: date = Query(...),
    item_id: Optional[int] = Query(None),
    movement_type: Optional[str] = Query(None),
    export_format: str = Query("json", regex="^(json|excel)$"),
    current_user: User = Depends(require_permission("reports.stock")),
    db: Session = Depends(get_db)
):
    """Get stock movement report"""
    
    query = db.query(StockMovement, Item.name.label('item_name')).join(
        Item, StockMovement.item_id == Item.id
    ).filter(
        and_(
            StockMovement.movement_date >= datetime.combine(date_from, datetime.min.time()),
            StockMovement.movement_date <= datetime.combine(date_to, datetime.max.time())
        )
    )
    
    if item_id:
        query = query.filter(StockMovement.item_id == item_id)
    
    if movement_type:
        query = query.filter(StockMovement.movement_type == movement_type)
    
    movements = query.order_by(StockMovement.movement_date.desc()).all()
    
    movement_data = []
    for movement, item_name in movements:
        movement_data.append({
            "movement_date": movement.movement_date,
            "item_name": item_name,
            "movement_type": movement.movement_type,
            "reference_type": movement.reference_type,
            "reference_number": movement.reference_number,
            "quantity": float(movement.quantity),
            "unit_cost": float(movement.unit_cost or 0),
            "total_cost": float(movement.total_cost or 0),
            "quantity_before": float(movement.quantity_before or 0),
            "quantity_after": float(movement.quantity_after or 0),
            "remarks": movement.remarks
        })
    
    if export_format == "excel":
        df = pd.DataFrame(movement_data)
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Stock Movements', index=False)
        
        output.seek(0)
        filename = f"stock_movements_{date_from}_{date_to}.xlsx"
        
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    return {
        "period": {"from": date_from, "to": date_to},
        "total_movements": len(movement_data),
        "movements": movement_data
    }

@router.get("/stock/low-stock")
async def get_low_stock_report(
    current_user: User = Depends(require_permission("reports.stock")),
    db: Session = Depends(get_db)
):
    """Get low stock report"""
    
    stock_service = StockService()
    low_stock_items = stock_service.get_low_stock_items(db)
    
    return {
        "generated_at": datetime.now(),
        "total_items": len(low_stock_items),
        "items": low_stock_items
    }

# Financial Reports
@router.get("/financial/gst-summary")
async def get_gst_summary_report(
    date_from: date = Query(...),
    date_to: date = Query(...),
    current_user: User = Depends(require_permission("reports.financial")),
    db: Session = Depends(get_db)
):
    """Get GST summary report"""
    
    # Sales GST (Output Tax)
    sales_gst = db.query(
        func.sum(SalesInvoiceItem.cgst_amount).label('total_cgst'),
        func.sum(SalesInvoiceItem.sgst_amount).label('total_sgst'),
        func.sum(SalesInvoiceItem.igst_amount).label('total_igst'),
        func.sum(SalesInvoiceItem.tax_amount).label('total_output_tax')
    ).join(
        SalesInvoice, SalesInvoiceItem.invoice_id == SalesInvoice.id
    ).filter(
        and_(
            SalesInvoice.invoice_date >= datetime.combine(date_from, datetime.min.time()),
            SalesInvoice.invoice_date <= datetime.combine(date_to, datetime.max.time()),
            SalesInvoice.status != 'cancelled'
        )
    ).first()
    
    # Purchase GST (Input Tax)
    purchase_gst = db.query(
        func.sum(PurchaseInvoiceItem.tax_amount).label('total_input_tax')
    ).join(
        PurchaseInvoice, PurchaseInvoiceItem.invoice_id == PurchaseInvoice.id
    ).filter(
        and_(
            PurchaseInvoice.invoice_date >= datetime.combine(date_from, datetime.min.time()),
            PurchaseInvoice.invoice_date <= datetime.combine(date_to, datetime.max.time())
        )
    ).first()
    
    # GST Rate-wise breakdown
    rate_wise_sales = db.query(
        SalesInvoiceItem.cgst_rate,
        SalesInvoiceItem.sgst_rate,
        SalesInvoiceItem.igst_rate,
        func.sum(SalesInvoiceItem.line_total).label('taxable_amount'),
        func.sum(SalesInvoiceItem.tax_amount).label('tax_amount')
    ).join(
        SalesInvoice, SalesInvoiceItem.invoice_id == SalesInvoice.id
    ).filter(
        and_(
            SalesInvoice.invoice_date >= datetime.combine(date_from, datetime.min.time()),
            SalesInvoice.invoice_date <= datetime.combine(date_to, datetime.max.time()),
            SalesInvoice.status != 'cancelled'
        )
    ).group_by(
        SalesInvoiceItem.cgst_rate,
        SalesInvoiceItem.sgst_rate,
        SalesInvoiceItem.igst_rate
    ).all()
    
    output_tax = float(sales_gst.total_output_tax or 0)
    input_tax = float(purchase_gst.total_input_tax or 0)
    net_gst_liability = output_tax - input_tax
    
    return {
        "period": {"from": date_from, "to": date_to},
        "summary": {
            "output_tax": output_tax,
            "input_tax": input_tax,
            "net_gst_liability": net_gst_liability,
            "cgst_collected": float(sales_gst.total_cgst or 0),
            "sgst_collected": float(sales_gst.total_sgst or 0),
            "igst_collected": float(sales_gst.total_igst or 0)
        },
        "rate_wise_breakdown": [
            {
                "gst_rate": float((row.cgst_rate or 0) + (row.sgst_rate or 0) + (row.igst_rate or 0)),
                "taxable_amount": float(row.taxable_amount),
                "tax_amount": float(row.tax_amount),
                "cgst_rate": float(row.cgst_rate or 0),
                "sgst_rate": float(row.sgst_rate or 0),
                "igst_rate": float(row.igst_rate or 0)
            }
            for row in rate_wise_sales
        ]
    }

@router.get("/financial/profit-loss")
async def get_profit_loss_report(
    date_from: date = Query(...),
    date_to: date = Query(...),
    current_user: User = Depends(require_permission("reports.financial")),
    db: Session = Depends(get_db)
):
    """Get profit and loss report"""
    
    # Sales Revenue
    sales_revenue = db.query(
        func.sum(SalesInvoice.subtotal).label('gross_sales'),
        func.sum(SalesInvoice.discount_amount).label('sales_discount'),
        func.sum(SalesInvoice.total_amount).label('net_sales')
    ).filter(
        and_(
            SalesInvoice.invoice_date >= datetime.combine(date_from, datetime.min.time()),
            SalesInvoice.invoice_date <= datetime.combine(date_to, datetime.max.time()),
            SalesInvoice.status != 'cancelled'
        )
    ).first()
    
    # Cost of Goods Sold (simplified calculation based on average costs)
    cogs_query = db.query(
        func.sum(
            SalesInvoiceItem.quantity * 
            func.coalesce(Item.landed_cost, Item.purchase_rate, 0)
        ).label('total_cogs')
    ).join(
        SalesInvoice, SalesInvoiceItem.invoice_id == SalesInvoice.id
    ).join(
        Item, SalesInvoiceItem.item_id == Item.id
    ).filter(
        and_(
            SalesInvoice.invoice_date >= datetime.combine(date_from, datetime.min.time()),
            SalesInvoice.invoice_date <= datetime.combine(date_to, datetime.max.time()),
            SalesInvoice.status != 'cancelled'
        )
    ).first()
    
    # Purchase Expenses
    purchase_expenses = db.query(
        func.sum(PurchaseInvoice.total_amount).label('total_purchases')
    ).filter(
        and_(
            PurchaseInvoice.invoice_date >= datetime.combine(date_from, datetime.min.time()),
            PurchaseInvoice.invoice_date <= datetime.combine(date_to, datetime.max.time())
        )
    ).first()
    
    # Calculate profit metrics
    gross_sales = float(sales_revenue.gross_sales or 0)
    sales_discount = float(sales_revenue.sales_discount or 0)
    net_sales = float(sales_revenue.net_sales or 0)
    cogs = float(cogs_query.total_cogs or 0)
    total_purchases = float(purchase_expenses.total_purchases or 0)
    
    gross_profit = net_sales - cogs
    gross_profit_margin = (gross_profit / net_sales * 100) if net_sales > 0 else 0
    
    return {
        "period": {"from": date_from, "to": date_to},
        "revenue": {
            "gross_sales": gross_sales,
            "sales_discount": sales_discount,
            "net_sales": net_sales
        },
        "costs": {
            "cost_of_goods_sold": cogs,
            "total_purchases": total_purchases
        },
        "profitability": {
            "gross_profit": gross_profit,
            "gross_profit_margin": round(gross_profit_margin, 2)
        }
    }

# Dashboard Reports
@router.get("/dashboard/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard summary data"""
    
    today = date.today()
    this_month_start = date(today.year, today.month, 1)
    
    # Today's sales
    today_sales = db.query(
        func.count(SalesInvoice.id).label('invoice_count'),
        func.sum(SalesInvoice.total_amount).label('total_amount')
    ).filter(
        and_(
            SalesInvoice.invoice_date >= datetime.combine(today, datetime.min.time()),
            SalesInvoice.invoice_date <= datetime.combine(today, datetime.max.time()),
            SalesInvoice.status != 'cancelled'
        )
    ).first()
    
    # This month's sales
    month_sales = db.query(
        func.count(SalesInvoice.id).label('invoice_count'),
        func.sum(SalesInvoice.total_amount).label('total_amount')
    ).filter(
        and_(
            SalesInvoice.invoice_date >= datetime.combine(this_month_start, datetime.min.time()),
            SalesInvoice.status != 'cancelled'
        )
    ).first()
    
    # Outstanding amounts
    outstanding_receivables = db.query(
        func.sum(SalesInvoice.balance_amount)
    ).filter(
        and_(
            SalesInvoice.balance_amount > 0,
            SalesInvoice.status != 'cancelled'
        )
    ).scalar() or 0
    
    outstanding_payables = db.query(
        func.sum(PurchaseInvoice.balance_amount)
    ).filter(
        PurchaseInvoice.balance_amount > 0
    ).scalar() or 0
    
    # Low stock items count
    stock_service = StockService()
    low_stock_count = len(stock_service.get_low_stock_items(db))
    
    # Recent activities (last 10)
    recent_sales = db.query(SalesInvoice).filter(
        SalesInvoice.status != 'cancelled'
    ).order_by(desc(SalesInvoice.created_at)).limit(5).all()
    
    recent_purchases = db.query(PurchaseInvoice).order_by(
        desc(PurchaseInvoice.created_at)
    ).limit(5).all()
    
    return {
        "today": {
            "sales_count": today_sales.invoice_count or 0,
            "sales_amount": float(today_sales.total_amount or 0)
        },
        "this_month": {
            "sales_count": month_sales.invoice_count or 0,
            "sales_amount": float(month_sales.total_amount or 0)
        },
        "outstanding": {
            "receivables": float(outstanding_receivables),
            "payables": float(outstanding_payables)
        },
        "alerts": {
            "low_stock_items": low_stock_count
        },
        "recent_activities": {
            "sales": [
                {
                    "invoice_number": inv.invoice_number,
                    "customer_name": inv.customer_name,
                    "amount": float(inv.total_amount),
                    "date": inv.invoice_date
                }
                for inv in recent_sales
            ],
            "purchases": [
                {
                    "invoice_number": inv.invoice_number,
                    "supplier_name": inv.supplier_name,
                    "amount": float(inv.total_amount),
                    "date": inv.invoice_date
                }
                for inv in recent_purchases
            ]
        }
    }
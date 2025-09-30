# backend/app/services/core/bill_modification_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Dict, List, Optional
from datetime import datetime, date
from decimal import Decimal

from ...models.purchase.purchase import PurchaseBill, PurchaseBillItem
from ...models.pos.pos_models import POSTransaction, POSTransactionItem
from ...models.sales.enhanced_sales import SaleInvoice, SaleInvoiceItem
from ...core.exceptions import HTTPException


class BillModificationService:
    """Service for handling bill modification and deletion with usage tracking"""
    
    @staticmethod
    def check_purchase_bill_usage(db: Session, bill_id: int) -> Dict:
        """Check if a purchase bill's items have been used in POS or Sales"""
        
        bill = db.query(PurchaseBill).filter(PurchaseBill.id == bill_id).first()
        if not bill:
            raise HTTPException(status_code=404, detail="Purchase bill not found")
        
        # Check if any items from this bill are used
        items_used_in_pos = []
        items_used_in_sales = []
        
        for item in bill.items:
            # Check if item is used in POS transactions
            pos_usage = db.query(POSTransactionItem).filter(
                and_(
                    POSTransactionItem.barcode == item.barcode,
                    POSTransactionItem.created_at > bill.pb_date
                )
            ).first()
            
            if pos_usage:
                items_used_in_pos.append({
                    'barcode': item.barcode,
                    'style_code': item.style_code,
                    'transaction_id': pos_usage.transaction_id
                })
                # Mark item as used
                item.used_in_pos = True
                item.pos_transaction_id = pos_usage.transaction_id
                item.modification_locked = True
            
            # Check if item is used in sales
            sale_usage = db.query(SaleInvoiceItem).filter(
                and_(
                    SaleInvoiceItem.barcode == item.barcode,
                    SaleInvoiceItem.created_at > bill.pb_date
                )
            ).first()
            
            if sale_usage:
                items_used_in_sales.append({
                    'barcode': item.barcode,
                    'style_code': item.style_code,
                    'invoice_id': sale_usage.invoice_id
                })
                # Mark item as used
                item.used_in_sales = True
                item.sale_id = sale_usage.invoice_id
                item.modification_locked = True
        
        # Update bill usage tracking
        if items_used_in_pos or items_used_in_sales:
            bill.used_in_pos = len(items_used_in_pos) > 0
            bill.used_in_sales = len(items_used_in_sales) > 0
            bill.modification_locked = True
            db.commit()
        
        return {
            'bill_id': bill_id,
            'pb_no': bill.pb_no,
            'used_in_pos': len(items_used_in_pos) > 0,
            'used_in_sales': len(items_used_in_sales) > 0,
            'modification_locked': bill.modification_locked,
            'items_used_in_pos': items_used_in_pos,
            'items_used_in_sales': items_used_in_sales,
            'can_modify': not bill.modification_locked,
            'can_delete': not bill.modification_locked
        }
    
    @staticmethod
    def can_modify_purchase_bill(db: Session, bill_id: int, user_role: str) -> Dict:
        """Check if a purchase bill can be modified"""
        
        bill = db.query(PurchaseBill).filter(PurchaseBill.id == bill_id).first()
        if not bill:
            raise HTTPException(status_code=404, detail="Purchase bill not found")
        
        # Check usage first
        usage_check = BillModificationService.check_purchase_bill_usage(db, bill_id)
        
        if usage_check['modification_locked']:
            return {
                'can_modify': False,
                'reason': 'Bill items have been used in POS or Sales transactions',
                'details': usage_check
            }
        
        # Check date restrictions
        today = date.today()
        bill_date = bill.pb_date.date() if isinstance(bill.pb_date, datetime) else bill.pb_date
        
        if bill_date != today and user_role != "admin":
            return {
                'can_modify': False,
                'reason': 'Only admin can modify bills from previous days',
                'bill_date': str(bill_date),
                'today': str(today)
            }
        
        return {
            'can_modify': True,
            'reason': 'Bill can be modified',
            'bill': {
                'id': bill.id,
                'pb_no': bill.pb_no,
                'pb_date': str(bill.pb_date),
                'supplier_id': bill.supplier_id,
                'grand_total': float(bill.grand_total)
            }
        }
    
    @staticmethod
    def modify_purchase_bill(db: Session, bill_id: int, bill_data: Dict, user_id: int, user_role: str) -> Dict:
        """Modify a purchase bill with validation"""
        
        # Check if bill can be modified
        can_modify = BillModificationService.can_modify_purchase_bill(db, bill_id, user_role)
        
        if not can_modify['can_modify']:
            raise HTTPException(
                status_code=403,
                detail=can_modify['reason']
            )
        
        bill = db.query(PurchaseBill).filter(PurchaseBill.id == bill_id).first()
        
        # Update bill header
        if 'supplier_id' in bill_data:
            bill.supplier_id = bill_data['supplier_id']
        if 'supplier_bill_no' in bill_data:
            bill.supplier_bill_no = bill_data['supplier_bill_no']
        if 'supplier_bill_date' in bill_data:
            bill.supplier_bill_date = bill_data['supplier_bill_date']
        if 'payment_mode' in bill_data:
            bill.payment_mode = bill_data['payment_mode']
        if 'tax_region' in bill_data:
            bill.tax_region = bill_data['tax_region']
        if 'reverse_charge' in bill_data:
            bill.reverse_charge = bill_data['reverse_charge']
        
        # Update items if provided
        if 'items' in bill_data:
            # Delete existing items that are not locked
            for item in bill.items:
                if not item.modification_locked:
                    db.delete(item)
            
            # Add new items
            for item_data in bill_data['items']:
                new_item = PurchaseBillItem(
                    purchase_bill_id=bill.id,
                    barcode=item_data['barcode'],
                    style_code=item_data['style_code'],
                    size=item_data.get('size'),
                    hsn=item_data.get('hsn'),
                    qty=item_data['qty'],
                    basic_rate=item_data['basic_rate'],
                    cgst_rate=item_data.get('cgst_rate', 0),
                    sgst_rate=item_data.get('sgst_rate', 0),
                    igst_rate=item_data.get('igst_rate', 0),
                    line_taxable=item_data['line_taxable'],
                    cgst_amount=item_data.get('cgst_amount', 0),
                    sgst_amount=item_data.get('sgst_amount', 0),
                    igst_amount=item_data.get('igst_amount', 0),
                    line_total=item_data['line_total'],
                    mrp=item_data.get('mrp')
                )
                db.add(new_item)
        
        # Recalculate totals
        if 'grand_total' in bill_data:
            bill.grand_total = bill_data['grand_total']
        if 'total_taxable' in bill_data:
            bill.total_taxable = bill_data['total_taxable']
        if 'total_cgst' in bill_data:
            bill.total_cgst = bill_data['total_cgst']
        if 'total_sgst' in bill_data:
            bill.total_sgst = bill_data['total_sgst']
        if 'total_igst' in bill_data:
            bill.total_igst = bill_data['total_igst']
        
        bill.updated_at = datetime.utcnow()
        bill.updated_by = user_id
        
        db.commit()
        db.refresh(bill)
        
        return {
            'message': 'Purchase bill modified successfully',
            'bill_id': bill.id,
            'pb_no': bill.pb_no,
            'grand_total': float(bill.grand_total)
        }
    
    @staticmethod
    def delete_purchase_bill(db: Session, bill_id: int, user_role: str) -> Dict:
        """Delete a purchase bill with validation"""
        
        # Check if bill can be deleted
        can_modify = BillModificationService.can_modify_purchase_bill(db, bill_id, user_role)
        
        if not can_modify['can_modify']:
            raise HTTPException(
                status_code=403,
                detail=f"Cannot delete bill: {can_modify['reason']}"
            )
        
        bill = db.query(PurchaseBill).filter(PurchaseBill.id == bill_id).first()
        
        # Delete items first
        for item in bill.items:
            if item.modification_locked:
                raise HTTPException(
                    status_code=403,
                    detail=f"Cannot delete bill: Item {item.barcode} has been used"
                )
            db.delete(item)
        
        # Delete bill
        pb_no = bill.pb_no
        db.delete(bill)
        db.commit()
        
        return {
            'message': 'Purchase bill deleted successfully',
            'pb_no': pb_no
        }
    
    @staticmethod
    def can_modify_sales_invoice(db: Session, invoice_id: int, user_role: str) -> Dict:
        """Check if a sales invoice can be modified"""
        
        invoice = db.query(SaleInvoice).filter(SaleInvoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Sales invoice not found")
        
        # Check status
        if invoice.status in ['cancelled', 'paid']:
            return {
                'can_modify': False,
                'reason': f'Cannot modify {invoice.status} invoice',
                'status': invoice.status
            }
        
        # Check date restrictions
        today = date.today()
        invoice_date = invoice.invoice_date.date() if isinstance(invoice.invoice_date, datetime) else invoice.invoice_date
        
        if invoice_date != today and user_role != "admin":
            return {
                'can_modify': False,
                'reason': 'Only admin can modify invoices from previous days',
                'invoice_date': str(invoice_date),
                'today': str(today)
            }
        
        return {
            'can_modify': True,
            'reason': 'Invoice can be modified',
            'invoice': {
                'id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'invoice_date': str(invoice.invoice_date),
                'customer_id': invoice.customer_id,
                'total_amount': float(invoice.total_amount)
            }
        }
    
    @staticmethod
    def modify_sales_invoice(db: Session, invoice_id: int, invoice_data: Dict, user_id: int, user_role: str) -> Dict:
        """Modify a sales invoice with validation"""
        
        # Check if invoice can be modified
        can_modify = BillModificationService.can_modify_sales_invoice(db, invoice_id, user_role)
        
        if not can_modify['can_modify']:
            raise HTTPException(
                status_code=403,
                detail=can_modify['reason']
            )
        
        invoice = db.query(SaleInvoice).filter(SaleInvoice.id == invoice_id).first()
        
        # Update invoice header
        if 'customer_id' in invoice_data:
            invoice.customer_id = invoice_data['customer_id']
        if 'payment_mode' in invoice_data:
            invoice.payment_mode = invoice_data['payment_mode']
        if 'payment_terms' in invoice_data:
            invoice.payment_terms = invoice_data['payment_terms']
        if 'notes' in invoice_data:
            invoice.notes = invoice_data['notes']
        
        # Update items if provided
        if 'items' in invoice_data:
            # Delete existing items
            for item in invoice.invoice_items:
                db.delete(item)
            
            # Add new items
            for item_data in invoice_data['items']:
                new_item = SaleInvoiceItem(
                    invoice_id=invoice.id,
                    item_id=item_data.get('item_id'),
                    barcode=item_data.get('barcode'),
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    discount_percent=item_data.get('discount_percent', 0),
                    discount_amount=item_data.get('discount_amount', 0),
                    tax_rate=item_data.get('tax_rate', 0),
                    tax_amount=item_data.get('tax_amount', 0),
                    line_total=item_data['line_total']
                )
                db.add(new_item)
        
        # Recalculate totals
        if 'total_amount' in invoice_data:
            invoice.total_amount = invoice_data['total_amount']
        if 'subtotal' in invoice_data:
            invoice.subtotal = invoice_data['subtotal']
        if 'discount_amount' in invoice_data:
            invoice.discount_amount = invoice_data['discount_amount']
        if 'tax_amount' in invoice_data:
            invoice.tax_amount = invoice_data['tax_amount']
        
        invoice.updated_at = datetime.utcnow()
        invoice.updated_by = user_id
        
        db.commit()
        db.refresh(invoice)
        
        return {
            'message': 'Sales invoice modified successfully',
            'invoice_id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'total_amount': float(invoice.total_amount)
        }
    
    @staticmethod
    def delete_sales_invoice(db: Session, invoice_id: int, user_role: str) -> Dict:
        """Delete a sales invoice with validation"""
        
        # Check if invoice can be deleted
        can_modify = BillModificationService.can_modify_sales_invoice(db, invoice_id, user_role)
        
        if not can_modify['can_modify']:
            raise HTTPException(
                status_code=403,
                detail=f"Cannot delete invoice: {can_modify['reason']}"
            )
        
        invoice = db.query(SaleInvoice).filter(SaleInvoice.id == invoice_id).first()
        
        # Delete items first
        for item in invoice.invoice_items:
            db.delete(item)
        
        # Delete invoice
        invoice_number = invoice.invoice_number
        db.delete(invoice)
        db.commit()
        
        return {
            'message': 'Sales invoice deleted successfully',
            'invoice_number': invoice_number
        }


bill_modification_service = BillModificationService()
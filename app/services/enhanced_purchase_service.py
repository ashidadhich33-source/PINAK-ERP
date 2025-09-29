# backend/app/services/enhanced_purchase_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date
import pandas as pd
import json
import logging
import os
import uuid

from ..models.enhanced_purchase import (
    PurchaseExcelImport, PurchaseExcelImportItem, PurchaseBillMatching,
    PurchaseBillMatchingItem, DirectStockInward, DirectStockInwardItem,
    PurchaseReturn, PurchaseReturnItem, PurchaseOrder, PurchaseOrderItem,
    PurchaseInvoice, PurchaseInvoiceItem
)
from ..models.item import Item
from ..models.supplier import Supplier
from ..models.stock import StockItem, StockLocation
from ..models.purchase import PurchaseBill, PurchaseBillItem
from ..models.double_entry_accounting import JournalEntry, JournalEntryItem
from ..models.company import ChartOfAccount

logger = logging.getLogger(__name__)

class EnhancedPurchaseService:
    """Service class for enhanced purchase management"""
    
    def __init__(self):
        pass
    
    def create_purchase_journal_entry(
        self,
        db: Session,
        company_id: int,
        purchase_invoice: PurchaseInvoice,
        user_id: int = None
    ) -> JournalEntry:
        """Create journal entry for purchase invoice"""
        
        # Generate journal entry number
        entry_number = f"JE-PURCH-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        # Create journal entry
        journal_entry = JournalEntry(
            company_id=company_id,
            entry_number=entry_number,
            entry_date=purchase_invoice.invoice_date,
            reference_number=purchase_invoice.invoice_number,
            reference_type='purchase',
            reference_id=purchase_invoice.id,
            narration=f"Purchase Invoice {purchase_invoice.invoice_number}",
            total_debit=Decimal('0'),
            total_credit=Decimal('0'),
            status='draft',
            created_by=user_id
        )
        
        db.add(journal_entry)
        db.flush()  # Get the ID
        
        # Get or create accounts
        purchase_account = self._get_or_create_account(
            db, company_id, "Purchase Account", "Expense", user_id
        )
        supplier_account = self._get_or_create_account(
            db, company_id, f"Supplier: {purchase_invoice.supplier.name}", "Liability", user_id
        )
        
        # Create journal entry items
        journal_items = []
        
        # Debit: Purchase Account (Expense)
        purchase_debit = JournalEntryItem(
            company_id=company_id,
            entry_id=journal_entry.id,
            account_id=purchase_account.id,
            debit_amount=purchase_invoice.subtotal_amount,
            credit_amount=Decimal('0'),
            description=f"Purchase from {purchase_invoice.supplier.name}",
            reference=purchase_invoice.invoice_number,
            created_by=user_id
        )
        journal_items.append(purchase_debit)
        
        # Credit: Supplier Account (Accounts Payable)
        supplier_credit = JournalEntryItem(
            company_id=company_id,
            entry_id=journal_entry.id,
            account_id=supplier_account.id,
            debit_amount=Decimal('0'),
            credit_amount=purchase_invoice.total_amount,
            description=f"Purchase from {purchase_invoice.supplier.name}",
            reference=purchase_invoice.invoice_number,
            created_by=user_id
        )
        journal_items.append(supplier_credit)
        
        # Add GST entries if applicable
        if purchase_invoice.gst_amount and purchase_invoice.gst_amount > 0:
            gst_account = self._get_or_create_account(
                db, company_id, "GST Input Credit", "Asset", user_id
            )
            
            gst_debit = JournalEntryItem(
                company_id=company_id,
                entry_id=journal_entry.id,
                account_id=gst_account.id,
                debit_amount=purchase_invoice.gst_amount,
                credit_amount=Decimal('0'),
                description="GST Input Credit",
                reference=purchase_invoice.invoice_number,
                created_by=user_id
            )
            journal_items.append(gst_debit)
        
        # Add all items to database
        for item in journal_items:
            db.add(item)
        
        # Update journal entry totals
        journal_entry.total_debit = sum(item.debit_amount for item in journal_items)
        journal_entry.total_credit = sum(item.credit_amount for item in journal_items)
        journal_entry.status = 'posted'
        
        db.commit()
        
        logger.info(f"Purchase journal entry created: {entry_number}")
        return journal_entry
    
    def _get_or_create_account(
        self,
        db: Session,
        company_id: int,
        account_name: str,
        account_type: str,
        user_id: int = None
    ) -> ChartOfAccount:
        """Get or create chart of account"""
        
        # Try to find existing account
        account = db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_name == account_name
        ).first()
        
        if account:
            return account
        
        # Create new account
        account_code = f"ACC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        account = ChartOfAccount(
            company_id=company_id,
            account_code=account_code,
            account_name=account_name,
            account_type=account_type,
            is_active=True,
            created_by=user_id
        )
        
        db.add(account)
        db.commit()
        db.refresh(account)
        
        return account
    
    # Excel Import Management
    def import_purchase_excel(
        self, 
        db: Session, 
        company_id: int,
        file_path: str,
        file_name: str,
        import_name: str,
        user_id: int = None
    ) -> PurchaseExcelImport:
        """Import purchase data from Excel file"""
        
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Create import record
            import_record = PurchaseExcelImport(
                company_id=company_id,
                import_name=import_name,
                file_name=file_name,
                file_path=file_path,
                total_rows=len(df),
                import_status='processing',
                created_by=user_id
            )
            
            db.add(import_record)
            db.commit()
            db.refresh(import_record)
            
            # Process each row
            processed_rows = 0
            success_rows = 0
            error_rows = 0
            error_log = []
            
            for index, row in df.iterrows():
                try:
                    # Create import item
                    import_item = PurchaseExcelImportItem(
                        company_id=company_id,
                        import_id=import_record.id,
                        row_number=index + 1,
                        item_name=row.get('item_name', ''),
                        item_code=row.get('item_code', ''),
                        barcode=row.get('barcode', ''),
                        quantity=Decimal(str(row.get('quantity', 0))),
                        unit_price=Decimal(str(row.get('unit_price', 0))),
                        total_amount=Decimal(str(row.get('total_amount', 0))),
                        gst_rate=Decimal(str(row.get('gst_rate', 0))) if row.get('gst_rate') else None,
                        hsn_code=row.get('hsn_code', ''),
                        supplier_name=row.get('supplier_name', ''),
                        supplier_code=row.get('supplier_code', ''),
                        bill_number=row.get('bill_number', ''),
                        bill_date=pd.to_datetime(row.get('bill_date')).date() if row.get('bill_date') else None,
                        processing_status='processed',
                        created_by=user_id
                    )
                    
                    db.add(import_item)
                    success_rows += 1
                    
                except Exception as e:
                    error_log.append(f"Row {index + 1}: {str(e)}")
                    error_rows += 1
                
                processed_rows += 1
            
            # Update import record
            import_record.processed_rows = processed_rows
            import_record.success_rows = success_rows
            import_record.error_rows = error_rows
            import_record.import_status = 'completed' if error_rows == 0 else 'completed_with_errors'
            import_record.error_log = json.dumps(error_log) if error_log else None
            
            db.commit()
            
            logger.info(f"Excel import completed: {success_rows} successful, {error_rows} errors")
            
            return import_record
            
        except Exception as e:
            logger.error(f"Excel import failed: {str(e)}")
            raise ValueError(f"Excel import failed: {str(e)}")
    
    def get_excel_import_items(
        self, 
        db: Session, 
        company_id: int,
        import_id: int,
        processing_status: Optional[str] = None
    ) -> List[PurchaseExcelImportItem]:
        """Get Excel import items"""
        
        query = db.query(PurchaseExcelImportItem).filter(
            PurchaseExcelImportItem.company_id == company_id,
            PurchaseExcelImportItem.import_id == import_id
        )
        
        if processing_status:
            query = query.filter(PurchaseExcelImportItem.processing_status == processing_status)
        
        items = query.order_by(PurchaseExcelImportItem.row_number).all()
        
        return items
    
    def match_excel_items_to_master_data(
        self, 
        db: Session, 
        company_id: int,
        import_id: int,
        user_id: int = None
    ) -> Dict:
        """Match Excel import items to master data"""
        
        import_items = self.get_excel_import_items(db, company_id, import_id)
        
        matched_items = 0
        unmatched_items = 0
        matching_results = []
        
        for item in import_items:
            try:
                # Try to match item by barcode
                matched_item = None
                if item.barcode:
                    matched_item = db.query(Item).filter(
                        Item.company_id == company_id,
                        Item.barcode == item.barcode
                    ).first()
                
                # Try to match item by item code
                if not matched_item and item.item_code:
                    matched_item = db.query(Item).filter(
                        Item.company_id == company_id,
                        Item.item_code == item.item_code
                    ).first()
                
                # Try to match item by name
                if not matched_item and item.item_name:
                    matched_item = db.query(Item).filter(
                        Item.company_id == company_id,
                        Item.name.ilike(f"%{item.item_name}%")
                    ).first()
                
                # Try to match supplier
                matched_supplier = None
                if item.supplier_name:
                    matched_supplier = db.query(Supplier).filter(
                        Supplier.company_id == company_id,
                        Supplier.name.ilike(f"%{item.supplier_name}%")
                    ).first()
                
                if matched_item:
                    item.matched_item_id = matched_item.id
                    item.processing_status = 'processed'
                    matched_items += 1
                else:
                    item.processing_status = 'error'
                    item.error_message = "Item not found in master data"
                    unmatched_items += 1
                
                if matched_supplier:
                    item.matched_supplier_id = matched_supplier.id
                
                matching_results.append({
                    "row_number": item.row_number,
                    "item_name": item.item_name,
                    "matched_item_id": item.matched_item_id,
                    "matched_supplier_id": item.matched_supplier_id,
                    "status": item.processing_status
                })
                
            except Exception as e:
                item.processing_status = 'error'
                item.error_message = str(e)
                unmatched_items += 1
        
        db.commit()
        
        return {
            "import_id": import_id,
            "total_items": len(import_items),
            "matched_items": matched_items,
            "unmatched_items": unmatched_items,
            "matching_results": matching_results
        }
    
    # Bill Matching Management
    def create_bill_matching(
        self, 
        db: Session, 
        company_id: int,
        import_id: int,
        supplier_id: int,
        bill_number: str,
        bill_date: date,
        bill_amount: Decimal,
        user_id: int = None
    ) -> PurchaseBillMatching:
        """Create bill matching record"""
        
        # Create bill matching
        bill_matching = PurchaseBillMatching(
            company_id=company_id,
            import_id=import_id,
            supplier_id=supplier_id,
            bill_number=bill_number,
            bill_date=bill_date,
            bill_amount=bill_amount,
            created_by=user_id
        )
        
        db.add(bill_matching)
        db.commit()
        db.refresh(bill_matching)
        
        logger.info(f"Bill matching created: {bill_number}")
        
        return bill_matching
    
    def add_items_to_bill_matching(
        self, 
        db: Session, 
        company_id: int,
        matching_id: int,
        import_item_ids: List[int],
        user_id: int = None
    ) -> List[PurchaseBillMatchingItem]:
        """Add items to bill matching"""
        
        matching_items = []
        
        for import_item_id in import_item_ids:
            import_item = db.query(PurchaseExcelImportItem).filter(
                PurchaseExcelImportItem.id == import_item_id,
                PurchaseExcelImportItem.company_id == company_id
            ).first()
            
            if not import_item:
                continue
            
            # Calculate GST amounts
            cgst_amount = Decimal('0')
            sgst_amount = Decimal('0')
            igst_amount = Decimal('0')
            
            if import_item.gst_rate:
                gst_amount = (import_item.total_amount * import_item.gst_rate / 100)
                cgst_amount = gst_amount / 2
                sgst_amount = gst_amount / 2
                igst_amount = gst_amount
            
            # Create matching item
            matching_item = PurchaseBillMatchingItem(
                company_id=company_id,
                matching_id=matching_id,
                import_item_id=import_item_id,
                item_id=import_item.matched_item_id,
                quantity=import_item.quantity,
                unit_price=import_item.unit_price,
                total_amount=import_item.total_amount,
                gst_rate=import_item.gst_rate,
                cgst_amount=cgst_amount,
                sgst_amount=sgst_amount,
                igst_amount=igst_amount,
                is_matched=True,
                created_by=user_id
            )
            
            db.add(matching_item)
            matching_items.append(matching_item)
        
        db.commit()
        
        # Update matching status
        matching = db.query(PurchaseBillMatching).filter(
            PurchaseBillMatching.id == matching_id
        ).first()
        
        if matching:
            total_matched_amount = sum(item.total_amount for item in matching_items)
            matching.matched_amount = total_matched_amount
            matching.matching_percentage = (total_matched_amount / matching.bill_amount * 100) if matching.bill_amount > 0 else 0
            
            if matching.matching_percentage >= 100:
                matching.matching_status = 'matched'
            elif matching.matching_percentage > 0:
                matching.matching_status = 'partial'
            else:
                matching.matching_status = 'unmatched'
            
            db.commit()
        
        logger.info(f"Added {len(matching_items)} items to bill matching")
        
        return matching_items
    
    # Direct Stock Inward Management
    def create_direct_stock_inward(
        self, 
        db: Session, 
        company_id: int,
        inward_date: date,
        inward_type: str = 'opening_stock',
        reference_number: str = None,
        reference_date: date = None,
        notes: str = None,
        user_id: int = None
    ) -> DirectStockInward:
        """Create direct stock inward"""
        
        # Generate inward number
        inward_number = f"DSI-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        # Create inward record
        inward = DirectStockInward(
            company_id=company_id,
            inward_number=inward_number,
            inward_date=inward_date,
            inward_type=inward_type,
            reference_number=reference_number,
            reference_date=reference_date,
            notes=notes,
            created_by=user_id
        )
        
        db.add(inward)
        db.commit()
        db.refresh(inward)
        
        logger.info(f"Direct stock inward created: {inward_number}")
        
        return inward
    
    def add_items_to_direct_inward(
        self, 
        db: Session, 
        company_id: int,
        inward_id: int,
        items: List[Dict],
        user_id: int = None
    ) -> List[DirectStockInwardItem]:
        """Add items to direct stock inward"""
        
        inward_items = []
        total_quantity = Decimal('0')
        total_value = Decimal('0')
        
        for item_data in items:
            # Create inward item
            inward_item = DirectStockInwardItem(
                company_id=company_id,
                inward_id=inward_id,
                item_id=item_data['item_id'],
                variant_id=item_data.get('variant_id'),
                quantity=item_data['quantity'],
                unit_cost=item_data['unit_cost'],
                total_cost=item_data['quantity'] * item_data['unit_cost'],
                location_id=item_data.get('location_id'),
                batch_number=item_data.get('batch_number'),
                expiry_date=item_data.get('expiry_date'),
                notes=item_data.get('notes'),
                created_by=user_id
            )
            
            db.add(inward_item)
            inward_items.append(inward_item)
            
            total_quantity += item_data['quantity']
            total_value += inward_item.total_cost
        
        # Update inward record
        inward = db.query(DirectStockInward).filter(
            DirectStockInward.id == inward_id
        ).first()
        
        if inward:
            inward.total_quantity = total_quantity
            inward.total_value = total_value
            inward.status = 'confirmed'
            db.commit()
        
        logger.info(f"Added {len(inward_items)} items to direct stock inward")
        
        return inward_items
    
    def process_direct_stock_inward(
        self, 
        db: Session, 
        company_id: int,
        inward_id: int,
        user_id: int = None
    ) -> bool:
        """Process direct stock inward and update stock"""
        
        inward = db.query(DirectStockInward).filter(
            DirectStockInward.id == inward_id,
            DirectStockInward.company_id == company_id
        ).first()
        
        if not inward:
            return False
        
        inward_items = db.query(DirectStockInwardItem).filter(
            DirectStockInwardItem.inward_id == inward_id
        ).all()
        
        for item in inward_items:
            # Update or create stock item
            stock_item = db.query(StockItem).filter(
                StockItem.item_id == item.item_id,
                StockItem.company_id == company_id,
                StockItem.location_id == item.location_id
            ).first()
            
            if stock_item:
                # Update existing stock
                stock_item.quantity += item.quantity
                stock_item.updated_by = user_id
                stock_item.updated_at = datetime.utcnow()
            else:
                # Create new stock item
                stock_item = StockItem(
                    company_id=company_id,
                    item_id=item.item_id,
                    location_id=item.location_id,
                    quantity=item.quantity,
                    average_cost=item.unit_cost,
                    created_by=user_id
                )
                db.add(stock_item)
        
        # Update inward status
        inward.status = 'processed'
        inward.updated_by = user_id
        inward.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Direct stock inward processed: {inward.inward_number}")
        
        return True
    
    # Purchase Return Management
    def create_purchase_return(
        self, 
        db: Session, 
        company_id: int,
        supplier_id: int,
        return_date: date,
        return_reason: str = None,
        return_type: str = 'defective',
        original_bill_id: int = None,
        notes: str = None,
        user_id: int = None
    ) -> PurchaseReturn:
        """Create purchase return"""
        
        # Generate return number
        return_number = f"PR-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        # Get original bill details if provided
        original_bill = None
        if original_bill_id:
            original_bill = db.query(PurchaseBill).filter(
                PurchaseBill.id == original_bill_id,
                PurchaseBill.company_id == company_id
            ).first()
        
        # Create return record
        purchase_return = PurchaseReturn(
            company_id=company_id,
            return_number=return_number,
            return_date=return_date,
            supplier_id=supplier_id,
            original_bill_id=original_bill_id,
            original_bill_number=original_bill.bill_number if original_bill else None,
            original_bill_date=original_bill.bill_date if original_bill else None,
            return_reason=return_reason,
            return_type=return_type,
            notes=notes,
            created_by=user_id
        )
        
        db.add(purchase_return)
        db.commit()
        db.refresh(purchase_return)
        
        logger.info(f"Purchase return created: {return_number}")
        
        return purchase_return
    
    def add_items_to_purchase_return(
        self, 
        db: Session, 
        company_id: int,
        return_id: int,
        items: List[Dict],
        user_id: int = None
    ) -> List[PurchaseReturnItem]:
        """Add items to purchase return"""
        
        return_items = []
        total_quantity = Decimal('0')
        total_amount = Decimal('0')
        total_cgst = Decimal('0')
        total_sgst = Decimal('0')
        total_igst = Decimal('0')
        
        for item_data in items:
            # Calculate GST amounts
            cgst_amount = Decimal('0')
            sgst_amount = Decimal('0')
            igst_amount = Decimal('0')
            
            if item_data.get('gst_rate'):
                gst_amount = (item_data['total_amount'] * item_data['gst_rate'] / 100)
                cgst_amount = gst_amount / 2
                sgst_amount = gst_amount / 2
                igst_amount = gst_amount
            
            # Create return item
            return_item = PurchaseReturnItem(
                company_id=company_id,
                return_id=return_id,
                item_id=item_data['item_id'],
                variant_id=item_data.get('variant_id'),
                original_bill_item_id=item_data.get('original_bill_item_id'),
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_amount=item_data['total_amount'],
                gst_rate=item_data.get('gst_rate'),
                cgst_amount=cgst_amount,
                sgst_amount=sgst_amount,
                igst_amount=igst_amount,
                return_reason=item_data.get('return_reason'),
                notes=item_data.get('notes'),
                created_by=user_id
            )
            
            db.add(return_item)
            return_items.append(return_item)
            
            total_quantity += item_data['quantity']
            total_amount += item_data['total_amount']
            total_cgst += cgst_amount
            total_sgst += sgst_amount
            total_igst += igst_amount
        
        # Update return record
        return_record = db.query(PurchaseReturn).filter(
            PurchaseReturn.id == return_id
        ).first()
        
        if return_record:
            return_record.total_quantity = total_quantity
            return_record.total_amount = total_amount
            return_record.cgst_amount = total_cgst
            return_record.sgst_amount = total_sgst
            return_record.igst_amount = total_igst
            return_record.total_gst_amount = total_cgst + total_sgst + total_igst
            return_record.net_amount = total_amount + return_record.total_gst_amount
            return_record.status = 'confirmed'
            db.commit()
        
        logger.info(f"Added {len(return_items)} items to purchase return")
        
        return return_items
    
    def process_purchase_return(
        self, 
        db: Session, 
        company_id: int,
        return_id: int,
        user_id: int = None
    ) -> bool:
        """Process purchase return and update stock"""
        
        return_record = db.query(PurchaseReturn).filter(
            PurchaseReturn.id == return_id,
            PurchaseReturn.company_id == company_id
        ).first()
        
        if not return_record:
            return False
        
        return_items = db.query(PurchaseReturnItem).filter(
            PurchaseReturnItem.return_id == return_id
        ).all()
        
        for item in return_items:
            # Update stock (reduce quantity)
            stock_item = db.query(StockItem).filter(
                StockItem.item_id == item.item_id,
                StockItem.company_id == company_id
            ).first()
            
            if stock_item:
                stock_item.quantity -= item.quantity
                stock_item.updated_by = user_id
                stock_item.updated_at = datetime.utcnow()
        
        # Update return status
        return_record.status = 'processed'
        return_record.updated_by = user_id
        return_record.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Purchase return processed: {return_record.return_number}")
        
        return True
    
    # Purchase Analytics
    def get_purchase_analytics(
        self, 
        db: Session, 
        company_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict:
        """Get purchase analytics"""
        
        # Get purchase bills
        query = db.query(PurchaseBill).filter(
            PurchaseBill.company_id == company_id,
            PurchaseBill.status != 'cancelled'
        )
        
        if from_date:
            query = query.filter(PurchaseBill.bill_date >= from_date)
        
        if to_date:
            query = query.filter(PurchaseBill.bill_date <= to_date)
        
        bills = query.all()
        
        # Calculate analytics
        total_bills = len(bills)
        total_amount = sum(bill.total_amount for bill in bills)
        total_gst = sum(bill.cgst_amount + bill.sgst_amount + bill.igst_amount for bill in bills)
        
        # Get top suppliers
        supplier_analytics = db.query(
            PurchaseBill.supplier_id,
            func.count(PurchaseBill.id).label('bill_count'),
            func.sum(PurchaseBill.total_amount).label('total_amount')
        ).filter(
            PurchaseBill.company_id == company_id,
            PurchaseBill.status != 'cancelled'
        ).group_by(PurchaseBill.supplier_id).all()
        
        return {
            "period": {
                "from_date": from_date,
                "to_date": to_date
            },
            "summary": {
                "total_bills": total_bills,
                "total_amount": total_amount,
                "total_gst": total_gst,
                "average_bill_amount": total_amount / total_bills if total_bills > 0 else 0
            },
            "supplier_analytics": [
                {
                    "supplier_id": supplier.supplier_id,
                    "bill_count": supplier.bill_count,
                    "total_amount": supplier.total_amount
                }
                for supplier in supplier_analytics
            ]
        }

# Global service instance
enhanced_purchase_service = EnhancedPurchaseService()
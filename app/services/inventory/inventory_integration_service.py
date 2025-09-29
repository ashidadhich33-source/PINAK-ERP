# backend/app/services/inventory/inventory_integration_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date
import json
import logging

from ...models.inventory import Item, StockItem, ItemCategory, Brand
from ...models.sales import SaleOrder, SaleOrderItem, SaleInvoice, SaleInvoiceItem
from ...models.purchase import PurchaseOrder, PurchaseOrderItem, PurchaseBill, PurchaseBillItem
from ...models.pos.pos_models import POSTransaction, POSTransactionItem
from ...models.accounting import JournalEntry, JournalEntryItem, ChartOfAccount
from ...models.customers import Customer
from ...models.core.discount_management import DiscountRule

logger = logging.getLogger(__name__)

class InventoryIntegrationService:
    """Service for inventory integration with all modules"""
    
    def __init__(self):
        self.stock_cache = {}
        self.item_cache = {}
    
    def update_stock_on_sale(self, db: Session, sale_order_id: int) -> Dict:
        """Update stock when sale order is created/confirmed"""
        
        try:
            # Get sale order
            sale_order = db.query(SaleOrder).filter(SaleOrder.id == sale_order_id).first()
            if not sale_order:
                raise ValueError("Sale order not found")
            
            # Get sale order items
            sale_items = db.query(SaleOrderItem).filter(SaleOrderItem.sale_order_id == sale_order_id).all()
            
            stock_updates = []
            
            for item in sale_items:
                # Update stock item
                stock_item = db.query(StockItem).filter(
                    StockItem.item_id == item.item_id,
                    StockItem.location_id == sale_order.location_id
                ).first()
                
                if stock_item:
                    # Reduce available quantity
                    stock_item.available_quantity -= item.quantity
                    stock_item.reserved_quantity += item.quantity
                    stock_item.update_available_quantity()
                    
                    # Update last movement
                    stock_item.last_movement_date = datetime.utcnow()
                    stock_item.last_movement_type = 'sale'
                    
                    stock_updates.append({
                        'item_id': item.item_id,
                        'quantity_reduced': item.quantity,
                        'new_available': stock_item.available_quantity,
                        'new_reserved': stock_item.reserved_quantity
                    })
            
            db.commit()
            
            return {
                'success': True,
                'sale_order_id': sale_order_id,
                'stock_updates': stock_updates,
                'message': 'Stock updated successfully for sale order'
            }
            
        except Exception as e:
            logger.error(f"Error updating stock on sale: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to update stock: {str(e)}")
    
    def update_stock_on_purchase(self, db: Session, purchase_order_id: int) -> Dict:
        """Update stock when purchase order is received"""
        
        try:
            # Get purchase order
            purchase_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == purchase_order_id).first()
            if not purchase_order:
                raise ValueError("Purchase order not found")
            
            # Get purchase order items
            purchase_items = db.query(PurchaseOrderItem).filter(PurchaseOrderItem.purchase_order_id == purchase_order_id).all()
            
            stock_updates = []
            
            for item in purchase_items:
                # Get or create stock item
                stock_item = db.query(StockItem).filter(
                    StockItem.item_id == item.item_id,
                    StockItem.location_id == purchase_order.location_id
                ).first()
                
                if not stock_item:
                    # Create new stock item
                    stock_item = StockItem(
                        item_id=item.item_id,
                        location_id=purchase_order.location_id,
                        quantity=0,
                        reserved_quantity=0,
                        available_quantity=0,
                        average_cost=0,
                        last_cost=0
                    )
                    db.add(stock_item)
                
                # Update stock quantities
                old_quantity = stock_item.quantity
                old_average_cost = stock_item.average_cost
                
                # Calculate new average cost
                total_cost = (old_quantity * old_average_cost) + (item.quantity * item.unit_price)
                total_quantity = old_quantity + item.quantity
                new_average_cost = total_cost / total_quantity if total_quantity > 0 else 0
                
                # Update stock item
                stock_item.quantity += item.quantity
                stock_item.available_quantity += item.quantity
                stock_item.average_cost = new_average_cost
                stock_item.last_cost = item.unit_price
                stock_item.update_available_quantity()
                
                # Update last movement
                stock_item.last_movement_date = datetime.utcnow()
                stock_item.last_movement_type = 'purchase'
                
                stock_updates.append({
                    'item_id': item.item_id,
                    'quantity_added': item.quantity,
                    'new_quantity': stock_item.quantity,
                    'new_average_cost': new_average_cost,
                    'new_available': stock_item.available_quantity
                })
            
            db.commit()
            
            return {
                'success': True,
                'purchase_order_id': purchase_order_id,
                'stock_updates': stock_updates,
                'message': 'Stock updated successfully for purchase order'
            }
            
        except Exception as e:
            logger.error(f"Error updating stock on purchase: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to update stock: {str(e)}")
    
    def update_stock_on_pos_transaction(self, db: Session, pos_transaction_id: int) -> Dict:
        """Update stock when POS transaction is completed"""
        
        try:
            # Get POS transaction
            pos_transaction = db.query(POSTransaction).filter(POSTransaction.id == pos_transaction_id).first()
            if not pos_transaction:
                raise ValueError("POS transaction not found")
            
            # Get POS transaction items
            pos_items = db.query(POSTransactionItem).filter(POSTransactionItem.transaction_id == pos_transaction_id).all()
            
            stock_updates = []
            
            for item in pos_items:
                # Update stock item
                stock_item = db.query(StockItem).filter(
                    StockItem.item_id == item.item_id,
                    StockItem.location_id == pos_transaction.store_id
                ).first()
                
                if stock_item:
                    # Reduce available quantity
                    stock_item.available_quantity -= item.quantity
                    stock_item.quantity -= item.quantity
                    stock_item.update_available_quantity()
                    
                    # Update last movement
                    stock_item.last_movement_date = datetime.utcnow()
                    stock_item.last_movement_type = 'pos_sale'
                    
                    stock_updates.append({
                        'item_id': item.item_id,
                        'quantity_sold': item.quantity,
                        'new_available': stock_item.available_quantity,
                        'new_quantity': stock_item.quantity
                    })
            
            db.commit()
            
            return {
                'success': True,
                'pos_transaction_id': pos_transaction_id,
                'stock_updates': stock_updates,
                'message': 'Stock updated successfully for POS transaction'
            }
            
        except Exception as e:
            logger.error(f"Error updating stock on POS transaction: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to update stock: {str(e)}")
    
    def get_item_availability(self, db: Session, item_id: int, location_id: int) -> Dict:
        """Get item availability for sales/POS"""
        
        try:
            # Get stock item
            stock_item = db.query(StockItem).filter(
                StockItem.item_id == item_id,
                StockItem.location_id == location_id
            ).first()
            
            if not stock_item:
                return {
                    'available': False,
                    'quantity': 0,
                    'reserved': 0,
                    'available_quantity': 0,
                    'message': 'Item not found in this location'
                }
            
            # Get item details
            item = db.query(Item).filter(Item.id == item_id).first()
            
            return {
                'available': stock_item.available_quantity > 0,
                'quantity': stock_item.quantity,
                'reserved': stock_item.reserved_quantity,
                'available_quantity': stock_item.available_quantity,
                'item_name': item.name if item else 'Unknown',
                'unit_price': item.selling_price if item else 0,
                'minimum_stock': item.minimum_stock_level if item else 0,
                'is_low_stock': stock_item.available_quantity <= (item.minimum_stock_level if item else 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting item availability: {str(e)}")
            return {
                'available': False,
                'quantity': 0,
                'reserved': 0,
                'available_quantity': 0,
                'message': f'Error: {str(e)}'
            }
    
    def get_low_stock_items(self, db: Session, company_id: int, location_id: Optional[int] = None) -> List[Dict]:
        """Get low stock items for alerts"""
        
        try:
            query = db.query(Item, StockItem).join(StockItem).filter(
                Item.company_id == company_id,
                StockItem.available_quantity <= Item.minimum_stock_level
            )
            
            if location_id:
                query = query.filter(StockItem.location_id == location_id)
            
            low_stock_items = query.all()
            
            items = []
            for item, stock in low_stock_items:
                items.append({
                    'item_id': item.id,
                    'item_name': item.name,
                    'item_code': item.item_code,
                    'current_stock': stock.available_quantity,
                    'minimum_stock': item.minimum_stock_level,
                    'location_id': stock.location_id,
                    'unit_cost': stock.average_cost,
                    'is_critical': stock.available_quantity <= (item.minimum_stock_level * 0.5)
                })
            
            return items
            
        except Exception as e:
            logger.error(f"Error getting low stock items: {str(e)}")
            return []
    
    def update_item_cost_from_purchase(self, db: Session, purchase_bill_id: int) -> Dict:
        """Update item cost from purchase bill"""
        
        try:
            # Get purchase bill
            purchase_bill = db.query(PurchaseBill).filter(PurchaseBill.id == purchase_bill_id).first()
            if not purchase_bill:
                raise ValueError("Purchase bill not found")
            
            # Get purchase bill items
            bill_items = db.query(PurchaseBillItem).filter(PurchaseBillItem.purchase_bill_id == purchase_bill_id).all()
            
            cost_updates = []
            
            for item in bill_items:
                # Update item cost
                item_record = db.query(Item).filter(Item.id == item.item_id).first()
                if item_record:
                    # Update item cost
                    item_record.cost_price = item.unit_price
                    item_record.last_purchase_price = item.unit_price
                    
                    # Update stock item cost
                    stock_item = db.query(StockItem).filter(
                        StockItem.item_id == item.item_id,
                        StockItem.location_id == purchase_bill.location_id
                    ).first()
                    
                    if stock_item:
                        stock_item.last_cost = item.unit_price
                        stock_item.average_cost = item.unit_price
                    
                    cost_updates.append({
                        'item_id': item.item_id,
                        'new_cost_price': item.unit_price,
                        'item_name': item_record.name
                    })
            
            db.commit()
            
            return {
                'success': True,
                'purchase_bill_id': purchase_bill_id,
                'cost_updates': cost_updates,
                'message': 'Item costs updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error updating item cost: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to update item cost: {str(e)}")
    
    def get_inventory_valuation(self, db: Session, company_id: int, location_id: Optional[int] = None) -> Dict:
        """Get inventory valuation for accounting"""
        
        try:
            query = db.query(Item, StockItem).join(StockItem).filter(
                Item.company_id == company_id
            )
            
            if location_id:
                query = query.filter(StockItem.location_id == location_id)
            
            inventory_items = query.all()
            
            total_value = 0
            total_quantity = 0
            items = []
            
            for item, stock in inventory_items:
                item_value = stock.quantity * stock.average_cost
                total_value += item_value
                total_quantity += stock.quantity
                
                items.append({
                    'item_id': item.id,
                    'item_name': item.name,
                    'quantity': stock.quantity,
                    'average_cost': stock.average_cost,
                    'total_value': item_value,
                    'location_id': stock.location_id
                })
            
            return {
                'total_value': total_value,
                'total_quantity': total_quantity,
                'items_count': len(items),
                'items': items,
                'valuation_date': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error getting inventory valuation: {str(e)}")
            return {
                'total_value': 0,
                'total_quantity': 0,
                'items_count': 0,
                'items': [],
                'valuation_date': datetime.utcnow()
            }
    
    def create_inventory_adjustment(self, db: Session, adjustment_data: Dict) -> Dict:
        """Create inventory adjustment entry"""
        
        try:
            # Create journal entry for inventory adjustment
            journal_entry = JournalEntry(
                company_id=adjustment_data['company_id'],
                entry_number=f"INV-ADJ-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                entry_date=adjustment_data['adjustment_date'],
                reference_type='inventory_adjustment',
                reference_id=adjustment_data['adjustment_id'],
                narration=f"Inventory adjustment for {adjustment_data['reason']}",
                total_debit=adjustment_data['total_amount'],
                total_credit=adjustment_data['total_amount'],
                status='posted'
            )
            
            db.add(journal_entry)
            db.flush()
            
            # Create journal entry items
            for item in adjustment_data['items']:
                # Debit/Credit inventory account
                journal_item = JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=item['inventory_account_id'],
                    debit_amount=item['debit_amount'],
                    credit_amount=item['credit_amount'],
                    description=f"Inventory adjustment for {item['item_name']}"
                )
                db.add(journal_item)
            
            db.commit()
            
            return {
                'success': True,
                'journal_entry_id': journal_entry.id,
                'message': 'Inventory adjustment journal entry created'
            }
            
        except Exception as e:
            logger.error(f"Error creating inventory adjustment: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to create inventory adjustment: {str(e)}")
    
    def get_item_sales_history(self, db: Session, item_id: int, from_date: Optional[date] = None, to_date: Optional[date] = None) -> Dict:
        """Get item sales history for analytics"""
        
        try:
            # Get sales data
            sales_query = db.query(SaleOrderItem).filter(SaleOrderItem.item_id == item_id)
            if from_date:
                sales_query = sales_query.join(SaleOrder).filter(SaleOrder.order_date >= from_date)
            if to_date:
                sales_query = sales_query.join(SaleOrder).filter(SaleOrder.order_date <= to_date)
            
            sales_items = sales_query.all()
            
            # Get POS data
            pos_query = db.query(POSTransactionItem).filter(POSTransactionItem.item_id == item_id)
            if from_date:
                pos_query = pos_query.join(POSTransaction).filter(POSTransaction.transaction_date >= from_date)
            if to_date:
                pos_query = pos_query.join(POSTransaction).filter(POSTransaction.transaction_date <= to_date)
            
            pos_items = pos_query.all()
            
            # Calculate totals
            total_sales_quantity = sum(item.quantity for item in sales_items)
            total_sales_amount = sum(item.quantity * item.unit_price for item in sales_items)
            total_pos_quantity = sum(item.quantity for item in pos_items)
            total_pos_amount = sum(item.quantity * item.unit_price for item in pos_items)
            
            return {
                'item_id': item_id,
                'sales_quantity': total_sales_quantity,
                'sales_amount': total_sales_amount,
                'pos_quantity': total_pos_quantity,
                'pos_amount': total_pos_amount,
                'total_quantity': total_sales_quantity + total_pos_quantity,
                'total_amount': total_sales_amount + total_pos_amount,
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting item sales history: {str(e)}")
            return {
                'item_id': item_id,
                'sales_quantity': 0,
                'sales_amount': 0,
                'pos_quantity': 0,
                'pos_amount': 0,
                'total_quantity': 0,
                'total_amount': 0,
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                }
            }
    
    def get_item_purchase_history(self, db: Session, item_id: int, from_date: Optional[date] = None, to_date: Optional[date] = None) -> Dict:
        """Get item purchase history for analytics"""
        
        try:
            # Get purchase data
            purchase_query = db.query(PurchaseOrderItem).filter(PurchaseOrderItem.item_id == item_id)
            if from_date:
                purchase_query = purchase_query.join(PurchaseOrder).filter(PurchaseOrder.order_date >= from_date)
            if to_date:
                purchase_query = purchase_query.join(PurchaseOrder).filter(PurchaseOrder.order_date <= to_date)
            
            purchase_items = purchase_query.all()
            
            # Calculate totals
            total_quantity = sum(item.quantity for item in purchase_items)
            total_amount = sum(item.quantity * item.unit_price for item in purchase_items)
            average_cost = total_amount / total_quantity if total_quantity > 0 else 0
            
            return {
                'item_id': item_id,
                'total_quantity': total_quantity,
                'total_amount': total_amount,
                'average_cost': average_cost,
                'purchase_count': len(purchase_items),
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting item purchase history: {str(e)}")
            return {
                'item_id': item_id,
                'total_quantity': 0,
                'total_amount': 0,
                'average_cost': 0,
                'purchase_count': 0,
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                }
            }
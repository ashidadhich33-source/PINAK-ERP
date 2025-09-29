# backend/app/services/pos/pos_real_time_integration_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date, timedelta
import json
import logging
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

from ...models.pos.pos_models import POSTransaction, POSTransactionItem, POSPayment, POSSession
from ...models.customers import Customer
from ...models.inventory import Item, StockItem
from ...models.accounting import JournalEntry, JournalEntryItem, ChartOfAccount
from ...models.core.discount_management import DiscountRule, DiscountCoupon, CustomerDiscount
from ...models.loyalty import LoyaltyTransaction, LoyaltyProgram
from ...models.sales import SaleOrder, SaleInvoice
from ...models.core.payment import Payment

logger = logging.getLogger(__name__)

class POSRealTimeIntegrationService:
    """Service for real-time POS integration with all modules"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.pos_sessions: Dict[int, Dict] = {}
        self.real_time_cache = {}
    
    async def connect_websocket(self, websocket: WebSocket, session_id: int):
        """Connect WebSocket for real-time POS updates"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Initialize POS session
        self.pos_sessions[session_id] = {
            'websocket': websocket,
            'session_id': session_id,
            'connected_at': datetime.utcnow(),
            'last_activity': datetime.utcnow()
        }
        
        logger.info(f"POS WebSocket connected for session {session_id}")
    
    async def disconnect_websocket(self, websocket: WebSocket, session_id: int):
        """Disconnect WebSocket"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if session_id in self.pos_sessions:
            del self.pos_sessions[session_id]
        
        logger.info(f"POS WebSocket disconnected for session {session_id}")
    
    async def broadcast_to_session(self, session_id: int, message: Dict):
        """Broadcast message to specific POS session"""
        if session_id in self.pos_sessions:
            websocket = self.pos_sessions[session_id]['websocket']
            try:
                await websocket.send_json(message)
                self.pos_sessions[session_id]['last_activity'] = datetime.utcnow()
            except Exception as e:
                logger.error(f"Error broadcasting to session {session_id}: {str(e)}")
                await self.disconnect_websocket(websocket, session_id)
    
    async def broadcast_to_all(self, message: Dict):
        """Broadcast message to all active POS sessions"""
        for session_id, session_data in self.pos_sessions.items():
            await self.broadcast_to_session(session_id, message)
    
    def create_pos_transaction_with_real_time_integrations(self, db: Session, transaction_data: Dict) -> Dict:
        """Create POS transaction with real-time integrations"""
        
        try:
            # Create POS transaction
            pos_transaction = POSTransaction(
                company_id=transaction_data['company_id'],
                session_id=transaction_data['session_id'],
                transaction_number=transaction_data['transaction_number'],
                transaction_date=transaction_data['transaction_date'],
                customer_id=transaction_data.get('customer_id'),
                staff_id=transaction_data['staff_id'],
                subtotal=transaction_data['subtotal'],
                discount_amount=transaction_data.get('discount_amount', 0),
                tax_amount=transaction_data.get('tax_amount', 0),
                total_amount=transaction_data['total_amount'],
                payment_method=transaction_data['payment_method'],
                status='completed'
            )
            
            db.add(pos_transaction)
            db.flush()
            
            # Create transaction items
            transaction_items = []
            for item_data in transaction_data['items']:
                transaction_item = POSTransactionItem(
                    transaction_id=pos_transaction.id,
                    item_id=item_data['item_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total_price=item_data['total_price'],
                    discount_amount=item_data.get('discount_amount', 0)
                )
                db.add(transaction_item)
                transaction_items.append(transaction_item)
            
            db.flush()
            
            # Real-time integrations
            integration_results = {}
            
            # 1. Real-time Inventory Integration
            inventory_result = self.real_time_inventory_integration(db, pos_transaction, transaction_items)
            integration_results['inventory'] = inventory_result
            
            # 2. Real-time Customer Integration
            customer_result = self.real_time_customer_integration(db, pos_transaction)
            integration_results['customer'] = customer_result
            
            # 3. Real-time Discount Integration
            discount_result = self.real_time_discount_integration(db, pos_transaction, transaction_data.get('applied_discounts', []))
            integration_results['discounts'] = discount_result
            
            # 4. Real-time Loyalty Integration
            loyalty_result = self.real_time_loyalty_integration(db, pos_transaction)
            integration_results['loyalty'] = loyalty_result
            
            # 5. Real-time Accounting Integration
            accounting_result = self.real_time_accounting_integration(db, pos_transaction)
            integration_results['accounting'] = accounting_result
            
            # 6. Real-time Sales Integration
            sales_result = self.real_time_sales_integration(db, pos_transaction)
            integration_results['sales'] = sales_result
            
            db.commit()
            
            # Send real-time updates
            asyncio.create_task(self.send_real_time_updates(
                pos_transaction.session_id,
                {
                    'type': 'transaction_completed',
                    'transaction_id': pos_transaction.id,
                    'transaction_number': pos_transaction.transaction_number,
                    'total_amount': pos_transaction.total_amount,
                    'integration_results': integration_results
                }
            ))
            
            return {
                'success': True,
                'transaction_id': pos_transaction.id,
                'transaction_number': pos_transaction.transaction_number,
                'integration_results': integration_results,
                'message': 'POS transaction completed with real-time integrations'
            }
            
        except Exception as e:
            logger.error(f"Error creating POS transaction with real-time integrations: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to create POS transaction: {str(e)}")
    
    def real_time_inventory_integration(self, db: Session, pos_transaction: POSTransaction, transaction_items: List[POSTransactionItem]) -> Dict:
        """Real-time inventory integration for POS transaction"""
        
        try:
            stock_updates = []
            
            for item in transaction_items:
                # Get stock item
                stock_item = db.query(StockItem).filter(
                    StockItem.item_id == item.item_id,
                    StockItem.location_id == pos_transaction.store_id
                ).first()
                
                if stock_item:
                    # Update stock in real-time
                    stock_item.quantity -= item.quantity
                    stock_item.available_quantity -= item.quantity
                    stock_item.update_available_quantity()
                    
                    # Update last movement
                    stock_item.last_movement_date = datetime.utcnow()
                    stock_item.last_movement_type = 'pos_sale'
                    
                    stock_updates.append({
                        'item_id': item.item_id,
                        'quantity_sold': item.quantity,
                        'new_quantity': stock_item.quantity,
                        'new_available': stock_item.available_quantity,
                        'is_low_stock': stock_item.available_quantity <= (stock_item.item.minimum_stock_level if hasattr(stock_item, 'item') else 0)
                    })
            
            return {
                'status': 'success',
                'stock_updates': stock_updates,
                'message': 'Stock updated in real-time'
            }
            
        except Exception as e:
            logger.error(f"Error in real-time inventory integration: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def real_time_customer_integration(self, db: Session, pos_transaction: POSTransaction) -> Dict:
        """Real-time customer integration for POS transaction"""
        
        try:
            if not pos_transaction.customer_id:
                return {'status': 'skipped', 'message': 'No customer specified'}
            
            # Get customer
            customer = db.query(Customer).filter(Customer.id == pos_transaction.customer_id).first()
            if not customer:
                return {'status': 'error', 'message': 'Customer not found'}
            
            # Update customer analytics in real-time
            customer.total_purchases = (customer.total_purchases or 0) + pos_transaction.total_amount
            customer.last_purchase_date = pos_transaction.transaction_date
            
            # Update customer tier if applicable
            if hasattr(customer, 'customer_tier'):
                new_tier = self.calculate_customer_tier(db, customer)
                if new_tier != customer.customer_tier:
                    customer.customer_tier = new_tier
            
            return {
                'status': 'success',
                'customer_id': customer.id,
                'customer_name': customer.name,
                'total_purchases': customer.total_purchases,
                'customer_tier': getattr(customer, 'customer_tier', 'regular')
            }
            
        except Exception as e:
            logger.error(f"Error in real-time customer integration: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def real_time_discount_integration(self, db: Session, pos_transaction: POSTransaction, applied_discounts: List[Dict]) -> Dict:
        """Real-time discount integration for POS transaction"""
        
        try:
            discount_applications = []
            
            for discount_data in applied_discounts:
                # Get discount rule
                discount_rule = db.query(DiscountRule).filter(
                    DiscountRule.id == discount_data['discount_id']
                ).first()
                
                if discount_rule:
                    # Apply discount in real-time
                    discount_amount = self.calculate_discount_amount(
                        discount_rule, pos_transaction.subtotal
                    )
                    
                    discount_applications.append({
                        'discount_id': discount_rule.id,
                        'discount_name': discount_rule.rule_name,
                        'discount_amount': discount_amount,
                        'discount_type': discount_rule.rule_type
                    })
            
            return {
                'status': 'success',
                'applied_discounts': discount_applications,
                'total_discount': sum(d['discount_amount'] for d in discount_applications)
            }
            
        except Exception as e:
            logger.error(f"Error in real-time discount integration: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def real_time_loyalty_integration(self, db: Session, pos_transaction: POSTransaction) -> Dict:
        """Real-time loyalty integration for POS transaction"""
        
        try:
            if not pos_transaction.customer_id:
                return {'status': 'skipped', 'message': 'No customer specified'}
            
            # Get customer loyalty program
            loyalty_program = db.query(LoyaltyProgram).filter(
                LoyaltyProgram.company_id == pos_transaction.company_id
            ).first()
            
            if not loyalty_program:
                return {'status': 'skipped', 'message': 'No loyalty program found'}
            
            # Calculate points earned in real-time
            points_earned = int(pos_transaction.total_amount * loyalty_program.points_per_rupee)
            
            if points_earned > 0:
                # Create loyalty transaction in real-time
                loyalty_transaction = LoyaltyTransaction(
                    customer_id=pos_transaction.customer_id,
                    transaction_type='earned',
                    points=points_earned,
                    reference_type='pos_transaction',
                    reference_id=pos_transaction.id,
                    reference_number=pos_transaction.transaction_number,
                    description=f"Points earned for POS transaction {pos_transaction.transaction_number}"
                )
                
                db.add(loyalty_transaction)
            
            return {
                'status': 'success',
                'points_earned': points_earned,
                'loyalty_program': loyalty_program.program_name
            }
            
        except Exception as e:
            logger.error(f"Error in real-time loyalty integration: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def real_time_accounting_integration(self, db: Session, pos_transaction: POSTransaction) -> Dict:
        """Real-time accounting integration for POS transaction"""
        
        try:
            # Create journal entry in real-time
            journal_entry = JournalEntry(
                company_id=pos_transaction.company_id,
                entry_number=f"POS-{pos_transaction.transaction_number}",
                entry_date=pos_transaction.transaction_date,
                reference_type='pos_transaction',
                reference_id=pos_transaction.id,
                narration=f"POS transaction {pos_transaction.transaction_number}",
                total_debit=pos_transaction.total_amount,
                total_credit=pos_transaction.total_amount,
                status='posted'
            )
            
            db.add(journal_entry)
            db.flush()
            
            # Create journal entry items in real-time
            # Debit: Cash/Bank
            cash_account = self.get_cash_account(db, pos_transaction.company_id)
            journal_item_cash = JournalEntryItem(
                entry_id=journal_entry.id,
                account_id=cash_account.id,
                debit_amount=pos_transaction.total_amount,
                credit_amount=0,
                description=f"Cash received for POS transaction {pos_transaction.transaction_number}"
            )
            db.add(journal_item_cash)
            
            # Credit: Sales Revenue
            sales_account = self.get_sales_revenue_account(db, pos_transaction.company_id)
            journal_item_sales = JournalEntryItem(
                entry_id=journal_entry.id,
                account_id=sales_account.id,
                debit_amount=0,
                credit_amount=pos_transaction.total_amount,
                description=f"Sales revenue for POS transaction {pos_transaction.transaction_number}"
            )
            db.add(journal_item_sales)
            
            return {
                'status': 'success',
                'journal_entry_id': journal_entry.id,
                'message': 'Journal entry created in real-time'
            }
            
        except Exception as e:
            logger.error(f"Error in real-time accounting integration: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def real_time_sales_integration(self, db: Session, pos_transaction: POSTransaction) -> Dict:
        """Real-time sales integration for POS transaction"""
        
        try:
            # Create sale order in real-time
            sale_order = SaleOrder(
                company_id=pos_transaction.company_id,
                order_number=f"POS-{pos_transaction.transaction_number}",
                order_date=pos_transaction.transaction_date,
                customer_id=pos_transaction.customer_id,
                staff_id=pos_transaction.staff_id,
                subtotal=pos_transaction.subtotal,
                discount_amount=pos_transaction.discount_amount,
                tax_amount=pos_transaction.tax_amount,
                total_amount=pos_transaction.total_amount,
                status='completed',
                payment_terms='cash',
                notes=f"POS transaction {pos_transaction.transaction_number}"
            )
            
            db.add(sale_order)
            db.flush()
            
            # Create sale invoice in real-time
            sale_invoice = SaleInvoice(
                company_id=pos_transaction.company_id,
                invoice_number=f"POS-INV-{pos_transaction.transaction_number}",
                invoice_date=pos_transaction.transaction_date,
                customer_id=pos_transaction.customer_id,
                sale_order_id=sale_order.id,
                subtotal=pos_transaction.subtotal,
                discount_amount=pos_transaction.discount_amount,
                tax_amount=pos_transaction.tax_amount,
                total_amount=pos_transaction.total_amount,
                payment_status='paid',
                notes=f"POS transaction {pos_transaction.transaction_number}"
            )
            
            db.add(sale_invoice)
            
            return {
                'status': 'success',
                'sale_order_id': sale_order.id,
                'sale_invoice_id': sale_invoice.id,
                'message': 'Sales records created in real-time'
            }
            
        except Exception as e:
            logger.error(f"Error in real-time sales integration: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def send_real_time_updates(self, session_id: int, update_data: Dict):
        """Send real-time updates to POS session"""
        try:
            await self.broadcast_to_session(session_id, update_data)
        except Exception as e:
            logger.error(f"Error sending real-time updates: {str(e)}")
    
    async def send_inventory_updates(self, session_id: int, inventory_data: Dict):
        """Send real-time inventory updates"""
        try:
            update_message = {
                'type': 'inventory_update',
                'data': inventory_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            await self.broadcast_to_session(session_id, update_message)
        except Exception as e:
            logger.error(f"Error sending inventory updates: {str(e)}")
    
    async def send_customer_updates(self, session_id: int, customer_data: Dict):
        """Send real-time customer updates"""
        try:
            update_message = {
                'type': 'customer_update',
                'data': customer_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            await self.broadcast_to_session(session_id, update_message)
        except Exception as e:
            logger.error(f"Error sending customer updates: {str(e)}")
    
    async def send_discount_updates(self, session_id: int, discount_data: Dict):
        """Send real-time discount updates"""
        try:
            update_message = {
                'type': 'discount_update',
                'data': discount_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            await self.broadcast_to_session(session_id, update_message)
        except Exception as e:
            logger.error(f"Error sending discount updates: {str(e)}")
    
    async def send_loyalty_updates(self, session_id: int, loyalty_data: Dict):
        """Send real-time loyalty updates"""
        try:
            update_message = {
                'type': 'loyalty_update',
                'data': loyalty_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            await self.broadcast_to_session(session_id, update_message)
        except Exception as e:
            logger.error(f"Error sending loyalty updates: {str(e)}")
    
    def get_real_time_pos_analytics(self, db: Session, company_id: int, session_id: Optional[int] = None) -> Dict:
        """Get real-time POS analytics"""
        
        try:
            # Get POS session data
            if session_id:
                session_query = db.query(POSSession).filter(
                    POSSession.id == session_id,
                    POSSession.company_id == company_id
                )
            else:
                session_query = db.query(POSSession).filter(
                    POSSession.company_id == company_id
                )
            
            sessions = session_query.all()
            
            # Get transaction data
            transaction_query = db.query(POSTransaction).filter(
                POSTransaction.company_id == company_id
            )
            
            if session_id:
                transaction_query = transaction_query.filter(POSTransaction.session_id == session_id)
            
            transactions = transaction_query.all()
            
            # Calculate real-time metrics
            total_sessions = len(sessions)
            active_sessions = len([s for s in sessions if s.status == 'active'])
            total_transactions = len(transactions)
            total_sales = sum(t.total_amount for t in transactions)
            average_transaction = total_sales / total_transactions if total_transactions > 0 else 0
            
            # Get real-time customer data
            customer_data = self.get_real_time_customer_data(db, company_id)
            
            # Get real-time inventory data
            inventory_data = self.get_real_time_inventory_data(db, company_id)
            
            return {
                'sessions': {
                    'total_sessions': total_sessions,
                    'active_sessions': active_sessions,
                    'inactive_sessions': total_sessions - active_sessions
                },
                'transactions': {
                    'total_transactions': total_transactions,
                    'total_sales': total_sales,
                    'average_transaction': average_transaction
                },
                'customers': customer_data,
                'inventory': inventory_data,
                'last_updated': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time POS analytics: {str(e)}")
            return {
                'sessions': {'total_sessions': 0, 'active_sessions': 0, 'inactive_sessions': 0},
                'transactions': {'total_transactions': 0, 'total_sales': 0, 'average_transaction': 0},
                'customers': {},
                'inventory': {},
                'last_updated': datetime.utcnow()
            }
    
    def get_real_time_customer_data(self, db: Session, company_id: int) -> Dict:
        """Get real-time customer data"""
        try:
            # Get active customers
            active_customers = db.query(Customer).filter(
                Customer.company_id == company_id,
                Customer.is_active == True
            ).count()
            
            # Get customers with recent transactions
            recent_customers = db.query(Customer).join(POSTransaction).filter(
                Customer.company_id == company_id,
                POSTransaction.transaction_date >= datetime.utcnow() - timedelta(hours=24)
            ).distinct().count()
            
            return {
                'active_customers': active_customers,
                'recent_customers': recent_customers
            }
        except Exception as e:
            logger.error(f"Error getting real-time customer data: {str(e)}")
            return {'active_customers': 0, 'recent_customers': 0}
    
    def get_real_time_inventory_data(self, db: Session, company_id: int) -> Dict:
        """Get real-time inventory data"""
        try:
            # Get total items
            total_items = db.query(Item).filter(Item.company_id == company_id).count()
            
            # Get low stock items
            low_stock_items = db.query(Item).join(StockItem).filter(
                Item.company_id == company_id,
                StockItem.available_quantity <= Item.minimum_stock_level
            ).count()
            
            # Get out of stock items
            out_of_stock_items = db.query(Item).join(StockItem).filter(
                Item.company_id == company_id,
                StockItem.available_quantity <= 0
            ).count()
            
            return {
                'total_items': total_items,
                'low_stock_items': low_stock_items,
                'out_of_stock_items': out_of_stock_items
            }
        except Exception as e:
            logger.error(f"Error getting real-time inventory data: {str(e)}")
            return {'total_items': 0, 'low_stock_items': 0, 'out_of_stock_items': 0}
    
    # Helper methods
    def calculate_customer_tier(self, db: Session, customer: Customer) -> str:
        """Calculate customer tier based on total purchases"""
        try:
            total_purchases = customer.total_purchases or 0
            
            if total_purchases >= 100000:
                return 'platinum'
            elif total_purchases >= 50000:
                return 'gold'
            elif total_purchases >= 10000:
                return 'silver'
            else:
                return 'bronze'
        except Exception as e:
            logger.error(f"Error calculating customer tier: {str(e)}")
            return 'bronze'
    
    def calculate_discount_amount(self, discount_rule: DiscountRule, amount: Decimal) -> Decimal:
        """Calculate discount amount for rule"""
        try:
            if discount_rule.discount_percentage:
                discount_amount = amount * (discount_rule.discount_percentage / 100)
            else:
                discount_amount = discount_rule.discount_value
            
            # Apply maximum discount limit
            if discount_rule.max_discount_amount:
                discount_amount = min(discount_amount, discount_rule.max_discount_amount)
            
            return discount_amount
        except Exception as e:
            logger.error(f"Error calculating discount amount: {str(e)}")
            return 0
    
    def get_cash_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get cash account"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_name.ilike('%cash%')
        ).first()
    
    def get_sales_revenue_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get sales revenue account"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_type == 'revenue'
        ).first()
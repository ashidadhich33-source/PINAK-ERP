# backend/app/services/stock_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime
import logging

from ..models.stock import StockLocation, StockItem, StockMovement, StockAdjustment, StockAdjustmentItem
from ..models.item import Item

logger = logging.getLogger(__name__)

class StockService:
    """Service class for stock management operations"""
    
    def __init__(self):
        self.main_location_code = "MAIN"
    
    def get_main_location(self, db: Session) -> StockLocation:
        """Get the main stock location"""
        location = db.query(StockLocation).filter(
            StockLocation.code == self.main_location_code
        ).first()
        
        if not location:
            # Create main location if it doesn't exist
            location = StockLocation(
                code=self.main_location_code,
                name="Main Store",
                description="Primary stock location",
                is_main_location=True
            )
            db.add(location)
            db.commit()
        
        return location
    
    def get_item_stock(self, db: Session, item_id: int, location_id: Optional[int] = None) -> Optional[Decimal]:
        """Get current stock quantity for an item"""
        
        if location_id is None:
            location = self.get_main_location(db)
            location_id = location.id
        
        stock_item = db.query(StockItem).filter(
            and_(StockItem.item_id == item_id, StockItem.location_id == location_id)
        ).first()
        
        return stock_item.quantity if stock_item else Decimal('0')
    
    def get_item_stock_all_locations(self, db: Session, item_id: int) -> Dict[int, Decimal]:
        """Get stock quantities for an item across all locations"""
        
        stock_items = db.query(StockItem).filter(StockItem.item_id == item_id).all()
        
        return {stock.location_id: stock.quantity for stock in stock_items}
    
    def initialize_item_stock(self, db: Session, item_id: int, location_id: Optional[int] = None):
        """Initialize stock record for an item"""
        
        if location_id is None:
            location = self.get_main_location(db)
            location_id = location.id
        
        # Check if stock record already exists
        existing = db.query(StockItem).filter(
            and_(StockItem.item_id == item_id, StockItem.location_id == location_id)
        ).first()
        
        if not existing:
            stock_item = StockItem(
                item_id=item_id,
                location_id=location_id,
                quantity=Decimal('0'),
                reserved_quantity=Decimal('0'),
                available_quantity=Decimal('0'),
                average_cost=Decimal('0'),
                last_cost=Decimal('0')
            )
            db.add(stock_item)
            db.commit()
            logger.info(f"Initialized stock for item {item_id} at location {location_id}")
    
    def add_stock_movement(
        self, 
        db: Session, 
        item_id: int, 
        location_id: int,
        movement_type: str,
        quantity: Decimal,
        unit_cost: Optional[Decimal] = None,
        reference_type: Optional[str] = None,
        reference_id: Optional[int] = None,
        reference_number: Optional[str] = None,
        remarks: Optional[str] = None
    ) -> StockMovement:
        """Add a stock movement and update stock levels"""
        
        # Get current stock
        stock_item = db.query(StockItem).filter(
            and_(StockItem.item_id == item_id, StockItem.location_id == location_id)
        ).first()
        
        if not stock_item:
            # Initialize stock if it doesn't exist
            self.initialize_item_stock(db, item_id, location_id)
            stock_item = db.query(StockItem).filter(
                and_(StockItem.item_id == item_id, StockItem.location_id == location_id)
            ).first()
        
        # Calculate quantity change based on movement type
        quantity_change = quantity if movement_type in ['in', 'adjustment_in'] else -quantity
        
        # Store before quantity
        quantity_before = stock_item.quantity
        quantity_after = quantity_before + quantity_change
        
        # Validate negative stock if not allowed
        item = db.query(Item).filter(Item.id == item_id).first()
        if quantity_after < 0 and not (item and item.allow_negative_stock):
            raise ValueError(f"Insufficient stock. Available: {quantity_before}, Required: {quantity}")
        
        # Create stock movement record
        movement = StockMovement(
            item_id=item_id,
            location_id=location_id,
            movement_type=movement_type,
            reference_type=reference_type,
            reference_id=reference_id,
            reference_number=reference_number,
            quantity=quantity,
            unit_cost=unit_cost,
            total_cost=quantity * unit_cost if unit_cost else None,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            remarks=remarks
        )
        
        db.add(movement)
        
        # Update stock item
        stock_item.quantity = quantity_after
        stock_item.last_movement_date = datetime.utcnow()
        stock_item.last_movement_type = movement_type
        
        # Update cost information for incoming stock
        if movement_type in ['in', 'adjustment_in'] and unit_cost:
            # Calculate new average cost using weighted average
            if stock_item.quantity > 0:
                total_cost = (stock_item.quantity * stock_item.average_cost) + (quantity * unit_cost)
                stock_item.average_cost = total_cost / stock_item.quantity
            stock_item.last_cost = unit_cost
        
        # Update available quantity
        stock_item.update_available_quantity()
        
        db.commit()
        
        logger.info(f"Stock movement added: Item {item_id}, Type: {movement_type}, Qty: {quantity}")
        
        return movement
    
    def adjust_stock(
        self, 
        db: Session, 
        adjustments: List[Dict],
        location_id: Optional[int] = None,
        reason: str = "Manual Adjustment",
        approved_by: Optional[int] = None
    ) -> StockAdjustment:
        """Process stock adjustment for multiple items"""
        
        if location_id is None:
            location = self.get_main_location(db)
            location_id = location.id
        
        # Generate adjustment number
        adjustment_count = db.query(StockAdjustment).count() + 1
        adjustment_number = f"ADJ{adjustment_count:06d}"
        
        # Create adjustment header
        adjustment = StockAdjustment(
            adjustment_number=adjustment_number,
            location_id=location_id,
            adjustment_type="recount",
            reason=reason,
            approved_by=approved_by,
            status="approved" if approved_by else "draft"
        )
        
        db.add(adjustment)
        db.flush()  # Get adjustment ID
        
        total_adjustment_value = Decimal('0')
        
        for adj_data in adjustments:
            item_id = adj_data['item_id']
            physical_quantity = Decimal(str(adj_data['physical_quantity']))
            unit_cost = Decimal(str(adj_data.get('unit_cost', 0)))
            
            # Get current stock
            current_stock = self.get_item_stock(db, item_id, location_id)
            adjustment_qty = physical_quantity - current_stock
            
            # Create adjustment item record
            adj_item = StockAdjustmentItem(
                adjustment_id=adjustment.id,
                item_id=item_id,
                book_quantity=current_stock,
                physical_quantity=physical_quantity,
                adjustment_quantity=adjustment_qty,
                unit_cost=unit_cost
            )
            adj_item.calculate_adjustment()
            
            db.add(adj_item)
            
            # Add stock movement if there's a difference
            if adjustment_qty != 0:
                movement_type = "adjustment_in" if adjustment_qty > 0 else "adjustment_out"
                self.add_stock_movement(
                    db=db,
                    item_id=item_id,
                    location_id=location_id,
                    movement_type=movement_type,
                    quantity=abs(adjustment_qty),
                    unit_cost=unit_cost if unit_cost > 0 else None,
                    reference_type="adjustment",
                    reference_id=adjustment.id,
                    reference_number=adjustment_number,
                    remarks=f"Stock adjustment: {reason}"
                )
            
            total_adjustment_value += adj_item.adjustment_value or Decimal('0')
        
        # Update adjustment totals
        adjustment.total_items = len(adjustments)
        adjustment.total_adjustment_value = total_adjustment_value
        
        if approved_by:
            adjustment.approved_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Stock adjustment completed: {adjustment_number}")
        
        return adjustment
    
    def reserve_stock(self, db: Session, item_id: int, quantity: Decimal, location_id: Optional[int] = None):
        """Reserve stock for pending orders"""
        
        if location_id is None:
            location = self.get_main_location(db)
            location_id = location.id
        
        stock_item = db.query(StockItem).filter(
            and_(StockItem.item_id == item_id, StockItem.location_id == location_id)
        ).first()
        
        if not stock_item:
            raise ValueError("Stock record not found for item")
        
        if stock_item.available_quantity < quantity:
            raise ValueError(f"Insufficient available stock. Available: {stock_item.available_quantity}")
        
        stock_item.reserved_quantity += quantity
        stock_item.update_available_quantity()
        
        db.commit()
        
        logger.info(f"Reserved {quantity} units for item {item_id}")
    
    def release_reserved_stock(self, db: Session, item_id: int, quantity: Decimal, location_id: Optional[int] = None):
        """Release reserved stock"""
        
        if location_id is None:
            location = self.get_main_location(db)
            location_id = location.id
        
        stock_item = db.query(StockItem).filter(
            and_(StockItem.item_id == item_id, StockItem.location_id == location_id)
        ).first()
        
        if stock_item:
            stock_item.reserved_quantity = max(Decimal('0'), stock_item.reserved_quantity - quantity)
            stock_item.update_available_quantity()
            db.commit()
            
            logger.info(f"Released {quantity} reserved units for item {item_id}")
    
    def get_stock_movements(
        self, 
        db: Session, 
        item_id: Optional[int] = None,
        location_id: Optional[int] = None,
        movement_type: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100
    ) -> List[StockMovement]:
        """Get stock movements with filters"""
        
        query = db.query(StockMovement)
        
        if item_id:
            query = query.filter(StockMovement.item_id == item_id)
        
        if location_id:
            query = query.filter(StockMovement.location_id == location_id)
        
        if movement_type:
            query = query.filter(StockMovement.movement_type == movement_type)
        
        if date_from:
            query = query.filter(StockMovement.movement_date >= date_from)
        
        if date_to:
            query = query.filter(StockMovement.movement_date <= date_to)
        
        return query.order_by(StockMovement.movement_date.desc()).limit(limit).all()
    
    def get_low_stock_items(self, db: Session, location_id: Optional[int] = None) -> List[Dict]:
        """Get items with stock below minimum level"""
        
        if location_id is None:
            location = self.get_main_location(db)
            location_id = location.id
        
        # Query items with current stock below minimum level
        query = db.query(Item, StockItem).join(
            StockItem, and_(
                Item.id == StockItem.item_id,
                StockItem.location_id == location_id
            )
        ).filter(
            and_(
                Item.track_inventory == True,
                Item.status == 'active',
                StockItem.quantity <= Item.min_stock_level
            )
        )
        
        low_stock_items = []
        for item, stock in query.all():
            low_stock_items.append({
                'item_id': item.id,
                'barcode': item.barcode,
                'name': item.name,
                'current_stock': stock.quantity,
                'min_stock_level': item.min_stock_level,
                'shortage': item.min_stock_level - stock.quantity
            })
        
        return low_stock_items
    
    def get_stock_valuation(self, db: Session, location_id: Optional[int] = None) -> Dict:
        """Get stock valuation report"""
        
        if location_id is None:
            location = self.get_main_location(db)
            location_id = location.id
        
        # Query items with stock
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
        
        total_quantity = Decimal('0')
        total_value = Decimal('0')
        items_data = []
        
        for item, stock in query.all():
            unit_cost = stock.average_cost or item.landed_cost or item.purchase_rate or Decimal('0')
            item_value = stock.quantity * unit_cost
            
            items_data.append({
                'item_id': item.id,
                'barcode': item.barcode,
                'name': item.name,
                'quantity': stock.quantity,
                'unit_cost': unit_cost,
                'total_value': item_value
            })
            
            total_quantity += stock.quantity
            total_value += item_value
        
        return {
            'summary': {
                'total_items': len(items_data),
                'total_quantity': total_quantity,
                'total_value': total_value
            },
            'items': sorted(items_data, key=lambda x: x['total_value'], reverse=True)
        }
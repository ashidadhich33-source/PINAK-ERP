# backend/app/services/advanced_inventory_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date
import json
import logging

from ..models.inventory import (
    InventoryGroup, InventoryAttribute, InventoryVariant, 
    ItemVariantAttribute, SeasonalPlan, SeasonalItem
)
from ..models.inventory import Item
from ..models.inventory import StockItem

logger = logging.getLogger(__name__)

class AdvancedInventoryService:
    """Service class for advanced inventory management"""
    
    def __init__(self):
        pass
    
    # Inventory Groups Management
    def create_inventory_group(
        self, 
        db: Session, 
        company_id: int,
        name: str,
        description: str = None,
        parent_id: Optional[int] = None,
        group_code: str = None,
        display_order: int = 0,
        user_id: int = None
    ) -> InventoryGroup:
        """Create new inventory group"""
        
        # Generate group code if not provided
        if not group_code:
            group_code = name.lower().replace(' ', '_')
        
        # Check if group code already exists
        existing_group = db.query(InventoryGroup).filter(
            InventoryGroup.company_id == company_id,
            InventoryGroup.group_code == group_code
        ).first()
        
        if existing_group:
            raise ValueError(f"Group code {group_code} already exists")
        
        # Validate parent group if provided
        if parent_id:
            parent_group = db.query(InventoryGroup).filter(
                InventoryGroup.id == parent_id,
                InventoryGroup.company_id == company_id
            ).first()
            
            if not parent_group:
                raise ValueError("Parent group not found")
        
        # Create group
        group = InventoryGroup(
            company_id=company_id,
            name=name,
            description=description,
            parent_id=parent_id,
            group_code=group_code,
            display_order=display_order,
            created_by=user_id
        )
        
        db.add(group)
        db.commit()
        db.refresh(group)
        
        logger.info(f"Inventory group created: {name}")
        
        return group
    
    def get_inventory_group_hierarchy(
        self, 
        db: Session, 
        company_id: int
    ) -> Dict:
        """Get inventory group hierarchy"""
        
        groups = db.query(InventoryGroup).filter(
            InventoryGroup.company_id == company_id,
            InventoryGroup.is_active == True
        ).order_by(InventoryGroup.display_order, InventoryGroup.name).all()
        
        # Build hierarchy
        hierarchy = {}
        root_groups = []
        
        for group in groups:
            if group.parent_id is None:
                root_groups.append(group)
            else:
                if group.parent_id not in hierarchy:
                    hierarchy[group.parent_id] = []
                hierarchy[group.parent_id].append(group)
        
        # Build tree structure
        def build_tree(group):
            children = hierarchy.get(group.id, [])
            return {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "group_code": group.group_code,
                "display_order": group.display_order,
                "item_count": len(group.items),
                "children": [build_tree(child) for child in children]
            }
        
        tree = [build_tree(group) for group in root_groups]
        
        return {
            "hierarchy": tree,
            "total_groups": len(groups)
        }
    
    # Inventory Attributes Management
    def create_inventory_attribute(
        self, 
        db: Session, 
        company_id: int,
        name: str,
        attribute_type: str,
        description: str = None,
        is_required: bool = False,
        options: List[str] = None,
        display_order: int = 0,
        user_id: int = None
    ) -> InventoryAttribute:
        """Create new inventory attribute"""
        
        # Validate attribute type
        valid_types = ['text', 'number', 'select', 'color', 'size']
        if attribute_type not in valid_types:
            raise ValueError(f"Attribute type must be one of: {', '.join(valid_types)}")
        
        # Validate options for select type
        if attribute_type == 'select' and not options:
            raise ValueError("Select type attributes must have options")
        
        # Create attribute
        attribute = InventoryAttribute(
            company_id=company_id,
            name=name,
            attribute_type=attribute_type,
            description=description,
            is_required=is_required,
            options=json.dumps(options) if options else None,
            display_order=display_order,
            created_by=user_id
        )
        
        db.add(attribute)
        db.commit()
        db.refresh(attribute)
        
        logger.info(f"Inventory attribute created: {name}")
        
        return attribute
    
    def get_inventory_attributes(
        self, 
        db: Session, 
        company_id: int,
        attribute_type: Optional[str] = None,
        is_required: Optional[bool] = None
    ) -> List[InventoryAttribute]:
        """Get inventory attributes"""
        
        query = db.query(InventoryAttribute).filter(
            InventoryAttribute.company_id == company_id,
            InventoryAttribute.is_active == True
        )
        
        if attribute_type:
            query = query.filter(InventoryAttribute.attribute_type == attribute_type)
        
        if is_required is not None:
            query = query.filter(InventoryAttribute.is_required == is_required)
        
        attributes = query.order_by(InventoryAttribute.display_order, InventoryAttribute.name).all()
        
        return attributes
    
    # Inventory Variants Management
    def create_inventory_variant(
        self, 
        db: Session, 
        company_id: int,
        item_id: int,
        variant_name: str,
        variant_code: str = None,
        barcode: str = None,
        sku: str = None,
        cost_price: Decimal = None,
        selling_price: Decimal = None,
        mrp: Decimal = None,
        current_stock: Decimal = 0,
        minimum_stock: Decimal = 0,
        maximum_stock: Decimal = None,
        is_default: bool = False,
        user_id: int = None
    ) -> InventoryVariant:
        """Create new inventory variant"""
        
        # Validate item
        item = db.query(Item).filter(
            Item.id == item_id,
            Item.company_id == company_id
        ).first()
        
        if not item:
            raise ValueError("Item not found")
        
        # Check if variant code already exists
        if variant_code:
            existing_variant = db.query(InventoryVariant).filter(
                InventoryVariant.company_id == company_id,
                InventoryVariant.variant_code == variant_code
            ).first()
            
            if existing_variant:
                raise ValueError(f"Variant code {variant_code} already exists")
        
        # Create variant
        variant = InventoryVariant(
            company_id=company_id,
            item_id=item_id,
            variant_name=variant_name,
            variant_code=variant_code,
            barcode=barcode,
            sku=sku,
            cost_price=cost_price,
            selling_price=selling_price,
            mrp=mrp,
            current_stock=current_stock,
            minimum_stock=minimum_stock,
            maximum_stock=maximum_stock,
            is_default=is_default,
            created_by=user_id
        )
        
        db.add(variant)
        db.commit()
        db.refresh(variant)
        
        logger.info(f"Inventory variant created: {variant_name}")
        
        return variant
    
    def get_item_variants(
        self, 
        db: Session, 
        company_id: int,
        item_id: int
    ) -> List[InventoryVariant]:
        """Get variants for an item"""
        
        variants = db.query(InventoryVariant).filter(
            InventoryVariant.company_id == company_id,
            InventoryVariant.item_id == item_id,
            InventoryVariant.is_active == True
        ).order_by(InventoryVariant.variant_name).all()
        
        return variants
    
    def update_variant_attributes(
        self, 
        db: Session, 
        company_id: int,
        variant_id: int,
        attributes: List[Dict],
        user_id: int = None
    ) -> List[ItemVariantAttribute]:
        """Update variant attributes"""
        
        # Validate variant
        variant = db.query(InventoryVariant).filter(
            InventoryVariant.id == variant_id,
            InventoryVariant.company_id == company_id
        ).first()
        
        if not variant:
            raise ValueError("Variant not found")
        
        # Clear existing attributes
        db.query(ItemVariantAttribute).filter(
            ItemVariantAttribute.variant_id == variant_id
        ).delete()
        
        # Create new attributes
        variant_attributes = []
        
        for attr_data in attributes:
            attribute_id = attr_data.get('attribute_id')
            attribute_value = attr_data.get('attribute_value')
            
            # Validate attribute
            attribute = db.query(InventoryAttribute).filter(
                InventoryAttribute.id == attribute_id,
                InventoryAttribute.company_id == company_id
            ).first()
            
            if not attribute:
                continue
            
            variant_attr = ItemVariantAttribute(
                company_id=company_id,
                variant_id=variant_id,
                attribute_id=attribute_id,
                attribute_value=attribute_value,
                created_by=user_id
            )
            
            db.add(variant_attr)
            variant_attributes.append(variant_attr)
        
        db.commit()
        
        logger.info(f"Updated {len(variant_attributes)} variant attributes")
        
        return variant_attributes
    
    # Seasonal Planning Management
    def create_seasonal_plan(
        self, 
        db: Session, 
        company_id: int,
        name: str,
        description: str = None,
        season_start_date: datetime = None,
        season_end_date: datetime = None,
        target_sales: Decimal = None,
        target_margin: Decimal = None,
        planned_inventory_turnover: Decimal = None,
        user_id: int = None
    ) -> SeasonalPlan:
        """Create new seasonal plan"""
        
        # Create seasonal plan
        plan = SeasonalPlan(
            company_id=company_id,
            name=name,
            description=description,
            season_start_date=season_start_date,
            season_end_date=season_end_date,
            target_sales=target_sales,
            target_margin=target_margin,
            planned_inventory_turnover=planned_inventory_turnover,
            created_by=user_id
        )
        
        db.add(plan)
        db.commit()
        db.refresh(plan)
        
        logger.info(f"Seasonal plan created: {name}")
        
        return plan
    
    def add_item_to_seasonal_plan(
        self, 
        db: Session, 
        company_id: int,
        seasonal_plan_id: int,
        item_id: int,
        variant_id: Optional[int] = None,
        planned_quantity: Decimal = 0,
        planned_sales: Decimal = None,
        planned_margin: Decimal = None,
        priority: int = 1,
        user_id: int = None
    ) -> SeasonalItem:
        """Add item to seasonal plan"""
        
        # Validate seasonal plan
        plan = db.query(SeasonalPlan).filter(
            SeasonalPlan.id == seasonal_plan_id,
            SeasonalPlan.company_id == company_id
        ).first()
        
        if not plan:
            raise ValueError("Seasonal plan not found")
        
        # Validate item
        item = db.query(Item).filter(
            Item.id == item_id,
            Item.company_id == company_id
        ).first()
        
        if not item:
            raise ValueError("Item not found")
        
        # Validate variant if provided
        if variant_id:
            variant = db.query(InventoryVariant).filter(
                InventoryVariant.id == variant_id,
                InventoryVariant.company_id == company_id
            ).first()
            
            if not variant:
                raise ValueError("Variant not found")
        
        # Create seasonal item
        seasonal_item = SeasonalItem(
            company_id=company_id,
            seasonal_plan_id=seasonal_plan_id,
            item_id=item_id,
            variant_id=variant_id,
            planned_quantity=planned_quantity,
            planned_sales=planned_sales,
            planned_margin=planned_margin,
            priority=priority,
            created_by=user_id
        )
        
        db.add(seasonal_item)
        db.commit()
        db.refresh(seasonal_item)
        
        logger.info(f"Item added to seasonal plan: {item.name}")
        
        return seasonal_item
    
    def get_seasonal_plan_analysis(
        self, 
        db: Session, 
        company_id: int,
        seasonal_plan_id: int
    ) -> Dict:
        """Get seasonal plan analysis"""
        
        plan = db.query(SeasonalPlan).filter(
            SeasonalPlan.id == seasonal_plan_id,
            SeasonalPlan.company_id == company_id
        ).first()
        
        if not plan:
            raise ValueError("Seasonal plan not found")
        
        # Get seasonal items
        seasonal_items = db.query(SeasonalItem).filter(
            SeasonalItem.seasonal_plan_id == seasonal_plan_id,
            SeasonalItem.company_id == company_id
        ).all()
        
        # Calculate totals
        total_planned_quantity = sum(item.planned_quantity for item in seasonal_items)
        total_planned_sales = sum(item.planned_sales or Decimal('0') for item in seasonal_items)
        total_actual_quantity = sum(item.actual_quantity for item in seasonal_items)
        total_actual_sales = sum(item.actual_sales for item in seasonal_items)
        
        # Calculate performance metrics
        quantity_performance = (total_actual_quantity / total_planned_quantity * 100) if total_planned_quantity > 0 else 0
        sales_performance = (total_actual_sales / total_planned_sales * 100) if total_planned_sales > 0 else 0
        
        return {
            "seasonal_plan": {
                "id": plan.id,
                "name": plan.name,
                "start_date": plan.season_start_date,
                "end_date": plan.season_end_date,
                "target_sales": plan.target_sales,
                "target_margin": plan.target_margin
            },
            "summary": {
                "total_items": len(seasonal_items),
                "total_planned_quantity": total_planned_quantity,
                "total_planned_sales": total_planned_sales,
                "total_actual_quantity": total_actual_quantity,
                "total_actual_sales": total_actual_sales,
                "quantity_performance": quantity_performance,
                "sales_performance": sales_performance
            },
            "items": [
                {
                    "id": item.id,
                    "item_name": item.item.name,
                    "variant_name": item.variant.variant_name if item.variant else None,
                    "planned_quantity": item.planned_quantity,
                    "actual_quantity": item.actual_quantity,
                    "planned_sales": item.planned_sales,
                    "actual_sales": item.actual_sales,
                    "priority": item.priority,
                    "performance": (item.actual_quantity / item.planned_quantity * 100) if item.planned_quantity > 0 else 0
                }
                for item in seasonal_items
            ]
        }
    
    def get_inventory_analytics(
        self, 
        db: Session, 
        company_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict:
        """Get inventory analytics"""
        
        # Get inventory groups
        groups = db.query(InventoryGroup).filter(
            InventoryGroup.company_id == company_id,
            InventoryGroup.is_active == True
        ).all()
        
        # Get items with variants
        items_with_variants = db.query(Item).filter(
            Item.company_id == company_id,
            Item.is_active == True
        ).all()
        
        # Calculate analytics
        total_groups = len(groups)
        total_items = len(items_with_variants)
        total_variants = sum(len(item.variants) for item in items_with_variants)
        
        # Get stock levels
        stock_items = db.query(StockItem).join(
            Item, StockItem.item_id == Item.id
        ).filter(
            Item.company_id == company_id
        ).all()
        
        total_stock_value = sum(stock.quantity * stock.average_cost for stock in stock_items)
        low_stock_items = sum(1 for stock in stock_items if stock.quantity <= stock.minimum_stock)
        
        return {
            "inventory_overview": {
                "total_groups": total_groups,
                "total_items": total_items,
                "total_variants": total_variants,
                "total_stock_value": total_stock_value,
                "low_stock_items": low_stock_items
            },
            "groups_breakdown": [
                {
                    "group_name": group.name,
                    "item_count": len(group.items),
                    "total_stock": sum(stock.quantity for stock in group.items),
                    "total_value": sum(stock.quantity * stock.average_cost for stock in group.items)
                }
                for group in groups
            ],
            "performance_metrics": {
                "inventory_turnover": 0,  # This would require sales data
                "stock_accuracy": 0,  # This would require cycle counting
                "fill_rate": 0  # This would require order fulfillment data
            }
        }
    
    def get_inventory_recommendations(
        self, 
        db: Session, 
        company_id: int
    ) -> List[Dict]:
        """Get inventory recommendations"""
        
        recommendations = []
        
        # Check for low stock items
        low_stock_items = db.query(StockItem).join(
            Item, StockItem.item_id == Item.id
        ).filter(
            Item.company_id == company_id,
            StockItem.quantity <= StockItem.minimum_stock
        ).all()
        
        if low_stock_items:
            recommendations.append({
                "type": "low_stock",
                "priority": "high",
                "message": f"{len(low_stock_items)} items are below minimum stock level",
                "action": "Review and reorder low stock items"
            })
        
        # Check for overstock items
        overstock_items = db.query(StockItem).join(
            Item, StockItem.item_id == Item.id
        ).filter(
            Item.company_id == company_id,
            StockItem.quantity > StockItem.maximum_stock
        ).all()
        
        if overstock_items:
            recommendations.append({
                "type": "overstock",
                "priority": "medium",
                "message": f"{len(overstock_items)} items are over maximum stock level",
                "action": "Consider reducing stock levels or running promotions"
            })
        
        # Check for items without variants
        items_without_variants = db.query(Item).filter(
            Item.company_id == company_id,
            Item.is_active == True,
            ~Item.variants.any()
        ).all()
        
        if items_without_variants:
            recommendations.append({
                "type": "no_variants",
                "priority": "low",
                "message": f"{len(items_without_variants)} items don't have variants",
                "action": "Consider creating variants for better inventory management"
            })
        
        return recommendations

# Global service instance
advanced_inventory_service = AdvancedInventoryService()
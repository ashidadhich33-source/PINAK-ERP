# backend/app/schemas/enhanced_validation.py
from pydantic import BaseModel, validator, root_validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, date
import re

class EnhancedValidationMixin:
    """Mixin class for enhanced validation functionality"""
    
    @classmethod
    def validate_phone_number(cls, v):
        """Validate Indian phone number format"""
        if v:
            # Remove all non-digit characters
            phone = re.sub(r'\D', '', v)
            # Check if it's a valid Indian mobile number
            if len(phone) == 10 and phone.startswith(('6', '7', '8', '9')):
                return phone
            elif len(phone) == 12 and phone.startswith('91'):
                return phone[2:]  # Remove country code
            else:
                raise ValueError('Invalid Indian phone number format')
        return v
    
    @classmethod
    def validate_email(cls, v):
        """Validate email format"""
        if v:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v):
                raise ValueError('Invalid email format')
        return v
    
    @classmethod
    def validate_gst_number(cls, v):
        """Validate GST number format"""
        if v:
            gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
            if not re.match(gst_pattern, v):
                raise ValueError('Invalid GST number format')
        return v
    
    @classmethod
    def validate_pan_number(cls, v):
        """Validate PAN number format"""
        if v:
            pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
            if not re.match(pan_pattern, v):
                raise ValueError('Invalid PAN number format')
        return v

class EnhancedSaleChallanValidation(BaseModel, EnhancedValidationMixin):
    """Enhanced validation for sale challan with comprehensive business rules"""
    
    challan_number: str
    challan_date: date
    customer_id: int
    staff_id: Optional[int] = None
    challan_type: str = 'delivery'
    delivery_address: Optional[str] = None
    delivery_date: Optional[date] = None
    delivery_time: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None
    items: List[dict]
    
    @validator('challan_number')
    def validate_challan_number(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Challan number must be at least 3 characters')
        if not v.isalnum():
            raise ValueError('Challan number must contain only alphanumeric characters')
        return v.upper()
    
    @validator('challan_date')
    def validate_challan_date(cls, v):
        if v > date.today():
            raise ValueError('Challan date cannot be in the future')
        if v < date.today() - timedelta(days=365):
            raise ValueError('Challan date cannot be more than 1 year old')
        return v
    
    @validator('delivery_date')
    def validate_delivery_date(cls, v, values):
        if v and 'challan_date' in values:
            if v < values['challan_date']:
                raise ValueError('Delivery date cannot be before challan date')
            if (v - values['challan_date']).days > 30:
                raise ValueError('Delivery date cannot be more than 30 days after challan date')
        return v
    
    @validator('delivery_time')
    def validate_delivery_time(cls, v):
        if v:
            time_pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
            if not re.match(time_pattern, v):
                raise ValueError('Invalid time format. Use HH:MM format')
        return v
    
    @validator('contact_phone')
    def validate_contact_phone(cls, v):
        return cls.validate_phone_number(v)
    
    @validator('items')
    def validate_items(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one item is required')
        
        for item in v:
            if 'item_id' not in item:
                raise ValueError('Item ID is required for all items')
            if 'quantity' not in item or item['quantity'] <= 0:
                raise ValueError('Quantity must be greater than 0')
            if 'unit_price' not in item or item['unit_price'] <= 0:
                raise ValueError('Unit price must be greater than 0')
        
        return v
    
    @root_validator
    def validate_business_rules(cls, values):
        """Cross-field validation for business rules"""
        challan_date = values.get('challan_date')
        delivery_date = values.get('delivery_date')
        challan_type = values.get('challan_type')
        delivery_address = values.get('delivery_address')
        
        # Business rule: Delivery challans must have delivery address
        if challan_type == 'delivery' and not delivery_address:
            raise ValueError('Delivery address is required for delivery challans')
        
        # Business rule: Delivery date must be provided for delivery challans
        if challan_type == 'delivery' and not delivery_date:
            raise ValueError('Delivery date is required for delivery challans')
        
        return values

class EnhancedCustomerValidation(BaseModel, EnhancedValidationMixin):
    """Enhanced validation for customer data"""
    
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Customer name must be at least 2 characters')
        if len(v) > 100:
            raise ValueError('Customer name cannot exceed 100 characters')
        return v.strip()
    
    @validator('email')
    def validate_email(cls, v):
        return cls.validate_email(v)
    
    @validator('phone')
    def validate_phone(cls, v):
        return cls.validate_phone_number(v)
    
    @validator('gst_number')
    def validate_gst_number(cls, v):
        return cls.validate_gst_number(v)
    
    @validator('pan_number')
    def validate_pan_number(cls, v):
        return cls.validate_pan_number(v)
    
    @validator('pincode')
    def validate_pincode(cls, v):
        if v:
            if not v.isdigit() or len(v) != 6:
                raise ValueError('Pincode must be 6 digits')
        return v
    
    @validator('credit_limit')
    def validate_credit_limit(cls, v):
        if v is not None and v < 0:
            raise ValueError('Credit limit cannot be negative')
        return v
    
    @root_validator
    def validate_contact_requirements(cls, values):
        """Validate that at least one contact method is provided"""
        email = values.get('email')
        phone = values.get('phone')
        
        if not email and not phone:
            raise ValueError('Either email or phone number must be provided')
        
        return values

class EnhancedItemValidation(BaseModel, EnhancedValidationMixin):
    """Enhanced validation for item data"""
    
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    unit_price: Decimal
    quantity: Decimal
    min_stock_level: Optional[Decimal] = None
    max_stock_level: Optional[Decimal] = None
    hsn_code: Optional[str] = None
    gst_rate: Optional[Decimal] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Item name must be at least 2 characters')
        if len(v) > 100:
            raise ValueError('Item name cannot exceed 100 characters')
        return v.strip()
    
    @validator('unit_price')
    def validate_unit_price(cls, v):
        if v <= 0:
            raise ValueError('Unit price must be greater than 0')
        if v > Decimal('999999.99'):
            raise ValueError('Unit price cannot exceed 999,999.99')
        return v
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError('Quantity cannot be negative')
        if v > Decimal('999999.99'):
            raise ValueError('Quantity cannot exceed 999,999.99')
        return v
    
    @validator('hsn_code')
    def validate_hsn_code(cls, v):
        if v:
            if not v.isdigit() or len(v) < 4 or len(v) > 8:
                raise ValueError('HSN code must be 4-8 digits')
        return v
    
    @validator('gst_rate')
    def validate_gst_rate(cls, v):
        if v is not None:
            if v < 0 or v > 100:
                raise ValueError('GST rate must be between 0 and 100')
        return v
    
    @root_validator
    def validate_stock_levels(cls, values):
        """Validate stock level relationships"""
        min_stock = values.get('min_stock_level')
        max_stock = values.get('max_stock_level')
        quantity = values.get('quantity')
        
        if min_stock is not None and max_stock is not None:
            if min_stock > max_stock:
                raise ValueError('Minimum stock level cannot be greater than maximum stock level')
        
        if min_stock is not None and quantity is not None:
            if quantity < min_stock:
                raise ValueError('Current quantity is below minimum stock level')
        
        return values

class EnhancedPaymentValidation(BaseModel, EnhancedValidationMixin):
    """Enhanced validation for payment data"""
    
    amount: Decimal
    payment_method: str
    payment_date: date
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Payment amount must be greater than 0')
        if v > Decimal('999999.99'):
            raise ValueError('Payment amount cannot exceed 999,999.99')
        return v
    
    @validator('payment_method')
    def validate_payment_method(cls, v):
        valid_methods = ['cash', 'card', 'upi', 'netbanking', 'cheque', 'bank_transfer']
        if v.lower() not in valid_methods:
            raise ValueError(f'Payment method must be one of: {", ".join(valid_methods)}')
        return v.lower()
    
    @validator('payment_date')
    def validate_payment_date(cls, v):
        if v > date.today():
            raise ValueError('Payment date cannot be in the future')
        if v < date.today() - timedelta(days=365):
            raise ValueError('Payment date cannot be more than 1 year old')
        return v
    
    @validator('reference_number')
    def validate_reference_number(cls, v):
        if v and len(v) < 3:
            raise ValueError('Reference number must be at least 3 characters')
        return v

class EnhancedInventoryValidation(BaseModel, EnhancedValidationMixin):
    """Enhanced validation for inventory operations"""
    
    item_id: int
    quantity: Decimal
    operation_type: str  # 'in', 'out', 'adjustment'
    reason: Optional[str] = None
    reference_number: Optional[str] = None
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v
    
    @validator('operation_type')
    def validate_operation_type(cls, v):
        valid_types = ['in', 'out', 'adjustment']
        if v.lower() not in valid_types:
            raise ValueError(f'Operation type must be one of: {", ".join(valid_types)}')
        return v.lower()
    
    @validator('reason')
    def validate_reason(cls, v, values):
        operation_type = values.get('operation_type')
        if operation_type == 'adjustment' and not v:
            raise ValueError('Reason is required for inventory adjustments')
        return v

class EnhancedReportValidation(BaseModel, EnhancedValidationMixin):
    """Enhanced validation for report generation"""
    
    report_type: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    filters: Optional[Dict[str, Any]] = None
    format: str = 'json'
    
    @validator('report_type')
    def validate_report_type(cls, v):
        valid_types = ['sales', 'purchase', 'inventory', 'financial', 'customer', 'supplier']
        if v.lower() not in valid_types:
            raise ValueError(f'Report type must be one of: {", ".join(valid_types)}')
        return v.lower()
    
    @validator('format')
    def validate_format(cls, v):
        valid_formats = ['json', 'pdf', 'excel', 'csv']
        if v.lower() not in valid_formats:
            raise ValueError(f'Format must be one of: {", ".join(valid_formats)}')
        return v.lower()
    
    @root_validator
    def validate_date_range(cls, values):
        """Validate date range for reports"""
        start_date = values.get('start_date')
        end_date = values.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise ValueError('Start date cannot be after end date')
            if (end_date - start_date).days > 365:
                raise ValueError('Date range cannot exceed 1 year')
        
        return values

# Business Rule Validation Functions
class BusinessRuleValidator:
    """Class for validating business rules"""
    
    @staticmethod
    def validate_credit_limit(customer_id: int, order_amount: Decimal, db) -> bool:
        """Validate customer credit limit"""
        try:
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer or not customer.credit_limit:
                return True  # No credit limit set
            
            # Get current outstanding amount
            outstanding = db.query(func.sum(SaleInvoice.total_amount)).filter(
                SaleInvoice.customer_id == customer_id,
                SaleInvoice.payment_status == 'pending'
            ).scalar() or 0
            
            return (outstanding + order_amount) <= customer.credit_limit
        except Exception:
            return False
    
    @staticmethod
    def validate_inventory_availability(item_id: int, quantity: Decimal, db) -> bool:
        """Validate inventory availability"""
        try:
            item = db.query(Item).filter(Item.id == item_id).first()
            if not item:
                return False
            
            return item.quantity >= quantity
        except Exception:
            return False
    
    @staticmethod
    def validate_business_hours(operation_time: datetime) -> bool:
        """Validate if operation is within business hours"""
        # Business hours: 9 AM to 6 PM, Monday to Friday
        if operation_time.weekday() >= 5:  # Weekend
            return False
        
        if operation_time.hour < 9 or operation_time.hour >= 18:
            return False
        
        return True
    
    @staticmethod
    def validate_tax_calculation(amount: Decimal, tax_rate: Decimal) -> Decimal:
        """Validate and calculate tax amount"""
        if tax_rate < 0 or tax_rate > 100:
            raise ValueError('Tax rate must be between 0 and 100')
        
        return amount * (tax_rate / 100)
    
    @staticmethod
    def validate_discount_application(amount: Decimal, discount_percent: Decimal) -> Decimal:
        """Validate and calculate discount amount"""
        if discount_percent < 0 or discount_percent > 100:
            raise ValueError('Discount percentage must be between 0 and 100')
        
        return amount * (discount_percent / 100)
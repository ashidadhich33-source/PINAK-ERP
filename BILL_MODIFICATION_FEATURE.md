# Bill Modification & Deletion Feature

## Overview
This document describes the comprehensive bill modification and deletion feature implemented in the POS/ERP system. This feature allows users to modify and delete purchase and sales bills with proper usage tracking and business rule enforcement.

## Features Implemented

### 1. Usage Tracking System
- **Purchase Bills**: Tracks if items from purchase bills have been used in POS or Sales transactions
- **Sales Invoices**: Tracks invoice status (draft, confirmed, paid, cancelled)
- **Item-Level Tracking**: Each item is tracked individually to prevent modification of used items
- **Modification Lock**: Automatic locking when items are used in downstream transactions

### 2. Bill Modification Capabilities

#### Purchase Bills
- **Endpoint**: `PUT /api/v1/purchase/bills/{bill_id}`
- **Fields Modifiable**:
  - Supplier information
  - Supplier bill number and date
  - Payment mode (cash/credit)
  - Tax region (local/inter)
  - Reverse charge status
  - Bill items (add/remove/modify)
  - Tax amounts and totals

#### Sales Invoices
- **Endpoint**: `PUT /api/v1/sales/invoices/{invoice_id}`
- **Fields Modifiable**:
  - Customer information
  - Payment mode and terms
  - Notes
  - Invoice items (add/remove/modify)
  - Discount amounts
  - Tax amounts and totals

### 3. Bill Deletion Capabilities

#### Purchase Bills
- **Endpoint**: `DELETE /api/v1/purchase/bills/{bill_id}`
- **Validation**: Checks if items have been used before deletion

#### Sales Invoices
- **Endpoint**: `DELETE /api/v1/sales/invoices/{invoice_id}`
- **Validation**: Checks invoice status before deletion

### 4. Business Rules & Restrictions

#### Purchase Bill Modification/Deletion
1. **Usage Check**: Cannot modify/delete if items have been used in POS or Sales
2. **Date Restriction**: Only admins can modify bills from previous days
3. **Item Lock**: Locked items cannot be modified or deleted
4. **Automatic Tracking**: System automatically marks items as used when they appear in POS/Sales transactions

#### Sales Invoice Modification/Deletion
1. **Status Check**: Cannot modify/delete paid or cancelled invoices
2. **Date Restriction**: Only admins can modify invoices from previous days
3. **Permission Check**: Requires appropriate permissions

## Database Schema Changes

### PurchaseBill Model
```python
used_in_pos = Column(Boolean, default=False)
used_in_sales = Column(Boolean, default=False)
pos_transaction_id = Column(Integer, ForeignKey('pos_transaction.id'), nullable=True)
sale_id = Column(Integer, ForeignKey('sale.id'), nullable=True)
modification_locked = Column(Boolean, default=False)
```

### PurchaseBillItem Model
```python
used_in_pos = Column(Boolean, default=False)
used_in_sales = Column(Boolean, default=False)
pos_transaction_id = Column(Integer, ForeignKey('pos_transaction.id'), nullable=True)
sale_id = Column(Integer, ForeignKey('sale.id'), nullable=True)
modification_locked = Column(Boolean, default=False)
```

## API Endpoints

### Purchase Bill Endpoints

#### 1. Check Bill Usage
```http
GET /api/v1/purchase/bills/{bill_id}/check-usage?company_id={company_id}
```

**Response**:
```json
{
  "bill_id": 1,
  "pb_no": "PB-00001",
  "used_in_pos": true,
  "used_in_sales": false,
  "modification_locked": true,
  "can_modify": false,
  "can_delete": false,
  "items_used_in_pos": [
    {
      "barcode": "12345",
      "style_code": "ABC-001",
      "transaction_id": 10
    }
  ],
  "items_used_in_sales": []
}
```

#### 2. Check Modification Permission
```http
GET /api/v1/purchase/bills/{bill_id}/can-modify?company_id={company_id}
```

**Response**:
```json
{
  "can_modify": false,
  "reason": "Bill items have been used in POS or Sales transactions",
  "details": {
    "used_in_pos": true,
    "used_in_sales": false
  }
}
```

#### 3. Modify Purchase Bill
```http
PUT /api/v1/purchase/bills/{bill_id}?company_id={company_id}
```

**Request Body**:
```json
{
  "supplier_id": 5,
  "supplier_bill_no": "SUP-123",
  "supplier_bill_date": "2025-09-30",
  "payment_mode": "credit",
  "tax_region": "local",
  "items": [
    {
      "barcode": "12345",
      "style_code": "ABC-001",
      "qty": 10,
      "basic_rate": 100.00,
      "cgst_rate": 6.00,
      "sgst_rate": 6.00,
      "line_taxable": 1000.00,
      "cgst_amount": 60.00,
      "sgst_amount": 60.00,
      "line_total": 1120.00
    }
  ],
  "grand_total": 1120.00
}
```

**Response**:
```json
{
  "message": "Purchase bill modified successfully",
  "bill_id": 1,
  "pb_no": "PB-00001",
  "grand_total": 1120.00
}
```

#### 4. Delete Purchase Bill
```http
DELETE /api/v1/purchase/bills/{bill_id}?company_id={company_id}
```

**Response**:
```json
{
  "message": "Purchase bill deleted successfully",
  "pb_no": "PB-00001"
}
```

### Sales Invoice Endpoints

#### 1. Check Modification Permission
```http
GET /api/v1/sales/invoices/{invoice_id}/can-modify?company_id={company_id}
```

**Response**:
```json
{
  "can_modify": false,
  "reason": "Cannot modify paid invoice",
  "status": "paid"
}
```

#### 2. Modify Sales Invoice
```http
PUT /api/v1/sales/invoices/{invoice_id}?company_id={company_id}
```

**Request Body**:
```json
{
  "customer_id": 10,
  "payment_mode": "cash",
  "notes": "Updated invoice",
  "items": [
    {
      "item_id": 5,
      "barcode": "12345",
      "quantity": 2,
      "unit_price": 500.00,
      "tax_rate": 18.00,
      "tax_amount": 180.00,
      "line_total": 1180.00
    }
  ],
  "total_amount": 1180.00
}
```

**Response**:
```json
{
  "message": "Sales invoice modified successfully",
  "invoice_id": 1,
  "invoice_number": "INV-00001",
  "total_amount": 1180.00
}
```

#### 3. Delete Sales Invoice
```http
DELETE /api/v1/sales/invoices/{invoice_id}?company_id={company_id}
```

**Response**:
```json
{
  "message": "Sales invoice deleted successfully",
  "invoice_number": "INV-00001"
}
```

## Permission Requirements

### Purchase Operations
- `purchases.view` - View purchase bills and check usage
- `purchases.edit` - Modify purchase bills
- `purchases.delete` - Delete purchase bills

### Sales Operations
- `sales.view` - View sales invoices and check modification permission
- `sales.edit` - Modify sales invoices
- `sales.delete` - Delete sales invoices

### Admin Override
- Admin role can modify/delete bills from previous days
- Admin role bypasses date restrictions (but not usage restrictions)

## Error Handling

### Common Error Responses

#### 403 Forbidden
```json
{
  "detail": "Cannot modify bill: Bill items have been used in POS or Sales transactions"
}
```

#### 403 Forbidden (Date Restriction)
```json
{
  "detail": "Only admin can modify bills from previous days"
}
```

#### 403 Forbidden (Status)
```json
{
  "detail": "Cannot modify paid invoice"
}
```

#### 404 Not Found
```json
{
  "detail": "Purchase bill not found"
}
```

## Usage Examples

### Example 1: Modify a Purchase Bill
```python
import requests

# 1. Check if bill can be modified
response = requests.get(
    "http://localhost:8000/api/v1/purchase/bills/1/can-modify",
    params={"company_id": 1},
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

if response.json()["can_modify"]:
    # 2. Modify the bill
    bill_data = {
        "supplier_id": 5,
        "grand_total": 1500.00
    }
    response = requests.put(
        "http://localhost:8000/api/v1/purchase/bills/1",
        json=bill_data,
        params={"company_id": 1},
        headers={"Authorization": "Bearer YOUR_TOKEN"}
    )
    print(response.json())
```

### Example 2: Check Bill Usage
```python
import requests

response = requests.get(
    "http://localhost:8000/api/v1/purchase/bills/1/check-usage",
    params={"company_id": 1},
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

usage_info = response.json()
if usage_info["modification_locked"]:
    print(f"Bill is locked. Items used in POS: {usage_info['items_used_in_pos']}")
```

### Example 3: Delete a Sales Invoice
```python
import requests

# 1. Check if invoice can be modified (also applies to deletion)
response = requests.get(
    "http://localhost:8000/api/v1/sales/invoices/1/can-modify",
    params={"company_id": 1},
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

if response.json()["can_modify"]:
    # 2. Delete the invoice
    response = requests.delete(
        "http://localhost:8000/api/v1/sales/invoices/1",
        params={"company_id": 1},
        headers={"Authorization": "Bearer YOUR_TOKEN"}
    )
    print(response.json())
```

## Migration Steps

### 1. Database Migration
Run the following SQL to add new columns to existing tables:

```sql
-- Add columns to purchase_bill table
ALTER TABLE purchase_bill 
ADD COLUMN used_in_pos BOOLEAN DEFAULT FALSE,
ADD COLUMN used_in_sales BOOLEAN DEFAULT FALSE,
ADD COLUMN pos_transaction_id INTEGER REFERENCES pos_transaction(id),
ADD COLUMN sale_id INTEGER REFERENCES sale(id),
ADD COLUMN modification_locked BOOLEAN DEFAULT FALSE;

-- Add columns to purchase_bill_item table
ALTER TABLE purchase_bill_item 
ADD COLUMN used_in_pos BOOLEAN DEFAULT FALSE,
ADD COLUMN used_in_sales BOOLEAN DEFAULT FALSE,
ADD COLUMN pos_transaction_id INTEGER REFERENCES pos_transaction(id),
ADD COLUMN sale_id INTEGER REFERENCES sale(id),
ADD COLUMN modification_locked BOOLEAN DEFAULT FALSE;
```

### 2. Update Existing Records
Run a script to check existing bills and mark those that have been used:

```python
from app.services.core.bill_modification_service import bill_modification_service
from app.database import get_db

db = next(get_db())

# Check all purchase bills
bills = db.query(PurchaseBill).all()
for bill in bills:
    bill_modification_service.check_purchase_bill_usage(db, bill.id)
```

## Testing

### Test Cases

1. **Test Modification of Unused Bill**: Should succeed
2. **Test Modification of Used Bill**: Should fail with appropriate error
3. **Test Deletion of Unused Bill**: Should succeed
4. **Test Deletion of Used Bill**: Should fail with appropriate error
5. **Test Admin Override for Date**: Should succeed for admin
6. **Test Non-Admin Date Restriction**: Should fail for non-admin users
7. **Test Modification of Paid Invoice**: Should fail
8. **Test Modification of Draft Invoice**: Should succeed

## Best Practices

1. **Always Check Before Modifying**: Use the `/can-modify` endpoint before attempting modifications
2. **Check Usage Information**: Use the `/check-usage` endpoint to get detailed usage information
3. **Handle Errors Gracefully**: Provide clear feedback to users when modifications are not allowed
4. **Admin Privileges**: Be cautious with admin override capabilities
5. **Audit Trail**: All modifications are tracked with user ID and timestamp

## Future Enhancements

1. **Partial Modification**: Allow modification of unlocked items only
2. **Approval Workflow**: Require approval for modifications of old bills
3. **Audit Log**: Detailed log of all modifications with before/after states
4. **Rollback Capability**: Ability to rollback modifications
5. **Bulk Operations**: Modify/delete multiple bills at once
6. **Export**: Export usage reports for analysis

## Support

For issues or questions, please contact the development team or refer to the main documentation.
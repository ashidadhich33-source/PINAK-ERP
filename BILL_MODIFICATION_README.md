# Bill Modification & Deletion Feature - Complete Guide

## 🎯 Overview

This feature enables users to **modify and delete purchase and sales bills** with intelligent **usage tracking** and **business rule enforcement**. The system automatically prevents modification of bills whose items have been used in downstream transactions (POS or Sales).

---

## ✨ Key Features

### 1. **Smart Usage Tracking**
- Automatically detects when bill items are used in POS or Sales
- Locks bills and items to prevent accidental modifications
- Tracks exact transactions where items were used

### 2. **Flexible Modification**
- Modify supplier/customer information
- Update bill items (add/remove/edit)
- Change amounts, taxes, and discounts
- Full audit trail of all changes

### 3. **Safe Deletion**
- Delete incorrect bills before they're used
- Automatic validation prevents data corruption
- Clear error messages when deletion is not allowed

### 4. **Role-Based Access**
- Regular users: Can modify today's bills only
- Admin users: Can modify any bill (if not used)
- Permission-based access control

---

## 🚀 Quick Start

### Step 1: Run Database Migration

```bash
# Run the migration to add tracking columns
python migration_add_usage_tracking.py

# Check for errors and verify columns were added
```

### Step 2: Update Existing Bills

```bash
# Check all existing bills and mark those that have been used
python update_existing_bills.py

# View locked bills
python update_existing_bills.py --show-locked

# View modifiable bills
python update_existing_bills.py --show-modifiable
```

### Step 3: Test the Endpoints

```bash
# Start your application
python run_app.py

# Open API docs
# http://localhost:8000/docs

# Navigate to:
# - ✏️ Purchase Bill Modification
# - ✏️ Sales Bill Modification
```

---

## 📚 API Endpoints

### Purchase Bill Operations

#### 1. Check Bill Usage
```http
GET /api/v1/purchase/bills/{bill_id}/check-usage?company_id=1
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "bill_id": 1,
  "pb_no": "PB-00001",
  "used_in_pos": true,
  "modification_locked": true,
  "can_modify": false,
  "items_used_in_pos": [
    {"barcode": "12345", "transaction_id": 10}
  ]
}
```

#### 2. Check Modification Permission
```http
GET /api/v1/purchase/bills/{bill_id}/can-modify?company_id=1
Authorization: Bearer YOUR_TOKEN
```

#### 3. Modify Purchase Bill
```http
PUT /api/v1/purchase/bills/{bill_id}?company_id=1
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "supplier_id": 5,
  "supplier_bill_no": "SUP-123",
  "items": [
    {
      "barcode": "12345",
      "style_code": "ABC-001",
      "qty": 10,
      "basic_rate": 100.00,
      "line_total": 1120.00
    }
  ],
  "grand_total": 1120.00
}
```

#### 4. Delete Purchase Bill
```http
DELETE /api/v1/purchase/bills/{bill_id}?company_id=1
Authorization: Bearer YOUR_TOKEN
```

### Sales Invoice Operations

#### 1. Check Modification Permission
```http
GET /api/v1/sales/invoices/{invoice_id}/can-modify?company_id=1
Authorization: Bearer YOUR_TOKEN
```

#### 2. Modify Sales Invoice
```http
PUT /api/v1/sales/invoices/{invoice_id}?company_id=1
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "customer_id": 10,
  "items": [
    {
      "barcode": "12345",
      "quantity": 2,
      "unit_price": 500.00,
      "line_total": 1180.00
    }
  ],
  "total_amount": 1180.00
}
```

#### 3. Delete Sales Invoice
```http
DELETE /api/v1/sales/invoices/{invoice_id}?company_id=1
Authorization: Bearer YOUR_TOKEN
```

---

## 🔒 Business Rules

### Purchase Bills

| Rule | Description | Can Modify? |
|------|-------------|-------------|
| **Items Used in POS** | Bill items sold through POS | ❌ No |
| **Items Used in Sales** | Bill items sold through Sales | ❌ No |
| **Previous Day (User)** | Bill from yesterday, regular user | ❌ No |
| **Previous Day (Admin)** | Bill from yesterday, admin user | ✅ Yes (if not used) |
| **Today's Bill** | Bill created today, not used | ✅ Yes |

### Sales Invoices

| Rule | Description | Can Modify? |
|------|-------------|-------------|
| **Paid Invoice** | Invoice marked as paid | ❌ No |
| **Cancelled Invoice** | Invoice cancelled | ❌ No |
| **Previous Day (User)** | Invoice from yesterday, regular user | ❌ No |
| **Previous Day (Admin)** | Invoice from yesterday, admin user | ✅ Yes |
| **Draft/Confirmed** | Invoice in draft or confirmed status | ✅ Yes |

---

## 👥 Permissions Required

### Purchase Operations
- `purchases.view` - View bills and check usage
- `purchases.edit` - Modify bills
- `purchases.delete` - Delete bills

### Sales Operations
- `sales.view` - View invoices
- `sales.edit` - Modify invoices
- `sales.delete` - Delete invoices

---

## 💡 Usage Examples

### Example 1: Correct a Mistake in Purchase Bill

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your_auth_token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# 1. Check if bill can be modified
bill_id = 1
response = requests.get(
    f"{BASE_URL}/purchase/bills/{bill_id}/can-modify",
    params={"company_id": 1},
    headers=headers
)

if response.json()["can_modify"]:
    # 2. Modify the bill
    bill_data = {
        "supplier_id": 5,  # Correct supplier
        "grand_total": 1500.00  # Correct total
    }
    response = requests.put(
        f"{BASE_URL}/purchase/bills/{bill_id}",
        json=bill_data,
        params={"company_id": 1},
        headers=headers
    )
    print("✅ Bill modified:", response.json())
else:
    print("❌ Cannot modify:", response.json()["reason"])
```

### Example 2: Delete Incorrect Bill

```python
# Check usage first
response = requests.get(
    f"{BASE_URL}/purchase/bills/{bill_id}/check-usage",
    params={"company_id": 1},
    headers=headers
)

usage_info = response.json()
if not usage_info["modification_locked"]:
    # Delete the bill
    response = requests.delete(
        f"{BASE_URL}/purchase/bills/{bill_id}",
        params={"company_id": 1},
        headers=headers
    )
    print("✅ Bill deleted:", response.json())
else:
    print("❌ Bill is locked - items used in:")
    print("  POS:", usage_info["items_used_in_pos"])
    print("  Sales:", usage_info["items_used_in_sales"])
```

### Example 3: Modify Sales Invoice

```python
# Check if invoice can be modified
invoice_id = 1
response = requests.get(
    f"{BASE_URL}/sales/invoices/{invoice_id}/can-modify",
    params={"company_id": 1},
    headers=headers
)

if response.json()["can_modify"]:
    # Modify the invoice
    invoice_data = {
        "customer_id": 10,
        "notes": "Updated invoice"
    }
    response = requests.put(
        f"{BASE_URL}/sales/invoices/{invoice_id}",
        json=invoice_data,
        params={"company_id": 1},
        headers=headers
    )
    print("✅ Invoice modified:", response.json())
```

---

## 🐛 Common Errors & Solutions

### Error: "Bill items have been used in POS or Sales transactions"
**Cause:** Items from this bill have already been sold  
**Solution:** Cannot modify. Create a purchase return instead.

### Error: "Only admin can modify bills from previous days"
**Cause:** Regular user trying to modify old bill  
**Solution:** Ask admin to make the change, or use today's date restriction.

### Error: "Cannot modify paid invoice"
**Cause:** Trying to modify an invoice that's been paid  
**Solution:** Create a credit note instead of modifying.

### Error: "Purchase bill not found"
**Cause:** Invalid bill ID  
**Solution:** Check bill ID and ensure it exists.

---

## 📊 Monitoring & Reports

### View Locked Bills
```bash
python update_existing_bills.py --show-locked
```

### View Modifiable Bills
```bash
python update_existing_bills.py --show-modifiable
```

### Check Specific Bill
```bash
curl -X GET "http://localhost:8000/api/v1/purchase/bills/1/check-usage?company_id=1" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔧 Troubleshooting

### Issue: Migration fails
**Solution:**
```bash
# Check database connection
python -c "from app.database import check_database_connection; check_database_connection()"

# Rollback migration
python migration_add_usage_tracking.py --rollback

# Try again
python migration_add_usage_tracking.py
```

### Issue: Columns already exist
**Solution:** This is normal if migration was run before. The script uses `ADD COLUMN IF NOT EXISTS`.

### Issue: Permission denied
**Solution:** Check user permissions:
```python
# In Python shell
from app.database import get_db
from app.models.core.user import User

db = next(get_db())
user = db.query(User).filter(User.username == "your_username").first()
print(user.permissions)
```

---

## 📝 Best Practices

1. **Always Check First**: Use `/can-modify` before attempting modifications
2. **Check Usage**: Use `/check-usage` to understand why a bill is locked
3. **Admin Privileges**: Be careful with admin override - date restrictions exist for a reason
4. **Audit Trail**: Review modification logs regularly
5. **User Training**: Ensure users understand the restrictions
6. **Regular Backups**: Take backups before major modifications

---

## 🎓 Training Guide

### For Regular Users
1. Can modify today's bills only
2. Cannot modify if items are used
3. Check modification permission before attempting changes
4. Ask admin for help with old bills

### For Admin Users
1. Can modify bills from any date
2. Still cannot modify if items are used
3. Responsible for ensuring data integrity
4. Should verify reason for modification

### For Developers
1. Review `bill_modification_service.py` for business logic
2. Check endpoint security and permissions
3. Monitor audit logs
4. Keep documentation updated

---

## 📦 Files Reference

### Core Files
- `app/services/core/bill_modification_service.py` - Business logic
- `app/api/endpoints/purchase/bill_modification.py` - Purchase endpoints
- `app/api/endpoints/sales/bill_modification.py` - Sales endpoints
- `app/models/purchase/purchase.py` - Database models

### Scripts
- `migration_add_usage_tracking.py` - Database migration
- `update_existing_bills.py` - Update existing data

### Documentation
- `BILL_MODIFICATION_FEATURE.md` - Detailed documentation
- `BILL_MODIFICATION_SUMMARY.md` - Quick summary
- `BILL_MODIFICATION_README.md` - This file

---

## 🚀 Deployment Checklist

- [ ] Run database migration
- [ ] Update existing bills
- [ ] Test all endpoints
- [ ] Verify permissions
- [ ] Update frontend (if applicable)
- [ ] Train users
- [ ] Monitor for issues
- [ ] Document any custom changes

---

## 📞 Support

For issues or questions:
- Check detailed docs: `BILL_MODIFICATION_FEATURE.md`
- API documentation: `/docs` endpoint
- Test with Swagger UI: `/docs`
- Review audit logs for debugging

---

**Status**: ✅ **PRODUCTION READY**

All features implemented, tested, and documented. Ready for deployment!
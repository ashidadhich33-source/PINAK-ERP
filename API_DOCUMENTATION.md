# 🚀 **Enterprise ERP System - API Documentation**

## 📋 **Table of Contents**

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Company Management](#company-management)
4. [GST Management](#gst-management)
5. [Financial Year Management](#financial-year-management)
6. [Chart of Accounts](#chart-of-accounts)
7. [Advanced Inventory Management](#advanced-inventory-management)
8. [Enhanced Item Master](#enhanced-item-master)
9. [Enhanced Purchase Management](#enhanced-purchase-management)
10. [Enhanced Sales Management](#enhanced-sales-management)
11. [Double Entry Accounting](#double-entry-accounting)
12. [Discount Management](#discount-management)
13. [Report Studio](#report-studio)
14. [Loyalty Program](#loyalty-program)
15. [System Integration](#system-integration)
16. [Error Handling](#error-handling)
17. [Rate Limiting](#rate-limiting)

---

## 🔍 **Overview**

The Enterprise ERP System is a comprehensive business management solution built with FastAPI, SQLAlchemy, and PostgreSQL. It provides complete functionality for multi-company management, GST compliance, inventory management, sales, purchases, accounting, and more.

### **Base URL**
```
https://api.enterprise-erp.com/api/v1
```

### **Authentication**
All API endpoints require authentication using JWT tokens.

---

## 🔐 **Authentication**

### **Login**
```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### **Register**
```http
POST /auth/register
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "full_name": "New User"
}
```

---

## 🏢 **Company Management**

### **Create Company**
```http
POST /companies
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_name": "My Company",
  "company_code": "MYCOMP",
  "email": "company@example.com",
  "phone": "+1234567890",
  "address": "123 Main St",
  "city": "New York",
  "state": "NY",
  "country": "USA",
  "pincode": "10001",
  "gst_number": "12ABCDE1234F1Z5",
  "pan_number": "ABCDE1234F"
}
```

### **Get Companies**
```http
GET /companies
Authorization: Bearer <token>
```

### **Get Company by ID**
```http
GET /companies/{company_id}
Authorization: Bearer <token>
```

### **Update Company**
```http
PUT /companies/{company_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_name": "Updated Company Name",
  "email": "updated@example.com"
}
```

### **Delete Company**
```http
DELETE /companies/{company_id}
Authorization: Bearer <token>
```

---

## 🏛️ **GST Management**

### **Get GST State Codes**
```http
GET /gst/state-codes
Authorization: Bearer <token>
```

### **Get GST Slabs**
```http
GET /gst/slabs?company_id=1
Authorization: Bearer <token>
```

### **Create GST Slab**
```http
POST /gst/slabs
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "slab_name": "Standard Rate",
  "cgst_rate": 9.0,
  "sgst_rate": 9.0,
  "igst_rate": 18.0,
  "is_active": true
}
```

### **Calculate GST**
```http
POST /gst/calculate
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "amount": 1000.00,
  "gst_type": "cgst_sgst",
  "state_code": "07"
}
```

### **Generate GST Return**
```http
POST /gst/generate-return
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "from_date": "2024-01-01",
  "to_date": "2024-01-31",
  "return_type": "gstr1"
}
```

---

## 📅 **Financial Year Management**

### **Create Financial Year**
```http
POST /financial-year-management/financial-years
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "year_name": "FY 2024-25",
  "year_code": "FY2425",
  "start_date": "2024-04-01",
  "end_date": "2025-03-31",
  "notes": "Financial Year 2024-25"
}
```

### **Get Financial Years**
```http
GET /financial-year-management/financial-years?company_id=1
Authorization: Bearer <token>
```

### **Activate Financial Year**
```http
POST /financial-year-management/financial-years/{year_id}/activate
Authorization: Bearer <token>
```

### **Close Financial Year**
```http
POST /financial-year-management/financial-years/{year_id}/close
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "closing_type": "full_closing",
  "closing_notes": "Year end closing"
}
```

### **Create Opening Balance**
```http
POST /financial-year-management/opening-balances
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "financial_year_id": 1,
  "account_id": 1,
  "debit_balance": 1000.00,
  "credit_balance": 0.00,
  "balance_type": "debit"
}
```

---

## 📊 **Chart of Accounts**

### **Create Account**
```http
POST /chart-of-accounts/accounts
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "account_name": "Cash Account",
  "account_code": "CASH001",
  "account_type": "Asset",
  "parent_account_id": null,
  "is_active": true
}
```

### **Get Accounts**
```http
GET /chart-of-accounts/accounts?company_id=1
Authorization: Bearer <token>
```

### **Get Trial Balance**
```http
GET /chart-of-accounts/trial-balance?company_id=1&as_on_date=2024-01-31
Authorization: Bearer <token>
```

### **Get Balance Sheet**
```http
GET /chart-of-accounts/balance-sheet?company_id=1&as_on_date=2024-01-31
Authorization: Bearer <token>
```

### **Get Profit & Loss**
```http
GET /chart-of-accounts/profit-loss?company_id=1&from_date=2024-01-01&to_date=2024-01-31
Authorization: Bearer <token>
```

---

## 📦 **Advanced Inventory Management**

### **Create Inventory Group**
```http
POST /advanced-inventory/inventory-groups
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "group_name": "Electronics",
  "group_code": "ELEC",
  "description": "Electronic items",
  "parent_group_id": null
}
```

### **Create Inventory Attribute**
```http
POST /advanced-inventory/inventory-attributes
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "attribute_name": "Color",
  "attribute_type": "text",
  "is_required": true,
  "options": ["Red", "Blue", "Green"]
}
```

### **Create Inventory Variant**
```http
POST /advanced-inventory/inventory-variants
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "variant_name": "iPhone 15 Pro",
  "variant_code": "IPH15PRO",
  "item_id": 1,
  "attributes": {
    "color": "Blue",
    "storage": "256GB"
  }
}
```

### **Create Seasonal Plan**
```http
POST /advanced-inventory/seasonal-plans
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "plan_name": "Summer Collection 2024",
  "season": "Summer",
  "start_date": "2024-04-01",
  "end_date": "2024-06-30",
  "items": [
    {
      "item_id": 1,
      "target_quantity": 100,
      "forecast_demand": 120
    }
  ]
}
```

---

## 🛍️ **Enhanced Item Master**

### **Create HSN Code**
```http
POST /enhanced-item-master/hsn-codes
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "hsn_code": "85171200",
  "description": "Mobile phones",
  "gst_rate": 18.0,
  "is_active": true
}
```

### **Create Barcode**
```http
POST /enhanced-item-master/barcodes
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "item_id": 1,
  "barcode": "1234567890123",
  "barcode_type": "EAN13",
  "is_primary": true
}
```

### **Create Item Specification**
```http
POST /enhanced-item-master/item-specifications
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "item_id": 1,
  "specification_name": "Screen Size",
  "specification_value": "6.1 inches",
  "specification_type": "text"
}
```

### **Create Item Image**
```http
POST /enhanced-item-master/item-images
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "item_id": 1,
  "image_url": "https://example.com/image.jpg",
  "image_type": "main",
  "is_primary": true
}
```

### **Create Item Pricing**
```http
POST /enhanced-item-master/item-pricing
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "item_id": 1,
  "price_type": "selling",
  "price": 999.99,
  "currency": "USD",
  "valid_from": "2024-01-01",
  "valid_to": "2024-12-31"
}
```

---

## 🛒 **Enhanced Purchase Management**

### **Create Purchase Excel Import**
```http
POST /enhanced-purchase/purchase-excel-imports
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "import_name": "January Purchases",
  "file_path": "/uploads/purchases.xlsx",
  "supplier_id": 1,
  "import_date": "2024-01-15"
}
```

### **Create Purchase Bill Matching**
```http
POST /enhanced-purchase/purchase-bill-matchings
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "supplier_id": 1,
  "bill_number": "BILL001",
  "bill_date": "2024-01-15",
  "bill_amount": 1000.00,
  "matched_items": [
    {
      "item_id": 1,
      "quantity": 10,
      "rate": 100.00
    }
  ]
}
```

### **Create Direct Stock Inward**
```http
POST /enhanced-purchase/direct-stock-inwards
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "inward_date": "2024-01-15",
  "reference_number": "INW001",
  "items": [
    {
      "item_id": 1,
      "quantity": 50,
      "rate": 100.00,
      "location_id": 1
    }
  ]
}
```

### **Create Purchase Return**
```http
POST /enhanced-purchase/purchase-returns
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "supplier_id": 1,
  "return_date": "2024-01-15",
  "return_reason": "Defective goods",
  "items": [
    {
      "item_id": 1,
      "quantity": 5,
      "rate": 100.00
    }
  ]
}
```

---

## 💰 **Enhanced Sales Management**

### **Create Sale Challan**
```http
POST /enhanced-sales/sale-challans
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "customer_id": 1,
  "challan_date": "2024-01-15",
  "challan_number": "CHL001",
  "items": [
    {
      "item_id": 1,
      "quantity": 2,
      "rate": 500.00
    }
  ]
}
```

### **Create Bill Series**
```http
POST /enhanced-sales/bill-series
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "series_name": "Sales Invoice",
  "series_code": "SI",
  "prefix": "SI",
  "suffix": "",
  "start_number": 1,
  "current_number": 1,
  "is_active": true
}
```

### **Create Payment Mode**
```http
POST /enhanced-sales/payment-modes
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "mode_name": "Credit Card",
  "mode_code": "CC",
  "is_active": true
}
```

### **Create Staff**
```http
POST /enhanced-sales/staff
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "staff_name": "John Doe",
  "staff_code": "STF001",
  "department": "Sales",
  "position": "Sales Executive",
  "is_active": true
}
```

### **Create Sale Return**
```http
POST /enhanced-sales/sale-returns
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "customer_id": 1,
  "return_date": "2024-01-15",
  "return_reason": "Customer request",
  "items": [
    {
      "item_id": 1,
      "quantity": 1,
      "rate": 500.00
    }
  ]
}
```

### **Create POS Session**
```http
POST /enhanced-sales/pos-sessions
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "session_name": "Morning Shift",
  "staff_id": 1,
  "start_time": "2024-01-15T09:00:00",
  "opening_balance": 1000.00
}
```

---

## 📊 **Double Entry Accounting**

### **Create Journal Entry**
```http
POST /double-entry-accounting/journal-entries
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "entry_date": "2024-01-15",
  "reference": "JE001",
  "description": "Sales entry",
  "items": [
    {
      "account_id": 1,
      "debit_amount": 1000.00,
      "credit_amount": 0.00,
      "description": "Cash received"
    },
    {
      "account_id": 2,
      "debit_amount": 0.00,
      "credit_amount": 1000.00,
      "description": "Sales revenue"
    }
  ]
}
```

### **Get Trial Balance**
```http
GET /double-entry-accounting/trial-balance?company_id=1&as_on_date=2024-01-31
Authorization: Bearer <token>
```

### **Get Balance Sheet**
```http
GET /double-entry-accounting/balance-sheet?company_id=1&as_on_date=2024-01-31
Authorization: Bearer <token>
```

### **Get Profit & Loss**
```http
GET /double-entry-accounting/profit-loss?company_id=1&from_date=2024-01-01&to_date=2024-01-31
Authorization: Bearer <token>
```

### **Get Cash Flow Statement**
```http
GET /double-entry-accounting/cash-flow?company_id=1&from_date=2024-01-01&to_date=2024-01-31
Authorization: Bearer <token>
```

---

## 💰 **Discount Management**

### **Create Discount Type**
```http
POST /discount-management/discount-types
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "type_name": "Percentage Discount",
  "type_code": "PERC",
  "calculation_method": "percentage",
  "description": "Percentage based discount"
}
```

### **Create Discount Rule**
```http
POST /discount-management/discount-rules
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "rule_name": "Bulk Purchase Discount",
  "rule_code": "BULK",
  "discount_type_id": 1,
  "rule_type": "quantity",
  "condition_type": "quantity",
  "condition_value": 10,
  "condition_operator": ">=",
  "discount_value": 5.00,
  "discount_percentage": 5.0
}
```

### **Create Discount Coupon**
```http
POST /discount-management/discount-coupons
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "coupon_code": "SAVE10",
  "coupon_name": "10% Off Coupon",
  "discount_type_id": 1,
  "discount_percentage": 10.0,
  "max_usage_count": 100,
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

### **Apply Discount Rule**
```http
POST /discount-management/discount-rules/{rule_id}/apply
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "transaction_type": "sale",
  "transaction_id": 1,
  "item_id": 1,
  "customer_id": 1,
  "original_amount": 1000.00,
  "quantity": 15
}
```

---

## 📊 **Report Studio**

### **Create Report Category**
```http
POST /report-studio/report-categories
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "category_name": "Sales Reports",
  "category_code": "SALES",
  "description": "Sales related reports"
}
```

### **Create Report Template**
```http
POST /report-studio/report-templates
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "template_name": "Sales Summary",
  "template_code": "SALES_SUMMARY",
  "category_id": 1,
  "report_type": "table",
  "data_source": "sales",
  "query_sql": "SELECT * FROM sale_bill WHERE company_id = :company_id"
}
```

### **Create Report Instance**
```http
POST /report-studio/report-instances
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "template_id": 1,
  "instance_name": "January Sales Report",
  "parameters": {
    "from_date": "2024-01-01",
    "to_date": "2024-01-31"
  }
}
```

### **Generate Report Instance**
```http
POST /report-studio/report-instances/{instance_id}/generate
Authorization: Bearer <token>
```

### **Export Report Instance**
```http
POST /report-studio/report-instances/{instance_id}/export
Authorization: Bearer <token>
Content-Type: application/json

{
  "export_format": "pdf",
  "export_config": {
    "include_charts": true,
    "page_size": "A4"
  }
}
```

---

## 🎁 **Loyalty Program**

### **Create Loyalty Program**
```http
POST /loyalty-program/loyalty-programs
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "program_name": "VIP Customer Program",
  "program_code": "VIP",
  "program_type": "points",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "auto_enrollment": true
}
```

### **Create Loyalty Tier**
```http
POST /loyalty-program/loyalty-tiers
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "loyalty_program_id": 1,
  "tier_name": "Gold",
  "tier_code": "GOLD",
  "tier_level": 2,
  "min_points": 1000,
  "max_points": 5000,
  "tier_multiplier": 1.5
}
```

### **Create Loyalty Point**
```http
POST /loyalty-program/loyalty-points
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "loyalty_program_id": 1,
  "point_name": "Purchase Points",
  "point_code": "PURCHASE",
  "point_value": 1.0,
  "point_type": "earn",
  "point_category": "purchase"
}
```

### **Earn Loyalty Points**
```http
POST /loyalty-program/loyalty-points/earn
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "customer_id": 1,
  "loyalty_program_id": 1,
  "loyalty_point_id": 1,
  "points_amount": 100,
  "transaction_reference": "SALE001"
}
```

### **Create Loyalty Reward**
```http
POST /loyalty-program/loyalty-rewards
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "loyalty_program_id": 1,
  "reward_name": "Free Shipping",
  "reward_code": "FREESHIP",
  "reward_type": "discount",
  "reward_value": 0.00,
  "points_required": 500,
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

### **Redeem Loyalty Points**
```http
POST /loyalty-program/loyalty-rewards/redeem
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "customer_id": 1,
  "loyalty_program_id": 1,
  "loyalty_reward_id": 1,
  "points_amount": 500,
  "transaction_reference": "REDEEM001"
}
```

---

## 🔧 **System Integration**

### **System Health Check**
```http
GET /system-integration/health-check?company_id=1
Authorization: Bearer <token>
```

### **Optimize System**
```http
POST /system-integration/optimize?company_id=1
Authorization: Bearer <token>
```

### **Enhance Security**
```http
POST /system-integration/enhance-security?company_id=1
Authorization: Bearer <token>
```

### **System Testing**
```http
POST /system-integration/test?company_id=1
Authorization: Bearer <token>
```

### **Get System Status**
```http
GET /system-integration/status?company_id=1
Authorization: Bearer <token>
```

### **Get System Metrics**
```http
GET /system-integration/metrics?company_id=1
Authorization: Bearer <token>
```

### **Create System Backup**
```http
POST /system-integration/backup?company_id=1
Authorization: Bearer <token>
Content-Type: application/json

{
  "backup_type": "full"
}
```

### **System Maintenance**
```http
POST /system-integration/maintenance?company_id=1
Authorization: Bearer <token>
Content-Type: application/json

{
  "maintenance_type": "routine"
}
```

---

## ❌ **Error Handling**

### **Error Response Format**
```json
{
  "detail": "Error message",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### **Common Error Codes**
- `VALIDATION_ERROR`: Input validation failed
- `AUTHENTICATION_ERROR`: Authentication failed
- `AUTHORIZATION_ERROR`: Access denied
- `NOT_FOUND`: Resource not found
- `CONFLICT`: Resource conflict
- `INTERNAL_ERROR`: Internal server error

### **HTTP Status Codes**
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `409`: Conflict
- `422`: Validation Error
- `500`: Internal Server Error

---

## ⚡ **Rate Limiting**

### **Rate Limits**
- **Authentication**: 5 requests per minute
- **General API**: 100 requests per minute
- **Bulk Operations**: 10 requests per minute
- **Reports**: 20 requests per minute

### **Rate Limit Headers**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

---

## 📝 **Notes**

1. **Authentication**: All endpoints require valid JWT tokens
2. **Company ID**: Most endpoints require a company_id parameter
3. **Pagination**: List endpoints support pagination with `page` and `limit` parameters
4. **Filtering**: Most endpoints support filtering with query parameters
5. **Sorting**: List endpoints support sorting with `sort_by` and `sort_order` parameters
6. **Date Formats**: All dates should be in ISO 8601 format (YYYY-MM-DD)
7. **Time Formats**: All times should be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)

---

## 🔗 **Related Documentation**

- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [User Guide](USER_GUIDE.md)
- [Developer Guide](DEVELOPER_GUIDE.md)
- [Database Schema](DATABASE_SCHEMA.md)
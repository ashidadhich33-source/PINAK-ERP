# PINAK-ERP - Frontend Development Master Plan

**Generated**: December 19, 2024
**Backend Framework**: Python Flask/FastAPI
**Frontend Stack**: React + Node.js + Tailwind CSS (JavaScript - NO TypeScript)
**Backend Location**: PINAK-ERP/app/

---

## 📋 TABLE OF CONTENTS
1. [API Endpoints Inventory](#api-endpoints-inventory)
2. [Data Models & Structures](#data-models--structures)
3. [Authentication & Security](#authentication--security)
4. [Development Phases](#development-phases)
5. [Module Implementation Checklist](#module-implementation-checklist)
6. [Component Standards](#component-standards)
7. [Progress Tracking](#progress-tracking)

---

## 🔗 API ENDPOINTS INVENTORY

> **⚠️ CRITICAL**: Found **766 API endpoints** across **69 files** - Complete documentation below

### **CORE MODULE ENDPOINTS**

#### **Authentication & User Management**
- **POST** `/api/auth/login` - User login with JWT token
- **POST** `/api/auth/login-form` - OAuth2 compatible login
- **GET** `/api/auth/me` - Get current user info
- **POST** `/api/auth/change-password` - Change user password
- **POST** `/api/auth/logout` - Logout user
- **POST** `/api/auth/users` - Create new user (admin only)
- **GET** `/api/auth/users` - List all users (admin only)
- **GET** `/api/auth/users/{user_id}` - Get user by ID
- **PUT** `/api/auth/users/{user_id}/toggle-status` - Activate/deactivate user
- **GET** `/api/auth/roles` - Get all available roles

#### **Company Management**
- **POST** `/api/companies/` - Create new company
- **GET** `/api/companies/` - List companies (with filters)
- **GET** `/api/companies/{company_id}` - Get company details
- **PUT** `/api/companies/{company_id}` - Update company
- **DELETE** `/api/companies/{company_id}` - Delete company (soft delete)
- **POST** `/api/companies/{company_id}/users` - Add user to company
- **GET** `/api/companies/{company_id}/users` - List company users
- **PUT** `/api/companies/{company_id}/users/{user_id}` - Update user-company association
- **DELETE** `/api/companies/{company_id}/users/{user_id}` - Remove user from company

#### **System Settings & Configuration**
- **GET** `/api/settings/settings` - Get all system settings
- **GET** `/api/settings/settings/{section}` - Get section settings
- **POST** `/api/settings/update` - Update single setting
- **POST** `/api/settings/update-section` - Update section settings
- **POST** `/api/settings/reset/{section}` - Reset section to defaults
- **GET** `/api/settings/validate` - Validate all settings
- **POST** `/api/settings/export` - Export settings to JSON
- **POST** `/api/settings/import` - Import settings from JSON
- **GET** `/api/settings/company` - Get company settings
- **POST** `/api/settings/company` - Update company settings
- **POST** `/api/settings/company/logo` - Upload company logo
- **GET** `/api/settings/templates` - List print templates
- **GET** `/api/settings/templates/{template_type}` - Get specific template
- **POST** `/api/settings/templates` - Update print template
- **POST** `/api/settings/templates/{template_type}/reset` - Reset template
- **GET** `/api/settings/system-info` - Get system information
- **POST** `/api/settings/quick-settings/toggle-gst` - Toggle GST
- **POST** `/api/settings/quick-settings/toggle-loyalty` - Toggle loyalty
- **POST** `/api/settings/quick-settings/toggle-whatsapp` - Toggle WhatsApp
- **POST** `/api/settings/quick-settings/update-financial-year` - Update financial year
- **POST** `/api/settings/quick-settings/update-tax-rates` - Update tax rates

#### **Database & System Setup**
- **POST** `/api/setup/initialize` - Initialize system
- **GET** `/api/setup/status` - Get setup status
- **POST** `/api/setup/complete` - Complete setup
- **GET** `/api/database/status` - Get database status
- **POST** `/api/database/migrate` - Run database migrations
- **POST** `/api/database/seed` - Seed initial data

#### **Backup & Recovery**
- **POST** `/api/backup/create` - Create system backup
- **GET** `/api/backup/list` - List available backups
- **POST** `/api/backup/restore` - Restore from backup
- **DELETE** `/api/backup/{backup_id}` - Delete backup
- **GET** `/api/backup/{backup_id}/download` - Download backup

#### **Expense Management**
- **POST** `/api/expenses/` - Create expense
- **GET** `/api/expenses/` - List expenses
- **GET** `/api/expenses/{expense_id}` - Get expense details
- **PUT** `/api/expenses/{expense_id}` - Update expense
- **DELETE** `/api/expenses/{expense_id}` - Delete expense
- **GET** `/api/expenses/categories` - Get expense categories
- **POST** `/api/expenses/categories` - Create expense category
- **GET** `/api/expenses/items` - Get expense items
- **POST** `/api/expenses/items` - Create expense item

#### **Payment Management**
- **POST** `/api/payments/` - Create payment
- **GET** `/api/payments/` - List payments
- **GET** `/api/payments/{payment_id}` - Get payment details
- **PUT** `/api/payments/{payment_id}` - Update payment
- **DELETE** `/api/payments/{payment_id}` - Delete payment
- **GET** `/api/payments/methods` - Get payment methods
- **POST** `/api/payments/methods` - Create payment method
- **GET** `/api/payments/gateways` - Get payment gateways
- **POST** `/api/payments/gateways` - Create payment gateway

#### **GST Management**
- **GET** `/api/gst/slabs` - Get GST slabs
- **POST** `/api/gst/slabs` - Create GST slab
- **PUT** `/api/gst/slabs/{slab_id}` - Update GST slab
- **DELETE** `/api/gst/slabs/{slab_id}` - Delete GST slab
- **GET** `/api/gst/returns` - Get GST returns
- **POST** `/api/gst/returns` - Create GST return
- **GET** `/api/gst/compliance` - Get GST compliance status
- **POST** `/api/gst/compliance/update` - Update compliance status

#### **Discount Management**
- **GET** `/api/discounts/` - List discounts
- **POST** `/api/discounts/` - Create discount
- **GET** `/api/discounts/{discount_id}` - Get discount details
- **PUT** `/api/discounts/{discount_id}` - Update discount
- **DELETE** `/api/discounts/{discount_id}` - Delete discount
- **GET** `/api/discounts/rules` - Get discount rules
- **POST** `/api/discounts/rules` - Create discount rule
- **GET** `/api/discounts/categories` - Get discount categories
- **POST** `/api/discounts/categories` - Create discount category

#### **Automation Control**
- **GET** `/api/automation/workflows` - List automation workflows
- **POST** `/api/automation/workflows` - Create workflow
- **GET** `/api/automation/rules` - List automation rules
- **POST** `/api/automation/rules` - Create automation rule
- **GET** `/api/automation/triggers` - List automation triggers
- **POST** `/api/automation/triggers` - Create automation trigger
- **GET** `/api/automation/actions` - List automation actions
- **POST** `/api/automation/actions` - Create automation action
- **GET** `/api/automation/logs` - Get automation logs
- **POST** `/api/automation/execute` - Execute automation
- **POST** `/api/automation/approve` - Approve automation
- **POST** `/api/automation/rollback` - Rollback automation

#### **Company Management**
- **POST** `/api/companies/` - Create new company
- **GET** `/api/companies/` - List companies (with filters)
- **GET** `/api/companies/{company_id}` - Get company details
- **PUT** `/api/companies/{company_id}` - Update company
- **DELETE** `/api/companies/{company_id}` - Delete company (soft delete)
- **POST** `/api/companies/{company_id}/users` - Add user to company
- **GET** `/api/companies/{company_id}/users` - List company users
- **PUT** `/api/companies/{company_id}/users/{user_id}` - Update user-company association
- **DELETE** `/api/companies/{company_id}/users/{user_id}` - Remove user from company

#### **System Settings**
- **GET** `/api/settings/settings` - Get all system settings
- **GET** `/api/settings/settings/{section}` - Get section settings
- **POST** `/api/settings/update` - Update single setting
- **POST** `/api/settings/update-section` - Update section settings
- **POST** `/api/settings/reset/{section}` - Reset section to defaults
- **GET** `/api/settings/validate` - Validate all settings
- **POST** `/api/settings/export` - Export settings to JSON
- **POST** `/api/settings/import` - Import settings from JSON
- **GET** `/api/settings/company` - Get company settings
- **POST** `/api/settings/company` - Update company settings
- **POST** `/api/settings/company/logo` - Upload company logo
- **GET** `/api/settings/templates` - List print templates
- **GET** `/api/settings/templates/{template_type}` - Get specific template
- **POST** `/api/settings/templates` - Update print template
- **POST** `/api/settings/templates/{template_type}/reset` - Reset template
- **GET** `/api/settings/system-info` - Get system information

### **CUSTOMER MODULE ENDPOINTS**

#### **Customer Management**
- **GET** `/api/customers/` - List customers (with filters)
- **GET** `/api/customers/{customer_id}` - Get customer by ID
- **GET** `/api/customers/code/{customer_code}` - Get customer by code
- **GET** `/api/customers/mobile/{mobile}` - Get customer by mobile
- **POST** `/api/customers/` - Create new customer
- **PUT** `/api/customers/{customer_id}` - Update customer
- **DELETE** `/api/customers/{customer_id}` - Delete customer (soft delete)
- **PUT** `/api/customers/{customer_id}/toggle-status` - Activate/deactivate customer
- **PUT** `/api/customers/{customer_id}/loyalty` - Toggle loyalty membership
- **GET** `/api/customers/{customer_id}/balance-summary` - Get customer balance summary

#### **Customer Groups**
- **GET** `/api/customers/groups` - Get all customer groups
- **POST** `/api/customers/groups` - Create customer group

### **INVENTORY MODULE ENDPOINTS**

#### **Item Management**
- **GET** `/api/items/` - List items (with filters)
- **GET** `/api/items/{item_id}` - Get item by ID
- **GET** `/api/items/barcode/{barcode}` - Get item by barcode (POS scanning)
- **POST** `/api/items/` - Create new item
- **PUT** `/api/items/{item_id}` - Update item
- **DELETE** `/api/items/{item_id}` - Delete item (soft delete)
- **GET** `/api/items/categories` - Get all categories
- **POST** `/api/items/categories` - Create category
- **GET** `/api/items/brands` - Get all brands
- **POST** `/api/items/brands` - Create brand
- **POST** `/api/items/import-excel` - Import items from Excel
- **GET** `/api/items/export-excel` - Export items to Excel
- **GET** `/api/items/low-stock` - Get low stock items
- **GET** `/api/items/stock-valuation` - Get stock valuation report

### **POS MODULE ENDPOINTS**

#### **POS Sessions**
- **POST** `/api/pos/pos-sessions` - Create POS session
- **GET** `/api/pos/pos-sessions` - Get POS sessions (with filters)
- **GET** `/api/pos/pos-sessions/{session_id}` - Get specific POS session
- **POST** `/api/pos/pos-sessions/{session_id}/close` - Close POS session

#### **POS Transactions**
- **POST** `/api/pos/pos-transactions` - Create POS transaction
- **POST** `/api/pos/pos-transactions/{transaction_id}/complete` - Complete transaction
- **GET** `/api/pos/pos-transactions` - Get POS transactions (with filters)
- **GET** `/api/pos/pos-transactions/{transaction_id}` - Get specific transaction
- **POST** `/api/pos/pos-transactions/{transaction_id}/items` - Add items to transaction
- **POST** `/api/pos/pos-transactions/{transaction_id}/payments` - Add payment
- **POST** `/api/pos/pos-transactions/{transaction_id}/void` - Void transaction

#### **Store Management**
- **POST** `/api/pos/stores` - Create store
- **GET** `/api/pos/stores` - Get stores

#### **POS Receipts**
- **POST** `/api/pos/pos-transactions/{transaction_id}/receipt` - Create receipt
- **POST** `/api/pos/pos-transactions/{transaction_id}/print-receipt` - Print receipt

#### **POS Analytics**
- **GET** `/api/pos/pos-analytics/dashboard` - Get POS dashboard
- **GET** `/api/pos/pos-analytics/sales-report` - Get POS sales report

### **SALES MODULE ENDPOINTS**

#### **Sales Orders & Invoices**
- **POST** `/api/sales/sale-challans` - Create sale challan
- **GET** `/api/sales/sale-challans` - List sale challans
- **GET** `/api/sales/sale-challans/{challan_id}` - Get specific challan
- **PUT** `/api/sales/sale-challans/{challan_id}` - Update challan
- **POST** `/api/sales/sale-challans/{challan_id}/items` - Add items to challan
- **POST** `/api/sales/sale-challans/{challan_id}/convert-to-invoice` - Convert to invoice

#### **Bill Series Management**
- **POST** `/api/sales/bill-series` - Create bill series
- **GET** `/api/sales/bill-series` - List bill series
- **PUT** `/api/sales/bill-series/{series_id}` - Update bill series
- **DELETE** `/api/sales/bill-series/{series_id}` - Delete bill series

#### **Payment Modes**
- **POST** `/api/sales/payment-modes` - Create payment mode
- **GET** `/api/sales/payment-modes` - List payment modes
- **PUT** `/api/sales/payment-modes/{mode_id}` - Update payment mode

### **PURCHASE MODULE ENDPOINTS**

#### **Purchase Orders**
- **POST** `/api/purchases/orders` - Create purchase order
- **GET** `/api/purchases/orders` - List purchase orders
- **GET** `/api/purchases/orders/{order_id}` - Get specific order
- **PUT** `/api/purchases/orders/{order_id}` - Update order
- **POST** `/api/purchases/orders/{order_id}/receive` - Receive order items

#### **Purchase Invoices**
- **POST** `/api/purchases/invoices` - Create purchase invoice
- **GET** `/api/purchases/invoices` - List purchase invoices
- **GET** `/api/purchases/invoices/{invoice_id}` - Get specific invoice
- **PUT** `/api/purchases/invoices/{invoice_id}` - Update invoice

### **REPORTS MODULE ENDPOINTS**

#### **Sales Reports**
- **GET** `/api/reports/sales/summary` - Sales summary report
- **GET** `/api/reports/sales/detailed` - Detailed sales report
- **GET** `/api/reports/sales/top-customers` - Top customers report
- **GET** `/api/reports/sales/top-items` - Top selling items report

#### **Stock Reports**
- **GET** `/api/reports/stock/valuation` - Stock valuation report
- **GET** `/api/reports/stock/movements` - Stock movement report
- **GET** `/api/reports/stock/low-stock` - Low stock report

#### **Financial Reports**
- **GET** `/api/reports/financial/gst-summary` - GST summary report
- **GET** `/api/reports/financial/profit-loss` - Profit & Loss report

#### **Dashboard Reports**
- **GET** `/api/reports/dashboard/summary` - Dashboard summary

### **ACCOUNTING MODULE ENDPOINTS**

#### **Chart of Accounts**
- **POST** `/api/accounting/chart-of-accounts` - Create account
- **GET** `/api/accounting/chart-of-accounts` - List accounts
- **PUT** `/api/accounting/chart-of-accounts/{account_id}` - Update account
- **DELETE** `/api/accounting/chart-of-accounts/{account_id}` - Delete account

#### **Double Entry Accounting**
- **POST** `/api/accounting/journal-entries` - Create journal entry
- **GET** `/api/accounting/journal-entries` - List journal entries
- **GET** `/api/accounting/ledger/{account_id}` - Get account ledger

### **LOYALTY MODULE ENDPOINTS**

#### **Loyalty Programs**
- **POST** `/api/loyalty/programs` - Create loyalty program
- **GET** `/api/loyalty/programs` - List loyalty programs
- **POST** `/api/loyalty/transactions` - Create loyalty transaction
- **GET** `/api/loyalty/transactions` - List loyalty transactions
- **GET** `/api/loyalty/customers/{customer_id}/balance` - Get customer loyalty balance

### **WHATSAPP MODULE ENDPOINTS**

#### **WhatsApp Integration**
- **POST** `/api/whatsapp/setup` - Setup WhatsApp integration
- **GET** `/api/whatsapp/templates` - List message templates
- **POST** `/api/whatsapp/send-message` - Send WhatsApp message
- **POST** `/api/whatsapp/webhooks` - WhatsApp webhook handler

### **ACCOUNTING MODULE ENDPOINTS**

#### **Chart of Accounts**
- **POST** `/api/accounting/chart-of-accounts` - Create account
- **GET** `/api/accounting/chart-of-accounts` - List accounts
- **GET** `/api/accounting/chart-of-accounts/{account_id}` - Get account details
- **PUT** `/api/accounting/chart-of-accounts/{account_id}` - Update account
- **DELETE** `/api/accounting/chart-of-accounts/{account_id}` - Delete account
- **GET** `/api/accounting/chart-of-accounts/tree` - Get account hierarchy
- **POST** `/api/accounting/chart-of-accounts/import` - Import accounts
- **GET** `/api/accounting/chart-of-accounts/export` - Export accounts

#### **Double Entry Accounting**
- **POST** `/api/accounting/journal-entries` - Create journal entry
- **GET** `/api/accounting/journal-entries` - List journal entries
- **GET** `/api/accounting/journal-entries/{entry_id}` - Get journal entry
- **PUT** `/api/accounting/journal-entries/{entry_id}` - Update journal entry
- **DELETE** `/api/accounting/journal-entries/{entry_id}` - Delete journal entry
- **POST** `/api/accounting/journal-entries/{entry_id}/approve` - Approve entry
- **POST** `/api/accounting/journal-entries/{entry_id}/reverse` - Reverse entry

#### **Ledger Management**
- **GET** `/api/accounting/ledger/{account_id}` - Get account ledger
- **GET** `/api/accounting/ledger/{account_id}/balance` - Get account balance
- **GET** `/api/accounting/ledger/{account_id}/transactions` - Get account transactions
- **POST** `/api/accounting/ledger/{account_id}/opening-balance` - Set opening balance

#### **Financial Year Management**
- **POST** `/api/accounting/financial-years` - Create financial year
- **GET** `/api/accounting/financial-years` - List financial years
- **GET** `/api/accounting/financial-years/{year_id}` - Get financial year
- **PUT** `/api/accounting/financial-years/{year_id}` - Update financial year
- **POST** `/api/accounting/financial-years/{year_id}/close` - Close financial year
- **POST** `/api/accounting/financial-years/{year_id}/reopen` - Reopen financial year

#### **Banking Integration**
- **GET** `/api/accounting/banks` - List banks
- **POST** `/api/accounting/banks` - Create bank
- **GET** `/api/accounting/banks/{bank_id}` - Get bank details
- **PUT** `/api/accounting/banks/{bank_id}` - Update bank
- **GET** `/api/accounting/banks/{bank_id}/accounts` - Get bank accounts
- **POST** `/api/accounting/banks/{bank_id}/accounts` - Create bank account
- **GET** `/api/accounting/banks/{bank_id}/transactions` - Get bank transactions
- **POST** `/api/accounting/banks/{bank_id}/reconcile` - Reconcile bank account

#### **Advanced Reporting**
- **GET** `/api/accounting/reports/trial-balance` - Trial balance report
- **GET** `/api/accounting/reports/balance-sheet` - Balance sheet report
- **GET** `/api/accounting/reports/profit-loss` - Profit & Loss report
- **GET** `/api/accounting/reports/cash-flow` - Cash flow report
- **GET** `/api/accounting/reports/aged-receivables` - Aged receivables report
- **GET** `/api/accounting/reports/aged-payables` - Aged payables report

### **LOYALTY MODULE ENDPOINTS**

#### **Loyalty Programs**
- **POST** `/api/loyalty/programs` - Create loyalty program
- **GET** `/api/loyalty/programs` - List loyalty programs
- **GET** `/api/loyalty/programs/{program_id}` - Get loyalty program
- **PUT** `/api/loyalty/programs/{program_id}` - Update loyalty program
- **DELETE** `/api/loyalty/programs/{program_id}` - Delete loyalty program
- **POST** `/api/loyalty/programs/{program_id}/activate` - Activate program
- **POST** `/api/loyalty/programs/{program_id}/deactivate` - Deactivate program

#### **Loyalty Transactions**
- **POST** `/api/loyalty/transactions` - Create loyalty transaction
- **GET** `/api/loyalty/transactions` - List loyalty transactions
- **GET** `/api/loyalty/transactions/{transaction_id}` - Get loyalty transaction
- **POST** `/api/loyalty/transactions/{transaction_id}/reverse` - Reverse transaction
- **GET** `/api/loyalty/customers/{customer_id}/balance` - Get customer loyalty balance
- **GET** `/api/loyalty/customers/{customer_id}/history` - Get customer loyalty history

#### **Loyalty Rewards**
- **GET** `/api/loyalty/rewards` - List loyalty rewards
- **POST** `/api/loyalty/rewards` - Create loyalty reward
- **GET** `/api/loyalty/rewards/{reward_id}` - Get loyalty reward
- **PUT** `/api/loyalty/rewards/{reward_id}` - Update loyalty reward
- **DELETE** `/api/loyalty/rewards/{reward_id}` - Delete loyalty reward
- **POST** `/api/loyalty/rewards/{reward_id}/redeem` - Redeem reward

### **WHATSAPP MODULE ENDPOINTS**

#### **WhatsApp Setup**
- **POST** `/api/whatsapp/setup` - Setup WhatsApp integration
- **GET** `/api/whatsapp/setup/status` - Get integration status
- **PUT** `/api/whatsapp/setup` - Update integration settings
- **POST** `/api/whatsapp/setup/verify` - Verify WhatsApp connection
- **DELETE** `/api/whatsapp/setup` - Remove WhatsApp integration

#### **Message Templates**
- **GET** `/api/whatsapp/templates` - List message templates
- **POST** `/api/whatsapp/templates` - Create message template
- **GET** `/api/whatsapp/templates/{template_id}` - Get message template
- **PUT** `/api/whatsapp/templates/{template_id}` - Update message template
- **DELETE** `/api/whatsapp/templates/{template_id}` - Delete message template
- **POST** `/api/whatsapp/templates/{template_id}/approve` - Approve template
- **POST** `/api/whatsapp/templates/{template_id}/reject` - Reject template

#### **WhatsApp Messages**
- **POST** `/api/whatsapp/messages/send` - Send WhatsApp message
- **GET** `/api/whatsapp/messages` - List sent messages
- **GET** `/api/whatsapp/messages/{message_id}` - Get message details
- **POST** `/api/whatsapp/messages/{message_id}/status` - Update message status
- **GET** `/api/whatsapp/messages/delivery-reports` - Get delivery reports

#### **WhatsApp Campaigns**
- **POST** `/api/whatsapp/campaigns` - Create WhatsApp campaign
- **GET** `/api/whatsapp/campaigns` - List campaigns
- **GET** `/api/whatsapp/campaigns/{campaign_id}` - Get campaign details
- **PUT** `/api/whatsapp/campaigns/{campaign_id}` - Update campaign
- **POST** `/api/whatsapp/campaigns/{campaign_id}/start` - Start campaign
- **POST** `/api/whatsapp/campaigns/{campaign_id}/stop` - Stop campaign
- **GET** `/api/whatsapp/campaigns/{campaign_id}/analytics` - Get campaign analytics

#### **WhatsApp Webhooks**
- **POST** `/api/whatsapp/webhooks` - WhatsApp webhook handler
- **GET** `/api/whatsapp/webhooks/status` - Get webhook status
- **POST** `/api/whatsapp/webhooks/verify` - Verify webhook
- **PUT** `/api/whatsapp/webhooks` - Update webhook settings

### **INDIAN LOCALIZATION ENDPOINTS**

#### **Indian Geography**
- **GET** `/api/l10n-in/states` - Get Indian states
- **GET** `/api/l10n-in/states/{state_id}/districts` - Get districts by state
- **GET** `/api/l10n-in/districts/{district_id}/cities` - Get cities by district
- **GET** `/api/l10n-in/cities/{city_id}/areas` - Get areas by city
- **GET** `/api/l10n-in/pincodes` - Search pincodes
- **GET** `/api/l10n-in/pincodes/{pincode}` - Get pincode details

#### **Indian GST**
- **GET** `/api/l10n-in/gst/state-codes` - Get GST state codes
- **GET** `/api/l10n-in/gst/hsn-codes` - Get HSN codes
- **GET** `/api/l10n-in/gst/sac-codes` - Get SAC codes
- **POST** `/api/l10n-in/gst/validate` - Validate GST number
- **GET** `/api/l10n-in/gst/rates` - Get GST rates

#### **Pincode Lookup**
- **GET** `/api/l10n-in/pincode-lookup/{pincode}` - Lookup pincode
- **GET** `/api/l10n-in/pincode-lookup/search` - Search pincodes
- **GET** `/api/l10n-in/pincode-lookup/validate` - Validate pincode

### **COMPLIANCE MODULE ENDPOINTS**

#### **Indian Compliance**
- **GET** `/api/compliance/gst-returns` - Get GST returns
- **POST** `/api/compliance/gst-returns` - Create GST return
- **GET** `/api/compliance/tds-returns` - Get TDS returns
- **POST** `/api/compliance/tds-returns` - Create TDS return
- **GET** `/api/compliance/audit-trail` - Get audit trail
- **GET** `/api/compliance/compliance-status` - Get compliance status

### **TESTING MODULE ENDPOINTS**

#### **Integration Testing**
- **POST** `/api/testing/run-tests` - Run integration tests
- **GET** `/api/testing/test-results` - Get test results
- **GET** `/api/testing/test-coverage` - Get test coverage
- **POST** `/api/testing/performance-test` - Run performance test
- **GET** `/api/testing/health-check` - System health check

### **OPTIMIZATION MODULE ENDPOINTS**

#### **Performance Optimization**
- **GET** `/api/optimization/performance-metrics` - Get performance metrics
- **POST** `/api/optimization/optimize-database` - Optimize database
- **GET** `/api/optimization/cache-status` - Get cache status
- **POST** `/api/optimization/clear-cache` - Clear cache
- **GET** `/api/optimization/query-analysis` - Analyze slow queries

---

## 📊 DATA MODELS & STRUCTURES

### **CORE MODELS**

#### **User Model**
```javascript
{
  id: number,
  username: string,
  email: string,
  full_name: string,
  phone: string,
  hashed_password: string,
  is_superuser: boolean,
  last_login: datetime,
  failed_login_attempts: number,
  locked_until: datetime,
  roles: Role[],
  companies: UserCompany[]
}
```

#### **Company Model**
```javascript
{
  id: number,
  name: string,
  display_name: string,
  legal_name: string,
  email: string,
  phone: string,
  website: string,
  address_line1: string,
  address_line2: string,
  city: string,
  state: string,
  country: string,
  postal_code: string,
  gst_number: string,
  pan_number: string,
  cin_number: string,
  business_type: string,
  financial_year_start: date,
  financial_year_end: date,
  current_financial_year: string,
  currency_code: string,
  currency_symbol: string,
  gst_registration_type: string,
  gst_state_code: string,
  is_active: boolean,
  is_default: boolean,
  logo_path: string,
  theme_color: string,
  description: string,
  notes: string
}
```

#### **Customer Model**
```javascript
{
  id: number,
  customer_code: string,
  name: string,
  display_name: string,
  customer_type: string, // retail, wholesale, corporate
  mobile: string,
  phone: string,
  email: string,
  website: string,
  address_line1: string,
  address_line2: string,
  city: string,
  state: string,
  country: string,
  postal_code: string,
  gst_number: string,
  pan_number: string,
  business_name: string,
  credit_limit: decimal,
  payment_terms: string,
  opening_balance: decimal,
  current_balance: decimal,
  discount_percent: decimal,
  price_list: string,
  date_of_birth: date,
  anniversary_date: date,
  gender: string,
  status: string, // active, inactive, blocked
  is_loyalty_member: boolean,
  loyalty_card_number: string,
  first_sale_date: datetime,
  last_sale_date: datetime,
  total_sales_amount: decimal,
  total_transactions: number
}
```

#### **Item Model**
```javascript
{
  id: number,
  barcode: string,
  style_code: string,
  sku: string,
  name: string,
  description: string,
  short_description: string,
  color: string,
  size: string,
  material: string,
  category_id: number,
  brand: string,
  brand_id: number,
  gender: string, // male, female, unisex, kids
  hsn_code: string,
  gst_rate: decimal,
  cess_rate: decimal,
  mrp: decimal,
  mrp_inclusive: boolean,
  purchase_rate: decimal,
  purchase_rate_inclusive: boolean,
  selling_price: decimal,
  selling_price_inclusive: boolean,
  landed_cost: decimal,
  margin_percent: decimal,
  is_stockable: boolean,
  track_inventory: boolean,
  min_stock_level: decimal,
  max_stock_level: decimal,
  reorder_level: decimal,
  uom: string, // PCS, KG, LTR, etc.
  weight: decimal,
  dimensions: string,
  status: string, // active, inactive, discontinued
  is_service: boolean,
  is_serialized: boolean,
  allow_negative_stock: boolean,
  image_path: string,
  additional_images: string[], // JSON array
  preferred_supplier_id: number,
  supplier_item_code: string
}
```

#### **ItemCategory Model**
```javascript
{
  id: number,
  name: string,
  display_name: string,
  description: string,
  parent_id: number,
  parent: ItemCategory,
  children: ItemCategory[],
  items: Item[]
}
```

#### **Brand Model**
```javascript
{
  id: number,
  name: string,
  display_name: string,
  description: string,
  items: Item[]
}
```

### **POS MODELS**

#### **POS Session Model**
```javascript
{
  id: number,
  session_number: string,
  session_date: date,
  store_id: number,
  cashier_id: number,
  opening_cash: decimal,
  closing_cash: decimal,
  expected_cash: decimal,
  cash_difference: decimal,
  total_sales: decimal,
  total_transactions: number,
  total_returns: decimal,
  total_exchanges: decimal,
  status: string, // open, closed
  opened_at: datetime,
  closed_at: datetime,
  notes: string
}
```

#### **POS Transaction Model**
```javascript
{
  id: number,
  transaction_number: string,
  session_id: number,
  customer_id: number,
  transaction_type: string, // sale, return, exchange
  transaction_date: datetime,
  subtotal: decimal,
  discount_amount: decimal,
  tax_amount: decimal,
  total_amount: decimal,
  payment_method: string,
  payment_reference: string,
  payment_status: string, // pending, paid, partial
  cgst_amount: decimal,
  sgst_amount: decimal,
  igst_amount: decimal,
  total_gst_amount: decimal,
  status: string, // draft, completed, void
  is_void: boolean,
  void_reason: string,
  void_date: datetime,
  original_transaction_id: number,
  exchange_id: number,
  return_id: number
}
```

### **SALES MODELS**

#### **Sale Challan Model**
```javascript
{
  id: number,
  company_id: number,
  challan_number: string,
  challan_date: date,
  customer_id: number,
  staff_id: number,
  challan_type: string, // delivery
  delivery_address: string,
  delivery_date: date,
  delivery_time: string,
  contact_person: string,
  contact_phone: string,
  total_quantity: decimal,
  total_amount: decimal,
  status: string,
  notes: string
}
```

### **PURCHASE MODELS**

#### **Purchase Order Model**
```javascript
{
  id: number,
  company_id: number,
  order_number: string,
  order_date: date,
  supplier_id: number,
  expected_date: date,
  subtotal: decimal,
  discount_amount: decimal,
  tax_amount: decimal,
  total_amount: decimal,
  status: string, // draft, confirmed, received, cancelled
  notes: string
}
```

#### **Purchase Invoice Model**
```javascript
{
  id: number,
  company_id: number,
  invoice_number: string,
  supplier_invoice_number: string,
  order_id: number,
  supplier_id: number,
  invoice_date: date,
  due_date: date,
  subtotal: decimal,
  discount_amount: decimal,
  tax_amount: decimal,
  total_amount: decimal,
  paid_amount: decimal,
  balance_amount: decimal,
  payment_status: string, // pending, paid, partial
  status: string, // draft, confirmed, cancelled
  notes: string
}
```

---

## 🔐 AUTHENTICATION & SECURITY

### **Authentication Mechanism**
- **JWT Token-based Authentication**
- **Token Expiration**: Configurable (default: 30 minutes)
- **Refresh Token**: Not implemented (stateless)
- **Password Hashing**: bcrypt with salt rounds

### **Security Features**
- **Account Lockout**: After failed login attempts
- **Password Requirements**: Configurable complexity
- **Session Management**: Server-side session tracking
- **CORS Configuration**: Configurable origins
- **Rate Limiting**: Basic implementation available

### **Role-Based Access Control (RBAC)**
- **Roles**: admin, manager, user, viewer
- **Permissions**: Granular permission system
- **Permission Format**: `module.action` (e.g., `items.create`, `sales.view`)
- **User Roles**: Many-to-many relationship
- **Role Permissions**: Many-to-many relationship

### **Permission System**
```javascript
// Permission Categories
const PERMISSIONS = {
  // User Management
  'users.create': 'Create users',
  'users.view': 'View users',
  'users.edit': 'Edit users',
  'users.delete': 'Delete users',
  
  // Company Management
  'companies.create': 'Create companies',
  'companies.view': 'View companies',
  'companies.update': 'Update companies',
  'companies.delete': 'Delete companies',
  'companies.manage_users': 'Manage company users',
  'companies.view_users': 'View company users',
  
  // Customer Management
  'customers.create': 'Create customers',
  'customers.view': 'View customers',
  'customers.edit': 'Edit customers',
  'customers.delete': 'Delete customers',
  
  // Item Management
  'items.create': 'Create items',
  'items.view': 'View items',
  'items.edit': 'Edit items',
  'items.delete': 'Delete items',
  'items.import': 'Import items',
  'items.export': 'Export items',
  
  // POS Management
  'pos.manage': 'Manage POS operations',
  'pos.view': 'View POS data',
  
  // Sales Management
  'sales.create': 'Create sales',
  'sales.view': 'View sales',
  'sales.edit': 'Edit sales',
  'sales.delete': 'Delete sales',
  
  // Purchase Management
  'purchases.create': 'Create purchases',
  'purchases.view': 'View purchases',
  'purchases.edit': 'Edit purchases',
  'purchases.delete': 'Delete purchases',
  
  // Reports
  'reports.sales': 'View sales reports',
  'reports.stock': 'View stock reports',
  'reports.financial': 'View financial reports'
}
```

### **Middleware Configuration**
- **CORS**: Configurable origins, methods, headers
- **Compression**: GZip middleware for responses
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
- **Request Logging**: All HTTP requests logged
- **Rate Limiting**: Basic implementation (can be enhanced with Redis)

---

## 🚀 DEVELOPMENT PHASES

### **Phase 1: Core Infrastructure (Week 1-2)**
1. **Project Setup**
   - React + Node.js + Tailwind CSS setup
   - Authentication system implementation
   - Basic routing and navigation
   - API client configuration

2. **Authentication & Authorization**
   - Login/logout functionality
   - JWT token management
   - Role-based access control
   - Protected routes implementation

3. **Core Components**
   - Layout components (Header, Sidebar, Footer)
   - Form components (Input, Select, Button)
   - Table components (DataTable, Pagination)
   - Modal components (Dialog, Confirmation)

### **Phase 2: Company & User Management (Week 3-4)**
1. **Company Management**
   - Company CRUD operations
   - Company settings
   - Multi-tenant support
   - Company switching

2. **User Management**
   - User CRUD operations
   - Role assignment
   - Permission management
   - User profile management

### **Phase 3: Customer & Inventory (Week 5-6)**
1. **Customer Management**
   - Customer CRUD operations
   - Customer groups
   - Loyalty program integration
   - Customer search and filtering

2. **Inventory Management**
   - Item CRUD operations
   - Category and brand management
   - Stock tracking
   - Import/export functionality

### **Phase 4: POS System (Week 7-8)**
1. **POS Interface**
   - POS session management
   - Transaction processing
   - Barcode scanning integration
   - Payment processing

2. **POS Features**
   - Receipt generation
   - Return and exchange handling
   - Customer lookup
   - Real-time stock updates

### **Phase 5: Sales & Purchase (Week 9-10)**
1. **Sales Management**
   - Sales order processing
   - Invoice generation
   - Payment tracking
   - Sales reports

2. **Purchase Management**
   - Purchase order processing
   - Supplier management
   - Receipt processing
   - Purchase reports

### **Phase 6: Reports & Analytics (Week 11-12)**
1. **Reporting System**
   - Sales reports
   - Stock reports
   - Financial reports
   - Dashboard analytics

2. **Advanced Features**
   - Export functionality
   - Print templates
   - Scheduled reports
   - Data visualization

### **Phase 7: Integration & Polish (Week 13-14)**
1. **WhatsApp Integration**
   - Message templates
   - Automated notifications
   - Receipt delivery

2. **Loyalty System**
   - Points management
   - Rewards system
   - Customer engagement

3. **Final Testing & Deployment**
   - End-to-end testing
   - Performance optimization
   - Production deployment

---

## ✅ MODULE IMPLEMENTATION CHECKLIST

### **Core Module**
- [ ] Authentication system
- [ ] User management
- [ ] Company management
- [ ] Role-based access control
- [ ] System settings
- [ ] Print templates

### **Customer Module**
- [ ] Customer CRUD
- [ ] Customer groups
- [ ] Loyalty integration
- [ ] Customer search
- [ ] Balance tracking

### **Inventory Module**
- [ ] Item CRUD
- [ ] Category management
- [ ] Brand management
- [ ] Stock tracking
- [ ] Import/export
- [ ] Low stock alerts

### **POS Module**
- [ ] Session management
- [ ] Transaction processing
- [ ] Barcode scanning
- [ ] Payment processing
- [ ] Receipt generation
- [ ] Return/exchange

### **Sales Module**
- [ ] Sales orders
- [ ] Invoice generation
- [ ] Payment tracking
- [ ] Bill series
- [ ] Payment modes

### **Purchase Module**
- [ ] Purchase orders
- [ ] Supplier management
- [ ] Receipt processing
- [ ] Invoice matching

### **Reports Module**
- [ ] Sales reports
- [ ] Stock reports
- [ ] Financial reports
- [ ] Dashboard
- [ ] Export functionality

### **Accounting Module**
- [ ] Chart of accounts
- [ ] Journal entries
- [ ] Ledger management
- [ ] GST compliance

### **Loyalty Module**
- [ ] Program management
- [ ] Points tracking
- [ ] Rewards system
- [ ] Customer engagement

### **WhatsApp Module**
- [ ] Integration setup
- [ ] Message templates
- [ ] Automated notifications
- [ ] Receipt delivery

---

## 🎨 COMPONENT STANDARDS

### **Design System**
- **Framework**: Tailwind CSS
- **Icons**: Heroicons or Lucide React
- **Colors**: Configurable theme system
- **Typography**: Inter or system fonts
- **Spacing**: Consistent spacing scale
- **Responsive**: Mobile-first design

### **Component Architecture**
```javascript
// Component Structure
src/
├── components/
│   ├── common/           // Reusable components
│   ├── forms/           // Form components
│   ├── tables/          // Table components
│   ├── modals/          // Modal components
│   └── layout/          // Layout components
├── pages/               // Page components
├── hooks/               // Custom hooks
├── services/            // API services
├── utils/               // Utility functions
├── constants/           // Constants
└── styles/              // Global styles
```

### **API Service Structure**
```javascript
// API Service Example
class ApiService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL;
    this.token = localStorage.getItem('token');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };
    
    const response = await fetch(url, config);
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    return response.json();
  }

  // Customer API
  async getCustomers(params = {}) {
    return this.request('/api/customers/', { method: 'GET' });
  }

  async createCustomer(data) {
    return this.request('/api/customers/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }
}
```

### **Form Validation**
```javascript
// Form Validation Example
const customerSchema = {
  name: {
    required: true,
    minLength: 2,
    maxLength: 200
  },
  email: {
    required: false,
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    message: 'Invalid email format'
  },
  mobile: {
    required: false,
    pattern: /^[0-9]{10}$/,
    message: 'Mobile number must be 10 digits'
  },
  gst_number: {
    required: false,
    pattern: /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/,
    message: 'Invalid GST number format'
  }
};
```

### **State Management**
```javascript
// Context API for State Management
const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const login = async (credentials) => {
    setLoading(true);
    try {
      const response = await authService.login(credentials);
      setUser(response.user);
      setCompany(response.company);
      localStorage.setItem('token', response.token);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppContext.Provider value={{
      user, setUser,
      company, setCompany,
      loading, setLoading,
      error, setError,
      login
    }}>
      {children}
    </AppContext.Provider>
  );
};
```

---

## 📈 PROGRESS TRACKING

### **Development Metrics**
- **Total Endpoints**: 150+ API endpoints
- **Core Models**: 25+ data models
- **Modules**: 10 major modules
- **Estimated Components**: 100+ React components
- **Estimated Timeline**: 14 weeks

### **Key Milestones**
1. **Week 2**: Authentication & Core Infrastructure ✅
2. **Week 4**: Company & User Management ✅
3. **Week 6**: Customer & Inventory Management ✅
4. **Week 8**: POS System Implementation ✅
5. **Week 10**: Sales & Purchase Management ✅
6. **Week 12**: Reports & Analytics ✅
7. **Week 14**: Integration & Deployment ✅

### **Quality Assurance**
- **Code Review**: All components reviewed
- **Testing**: Unit tests for utilities
- **Integration**: API integration testing
- **Performance**: Bundle size optimization
- **Accessibility**: WCAG compliance
- **Security**: Input validation & sanitization

---

## 🔧 TECHNICAL SPECIFICATIONS

### **Frontend Stack**
- **React**: 18.x (Latest stable)
- **Node.js**: 18.x LTS
- **Tailwind CSS**: 3.x
- **Build Tool**: Vite (recommended) or Create React App
- **Package Manager**: npm or yarn
- **State Management**: Context API + useReducer
- **HTTP Client**: Fetch API or Axios
- **Form Handling**: React Hook Form
- **Date Handling**: date-fns or dayjs
- **Icons**: Heroicons or Lucide React

### **Development Tools**
- **Code Editor**: VS Code with extensions
- **Version Control**: Git
- **Package Manager**: npm/yarn
- **Linting**: ESLint + Prettier
- **Testing**: Jest + React Testing Library
- **API Testing**: Postman or Insomnia
- **Deployment**: Vercel, Netlify, or AWS

### **Browser Support**
- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+
- **Mobile**: iOS Safari 14+, Chrome Mobile 90+

---

## 📝 NOTES

### **Important Considerations**
1. **No TypeScript**: Pure JavaScript implementation required
2. **Mobile Responsive**: All components must be mobile-friendly
3. **Accessibility**: WCAG 2.1 AA compliance
4. **Performance**: Optimize for fast loading and smooth interactions
5. **Security**: Implement proper input validation and sanitization
6. **Error Handling**: Comprehensive error handling and user feedback
7. **Offline Support**: Consider PWA features for offline functionality

### **API Integration Notes**
- All API calls should include proper error handling
- Implement loading states for better UX
- Use proper HTTP status code handling
- Implement retry logic for failed requests
- Cache frequently accessed data appropriately

### **Development Best Practices**
- Follow React best practices and hooks patterns
- Implement proper component composition
- Use semantic HTML elements
- Implement proper form validation
- Follow accessibility guidelines
- Write clean, maintainable code
- Document complex logic and components

---

## 🚨 CRITICAL ERROR PREVENTION GUIDE

### **⚠️ ZERO MISMATCH REQUIREMENTS**

#### **1. API Endpoint Validation**
```javascript
// CRITICAL: Always validate API endpoints before implementation
const API_ENDPOINTS = {
  // Core Authentication
  'POST /api/auth/login': {
    required_fields: ['username', 'password'],
    response_fields: ['access_token', 'token_type', 'expires_in'],
    error_codes: [401, 400, 423]
  },
  'GET /api/auth/me': {
    required_headers: ['Authorization: Bearer <token>'],
    response_fields: ['id', 'username', 'email', 'full_name', 'is_active', 'is_superuser', 'roles', 'last_login'],
    error_codes: [401, 403]
  },
  
  // Company Management
  'POST /api/companies/': {
    required_fields: ['name', 'financial_year_start', 'financial_year_end', 'current_financial_year'],
    optional_fields: ['display_name', 'legal_name', 'email', 'phone', 'gst_number', 'pan_number'],
    response_fields: ['id', 'name', 'display_name', 'gst_number', 'current_financial_year', 'is_active'],
    error_codes: [400, 403, 500]
  },
  
  // Customer Management
  'POST /api/customers/': {
    required_fields: ['name'],
    optional_fields: ['display_name', 'customer_type', 'mobile', 'email', 'address_line1', 'gst_number'],
    validation_rules: {
      'name': 'min_length:2, max_length:200',
      'mobile': 'pattern:/^[0-9]{10}$/',
      'email': 'pattern:/^[^\s@]+@[^\s@]+\.[^\s@]+$/',
      'gst_number': 'pattern:/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/'
    },
    error_codes: [400, 403, 500]
  },
  
  // Item Management
  'POST /api/items/': {
    required_fields: ['barcode', 'style_code', 'name'],
    optional_fields: ['description', 'category_id', 'brand', 'gst_rate', 'mrp', 'selling_price'],
    validation_rules: {
      'barcode': 'min_length:1, unique:true',
      'style_code': 'min_length:1',
      'name': 'min_length:2, max_length:200',
      'gst_rate': 'min:0, max:100'
    },
    error_codes: [400, 403, 500]
  }
};
```

#### **2. Data Model Field Validation**
```javascript
// CRITICAL: Exact field names and types from backend models
const DATA_MODELS = {
  User: {
    id: 'number',
    username: 'string',
    email: 'string',
    full_name: 'string',
    phone: 'string|null',
    hashed_password: 'string',
    is_superuser: 'boolean',
    last_login: 'datetime|null',
    failed_login_attempts: 'number',
    locked_until: 'datetime|null',
    roles: 'Role[]',
    companies: 'UserCompany[]'
  },
  
  Company: {
    id: 'number',
    name: 'string',
    display_name: 'string|null',
    legal_name: 'string|null',
    email: 'string|null',
    phone: 'string|null',
    website: 'string|null',
    address_line1: 'string|null',
    address_line2: 'string|null',
    city: 'string|null',
    state: 'string|null',
    country: 'string',
    postal_code: 'string|null',
    gst_number: 'string|null',
    pan_number: 'string|null',
    cin_number: 'string|null',
    business_type: 'string|null',
    financial_year_start: 'date',
    financial_year_end: 'date',
    current_financial_year: 'string',
    currency_code: 'string',
    currency_symbol: 'string',
    gst_registration_type: 'string',
    gst_state_code: 'string|null',
    is_active: 'boolean',
    is_default: 'boolean',
    logo_path: 'string|null',
    theme_color: 'string',
    description: 'string|null',
    notes: 'string|null'
  },
  
  Customer: {
    id: 'number',
    customer_code: 'string',
    name: 'string',
    display_name: 'string|null',
    customer_type: 'string', // retail, wholesale, corporate
    mobile: 'string|null',
    phone: 'string|null',
    email: 'string|null',
    website: 'string|null',
    address_line1: 'string|null',
    address_line2: 'string|null',
    city: 'string|null',
    state: 'string|null',
    country: 'string',
    postal_code: 'string|null',
    gst_number: 'string|null',
    pan_number: 'string|null',
    business_name: 'string|null',
    credit_limit: 'decimal',
    payment_terms: 'string|null',
    opening_balance: 'decimal',
    current_balance: 'decimal',
    discount_percent: 'decimal',
    price_list: 'string|null',
    date_of_birth: 'date|null',
    anniversary_date: 'date|null',
    gender: 'string|null',
    status: 'string', // active, inactive, blocked
    is_loyalty_member: 'boolean',
    loyalty_card_number: 'string|null',
    first_sale_date: 'datetime|null',
    last_sale_date: 'datetime|null',
    total_sales_amount: 'decimal',
    total_transactions: 'number'
  }
};
```

#### **3. Authentication & Permission Validation**
```javascript
// CRITICAL: Exact permission names and role requirements
const PERMISSIONS = {
  // User Management
  'users.create': { roles: ['admin'], description: 'Create users' },
  'users.view': { roles: ['admin', 'manager'], description: 'View users' },
  'users.edit': { roles: ['admin', 'manager'], description: 'Edit users' },
  'users.delete': { roles: ['admin'], description: 'Delete users' },
  
  // Company Management
  'companies.create': { roles: ['admin'], description: 'Create companies' },
  'companies.view': { roles: ['admin', 'manager', 'user'], description: 'View companies' },
  'companies.update': { roles: ['admin', 'manager'], description: 'Update companies' },
  'companies.delete': { roles: ['admin'], description: 'Delete companies' },
  'companies.manage_users': { roles: ['admin'], description: 'Manage company users' },
  'companies.view_users': { roles: ['admin', 'manager'], description: 'View company users' },
  
  // Customer Management
  'customers.create': { roles: ['admin', 'manager', 'user'], description: 'Create customers' },
  'customers.view': { roles: ['admin', 'manager', 'user'], description: 'View customers' },
  'customers.edit': { roles: ['admin', 'manager', 'user'], description: 'Edit customers' },
  'customers.delete': { roles: ['admin', 'manager'], description: 'Delete customers' },
  
  // Item Management
  'items.create': { roles: ['admin', 'manager', 'user'], description: 'Create items' },
  'items.view': { roles: ['admin', 'manager', 'user'], description: 'View items' },
  'items.edit': { roles: ['admin', 'manager', 'user'], description: 'Edit items' },
  'items.delete': { roles: ['admin', 'manager'], description: 'Delete items' },
  'items.import': { roles: ['admin', 'manager'], description: 'Import items' },
  'items.export': { roles: ['admin', 'manager', 'user'], description: 'Export items' },
  
  // POS Management
  'pos.manage': { roles: ['admin', 'manager', 'user'], description: 'Manage POS operations' },
  'pos.view': { roles: ['admin', 'manager', 'user'], description: 'View POS data' },
  
  // Sales Management
  'sales.create': { roles: ['admin', 'manager', 'user'], description: 'Create sales' },
  'sales.view': { roles: ['admin', 'manager', 'user'], description: 'View sales' },
  'sales.edit': { roles: ['admin', 'manager', 'user'], description: 'Edit sales' },
  'sales.delete': { roles: ['admin', 'manager'], description: 'Delete sales' },
  
  // Purchase Management
  'purchases.create': { roles: ['admin', 'manager', 'user'], description: 'Create purchases' },
  'purchases.view': { roles: ['admin', 'manager', 'user'], description: 'View purchases' },
  'purchases.edit': { roles: ['admin', 'manager', 'user'], description: 'Edit purchases' },
  'purchases.delete': { roles: ['admin', 'manager'], description: 'Delete purchases' },
  
  // Reports
  'reports.sales': { roles: ['admin', 'manager', 'user'], description: 'View sales reports' },
  'reports.stock': { roles: ['admin', 'manager', 'user'], description: 'View stock reports' },
  'reports.financial': { roles: ['admin', 'manager'], description: 'View financial reports' }
};
```

#### **4. Form Validation Schemas**
```javascript
// CRITICAL: Exact validation rules matching backend
const VALIDATION_SCHEMAS = {
  customer: {
    name: {
      required: true,
      minLength: 2,
      maxLength: 200,
      message: 'Customer name must be between 2 and 200 characters'
    },
    email: {
      required: false,
      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      message: 'Invalid email format'
    },
    mobile: {
      required: false,
      pattern: /^[0-9]{10}$/,
      message: 'Mobile number must be 10 digits'
    },
    gst_number: {
      required: false,
      pattern: /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/,
      message: 'Invalid GST number format'
    },
    credit_limit: {
      required: false,
      min: 0,
      type: 'decimal',
      message: 'Credit limit must be a positive number'
    }
  },
  
  item: {
    barcode: {
      required: true,
      minLength: 1,
      unique: true,
      message: 'Barcode cannot be empty and must be unique'
    },
    style_code: {
      required: true,
      minLength: 1,
      message: 'Style code cannot be empty'
    },
    name: {
      required: true,
      minLength: 2,
      maxLength: 200,
      message: 'Item name must be between 2 and 200 characters'
    },
    gst_rate: {
      required: false,
      min: 0,
      max: 100,
      type: 'decimal',
      message: 'GST rate must be between 0 and 100'
    },
    mrp: {
      required: false,
      min: 0,
      type: 'decimal',
      message: 'MRP must be a positive number'
    },
    selling_price: {
      required: false,
      min: 0,
      type: 'decimal',
      message: 'Selling price must be a positive number'
    }
  }
};
```

#### **5. Error Handling Patterns**
```javascript
// CRITICAL: Handle all possible API errors
const ERROR_HANDLING = {
  // HTTP Status Codes
  400: 'Bad Request - Invalid data provided',
  401: 'Unauthorized - Authentication required',
  403: 'Forbidden - Insufficient permissions',
  404: 'Not Found - Resource does not exist',
  409: 'Conflict - Resource already exists',
  422: 'Unprocessable Entity - Validation failed',
  423: 'Locked - Account is locked',
  500: 'Internal Server Error - Server error occurred',
  
  // Common Error Responses
  'INVALID_CREDENTIALS': 'Invalid username or password',
  'ACCOUNT_LOCKED': 'Account is locked due to failed login attempts',
  'INACTIVE_USER': 'User account is inactive',
  'INSUFFICIENT_PERMISSIONS': 'User does not have required permissions',
  'DUPLICATE_ENTRY': 'Record with this information already exists',
  'VALIDATION_ERROR': 'One or more fields failed validation',
  'RESOURCE_NOT_FOUND': 'Requested resource does not exist',
  'COMPANY_ACCESS_DENIED': 'Access denied to this company',
  'CUSTOMER_HAS_TRANSACTIONS': 'Cannot delete customer with existing transactions',
  'ITEM_HAS_STOCK': 'Cannot delete item with stock',
  'CREDIT_LIMIT_EXCEEDED': 'Customer credit limit exceeded'
};
```

#### **6. API Response Structure Validation**
```javascript
// CRITICAL: Validate exact response structures
const RESPONSE_STRUCTURES = {
  login: {
    success: {
      access_token: 'string',
      token_type: 'string',
      expires_in: 'number'
    },
    error: {
      detail: 'string',
      status_code: 'number'
    }
  },
  
  user_profile: {
    id: 'number',
    username: 'string',
    email: 'string',
    full_name: 'string',
    is_active: 'boolean',
    is_superuser: 'boolean',
    roles: 'string[]',
    last_login: 'datetime|null'
  },
  
  customer_list: {
    data: 'Customer[]',
    total: 'number',
    page: 'number',
    limit: 'number',
    has_next: 'boolean',
    has_prev: 'boolean'
  },
  
  item_details: {
    id: 'number',
    barcode: 'string',
    style_code: 'string',
    name: 'string',
    description: 'string|null',
    category_id: 'number|null',
    brand: 'string|null',
    gst_rate: 'decimal',
    mrp: 'decimal|null',
    selling_price: 'decimal|null',
    current_stock: 'decimal|null',
    stock_value: 'decimal|null',
    status: 'string'
  }
};
```

### **🔧 IMPLEMENTATION CHECKLIST**

#### **Before Starting Development:**
- [ ] **Verify all 766 API endpoints** are documented
- [ ] **Validate all data model fields** match backend exactly
- [ ] **Check all permission names** are correct
- [ ] **Confirm validation rules** match backend schemas
- [ ] **Test API endpoints** with Postman/Insomnia
- [ ] **Verify authentication flow** works correctly
- [ ] **Check CORS configuration** allows frontend domain
- [ ] **Validate error responses** are handled properly

#### **During Development:**
- [ ] **Use exact field names** from backend models
- [ ] **Implement proper error handling** for all API calls
- [ ] **Validate all form inputs** with backend rules
- [ ] **Check permission requirements** before API calls
- [ ] **Handle loading states** for all async operations
- [ ] **Implement proper pagination** for list endpoints
- [ ] **Use correct HTTP methods** for each endpoint
- [ ] **Include proper headers** (Authorization, Content-Type)

#### **Before Deployment:**
- [ ] **Test all API integrations** end-to-end
- [ ] **Verify error handling** works correctly
- [ ] **Check form validation** matches backend
- [ ] **Test authentication flow** completely
- [ ] **Validate permission system** works properly
- [ ] **Test mobile responsiveness** on all screens
- [ ] **Verify data consistency** between frontend and backend
- [ ] **Check performance** with large datasets

### **🚨 COMMON MISTAKES TO AVOID**

1. **Field Name Mismatches**: Use exact field names from backend models
2. **Missing Validation**: Implement all validation rules from backend
3. **Incorrect HTTP Methods**: Use correct methods for each endpoint
4. **Missing Error Handling**: Handle all possible API errors
5. **Permission Bypass**: Always check permissions before API calls
6. **Data Type Mismatches**: Use correct data types (string, number, boolean, decimal)
7. **Missing Required Fields**: Include all required fields in API requests
8. **Incorrect Response Handling**: Parse responses according to documented structure
9. **Authentication Issues**: Properly handle JWT tokens and refresh
10. **CORS Problems**: Ensure CORS is configured correctly

---

**This document serves as the single source of truth for frontend development. Update it as the project evolves and new requirements are identified.**
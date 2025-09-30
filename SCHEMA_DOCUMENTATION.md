# Comprehensive Schema Documentation

## Overview
This document provides comprehensive documentation for all Pydantic schemas in the ERP system. The schemas are organized by functional modules and provide type safety, validation, and serialization for API endpoints.

## Schema Categories

### 1. User Management Schemas
**File**: `app/schemas/user_schema.py`

#### Core Schemas
- **UserBase**: Base user information
- **UserCreate**: User creation with password
- **UserUpdate**: User information updates
- **UserResponse**: Complete user information with metadata
- **UserLogin**: Login credentials
- **Token**: Authentication token response
- **ACLPermission**: Access control permissions

#### Key Features
- Email validation
- Password strength requirements
- Role-based access control
- User status management
- Security features (failed login tracking, account locking)

### 2. Customer Management Schemas
**File**: `app/schemas/customer_schema.py`

#### Core Schemas
- **CustomerBase**: Base customer information
- **CustomerCreate**: New customer creation
- **CustomerUpdate**: Customer information updates
- **CustomerResponse**: Complete customer data with analytics
- **CustomerDetailResponse**: Extended customer information
- **CustomerImportResponse**: Bulk import results
- **CustomerActivityResponse**: Customer activity summary

#### Key Features
- GST number validation
- PAN number validation
- Credit limit management
- Loyalty program integration
- Customer segmentation
- Import/export functionality

### 3. Sales Management Schemas
**File**: `app/schemas/sales_schema.py`

#### Core Schemas
- **SalesInvoiceCreate/Update/Response**: Invoice management
- **SalesItemCreate/Update/Response**: Invoice line items
- **SalesReturnCreate/Update/Response**: Return processing
- **SalesPaymentCreate/Update/Response**: Payment tracking
- **SalesQuoteCreate/Update/Response**: Quotation management
- **SalesOrderCreate/Update/Response**: Order processing

#### Key Features
- Multi-currency support
- GST calculation
- Payment tracking
- Return processing
- Commission management
- Discount management
- Analytics and reporting

### 4. Purchase Management Schemas
**File**: `app/schemas/purchase_schema.py`

#### Core Schemas
- **PurchaseOrderCreate/Update/Response**: Purchase order management
- **PurchaseItemCreate/Update/Response**: Order line items
- **PurchaseReceiptCreate/Update/Response**: Goods receipt
- **PurchaseReturnCreate/Update/Response**: Purchase returns
- **PurchasePaymentCreate/Update/Response**: Payment processing
- **SupplierCreate/Update/Response**: Supplier management

#### Key Features
- Supplier management
- Purchase approval workflow
- Goods receipt processing
- Return management
- Payment tracking
- Supplier analytics
- Purchase comparison

### 5. Inventory Management Schemas
**File**: `app/schemas/inventory_schema.py`

#### Core Schemas
- **ItemCreate/Update/Response**: Product management
- **ItemVariantCreate/Update/Response**: Product variants
- **StockMovementCreate/Update/Response**: Stock transactions
- **StockAdjustmentCreate/Update/Response**: Stock adjustments
- **InventoryGroupCreate/Update/Response**: Category management
- **StockTransferCreate/Update/Response**: Inter-location transfers

#### Key Features
- Product lifecycle management
- Variant management
- Stock tracking
- Serial number tracking
- Batch number tracking
- Expiry date management
- Stock valuation
- Reorder management

### 6. POS Management Schemas
**File**: `app/schemas/pos_schema.py`

#### Core Schemas
- **POSSessionCreate/Update/Response**: Session management
- **POSTransactionCreate/Update/Response**: Transaction processing
- **POSTransactionItemCreate/Update/Response**: Transaction items
- **POSPaymentCreate/Update/Response**: Payment processing
- **StoreCreate/Update/Response**: Store management
- **StoreStaffCreate/Update/Response**: Staff management

#### Key Features
- Session management
- Transaction processing
- Payment method support
- Receipt generation
- Store management
- Staff permissions
- Analytics and reporting

### 7. Loyalty Management Schemas
**File**: `app/schemas/loyalty_schema.py`

#### Core Schemas
- **LoyaltyGradeCreate/Update/Response**: Tier management
- **LoyaltyTransactionCreate/Update/Response**: Points transactions
- **LoyaltyPointsCreate/Update/Response**: Points balance
- **LoyaltyRewardCreate/Update/Response**: Reward management
- **LoyaltyProgramCreate/Update/Response**: Program management
- **LoyaltyRuleCreate/Update/Response**: Rule engine
- **LoyaltyTierCreate/Update/Response**: Tier management

#### Key Features
- Multi-tier loyalty programs
- Points earning and redemption
- Reward management
- Rule engine
- Customer segmentation
- Analytics and reporting
- Import/export functionality

### 8. Accounting Management Schemas
**File**: `app/schemas/accounting_schema.py`

#### Core Schemas
- **ChartOfAccountCreate/Update/Response**: Account management
- **JournalEntryCreate/Update/Response**: Journal entries
- **TrialBalanceCreate/Update/Response**: Trial balance
- **BalanceSheetCreate/Update/Response**: Balance sheet
- **ProfitLossStatementCreate/Update/Response**: P&L statement
- **AccountBalanceCreate/Update/Response**: Account balances
- **FinancialYearCreate/Update/Response**: Financial year management

#### Key Features
- Double-entry bookkeeping
- Chart of accounts
- Journal entries
- Financial reporting
- Bank reconciliation
- Advanced reporting
- Analytics and insights

### 9. Core System Schemas
**File**: `app/schemas/core_schema.py`

#### Core Schemas
- **CompanyCreate/Update/Response**: Company management
- **StaffCreate/Update/Response**: Staff management
- **ExpenseCreate/Update/Response**: Expense tracking
- **PaymentCreate/Update/Response**: Payment processing
- **GSTCreate/Update/Response**: GST management
- **DiscountCreate/Update/Response**: Discount management
- **ReportCreate/Update/Response**: Report management

#### Key Features
- Company setup
- Staff management
- Expense tracking
- Payment processing
- GST compliance
- Discount management
- Report generation
- System integration
- Backup management

### 10. Indian Localization Schemas
**File**: `app/schemas/l10n_in_schema.py`

#### Core Schemas
- **GSTTaxStructureCreate/Update/Response**: GST tax rates
- **StateCreate/Update/Response**: State management
- **DistrictCreate/Update/Response**: District management
- **PincodeCreate/Update/Response**: Pincode management
- **BankCreate/Update/Response**: Bank management
- **BankBranchCreate/Update/Response**: Branch management
- **TDSCreate/Update/Response**: TDS management
- **EInvoiceCreate/Update/Response**: E-invoice management
- **EWaybillCreate/Update/Response**: E-waybill management

#### Key Features
- GST compliance
- Indian geography
- Banking integration
- TDS/TCS management
- E-invoice generation
- E-waybill management
- Compliance reporting
- Analytics and insights

### 11. WhatsApp Integration Schemas
**File**: `app/schemas/whatsapp_schema.py`

#### Core Schemas
- **WhatsAppTemplateCreate/Update/Response**: Template management
- **WhatsAppMessageSend/Response**: Message sending
- **WhatsAppCampaignCreate/Update/Response**: Campaign management
- **POSReceiptRequest**: POS receipt sending
- **LoyaltyPointsRequest**: Loyalty notifications
- **InvoiceRequest**: Invoice sending
- **MarketingMessageRequest**: Marketing messages
- **OptInRequest/OptOutRequest**: Consent management

#### Key Features
- Template management
- Message sending
- Campaign management
- POS integration
- Loyalty integration
- Marketing automation
- Consent management
- Analytics and reporting

## Schema Design Principles

### 1. Naming Conventions
- **Create**: For creating new records
- **Update**: For updating existing records
- **Response**: For API responses
- **Request**: For API requests
- **Base**: For base classes
- **Enum**: For enumeration types

### 2. Field Validation
- **Required Fields**: Clearly marked with `...` or `Field(...)`
- **Optional Fields**: Marked with `Optional[Type]` or `Field(None)`
- **Validation Rules**: Using Pydantic validators
- **Type Safety**: Proper type hints for all fields

### 3. Data Types
- **Monetary Values**: `Decimal` for precision
- **Dates**: `date` for dates, `datetime` for timestamps
- **IDs**: `int` for primary keys
- **Text**: `str` with length constraints
- **Lists**: `List[Type]` for collections
- **Dictionaries**: `Dict[str, Any]` for JSON data

### 4. Relationships
- **Foreign Keys**: Referenced by ID
- **Nested Objects**: Using response schemas
- **Associations**: Through junction tables

### 5. Security
- **Sensitive Data**: Excluded from responses
- **Validation**: Input validation and sanitization
- **Authorization**: Role-based access control
- **Audit Trail**: Created/updated timestamps

## Usage Examples

### Creating a Customer
```python
from app.schemas import CustomerCreate

customer_data = CustomerCreate(
    name="John Doe",
    email="john@example.com",
    mobile="9876543210",
    customer_type="retail"
)
```

### Updating a Customer
```python
from app.schemas import CustomerUpdate

update_data = CustomerUpdate(
    name="John Smith",
    email="johnsmith@example.com"
)
```

### API Response
```python
from app.schemas import CustomerResponse

# Automatically serialized from database model
customer = CustomerResponse.from_orm(db_customer)
```

## Validation Rules

### Common Validations
- **Email**: Valid email format
- **Phone**: 10-15 digits
- **GST**: 15-character GST number
- **PAN**: 10-character PAN number
- **Amounts**: Non-negative decimal values
- **Dates**: Valid date format
- **URLs**: Valid URL format

### Custom Validations
- **GST Number**: State code + PAN + check digit
- **PAN Number**: 5 letters + 4 digits + 1 letter
- **Phone Numbers**: Country-specific formats
- **Postal Codes**: Country-specific formats

## Error Handling

### Validation Errors
- **Field Required**: Missing required fields
- **Invalid Format**: Incorrect data format
- **Value Out of Range**: Values outside allowed range
- **Invalid Type**: Wrong data type

### Business Logic Errors
- **Duplicate Values**: Unique constraint violations
- **Referential Integrity**: Foreign key violations
- **Business Rules**: Custom business logic violations

## Best Practices

### 1. Schema Design
- Keep schemas focused and single-purpose
- Use inheritance for common fields
- Provide clear field descriptions
- Use appropriate data types

### 2. Validation
- Validate at the schema level
- Provide meaningful error messages
- Use custom validators for complex rules
- Test validation thoroughly

### 3. Documentation
- Document all schemas and fields
- Provide usage examples
- Explain business rules
- Keep documentation up to date

### 4. Performance
- Use appropriate field types
- Avoid unnecessary validations
- Optimize for serialization
- Consider caching strategies

## Testing

### Unit Tests
- Test all validation rules
- Test edge cases
- Test error conditions
- Test serialization/deserialization

### Integration Tests
- Test API endpoints
- Test database operations
- Test business logic
- Test error handling

## Maintenance

### Regular Updates
- Review and update schemas
- Add new fields as needed
- Remove deprecated fields
- Update documentation

### Version Control
- Use semantic versioning
- Maintain backward compatibility
- Document breaking changes
- Provide migration guides

## Conclusion

This comprehensive schema system provides:
- **Type Safety**: Compile-time type checking
- **Validation**: Runtime data validation
- **Documentation**: Self-documenting APIs
- **Consistency**: Standardized data structures
- **Maintainability**: Easy to update and extend
- **Performance**: Optimized serialization
- **Security**: Input validation and sanitization

The schemas are designed to be flexible, maintainable, and performant while providing comprehensive validation and documentation for the entire ERP system.
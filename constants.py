"""Application constants"""

# API
API_PREFIX = "/api/v1"

# Pagination
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200

# GST Rates
GST_RATE_5 = 0.05
GST_RATE_12 = 0.12
GST_THRESHOLD = 999.00  # If MRP <= 999, use 5% GST, else 12%

# User Roles
class UserRole:
    ADMIN = "admin"
    MANAGER = "manager"
    CASHIER = "cashier"
    VIEWER = "viewer"

# Item Status
class ItemStatus:
    ACTIVE = "active"
    INACTIVE = "inactive"

# Bill Status
class BillStatus:
    DRAFT = "draft"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Payment Status
class PaymentStatus:
    PENDING = "pending"
    PARTIAL = "partial"
    COMPLETED = "completed"

# Return Credit Status
class ReturnCreditStatus:
    OPEN = "open"
    PARTIAL = "partial"
    CLOSED = "closed"

# Tax Regions
class TaxRegion:
    LOCAL = "local"
    INTER = "inter"

# Payment Settlement Types
class SettlementType:
    CASH = "cash"
    BANK = "bank"
    SUPPLIER = "supplier"

# Coupon Types
class CouponType:
    PERCENT = "percent"
    FLAT = "flat"

# Gender Options
GENDER_OPTIONS = ["Male", "Female", "Unisex", "Kids"]

# Round Off Options
ROUND_OFF_OPTIONS = [0.01, 0.50, 1.00]

# Date Format
DATE_FORMAT = "%d-%m-%Y"
DATETIME_FORMAT = "%d-%m-%Y %H:%M:%S"

# File Upload
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# WhatsApp Templates
WHATSAPP_TEMPLATES = {
    "OTP": "otp_template",
    "INVOICE": "invoice_template",
    "COUPON": "coupon_template"
}
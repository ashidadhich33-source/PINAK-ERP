# backend/app/models/enhanced_purchase.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from .base import BaseModel

class PlaceOfSupplyType(PyEnum):
    """Place of Supply Types for Indian GST"""
    INTRA_STATE = "intra_state"  # Within same state
    INTER_STATE = "inter_state"  # Between different states
    EXPORT = "export"  # Export of goods/services
    IMPORT = "import"  # Import of goods/services

class PurchaseExcelImport(BaseModel):
    """Purchase Excel import tracking"""
    __tablename__ = "purchase_excel_import"
    
    import_name = Column(String(200), nullable=False)
    file_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    total_rows = Column(Integer, default=0)
    processed_rows = Column(Integer, default=0)
    success_rows = Column(Integer, default=0)
    error_rows = Column(Integer, default=0)
    import_status = Column(String(20), default='pending')  # pending, processing, completed, failed
    error_log = Column(Text, nullable=True)
    import_data = Column(JSON, nullable=True)  # Store parsed Excel data
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Relationships
    import_items = relationship("PurchaseExcelImportItem", back_populates="import_record")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<PurchaseExcelImport(name='{self.import_name}', status='{self.import_status}')>"

class PurchaseExcelImportItem(BaseModel):
    """Individual items from Excel import"""
    __tablename__ = "purchase_excel_import_item"
    
    import_id = Column(Integer, ForeignKey('purchase_excel_import.id'), nullable=False)
    row_number = Column(Integer, nullable=False)
    item_name = Column(String(200), nullable=False)
    item_code = Column(String(100), nullable=True)
    barcode = Column(String(50), nullable=True)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    gst_rate = Column(Numeric(5, 2), nullable=True)
    hsn_code = Column(String(10), nullable=True)
    supplier_name = Column(String(200), nullable=True)
    supplier_code = Column(String(100), nullable=True)
    bill_number = Column(String(100), nullable=True)
    bill_date = Column(Date, nullable=True)
    processing_status = Column(String(20), default='pending')  # pending, processed, error
    error_message = Column(Text, nullable=True)
    matched_item_id = Column(Integer, ForeignKey('item.id'), nullable=True)
    matched_supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=True)
    
    # Relationships
    import_record = relationship("PurchaseExcelImport", back_populates="import_items")
    matched_item = relationship("Item")
    matched_supplier = relationship("Supplier")
    
    def __repr__(self):
        return f"<PurchaseExcelImportItem(item='{self.item_name}', row={self.row_number})>"

class PurchaseBillMatching(BaseModel):
    """Purchase bill matching for Excel imports"""
    __tablename__ = "purchase_bill_matching"
    
    import_id = Column(Integer, ForeignKey('purchase_excel_import.id'), nullable=False)
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    bill_number = Column(String(100), nullable=False)
    bill_date = Column(Date, nullable=False)
    bill_amount = Column(Numeric(12, 2), nullable=False)
    matched_amount = Column(Numeric(12, 2), default=0)
    matching_status = Column(String(20), default='pending')  # pending, matched, partial, unmatched
    matching_percentage = Column(Numeric(5, 2), default=0)
    notes = Column(Text, nullable=True)
    
    # Relationships
    import_record = relationship("PurchaseExcelImport")
    supplier = relationship("Supplier")
    matching_items = relationship("PurchaseBillMatchingItem", back_populates="matching_record")
    
    def __repr__(self):
        return f"<PurchaseBillMatching(bill='{self.bill_number}', status='{self.matching_status}')>"

class PurchaseBillMatchingItem(BaseModel):
    """Individual items in bill matching"""
    __tablename__ = "purchase_bill_matching_item"
    
    matching_id = Column(Integer, ForeignKey('purchase_bill_matching.id'), nullable=False)
    import_item_id = Column(Integer, ForeignKey('purchase_excel_import_item.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    gst_rate = Column(Numeric(5, 2), nullable=True)
    cgst_amount = Column(Numeric(10, 2), nullable=True)
    sgst_amount = Column(Numeric(10, 2), nullable=True)
    igst_amount = Column(Numeric(10, 2), nullable=True)
    is_matched = Column(Boolean, default=False)
    
    # Relationships
    matching_record = relationship("PurchaseBillMatching", back_populates="matching_items")
    import_item = relationship("PurchaseExcelImportItem")
    item = relationship("Item")
    
    def __repr__(self):
        return f"<PurchaseBillMatchingItem(item_id={self.item_id}, amount={self.total_amount})>"

class DirectStockInward(BaseModel):
    """Direct stock inward without purchase"""
    __tablename__ = "direct_stock_inward"
    
    inward_number = Column(String(100), unique=True, nullable=False)
    inward_date = Column(Date, nullable=False)
    inward_type = Column(String(50), default='opening_stock')  # opening_stock, adjustment, transfer
    reference_number = Column(String(100), nullable=True)
    reference_date = Column(Date, nullable=True)
    total_quantity = Column(Numeric(10, 2), default=0)
    total_value = Column(Numeric(12, 2), default=0)
    notes = Column(Text, nullable=True)
    status = Column(String(20), default='draft')  # draft, confirmed, cancelled
    
    # Relationships
    inward_items = relationship("DirectStockInwardItem", back_populates="inward_record")
    
    def __repr__(self):
        return f"<DirectStockInward(number='{self.inward_number}', type='{self.inward_type}')>"

class DirectStockInwardItem(BaseModel):
    """Individual items in direct stock inward"""
    __tablename__ = "direct_stock_inward_item"
    
    inward_id = Column(Integer, ForeignKey('direct_stock_inward.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=True)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=False)
    total_cost = Column(Numeric(10, 2), nullable=False)
    location_id = Column(Integer, ForeignKey('stock_location.id'), nullable=True)
    batch_number = Column(String(100), nullable=True)
    expiry_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    inward_record = relationship("DirectStockInward", back_populates="inward_items")
    item = relationship("Item")
    variant = relationship("InventoryVariant")
    location = relationship("StockLocation")
    
    def __repr__(self):
        return f"<DirectStockInwardItem(item_id={self.item_id}, quantity={self.quantity})>"

class PurchaseReturn(BaseModel):
    """Purchase return management"""
    __tablename__ = "purchase_return"
    
    return_number = Column(String(100), unique=True, nullable=False)
    return_date = Column(Date, nullable=False)
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    original_bill_id = Column(Integer, ForeignKey('purchase_bill.id'), nullable=True)
    original_bill_number = Column(String(100), nullable=True)
    original_bill_date = Column(Date, nullable=True)
    return_reason = Column(String(200), nullable=True)
    return_type = Column(String(50), default='defective')  # defective, excess, wrong_item, damaged
    total_quantity = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(12, 2), default=0)
    cgst_amount = Column(Numeric(10, 2), default=0)
    sgst_amount = Column(Numeric(10, 2), default=0)
    igst_amount = Column(Numeric(10, 2), default=0)
    total_gst_amount = Column(Numeric(10, 2), default=0)
    net_amount = Column(Numeric(12, 2), default=0)
    status = Column(String(20), default='draft')  # draft, confirmed, processed, cancelled
    notes = Column(Text, nullable=True)
    
    # Relationships
    supplier = relationship("Supplier")
    original_bill = relationship("PurchaseBill")
    return_items = relationship("PurchaseReturnItem", back_populates="return_record")
    
    def __repr__(self):
        return f"<PurchaseReturn(number='{self.return_number}', supplier_id={self.supplier_id})>"

class PurchaseReturnItem(BaseModel):
    """Individual items in purchase return"""
    __tablename__ = "purchase_return_item"
    
    return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=True)
    original_bill_item_id = Column(Integer, ForeignKey('purchase_bill_item.id'), nullable=True)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    gst_rate = Column(Numeric(5, 2), nullable=True)
    cgst_amount = Column(Numeric(10, 2), nullable=True)
    sgst_amount = Column(Numeric(10, 2), nullable=True)
    igst_amount = Column(Numeric(10, 2), nullable=True)
    return_reason = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    return_record = relationship("PurchaseReturn", back_populates="return_items")
    item = relationship("Item")
    variant = relationship("InventoryVariant")
    original_bill_item = relationship("PurchaseBillItem")
    
    def __repr__(self):
        return f"<PurchaseReturnItem(item_id={self.item_id}, quantity={self.quantity})>"

class PurchaseOrder(BaseModel):
    """Purchase order management"""
    __tablename__ = "purchase_order"
    
    order_number = Column(String(100), unique=True, nullable=False)
    order_date = Column(Date, nullable=False)
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    expected_delivery_date = Column(Date, nullable=True)
    order_status = Column(String(20), default='draft')  # draft, sent, confirmed, partial, completed, cancelled
    total_quantity = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(12, 2), default=0)
    notes = Column(Text, nullable=True)
    
    # Relationships
    supplier = relationship("Supplier")
    order_items = relationship("PurchaseOrderItem", back_populates="order_record")
    
    def __repr__(self):
        return f"<PurchaseOrder(number='{self.order_number}', supplier_id={self.supplier_id})>"

class PurchaseOrderItem(BaseModel):
    """Individual items in purchase order"""
    __tablename__ = "purchase_order_item"
    
    order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=True)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    received_quantity = Column(Numeric(10, 2), default=0)
    pending_quantity = Column(Numeric(10, 2), nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    order_record = relationship("PurchaseOrder", back_populates="order_items")
    item = relationship("Item")
    variant = relationship("InventoryVariant")
    
    def __repr__(self):
        return f"<PurchaseOrderItem(item_id={self.item_id}, quantity={self.quantity})>"

class PurchaseInvoice(BaseModel):
    """Purchase invoice management with Indian GST compliance"""
    __tablename__ = "purchase_invoice"
    
    invoice_number = Column(String(100), unique=True, nullable=False)
    invoice_date = Column(Date, nullable=False)
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    bill_id = Column(Integer, ForeignKey('purchase_bill.id'), nullable=True)
    invoice_type = Column(String(50), default='regular')  # regular, credit_note, debit_note
    
    # Indian GST Compliance Fields
    gstin = Column(String(15), nullable=True)  # Supplier GSTIN
    place_of_supply = Column(Enum(PlaceOfSupplyType), nullable=True)
    supplier_state_code = Column(String(2), nullable=True)
    recipient_state_code = Column(String(2), nullable=True)
    
    # Amount Fields
    subtotal_amount = Column(Numeric(12, 2), nullable=False)  # Amount before GST
    cgst_rate = Column(Numeric(5, 2), nullable=True)
    cgst_amount = Column(Numeric(10, 2), default=0)
    sgst_rate = Column(Numeric(5, 2), nullable=True)
    sgst_amount = Column(Numeric(10, 2), default=0)
    igst_rate = Column(Numeric(5, 2), nullable=True)
    igst_amount = Column(Numeric(10, 2), default=0)
    cess_rate = Column(Numeric(5, 2), nullable=True)
    cess_amount = Column(Numeric(10, 2), default=0)
    total_gst_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(12, 2), nullable=False)  # Final amount including GST
    
    # Reverse Charge Fields
    reverse_charge_applicable = Column(Boolean, default=False)
    reverse_charge_amount = Column(Numeric(10, 2), default=0)
    reverse_charge_section = Column(String(10), nullable=True)
    
    # TDS Fields
    tds_applicable = Column(Boolean, default=False)
    tds_rate = Column(Numeric(5, 2), nullable=True)
    tds_amount = Column(Numeric(10, 2), default=0)
    tds_section = Column(String(10), nullable=True)
    
    # Status and Notes
    status = Column(String(20), default='draft')  # draft, confirmed, paid, cancelled
    notes = Column(Text, nullable=True)
    
    # Accounting Integration Fields
    journal_entry_created = Column(Boolean, default=False)
    journal_entry_id = Column(Integer, ForeignKey('journal_entry.id'), nullable=True)
    payment_terms_id = Column(Integer, ForeignKey('payment_term.id'), nullable=True)
    analytic_account_id = Column(Integer, ForeignKey('analytic_account.id'), nullable=True)
    bank_account_id = Column(Integer, ForeignKey('bank_account.id'), nullable=True)
    payment_method_id = Column(Integer, ForeignKey('payment_method.id'), nullable=True)
    
    # Relationships
    supplier = relationship("Supplier")
    bill = relationship("PurchaseBill")
    invoice_items = relationship("PurchaseInvoiceItem", back_populates="invoice_record")
    
    # Accounting Integration Relationships
    journal_entry = relationship("JournalEntry")
    payment_terms = relationship("PaymentTerm")
    analytic_account = relationship("AnalyticAccount")
    bank_account = relationship("BankAccount")
    payment_method = relationship("PaymentMethod")
    purchase_journal_entries = relationship("PurchaseJournalEntry", foreign_keys="PurchaseJournalEntry.purchase_invoice_id")
    purchase_payments = relationship("PurchasePayment", foreign_keys="PurchasePayment.purchase_invoice_id")
    purchase_analytics = relationship("PurchaseAnalytic", foreign_keys="PurchaseAnalytic.purchase_invoice_id")
    purchase_workflows = relationship("PurchaseWorkflow", foreign_keys="PurchaseWorkflow.purchase_invoice_id")
    purchase_documents = relationship("PurchaseDocument", foreign_keys="PurchaseDocument.purchase_invoice_id")
    purchase_audit_trails = relationship("PurchaseAuditTrail", foreign_keys="PurchaseAuditTrail.purchase_invoice_id")
    
    # Indian Localization Integration Relationships
    purchase_gst = relationship("PurchaseGST", foreign_keys="PurchaseGST.purchase_invoice_id")
    purchase_e_invoice = relationship("PurchaseEInvoice", foreign_keys="PurchaseEInvoice.purchase_invoice_id")
    purchase_e_waybill = relationship("PurchaseEWaybill", foreign_keys="PurchaseEWaybill.purchase_invoice_id")
    purchase_tds = relationship("PurchaseTDS", foreign_keys="PurchaseTDS.purchase_invoice_id")
    purchase_tcs = relationship("PurchaseTCS", foreign_keys="PurchaseTCS.purchase_invoice_id")
    purchase_indian_banking = relationship("PurchaseIndianBanking", foreign_keys="PurchaseIndianBanking.purchase_invoice_id")
    purchase_indian_geography = relationship("PurchaseIndianGeography", foreign_keys="PurchaseIndianGeography.purchase_invoice_id")
    
    # Advanced Features Integration Relationships
    purchase_advanced_workflows = relationship("PurchaseAdvancedWorkflow", foreign_keys="PurchaseAdvancedWorkflow.purchase_invoice_id")
    purchase_document_management = relationship("PurchaseDocumentManagement", foreign_keys="PurchaseDocumentManagement.purchase_invoice_id")
    purchase_advanced_reporting = relationship("PurchaseAdvancedReporting", foreign_keys="PurchaseAdvancedReporting.purchase_invoice_id")
    purchase_audit_trail_advanced = relationship("PurchaseAuditTrailAdvanced", foreign_keys="PurchaseAuditTrailAdvanced.purchase_invoice_id")
    purchase_notifications = relationship("PurchaseNotification", foreign_keys="PurchaseNotification.purchase_invoice_id")
    purchase_dashboards = relationship("PurchaseDashboard", foreign_keys="PurchaseDashboard.purchase_invoice_id")
    
    def __repr__(self):
        return f"<PurchaseInvoice(number='{self.invoice_number}', supplier_id={self.supplier_id})>"

class PurchaseInvoiceItem(BaseModel):
    """Individual items in purchase invoice with Indian GST compliance"""
    __tablename__ = "purchase_invoice_item"
    
    invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=True)
    
    # Basic Item Information
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    subtotal_amount = Column(Numeric(10, 2), nullable=False)  # Amount before GST
    
    # HSN/SAC Information
    hsn_code = Column(String(8), nullable=True)
    sac_code = Column(String(6), nullable=True)
    
    # GST Information
    gst_rate = Column(Numeric(5, 2), nullable=True)
    cgst_rate = Column(Numeric(5, 2), nullable=True)
    cgst_amount = Column(Numeric(10, 2), nullable=True)
    sgst_rate = Column(Numeric(5, 2), nullable=True)
    sgst_amount = Column(Numeric(10, 2), nullable=True)
    igst_rate = Column(Numeric(5, 2), nullable=True)
    igst_amount = Column(Numeric(10, 2), nullable=True)
    cess_rate = Column(Numeric(5, 2), nullable=True)
    cess_amount = Column(Numeric(10, 2), nullable=True)
    total_gst_amount = Column(Numeric(10, 2), nullable=True)
    total_amount = Column(Numeric(10, 2), nullable=False)  # Final amount including GST
    
    # Reverse Charge Information
    reverse_charge_applicable = Column(Boolean, default=False)
    reverse_charge_amount = Column(Numeric(10, 2), default=0)
    
    # Unit of Measure
    unit_of_measure = Column(String(10), nullable=True)  # NOS, KGS, LTR, etc.
    
    # Relationships
    invoice_record = relationship("PurchaseInvoice", back_populates="invoice_items")
    item = relationship("Item")
    variant = relationship("InventoryVariant")
    
    def __repr__(self):
        return f"<PurchaseInvoiceItem(item_id={self.item_id}, quantity={self.quantity})>"
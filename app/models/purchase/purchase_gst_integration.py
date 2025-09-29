# backend/app/models/purchase/purchase_gst_integration.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from .base import BaseModel

class GSTTaxType(PyEnum):
    """GST Tax Types"""
    CGST = "CGST"  # Central GST
    SGST = "SGST"  # State GST
    IGST = "IGST"  # Integrated GST
    CESS = "CESS"  # Cess
    UTGST = "UTGST"  # Union Territory GST

class PlaceOfSupplyType(PyEnum):
    """Place of Supply Types"""
    INTRA_STATE = "intra_state"  # Within same state
    INTER_STATE = "inter_state"  # Between different states
    EXPORT = "export"  # Export of goods/services
    IMPORT = "import"  # Import of goods/services

class PurchaseGST(BaseModel):
    """Link Purchases to GST Tax Structure"""
    __tablename__ = "purchase_gst"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=True)
    purchase_return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=True)
    
    # GST Reference
    gst_slab_id = Column(Integer, ForeignKey('gst_slab.id'), nullable=False)
    hsn_sac_code = Column(String(10), nullable=True)
    
    # Place of Supply
    place_of_supply = Column(Enum(PlaceOfSupplyType), nullable=False)
    supplier_state_code = Column(String(2), nullable=True)
    recipient_state_code = Column(String(2), nullable=True)
    
    # GST Amounts
    taxable_amount = Column(Numeric(15, 2), nullable=False)
    cgst_rate = Column(Numeric(5, 2), nullable=True)
    cgst_amount = Column(Numeric(15, 2), default=0)
    sgst_rate = Column(Numeric(5, 2), nullable=True)
    sgst_amount = Column(Numeric(15, 2), default=0)
    igst_rate = Column(Numeric(5, 2), nullable=True)
    igst_amount = Column(Numeric(15, 2), default=0)
    cess_rate = Column(Numeric(5, 2), nullable=True)
    cess_amount = Column(Numeric(15, 2), default=0)
    total_gst_amount = Column(Numeric(15, 2), default=0)
    
    # Reverse Charge
    reverse_charge_applicable = Column(Boolean, default=False)
    reverse_charge_amount = Column(Numeric(15, 2), default=0)
    reverse_charge_section = Column(String(10), nullable=True)
    
    # Additional Information
    gst_in_voice = Column(String(15), nullable=True)  # Supplier GSTIN
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional GST data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    purchase_order = relationship("PurchaseOrder")
    purchase_return = relationship("PurchaseReturn")
    gst_slab = relationship("GSTSlab")
    
    def __repr__(self):
        return f"<PurchaseGST(purchase_id={self.purchase_invoice_id}, gst_amount={self.total_gst_amount})>"

class PurchaseEInvoice(BaseModel):
    """Link Purchases to E-invoicing"""
    __tablename__ = "purchase_e_invoice"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    
    # E-invoice Reference
    e_invoice_id = Column(Integer, ForeignKey('e_invoice.id'), nullable=True)
    
    # E-invoice Details
    irn = Column(String(64), nullable=True)  # Invoice Reference Number
    qr_code = Column(Text, nullable=True)  # QR code data
    e_invoice_status = Column(String(20), default='pending')  # pending, generated, uploaded, accepted, rejected
    ack_no = Column(String(50), nullable=True)  # Acknowledgment number
    ack_date = Column(DateTime, nullable=True)  # Acknowledgment date
    
    # Government Portal Integration
    portal_upload_status = Column(String(20), default='pending')  # pending, uploaded, failed
    portal_upload_date = Column(DateTime, nullable=True)
    portal_response = Column(JSON, nullable=True)  # Portal response data
    
    # Additional Information
    generation_attempts = Column(Integer, default=0)
    last_generation_attempt = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional E-invoice data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    e_invoice = relationship("EInvoice")
    
    def __repr__(self):
        return f"<PurchaseEInvoice(purchase_id={self.purchase_invoice_id}, irn='{self.irn}')>"

class PurchaseEWaybill(BaseModel):
    """Link Purchases to E-waybill"""
    __tablename__ = "purchase_e_waybill"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=True)
    
    # E-waybill Reference
    e_waybill_id = Column(Integer, ForeignKey('e_waybill.id'), nullable=True)
    
    # E-waybill Details
    eway_bill_no = Column(String(50), nullable=True)
    eway_bill_date = Column(Date, nullable=True)
    eway_bill_valid_upto = Column(DateTime, nullable=True)
    eway_bill_status = Column(String(20), default='pending')  # pending, generated, active, expired, cancelled
    
    # Transportation Details
    transport_mode = Column(String(50), nullable=True)  # Road, Rail, Air, Ship
    vehicle_number = Column(String(20), nullable=True)
    driver_name = Column(String(100), nullable=True)
    driver_phone = Column(String(20), nullable=True)
    driver_license = Column(String(50), nullable=True)
    
    # Distance and Route
    distance_km = Column(Numeric(10, 2), nullable=True)
    route_description = Column(Text, nullable=True)
    
    # Government Portal Integration
    portal_upload_status = Column(String(20), default='pending')  # pending, uploaded, failed
    portal_upload_date = Column(DateTime, nullable=True)
    portal_response = Column(JSON, nullable=True)  # Portal response data
    
    # Additional Information
    generation_attempts = Column(Integer, default=0)
    last_generation_attempt = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional E-waybill data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    purchase_order = relationship("PurchaseOrder")
    e_waybill = relationship("EWaybill")
    
    def __repr__(self):
        return f"<PurchaseEWaybill(purchase_id={self.purchase_invoice_id}, eway_no='{self.eway_bill_no}')>"

class PurchaseTDS(BaseModel):
    """Link Purchases to TDS"""
    __tablename__ = "purchase_tds"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    
    # TDS Reference
    tds_id = Column(Integer, ForeignKey('tds.id'), nullable=True)
    
    # TDS Details
    tds_applicable = Column(Boolean, default=False)
    tds_rate = Column(Numeric(5, 2), nullable=True)
    tds_amount = Column(Numeric(15, 2), default=0)
    tds_section = Column(String(10), nullable=True)
    tds_certificate_no = Column(String(50), nullable=True)
    tds_certificate_date = Column(Date, nullable=True)
    
    # TDS Deduction Details
    tds_deducted_by = Column(String(100), nullable=True)  # Deductor name
    tds_deducted_date = Column(Date, nullable=True)
    tds_deposited_date = Column(Date, nullable=True)
    tds_challan_no = Column(String(50), nullable=True)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional TDS data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    tds = relationship("TDS")
    
    def __repr__(self):
        return f"<PurchaseTDS(purchase_id={self.purchase_invoice_id}, tds_amount={self.tds_amount})>"

class PurchaseTCS(BaseModel):
    """Link Purchases to TCS"""
    __tablename__ = "purchase_tcs"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    
    # TCS Reference
    tcs_id = Column(Integer, ForeignKey('tcs.id'), nullable=True)
    
    # TCS Details
    tcs_applicable = Column(Boolean, default=False)
    tcs_rate = Column(Numeric(5, 2), nullable=True)
    tcs_amount = Column(Numeric(15, 2), default=0)
    tcs_section = Column(String(10), nullable=True)
    tcs_certificate_no = Column(String(50), nullable=True)
    tcs_certificate_date = Column(Date, nullable=True)
    
    # TCS Collection Details
    tcs_collected_by = Column(String(100), nullable=True)  # Collector name
    tcs_collected_date = Column(Date, nullable=True)
    tcs_deposited_date = Column(Date, nullable=True)
    tcs_challan_no = Column(String(50), nullable=True)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional TCS data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    tcs = relationship("TCS")
    
    def __repr__(self):
        return f"<PurchaseTCS(purchase_id={self.purchase_invoice_id}, tcs_amount={self.tcs_amount})>"

class PurchaseIndianBanking(BaseModel):
    """Link Purchases to Indian Banking"""
    __tablename__ = "purchase_indian_banking"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    
    # Payment Reference
    payment_id = Column(Integer, ForeignKey('payment.id'), nullable=True)
    
    # Indian Payment Methods
    payment_method_type = Column(String(50), nullable=True)  # UPI, NEFT, RTGS, Cheque, Cash
    upi_id = Column(String(100), nullable=True)
    upi_transaction_id = Column(String(100), nullable=True)
    neft_reference = Column(String(50), nullable=True)
    rtgs_reference = Column(String(50), nullable=True)
    cheque_number = Column(String(50), nullable=True)
    cheque_date = Column(Date, nullable=True)
    bank_name = Column(String(100), nullable=True)
    bank_branch = Column(String(100), nullable=True)
    
    # Digital Wallet Integration
    wallet_provider = Column(String(50), nullable=True)  # Paytm, PhonePe, Google Pay
    wallet_transaction_id = Column(String(100), nullable=True)
    wallet_reference = Column(String(100), nullable=True)
    
    # Additional Information
    payment_status = Column(String(20), default='pending')  # pending, completed, failed
    payment_reference = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional banking data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    payment = relationship("Payment")
    
    def __repr__(self):
        return f"<PurchaseIndianBanking(purchase_id={self.purchase_invoice_id}, method='{self.payment_method_type}')>"

class PurchaseIndianGeography(BaseModel):
    """Link Purchases to Indian Geography"""
    __tablename__ = "purchase_indian_geography"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=True)
    
    # Geography References
    supplier_state_id = Column(Integer, ForeignKey('indian_state.id'), nullable=True)
    supplier_city_id = Column(Integer, ForeignKey('indian_city.id'), nullable=True)
    supplier_pincode_id = Column(Integer, ForeignKey('indian_pincode.id'), nullable=True)
    recipient_state_id = Column(Integer, ForeignKey('indian_state.id'), nullable=True)
    recipient_city_id = Column(Integer, ForeignKey('indian_city.id'), nullable=True)
    recipient_pincode_id = Column(Integer, ForeignKey('indian_pincode.id'), nullable=True)
    
    # Address Details
    supplier_address = Column(Text, nullable=True)
    recipient_address = Column(Text, nullable=True)
    delivery_address = Column(Text, nullable=True)
    
    # Distance Calculation
    distance_km = Column(Numeric(10, 2), nullable=True)
    estimated_delivery_days = Column(Integer, nullable=True)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional geography data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    purchase_order = relationship("PurchaseOrder")
    supplier_state = relationship("IndianState", foreign_keys=[supplier_state_id])
    supplier_city = relationship("IndianCity", foreign_keys=[supplier_city_id])
    supplier_pincode = relationship("IndianPincode", foreign_keys=[supplier_pincode_id])
    recipient_state = relationship("IndianState", foreign_keys=[recipient_state_id])
    recipient_city = relationship("IndianCity", foreign_keys=[recipient_city_id])
    recipient_pincode = relationship("IndianPincode", foreign_keys=[recipient_pincode_id])
    
    def __repr__(self):
        return f"<PurchaseIndianGeography(purchase_id={self.purchase_invoice_id}, distance={self.distance_km}km)>"
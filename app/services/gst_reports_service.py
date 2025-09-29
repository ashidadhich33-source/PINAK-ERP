# backend/app/services/gst_reports_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime, date
import pandas as pd
import io
import logging

from ..models.company import Company
from ..models.enhanced_sales import SalesInvoice, SalesInvoiceItem
from ..models.purchase import PurchaseBill, PurchaseBillItem
from ..services.gst_calculation_service import gst_calculation_service

logger = logging.getLogger(__name__)

class GSTReportsService:
    """Service class for GST reports and analytics"""
    
    def __init__(self):
        pass
    
    def generate_gst_summary_report(
        self, 
        db: Session, 
        company_id: int,
        from_date: date,
        to_date: date
    ) -> Dict:
        """Generate comprehensive GST summary report"""
        
        # Get company details
        company = db.query(Company).filter(Company.id == company_id).first()
        
        # Calculate GST liability
        liability = gst_calculation_service.calculate_gst_liability(
            db, company_id, from_date, to_date
        )
        
        # Get sales summary by GST rate
        sales_by_rate = db.query(
            SalesInvoiceItem.gst_rate,
            func.sum(SalesInvoiceItem.line_total).label('total_amount'),
            func.sum(SalesInvoiceItem.cgst_amount).label('cgst_amount'),
            func.sum(SalesInvoiceItem.sgst_amount).label('sgst_amount'),
            func.sum(SalesInvoiceItem.igst_amount).label('igst_amount'),
            func.count(SalesInvoiceItem.id).label('invoice_count')
        ).join(
            SalesInvoice, SalesInvoiceItem.invoice_id == SalesInvoice.id
        ).filter(
            SalesInvoice.company_id == company_id,
            SalesInvoice.invoice_date >= from_date,
            SalesInvoice.invoice_date <= to_date,
            SalesInvoice.status != 'cancelled'
        ).group_by(SalesInvoiceItem.gst_rate).all()
        
        # Get purchase summary by GST rate
        purchase_by_rate = db.query(
            PurchaseBillItem.gst_rate,
            func.sum(PurchaseBillItem.line_total).label('total_amount'),
            func.sum(PurchaseBillItem.cgst_amount).label('cgst_amount'),
            func.sum(PurchaseBillItem.sgst_amount).label('sgst_amount'),
            func.sum(PurchaseBillItem.igst_amount).label('igst_amount'),
            func.count(PurchaseBillItem.id).label('bill_count')
        ).join(
            PurchaseBill, PurchaseBillItem.bill_id == PurchaseBill.id
        ).filter(
            PurchaseBill.company_id == company_id,
            PurchaseBill.bill_date >= from_date,
            PurchaseBill.bill_date <= to_date,
            PurchaseBill.status != 'cancelled'
        ).group_by(PurchaseBillItem.gst_rate).all()
        
        return {
            "company_details": {
                "name": company.name,
                "gst_number": company.gst_number,
                "address": f"{company.address_line1}, {company.city}, {company.state}"
            },
            "report_period": {
                "from_date": from_date,
                "to_date": to_date
            },
            "gst_liability": liability,
            "sales_summary": [
                {
                    "gst_rate": sale.gst_rate,
                    "total_amount": sale.total_amount,
                    "cgst_amount": sale.cgst_amount,
                    "sgst_amount": sale.sgst_amount,
                    "igst_amount": sale.igst_amount,
                    "invoice_count": sale.invoice_count
                }
                for sale in sales_by_rate
            ],
            "purchase_summary": [
                {
                    "gst_rate": purchase.gst_rate,
                    "total_amount": purchase.total_amount,
                    "cgst_amount": purchase.cgst_amount,
                    "sgst_amount": purchase.sgst_amount,
                    "igst_amount": purchase.igst_amount,
                    "bill_count": purchase.bill_count
                }
                for purchase in purchase_by_rate
            ]
        }
    
    def generate_gst_rate_wise_report(
        self, 
        db: Session, 
        company_id: int,
        from_date: date,
        to_date: date
    ) -> Dict:
        """Generate GST rate-wise detailed report"""
        
        # Get all GST rates used in the period
        sales_rates = db.query(SalesInvoiceItem.gst_rate).join(
            SalesInvoice, SalesInvoiceItem.invoice_id == SalesInvoice.id
        ).filter(
            SalesInvoice.company_id == company_id,
            SalesInvoice.invoice_date >= from_date,
            SalesInvoice.invoice_date <= to_date,
            SalesInvoice.status != 'cancelled'
        ).distinct().all()
        
        purchase_rates = db.query(PurchaseBillItem.gst_rate).join(
            PurchaseBill, PurchaseBillItem.bill_id == PurchaseBill.id
        ).filter(
            PurchaseBill.company_id == company_id,
            PurchaseBill.bill_date >= from_date,
            PurchaseBill.bill_date <= to_date,
            PurchaseBill.status != 'cancelled'
        ).distinct().all()
        
        all_rates = set([rate.gst_rate for rate in sales_rates + purchase_rates])
        
        rate_wise_data = []
        
        for rate in sorted(all_rates):
            # Sales data for this rate
            sales_data = db.query(
                func.sum(SalesInvoiceItem.line_total).label('total_amount'),
                func.sum(SalesInvoiceItem.cgst_amount).label('cgst_amount'),
                func.sum(SalesInvoiceItem.sgst_amount).label('sgst_amount'),
                func.sum(SalesInvoiceItem.igst_amount).label('igst_amount'),
                func.count(SalesInvoiceItem.id).label('transaction_count')
            ).join(
                SalesInvoice, SalesInvoiceItem.invoice_id == SalesInvoice.id
            ).filter(
                SalesInvoice.company_id == company_id,
                SalesInvoice.invoice_date >= from_date,
                SalesInvoice.invoice_date <= to_date,
                SalesInvoice.status != 'cancelled',
                SalesInvoiceItem.gst_rate == rate
            ).first()
            
            # Purchase data for this rate
            purchase_data = db.query(
                func.sum(PurchaseBillItem.line_total).label('total_amount'),
                func.sum(PurchaseBillItem.cgst_amount).label('cgst_amount'),
                func.sum(PurchaseBillItem.sgst_amount).label('sgst_amount'),
                func.sum(PurchaseBillItem.igst_amount).label('igst_amount'),
                func.count(PurchaseBillItem.id).label('transaction_count')
            ).join(
                PurchaseBill, PurchaseBillItem.bill_id == PurchaseBill.id
            ).filter(
                PurchaseBill.company_id == company_id,
                PurchaseBill.bill_date >= from_date,
                PurchaseBill.bill_date <= to_date,
                PurchaseBill.status != 'cancelled',
                PurchaseBillItem.gst_rate == rate
            ).first()
            
            rate_wise_data.append({
                "gst_rate": rate,
                "sales": {
                    "total_amount": sales_data.total_amount or Decimal('0'),
                    "cgst_amount": sales_data.cgst_amount or Decimal('0'),
                    "sgst_amount": sales_data.sgst_amount or Decimal('0'),
                    "igst_amount": sales_data.igst_amount or Decimal('0'),
                    "transaction_count": sales_data.transaction_count or 0
                },
                "purchase": {
                    "total_amount": purchase_data.total_amount or Decimal('0'),
                    "cgst_amount": purchase_data.cgst_amount or Decimal('0'),
                    "sgst_amount": purchase_data.sgst_amount or Decimal('0'),
                    "igst_amount": purchase_data.igst_amount or Decimal('0'),
                    "transaction_count": purchase_data.transaction_count or 0
                },
                "net_liability": {
                    "cgst": (sales_data.cgst_amount or Decimal('0')) - (purchase_data.cgst_amount or Decimal('0')),
                    "sgst": (sales_data.sgst_amount or Decimal('0')) - (purchase_data.sgst_amount or Decimal('0')),
                    "igst": (sales_data.igst_amount or Decimal('0')) - (purchase_data.igst_amount or Decimal('0'))
                }
            })
        
        return {
            "report_period": {
                "from_date": from_date,
                "to_date": to_date
            },
            "rate_wise_data": rate_wise_data
        }
    
    def generate_gst_monthly_report(
        self, 
        db: Session, 
        company_id: int,
        year: int,
        month: Optional[int] = None
    ) -> Dict:
        """Generate GST monthly report"""
        
        # Get company details
        company = db.query(Company).filter(Company.id == company_id).first()
        
        if month:
            # Single month report
            from_date = date(year, month, 1)
            if month == 12:
                to_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                to_date = date(year, month + 1, 1) - timedelta(days=1)
            
            return self.generate_gst_summary_report(db, company_id, from_date, to_date)
        else:
            # Yearly report with monthly breakdown
            monthly_data = []
            
            for month_num in range(1, 13):
                from_date = date(year, month_num, 1)
                if month_num == 12:
                    to_date = date(year + 1, 1, 1) - timedelta(days=1)
                else:
                    to_date = date(year, month_num + 1, 1) - timedelta(days=1)
                
                month_data = self.generate_gst_summary_report(db, company_id, from_date, to_date)
                monthly_data.append({
                    "month": month_num,
                    "month_name": from_date.strftime("%B"),
                    "data": month_data
                })
            
            return {
                "company_details": {
                    "name": company.name,
                    "gst_number": company.gst_number
                },
                "year": year,
                "monthly_data": monthly_data
            }
    
    def generate_gst_return_excel(
        self, 
        db: Session, 
        company_id: int,
        from_date: date,
        to_date: date
    ) -> bytes:
        """Generate GST return data in Excel format"""
        
        # Get GST return data
        return_data = gst_calculation_service.generate_gst_return_data(
            db, company_id, from_date, to_date
        )
        
        # Create Excel file
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Company details sheet
            company_df = pd.DataFrame([return_data['company_details']])
            company_df.to_excel(writer, sheet_name='Company Details', index=False)
            
            # Sales data sheet
            if return_data['sales_data']:
                sales_df = pd.DataFrame(return_data['sales_data'])
                sales_df.to_excel(writer, sheet_name='Sales Data', index=False)
            
            # Purchase data sheet
            if return_data['purchase_data']:
                purchase_df = pd.DataFrame(return_data['purchase_data'])
                purchase_df.to_excel(writer, sheet_name='Purchase Data', index=False)
        
        output.seek(0)
        return output.getvalue()
    
    def generate_gst_liability_excel(
        self, 
        db: Session, 
        company_id: int,
        from_date: date,
        to_date: date
    ) -> bytes:
        """Generate GST liability report in Excel format"""
        
        # Get GST summary report
        summary_data = self.generate_gst_summary_report(db, company_id, from_date, to_date)
        
        # Create Excel file
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Summary sheet
            summary_df = pd.DataFrame([{
                "Company": summary_data['company_details']['name'],
                "GST Number": summary_data['company_details']['gst_number'],
                "Period": f"{from_date} to {to_date}",
                "Total CGST Liability": summary_data['gst_liability']['net_liability']['cgst'],
                "Total SGST Liability": summary_data['gst_liability']['net_liability']['sgst'],
                "Total IGST Liability": summary_data['gst_liability']['net_liability']['igst'],
                "Total Liability": summary_data['gst_liability']['net_liability']['total']
            }])
            summary_df.to_excel(writer, sheet_name='GST Summary', index=False)
            
            # Sales summary sheet
            if summary_data['sales_summary']:
                sales_df = pd.DataFrame(summary_data['sales_summary'])
                sales_df.to_excel(writer, sheet_name='Sales Summary', index=False)
            
            # Purchase summary sheet
            if summary_data['purchase_summary']:
                purchase_df = pd.DataFrame(summary_data['purchase_summary'])
                purchase_df.to_excel(writer, sheet_name='Purchase Summary', index=False)
        
        output.seek(0)
        return output.getvalue()
    
    def get_gst_compliance_status(
        self, 
        db: Session, 
        company_id: int,
        from_date: date,
        to_date: date
    ) -> Dict:
        """Get GST compliance status for the period"""
        
        # Get GST liability
        liability = gst_calculation_service.calculate_gst_liability(
            db, company_id, from_date, to_date
        )
        
        # Check for any GST-related issues
        issues = []
        
        # Check for negative GST liability (refund situation)
        if liability['net_liability']['total'] < 0:
            issues.append({
                "type": "refund_eligible",
                "message": "You are eligible for GST refund",
                "amount": abs(liability['net_liability']['total'])
            })
        
        # Check for high GST liability
        if liability['net_liability']['total'] > 100000:  # 1 lakh
            issues.append({
                "type": "high_liability",
                "message": "High GST liability detected",
                "amount": liability['net_liability']['total']
            })
        
        # Check for missing GST numbers in transactions
        # This would require additional implementation
        
        return {
            "period": {
                "from_date": from_date,
                "to_date": to_date
            },
            "gst_liability": liability,
            "compliance_status": "compliant" if not issues else "issues_found",
            "issues": issues,
            "recommendations": [
                "Ensure all transactions have proper GST rates",
                "Verify GST numbers of customers and suppliers",
                "File GST returns on time",
                "Maintain proper documentation"
            ]
        }

# Global service instance
gst_reports_service = GSTReportsService()
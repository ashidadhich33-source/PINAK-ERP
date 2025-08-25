"""
PDF Generation Service for Invoices and Reports
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
from datetime import datetime
from decimal import Decimal
from typing import Optional

class PDFService:
    """Service for generating PDF documents"""
    
    @classmethod
    def generate_invoice_pdf(cls, sale) -> bytes:
        """
        Generate invoice PDF for a sale
        Returns PDF content as bytes
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#333333'),
            alignment=TA_CENTER
        )
        
        # Company Header
        elements.append(Paragraph("YOUR COMPANY NAME", title_style))
        elements.append(Spacer(1, 12))
        
        # Invoice Details
        invoice_data = [
            ['Invoice No:', sale.bill_no, 'Date:', sale.bill_date.strftime('%d-%m-%Y')],
            ['Customer:', sale.customer.name if sale.customer else 'Walk-in', 
             'Mobile:', sale.customer_mobile or '']
        ]
        
        invoice_table = Table(invoice_data, colWidths=[2*inch, 2*inch, 2*inch, 2*inch])
        invoice_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(invoice_table)
        elements.append(Spacer(1, 20))
        
        # Items Table
        items_data = [['Item', 'Qty', 'MRP', 'Disc%', 'Amount']]
        
        for item in sale.items:
            items_data.append([
                f"{item.style_code} - {item.size}",
                str(item.qty),
                f"₹{item.mrp_incl:.2f}",
                f"{item.disc_pct:.1f}%",
                f"₹{item.line_inclusive:.2f}"
            ])
        
        items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1*inch, 1.5*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(items_table)
        elements.append(Spacer(1, 20))
        
        # Totals
        totals_data = [
            ['', '', '', 'Gross Total:', f"₹{sale.gross_incl:.2f}"],
            ['', '', '', 'Discount:', f"₹{sale.discount_incl:.2f}"],
            ['', '', '', 'Net Amount:', f"₹{sale.final_payable:.2f}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (3, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (3, -1), (-1, -1), 14),
        ]))
        
        elements.append(totals_table)
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
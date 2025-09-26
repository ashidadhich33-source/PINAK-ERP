# backend/app/services/gst_service.py
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class GSTService:
    """Service class for GST (Goods and Services Tax) calculations"""
    
    def __init__(self):
        # GST rates in India
        self.valid_gst_rates = [0, 3, 5, 12, 18, 28]
        self.round_to_places = 2
    
    def round_amount(self, amount: Decimal) -> Decimal:
        """Round amount to 2 decimal places using banker's rounding"""
        return amount.quantize(Decimal(f'0.{"0" * self.round_to_places}'), rounding=ROUND_HALF_UP)
    
    def is_inter_state_transaction(self, seller_state: str, buyer_state: str) -> bool:
        """Check if transaction is inter-state (for IGST vs CGST+SGST)"""
        if not seller_state or not buyer_state:
            return False
        return seller_state.upper().strip() != buyer_state.upper().strip()
    
    def calculate_tax_inclusive_amount(self, inclusive_amount: Decimal, tax_rate: Decimal) -> Dict[str, Decimal]:
        """Calculate tax from tax-inclusive amount"""
        if tax_rate <= 0:
            return {
                'base_amount': inclusive_amount,
                'tax_amount': Decimal('0'),
                'total_amount': inclusive_amount
            }
        
        # Formula: Base = Inclusive Amount / (1 + Tax Rate/100)
        tax_multiplier = Decimal('1') + (tax_rate / Decimal('100'))
        base_amount = self.round_amount(inclusive_amount / tax_multiplier)
        tax_amount = self.round_amount(inclusive_amount - base_amount)
        
        return {
            'base_amount': base_amount,
            'tax_amount': tax_amount,
            'total_amount': inclusive_amount
        }
    
    def calculate_tax_exclusive_amount(self, base_amount: Decimal, tax_rate: Decimal) -> Dict[str, Decimal]:
        """Calculate tax on tax-exclusive amount"""
        if tax_rate <= 0:
            return {
                'base_amount': base_amount,
                'tax_amount': Decimal('0'),
                'total_amount': base_amount
            }
        
        tax_amount = self.round_amount(base_amount * (tax_rate / Decimal('100')))
        total_amount = base_amount + tax_amount
        
        return {
            'base_amount': base_amount,
            'tax_amount': tax_amount,
            'total_amount': total_amount
        }
    
    def calculate_gst_breakdown(
        self, 
        base_amount: Decimal, 
        gst_rate: Decimal, 
        is_registered_buyer: bool = True,
        seller_state: str = "Maharashtra",
        buyer_state: Optional[str] = None
    ) -> Dict[str, Decimal]:
        """
        Calculate detailed GST breakdown (CGST, SGST, IGST)
        
        Args:
            base_amount: Taxable amount
            gst_rate: GST rate (e.g., 18.00 for 18%)
            is_registered_buyer: Whether buyer is GST registered
            seller_state: State of seller
            buyer_state: State of buyer (if None, assumes same as seller)
        """
        
        if gst_rate <= 0:
            return {
                'gst_rate': Decimal('0'),
                'cgst_rate': Decimal('0'),
                'sgst_rate': Decimal('0'),
                'igst_rate': Decimal('0'),
                'cgst_amount': Decimal('0'),
                'sgst_amount': Decimal('0'),
                'igst_amount': Decimal('0'),
                'total_tax': Decimal('0'),
                'taxable_amount': base_amount,
                'total_amount': base_amount
            }
        
        # Determine if inter-state transaction
        if buyer_state is None:
            buyer_state = seller_state
        
        is_inter_state = self.is_inter_state_transaction(seller_state, buyer_state)
        
        if is_inter_state:
            # Inter-state: IGST only
            igst_rate = gst_rate
            cgst_rate = Decimal('0')
            sgst_rate = Decimal('0')
        else:
            # Intra-state: CGST + SGST (each is half of total GST)
            igst_rate = Decimal('0')
            cgst_rate = gst_rate / Decimal('2')
            sgst_rate = gst_rate / Decimal('2')
        
        # Calculate amounts
        cgst_amount = self.round_amount(base_amount * (cgst_rate / Decimal('100')))
        sgst_amount = self.round_amount(base_amount * (sgst_rate / Decimal('100')))
        igst_amount = self.round_amount(base_amount * (igst_rate / Decimal('100')))
        
        total_tax = cgst_amount + sgst_amount + igst_amount
        total_amount = base_amount + total_tax
        
        return {
            'gst_rate': gst_rate,
            'cgst_rate': cgst_rate,
            'sgst_rate': sgst_rate,
            'igst_rate': igst_rate,
            'cgst_amount': cgst_amount,
            'sgst_amount': sgst_amount,
            'igst_amount': igst_amount,
            'total_tax': total_tax,
            'taxable_amount': base_amount,
            'total_amount': total_amount,
            'is_inter_state': is_inter_state
        }
    
    def calculate_tax(
        self, 
        amount: Decimal, 
        tax_rate: Decimal, 
        is_registered_buyer: bool = True
    ) -> Dict[str, Decimal]:
        """Simple tax calculation (backward compatibility)"""
        return self.calculate_tax_exclusive_amount(amount, tax_rate)
    
    def reverse_calculate_tax(self, inclusive_amount: Decimal, tax_rate: Decimal) -> Dict[str, Decimal]:
        """Calculate base amount from tax-inclusive amount"""
        return self.calculate_tax_inclusive_amount(inclusive_amount, tax_rate)
    
    def validate_gst_number(self, gst_number: str) -> Dict[str, any]:
        """
        Validate GST number format and extract information
        GST format: GGSPPPPPPPPPCZZ
        GG = State code, S = Entity type, PPPPPPPPP = PAN, C = Check digit, ZZ = Entity number
        """
        if not gst_number or len(gst_number.strip()) == 0:
            return {'valid': True, 'message': 'GST number is optional'}
        
        gst = gst_number.strip().upper()
        
        # Basic length check
        if len(gst) != 15:
            return {'valid': False, 'message': 'GST number must be 15 characters'}
        
        # Check if all characters are alphanumeric
        if not gst.isalnum():
            return {'valid': False, 'message': 'GST number must contain only letters and numbers'}
        
        # Extract components
        state_code = gst[:2]
        entity_type = gst[2]
        pan_part = gst[3:12]
        check_digit = gst[12]
        entity_number = gst[13:15]
        
        # Validate state code (should be numeric)
        if not state_code.isdigit():
            return {'valid': False, 'message': 'Invalid state code in GST number'}
        
        state_code_num = int(state_code)
        if state_code_num < 1 or state_code_num > 37:
            return {'valid': False, 'message': 'Invalid state code in GST number'}
        
        # Basic PAN format check (5 letters + 4 digits)
        if not (pan_part[:5].isalpha() and pan_part[5:9].isdigit() and pan_part[9].isalpha()):
            return {'valid': False, 'message': 'Invalid PAN format in GST number'}
        
        return {
            'valid': True,
            'message': 'Valid GST number',
            'state_code': state_code,
            'entity_type': entity_type,
            'pan': pan_part,
            'check_digit': check_digit,
            'entity_number': entity_number
        }
    
    def get_hsn_tax_rate(self, hsn_code: str) -> Decimal:
        """
        Get GST rate for HSN code (simplified mapping)
        In real implementation, this would query a comprehensive HSN database
        """
        hsn_tax_mapping = {
            # Common HSN codes and their GST rates
            '1001': Decimal('0'),      # Wheat
            '1006': Decimal('0'),      # Rice
            '1701': Decimal('0'),      # Cane sugar
            '2106': Decimal('18'),     # Food preparations
            '2203': Decimal('28'),     # Beer
            '3004': Decimal('12'),     # Medicines
            '4011': Decimal('28'),     # Tyres
            '6109': Decimal('12'),     # T-shirts
            '6203': Decimal('12'),     # Men's suits
            '6204': Decimal('12'),     # Women's suits
            '8471': Decimal('18'),     # Computers
            '8517': Decimal('18'),     # Mobile phones
            '8703': Decimal('28'),     # Motor cars
            '9403': Decimal('18'),     # Furniture
        }
        
        if hsn_code and len(hsn_code) >= 4:
            # Try exact match first
            if hsn_code in hsn_tax_mapping:
                return hsn_tax_mapping[hsn_code]
            
            # Try first 4 digits
            hsn_prefix = hsn_code[:4]
            if hsn_prefix in hsn_tax_mapping:
                return hsn_tax_mapping[hsn_prefix]
        
        # Default GST rate if HSN not found
        return Decimal('18')
    
    def calculate_invoice_totals(self, line_items: list, discount_amount: Decimal = Decimal('0')) -> Dict[str, Decimal]:
        """
        Calculate invoice totals with GST breakdown
        
        Args:
            line_items: List of items with 'taxable_amount' and 'gst_rate'
            discount_amount: Total discount on invoice
        """
        
        subtotal = Decimal('0')
        total_cgst = Decimal('0')
        total_sgst = Decimal('0')
        total_igst = Decimal('0')
        total_tax = Decimal('0')
        
        tax_wise_breakdown = {}  # Group by tax rates
        
        for item in line_items:
            taxable_amount = item.get('taxable_amount', Decimal('0'))
            gst_rate = item.get('gst_rate', Decimal('0'))
            buyer_state = item.get('buyer_state')
            seller_state = item.get('seller_state', 'Maharashtra')
            
            subtotal += taxable_amount
            
            if gst_rate > 0:
                gst_breakdown = self.calculate_gst_breakdown(
                    taxable_amount, gst_rate, True, seller_state, buyer_state
                )
                
                total_cgst += gst_breakdown['cgst_amount']
                total_sgst += gst_breakdown['sgst_amount'] 
                total_igst += gst_breakdown['igst_amount']
                total_tax += gst_breakdown['total_tax']
                
                # Group by tax rate for summary
                rate_key = f"{gst_rate}%"
                if rate_key not in tax_wise_breakdown:
                    tax_wise_breakdown[rate_key] = {
                        'rate': gst_rate,
                        'taxable_amount': Decimal('0'),
                        'cgst_amount': Decimal('0'),
                        'sgst_amount': Decimal('0'),
                        'igst_amount': Decimal('0'),
                        'total_tax': Decimal('0')
                    }
                
                tax_wise_breakdown[rate_key]['taxable_amount'] += taxable_amount
                tax_wise_breakdown[rate_key]['cgst_amount'] += gst_breakdown['cgst_amount']
                tax_wise_breakdown[rate_key]['sgst_amount'] += gst_breakdown['sgst_amount']
                tax_wise_breakdown[rate_key]['igst_amount'] += gst_breakdown['igst_amount']
                tax_wise_breakdown[rate_key]['total_tax'] += gst_breakdown['total_tax']
        
        # Calculate final amounts
        subtotal_after_discount = subtotal - discount_amount
        invoice_total = subtotal_after_discount + total_tax
        
        return {
            'subtotal': self.round_amount(subtotal),
            'discount_amount': self.round_amount(discount_amount),
            'taxable_amount': self.round_amount(subtotal_after_discount),
            'cgst_amount': self.round_amount(total_cgst),
            'sgst_amount': self.round_amount(total_sgst),
            'igst_amount': self.round_amount(total_igst),
            'total_tax': self.round_amount(total_tax),
            'invoice_total': self.round_amount(invoice_total),
            'tax_wise_breakdown': tax_wise_breakdown
        }
    
    def generate_gst_summary_report(self, transactions: list, period: str) -> Dict:
        """Generate GST summary report for a period"""
        
        total_sales = Decimal('0')
        total_purchases = Decimal('0')
        output_tax = Decimal('0')  # Tax collected on sales
        input_tax = Decimal('0')   # Tax paid on purchases
        
        tax_rate_wise = {}
        
        for transaction in transactions:
            amount = transaction.get('amount', Decimal('0'))
            tax_amount = transaction.get('tax_amount', Decimal('0'))
            transaction_type = transaction.get('type', 'sale')  # sale or purchase
            tax_rate = transaction.get('tax_rate', Decimal('0'))
            
            if transaction_type == 'sale':
                total_sales += amount
                output_tax += tax_amount
            else:
                total_purchases += amount
                input_tax += tax_amount
            
            # Rate-wise breakdown
            rate_key = f"{tax_rate}%"
            if rate_key not in tax_rate_wise:
                tax_rate_wise[rate_key] = {
                    'rate': tax_rate,
                    'sales_amount': Decimal('0'),
                    'sales_tax': Decimal('0'),
                    'purchase_amount': Decimal('0'),
                    'purchase_tax': Decimal('0')
                }
            
            if transaction_type == 'sale':
                tax_rate_wise[rate_key]['sales_amount'] += amount
                tax_rate_wise[rate_key]['sales_tax'] += tax_amount
            else:
                tax_rate_wise[rate_key]['purchase_amount'] += amount
                tax_rate_wise[rate_key]['purchase_tax'] += tax_amount
        
        # Calculate net tax liability
        net_tax_liability = output_tax - input_tax
        
        return {
            'period': period,
            'summary': {
                'total_sales': self.round_amount(total_sales),
                'total_purchases': self.round_amount(total_purchases),
                'output_tax': self.round_amount(output_tax),
                'input_tax': self.round_amount(input_tax),
                'net_tax_liability': self.round_amount(net_tax_liability),
            },
            'tax_rate_wise': tax_rate_wise,
            'generated_at': logger.info(f"GST summary generated for period: {period}")
        }
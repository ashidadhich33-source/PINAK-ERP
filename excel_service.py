import pandas as pd
from typing import List, Dict, Any, Tuple
import io
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

class ExcelService:
    """Service for Excel import/export operations"""
    
    @staticmethod
    def create_item_master_template() -> bytes:
        """Create Excel template for Item Master import"""
        columns = [
            'BARCODE', 'STYLE_CODE', 'COLOR', 'SIZE', 'MRP', 
            'HSN', 'BRAND', 'GENDER', 'CATEGORY', 'SUB_CATEGORY', 
            'PURCHASE_RATE', 'STATUS'
        ]
        
        # Create DataFrame with headers
        df = pd.DataFrame(columns=columns)
        
        # Add sample row
        sample_data = {
            'BARCODE': '1234567890123',
            'STYLE_CODE': 'STY001',
            'COLOR': 'Blue',
            'SIZE': 'M',
            'MRP': '999.00',
            'HSN': '6109',
            'BRAND': 'Brand Name',
            'GENDER': 'Male',
            'CATEGORY': 'Clothing',
            'SUB_CATEGORY': 'T-Shirts',
            'PURCHASE_RATE': '450.00',
            'STATUS': 'active'
        }
        df = pd.concat([df, pd.DataFrame([sample_data])], ignore_index=True)
        
        # Create Excel file with formatting
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Item_Master', index=False)
            
            # Get worksheet
            worksheet = writer.sheets['Item_Master']
            
            # Format headers
            for cell in worksheet[1]:
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                cell.font = Font(color="FFFFFF", bold=True)
                cell.alignment = Alignment(horizontal="center")
            
            # Adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 30)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        return output.read()
    
    @staticmethod
    def import_items_from_excel(file_content: bytes) -> Tuple[List[Dict], List[Dict]]:
        """
        Import items from Excel file
        Returns: (successful_items, errors)
        """
        try:
            df = pd.read_excel(io.BytesIO(file_content), sheet_name=0)
            
            # Normalize column names
            df.columns = df.columns.str.strip().str.upper()
            
            required_columns = ['BARCODE', 'STYLE_CODE']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return [], [{'error': f'Missing required columns: {", ".join(missing_columns)}'}]
            
            successful_items = []
            errors = []
            
            for idx, row in df.iterrows():
                try:
                    # Clean and validate data
                    item = {
                        'barcode': str(row.get('BARCODE', '')).strip(),
                        'style_code': str(row.get('STYLE_CODE', '')).strip(),
                        'color': str(row.get('COLOR', '')).strip() if pd.notna(row.get('COLOR')) else None,
                        'size': str(row.get('SIZE', '')).strip() if pd.notna(row.get('SIZE')) else None,
                        'mrp_incl': float(row.get('MRP', 0)) if pd.notna(row.get('MRP')) else None,
                        'hsn': str(row.get('HSN', '')).strip() if pd.notna(row.get('HSN')) else None,
                        'brand': str(row.get('BRAND', '')).strip() if pd.notna(row.get('BRAND')) else None,
                        'gender': str(row.get('GENDER', '')).strip() if pd.notna(row.get('GENDER')) else None,
                        'category': str(row.get('CATEGORY', '')).strip() if pd.notna(row.get('CATEGORY')) else None,
                        'sub_category': str(row.get('SUB_CATEGORY', '')).strip() if pd.notna(row.get('SUB_CATEGORY')) else None,
                        'purchase_rate_basic': float(row.get('PURCHASE_RATE', 0)) if pd.notna(row.get('PURCHASE_RATE')) else None,
                        'status': str(row.get('STATUS', 'active')).strip().lower()
                    }
                    
                    # Validate barcode
                    if not item['barcode']:
                        errors.append({'row': idx + 2, 'error': 'Barcode is required'})
                        continue
                    
                    if not item['style_code']:
                        errors.append({'row': idx + 2, 'error': 'Style Code is required'})
                        continue
                    
                    successful_items.append(item)
                    
                except Exception as e:
                    errors.append({'row': idx + 2, 'error': str(e)})
            
            return successful_items, errors
            
        except Exception as e:
            return [], [{'error': f'Failed to read Excel file: {str(e)}'}]
    
    @staticmethod
    def import_purchase_order(file_content: bytes) -> Tuple[List[Dict], List[Dict]]:
        """
        Import purchase order (BARCODE, QTY)
        Returns: (items, errors)
        """
        try:
            df = pd.read_excel(io.BytesIO(file_content), sheet_name=0)
            df.columns = df.columns.str.strip().str.upper()
            
            if 'BARCODE' not in df.columns or 'QTY' not in df.columns:
                return [], [{'error': 'Excel must have BARCODE and QTY columns'}]
            
            items = []
            errors = []
            
            for idx, row in df.iterrows():
                try:
                    barcode = str(row['BARCODE']).strip()
                    qty = int(row['QTY'])
                    
                    if not barcode:
                        errors.append({'row': idx + 2, 'error': 'Barcode is required'})
                        continue
                    
                    if qty <= 0:
                        errors.append({'row': idx + 2, 'error': 'Quantity must be positive'})
                        continue
                    
                    items.append({'barcode': barcode, 'qty': qty})
                    
                except ValueError:
                    errors.append({'row': idx + 2, 'error': 'Invalid quantity'})
                except Exception as e:
                    errors.append({'row': idx + 2, 'error': str(e)})
            
            return items, errors
            
        except Exception as e:
            return [], [{'error': f'Failed to read Excel file: {str(e)}'}]
#!/usr/bin/env python3
"""
Update Existing Bills Script
This script checks all existing purchase bills and marks those that have been used in POS or Sales
"""

import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.database import get_db
from app.models.purchase.purchase import PurchaseBill
from app.services.core.bill_modification_service import bill_modification_service


def update_existing_bills():
    """Check and update all existing purchase bills"""
    
    print("Updating Existing Purchase Bills")
    print("=" * 60)
    
    db = next(get_db())
    
    try:
        # Get all purchase bills
        bills = db.query(PurchaseBill).all()
        total_bills = len(bills)
        
        print(f"\nFound {total_bills} purchase bills to check")
        print("\nChecking usage...")
        
        locked_count = 0
        unlocked_count = 0
        error_count = 0
        
        for i, bill in enumerate(bills, 1):
            try:
                print(f"\r[{i}/{total_bills}] Checking bill: {bill.pb_no}...", end="")
                
                # Check usage
                usage_info = bill_modification_service.check_purchase_bill_usage(db, bill.id)
                
                if usage_info['modification_locked']:
                    locked_count += 1
                else:
                    unlocked_count += 1
                    
            except Exception as e:
                error_count += 1
                print(f"\n   ⚠ Error checking bill {bill.pb_no}: {str(e)}")
        
        print("\n\n" + "=" * 60)
        print("Update Summary:")
        print(f"   Total bills checked: {total_bills}")
        print(f"   Locked bills (used in POS/Sales): {locked_count}")
        print(f"   Unlocked bills (can be modified): {unlocked_count}")
        print(f"   Errors: {error_count}")
        print("=" * 60)
        
        if locked_count > 0:
            print(f"\n⚠️  {locked_count} bills are now locked and cannot be modified")
            print("   These bills have items that were used in POS or Sales transactions")
        
        if unlocked_count > 0:
            print(f"\n✅ {unlocked_count} bills can still be modified")
        
        print("\nUpdate completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Update failed: {str(e)}")
        raise
    finally:
        db.close()


def show_locked_bills():
    """Show all locked bills"""
    
    print("Locked Purchase Bills Report")
    print("=" * 60)
    
    db = next(get_db())
    
    try:
        # Get all locked bills
        locked_bills = db.query(PurchaseBill).filter(
            PurchaseBill.modification_locked == True
        ).all()
        
        if not locked_bills:
            print("\nNo locked bills found")
            return
        
        print(f"\nFound {len(locked_bills)} locked bills:\n")
        
        for bill in locked_bills:
            print(f"Bill: {bill.pb_no}")
            print(f"   Date: {bill.pb_date}")
            print(f"   Supplier: {bill.supplier.name if bill.supplier else 'N/A'}")
            print(f"   Amount: ₹{bill.grand_total}")
            print(f"   Used in POS: {bill.used_in_pos}")
            print(f"   Used in Sales: {bill.used_in_sales}")
            
            # Count locked items
            locked_items = [item for item in bill.items if item.modification_locked]
            print(f"   Locked items: {len(locked_items)}/{len(bill.items)}")
            print()
        
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Report failed: {str(e)}")
        raise
    finally:
        db.close()


def show_modifiable_bills():
    """Show all modifiable bills"""
    
    print("Modifiable Purchase Bills Report")
    print("=" * 60)
    
    db = next(get_db())
    
    try:
        # Get all unlocked bills
        modifiable_bills = db.query(PurchaseBill).filter(
            PurchaseBill.modification_locked == False
        ).all()
        
        if not modifiable_bills:
            print("\nNo modifiable bills found")
            return
        
        print(f"\nFound {len(modifiable_bills)} modifiable bills:\n")
        
        for bill in modifiable_bills:
            print(f"Bill: {bill.pb_no}")
            print(f"   Date: {bill.pb_date}")
            print(f"   Supplier: {bill.supplier.name if bill.supplier else 'N/A'}")
            print(f"   Amount: ₹{bill.grand_total}")
            print()
        
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Report failed: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Update existing bills with usage tracking')
    parser.add_argument('--show-locked', action='store_true', help='Show locked bills')
    parser.add_argument('--show-modifiable', action='store_true', help='Show modifiable bills')
    args = parser.parse_args()
    
    if args.show_locked:
        show_locked_bills()
    elif args.show_modifiable:
        show_modifiable_bills()
    else:
        update_existing_bills()
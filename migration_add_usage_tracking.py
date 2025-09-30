#!/usr/bin/env python3
"""
Migration Script: Add Usage Tracking to Purchase Bills
This script adds usage tracking columns to purchase_bill and purchase_bill_item tables
"""

import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.database import engine
from sqlalchemy import text


def run_migration():
    """Run the migration to add usage tracking columns"""
    
    print("Starting migration: Add Usage Tracking to Purchase Bills")
    print("=" * 60)
    
    with engine.connect() as connection:
        try:
            # Add columns to purchase_bill table
            print("\n1. Adding columns to purchase_bill table...")
            
            migration_queries = [
                """
                ALTER TABLE purchase_bill 
                ADD COLUMN IF NOT EXISTS used_in_pos BOOLEAN DEFAULT FALSE;
                """,
                """
                ALTER TABLE purchase_bill 
                ADD COLUMN IF NOT EXISTS used_in_sales BOOLEAN DEFAULT FALSE;
                """,
                """
                ALTER TABLE purchase_bill 
                ADD COLUMN IF NOT EXISTS pos_transaction_id INTEGER;
                """,
                """
                ALTER TABLE purchase_bill 
                ADD COLUMN IF NOT EXISTS sale_id INTEGER;
                """,
                """
                ALTER TABLE purchase_bill 
                ADD COLUMN IF NOT EXISTS modification_locked BOOLEAN DEFAULT FALSE;
                """,
                
                # Add columns to purchase_bill_item table
                """
                ALTER TABLE purchase_bill_item 
                ADD COLUMN IF NOT EXISTS used_in_pos BOOLEAN DEFAULT FALSE;
                """,
                """
                ALTER TABLE purchase_bill_item 
                ADD COLUMN IF NOT EXISTS used_in_sales BOOLEAN DEFAULT FALSE;
                """,
                """
                ALTER TABLE purchase_bill_item 
                ADD COLUMN IF NOT EXISTS pos_transaction_id INTEGER;
                """,
                """
                ALTER TABLE purchase_bill_item 
                ADD COLUMN IF NOT EXISTS sale_id INTEGER;
                """,
                """
                ALTER TABLE purchase_bill_item 
                ADD COLUMN IF NOT EXISTS modification_locked BOOLEAN DEFAULT FALSE;
                """
            ]
            
            for i, query in enumerate(migration_queries, 1):
                try:
                    connection.execute(text(query))
                    print(f"   ✓ Query {i} executed successfully")
                except Exception as e:
                    print(f"   ⚠ Query {i} warning: {str(e)}")
            
            connection.commit()
            print("\n✅ Migration completed successfully!")
            print("\n2. Verifying columns...")
            
            # Verify purchase_bill columns
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'purchase_bill' 
                AND column_name IN ('used_in_pos', 'used_in_sales', 'pos_transaction_id', 'sale_id', 'modification_locked');
            """))
            
            columns = [row[0] for row in result]
            print(f"\n   purchase_bill columns added: {columns}")
            
            # Verify purchase_bill_item columns
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'purchase_bill_item' 
                AND column_name IN ('used_in_pos', 'used_in_sales', 'pos_transaction_id', 'sale_id', 'modification_locked');
            """))
            
            columns = [row[0] for row in result]
            print(f"   purchase_bill_item columns added: {columns}")
            
            print("\n" + "=" * 60)
            print("Migration completed successfully!")
            print("\nNext steps:")
            print("1. Restart your application")
            print("2. Run update_existing_bills.py to check existing bills")
            print("3. Test the new bill modification endpoints")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            connection.rollback()
            raise


def rollback_migration():
    """Rollback the migration (remove added columns)"""
    
    print("Rolling back migration: Remove Usage Tracking from Purchase Bills")
    print("=" * 60)
    
    with engine.connect() as connection:
        try:
            rollback_queries = [
                "ALTER TABLE purchase_bill DROP COLUMN IF EXISTS used_in_pos;",
                "ALTER TABLE purchase_bill DROP COLUMN IF EXISTS used_in_sales;",
                "ALTER TABLE purchase_bill DROP COLUMN IF EXISTS pos_transaction_id;",
                "ALTER TABLE purchase_bill DROP COLUMN IF EXISTS sale_id;",
                "ALTER TABLE purchase_bill DROP COLUMN IF EXISTS modification_locked;",
                "ALTER TABLE purchase_bill_item DROP COLUMN IF EXISTS used_in_pos;",
                "ALTER TABLE purchase_bill_item DROP COLUMN IF EXISTS used_in_sales;",
                "ALTER TABLE purchase_bill_item DROP COLUMN IF EXISTS pos_transaction_id;",
                "ALTER TABLE purchase_bill_item DROP COLUMN IF EXISTS sale_id;",
                "ALTER TABLE purchase_bill_item DROP COLUMN IF EXISTS modification_locked;"
            ]
            
            for query in rollback_queries:
                connection.execute(text(query))
            
            connection.commit()
            print("✅ Rollback completed successfully!")
            
        except Exception as e:
            print(f"❌ Rollback failed: {str(e)}")
            connection.rollback()
            raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Migration script for usage tracking')
    parser.add_argument('--rollback', action='store_true', help='Rollback the migration')
    args = parser.parse_args()
    
    if args.rollback:
        confirm = input("Are you sure you want to rollback? (yes/no): ")
        if confirm.lower() == 'yes':
            rollback_migration()
        else:
            print("Rollback cancelled")
    else:
        run_migration()
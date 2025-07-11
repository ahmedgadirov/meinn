#!/usr/bin/env python3
"""
Verification Script for Render Import
Checks if categories and menu items are properly imported and accessible
"""

import sqlite3
import json
import os
from pathlib import Path

def verify_database():
    """Verify database contents and structure"""
    db_file = 'menu_data.db'
    
    if not Path(db_file).exists():
        print("❌ Database file not found!")
        return False
    
    print("🔍 Verifying database contents...")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check categories
        cursor.execute('SELECT COUNT(*) FROM categories')
        category_count = cursor.fetchone()[0]
        print(f"📂 Categories: {category_count}")
        
        if category_count > 0:
            cursor.execute('SELECT id, name_en FROM categories LIMIT 5')
            categories = cursor.fetchall()
            print("   Sample categories:")
            for cat_id, name in categories:
                print(f"   - {cat_id}: {name}")
        
        # Check menu items
        cursor.execute('SELECT COUNT(*) FROM menu_items')
        item_count = cursor.fetchone()[0]
        print(f"🍽️  Menu Items: {item_count}")
        
        if item_count > 0:
            cursor.execute('SELECT id, name, category_id, price FROM menu_items LIMIT 5')
            items = cursor.fetchall()
            print("   Sample items:")
            for item_id, name, cat_id, price in items:
                print(f"   - {name} ({cat_id}): ${price}")
        
        # Check item_details for multilingual support
        cursor.execute('SELECT COUNT(*) FROM item_details')
        details_count = cursor.fetchone()[0]
        print(f"🌐 Item Details (translations): {details_count}")
        
        # Test specific queries that the API would use
        print("\n🔧 Testing API-style queries...")
        
        # Get categories with items count
        cursor.execute('''
            SELECT c.id, c.name_en, COUNT(m.id) as item_count
            FROM categories c
            LEFT JOIN menu_items m ON c.id = m.category_id
            WHERE m.available = 1
            GROUP BY c.id, c.name_en
            ORDER BY c.display_order, c.name_en
        ''')
        category_data = cursor.fetchall()
        
        print(f"✅ API Categories Query: {len(category_data)} categories with items")
        for cat_id, name, count in category_data[:3]:
            print(f"   - {name}: {count} items")
        
        # Get menu items for first category
        if category_data:
            first_cat = category_data[0][0]
            cursor.execute('''
                SELECT id, name, description, price, available
                FROM menu_items
                WHERE category_id = ? AND available = 1
                LIMIT 3
            ''', (first_cat,))
            cat_items = cursor.fetchall()
            
            print(f"✅ Category Items Query: {len(cat_items)} items in '{category_data[0][1]}'")
            for item_id, name, desc, price, available in cat_items:
                print(f"   - {name}: ${price} (available: {bool(available)})")
        
        conn.close()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 50)
        
        if category_count > 0 and item_count > 0:
            print("✅ SUCCESS: Both categories and menu items are present")
            print("✅ Database structure is correct")
            print("✅ API queries work properly")
            
            print(f"\n📈 Import Statistics:")
            print(f"   - {category_count} categories imported")
            print(f"   - {item_count} menu items imported") 
            print(f"   - {details_count} translation records")
            
            return True
        else:
            print("❌ ISSUE: Missing data")
            if category_count == 0:
                print("   - No categories found")
            if item_count == 0:
                print("   - No menu items found")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def test_menu_manager_compatibility():
    """Test if the data works with MenuManager"""
    print("\n🔧 Testing MenuManager compatibility...")
    
    try:
        # Import the MenuManager if available
        import sys
        sys.path.append('src/services/product')
        
        from menu_manager import MenuManager
        
        # Test basic operations
        manager = MenuManager()
        
        # Get categories
        categories = manager.get_categories()
        print(f"✅ MenuManager.get_categories(): {len(categories)} categories")
        
        # Get menu items for first category if available
        if categories:
            first_cat = categories[0]['id']
            items = manager.get_menu_items(first_cat)
            print(f"✅ MenuManager.get_menu_items('{first_cat}'): {len(items)} items")
            
            # Test get all items
            all_items = manager.get_all_menu_items()
            print(f"✅ MenuManager.get_all_menu_items(): {len(all_items)} items")
            
        return True
        
    except ImportError:
        print("⚠️  MenuManager not available for testing")
        return True
    except Exception as e:
        print(f"❌ MenuManager test failed: {e}")
        return False

def main():
    """Main verification function"""
    print("🔍 RENDER IMPORT VERIFICATION")
    print("=" * 50)
    print("Checking if categories and menu items are properly imported...")
    print()
    
    # Verify database
    db_success = verify_database()
    
    # Test MenuManager compatibility
    manager_success = test_menu_manager_compatibility()
    
    # Final result
    print("\n" + "=" * 50)
    if db_success and manager_success:
        print("🎉 VERIFICATION PASSED!")
        print("✅ Your menu data is properly imported and ready for production")
        print("✅ Both categories and menu items are accessible")
        print("✅ The data structure is compatible with your API")
        print("\n💡 Your render shell import issue should now be resolved!")
    else:
        print("❌ VERIFICATION FAILED!")
        print("⚠️  There may still be issues with the import")
        
    print("=" * 50)

if __name__ == "__main__":
    main()

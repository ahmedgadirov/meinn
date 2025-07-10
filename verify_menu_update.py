#!/usr/bin/env python3
"""
Verification script to check the updated menu data
"""

import sqlite3
import json

def verify_menu_data():
    """Verify the imported menu data"""
    conn = sqlite3.connect('menu_data.db')
    cursor = conn.cursor()
    
    print("🍕 MEINN RESTAURANT - MENU UPDATE VERIFICATION")
    print("=" * 60)
    
    # Check categories with multilingual support
    print("\n📂 CATEGORIES WITH MULTILINGUAL SUPPORT:")
    cursor.execute('''
        SELECT id, name, name_en, name_az, name_ru, name_tr 
        FROM categories 
        ORDER BY id
    ''')
    categories = cursor.fetchall()
    
    for cat_id, name, name_en, name_az, name_ru, name_tr in categories:
        cursor.execute('SELECT COUNT(*) FROM menu_items WHERE category_id = ?', (cat_id,))
        item_count = cursor.fetchone()[0]
        print(f"  {cat_id}: {item_count} items")
        print(f"    EN: {name_en}")
        print(f"    AZ: {name_az}")
        print(f"    RU: {name_ru}")
        print(f"    TR: {name_tr}")
        print()
    
    # Show sample items from different categories
    print("\n🍽️ SAMPLE MENU ITEMS:")
    sample_categories = ['PIZZA', 'BEVERAGES', 'BREAKFAST', 'KEBABS']
    
    for category in sample_categories:
        print(f"\n--- {category} ---")
        cursor.execute('''
            SELECT name, price, name_en, name_az, name_ru, available
            FROM menu_items 
            WHERE category_id = ? 
            LIMIT 3
        ''', (category,))
        items = cursor.fetchall()
        
        for name, price, name_en, name_az, name_ru, available in items:
            status = "✅ Available" if available else "❌ Unavailable"
            print(f"  • {name} - ${price}")
            print(f"    EN: {name_en}")
            print(f"    AZ: {name_az}")
            print(f"    RU: {name_ru}")
            print(f"    {status}")
            print()
    
    # Check price ranges
    print("\n💰 PRICE ANALYSIS:")
    cursor.execute('SELECT MIN(price), MAX(price), AVG(price) FROM menu_items WHERE price > 0')
    min_price, max_price, avg_price = cursor.fetchone()
    print(f"  Price Range: ${min_price:.2f} - ${max_price:.2f}")
    print(f"  Average Price: ${avg_price:.2f}")
    
    # Check availability
    cursor.execute('SELECT COUNT(*) FROM menu_items WHERE available = 1')
    available_items = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM menu_items')
    total_items = cursor.fetchone()[0]
    print(f"  Available Items: {available_items}/{total_items} ({available_items/total_items*100:.1f}%)")
    
    # Check popular items
    cursor.execute('SELECT COUNT(*) FROM menu_items WHERE popular = 1')
    popular_items = cursor.fetchone()[0]
    print(f"  Popular Items: {popular_items}")
    
    conn.close()
    print("\n✅ Menu update verification completed!")

if __name__ == "__main__":
    verify_menu_data()

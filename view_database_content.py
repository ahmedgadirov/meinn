#!/usr/bin/env python3
"""
Script to view all database content clearly
"""

import sqlite3
import json

def view_categories():
    """Display all categories"""
    print("=" * 80)
    print("CATEGORIES")
    print("=" * 80)
    
    conn = sqlite3.connect('menu_data.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, description, image_url, name_en, name_az, name_ru
        FROM categories
        ORDER BY id
    """)
    
    categories = cursor.fetchall()
    
    for i, cat in enumerate(categories, 1):
        print(f"{i:2d}. ID: {cat[0]}")
        print(f"    Name: {cat[1]}")
        print(f"    Description: {cat[2] or 'N/A'}")
        print(f"    Image: {cat[3] or 'N/A'}")
        print(f"    English: {cat[4] or 'N/A'}")
        print(f"    Azerbaijani: {cat[5] or 'N/A'}")
        print(f"    Russian: {cat[6] or 'N/A'}")
        print()
    
    conn.close()

def view_menu_items():
    """Display all menu items"""
    print("=" * 80)
    print("MENU ITEMS")
    print("=" * 80)
    
    conn = sqlite3.connect('menu_data.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT m.id, m.name, m.description, m.category_id, m.price, m.available,
               m.name_en, m.name_az, m.name_ru
        FROM menu_items m
        ORDER BY m.category_id, m.id
        LIMIT 20
    """)
    
    items = cursor.fetchall()
    
    for i, item in enumerate(items, 1):
        print(f"{i:2d}. ID: {item[0]}")
        print(f"    Name: {item[1]}")
        print(f"    Description: {item[2][:100]}..." if item[2] and len(item[2]) > 100 else f"    Description: {item[2] or 'N/A'}")
        print(f"    Category: {item[3]}")
        print(f"    Price: ${item[4]}")
        print(f"    Available: {'Yes' if item[5] else 'No'}")
        print(f"    English: {item[6] or 'N/A'}")
        print(f"    Azerbaijani: {item[7] or 'N/A'}")
        print(f"    Russian: {item[8] or 'N/A'}")
        print()
    
    # Show total count
    cursor.execute("SELECT COUNT(*) FROM menu_items")
    total = cursor.fetchone()[0]
    print(f"(Showing first 20 of {total} total menu items)")
    
    conn.close()

def view_database_stats():
    """Show database statistics"""
    print("=" * 80)
    print("DATABASE STATISTICS")
    print("=" * 80)
    
    conn = sqlite3.connect('menu_data.db')
    cursor = conn.cursor()
    
    # Categories stats
    cursor.execute("SELECT COUNT(*) FROM categories")
    cat_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM categories WHERE name_en IS NOT NULL AND name_en != ''")
    cat_en_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM categories WHERE name_az IS NOT NULL AND name_az != ''")
    cat_az_count = cursor.fetchone()[0]
    
    # Menu items stats
    cursor.execute("SELECT COUNT(*) FROM menu_items")
    item_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM menu_items WHERE name_en IS NOT NULL AND name_en != ''")
    item_en_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM menu_items WHERE name_az IS NOT NULL AND name_az != ''")
    item_az_count = cursor.fetchone()[0]
    
    # Available items
    cursor.execute("SELECT COUNT(*) FROM menu_items WHERE available = 1")
    available_count = cursor.fetchone()[0]
    
    print(f"Categories: {cat_count} total")
    print(f"  - With English translations: {cat_en_count}")
    print(f"  - With Azerbaijani translations: {cat_az_count}")
    print()
    print(f"Menu Items: {item_count} total")
    print(f"  - With English translations: {item_en_count}")
    print(f"  - With Azerbaijani translations: {item_az_count}")
    print(f"  - Currently available: {available_count}")
    
    conn.close()

if __name__ == "__main__":
    print("MEINN RESTAURANT DATABASE CONTENT")
    print("=" * 80)
    
    view_database_stats()
    print()
    view_categories()
    print()
    view_menu_items()
    
    print("\n" + "=" * 80)
    print("To view the database with a GUI tool, you can:")
    print("1. Install DB Browser for SQLite: sudo apt install sqlitebrowser")
    print("2. Then run: sqlitebrowser menu_data.db")
    print("=" * 80)

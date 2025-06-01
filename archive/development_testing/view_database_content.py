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
        SELECT id, name, description, image_url, 
               name_en, name_az, name_ru, name_tr, name_ar, name_hi, name_fr, name_it
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
        print(f"    Turkish: {cat[7] or 'N/A'}")
        print(f"    Arabic: {cat[8] or 'N/A'}")
        print(f"    Hindi: {cat[9] or 'N/A'}")
        print(f"    French: {cat[10] or 'N/A'}")
        print(f"    Italian: {cat[11] or 'N/A'}")
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
               m.name_en, m.name_az, m.name_ru, m.name_tr, m.name_ar, m.name_hi, m.name_fr, m.name_it
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
        print(f"    Turkish: {item[9] or 'N/A'}")
        print(f"    Arabic: {item[10] or 'N/A'}")
        print(f"    Hindi: {item[11] or 'N/A'}")
        print(f"    French: {item[12] or 'N/A'}")
        print(f"    Italian: {item[13] or 'N/A'}")
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
    
    # Check if multilingual columns exist
    cursor.execute("PRAGMA table_info(categories)")
    cat_columns = [column[1] for column in cursor.fetchall()]
    
    cursor.execute("PRAGMA table_info(menu_items)")
    item_columns = [column[1] for column in cursor.fetchall()]
    
    print("Database Schema:")
    print(f"Categories table columns: {len(cat_columns)}")
    print(f"Menu items table columns: {len(item_columns)}")
    
    # Check for multilingual columns
    languages = ['en', 'az', 'ru', 'tr', 'ar', 'hi', 'fr', 'it']
    lang_names = ['English', 'Azerbaijani', 'Russian', 'Turkish', 'Arabic', 'Hindi', 'French', 'Italian']
    
    multilingual_cat_cols = [col for col in cat_columns if col.startswith('name_') and col.split('_')[1] in languages]
    multilingual_item_cols = [col for col in item_columns if col.startswith('name_') and col.split('_')[1] in languages]
    
    print(f"Multilingual category columns found: {multilingual_cat_cols}")
    print(f"Multilingual menu item columns found: {multilingual_item_cols}")
    print()
    
    # Categories stats
    cursor.execute("SELECT COUNT(*) FROM categories")
    cat_count = cursor.fetchone()[0]
    
    print(f"Categories: {cat_count} total")
    for i, lang in enumerate(languages):
        col_name = f'name_{lang}'
        if col_name in cat_columns:
            cursor.execute(f"SELECT COUNT(*) FROM categories WHERE {col_name} IS NOT NULL AND {col_name} != ''")
            count = cursor.fetchone()[0]
            print(f"  - With {lang_names[i]} translations: {count}")
        else:
            print(f"  - {lang_names[i]} column missing")
    
    print()
    
    # Menu items stats
    cursor.execute("SELECT COUNT(*) FROM menu_items")
    item_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM menu_items WHERE available = 1")
    available_count = cursor.fetchone()[0]
    
    print(f"Menu Items: {item_count} total ({available_count} available)")
    for i, lang in enumerate(languages):
        col_name = f'name_{lang}'
        if col_name in item_columns:
            cursor.execute(f"SELECT COUNT(*) FROM menu_items WHERE {col_name} IS NOT NULL AND {col_name} != ''")
            count = cursor.fetchone()[0]
            print(f"  - With {lang_names[i]} translations: {count}")
        else:
            print(f"  - {lang_names[i]} column missing")
    
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

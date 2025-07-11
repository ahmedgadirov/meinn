#!/usr/bin/env python3
"""
Import real_menu_data.csv into menu_data.db
Quick fix to get the menu working
"""

import sqlite3
import csv
import json
from datetime import datetime

def import_menu_data():
    """Import menu items from real_menu_data.csv"""
    print("Starting menu import...")
    
    # Connect to database
    conn = sqlite3.connect('menu_data.db')
    cursor = conn.cursor()
    
    # Clear existing menu items (but keep categories)
    print("Clearing existing menu items...")
    cursor.execute('DELETE FROM menu_items')
    
    imported_count = 0
    
    try:
        with open('real_menu_data.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                try:
                    # Extract basic fields
                    item_id = row.get('ID', '')
                    name = row.get('Name', '').strip()
                    description = row.get('Description', '').strip()
                    category_id = row.get('Category Name', '').strip()
                    
                    # Skip if missing essential fields
                    if not name or not category_id:
                        continue
                    
                    # Price handling
                    price = 0.0
                    try:
                        price_str = row.get('Price', '0').strip()
                        if price_str:
                            price = float(price_str)
                    except:
                        price = 0.0
                    
                    # Other fields
                    image_url = row.get('Image URL', '').strip() or 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTcWKAPNpBPrNwnMLN98hVyg5Vs1x3GOpALlg&s'
                    available = row.get('Available', 'TRUE').upper() == 'TRUE'
                    popular = row.get('Popular', 'FALSE').upper() == 'TRUE'
                    
                    prep_time = 15
                    try:
                        prep_time_str = row.get('Preparation Time', '15').strip()
                        if prep_time_str:
                            prep_time = int(prep_time_str)
                    except:
                        prep_time = 15
                    
                    # Timestamps
                    now = datetime.now().isoformat()
                    
                    # Insert menu item
                    cursor.execute('''
                        INSERT INTO menu_items (
                            id, name, description, category_id, price, image_url,
                            available, popular, preparation_time, created_at, updated_at,
                            name_az, name_en, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
                            description_az, description_en, description_ru, description_tr,
                            description_ar, description_hi, description_fr, description_it,
                            size_options, size_prices, default_size
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item_id or f"item_{imported_count + 1}",
                        name,
                        description,
                        category_id,
                        price,
                        image_url,
                        available,
                        popular,
                        prep_time,
                        now,
                        now,
                        row.get('Name AZ', '').strip() or name,
                        row.get('Name EN', '').strip() or name,
                        row.get('Name RU', '').strip() or name,
                        row.get('Name TR', '').strip() or name,
                        row.get('Name AR', '').strip() or name,
                        row.get('Name HI', '').strip() or name,
                        row.get('Name FR', '').strip() or name,
                        row.get('Name IT', '').strip() or name,
                        row.get('Description AZ', '').strip() or description,
                        row.get('Description EN', '').strip() or description,
                        row.get('Description RU', '').strip() or description,
                        row.get('Description TR', '').strip() or description,
                        row.get('Description AR', '').strip() or description,
                        row.get('Description HI', '').strip() or description,
                        row.get('Description FR', '').strip() or description,
                        row.get('Description IT', '').strip() or description,
                        json.dumps([]),  # size_options
                        json.dumps({}),  # size_prices
                        ''               # default_size
                    ))
                    
                    imported_count += 1
                    
                except Exception as e:
                    print(f"Error importing row: {e}")
                    continue
        
        # Commit all changes
        conn.commit()
        print(f"Successfully imported {imported_count} menu items!")
        
        # Verify the import
        cursor.execute('SELECT COUNT(*) FROM menu_items')
        total_items = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM categories')
        total_categories = cursor.fetchone()[0]
        
        print(f"Database now contains:")
        print(f"  - {total_categories} categories")
        print(f"  - {total_items} menu items")
        
    except Exception as e:
        print(f"Import failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    import_menu_data()

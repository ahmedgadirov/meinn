#!/usr/bin/env python3

import csv
import sqlite3
import json
from datetime import datetime

def import_multilingual_categories():
    """Import categories with all language translations"""
    print("Importing multilingual categories...")
    
    conn = sqlite3.connect('menu_data.db')
    cursor = conn.cursor()
    
    # Clear existing categories
    cursor.execute("DELETE FROM categories")
    
    # Read and import categories
    with open('menu_categories_export.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            category_id = row['ID']
            name = row['Name']
            description = row['Description']
            image_url = row['Image URL']
            
            # Language translations
            name_en = row['Name EN']
            name_az = row['Name AZ'] 
            name_ru = row['Name RU']
            name_tr = row['Name TR']
            name_ar = row['Name AR']
            name_hi = row['Name HI']
            name_fr = row['Name FR']
            name_it = row['Name IT']
            
            desc_en = row['Description EN']
            desc_az = row['Description AZ']
            desc_ru = row['Description RU'] 
            desc_tr = row['Description TR']
            desc_ar = row['Description AR']
            desc_hi = row['Description HI']
            desc_fr = row['Description FR']
            desc_it = row['Description IT']
            
            cursor.execute("""
                INSERT INTO categories (
                    id, name, description, image_url,
                    name_en, name_az, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
                    description_en, description_az, description_ru, description_tr, 
                    description_ar, description_hi, description_fr, description_it
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                category_id, name, description, image_url,
                name_en, name_az, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
                desc_en, desc_az, desc_ru, desc_tr, desc_ar, desc_hi, desc_fr, desc_it
            ))
    
    conn.commit()
    conn.close()
    print(f"Categories imported successfully!")

def import_multilingual_menu_items():
    """Import menu items with all language translations"""
    print("Importing multilingual menu items...")
    
    conn = sqlite3.connect('menu_data.db')
    cursor = conn.cursor()
    
    # Clear existing menu items and details
    cursor.execute("DELETE FROM item_details")
    cursor.execute("DELETE FROM menu_items")
    
    # Read and import menu items
    with open('menu_items_export.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            item_id = row['ID']
            name = row['Name']
            description = row['Description']
            category_id = row['Category ID']
            price = float(row['Price'])
            available = int(row['Available'])
            image_url = row['Image URL']
            popular = int(row['Popular'])
            prep_time = int(row['Preparation Time'])
            
            # Language translations
            name_en = row['Name EN']
            name_az = row['Name AZ']
            name_ru = row['Name RU'] 
            name_tr = row['Name TR']
            name_ar = row['Name AR']
            name_hi = row['Name HI']
            name_fr = row['Name FR']
            name_it = row['Name IT']
            
            desc_en = row['Description EN']
            desc_az = row['Description AZ']
            desc_ru = row['Description RU']
            desc_tr = row['Description TR'] 
            desc_ar = row['Description AR']
            desc_hi = row['Description HI']
            desc_fr = row['Description FR']
            desc_it = row['Description IT']
            
            # Insert menu item
            cursor.execute("""
                INSERT INTO menu_items (
                    id, name, description, category_id, price, available, 
                    image_url, popular, preparation_time,
                    name_en, name_az, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
                    description_en, description_az, description_ru, description_tr,
                    description_ar, description_hi, description_fr, description_it
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item_id, name, description, category_id, price, available,
                image_url, popular, prep_time,
                name_en, name_az, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
                desc_en, desc_az, desc_ru, desc_tr, desc_ar, desc_hi, desc_fr, desc_it
            ))
            
            # Insert item details (empty for now, could be enhanced)
            cursor.execute("""
                INSERT INTO item_details (item_id, allergens, ingredients, nutrition)
                VALUES (?, ?, ?, ?)
            """, (item_id, '[]', '[]', '{}'))
    
    conn.commit()
    conn.close()
    print(f"Menu items imported successfully!")

def main():
    print("Starting multilingual menu import...")
    try:
        import_multilingual_categories()
        import_multilingual_menu_items()
        print("\n✅ All data imported successfully!")
        print("🌍 Multilingual support is now active!")
        
        # Test the import
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM categories")
        cat_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM menu_items")
        item_count = cursor.fetchone()[0]
        
        print(f"📊 Import Summary:")
        print(f"   - Categories: {cat_count}")
        print(f"   - Menu Items: {item_count}")
        
        # Test translations
        cursor.execute("SELECT id, name, name_en, name_az, name_ru FROM categories LIMIT 2")
        test_cats = cursor.fetchall()
        print(f"\n🧪 Sample translations:")
        for cat in test_cats:
            print(f"   {cat[0]}: EN='{cat[2]}', AZ='{cat[3]}', RU='{cat[4]}'")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during import: {str(e)}")
        raise

if __name__ == "__main__":
    main()

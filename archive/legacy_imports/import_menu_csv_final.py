#!/usr/bin/env python3

import csv
import sqlite3
import logging
import sys
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('meinn_ai.csv_import_final')

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect('data/menu.db')

def clear_existing_data():
    """Clear existing menu data"""
    logger.info("Clearing existing menu items...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clear in correct order due to foreign key constraints
    cursor.execute("DELETE FROM menu_item_details")
    cursor.execute("DELETE FROM menu_items")
    cursor.execute("DELETE FROM menu_categories WHERE id NOT IN (1, 2, 3, 4, 5, 6, 7, 8)")  # Keep core categories
    
    conn.commit()
    conn.close()

def create_category_if_not_exists(category_name, category_translations):
    """Create category if it doesn't exist and return its ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if category exists
    cursor.execute("SELECT id FROM menu_categories WHERE name = ?", (category_name,))
    result = cursor.fetchone()
    
    if result:
        category_id = result[0]
    else:
        # Create new category
        cursor.execute("""
            INSERT INTO menu_categories (name, description, display_order, active)
            VALUES (?, ?, ?, ?)
        """, (category_name, f"Category for {category_name}", 1, True))
        category_id = cursor.lastrowid
        
        # Create translations for this category
        languages = ['en', 'az', 'ru', 'tr', 'ar', 'hi', 'fr', 'it']
        for i, lang in enumerate(languages):
            translation_key = f"category_{category_id}_name"
            translation_value = category_translations.get(lang, category_name)
            
            cursor.execute("""
                INSERT OR REPLACE INTO translations (key, language, value)
                VALUES (?, ?, ?)
            """, (translation_key, lang, translation_value))
    
    conn.commit()
    conn.close()
    return category_id

def import_menu_item(row_data, row_num):
    """Import a single menu item"""
    try:
        # Parse the 37 columns
        (item_id, name, description, category_id_str, category_name, price_str, size, 
         available_str, image_url, popular_str, prep_time_str,
         category_en, category_az, category_ru, category_tr, category_ar, category_hi, category_fr, category_it,
         name_en, name_az, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
         desc_en, desc_az, desc_ru, desc_tr, desc_ar, desc_hi, desc_fr, desc_it,
         created_at, updated_at) = row_data
        
        # Parse and validate data
        price = float(price_str) if price_str else 0.0
        available = available_str.upper() == 'TRUE' if available_str else True
        popular = popular_str.upper() == 'TRUE' if popular_str else False
        prep_time = int(prep_time_str) if prep_time_str and prep_time_str.isdigit() else 0
        
        # Category translations
        category_translations = {
            'en': category_en or category_name,
            'az': category_az or category_name,
            'ru': category_ru or category_name,
            'tr': category_tr or category_name,
            'ar': category_ar or category_name,
            'hi': category_hi or category_name,
            'fr': category_fr or category_name,
            'it': category_it or category_name
        }
        
        # Create/get category
        if not category_name:
            logger.warning(f"Row {row_num}: No category name, skipping")
            return False
            
        category_id = create_category_if_not_exists(category_name, category_translations)
        
        # Create menu item
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO menu_items (
                category_id, name, description, price, image_url, 
                available, popular, preparation_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            category_id, name or name_en, description or desc_en, price, 
            image_url, available, popular, prep_time
        ))
        
        menu_item_id = cursor.lastrowid
        
        # Create item details (for size variations if needed)
        cursor.execute("""
            INSERT INTO menu_item_details (
                item_id, size, price, available
            ) VALUES (?, ?, ?, ?)
        """, (menu_item_id, size or 'regular', price, available))
        
        # Create translations for item name
        languages = ['en', 'az', 'ru', 'tr', 'ar', 'hi', 'fr', 'it']
        name_translations = [name_en, name_az, name_ru, name_tr, name_ar, name_hi, name_fr, name_it]
        desc_translations = [desc_en, desc_az, desc_ru, desc_tr, desc_ar, desc_hi, desc_fr, desc_it]
        
        for i, lang in enumerate(languages):
            # Name translation
            if name_translations[i]:
                cursor.execute("""
                    INSERT OR REPLACE INTO translations (key, language, value)
                    VALUES (?, ?, ?)
                """, (f"item_{menu_item_id}_name", lang, name_translations[i]))
            
            # Description translation
            if desc_translations[i]:
                cursor.execute("""
                    INSERT OR REPLACE INTO translations (key, language, value)
                    VALUES (?, ?, ?)
                """, (f"item_{menu_item_id}_description", lang, desc_translations[i]))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Imported item {menu_item_id}: {name} in category {category_name}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing row {row_num}: {str(e)}")
        return False

def import_csv():
    """Main import function"""
    csv_file = "/home/ahmd/Desktop/menu pizza inn/menu_items_export.csv"
    
    logger.info("Starting final CSV menu import...")
    
    # Clear existing data
    clear_existing_data()
    
    # Import data
    total_processed = 0
    total_imported = 0
    total_errors = 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            
            logger.info(f"CSV has {len(headers)} columns")
            
            if len(headers) != 37:
                logger.error(f"Expected 37 columns, got {len(headers)}")
                return
            
            for row_num, row in enumerate(reader, start=1):
                total_processed += 1
                
                if len(row) != 37:
                    logger.error(f"Row {row_num}: Expected 37 values, got {len(row)}")
                    total_errors += 1
                    continue
                
                if import_menu_item(row, row_num):
                    total_imported += 1
                else:
                    total_errors += 1
    
    except FileNotFoundError:
        logger.error(f"CSV file not found: {csv_file}")
        return
    except Exception as e:
        logger.error(f"Error reading CSV: {str(e)}")
        return
    
    # Verification
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM menu_items")
    total_items = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM menu_item_details")
    total_details = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT c.name, COUNT(mi.id) as item_count
        FROM menu_categories c
        LEFT JOIN menu_items mi ON c.id = mi.category_id
        GROUP BY c.id, c.name
        HAVING item_count > 0
        ORDER BY item_count DESC
    """)
    categories = cursor.fetchall()
    
    conn.close()
    
    logger.info("Import completed successfully!")
    logger.info(f"Total items imported: {total_imported}")
    logger.info(f"Total item details created: {total_details}")
    logger.info(f"Processed: {total_processed}, Errors: {total_errors}")
    
    logger.info("\nImport Verification - Items by Category:")
    logger.info("=" * 50)
    for category_name, count in categories:
        logger.info(f"{category_name}: {count} items")
    
    logger.info(f"\nTotal items across all categories: {total_items}")
    logger.info(f"Items with custom size options: {total_details}")
    
    logger.info("Menu CSV import completed successfully!")

if __name__ == "__main__":
    import_csv()

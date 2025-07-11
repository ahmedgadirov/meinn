#!/usr/bin/env python3
"""
Fixed Menu Data Import Script for Meinn Restaurant
Addresses database path issues and improves error handling for menu import
"""

import os
import sys
import sqlite3
import csv
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('menu_import_fixed.log')
    ]
)
logger = logging.getLogger(__name__)

def connect_database():
    """Connect to the menu database"""
    db_path = 'data/menu.db'
    if not os.path.exists(db_path):
        logger.error(f"Database not found: {db_path}")
        sys.exit(1)
    
    conn = sqlite3.connect(db_path)
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def clear_existing_data(conn):
    """Clear existing menu data"""
    logger.info("Clearing existing menu data...")
    cursor = conn.cursor()
    
    try:
        # Clear tables in correct order (respecting foreign keys)
        cursor.execute('DELETE FROM item_pairings')
        cursor.execute('DELETE FROM item_details')
        cursor.execute('DELETE FROM order_items')
        cursor.execute('DELETE FROM orders')
        cursor.execute('DELETE FROM menu_items')
        cursor.execute('DELETE FROM categories')
        
        conn.commit()
        logger.info("Existing data cleared successfully")
    except Exception as e:
        logger.error(f"Error clearing data: {str(e)}")
        conn.rollback()
        raise

def create_categories(conn, csv_file_path):
    """Extract and create unique categories from CSV"""
    logger.info("Creating categories...")
    cursor = conn.cursor()
    
    categories = {}
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row_num, row in enumerate(reader, 1):
                try:
                    # Use 'Category Name' as the key field
                    category_name = row.get('Category Name', '').strip()
                    if category_name and category_name not in categories:
                        categories[category_name] = {
                            'name': category_name,
                            'name_en': row.get('Category EN', '').strip(),
                            'name_az': row.get('Category AZ', '').strip(),
                            'name_ru': row.get('Category RU', '').strip(),
                            'name_tr': row.get('Category TR', '').strip(),
                            'name_ar': row.get('Category AR', '').strip(),
                            'name_hi': row.get('Category HI', '').strip(),
                            'name_fr': row.get('Category FR', '').strip(),
                            'name_it': row.get('Category IT', '').strip(),
                        }
                except Exception as e:
                    logger.warning(f"Error processing category in row {row_num}: {str(e)}")
                    continue
        
        # Insert categories
        for category_id, category_data in categories.items():
            try:
                cursor.execute('''
                    INSERT INTO categories (
                        id, name, description, image_url,
                        name_az, name_en, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
                        description_az, description_en, description_ru, description_tr, 
                        description_ar, description_hi, description_fr, description_it,
                        parent_id, sort_order, is_active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    category_id,
                    category_data['name'],
                    '',  # description
                    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTcWKAPNpBPrNwnMLN98hVyg5Vs1x3GOpALlg&s',  # default image
                    category_data['name_az'] or category_data['name'],
                    category_data['name_en'] or category_data['name'],
                    category_data['name_ru'] or category_data['name'],
                    category_data['name_tr'] or category_data['name'],
                    category_data['name_ar'] or category_data['name'],
                    category_data['name_hi'] or category_data['name'],
                    category_data['name_fr'] or category_data['name'],
                    category_data['name_it'] or category_data['name'],
                    '',  # description_az
                    '',  # description_en
                    '',  # description_ru
                    '',  # description_tr
                    '',  # description_ar
                    '',  # description_hi
                    '',  # description_fr
                    '',  # description_it
                    None,  # parent_id
                    0,     # sort_order
                    1      # is_active
                ))
            except Exception as e:
                logger.error(f"Error inserting category {category_id}: {str(e)}")
                continue
        
        conn.commit()
        logger.info(f"Created {len(categories)} categories")
        
    except Exception as e:
        logger.error(f"Error creating categories: {str(e)}")
        conn.rollback()
        raise

def safe_get_field(row, field, default=''):
    """Safely get field from row with fallback"""
    return row.get(field, default).strip() if row.get(field) else default

def safe_float(value, default=0.0):
    """Safely convert to float"""
    try:
        return float(value) if value and str(value).strip() else default
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    """Safely convert to integer"""
    try:
        return int(value) if value and str(value).strip() else default
    except (ValueError, TypeError):
        return default

def safe_bool(value, default=False):
    """Safely convert to boolean"""
    if not value:
        return default
    return str(value).strip().upper() in ('TRUE', '1', 'YES', 'Y')

def import_menu_items(conn, csv_file_path):
    """Import menu items from CSV, grouping by product and creating variants for sizes."""
    logger.info("Importing menu items with variant support...")
    cursor = conn.cursor()

    item_count = 0
    skipped_count = 0

    # Step 1: Read all rows and group by (base name, category)
    groups = {}
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row_num, row in enumerate(reader, 1):
                try:
                    # Extract base name and category - safely get values
                    name = safe_get_field(row, 'Name')
                    category_id = safe_get_field(row, 'Category Name')
                    
                    if not name or not category_id:
                        logger.warning(f"Row {row_num}: Missing name or category - skipping")
                        skipped_count += 1
                        continue

                    # Try to get size from 'Size' field, else parse from name if present
                    size = safe_get_field(row, 'Size')
                    base_name = name
                    
                    if not size and '(' in name and name.endswith(')'):
                        # e.g. "Pizza Margherita (Large)"
                        base_name = name[:name.rfind('(')].strip()
                        size = name[name.rfind('(')+1:-1].strip()

                    # Group key: (base_name, category_id)
                    group_key = (base_name, category_id)
                    if group_key not in groups:
                        groups[group_key] = []
                    groups[group_key].append((row, size, row_num))
                    
                except Exception as e:
                    logger.error(f"Error grouping item in row {row_num}: {str(e)}")
                    skipped_count += 1
                    continue

        # Step 2: For each group, create a single menu item with variants
        for (base_name, category_id), items in groups.items():
            try:
                # Collect sizes and prices
                size_options = []
                size_prices = {}
                
                # Use the first item as the base for shared fields
                first_row, first_size, first_row_num = items[0]
                
                # Extract data with safe methods
                description = safe_get_field(first_row, 'Description')
                image_url = safe_get_field(first_row, 'Image URL') or 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTcWKAPNpBPrNwnMLN98hVyg5Vs1x3GOpALlg&s'
                available = safe_bool(first_row.get('Available', ''), True)
                popular = safe_bool(first_row.get('Popular', ''), False)
                prep_time = safe_int(first_row.get('Preparation Time', ''), 15)
                
                # Translations
                name_translations = {
                    'name_az': safe_get_field(first_row, 'Name AZ') or base_name,
                    'name_en': safe_get_field(first_row, 'Name EN') or base_name,
                    'name_ru': safe_get_field(first_row, 'Name RU') or base_name,
                    'name_tr': safe_get_field(first_row, 'Name TR') or base_name,
                    'name_ar': safe_get_field(first_row, 'Name AR') or base_name,
                    'name_hi': safe_get_field(first_row, 'Name HI') or base_name,
                    'name_fr': safe_get_field(first_row, 'Name FR') or base_name,
                    'name_it': safe_get_field(first_row, 'Name IT') or base_name,
                }
                
                description_translations = {
                    'description_az': safe_get_field(first_row, 'Description AZ'),
                    'description_en': safe_get_field(first_row, 'Description EN'),
                    'description_ru': safe_get_field(first_row, 'Description RU'),
                    'description_tr': safe_get_field(first_row, 'Description TR'),
                    'description_ar': safe_get_field(first_row, 'Description AR'),
                    'description_hi': safe_get_field(first_row, 'Description HI'),
                    'description_fr': safe_get_field(first_row, 'Description FR'),
                    'description_it': safe_get_field(first_row, 'Description IT'),
                }

                # Collect all sizes and prices
                price_for_main = 0.0
                default_size = ""
                
                for row, size, row_num in items:
                    try:
                        price = safe_float(row.get('Price', ''), 0.0)
                        if size and size not in size_options:
                            size_options.append(size)
                        if size:
                            size_prices[size] = price
                        else:
                            # If no size, treat as default
                            price_for_main = price
                    except Exception as e:
                        logger.warning(f"Error processing price for row {row_num}: {str(e)}")
                        continue

                # Determine default configuration
                if size_options:
                    default_size = size_options[0]
                    price_for_main = size_prices.get(default_size, 0.0)
                else:
                    # No sizes, use price from first item
                    price_for_main = safe_float(first_row.get('Price', ''), 0.0)

                # Generate a unique ID for the group
                item_id = safe_get_field(first_row, 'ID') or f"{base_name.replace(' ', '_')}_{category_id}"
                
                # Prepare timestamps
                created_at = datetime.now().isoformat()
                updated_at = created_at

                # Insert menu item with variants
                cursor.execute('''
                    INSERT INTO menu_items (
                        id, name, description, category_id, price, image_url, 
                        available, popular, preparation_time, created_at, updated_at,
                        name_az, name_en, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
                        description_az, description_en, description_ru, description_tr,
                        description_ar, description_hi, description_fr, description_it,
                        size_options, size_prices, default_size
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item_id,
                    base_name,
                    description,
                    category_id,
                    price_for_main,
                    image_url,
                    available,
                    popular,
                    prep_time,
                    created_at,
                    updated_at,
                    name_translations['name_az'],
                    name_translations['name_en'],
                    name_translations['name_ru'],
                    name_translations['name_tr'],
                    name_translations['name_ar'],
                    name_translations['name_hi'],
                    name_translations['name_fr'],
                    name_translations['name_it'],
                    description_translations['description_az'],
                    description_translations['description_en'],
                    description_translations['description_ru'],
                    description_translations['description_tr'],
                    description_translations['description_ar'],
                    description_translations['description_hi'],
                    description_translations['description_fr'],
                    description_translations['description_it'],
                    json.dumps(size_options, ensure_ascii=False),
                    json.dumps(size_prices, ensure_ascii=False),
                    default_size
                ))
                item_count += 1
                logger.debug(f"Imported: {base_name} (category: {category_id})")
                
            except Exception as e:
                logger.error(f"Error importing group {base_name} ({category_id}): {str(e)}")
                skipped_count += 1
                continue

        conn.commit()
        logger.info(f"Successfully imported {item_count} menu items (grouped with variants)")
        if skipped_count > 0:
            logger.warning(f"Skipped {skipped_count} items/groups due to errors")
            
    except Exception as e:
        logger.error(f"Error during import: {str(e)}")
        conn.rollback()
        raise

def verify_import(conn):
    """Verify the imported data"""
    logger.info("Verifying imported data...")
    cursor = conn.cursor()
    
    try:
        # Count categories
        cursor.execute('SELECT COUNT(*) FROM categories')
        category_count = cursor.fetchone()[0]
        logger.info(f"Categories in database: {category_count}")
        
        # Count menu items
        cursor.execute('SELECT COUNT(*) FROM menu_items')
        item_count = cursor.fetchone()[0]
        logger.info(f"Menu items in database: {item_count}")
        
        # Show categories with item counts
        cursor.execute('SELECT id, name FROM categories ORDER BY id')
        categories = cursor.fetchall()
        logger.info("Categories:")
        for cat_id, cat_name in categories:
            cursor.execute('SELECT COUNT(*) FROM menu_items WHERE category_id = ?', (cat_id,))
            item_count = cursor.fetchone()[0]
            logger.info(f"  - {cat_name}: {item_count} items")
            
        # Check for items with size variants
        cursor.execute('SELECT COUNT(*) FROM menu_items WHERE size_options != "[]" AND size_options IS NOT NULL')
        items_with_sizes = cursor.fetchone()[0]
        logger.info(f"Items with size variants: {items_with_sizes}")
        
    except Exception as e:
        logger.error(f"Error during verification: {str(e)}")

def print_summary():
    """Print import summary"""
    try:
        conn = sqlite3.connect('data/menu.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM categories")
        cat_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM menu_items")
        item_count = cursor.fetchone()[0]
        
        # Check multilingual data
        cursor.execute("SELECT COUNT(*) FROM menu_items WHERE name_en IS NOT NULL AND name_en != ''")
        translated_items = cursor.fetchone()[0]
        
        # Check size variants
        cursor.execute("SELECT COUNT(*) FROM menu_items WHERE size_options != '[]' AND size_options IS NOT NULL")
        items_with_sizes = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"\n=== Import Summary ===")
        print(f"Categories imported: {cat_count}")
        print(f"Menu items imported: {item_count}")
        print(f"Items with translations: {translated_items}")
        print(f"Items with size variants: {items_with_sizes}")
        print(f"Languages supported: 8 (EN, AZ, RU, TR, AR, HI, FR, IT)")
        print(f"======================\n")
        
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")

def main():
    """Main import function"""
    csv_file_path = 'data/menu_items_export.csv'
    
    if not os.path.exists(csv_file_path):
        logger.error(f"CSV file not found: {csv_file_path}")
        sys.exit(1)
    
    logger.info("Starting fixed menu import from CSV...")
    logger.info(f"CSV file: {csv_file_path}")
    
    try:
        # Connect to database
        conn = connect_database()
        logger.info("Connected to database successfully")
        
        # Clear existing data
        clear_existing_data(conn)
        
        # Create categories
        create_categories(conn, csv_file_path)
        
        # Import menu items
        import_menu_items(conn, csv_file_path)
        
        # Verify import
        verify_import(conn)
        
        # Print summary
        print_summary()
        
        conn.close()
        logger.info("Menu import completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"Import failed: {str(e)}")
        return False

if __name__ == "__main__":
    main()

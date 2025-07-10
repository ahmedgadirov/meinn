#!/usr/bin/env python3
"""
Comprehensive Menu Data Import Script for Meinn Restaurant
Updated to import from the comprehensive CSV file with all 361 menu items
Uses the same source as import_comprehensive_menu.py for consistency
"""

import os
import sys
import sqlite3
import csv
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('menu_import.log')
    ]
)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with proper schema"""
    try:
        # Add project root to Python path
        project_root = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_root)
        
        # Import the init_db module
        from src.db.init_db import init_database as init_db
        
        logger.info("Initializing database schema...")
        init_db()
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def connect_database():
    """Connect to the menu database"""
    db_path = 'menu_data.db'
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
    
    # Clear tables in correct order (respecting foreign keys)
    cursor.execute('DELETE FROM item_pairings')
    cursor.execute('DELETE FROM item_details')
    cursor.execute('DELETE FROM order_items')
    cursor.execute('DELETE FROM orders')
    cursor.execute('DELETE FROM menu_items')
    cursor.execute('DELETE FROM categories')
    
    conn.commit()
    logger.info("Existing data cleared successfully")

def create_categories(conn, csv_file_path):
    """Extract and create unique categories from CSV"""
    logger.info("Creating categories...")
    cursor = conn.cursor()
    
    categories = {}
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            category_name = row['Category Name'].strip()
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
    
    # Insert categories
    for category_id, category_data in categories.items():
        cursor.execute('''
            INSERT INTO categories (
                id, name, description, image_url,
                name_az, name_en, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
                description_az, description_en, description_ru, description_tr, 
                description_ar, description_hi, description_fr, description_it
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        ))
    
    conn.commit()
    logger.info(f"Created {len(categories)} categories")

def import_menu_items(conn, csv_file_path):
    """Import menu items from CSV, grouping by product and creating variants for sizes."""
    import json
    logger.info("Importing menu items with variant support...")
    cursor = conn.cursor()

    item_count = 0
    skipped_count = 0

    # Step 1: Read all rows and group by (base name, category)
    groups = {}
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                # Extract base name and category
                name = row['Name'].strip()
                category_id = row['Category Name'].strip()
                if not name or not category_id:
                    skipped_count += 1
                    continue

                # Try to get size from 'Size' field, else parse from name if present
                size = row.get('Size', '').strip()
                base_name = name
                if not size and '(' in name and name.endswith(')'):
                    # e.g. "Pizza Margherita (Large)"
                    base_name = name[:name.rfind('(')].strip()
                    size = name[name.rfind('(')+1:-1].strip()

                # Fallback: if still no size, use empty string
                size = size or ""

                # Group key: (base_name, category_id)
                group_key = (base_name, category_id)
                if group_key not in groups:
                    groups[group_key] = []
                groups[group_key].append((row, size))
            except Exception as e:
                logger.error(f"Error grouping item: {str(e)}")
                skipped_count += 1
                continue

    # Step 2: For each group, create a single menu item with variants
    for (base_name, category_id), items in groups.items():
        try:
            # Collect sizes and prices
            size_options = []
            size_prices = {}
            available = False
            popular = False
            prep_time = 15
            description = ""
            image_url = ""
            name_translations = {}
            description_translations = {}
            created_at = datetime.now().isoformat()
            updated_at = datetime.now().isoformat()
            default_size = ""
            price_for_main = 0.0

            # Use the first item as the base for shared fields
            first_row, first_size = items[0]
            description = first_row.get('Description', '').strip()
            image_url = first_row.get('Image URL', '').strip() or 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTcWKAPNpBPrNwnMLN98hVyg5Vs1x3GOpALlg&s'
            available = first_row['Available'].strip().upper() in ('TRUE', '1', 'YES')
            popular = first_row['Popular'].strip().upper() in ('TRUE', '1', 'YES') if first_row['Popular'].strip() else False
            try:
                prep_time = int(first_row['Preparation Time']) if first_row['Preparation Time'].strip() else 15
            except Exception:
                prep_time = 15

            # Translations
            name_translations = {
                'name_az': first_row.get('Name AZ', '').strip() or base_name,
                'name_en': first_row.get('Name EN', '').strip() or base_name,
                'name_ru': first_row.get('Name RU', '').strip() or base_name,
                'name_tr': first_row.get('Name TR', '').strip() or base_name,
                'name_ar': first_row.get('Name AR', '').strip() or base_name,
                'name_hi': first_row.get('Name HI', '').strip() or base_name,
                'name_fr': first_row.get('Name FR', '').strip() or base_name,
                'name_it': first_row.get('Name IT', '').strip() or base_name,
            }
            description_translations = {
                'description_az': first_row.get('Description AZ', '').strip(),
                'description_en': first_row.get('Description EN', '').strip(),
                'description_ru': first_row.get('Description RU', '').strip(),
                'description_tr': first_row.get('Description TR', '').strip(),
                'description_ar': first_row.get('Description AR', '').strip(),
                'description_hi': first_row.get('Description HI', '').strip(),
                'description_fr': first_row.get('Description FR', '').strip(),
                'description_it': first_row.get('Description IT', '').strip(),
            }

            # Collect all sizes and prices
            for row, size in items:
                try:
                    price = float(row['Price']) if row['Price'].strip() else 0.0
                except Exception:
                    price = 0.0
                if size and size not in size_options:
                    size_options.append(size)
                if size:
                    size_prices[size] = price
                else:
                    # If no size, treat as default
                    default_size = ""
                    price_for_main = price

            # If only one item and no size, treat as normal product
            if not size_options:
                size_options = []
                size_prices = {}
                default_size = ""
                price_for_main = float(first_row['Price']) if first_row['Price'].strip() else 0.0
            else:
                default_size = size_options[0]
                price_for_main = size_prices[default_size]

            # Generate a unique ID for the group (use first item's ID)
            item_id = first_row['ID'].strip()

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
        except Exception as e:
            logger.error(f"Error importing group {base_name} ({category_id}): {str(e)}")
            skipped_count += 1
            continue

    conn.commit()
    logger.info(f"Successfully imported {item_count} menu items (grouped with variants)")
    if skipped_count > 0:
        logger.warning(f"Skipped {skipped_count} items/groups due to errors")

def verify_import(conn):
    """Verify the imported data"""
    logger.info("Verifying imported data...")
    cursor = conn.cursor()
    
    # Count categories
    cursor.execute('SELECT COUNT(*) FROM categories')
    category_count = cursor.fetchone()[0]
    logger.info(f"Categories in database: {category_count}")
    
    # Count menu items
    cursor.execute('SELECT COUNT(*) FROM menu_items')
    item_count = cursor.fetchone()[0]
    logger.info(f"Menu items in database: {item_count}")
    
    # Show categories
    cursor.execute('SELECT id, name FROM categories ORDER BY id')
    categories = cursor.fetchall()
    logger.info("Categories:")
    for cat_id, cat_name in categories:
        cursor.execute('SELECT COUNT(*) FROM menu_items WHERE category_id = ?', (cat_id,))
        item_count = cursor.fetchone()[0]
        logger.info(f"  - {cat_name}: {item_count} items")

def print_summary():
    """Print import summary"""
    try:
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM categories")
        cat_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM menu_items")
        item_count = cursor.fetchone()[0]
        
        # Check multilingual data
        cursor.execute("SELECT COUNT(*) FROM menu_items WHERE name_en IS NOT NULL AND name_en != ''")
        translated_items = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"\n=== Import Summary ===")
        print(f"Categories imported: {cat_count}")
        print(f"Menu items imported: {item_count}")
        print(f"Items with translations: {translated_items}")
        print(f"Languages supported: 8 (EN, AZ, RU, TR, AR, HI, FR, IT)")
        print(f"======================\n")
        
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")

def main():
    """Main import function"""
    import os
csv_file_path = os.getenv('CSV_FILE_PATH', 'data/menu_items_export.csv')
    
    if not os.path.exists(csv_file_path):
        logger.error(f"CSV file not found: {csv_file_path}")
        sys.exit(1)
    
    logger.info("Starting comprehensive menu import from CSV...")
    logger.info(f"CSV file: {csv_file_path}")
    
    try:
        # Initialize database schema
        init_database()
        
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

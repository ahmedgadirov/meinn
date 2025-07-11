#!/usr/bin/env python3
"""
Comprehensive Menu Data Import Script for Meinn Restaurant
Updates menu data from the exported CSV file with full multilingual support
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
    """Import menu items from CSV"""
    logger.info("Importing menu items...")
    cursor = conn.cursor()
    
    item_count = 0
    skipped_count = 0
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                # Extract basic data
                item_id = row['ID'].strip()
                name = row['Name'].strip()
                category_id = row['Category Name'].strip()
                
                if not item_id or not name or not category_id:
                    logger.warning(f"Skipping row with missing required data: ID={item_id}, Name={name}, Category={category_id}")
                    skipped_count += 1
                    continue
                
                # Parse price
                try:
                    price = float(row['Price']) if row['Price'].strip() else 0.0
                except ValueError:
                    logger.warning(f"Invalid price for item {item_id}: {row['Price']}")
                    price = 0.0
                
                # Parse boolean fields
                available = row['Available'].strip().upper() in ('TRUE', '1', 'YES')
                popular = row['Popular'].strip().upper() in ('TRUE', '1', 'YES') if row['Popular'].strip() else False
                
                # Parse preparation time
                try:
                    prep_time = int(row['Preparation Time']) if row['Preparation Time'].strip() else 15
                except ValueError:
                    prep_time = 15
                
                # Get description and image
                description = row.get('Description', '').strip()
                image_url = row.get('Image URL', '').strip() or 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTcWKAPNpBPrNwnMLN98hVyg5Vs1x3GOpALlg&s'
                size = row.get('Size', '').strip()
                
                # Get all translations
                name_translations = {
                    'name_az': row.get('Name AZ', '').strip() or name,
                    'name_en': row.get('Name EN', '').strip() or name,
                    'name_ru': row.get('Name RU', '').strip() or name,
                    'name_tr': row.get('Name TR', '').strip() or name,
                    'name_ar': row.get('Name AR', '').strip() or name,
                    'name_hi': row.get('Name HI', '').strip() or name,
                    'name_fr': row.get('Name FR', '').strip() or name,
                    'name_it': row.get('Name IT', '').strip() or name,
                }
                
                description_translations = {
                    'description_az': row.get('Description AZ', '').strip(),
                    'description_en': row.get('Description EN', '').strip(),
                    'description_ru': row.get('Description RU', '').strip(),
                    'description_tr': row.get('Description TR', '').strip(),
                    'description_ar': row.get('Description AR', '').strip(),
                    'description_hi': row.get('Description HI', '').strip(),
                    'description_fr': row.get('Description FR', '').strip(),
                    'description_it': row.get('Description IT', '').strip(),
                }
                
                # Create display name with size if available
                display_name = f"{name} ({size})" if size else name
                
                # Insert menu item
                cursor.execute('''
                    INSERT INTO menu_items (
                        id, name, description, category_id, price, image_url, 
                        available, popular, preparation_time, created_at, updated_at,
                        name_az, name_en, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
                        description_az, description_en, description_ru, description_tr,
                        description_ar, description_hi, description_fr, description_it
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item_id,
                    display_name,
                    description,
                    category_id,
                    price,
                    image_url,
                    available,
                    popular,
                    prep_time,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
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
                    description_translations['description_it']
                ))
                
                item_count += 1
                
            except Exception as e:
                logger.error(f"Error importing item {row.get('ID', 'unknown')}: {str(e)}")
                skipped_count += 1
                continue
    
    conn.commit()
    logger.info(f"Successfully imported {item_count} menu items")
    if skipped_count > 0:
        logger.warning(f"Skipped {skipped_count} items due to errors")

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
    
    # Check for items without categories
    cursor.execute('''
        SELECT COUNT(*) FROM menu_items 
        WHERE category_id NOT IN (SELECT id FROM categories)
    ''')
    orphaned_items = cursor.fetchone()[0]
    if orphaned_items > 0:
        logger.warning(f"Found {orphaned_items} items without valid categories")

def main():
    """Main import function"""
    csv_file_path = '/home/ahmd/Desktop/menu pizza inn/menu_items_export.csv'
    
    if not os.path.exists(csv_file_path):
        logger.error(f"CSV file not found: {csv_file_path}")
        sys.exit(1)
    
    logger.info("Starting comprehensive menu import...")
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
        
        conn.close()
        logger.info("Menu import completed successfully!")
        
    except Exception as e:
        logger.error(f"Import failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

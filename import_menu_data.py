#!/usr/bin/env python3
"""
Import menu data from JSON export for deployment.
This script loads data from menu_translations_export.json and populates
the database with categories and menu items including all translations.
"""

import json
import sqlite3
import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("meinn_ai.menu_import")

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

def import_from_json():
    """Import menu data from JSON export file"""
    try:
        # Check if JSON file exists
        json_file = 'menu_translations_export.json'
        if not os.path.exists(json_file):
            logger.error(f"JSON export file not found: {json_file}")
            return False
        
        # Load JSON data
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        logger.info(f"Loaded export data from {data.get('export_date', 'unknown date')}")
        
        # Connect to database
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        # Clear existing data
        logger.info("Cleaning existing data...")
        cursor.execute("DELETE FROM order_items")
        cursor.execute("DELETE FROM orders") 
        cursor.execute("DELETE FROM item_details")
        cursor.execute("DELETE FROM item_pairings")
        cursor.execute("DELETE FROM menu_items")
        cursor.execute("DELETE FROM categories")
        
        # Import categories
        logger.info("Importing categories...")
        categories = data.get('categories', [])
        for category in categories:
            cursor.execute('''
                INSERT INTO categories (
                    id, name, description, image_url,
                    name_az, name_en, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
                    description_az, description_en, description_ru, description_tr, 
                    description_ar, description_hi, description_fr, description_it
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                category['id'],
                category['name'],
                category['description'], 
                category['image_url'],
                category.get('name_az', ''),
                category.get('name_en', ''),
                category.get('name_ru', ''),
                category.get('name_tr', ''),
                category.get('name_ar', ''),
                category.get('name_hi', ''),
                category.get('name_fr', ''),
                category.get('name_it', ''),
                category.get('description_az', ''),
                category.get('description_en', ''),
                category.get('description_ru', ''),
                category.get('description_tr', ''),
                category.get('description_ar', ''),
                category.get('description_hi', ''),
                category.get('description_fr', ''),
                category.get('description_it', '')
            ))
        
        logger.info(f"Imported {len(categories)} categories")
        
        # Import menu items
        logger.info("Importing menu items...")
        menu_items = data.get('menu_items', [])
        for item in menu_items:
            cursor.execute('''
                INSERT INTO menu_items (
                    id, name, description, category_id, price, image_url,
                    available, popular, preparation_time, created_at, updated_at,
                    name_az, name_en, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
                    description_az, description_en, description_ru, description_tr,
                    description_ar, description_hi, description_fr, description_it
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['id'],
                item['name'],
                item['description'],
                item['category_id'],
                item['price'],
                item['image_url'],
                item.get('available', 1),
                item.get('popular', 0),
                item.get('preparation_time', 15),
                item.get('created_at', datetime.now().isoformat()),
                item.get('updated_at', datetime.now().isoformat()),
                item.get('name_az', ''),
                item.get('name_en', ''),
                item.get('name_ru', ''),
                item.get('name_tr', ''),
                item.get('name_ar', ''),
                item.get('name_hi', ''),
                item.get('name_fr', ''),
                item.get('name_it', ''),
                item.get('description_az', ''),
                item.get('description_en', ''),
                item.get('description_ru', ''),
                item.get('description_tr', ''),
                item.get('description_ar', ''),
                item.get('description_hi', ''),
                item.get('description_fr', ''),
                item.get('description_it', '')
            ))
            
            # Add item details with empty defaults
            cursor.execute('''
                INSERT INTO item_details (item_id, allergens, ingredients, nutrition)
                VALUES (?, ?, ?, ?)
            ''', (
                item['id'],
                '[]',  # Empty allergens
                '[]',  # Empty ingredients  
                '{"calories": 0, "protein": 0, "carbs": 0, "fat": 0}'  # Basic nutrition
            ))
        
        logger.info(f"Imported {len(menu_items)} menu items")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        logger.info("Menu data import completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error importing menu data: {str(e)}")
        return False

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
    try:
        logger.info("Starting menu data import from JSON...")
        
        # Initialize database schema
        init_database()
        
        # Import data from JSON
        success = import_from_json()
        
        if success:
            print_summary()
            logger.info("Menu data import completed successfully!")
        else:
            logger.error("Menu data import failed!")
        
        return success
        
    except Exception as e:
        logger.error(f"Import failed: {str(e)}")
        return False

if __name__ == "__main__":
    main()

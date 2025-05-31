#!/usr/bin/env python3
"""
Import updated menu data from CSV files into the database.
Handles multilingual content and updates existing data.
"""

import csv
import sqlite3
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("meinn_ai.menu_import")

def clean_database():
    """Clean existing menu data before importing new data"""
    try:
        # Connect to main menu database
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        # Delete existing data (in correct order due to foreign keys)
        cursor.execute("DELETE FROM item_pairings")
        cursor.execute("DELETE FROM item_details")
        cursor.execute("DELETE FROM order_items")
        cursor.execute("DELETE FROM orders")
        cursor.execute("DELETE FROM menu_items")
        cursor.execute("DELETE FROM categories")
        
        conn.commit()
        conn.close()
        
        # Also clean translation database
        if os.path.exists('translation_data.db'):
            trans_conn = sqlite3.connect('translation_data.db')
            trans_cursor = trans_conn.cursor()
            
            trans_cursor.execute("DELETE FROM menu_translations")
            trans_cursor.execute("DELETE FROM category_translations")
            
            trans_conn.commit()
            trans_conn.close()
        
        logger.info("Existing menu data cleaned successfully")
        
    except Exception as e:
        logger.error(f"Error cleaning database: {str(e)}")
        raise

def import_categories():
    """Import categories from CSV file"""
    try:
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        # Initialize translation database connection
        trans_conn = sqlite3.connect('translation_data.db')
        trans_cursor = trans_conn.cursor()
        
        # Create translation tables if they don't exist
        trans_cursor.execute('''
        CREATE TABLE IF NOT EXISTS category_translations (
            category_id TEXT NOT NULL,
            language TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            PRIMARY KEY (category_id, language)
        )
        ''')
        
        with open('menu_categories_export.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                category_id = row['ID']
                
                # Insert main category record
                cursor.execute('''
                    INSERT INTO categories (id, name, description, image_url)
                    VALUES (?, ?, ?, ?)
                ''', (
                    category_id,
                    row['Name EN'],  # Use English as default
                    row['Description EN'],
                    row['Image URL']
                ))
                
                # Insert translations
                languages = {
                    'en': {'name': row['Name EN'], 'desc': row['Description EN']},
                    'az': {'name': row['Name AZ'], 'desc': row['Description AZ']},
                    'ru': {'name': row['Name RU'], 'desc': row['Description RU']},
                    'tr': {'name': row['Name TR'], 'desc': row['Description TR']},
                    'ar': {'name': row['Name AR'], 'desc': row['Description AR']},
                    'hi': {'name': row['Name HI'], 'desc': row['Description HI']},
                    'fr': {'name': row['Name FR'], 'desc': row['Description FR']},
                    'it': {'name': row['Name IT'], 'desc': row['Description IT']}
                }
                
                for lang, data in languages.items():
                    if data['name']:  # Only insert if translation exists
                        trans_cursor.execute('''
                            INSERT INTO category_translations (category_id, language, name, description)
                            VALUES (?, ?, ?, ?)
                        ''', (category_id, lang, data['name'], data['desc']))
        
        conn.commit()
        trans_conn.commit()
        conn.close()
        trans_conn.close()
        
        logger.info("Categories imported successfully")
        
    except Exception as e:
        logger.error(f"Error importing categories: {str(e)}")
        raise

def import_menu_items():
    """Import menu items from CSV file"""
    try:
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        # Initialize translation database connection
        trans_conn = sqlite3.connect('translation_data.db')
        trans_cursor = trans_conn.cursor()
        
        # Create translation tables if they don't exist
        trans_cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_translations (
            item_id TEXT NOT NULL,
            language TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            PRIMARY KEY (item_id, language)
        )
        ''')
        
        with open('menu_items_export.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                item_id = row['ID']
                
                # Convert string boolean to integer
                available = 1 if row['Available'] == '1' else 0
                popular = 1 if row['Popular'] == '1' else 0
                
                # Parse preparation time
                prep_time = int(row['Preparation Time']) if row['Preparation Time'] else 15
                
                # Parse price
                price = float(row['Price']) if row['Price'] else 0.0
                
                # Insert main menu item record
                cursor.execute('''
                    INSERT INTO menu_items (
                        id, name, description, category_id, price, image_url, 
                        available, popular, preparation_time, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item_id,
                    row['Name EN'],  # Use English as default
                    row['Description EN'],
                    row['Category ID'],
                    price,
                    row['Image URL'],
                    available,
                    popular,
                    prep_time,
                    row.get('Created At', datetime.now().isoformat()),
                    row.get('Updated At', datetime.now().isoformat())
                ))
                
                # Insert item details (basic nutrition info)
                cursor.execute('''
                    INSERT INTO item_details (item_id, allergens, ingredients, nutrition)
                    VALUES (?, ?, ?, ?)
                ''', (
                    item_id,
                    '[]',  # Empty allergens for now
                    '[]',  # Empty ingredients for now
                    '{"calories": 0, "protein": 0, "carbs": 0, "fat": 0}'  # Basic nutrition
                ))
                
                # Insert translations
                languages = {
                    'en': {'name': row['Name EN'], 'desc': row['Description EN']},
                    'az': {'name': row['Name AZ'], 'desc': row['Description AZ']},
                    'ru': {'name': row['Name RU'], 'desc': row['Description RU']},
                    'tr': {'name': row['Name TR'], 'desc': row['Description TR']},
                    'ar': {'name': row['Name AR'], 'desc': row['Description AR']},
                    'hi': {'name': row['Name HI'], 'desc': row['Description HI']},
                    'fr': {'name': row['Name FR'], 'desc': row['Description FR']},
                    'it': {'name': row['Name IT'], 'desc': row['Description IT']}
                }
                
                for lang, data in languages.items():
                    if data['name']:  # Only insert if translation exists
                        trans_cursor.execute('''
                            INSERT INTO menu_translations (item_id, language, name, description)
                            VALUES (?, ?, ?, ?)
                        ''', (item_id, lang, data['name'], data['desc']))
        
        conn.commit()
        trans_conn.commit()
        conn.close()
        trans_conn.close()
        
        logger.info("Menu items imported successfully")
        
    except Exception as e:
        logger.error(f"Error importing menu items: {str(e)}")
        raise

def create_sample_pairings():
    """Create some sample item pairings for recommendations"""
    try:
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        # Get some items to create pairings
        cursor.execute("SELECT id, category_id FROM menu_items LIMIT 20")
        items = cursor.fetchall()
        
        # Create some logical pairings
        pairings = []
        
        for i, (item_id, category_id) in enumerate(items):
            # Pair each item with 2-3 other items
            for j in range(min(3, len(items) - i - 1)):
                if i + j + 1 < len(items):
                    paired_id = items[i + j + 1][0]
                    score = 0.7 + (j * 0.1)  # Decreasing scores
                    pairings.append((item_id, paired_id, score))
        
        # Insert pairings
        cursor.executemany('''
            INSERT INTO item_pairings (item_id, paired_with_id, score)
            VALUES (?, ?, ?)
        ''', pairings)
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created {len(pairings)} sample pairings")
        
    except Exception as e:
        logger.error(f"Error creating sample pairings: {str(e)}")
        raise

def main():
    """Main import function"""
    try:
        logger.info("Starting menu data import...")
        
        # Check if CSV files exist
        if not os.path.exists('menu_categories_export.csv'):
            logger.error("menu_categories_export.csv file not found")
            return
            
        if not os.path.exists('menu_items_export.csv'):
            logger.error("menu_items_export.csv file not found")
            return
        
        # Initialize databases
        from src.db.init_db import init_database
        init_database()
        
        # Clean existing data
        clean_database()
        
        # Import new data
        import_categories()
        import_menu_items()
        create_sample_pairings()
        
        logger.info("Menu data import completed successfully!")
        
        # Print summary
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM categories")
        cat_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM menu_items")
        item_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM item_pairings")
        pair_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"\n=== Import Summary ===")
        print(f"Categories imported: {cat_count}")
        print(f"Menu items imported: {item_count}")
        print(f"Item pairings created: {pair_count}")
        print(f"======================")
        
    except Exception as e:
        logger.error(f"Import failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()

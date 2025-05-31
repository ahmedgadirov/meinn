#!/usr/bin/env python3
"""
Import menu data from CSV file into the database.
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

def init_database():
    """Initialize database with proper schema"""
    try:
        # Initialize menu database
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        # Create categories table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            image_url TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create menu_items table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category_id TEXT,
            price REAL,
            image_url TEXT,
            available INTEGER DEFAULT 1,
            popular INTEGER DEFAULT 0,
            preparation_time INTEGER DEFAULT 15,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
        ''')
        
        # Create item_details table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS item_details (
            item_id TEXT PRIMARY KEY,
            allergens TEXT DEFAULT '[]',
            ingredients TEXT DEFAULT '[]',
            nutrition TEXT DEFAULT '{}',
            FOREIGN KEY (item_id) REFERENCES menu_items (id)
        )
        ''')
        
        # Create translation tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_translations (
            item_id TEXT NOT NULL,
            language TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            PRIMARY KEY (item_id, language),
            FOREIGN KEY (item_id) REFERENCES menu_items (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS category_translations (
            category_id TEXT NOT NULL,
            language TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            PRIMARY KEY (category_id, language),
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database schema initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def clean_database():
    """Clean existing menu data"""
    try:
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        # Delete in proper order due to foreign keys
        cursor.execute("DELETE FROM menu_translations")
        cursor.execute("DELETE FROM category_translations")
        cursor.execute("DELETE FROM item_details")
        cursor.execute("DELETE FROM menu_items")
        cursor.execute("DELETE FROM categories")
        
        conn.commit()
        conn.close()
        logger.info("Existing menu data cleaned successfully")
        
    except Exception as e:
        logger.error(f"Error cleaning database: {str(e)}")
        raise

def import_menu_data():
    """Import menu data from CSV"""
    try:
        if not os.path.exists('menu_items_data.csv'):
            logger.error("menu_items_data.csv file not found")
            return False
        
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        # Keep track of categories we've seen
        categories_added = set()
        
        with open('menu_items_data.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # Extract data
                item_id = row['ID']
                category_id = row['Category ID']
                category_name = row['Category Name']
                
                # Add category if not already added
                if category_id not in categories_added:
                    cursor.execute('''
                        INSERT OR IGNORE INTO categories (id, name, description, image_url)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        category_id,
                        category_name,
                        f"{category_name} dishes and specialties",
                        "/spinner.svg"
                    ))
                    categories_added.add(category_id)
                    
                    # Add category translations
                    languages = {
                        'en': category_name,
                        'az': category_name,  # Using same for now
                        'ru': category_name,
                        'tr': category_name,
                        'ar': category_name,
                        'hi': category_name,
                        'fr': category_name,
                        'it': category_name
                    }
                    
                    for lang, name in languages.items():
                        cursor.execute('''
                            INSERT OR IGNORE INTO category_translations (category_id, language, name, description)
                            VALUES (?, ?, ?, ?)
                        ''', (category_id, lang, name, f"{name} dishes and specialties"))
                
                # Parse menu item data
                available = 1 if row['Available'] == '1' else 0
                popular = 1 if row['Popular'] == '1' else 0
                prep_time = int(row['Preparation Time']) if row['Preparation Time'] else 15
                price = float(row['Price']) if row['Price'] else 0.0
                
                # Insert menu item
                cursor.execute('''
                    INSERT OR REPLACE INTO menu_items (
                        id, name, description, category_id, price, image_url, 
                        available, popular, preparation_time, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item_id,
                    row['Name EN'],  # Use English as default
                    row['Description EN'],
                    category_id,
                    price,
                    row['Image URL'],
                    available,
                    popular,
                    prep_time,
                    row.get('Created At', datetime.now().isoformat()),
                    row.get('Updated At', datetime.now().isoformat())
                ))
                
                # Insert item details
                cursor.execute('''
                    INSERT OR REPLACE INTO item_details (item_id, allergens, ingredients, nutrition)
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
                        cursor.execute('''
                            INSERT OR REPLACE INTO menu_translations (item_id, language, name, description)
                            VALUES (?, ?, ?, ?)
                        ''', (item_id, lang, data['name'], data['desc']))
        
        conn.commit()
        conn.close()
        
        logger.info("Menu data imported successfully")
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
        
        cursor.execute("SELECT COUNT(*) FROM menu_translations")
        trans_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"\n=== Import Summary ===")
        print(f"Categories imported: {cat_count}")
        print(f"Menu items imported: {item_count}")
        print(f"Translations created: {trans_count}")
        print(f"======================\n")
        
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")

def main():
    """Main import function"""
    try:
        logger.info("Starting menu data import...")
        
        # Initialize database schema
        init_database()
        
        # Clean existing data
        clean_database()
        
        # Import new data
        success = import_menu_data()
        
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

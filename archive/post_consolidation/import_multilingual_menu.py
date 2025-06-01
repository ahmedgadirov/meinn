#!/usr/bin/env python3
"""
Import multilingual menu data from CSV file into the database with direct columns.
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
logger = logging.getLogger("meinn_ai.multilingual_import")

def clean_database():
    """Clean existing menu data"""
    try:
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        # Delete in proper order due to foreign keys
        cursor.execute("DELETE FROM item_details")
        cursor.execute("DELETE FROM menu_items")
        cursor.execute("DELETE FROM categories")
        
        conn.commit()
        conn.close()
        logger.info("Existing menu data cleaned successfully")
        
    except Exception as e:
        logger.error(f"Error cleaning database: {str(e)}")
        raise

def import_multilingual_menu_data():
    """Import menu data from CSV with direct multilingual columns"""
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
                        INSERT OR IGNORE INTO categories (
                            id, name, description, image_url,
                            name_en, name_az, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
                            description_en, description_az, description_ru, description_tr, 
                            description_ar, description_hi, description_fr, description_it
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        category_id,
                        category_name,  # Default name
                        f"{category_name} dishes and specialties",  # Default description
                        "/spinner.svg",  # Default image
                        # Multilingual names (using category name for all languages for now)
                        category_name, category_name, category_name, category_name,
                        category_name, category_name, category_name, category_name,
                        # Multilingual descriptions
                        f"{category_name} dishes and specialties",
                        f"{category_name} yeməkləri və spesialitələri",
                        f"Блюда и фирменные блюда {category_name}",
                        f"{category_name} yemekleri ve özel lezzetleri",
                        f"أطباق ومأكولات خاصة {category_name}",
                        f"{category_name} व्यंजन और विशेषताएं",
                        f"Plats et spécialités {category_name}",
                        f"Piatti e specialità {category_name}"
                    ))
                    categories_added.add(category_id)
                    logger.info(f"Added category: {category_name}")
                
                # Parse menu item data
                available = 1 if row['Available'] == '1' else 0
                popular = 1 if row['Popular'] == '1' else 0
                prep_time = int(row['Preparation Time']) if row['Preparation Time'] else 15
                price = float(row['Price']) if row['Price'] else 0.0
                
                # Insert menu item with all multilingual data
                cursor.execute('''
                    INSERT OR REPLACE INTO menu_items (
                        id, name, description, category_id, price, image_url, 
                        available, popular, preparation_time, created_at, updated_at,
                        name_en, name_az, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
                        description_en, description_az, description_ru, description_tr, 
                        description_ar, description_hi, description_fr, description_it
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item_id,
                    row['Name EN'] or row['Name'],  # Use English as default
                    row['Description EN'] or row['Description'],  # Use English as default
                    category_id,
                    price,
                    row['Image URL'],
                    available,
                    popular,
                    prep_time,
                    row.get('Created At', datetime.now().isoformat()),
                    row.get('Updated At', datetime.now().isoformat()),
                    # Multilingual names
                    row['Name EN'] or row['Name'],
                    row['Name AZ'] or row['Name EN'] or row['Name'],
                    row['Name RU'] or row['Name EN'] or row['Name'],
                    row['Name TR'] or row['Name EN'] or row['Name'],
                    row['Name AR'] or row['Name EN'] or row['Name'],
                    row['Name HI'] or row['Name EN'] or row['Name'],
                    row['Name FR'] or row['Name EN'] or row['Name'],
                    row['Name IT'] or row['Name EN'] or row['Name'],
                    # Multilingual descriptions
                    row['Description EN'] or row['Description'],
                    row['Description AZ'] or row['Description EN'] or row['Description'],
                    row['Description RU'] or row['Description EN'] or row['Description'],
                    row['Description TR'] or row['Description EN'] or row['Description'],
                    row['Description AR'] or row['Description EN'] or row['Description'],
                    row['Description HI'] or row['Description EN'] or row['Description'],
                    row['Description FR'] or row['Description EN'] or row['Description'],
                    row['Description IT'] or row['Description EN'] or row['Description']
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
        
        conn.commit()
        conn.close()
        
        logger.info("Multilingual menu data imported successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error importing multilingual menu data: {str(e)}")
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
        languages = ['en', 'az', 'ru', 'tr', 'ar', 'hi', 'fr', 'it']
        lang_names = ['English', 'Azerbaijani', 'Russian', 'Turkish', 'Arabic', 'Hindi', 'French', 'Italian']
        
        print(f"\n=== Import Summary ===")
        print(f"Categories imported: {cat_count}")
        print(f"Menu items imported: {item_count}")
        print(f"\nTranslation Coverage:")
        
        for i, lang in enumerate(languages):
            cursor.execute(f"SELECT COUNT(*) FROM menu_items WHERE name_{lang} IS NOT NULL AND name_{lang} != ''")
            count = cursor.fetchone()[0]
            percentage = (count / item_count * 100) if item_count > 0 else 0
            print(f"  {lang_names[i]}: {count}/{item_count} items ({percentage:.1f}%)")
        
        print(f"======================\n")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")

def main():
    """Main import function"""
    try:
        logger.info("Starting multilingual menu data import...")
        
        # Clean existing data
        clean_database()
        
        # Import new data
        success = import_multilingual_menu_data()
        
        if success:
            print_summary()
            logger.info("Multilingual menu data import completed successfully!")
        else:
            logger.error("Multilingual menu data import failed!")
        
        return success
        
    except Exception as e:
        logger.error(f"Import failed: {str(e)}")
        return False

if __name__ == "__main__":
    main()

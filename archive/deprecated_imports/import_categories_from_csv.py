#!/usr/bin/env python3
"""
Import categories from the categories CSV file with proper translations
"""

import csv
import sqlite3
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("meinn_ai.categories_import")

def import_categories_from_csv():
    """Import categories from the categories CSV file"""
    csv_file = 'archive/generated_data/menu_categories_export.csv'
    
    try:
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        # First, clear existing categories
        cursor.execute("DELETE FROM categories")
        logger.info("Cleared existing categories")
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # Insert category with all translations
                cursor.execute('''
                    INSERT INTO categories (
                        id, name, description, image_url,
                        name_en, name_az, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
                        description_en, description_az, description_ru, description_tr, 
                        description_ar, description_hi, description_fr, description_it
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['ID'],
                    row['Name EN'],  # Use English as default
                    row['Description EN'],  # Use English as default
                    row['Image URL'],
                    # All name translations
                    row['Name EN'], row['Name AZ'], row['Name RU'], row['Name TR'],
                    row['Name AR'], row['Name HI'], row['Name FR'], row['Name IT'],
                    # All description translations
                    row['Description EN'], row['Description AZ'], row['Description RU'], row['Description TR'],
                    row['Description AR'], row['Description HI'], row['Description FR'], row['Description IT']
                ))
                
                logger.info(f"Imported category: {row['Name EN']} ({row['ID']})")
        
        conn.commit()
        conn.close()
        
        logger.info("Categories imported successfully from CSV!")
        return True
        
    except Exception as e:
        logger.error(f"Error importing categories: {str(e)}")
        return False

def verify_categories():
    """Verify the categories were imported correctly"""
    conn = sqlite3.connect('menu_data.db')
    cursor = conn.cursor()
    
    print("\nVerifying imported categories:")
    print("=" * 80)
    cursor.execute("SELECT id, name_en, name_az, name_ru FROM categories ORDER BY name_en")
    categories = cursor.fetchall()
    
    print(f"{'English':20} | {'Azerbaijani':25} | {'Russian':20}")
    print("-" * 80)
    for cat in categories:
        print(f"{cat[1]:20} | {cat[2]:25} | {cat[3]:20}")
    
    print(f"\nTotal categories imported: {len(categories)}")
    conn.close()

if __name__ == "__main__":
    print("Importing categories from CSV file...")
    success = import_categories_from_csv()
    
    if success:
        verify_categories()
    else:
        print("Failed to import categories!")

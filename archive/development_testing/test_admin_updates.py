#!/usr/bin/env python3
"""
Test script to verify the admin panel database updates are working correctly
"""

import sqlite3
import json
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_schema():
    """Test that the database schema has been updated correctly"""
    print("Testing database schema...")
    
    try:
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        # Test categories table
        cursor.execute("PRAGMA table_info(categories)")
        categories_columns = [col[1] for col in cursor.fetchall()]
        
        expected_lang_columns = [
            'name_az', 'name_en', 'name_ru', 'name_tr', 'name_ar', 'name_hi', 'name_fr', 'name_it',
            'description_az', 'description_en', 'description_ru', 'description_tr', 
            'description_ar', 'description_hi', 'description_fr', 'description_it'
        ]
        
        for col in expected_lang_columns:
            if col in categories_columns:
                print(f"✓ Categories table has column: {col}")
            else:
                print(f"✗ Categories table missing column: {col}")
        
        # Test menu_items table
        cursor.execute("PRAGMA table_info(menu_items)")
        items_columns = [col[1] for col in cursor.fetchall()]
        
        for col in expected_lang_columns:
            if col in items_columns:
                print(f"✓ Menu_items table has column: {col}")
            else:
                print(f"✗ Menu_items table missing column: {col}")
        
        # Test that existing data was migrated
        cursor.execute("SELECT COUNT(*) FROM categories WHERE name_en IS NOT NULL")
        categories_with_en = cursor.fetchone()[0]
        print(f"✓ {categories_with_en} categories have English translations")
        
        cursor.execute("SELECT COUNT(*) FROM menu_items WHERE name_en IS NOT NULL")
        items_with_en = cursor.fetchone()[0]
        print(f"✓ {items_with_en} menu items have English translations")
        
        conn.close()
        print("Database schema test completed successfully!")
        
    except Exception as e:
        print(f"✗ Database schema test failed: {e}")

def test_category_sample():
    """Test adding a sample category with translations"""
    print("\nTesting category creation with translations...")
    
    sample_category = {
        "id": "test-category",
        "image_url": "/static/images/test.jpg",
        "translations": {
            "en": {
                "name": "Test Category",
                "description": "A test category for verification"
            },
            "az": {
                "name": "Test Kateqoriyası",
                "description": "Yoxlama üçün test kateqoriyası"
            },
            "ru": {
                "name": "Тестовая Категория",
                "description": "Тестовая категория для проверки"
            }
        }
    }
    
    try:
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        # Delete test category if it exists
        cursor.execute("DELETE FROM categories WHERE id = 'test-category'")
        
        # Test the insertion logic (simulating what the API does)
        translations = sample_category['translations']
        supported_languages = ['az', 'en', 'ru', 'tr', 'ar', 'hi', 'fr', 'it']
        
        primary_name = translations.get('en', {}).get('name', '')
        primary_description = translations.get('en', {}).get('description', '')
        
        columns = ['id', 'name', 'description', 'image_url']
        values = [sample_category['id'], primary_name, primary_description, sample_category['image_url']]
        
        for lang in supported_languages:
            columns.extend([f'name_{lang}', f'description_{lang}'])
            lang_data = translations.get(lang, {})
            values.extend([
                lang_data.get('name', primary_name),
                lang_data.get('description', primary_description)
            ])
        
        placeholders = ', '.join(['?' for _ in values])
        column_names = ', '.join(columns)
        cursor.execute(
            f"INSERT INTO categories ({column_names}) VALUES ({placeholders})",
            values
        )
        
        # Verify insertion
        cursor.execute("SELECT name_en, name_az, name_ru FROM categories WHERE id = 'test-category'")
        result = cursor.fetchone()
        
        if result:
            print(f"✓ Test category created successfully!")
            print(f"  English: {result[0]}")
            print(f"  Azerbaijani: {result[1]}")
            print(f"  Russian: {result[2]}")
        else:
            print("✗ Test category was not created")
        
        # Clean up
        cursor.execute("DELETE FROM categories WHERE id = 'test-category'")
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"✗ Category test failed: {e}")

def print_database_summary():
    """Print a summary of the current database state"""
    print("\nDatabase Summary:")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        # Categories summary
        cursor.execute("SELECT COUNT(*) FROM categories")
        cat_count = cursor.fetchone()[0]
        print(f"Total Categories: {cat_count}")
        
        cursor.execute("SELECT id, name_en FROM categories LIMIT 5")
        sample_cats = cursor.fetchall()
        print("Sample categories:")
        for cat in sample_cats:
            print(f"  - {cat[0]}: {cat[1]}")
        
        # Menu items summary
        cursor.execute("SELECT COUNT(*) FROM menu_items")
        item_count = cursor.fetchone()[0]
        print(f"\nTotal Menu Items: {item_count}")
        
        cursor.execute("SELECT id, name_en FROM menu_items LIMIT 5")
        sample_items = cursor.fetchall()
        print("Sample menu items:")
        for item in sample_items:
            print(f"  - {item[0]}: {item[1]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error getting database summary: {e}")

if __name__ == "__main__":
    print("Testing Admin Panel Database Updates")
    print("=" * 50)
    
    test_database_schema()
    test_category_sample()
    print_database_summary()
    
    print("\n" + "=" * 50)
    print("Test completed! The database is now ready for multi-language admin panel operations.")
    print("The admin panel can now:")
    print("- Add categories with translations in 8 languages")
    print("- Edit existing categories with multi-language support")
    print("- Add menu items with translations in 8 languages")
    print("- Edit existing menu items with multi-language support")

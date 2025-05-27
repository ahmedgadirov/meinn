"""
Database schema update script to add multi-language support
"""

import sqlite3
import logging
import os

# Set up logger
logger = logging.getLogger("meinn_ai.db_update")

def update_database_schema():
    """Update the database schema to add multi-language columns"""
    
    db_path = "menu_data.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if multi-language columns already exist
        cursor.execute("PRAGMA table_info(categories)")
        categories_columns = [column[1] for column in cursor.fetchall()]
        
        cursor.execute("PRAGMA table_info(menu_items)")
        menu_items_columns = [column[1] for column in cursor.fetchall()]
        
        # Add multi-language columns to categories table if they don't exist
        multilang_columns_categories = [
            'name_az', 'name_en', 'name_ru', 'name_tr', 'name_ar', 'name_hi', 'name_fr', 'name_it',
            'description_az', 'description_en', 'description_ru', 'description_tr', 
            'description_ar', 'description_hi', 'description_fr', 'description_it'
        ]
        
        for column in multilang_columns_categories:
            if column not in categories_columns:
                cursor.execute(f"ALTER TABLE categories ADD COLUMN {column} TEXT")
                logger.info(f"Added column {column} to categories table")
        
        # Add multi-language columns to menu_items table if they don't exist
        multilang_columns_items = [
            'name_az', 'name_en', 'name_ru', 'name_tr', 'name_ar', 'name_hi', 'name_fr', 'name_it',
            'description_az', 'description_en', 'description_ru', 'description_tr', 
            'description_ar', 'description_hi', 'description_fr', 'description_it'
        ]
        
        for column in multilang_columns_items:
            if column not in menu_items_columns:
                cursor.execute(f"ALTER TABLE menu_items ADD COLUMN {column} TEXT")
                logger.info(f"Added column {column} to menu_items table")
        
        # Migrate existing data to the new columns
        # For categories: copy existing name and description to English columns
        cursor.execute("SELECT id, name, description FROM categories WHERE name_en IS NULL")
        categories_to_migrate = cursor.fetchall()
        
        for category in categories_to_migrate:
            cursor.execute(
                "UPDATE categories SET name_en = ?, description_en = ? WHERE id = ?",
                (category[1], category[2] or '', category[0])
            )
            logger.info(f"Migrated category {category[0]} to English columns")
        
        # For menu_items: copy existing name and description to English columns
        cursor.execute("SELECT id, name, description FROM menu_items WHERE name_en IS NULL")
        items_to_migrate = cursor.fetchall()
        
        for item in items_to_migrate:
            cursor.execute(
                "UPDATE menu_items SET name_en = ?, description_en = ? WHERE id = ?",
                (item[1], item[2] or '', item[0])
            )
            logger.info(f"Migrated menu item {item[0]} to English columns")
        
        # Commit all changes
        conn.commit()
        logger.info("Database schema updated successfully with multi-language support")
        
        # Verify the updates
        cursor.execute("PRAGMA table_info(categories)")
        print("Categories table columns after update:")
        for column in cursor.fetchall():
            print(f"  - {column[1]} ({column[2]})")
        
        cursor.execute("PRAGMA table_info(menu_items)")
        print("\nMenu items table columns after update:")
        for column in cursor.fetchall():
            print(f"  - {column[1]} ({column[2]})")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error updating database schema: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    update_database_schema()

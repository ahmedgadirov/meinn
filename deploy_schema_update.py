#!/usr/bin/env python3
"""
Production Database Schema Update Script
Safely adds multilingual columns to existing database
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'schema_update_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

def backup_database(db_path):
    """Create a backup of the database before making changes"""
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        logger.info(f"Database backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Failed to create backup: {str(e)}")
        raise

def check_current_schema(db_path):
    """Check the current database schema"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check categories table
        cursor.execute("PRAGMA table_info(categories)")
        categories_columns = [column[1] for column in cursor.fetchall()]
        
        # Check menu_items table
        cursor.execute("PRAGMA table_info(menu_items)")
        menu_items_columns = [column[1] for column in cursor.fetchall()]
        
        conn.close()
        
        has_multilingual = 'name_en' in categories_columns
        
        logger.info(f"Current schema status:")
        logger.info(f"  Categories columns: {categories_columns}")
        logger.info(f"  Menu items columns: {menu_items_columns}")
        logger.info(f"  Multilingual support: {has_multilingual}")
        
        return has_multilingual, categories_columns, menu_items_columns
        
    except Exception as e:
        logger.error(f"Error checking schema: {str(e)}")
        raise

def update_schema(db_path):
    """Update the database schema to add multilingual columns"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        has_multilingual, categories_columns, menu_items_columns = check_current_schema(db_path)
        
        if has_multilingual:
            logger.info("Multilingual columns already exist. No update needed.")
            conn.close()
            return False
        
        logger.info("Starting schema update...")
        
        # Add multilingual columns to categories table
        multilang_columns_categories = [
            'name_az', 'name_en', 'name_ru', 'name_tr', 'name_ar', 'name_hi', 'name_fr', 'name_it',
            'description_az', 'description_en', 'description_ru', 'description_tr', 
            'description_ar', 'description_hi', 'description_fr', 'description_it'
        ]
        
        for column in multilang_columns_categories:
            if column not in categories_columns:
                cursor.execute(f"ALTER TABLE categories ADD COLUMN {column} TEXT")
                logger.info(f"Added column {column} to categories table")
        
        # Add multilingual columns to menu_items table
        multilang_columns_items = [
            'name_az', 'name_en', 'name_ru', 'name_tr', 'name_ar', 'name_hi', 'name_fr', 'name_it',
            'description_az', 'description_en', 'description_ru', 'description_tr', 
            'description_ar', 'description_hi', 'description_fr', 'description_it'
        ]
        
        for column in multilang_columns_items:
            if column not in menu_items_columns:
                cursor.execute(f"ALTER TABLE menu_items ADD COLUMN {column} TEXT")
                logger.info(f"Added column {column} to menu_items table")
        
        # Migrate existing data to English columns
        logger.info("Migrating existing data...")
        
        # Categories migration
        cursor.execute("SELECT id, name, description FROM categories WHERE name_en IS NULL")
        categories_to_migrate = cursor.fetchall()
        
        for category in categories_to_migrate:
            cursor.execute(
                "UPDATE categories SET name_en = ?, description_en = ? WHERE id = ?",
                (category[1], category[2] or '', category[0])
            )
            logger.info(f"Migrated category: {category[1]}")
        
        # Menu items migration
        cursor.execute("SELECT id, name, description FROM menu_items WHERE name_en IS NULL")
        items_to_migrate = cursor.fetchall()
        
        for item in items_to_migrate:
            cursor.execute(
                "UPDATE menu_items SET name_en = ?, description_en = ? WHERE id = ?",
                (item[1], item[2] or '', item[0])
            )
            logger.info(f"Migrated menu item: {item[1]}")
        
        # Commit all changes
        conn.commit()
        logger.info("Schema update completed successfully")
        
        # Verify the update
        cursor.execute("PRAGMA table_info(categories)")
        new_categories_columns = [column[1] for column in cursor.fetchall()]
        
        cursor.execute("PRAGMA table_info(menu_items)")
        new_menu_items_columns = [column[1] for column in cursor.fetchall()]
        
        logger.info("Updated schema verification:")
        logger.info(f"  Categories columns: {len(new_categories_columns)} total")
        logger.info(f"  Menu items columns: {len(new_menu_items_columns)} total")
        logger.info(f"  Multilingual columns added: {'name_en' in new_categories_columns}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error updating schema: {str(e)}")
        raise

def main():
    """Main deployment function"""
    # Determine database path (adjust as needed for production)
    db_path = "menu_data.db"
    
    # Check if database exists
    if not os.path.exists(db_path):
        logger.error(f"Database file not found: {db_path}")
        logger.info("Please ensure you're running this script from the correct directory")
        sys.exit(1)
    
    logger.info(f"Starting schema update for database: {db_path}")
    
    try:
        # Create backup
        backup_path = backup_database(db_path)
        
        # Update schema
        updated = update_schema(db_path)
        
        if updated:
            logger.info("✅ Schema update completed successfully!")
            logger.info(f"📦 Backup created at: {backup_path}")
            logger.info("🚀 You can now restart your application")
        else:
            logger.info("ℹ️  No schema update was needed")
        
    except Exception as e:
        logger.error(f"❌ Schema update failed: {str(e)}")
        logger.error("🔙 Please restore from backup if needed")
        sys.exit(1)

if __name__ == "__main__":
    main()

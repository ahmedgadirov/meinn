"""
Database schema update for Meinn Restaurant Menu AI Assistant v2.
Adds size support and enhances category structure for hierarchical organization.
"""

import os
import sys
import sqlite3
import logging
import json
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('schema_update_v2.log')
    ]
)
logger = logging.getLogger("meinn_ai.schema_update_v2")

def backup_database():
    """Create a backup of the current database"""
    try:
        db_path = os.path.join(os.path.dirname(__file__), "../../data/menu.db")
        backup_path = os.path.join(os.path.dirname(__file__), f"../../menu_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        
        if os.path.exists(db_path):
            import shutil
            shutil.copy2(db_path, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return backup_path
        else:
            logger.info("No existing database found, skipping backup")
            return None
    except Exception as e:
        logger.error(f"Error creating database backup: {str(e)}")
        return None

def update_schema():
    """Update database schema to support sizes and hierarchical categories"""
    db_path = os.path.join(os.path.dirname(__file__), "../../data/menu.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create backup first
        backup_path = backup_database()
        if backup_path:
            logger.info(f"Backup created successfully at: {backup_path}")
        
        logger.info("Starting schema update...")
        
        # Check if schema updates are needed
        cursor.execute("PRAGMA table_info(menu_items)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add size support columns to menu_items if they don't exist
        if 'size_options' not in columns:
            logger.info("Adding size_options column to menu_items table")
            cursor.execute("ALTER TABLE menu_items ADD COLUMN size_options TEXT") # JSON array of available sizes
            
        if 'size_prices' not in columns:
            logger.info("Adding size_prices column to menu_items table")
            cursor.execute("ALTER TABLE menu_items ADD COLUMN size_prices TEXT") # JSON object with size:price mapping
            
        if 'default_size' not in columns:
            logger.info("Adding default_size column to menu_items table")
            cursor.execute("ALTER TABLE menu_items ADD COLUMN default_size TEXT") # Default size selection
            
        # Check categories table
        cursor.execute("PRAGMA table_info(categories)")
        cat_columns = [column[1] for column in cursor.fetchall()]
        
        # Add parent_id for hierarchical categories if it doesn't exist
        if 'parent_id' not in cat_columns:
            logger.info("Adding parent_id column to categories table for hierarchy")
            cursor.execute("ALTER TABLE categories ADD COLUMN parent_id TEXT")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_id)")
            
        if 'sort_order' not in cat_columns:
            logger.info("Adding sort_order column to categories table")
            cursor.execute("ALTER TABLE categories ADD COLUMN sort_order INTEGER DEFAULT 0")
            
        if 'is_active' not in cat_columns:
            logger.info("Adding is_active column to categories table")
            cursor.execute("ALTER TABLE categories ADD COLUMN is_active BOOLEAN DEFAULT 1")
            
        # Update menu_items table to add size-related indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_menu_items_category ON menu_items(category_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_menu_items_available ON menu_items(available)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_menu_items_popular ON menu_items(popular)")
        
        # Initialize default values for existing items
        cursor.execute("UPDATE menu_items SET size_options = '[]' WHERE size_options IS NULL")
        cursor.execute("UPDATE menu_items SET size_prices = '{}' WHERE size_prices IS NULL")
        cursor.execute("UPDATE menu_items SET default_size = 'Regular' WHERE default_size IS NULL")
        
        # Initialize default values for existing categories
        cursor.execute("UPDATE categories SET sort_order = 0 WHERE sort_order IS NULL")
        cursor.execute("UPDATE categories SET is_active = 1 WHERE is_active IS NULL")
        
        conn.commit()
        logger.info("Schema update completed successfully")
        
        # Verify the updates
        cursor.execute("PRAGMA table_info(menu_items)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        logger.info(f"Menu items table now has columns: {updated_columns}")
        
        cursor.execute("PRAGMA table_info(categories)")
        updated_cat_columns = [column[1] for column in cursor.fetchall()]
        logger.info(f"Categories table now has columns: {updated_cat_columns}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error updating schema: {str(e)}", exc_info=True)
        return False

def verify_schema():
    """Verify that the schema update was successful"""
    db_path = os.path.join(os.path.dirname(__file__), "../../data/menu.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check menu_items table
        cursor.execute("PRAGMA table_info(menu_items)")
        columns = [column[1] for column in cursor.fetchall()]
        
        required_columns = ['size_options', 'size_prices', 'default_size']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            logger.error(f"Missing columns in menu_items: {missing_columns}")
            return False
            
        # Check categories table
        cursor.execute("PRAGMA table_info(categories)")
        cat_columns = [column[1] for column in cursor.fetchall()]
        
        required_cat_columns = ['parent_id', 'sort_order', 'is_active']
        missing_cat_columns = [col for col in required_cat_columns if col not in cat_columns]
        
        if missing_cat_columns:
            logger.error(f"Missing columns in categories: {missing_cat_columns}")
            return False
            
        logger.info("Schema verification completed successfully")
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error verifying schema: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("Starting database schema update v2...")
    
    if update_schema():
        if verify_schema():
            logger.info("Database schema update completed successfully!")
        else:
            logger.error("Schema verification failed!")
            sys.exit(1)
    else:
        logger.error("Schema update failed!")
        sys.exit(1)

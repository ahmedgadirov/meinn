"""
Database initialization script for Meinn Restaurant Menu AI Assistant.
Creates all necessary database tables if they don't exist.
"""

import os
import sys
import sqlite3
import logging

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('db_init.log')
    ]
)
logger = logging.getLogger("meinn_ai.db_init")

def init_database():
    """Initialize all database files and tables"""
    logger.info("Initializing databases...")
    
    # Create database directory if it doesn't exist
    db_dir = os.path.join(os.path.dirname(__file__), "../../data")
    os.makedirs(db_dir, exist_ok=True)
    
    # Initialize menu database
    init_menu_db()
    
    # Initialize conversation database
    init_conversation_db()
    
    # Initialize analytics database
    init_analytics_db()
    
    # Initialize translation database
    init_translation_db()
    
    logger.info("Database initialization complete")

def init_menu_db():
    """Initialize the menu database"""
    db_path = os.path.join(os.path.dirname(__file__), "../../menu_data.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create categories table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            image_url TEXT
        )
        ''')
        
        # Create menu items table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category_id TEXT,
            price REAL NOT NULL,
            image_url TEXT,
            available BOOLEAN DEFAULT 1,
            popular BOOLEAN DEFAULT 0,
            preparation_time INTEGER DEFAULT 15,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
        ''')
        
        # Create item details table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS item_details (
            item_id TEXT PRIMARY KEY,
            allergens TEXT, -- JSON array
            ingredients TEXT, -- JSON array
            nutrition TEXT, -- JSON object
            FOREIGN KEY (item_id) REFERENCES menu_items (id)
        )
        ''')
        
        # Create item pairings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS item_pairings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT,
            paired_with_id TEXT,
            score REAL DEFAULT 1.0,
            FOREIGN KEY (item_id) REFERENCES menu_items (id),
            FOREIGN KEY (paired_with_id) REFERENCES menu_items (id)
        )
        ''')
        
        # Create orders table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            status TEXT NOT NULL,
            total_price REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estimated_completion TIMESTAMP,
            special_instructions TEXT
        )
        ''')
        
        # Create order items table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            item_id TEXT,
            quantity INTEGER DEFAULT 1,
            item_price REAL NOT NULL,
            special_instructions TEXT,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (item_id) REFERENCES menu_items (id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("Menu database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing menu database: {str(e)}", exc_info=True)
        raise

def init_conversation_db():
    """Initialize the conversation database"""
    db_path = os.path.join(os.path.dirname(__file__), "../../conversations.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create conversations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            language TEXT DEFAULT 'az',
            session_id TEXT
        )
        ''')
        
        # Create messages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            sender TEXT NOT NULL, -- 'user' or 'bot'
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("Conversation database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing conversation database: {str(e)}", exc_info=True)
        raise

def init_analytics_db():
    """Initialize the analytics database"""
    db_path = os.path.join(os.path.dirname(__file__), "../../analytics_data.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create user interactions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            interaction_type TEXT NOT NULL, -- 'chat', 'order', 'menu_view', etc.
            interaction_data TEXT, -- JSON object with details
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create item popularity table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS item_popularity (
            item_id TEXT PRIMARY KEY,
            view_count INTEGER DEFAULT 0,
            order_count INTEGER DEFAULT 0,
            last_ordered TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES menu_items (id)
        )
        ''')
        
        # Create user preferences table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT PRIMARY KEY,
            favorite_items TEXT, -- JSON array
            dietary_preferences TEXT, -- JSON array
            language_preference TEXT DEFAULT 'az',
            last_visit TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create daily metrics table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_metrics (
            date TEXT PRIMARY KEY, -- YYYY-MM-DD
            total_orders INTEGER DEFAULT 0,
            total_revenue REAL DEFAULT 0,
            unique_users INTEGER DEFAULT 0,
            popular_items TEXT, -- JSON array
            average_order_value REAL DEFAULT 0
        )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("Analytics database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing analytics database: {str(e)}", exc_info=True)
        raise

def init_translation_db():
    """Initialize the translation database"""
    db_path = os.path.join(os.path.dirname(__file__), "../../translation_data.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create translations table for static content
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS translations (
            key TEXT NOT NULL,
            language TEXT NOT NULL,
            translation TEXT NOT NULL,
            context TEXT,
            PRIMARY KEY (key, language)
        )
        ''')
        
        # Create menu translations table
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
        
        # Create category translations table
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
        
        logger.info("Translation database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing translation database: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    init_database()

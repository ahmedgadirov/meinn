#!/usr/bin/env python3
"""
⚡ Lightning Menu Import System ⚡
Super-fast, smart menu data import with change detection and bulk operations
Replaces all the slow legacy import scripts with one efficient solution
"""

import sqlite3
import csv
import json
import hashlib
import time
from datetime import datetime
from pathlib import Path

class LightningImporter:
    def __init__(self, csv_file='real_menu_data.csv', db_file='menu_data.db'):
        self.csv_file = csv_file
        self.db_file = db_file
        self.conn = None
        self.stats = {
            'total_processed': 0,
            'new_items': 0,
            'updated_items': 0,
            'unchanged_items': 0,
            'categories_created': 0,
            'errors': 0
        }
    
    def connect_db(self):
        """Connect to database and ensure schema exists"""
        self.conn = sqlite3.connect(self.db_file)
        self.conn.execute('PRAGMA foreign_keys = ON')
        self.ensure_schema()
    
    def ensure_schema(self):
        """Ensure all required tables and columns exist"""
        cursor = self.conn.cursor()
        
        # Create categories table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id TEXT PRIMARY KEY,
                name_en TEXT NOT NULL,
                name_az TEXT,
                name_ru TEXT,
                name_tr TEXT,
                name_ar TEXT,
                name_hi TEXT,
                name_fr TEXT,
                name_it TEXT,
                display_order INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Create menu_items table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_items (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                category_id TEXT,
                price REAL DEFAULT 0,
                image_url TEXT,
                available BOOLEAN DEFAULT TRUE,
                popular BOOLEAN DEFAULT FALSE,
                preparation_time INTEGER DEFAULT 15,
                created_at TEXT,
                updated_at TEXT,
                name_az TEXT,
                name_en TEXT,
                name_ru TEXT,
                name_tr TEXT,
                name_ar TEXT,
                name_hi TEXT,
                name_fr TEXT,
                name_it TEXT,
                description_az TEXT,
                description_en TEXT,
                description_ru TEXT,
                description_tr TEXT,
                description_ar TEXT,
                description_hi TEXT,
                description_fr TEXT,
                description_it TEXT,
                size_options TEXT DEFAULT '[]',
                size_prices TEXT DEFAULT '{}',
                default_size TEXT DEFAULT '',
                data_hash TEXT,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # Create item_details table for backward compatibility
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS item_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id TEXT,
                language TEXT,
                name TEXT,
                description TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (item_id) REFERENCES menu_items (id)
            )
        ''')
        
        # Add missing columns if they don't exist
        try:
            cursor.execute('ALTER TABLE item_details ADD COLUMN language TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Add missing columns if they don't exist
        try:
            cursor.execute('ALTER TABLE menu_items ADD COLUMN data_hash TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        self.conn.commit()
    
    def calculate_hash(self, row_data):
        """Calculate hash for change detection"""
        # Create a string from all important fields
        hash_data = '|'.join([
            str(row_data.get('Name', '')),
            str(row_data.get('Description', '')),
            str(row_data.get('Category Name', '')),
            str(row_data.get('Price', '')),
            str(row_data.get('Available', '')),
            str(row_data.get('Size', '')),
            # Include all translations
            str(row_data.get('Name EN', '')),
            str(row_data.get('Name AZ', '')),
            str(row_data.get('Name RU', '')),
            str(row_data.get('Name TR', '')),
            str(row_data.get('Description EN', '')),
            str(row_data.get('Description AZ', '')),
        ])
        return hashlib.md5(hash_data.encode()).hexdigest()
    
    def get_existing_hashes(self):
        """Get all existing item hashes for change detection"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, data_hash FROM menu_items WHERE data_hash IS NOT NULL')
        return dict(cursor.fetchall())
    
    def ensure_category(self, category_name, translations):
        """Ensure category exists, create if needed"""
        cursor = self.conn.cursor()
        
        # Check if category exists
        cursor.execute('SELECT id FROM categories WHERE id = ?', (category_name,))
        if cursor.fetchone():
            return
        
        # Create new category
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO categories (
                id, name_en, name_az, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            category_name,
            translations.get('Category EN', category_name),
            translations.get('Category AZ', category_name),
            translations.get('Category RU', category_name),
            translations.get('Category TR', category_name),
            translations.get('Category AR', category_name),
            translations.get('Category HI', category_name),
            translations.get('Category FR', category_name),
            translations.get('Category IT', category_name),
            now, now
        ))
        
        self.stats['categories_created'] += 1
    
    def process_menu_item(self, row, existing_hashes):
        """Process a single menu item with smart updates"""
        try:
            # Extract basic data
            item_id = row.get('ID', '').strip()
            name = row.get('Name', '').strip()
            category_name = row.get('Category Name', '').strip()
            
            # Skip if missing essential fields
            if not name or not category_name:
                return False
            
            # Generate ID if missing
            if not item_id:
                item_id = f"item_{int(time.time())}_{self.stats['total_processed']}"
            
            # Calculate hash for change detection
            current_hash = self.calculate_hash(row)
            
            # Check if item changed
            if item_id in existing_hashes and existing_hashes[item_id] == current_hash:
                self.stats['unchanged_items'] += 1
                return True
            
            # Ensure category exists
            self.ensure_category(category_name, row)
            
            # Parse price
            price = 0.0
            try:
                price_str = row.get('Price', '0').strip()
                if price_str:
                    price = float(price_str)
            except:
                price = 0.0
            
            # Parse other fields
            description = row.get('Description', '').strip()
            image_url = row.get('Image URL', '').strip() or 'https://via.placeholder.com/300x200'
            available = row.get('Available', 'TRUE').upper() == 'TRUE'
            popular = row.get('Popular', 'FALSE').upper() == 'TRUE'
            
            prep_time = 15
            try:
                prep_time_str = row.get('Preparation Time', '15').strip()
                if prep_time_str:
                    prep_time = int(prep_time_str)
            except:
                prep_time = 15
            
            # Handle size information
            size = row.get('Size', '').strip()
            size_options = json.dumps([size] if size else [])
            size_prices = json.dumps({size: price} if size else {})
            default_size = size if size else ''
            
            # Prepare translations
            now = datetime.now().isoformat()
            
            # Check if item exists
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM menu_items WHERE id = ?', (item_id,))
            exists = cursor.fetchone() is not None
            
            if exists:
                # Update existing item
                cursor.execute('''
                    UPDATE menu_items SET
                        name = ?, description = ?, category_id = ?, price = ?, image_url = ?,
                        available = ?, popular = ?, preparation_time = ?, updated_at = ?,
                        name_az = ?, name_en = ?, name_ru = ?, name_tr = ?, name_ar = ?, name_hi = ?, name_fr = ?, name_it = ?,
                        description_az = ?, description_en = ?, description_ru = ?, description_tr = ?,
                        description_ar = ?, description_hi = ?, description_fr = ?, description_it = ?,
                        size_options = ?, size_prices = ?, default_size = ?, data_hash = ?
                    WHERE id = ?
                ''', (
                    name, description, category_name, price, image_url,
                    available, popular, prep_time, now,
                    row.get('Name AZ', '').strip() or name,
                    row.get('Name EN', '').strip() or name,
                    row.get('Name RU', '').strip() or name,
                    row.get('Name TR', '').strip() or name,
                    row.get('Name AR', '').strip() or name,
                    row.get('Name HI', '').strip() or name,
                    row.get('Name FR', '').strip() or name,
                    row.get('Name IT', '').strip() or name,
                    row.get('Description AZ', '').strip() or description,
                    row.get('Description EN', '').strip() or description,
                    row.get('Description RU', '').strip() or description,
                    row.get('Description TR', '').strip() or description,
                    row.get('Description AR', '').strip() or description,
                    row.get('Description HI', '').strip() or description,
                    row.get('Description FR', '').strip() or description,
                    row.get('Description IT', '').strip() or description,
                    size_options, size_prices, default_size, current_hash,
                    item_id
                ))
                self.stats['updated_items'] += 1
            else:
                # Insert new item
                cursor.execute('''
                    INSERT INTO menu_items (
                        id, name, description, category_id, price, image_url,
                        available, popular, preparation_time, created_at, updated_at,
                        name_az, name_en, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
                        description_az, description_en, description_ru, description_tr,
                        description_ar, description_hi, description_fr, description_it,
                        size_options, size_prices, default_size, data_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item_id, name, description, category_name, price, image_url,
                    available, popular, prep_time, now, now,
                    row.get('Name AZ', '').strip() or name,
                    row.get('Name EN', '').strip() or name,
                    row.get('Name RU', '').strip() or name,
                    row.get('Name TR', '').strip() or name,
                    row.get('Name AR', '').strip() or name,
                    row.get('Name HI', '').strip() or name,
                    row.get('Name FR', '').strip() or name,
                    row.get('Name IT', '').strip() or name,
                    row.get('Description AZ', '').strip() or description,
                    row.get('Description EN', '').strip() or description,
                    row.get('Description RU', '').strip() or description,
                    row.get('Description TR', '').strip() or description,
                    row.get('Description AR', '').strip() or description,
                    row.get('Description HI', '').strip() or description,
                    row.get('Description FR', '').strip() or description,
                    row.get('Description IT', '').strip() or description,
                    size_options, size_prices, default_size, current_hash
                ))
                self.stats['new_items'] += 1
            
            # Sync to item_details for backward compatibility
            self.sync_item_details(item_id, row)
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing item {row.get('Name', 'Unknown')}: {e}")
            self.stats['errors'] += 1
            return False
    
    def sync_item_details(self, item_id, row):
        """Sync multilingual data to item_details table"""
        cursor = self.conn.cursor()
        
        # Clear existing details
        cursor.execute('DELETE FROM item_details WHERE item_id = ?', (item_id,))
        
        # Insert language variants
        languages = {
            'en': {'name': row.get('Name EN', ''), 'desc': row.get('Description EN', '')},
            'az': {'name': row.get('Name AZ', ''), 'desc': row.get('Description AZ', '')},
            'ru': {'name': row.get('Name RU', ''), 'desc': row.get('Description RU', '')},
            'tr': {'name': row.get('Name TR', ''), 'desc': row.get('Description TR', '')},
            'ar': {'name': row.get('Name AR', ''), 'desc': row.get('Description AR', '')},
            'hi': {'name': row.get('Name HI', ''), 'desc': row.get('Description HI', '')},
            'fr': {'name': row.get('Name FR', ''), 'desc': row.get('Description FR', '')},
            'it': {'name': row.get('Name IT', ''), 'desc': row.get('Description IT', '')}
        }
        
        now = datetime.now().isoformat()
        for lang, data in languages.items():
            if data['name']:  # Only insert if name exists
                cursor.execute('''
                    INSERT INTO item_details (item_id, language, name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (item_id, lang, data['name'], data['desc'], now, now))
    
    def run_import(self):
        """Run the lightning-fast import process"""
        start_time = time.time()
        
        print("⚡ Starting Lightning Menu Import...")
        print(f"📁 Source: {self.csv_file}")
        print(f"🗄️  Database: {self.db_file}")
        print("-" * 50)
        
        # Connect to database
        self.connect_db()
        
        # Get existing hashes for change detection
        print("🔍 Analyzing existing data...")
        existing_hashes = self.get_existing_hashes()
        print(f"   Found {len(existing_hashes)} existing items")
        
        # Process CSV file
        if not Path(self.csv_file).exists():
            print(f"❌ Error: CSV file '{self.csv_file}' not found!")
            return False
        
        print("📊 Processing menu data...")
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Process in batches for better performance
                batch_size = 50
                batch = []
                
                for row in reader:
                    batch.append(row)
                    
                    if len(batch) >= batch_size:
                        self.process_batch(batch, existing_hashes)
                        batch = []
                        
                        # Show progress
                        print(f"   ✅ Processed {self.stats['total_processed']} items...", end='\r')
                
                # Process remaining items
                if batch:
                    self.process_batch(batch, existing_hashes)
            
            # Commit all changes
            self.conn.commit()
            
            # Calculate timing
            end_time = time.time()
            duration = end_time - start_time
            
            # Print results
            print("\n" + "=" * 50)
            print("⚡ LIGHTNING IMPORT COMPLETE! ⚡")
            print("=" * 50)
            print(f"⏱️  Duration: {duration:.2f} seconds")
            print(f"📊 Total processed: {self.stats['total_processed']}")
            print(f"🆕 New items: {self.stats['new_items']}")
            print(f"📝 Updated items: {self.stats['updated_items']}")
            print(f"⏭️  Unchanged items: {self.stats['unchanged_items']}")
            print(f"📂 Categories created: {self.stats['categories_created']}")
            if self.stats['errors'] > 0:
                print(f"⚠️  Errors: {self.stats['errors']}")
            
            # Show performance
            items_per_second = self.stats['total_processed'] / duration if duration > 0 else 0
            print(f"🚀 Speed: {items_per_second:.1f} items/second")
            print("=" * 50)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Import failed: {e}")
            if self.conn:
                self.conn.rollback()
            return False
        finally:
            if self.conn:
                self.conn.close()
    
    def process_batch(self, batch, existing_hashes):
        """Process a batch of items"""
        for row in batch:
            self.process_menu_item(row, existing_hashes)
            self.stats['total_processed'] += 1

def main():
    """Main entry point"""
    importer = LightningImporter()
    success = importer.run_import()
    
    if success:
        print("\n🎉 Your menu is now updated and ready to serve customers!")
        print("💡 Tip: Run this script anytime to sync changes automatically")
    else:
        print("\n💥 Import failed. Please check the error messages above.")
        exit(1)

if __name__ == "__main__":
    main()

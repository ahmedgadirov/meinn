#!/usr/bin/env python3
"""
⚡ Lightning Menu Import System - Render Shell Optimized ⚡
Enhanced for Render Shell deployment with robust error handling and chunked processing
Fixes the "categories yes, menu items no" issue in render environments
"""

import sqlite3
import csv
import json
import hashlib
import time
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

class RenderOptimizedImporter:
    def __init__(self, csv_file='real_menu_data.csv', db_file='menu_data.db'):
        # Always use absolute paths to ensure consistency with API and backend
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = current_dir

        # Ensure CSV file path is absolute and in project root unless absolute path provided
        if not os.path.isabs(csv_file):
            self.csv_file = os.path.join(project_root, csv_file)
        else:
            self.csv_file = csv_file

        # Ensure database path matches what MenuManager expects (project root)
        if not os.path.isabs(db_file):
            self.db_file = os.path.join(project_root, db_file)
        else:
            self.db_file = db_file

        self.conn = None
        self.stats = {
            'total_processed': 0,
            'new_items': 0,
            'updated_items': 0,
            'unchanged_items': 0,
            'categories_created': 0,
            'errors': 0,
            'skipped_items': 0
        }
        
        # Render shell optimization settings
        self.is_render_shell = self.detect_render_environment()
        self.chunk_size = 5 if self.is_render_shell else 25  # Much smaller chunks for render
        self.max_memory_items = 50 if self.is_render_shell else 200
        self.commit_frequency = 3 if self.is_render_shell else 10
        
        # Enhanced logging
        self.debug_mode = True
        self.log_file = 'lightning_import.log'
        
        # Resume capability
        self.resume_file = 'import_progress.json'
        self.last_processed_id = None
        
    def detect_render_environment(self):
        """Detect if running in Render shell environment"""
        render_indicators = [
            'RENDER' in os.environ,
            'RENDER_SERVICE_ID' in os.environ,
            'RENDER_EXTERNAL_URL' in os.environ,
            '/opt/render' in os.getcwd(),
            'render.com' in os.environ.get('HOSTNAME', ''),
        ]
        
        is_render = any(render_indicators)
        if is_render:
            self.log("🔧 Render Shell environment detected - using optimized settings")
        return is_render
    
    def log(self, message, level="INFO"):
        """Enhanced logging with file output"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {level}: {message}"
        
        # Always print to console
        print(log_entry)
        
        # Also write to log file for debugging
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except:
            pass  # Don't fail if we can't write to log file
    
    def save_progress(self, item_id):
        """Save current progress for resume capability"""
        try:
            progress_data = {
                'last_processed_id': item_id,
                'timestamp': datetime.now().isoformat(),
                'stats': self.stats
            }
            with open(self.resume_file, 'w') as f:
                json.dump(progress_data, f)
        except:
            pass  # Don't fail if we can't save progress
    
    def load_progress(self):
        """Load previous progress if available"""
        try:
            if os.path.exists(self.resume_file):
                with open(self.resume_file, 'r') as f:
                    progress_data = json.load(f)
                    self.last_processed_id = progress_data.get('last_processed_id')
                    if self.last_processed_id:
                        self.log(f"📂 Resuming from item: {self.last_processed_id}")
                        return True
        except:
            pass
        return False
    
    def connect_db(self):
        """Connect to database with enhanced error handling"""
        try:
            self.log("🔌 Connecting to database...")
            self.conn = sqlite3.connect(self.db_file, timeout=30.0)
            self.conn.execute('PRAGMA foreign_keys = ON')
            self.conn.execute('PRAGMA journal_mode = WAL')  # Better for concurrent access
            self.conn.execute('PRAGMA synchronous = NORMAL')  # Faster writes
            self.ensure_schema()
            self.log("✅ Database connected successfully")
            return True
        except Exception as e:
            self.log(f"❌ Database connection failed: {e}", "ERROR")
            return False
    
    def ensure_schema(self):
        """Ensure all required tables and columns exist with error handling"""
        try:
            self.log("🔨 Ensuring database schema...")
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
            
            # Add missing columns safely
            self.add_column_safe('item_details', 'language', 'TEXT')
            self.add_column_safe('menu_items', 'data_hash', 'TEXT')
            
            self.conn.commit()
            self.log("✅ Database schema verified")
            
        except Exception as e:
            self.log(f"❌ Schema creation failed: {e}", "ERROR")
            raise
    
    def add_column_safe(self, table, column, column_type):
        """Safely add column if it doesn't exist"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f'ALTER TABLE {table} ADD COLUMN {column} {column_type}')
            self.log(f"   ✅ Added column {table}.{column}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                self.log(f"   ⚠️ Column add warning for {table}.{column}: {e}")
    
    def calculate_hash(self, row_data):
        """Calculate hash for change detection"""
        hash_data = '|'.join([
            str(row_data.get('Name', '')),
            str(row_data.get('Description', '')),
            str(row_data.get('Category Name', '')),
            str(row_data.get('Price', '')),
            str(row_data.get('Available', '')),
            str(row_data.get('Size', '')),
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
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id, data_hash FROM menu_items WHERE data_hash IS NOT NULL')
            result = dict(cursor.fetchall())
            self.log(f"📊 Found {len(result)} existing item hashes")
            return result
        except Exception as e:
            self.log(f"⚠️ Could not load existing hashes: {e}", "WARNING")
            return {}
    
    def ensure_category(self, category_name, translations):
        """Ensure category exists with enhanced error handling"""
        try:
            cursor = self.conn.cursor()
            
            # Check if category exists
            cursor.execute('SELECT id FROM categories WHERE id = ?', (category_name,))
            if cursor.fetchone():
                return True
            
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
            self.log(f"   ✅ Created category: {category_name}")
            return True
            
        except Exception as e:
            self.log(f"❌ Category creation failed for {category_name}: {e}", "ERROR")
            return False
    
    def process_menu_item(self, row, existing_hashes):
        """Process a single menu item with enhanced error handling"""
        try:
            # Extract basic data
            item_id = row.get('ID', '').strip()
            name = row.get('Name', '').strip()
            category_name = row.get('Category Name', '').strip()
            
            # Skip if missing essential fields
            if not name or not category_name:
                self.log(f"⚠️ Skipping item with missing name or category: {row}", "WARNING")
                self.stats['skipped_items'] += 1
                return True  # Continue processing
            
            # Generate ID if missing
            if not item_id:
                item_id = f"item_{int(time.time())}_{self.stats['total_processed']}"
            
            # Skip if we're resuming and haven't reached the last processed item
            if self.last_processed_id and item_id != self.last_processed_id:
                if self.stats['total_processed'] == 0:  # Still looking for resume point
                    return True
                
            # Calculate hash for change detection
            current_hash = self.calculate_hash(row)
            
            # Check if item changed
            if item_id in existing_hashes and existing_hashes[item_id] == current_hash:
                self.stats['unchanged_items'] += 1
                return True
            
            # Ensure category exists
            if not self.ensure_category(category_name, row):
                self.log(f"❌ Failed to create category for item {name}", "ERROR")
                self.stats['errors'] += 1
                return False
            
            # Parse price safely
            price = 0.0
            try:
                price_str = row.get('Price', '0').strip()
                if price_str:
                    price = float(price_str)
            except Exception as e:
                self.log(f"⚠️ Invalid price for {name}: {price_str}, using 0.0", "WARNING")
                price = 0.0
            
            # Parse other fields safely
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
            
            # Handle size information safely
            size = row.get('Size', '').strip()
            try:
                size_options = json.dumps([size] if size else [])
                size_prices = json.dumps({size: price} if size else {})
            except:
                size_options = '[]'
                size_prices = '{}'
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
                self.log(f"   📝 Updated: {name}")
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
                self.log(f"   ✅ Added: {name}")
            
            # Sync to item_details for backward compatibility
            self.sync_item_details(item_id, row)
            
            # Save progress for resume capability
            self.save_progress(item_id)
            
            return True
            
        except Exception as e:
            error_msg = f"❌ Error processing item {row.get('Name', 'Unknown')}: {e}"
            self.log(error_msg, "ERROR")
            self.log(f"Full traceback: {traceback.format_exc()}", "DEBUG")
            self.stats['errors'] += 1
            return False
    
    def sync_item_details(self, item_id, row):
        """Sync multilingual data to item_details table with error handling"""
        try:
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
                    
        except Exception as e:
            self.log(f"⚠️ Warning: Could not sync item_details for {item_id}: {e}", "WARNING")
    
    def run_import(self):
        """Run the render-optimized import process"""
        start_time = time.time()
        
        self.log("⚡ Starting Render-Optimized Lightning Menu Import...")
        self.log(f"📁 Source: {self.csv_file}")
        self.log(f"🗄️  Database: {self.db_file}")
        
        if self.is_render_shell:
            self.log(f"🔧 Render Shell Mode: chunks={self.chunk_size}, commits every {self.commit_frequency}")
        
        self.log("-" * 50)
        
        # Validate file existence
        if not Path(self.csv_file).exists():
            self.log(f"❌ Error: CSV file '{self.csv_file}' not found!", "ERROR")
            return False
        
        # Load previous progress if resuming
        is_resuming = self.load_progress()
        
        # Connect to database
        if not self.connect_db():
            return False
        
        # Get existing hashes for change detection
        self.log("🔍 Analyzing existing data...")
        existing_hashes = self.get_existing_hashes()
        
        # Process CSV file
        self.log("📊 Processing menu data...")
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Convert to list to get total count
                all_rows = list(reader)
                total_rows = len(all_rows)
                self.log(f"📊 Total items to process: {total_rows}")
                
                # Process in small chunks optimized for render shell
                chunk = []
                chunk_count = 0
                
                for i, row in enumerate(all_rows):
                    chunk.append(row)
                    
                    # Process chunk when full or at end
                    if len(chunk) >= self.chunk_size or i == total_rows - 1:
                        chunk_count += 1
                        
                        self.log(f"🔄 Processing chunk {chunk_count}/{(total_rows + self.chunk_size - 1) // self.chunk_size}")
                        
                        # Process the chunk
                        success = self.process_chunk(chunk, existing_hashes)
                        
                        if not success:
                            self.log("❌ Chunk processing failed, stopping import", "ERROR")
                            return False
                        
                        # Commit frequently in render shell
                        if chunk_count % self.commit_frequency == 0:
                            self.log("💾 Committing transaction...")
                            self.conn.commit()
                        
                        # Clear chunk for next batch
                        chunk = []
                        
                        # Show progress
                        progress = (self.stats['total_processed'] / total_rows) * 100
                        self.log(f"📊 Progress: {progress:.1f}% ({self.stats['total_processed']}/{total_rows})")
                        
                        # Small delay for render shell resource management
                        if self.is_render_shell:
                            time.sleep(0.1)
            
            # Final commit
            self.log("💾 Final commit...")
            self.conn.commit()
            
            # Calculate timing
            end_time = time.time()
            duration = end_time - start_time
            
            # Clean up progress file on success
            try:
                if os.path.exists(self.resume_file):
                    os.remove(self.resume_file)
            except:
                pass
            
            # Print results
            self.log("\n" + "=" * 50)
            self.log("⚡ RENDER-OPTIMIZED IMPORT COMPLETE! ⚡")
            self.log("=" * 50)
            self.log(f"⏱️  Duration: {duration:.2f} seconds")
            self.log(f"📊 Total processed: {self.stats['total_processed']}")
            self.log(f"🆕 New items: {self.stats['new_items']}")
            self.log(f"📝 Updated items: {self.stats['updated_items']}")
            self.log(f"⏭️  Unchanged items: {self.stats['unchanged_items']}")
            self.log(f"📂 Categories created: {self.stats['categories_created']}")
            self.log(f"⏩ Skipped items: {self.stats['skipped_items']}")
            if self.stats['errors'] > 0:
                self.log(f"⚠️  Errors: {self.stats['errors']}")
            
            # Show performance
            items_per_second = self.stats['total_processed'] / duration if duration > 0 else 0
            self.log(f"🚀 Speed: {items_per_second:.1f} items/second")
            self.log("=" * 50)
            
            return self.stats['errors'] == 0  # Success if no errors
            
        except Exception as e:
            self.log(f"\n❌ Import failed: {e}", "ERROR")
            self.log(f"Full traceback: {traceback.format_exc()}", "DEBUG")
            if self.conn:
                self.conn.rollback()
            return False
        finally:
            if self.conn:
                self.conn.close()
    
    def process_chunk(self, chunk, existing_hashes):
        """Process a chunk of items with enhanced error handling"""
        try:
            chunk_success = True
            
            for row in chunk:
                try:
                    success = self.process_menu_item(row, existing_hashes)
                    if success:
                        self.stats['total_processed'] += 1
                    else:
                        chunk_success = False
                        # Continue processing other items in chunk
                        
                except Exception as e:
                    self.log(f"❌ Critical error in chunk processing: {e}", "ERROR")
                    chunk_success = False
                    break
            
            return chunk_success
            
        except Exception as e:
            self.log(f"❌ Chunk processing failed: {e}", "ERROR")
            return False

def main():
    """Main entry point with enhanced error handling"""
    try:
        importer = RenderOptimizedImporter()
        success = importer.run_import()
        
        if success:
            importer.log("\n🎉 Your menu is now updated and ready to serve customers!")
            importer.log("💡 Tip: Run this script anytime to sync changes automatically")
            sys.exit(0)
        else:
            importer.log("\n💥 Import failed. Check the logs above for details.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()

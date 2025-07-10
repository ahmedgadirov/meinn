"""
Enhanced CSV Import System for Meinn Restaurant Menu AI Assistant.
Imports menu items from CSV with size support and multilingual translations.
"""

import os
import sys
import sqlite3
import logging
import json
import csv
import uuid
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('menu_csv_import.log')
    ]
)
logger = logging.getLogger("meinn_ai.csv_import")

def load_category_mapping():
    """Load the category mapping from JSON file"""
    try:
        with open('category_mapping.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading category mapping: {str(e)}")
        return {}

def clean_price(price_str):
    """Clean and convert price string to float"""
    if not price_str or price_str.strip() == '':
        return 0.0
    
    # Remove currency symbols and clean
    cleaned = str(price_str).replace('₼', '').replace('AZN', '').replace('$', '').strip()
    
    try:
        return float(cleaned)
    except ValueError:
        logger.warning(f"Invalid price format: {price_str}")
        return 0.0

def extract_size_info(row):
    """Extract size information from CSV row"""
    size_info = {
        'options': [],
        'prices': {},
        'default_size': 'Regular'
    }
    
    size_field = row.get('Size', '').strip()
    price = clean_price(row.get('Price', 0))
    
    if size_field and size_field != '':
        # Parse size field (could be like "Regular/Large" or just "Large")
        sizes = [s.strip() for s in size_field.replace('/', ',').split(',') if s.strip()]
        
        if sizes:
            size_info['options'] = sizes
            size_info['default_size'] = sizes[0]
            
            # For now, assign the same price to all sizes
            # TODO: Could be enhanced to handle size-specific pricing
            for size in sizes:
                size_info['prices'][size] = price
        else:
            # No specific size info, use default
            size_info['options'] = ['Regular']
            size_info['prices']['Regular'] = price
    else:
        # No size specified, use default
        size_info['options'] = ['Regular']
        size_info['prices']['Regular'] = price
    
    return size_info

def map_csv_category_to_id(csv_category, category_mapping):
    """Map CSV category name to database category ID"""
    
    # Direct mapping first
    if csv_category in category_mapping:
        return category_mapping[csv_category]
    
    # Try case-insensitive mapping
    for cat_name, cat_id in category_mapping.items():
        if cat_name.lower() == csv_category.lower():
            return cat_id
    
    # Try partial matching for common variations
    csv_lower = csv_category.lower()
    
    # Common mappings
    mappings = {
        'breakfast': 'Breakfast',
        'appetizers': 'Appetizers (Cold & Hot)',
        'soups': 'Soups',
        'salads': 'Salads',
        'pasta': 'Pasta',
        'burgers': 'Burgers & Rolls',
        'chicken': 'Chicken Dishes',
        'meat': 'Meat Dishes',
        'seafood': 'Seafood',
        'kebabs': 'Kebabs',
        'pizza': 'Pizza',
        'desserts': 'Desserts',
        'beverages': 'Beverages',
        'tea': 'Tea',
        'coffee': 'Coffee',
        'soft drinks': 'Soft Drinks',
        'juices': 'Fresh Juices',
        'cocktails': 'Cocktails',
        'beer': 'Beer',
        'wine': 'Wine'
    }
    
    for key, mapped_name in mappings.items():
        if key in csv_lower:
            if mapped_name in category_mapping:
                return category_mapping[mapped_name]
    
    # Default to a general category if no match found
    logger.warning(f"No category mapping found for: {csv_category}, using default")
    return category_mapping.get('Appetizers (Cold & Hot)', None)

def process_menu_csv():
    """Process the CSV file and import menu items"""
    csv_file = "/home/ahmd/Desktop/menu pizza inn/menu_items_export.csv"
    
    if not os.path.exists(csv_file):
        logger.error(f"CSV file not found: {csv_file}")
        return False
    
    # Load category mapping
    category_mapping = load_category_mapping()
    if not category_mapping:
        logger.error("No category mapping available")
        return False
    
    try:
        db_path = os.path.join(os.path.dirname(__file__), "menu_data.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Clear existing menu items and item details
        logger.info("Clearing existing menu items...")
        cursor.execute("DELETE FROM item_details")
        cursor.execute("DELETE FROM menu_items")
        
        # Read and process CSV
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            processed_count = 0
            error_count = 0
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Extract basic information
                    item_id = str(uuid.uuid4())
                    name = row.get('Name EN', '').strip()
                    
                    if not name:
                        logger.warning(f"Row {row_num}: No English name found, skipping")
                        continue
                    
                    # Map category
                    csv_category = row.get('Category ID', '').strip()
                    category_id = map_csv_category_to_id(csv_category, category_mapping)
                    
                    if not category_id:
                        logger.warning(f"Row {row_num}: No valid category for {csv_category}, skipping item {name}")
                        continue
                    
                    # Extract size information
                    size_info = extract_size_info(row)
                    
                    # Extract basic fields
                    description = row.get('Description EN', '').strip()
                    image_url = row.get('Image URL', '/images/menu/placeholder.jpg').strip()
                    available = True  # Default to available
                    popular = False  # Default to not popular
                    preparation_time = 15  # Default preparation time
                    
                    # Extract multilingual names
                    names = {
                        'name_en': row.get('Name EN', name).strip(),
                        'name_az': row.get('Name AZ', name).strip(),
                        'name_ru': row.get('Name RU', name).strip(),
                        'name_tr': row.get('Name TR', name).strip(),
                        'name_ar': row.get('Name AR', name).strip(),
                        'name_hi': row.get('Name HI', name).strip(),
                        'name_fr': row.get('Name FR', name).strip(),
                        'name_it': row.get('Name IT', name).strip(),
                    }
                    
                    # Extract multilingual descriptions
                    descriptions = {
                        'description_en': row.get('Description EN', description).strip(),
                        'description_az': row.get('Description AZ', description).strip(),
                        'description_ru': row.get('Description RU', description).strip(),
                        'description_tr': row.get('Description TR', description).strip(),
                        'description_ar': row.get('Description AR', description).strip(),
                        'description_hi': row.get('Description HI', description).strip(),
                        'description_fr': row.get('Description FR', description).strip(),
                        'description_it': row.get('Description IT', description).strip(),
                    }
                    
                    # Insert menu item
                    cursor.execute("""
                        INSERT INTO menu_items (
                            id, name, description, category_id, price, image_url, 
                            available, popular, preparation_time, created_at, updated_at,
                            name_az, name_en, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
                            description_az, description_en, description_ru, description_tr, 
                            description_ar, description_hi, description_fr, description_it,
                            size_options, size_prices, default_size
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item_id, name, description, category_id, size_info['prices'].get(size_info['default_size'], 0),
                        image_url, available, popular, preparation_time, 
                        datetime.now().isoformat(), datetime.now().isoformat(),
                        names['name_az'], names['name_en'], names['name_ru'], names['name_tr'],
                        names['name_ar'], names['name_hi'], names['name_fr'], names['name_it'],
                        descriptions['description_az'], descriptions['description_en'], 
                        descriptions['description_ru'], descriptions['description_tr'],
                        descriptions['description_ar'], descriptions['description_hi'], 
                        descriptions['description_fr'], descriptions['description_it'],
                        json.dumps(size_info['options']), json.dumps(size_info['prices']), size_info['default_size']
                    ))
                    
                    # Insert item details
                    cursor.execute("""
                        INSERT INTO item_details (item_id, allergens, ingredients, nutrition)
                        VALUES (?, ?, ?, ?)
                    """, (
                        item_id,
                        json.dumps([]),  # Empty allergens for now
                        json.dumps([]),  # Empty ingredients for now
                        json.dumps({})   # Empty nutrition for now
                    ))
                    
                    processed_count += 1
                    
                    if processed_count % 50 == 0:
                        logger.info(f"Processed {processed_count} items...")
                
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error processing row {row_num}: {str(e)}")
                    continue
        
        conn.commit()
        
        # Log final results
        cursor.execute("SELECT COUNT(*) FROM menu_items")
        total_items = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM item_details")
        total_details = cursor.fetchone()[0]
        
        logger.info(f"Import completed successfully!")
        logger.info(f"Total items imported: {total_items}")
        logger.info(f"Total item details created: {total_details}")
        logger.info(f"Processed: {processed_count}, Errors: {error_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}", exc_info=True)
        return False

def verify_import():
    """Verify the import was successful"""
    try:
        db_path = os.path.join(os.path.dirname(__file__), "menu_data.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get summary by category
        cursor.execute("""
            SELECT c.name, COUNT(m.id) as item_count
            FROM categories c
            LEFT JOIN menu_items m ON c.id = m.category_id
            GROUP BY c.id, c.name
            ORDER BY item_count DESC
        """)
        
        results = cursor.fetchall()
        
        logger.info("\nImport Verification - Items by Category:")
        logger.info("=" * 50)
        
        total_items = 0
        for category, count in results:
            if count > 0:
                logger.info(f"{category}: {count} items")
                total_items += count
        
        logger.info(f"\nTotal items across all categories: {total_items}")
        
        # Check for items with size options
        cursor.execute("""
            SELECT COUNT(*) FROM menu_items 
            WHERE size_options != '[]' AND size_options IS NOT NULL
        """)
        items_with_sizes = cursor.fetchone()[0]
        
        logger.info(f"Items with size options: {items_with_sizes}")
        
        # Sample items with sizes
        cursor.execute("""
            SELECT name, size_options, size_prices, default_size 
            FROM menu_items 
            WHERE size_options != '[]' AND size_options IS NOT NULL
            LIMIT 5
        """)
        
        size_samples = cursor.fetchall()
        
        if size_samples:
            logger.info("\nSample items with sizes:")
            for name, options, prices, default in size_samples:
                logger.info(f"  {name}: options={options}, prices={prices}, default={default}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error verifying import: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting enhanced CSV menu import...")
    
    if process_menu_csv():
        if verify_import():
            logger.info("Menu CSV import completed successfully!")
        else:
            logger.error("Import verification failed!")
            sys.exit(1)
    else:
        logger.error("Menu CSV import failed!")
        sys.exit(1)

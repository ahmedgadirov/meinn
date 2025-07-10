"""
Import hierarchical category structure for Meinn Restaurant Menu AI Assistant.
Creates categories with multilingual support and hierarchy based on the menu_categories.json file.
"""

import os
import sys
import sqlite3
import logging
import json
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
        logging.FileHandler('category_import.log')
    ]
)
logger = logging.getLogger("meinn_ai.category_import")

def parse_categories_from_markdown():
    """Parse the category structure from the markdown-formatted JSON file"""
    categories_file = "/home/ahmd/Desktop/menu pizza inn/menu_categoires.json"
    
    try:
        with open(categories_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the markdown structure
        sections = content.split('## ')
        
        categories_by_language = {}
        
        for section in sections[1:]:  # Skip the first empty section
            lines = section.strip().split('\n')
            language_header = lines[0].strip()
            
            # Extract language code
            if 'English' in language_header:
                lang_code = 'en'
            elif 'Azerbaijani' in language_header:
                lang_code = 'az'
            elif 'Russian' in language_header:
                lang_code = 'ru'
            elif 'Turkish' in language_header:
                lang_code = 'tr'
            elif 'Italian' in language_header:
                lang_code = 'it'
            elif 'Hindi' in language_header:
                lang_code = 'hi'
            elif 'Arabic' in language_header:
                lang_code = 'ar'
            elif 'French' in language_header:
                lang_code = 'fr'
            else:
                continue
            
            categories = []
            current_category = None
            
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('- ') and not line.startswith('  -'):
                    # Main category
                    category_name = line[2:].strip()
                    current_category = {
                        'name': category_name,
                        'subcategories': []
                    }
                    categories.append(current_category)
                elif line.startswith('  - '):
                    # Subcategory
                    if current_category:
                        subcategory_name = line[4:].strip()
                        current_category['subcategories'].append(subcategory_name)
            
            categories_by_language[lang_code] = categories
        
        return categories_by_language
        
    except Exception as e:
        logger.error(f"Error parsing categories file: {str(e)}")
        return {}

def create_category_structure():
    """Create the hierarchical category structure in the database"""
    
    # Parse categories from the file
    categories_by_language = parse_categories_from_markdown()
    
    if not categories_by_language:
        logger.error("No categories found in the file")
        return False
    
    # Use English as the base structure
    base_categories = categories_by_language.get('en', [])
    
    if not base_categories:
        logger.error("No English categories found")
        return False
    
    try:
        db_path = os.path.join(os.path.dirname(__file__), "menu_data.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Clear existing categories
        logger.info("Clearing existing categories...")
        cursor.execute("DELETE FROM categories")
        
        category_mapping = {}  # Maps English names to IDs
        sort_order = 0
        
        for main_category in base_categories:
            main_cat_name = main_category['name']
            main_cat_id = str(uuid.uuid4())
            
            # Create translations dictionary for main category
            translations = {}
            for lang_code, lang_categories in categories_by_language.items():
                # Find corresponding category in this language
                for lang_cat in lang_categories:
                    if lang_cat['name'] and len(lang_categories) == len(base_categories):
                        # Match by position
                        cat_index = base_categories.index(main_category)
                        if cat_index < len(lang_categories):
                            translations[lang_code] = lang_categories[cat_index]['name']
                            break
            
            # Insert main category
            cursor.execute("""
                INSERT INTO categories (
                    id, name, description, image_url, parent_id, sort_order, is_active,
                    name_az, name_en, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
                    description_az, description_en, description_ru, description_tr, 
                    description_ar, description_hi, description_fr, description_it
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                main_cat_id,
                main_cat_name,
                f"Delicious {main_cat_name.lower()} options",
                f"/images/categories/{main_cat_name.lower().replace(' ', '_')}.jpg",
                None,  # parent_id is NULL for main categories
                sort_order,
                1,  # is_active
                translations.get('az', main_cat_name),
                translations.get('en', main_cat_name),
                translations.get('ru', main_cat_name),
                translations.get('tr', main_cat_name),
                translations.get('ar', main_cat_name),
                translations.get('hi', main_cat_name),
                translations.get('fr', main_cat_name),
                translations.get('it', main_cat_name),
                f"Delicious {main_cat_name.lower()} options",  # Default description for all languages
                f"Delicious {main_cat_name.lower()} options",
                f"Delicious {main_cat_name.lower()} options",
                f"Delicious {main_cat_name.lower()} options",
                f"Delicious {main_cat_name.lower()} options",
                f"Delicious {main_cat_name.lower()} options",
                f"Delicious {main_cat_name.lower()} options",
                f"Delicious {main_cat_name.lower()} options"
            ))
            
            category_mapping[main_cat_name] = main_cat_id
            sort_order += 1
            
            # Handle subcategories
            sub_sort_order = 0
            for subcategory_name in main_category['subcategories']:
                sub_cat_id = str(uuid.uuid4())
                
                # Create translations for subcategory
                sub_translations = {}
                for lang_code, lang_categories in categories_by_language.items():
                    # Find corresponding main category in this language
                    cat_index = base_categories.index(main_category)
                    if cat_index < len(lang_categories):
                        lang_main_cat = lang_categories[cat_index]
                        # Find corresponding subcategory
                        sub_index = main_category['subcategories'].index(subcategory_name)
                        if sub_index < len(lang_main_cat['subcategories']):
                            sub_translations[lang_code] = lang_main_cat['subcategories'][sub_index]
                
                cursor.execute("""
                    INSERT INTO categories (
                        id, name, description, image_url, parent_id, sort_order, is_active,
                        name_az, name_en, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
                        description_az, description_en, description_ru, description_tr, 
                        description_ar, description_hi, description_fr, description_it
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    sub_cat_id,
                    subcategory_name,
                    f"Premium {subcategory_name.lower()} selection",
                    f"/images/categories/{subcategory_name.lower().replace(' ', '_')}.jpg",
                    main_cat_id,  # parent_id points to main category
                    sub_sort_order,
                    1,  # is_active
                    sub_translations.get('az', subcategory_name),
                    sub_translations.get('en', subcategory_name),
                    sub_translations.get('ru', subcategory_name),
                    sub_translations.get('tr', subcategory_name),
                    sub_translations.get('ar', subcategory_name),
                    sub_translations.get('hi', subcategory_name),
                    sub_translations.get('fr', subcategory_name),
                    sub_translations.get('it', subcategory_name),
                    f"Premium {subcategory_name.lower()} selection",
                    f"Premium {subcategory_name.lower()} selection",
                    f"Premium {subcategory_name.lower()} selection",
                    f"Premium {subcategory_name.lower()} selection",
                    f"Premium {subcategory_name.lower()} selection",
                    f"Premium {subcategory_name.lower()} selection",
                    f"Premium {subcategory_name.lower()} selection",
                    f"Premium {subcategory_name.lower()} selection"
                ))
                
                category_mapping[subcategory_name] = sub_cat_id
                sub_sort_order += 1
        
        conn.commit()
        
        # Log the results
        cursor.execute("SELECT COUNT(*) FROM categories WHERE parent_id IS NULL")
        main_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM categories WHERE parent_id IS NOT NULL")
        sub_count = cursor.fetchone()[0]
        
        logger.info(f"Successfully created {main_count} main categories and {sub_count} subcategories")
        
        # Save category mapping for CSV import
        with open('category_mapping.json', 'w', encoding='utf-8') as f:
            json.dump(category_mapping, f, indent=2, ensure_ascii=False)
        
        logger.info("Category mapping saved to category_mapping.json")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error creating category structure: {str(e)}", exc_info=True)
        return False

def verify_categories():
    """Verify that categories were created successfully"""
    try:
        db_path = os.path.join(os.path.dirname(__file__), "menu_data.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all categories with hierarchy
        cursor.execute("""
            SELECT 
                c1.name as main_category,
                c2.name as subcategory,
                c1.name_en as main_en,
                c2.name_en as sub_en
            FROM categories c1
            LEFT JOIN categories c2 ON c1.id = c2.parent_id
            WHERE c1.parent_id IS NULL
            ORDER BY c1.sort_order, c2.sort_order
        """)
        
        results = cursor.fetchall()
        
        logger.info("\nCategory Structure Verification:")
        logger.info("=" * 50)
        
        current_main = None
        for row in results:
            main_category, subcategory, main_en, sub_en = row
            
            if main_category != current_main:
                logger.info(f"\n{main_category} ({main_en})")
                current_main = main_category
            
            if subcategory:
                logger.info(f"  └─ {subcategory} ({sub_en})")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error verifying categories: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting category structure import...")
    
    if create_category_structure():
        if verify_categories():
            logger.info("Category structure import completed successfully!")
        else:
            logger.error("Category verification failed!")
            sys.exit(1)
    else:
        logger.error("Category structure import failed!")
        sys.exit(1)

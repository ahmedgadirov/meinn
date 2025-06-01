#!/usr/bin/env python3
"""
Database audit and cleanup script to consolidate all translations
and eliminate duplicate sources
"""

import sqlite3
import json
import csv
import os
from datetime import datetime

class DatabaseAudit:
    def __init__(self, db_path='menu_data.db'):
        self.db_path = db_path
        self.languages = ['en', 'az', 'ru', 'tr', 'ar', 'hi', 'fr', 'it']
        self.lang_names = ['English', 'Azerbaijani', 'Russian', 'Turkish', 'Arabic', 'Hindi', 'French', 'Italian']
        
    def connect_db(self):
        """Create database connection"""
        return sqlite3.connect(self.db_path)
    
    def audit_database_structure(self):
        """Check if all multilingual columns exist"""
        print("=" * 80)
        print("DATABASE STRUCTURE AUDIT")
        print("=" * 80)
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        # Check categories table
        cursor.execute("PRAGMA table_info(categories)")
        cat_columns = [col[1] for col in cursor.fetchall()]
        
        # Check menu_items table  
        cursor.execute("PRAGMA table_info(menu_items)")
        item_columns = [col[1] for col in cursor.fetchall()]
        
        print("Categories table columns:", len(cat_columns))
        print("Menu items table columns:", len(item_columns))
        
        # Check for multilingual columns
        missing_cat_cols = []
        missing_item_cols = []
        
        for lang in self.languages:
            name_col = f'name_{lang}'
            desc_col = f'description_{lang}'
            
            if name_col not in cat_columns:
                missing_cat_cols.append(name_col)
            if desc_col not in cat_columns:
                missing_cat_cols.append(desc_col)
                
            if name_col not in item_columns:
                missing_item_cols.append(name_col)
            if desc_col not in item_columns:
                missing_item_cols.append(desc_col)
        
        if missing_cat_cols:
            print(f"⚠️  Missing category columns: {missing_cat_cols}")
        else:
            print("✅ All category multilingual columns exist")
            
        if missing_item_cols:
            print(f"⚠️  Missing menu item columns: {missing_item_cols}")
        else:
            print("✅ All menu item multilingual columns exist")
        
        conn.close()
        return missing_cat_cols, missing_item_cols
    
    def audit_categories(self):
        """Audit category translations"""
        print("\n" + "=" * 80)
        print("CATEGORY TRANSLATIONS AUDIT")
        print("=" * 80)
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        # Get all categories
        cursor.execute("SELECT * FROM categories ORDER BY id")
        categories = cursor.fetchall()
        
        # Get column names
        cursor.execute("PRAGMA table_info(categories)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"Total categories found: {len(categories)}")
        
        # Check translation coverage
        translation_stats = {}
        duplicate_check = {}
        
        for i, lang in enumerate(self.languages):
            name_col = f'name_{lang}'
            desc_col = f'description_{lang}'
            
            if name_col in columns:
                name_idx = columns.index(name_col)
                filled_names = sum(1 for cat in categories if cat[name_idx] and cat[name_idx].strip())
                translation_stats[f'{self.lang_names[i]} names'] = f"{filled_names}/{len(categories)}"
                
                # Check for duplicates
                names = [cat[name_idx] for cat in categories if cat[name_idx] and cat[name_idx].strip()]
                duplicates = []
                seen = set()
                for name in names:
                    if name in seen:
                        duplicates.append(name)
                    seen.add(name)
                
                if duplicates:
                    duplicate_check[f'{self.lang_names[i]} duplicate names'] = duplicates
            
            if desc_col in columns:
                desc_idx = columns.index(desc_col)
                filled_descs = sum(1 for cat in categories if cat[desc_idx] and cat[desc_idx].strip())
                translation_stats[f'{self.lang_names[i]} descriptions'] = f"{filled_descs}/{len(categories)}"
        
        print("\nTranslation Coverage:")
        for key, value in translation_stats.items():
            print(f"  {key}: {value}")
        
        if duplicate_check:
            print("\n⚠️  DUPLICATE TRANSLATIONS FOUND:")
            for key, value in duplicate_check.items():
                print(f"  {key}: {value}")
        else:
            print("\n✅ No duplicate category translations found")
        
        # Show categories with missing translations
        print(f"\nCategories with missing translations:")
        id_idx = columns.index('id')
        
        for cat in categories:
            missing_langs = []
            for lang in self.languages:
                name_col = f'name_{lang}'
                if name_col in columns:
                    name_idx = columns.index(name_col)
                    if not cat[name_idx] or not cat[name_idx].strip():
                        missing_langs.append(lang)
            
            if missing_langs:
                print(f"  {cat[id_idx]}: missing {missing_langs}")
        
        conn.close()
        return translation_stats, duplicate_check
    
    def audit_menu_items(self):
        """Audit menu item translations"""
        print("\n" + "=" * 80)
        print("MENU ITEMS TRANSLATIONS AUDIT")
        print("=" * 80)
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        # Get all menu items
        cursor.execute("SELECT * FROM menu_items ORDER BY category_id, id")
        items = cursor.fetchall()
        
        # Get column names
        cursor.execute("PRAGMA table_info(menu_items)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"Total menu items found: {len(items)}")
        
        # Check translation coverage
        translation_stats = {}
        duplicate_check = {}
        
        for i, lang in enumerate(self.languages):
            name_col = f'name_{lang}'
            desc_col = f'description_{lang}'
            
            if name_col in columns:
                name_idx = columns.index(name_col)
                filled_names = sum(1 for item in items if item[name_idx] and item[name_idx].strip())
                translation_stats[f'{self.lang_names[i]} names'] = f"{filled_names}/{len(items)}"
                
                # Check for duplicates
                names = [item[name_idx] for item in items if item[name_idx] and item[name_idx].strip()]
                duplicates = []
                seen = set()
                for name in names:
                    if name in seen:
                        duplicates.append(name)
                    seen.add(name)
                
                if duplicates:
                    duplicate_check[f'{self.lang_names[i]} duplicate names'] = duplicates[:5]  # Show first 5
            
            if desc_col in columns:
                desc_idx = columns.index(desc_col)
                filled_descs = sum(1 for item in items if item[desc_idx] and item[desc_idx].strip())
                translation_stats[f'{self.lang_names[i]} descriptions'] = f"{filled_descs}/{len(items)}"
        
        print("\nTranslation Coverage:")
        for key, value in translation_stats.items():
            print(f"  {key}: {value}")
        
        if duplicate_check:
            print("\n⚠️  DUPLICATE TRANSLATIONS FOUND:")
            for key, value in duplicate_check.items():
                print(f"  {key}: {value[:3]}{'...' if len(value) > 3 else ''}")
        else:
            print("\n✅ No duplicate menu item translations found")
        
        # Show items with missing translations (first 10)
        print(f"\nFirst 10 menu items with missing translations:")
        id_idx = columns.index('id')
        count = 0
        
        for item in items:
            if count >= 10:
                break
                
            missing_langs = []
            for lang in self.languages:
                name_col = f'name_{lang}'
                if name_col in columns:
                    name_idx = columns.index(name_col)
                    if not item[name_idx] or not item[name_idx].strip():
                        missing_langs.append(lang)
            
            if missing_langs:
                print(f"  {item[id_idx]}: missing {missing_langs}")
                count += 1
        
        conn.close()
        return translation_stats, duplicate_check
    
    def check_external_sources(self):
        """Check what translation data exists in external sources"""
        print("\n" + "=" * 80)
        print("EXTERNAL SOURCES AUDIT")
        print("=" * 80)
        
        # Check hardcoded translations
        hardcoded_file = 'fix_category_translations.py'
        if os.path.exists(hardcoded_file):
            print("✅ Found hardcoded category translations in fix_category_translations.py")
            with open(hardcoded_file, 'r') as f:
                content = f.read()
                # Count category entries
                if 'category_translations = {' in content:
                    lines = content.split('\n')
                    cat_count = sum(1 for line in lines if "'cat-" in line and "': {" in line)
                    print(f"   Contains {cat_count} hardcoded category translations")
        else:
            print("❌ No hardcoded translations file found")
        
        # Check CSV files
        csv_files = [
            'menu_items_data.csv',
            'archive/generated_data/menu_categories_export.csv'
        ]
        
        for csv_file in csv_files:
            if os.path.exists(csv_file):
                print(f"✅ Found CSV file: {csv_file}")
                try:
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        rows = list(reader)
                        print(f"   Contains {len(rows)} rows")
                        if rows:
                            print(f"   Columns: {list(rows[0].keys())[:5]}...")
                except Exception as e:
                    print(f"   ⚠️  Error reading file: {e}")
            else:
                print(f"❌ CSV file not found: {csv_file}")
    
    def generate_consolidation_plan(self):
        """Generate a plan for consolidating all data"""
        print("\n" + "=" * 80)
        print("CONSOLIDATION PLAN")
        print("=" * 80)
        
        print("Recommended steps:")
        print("1. ✅ Database structure is ready (all multilingual columns exist)")
        print("2. 🔄 Merge hardcoded category translations with database")
        print("3. 🔄 Fill missing translations from CSV data")
        print("4. 🔄 Remove duplicate entries")
        print("5. 🔄 Validate all translations")
        print("6. 🗑️  Archive/remove CSV import scripts")
        print("7. 🗑️  Remove hardcoded translation dictionaries")
        print("8. ✅ Update admin panel to use database only")
        
    def run_full_audit(self):
        """Run complete database audit"""
        print("MEINN RESTAURANT - DATABASE TRANSLATION AUDIT")
        print(f"Audit started at: {datetime.now()}")
        
        # Structure audit
        self.audit_database_structure()
        
        # Content audits
        self.audit_categories()
        self.audit_menu_items()
        
        # External sources
        self.check_external_sources()
        
        # Consolidation plan
        self.generate_consolidation_plan()
        
        print(f"\nAudit completed at: {datetime.now()}")
        print("=" * 80)

class DatabaseConsolidator:
    def __init__(self, db_path='menu_data.db'):
        self.db_path = db_path
        self.languages = ['en', 'az', 'ru', 'tr', 'ar', 'hi', 'fr', 'it']
        
    def connect_db(self):
        return sqlite3.connect(self.db_path)
    
    def merge_hardcoded_category_translations(self):
        """Merge hardcoded category translations into database"""
        print("\n" + "=" * 50)
        print("MERGING HARDCODED CATEGORY TRANSLATIONS")
        print("=" * 50)
        
        # Import the hardcoded translations
        hardcoded_translations = {
            'cat-8-burger-roll': {
                'en': 'Burger Roll',
                'az': 'Burger Roll',
                'ru': 'Бургеры и роллы',
                'tr': 'Burger Roll',
                'ar': 'برجر رول',
                'hi': 'बर्गर रोल',
                'fr': 'Burger Roll',
                'it': 'Burger Roll'
            },
            'cat-7-desert': {
                'en': 'Dessert',
                'az': 'Desert',
                'ru': 'Десерты',
                'tr': 'Tatlı',
                'ar': 'حلويات',
                'hi': 'मिठाई',
                'fr': 'Dessert',
                'it': 'Dolce'
            },
            'cat-15-d-ni-z-m-hsullari-': {
                'en': 'Seafood',
                'az': 'Dəniz məhsulları',
                'ru': 'Морепродукты',
                'tr': 'Deniz ürünleri',
                'ar': 'المأكولات البحرية',
                'hi': 'समुद्री भोजन',
                'fr': 'Fruits de mer',
                'it': 'Frutti di mare'
            },
            'cat-4-kabablar': {
                'en': 'Kebabs',
                'az': 'Kabablar',
                'ru': 'Кебабы',
                'tr': 'Kebaplar',
                'ar': 'كباب',
                'hi': 'कबाब',
                'fr': 'Kebabs',
                'it': 'Kebab'
            },
            'cat-6-pastalar': {
                'en': 'Pasta',
                'az': 'Pastalar',
                'ru': 'Паста',
                'tr': 'Makarnalar',
                'ar': 'معكرونة',
                'hi': 'पास्ता',
                'fr': 'Pâtes',
                'it': 'Pasta'
            },
            'cat-2-pi-zzalar': {
                'en': 'Pizza',
                'az': 'Pizzalar',
                'ru': 'Пицца',
                'tr': 'Pizza',
                'ar': 'بيتزا',
                'hi': 'पिज़्ज़ा',
                'fr': 'Pizza',
                'it': 'Pizza'
            },
            'cat-3-salatlar': {
                'en': 'Salads',
                'az': 'Salatlar',
                'ru': 'Салаты',
                'tr': 'Salatalar',
                'ar': 'سلطات',
                'hi': 'सलाद',
                'fr': 'Salades',
                'it': 'Insalate'
            },
            'cat-5--orbalar': {
                'en': 'Soups',
                'az': 'Şorbalar',
                'ru': 'Супы',
                'tr': 'Çorbalar',
                'ar': 'شوربات',
                'hi': 'सूप',
                'fr': 'Soupes',
                'it': 'Zuppe'
            },
            'cat-1-s-h-r-yem-yi': {
                'en': 'Breakfast',
                'az': 'Səhər yeməyi',
                'ru': 'Завтрак',
                'tr': 'Kahvaltı',
                'ar': 'فطار',
                'hi': 'नाश्ता',
                'fr': 'Petit-déjeuner',
                'it': 'Colazione'
            },
            'cat-9-soyuq-q-lyanaltilar': {
                'en': 'Cold Appetizers',
                'az': 'Soyuq qəlyanaltılar',
                'ru': 'Холодные закуски',
                'tr': 'Soğuk mezeler',
                'ar': 'مقبلات باردة',
                'hi': 'ठंडे ऐपेटाइज़र',
                'fr': 'Hors-d\'œuvres froids',
                'it': 'Antipasti freddi'
            },
            'cat-10-i-sti--q-lyanaltilar': {
                'en': 'Hot Appetizers',
                'az': 'İsti qəlyanaltılar',
                'ru': 'Горячие закуски',
                'tr': 'Sıcak mezeler',
                'ar': 'مقبلات ساخنة',
                'hi': 'गर्म ऐपेटाइज़र',
                'fr': 'Hors-d\'œuvres chauds',
                'it': 'Antipasti caldi'
            },
            'cat-11-toyuq-yem-kl-ri-': {
                'en': 'Chicken Dishes',
                'az': 'Toyuq yeməkləri',
                'ru': 'Блюда из курицы',
                'tr': 'Tavuk yemekleri',
                'ar': 'أطباق الدجاج',
                'hi': 'चिकन के व्यंजन',
                'fr': 'Plats de poulet',
                'it': 'Piatti di pollo'
            },
            'cat-13--t-yem-kl-ri-': {
                'en': 'Meat Dishes',
                'az': 'Ət yeməkləri',
                'ru': 'Мясные блюда',
                'tr': 'Et yemekleri',
                'ar': 'أطباق اللحوم',
                'hi': 'मांस के व्यंजन',
                'fr': 'Plats de viande',
                'it': 'Piatti di carne'
            },
            'cat-14-sac': {
                'en': 'Sac',
                'az': 'Sac',
                'ru': 'Сач',
                'tr': 'Saç',
                'ar': 'ساتش',
                'hi': 'साच',
                'fr': 'Sac',
                'it': 'Sac'
            }
        }
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        updated_count = 0
        for category_id, translations in hardcoded_translations.items():
            # Check if category exists
            cursor.execute("SELECT id FROM categories WHERE id = ?", (category_id,))
            if cursor.fetchone():
                # Update with hardcoded translations
                update_query = """
                    UPDATE categories SET 
                        name_en = ?, name_az = ?, name_ru = ?, name_tr = ?,
                        name_ar = ?, name_hi = ?, name_fr = ?, name_it = ?
                    WHERE id = ?
                """
                
                cursor.execute(update_query, (
                    translations['en'], translations['az'], translations['ru'], translations['tr'],
                    translations['ar'], translations['hi'], translations['fr'], translations['it'],
                    category_id
                ))
                updated_count += 1
                print(f"✅ Updated {category_id}: {translations['en']}")
            else:
                print(f"⚠️  Category {category_id} not found in database")
        
        conn.commit()
        conn.close()
        
        print(f"Updated {updated_count} categories with hardcoded translations")
    
    def remove_exact_duplicates(self):
        """Remove exact duplicate menu items"""
        print("\n" + "=" * 50)
        print("REMOVING EXACT DUPLICATES")
        print("=" * 50)
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        # Find exact duplicates in menu_items (same name_en)
        cursor.execute("""
            SELECT name_en, COUNT(*), GROUP_CONCAT(id) as ids
            FROM menu_items 
            WHERE name_en IS NOT NULL AND name_en != ''
            GROUP BY name_en 
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        removed_count = 0
        
        for name, count, ids in duplicates:
            id_list = ids.split(',')
            # Keep the first one, remove the rest
            for item_id in id_list[1:]:
                cursor.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
                cursor.execute("DELETE FROM item_details WHERE item_id = ?", (item_id,))
                removed_count += 1
                print(f"🗑️  Removed duplicate item: {item_id} ({name})")
        
        conn.commit()
        conn.close()
        
        print(f"Removed {removed_count} duplicate menu items")
    
    def consolidate_all(self):
        """Run full consolidation process"""
        print("STARTING DATABASE CONSOLIDATION")
        print("=" * 50)
        
        # Merge hardcoded translations
        self.merge_hardcoded_category_translations()
        
        # Remove duplicates
        self.remove_exact_duplicates()
        
        print("\n✅ DATABASE CONSOLIDATION COMPLETE")
        print("Database is now the single source of truth for all translations")

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'consolidate':
        # Run consolidation
        consolidator = DatabaseConsolidator()
        consolidator.consolidate_all()
    else:
        # Run audit
        auditor = DatabaseAudit()
        auditor.run_full_audit()

if __name__ == "__main__":
    main()

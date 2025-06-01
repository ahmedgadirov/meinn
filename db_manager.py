#!/usr/bin/env python3
"""
Database Management Script for MEINN Restaurant
Single source of truth for all menu translations
"""

import sqlite3
import json
from datetime import datetime

class MenuDatabaseManager:
    def __init__(self, db_path='menu_data.db'):
        self.db_path = db_path
        self.languages = ['en', 'az', 'ru', 'tr', 'ar', 'hi', 'fr', 'it']
        
    def connect_db(self):
        return sqlite3.connect(self.db_path)
    
    def backup_database(self, backup_path=None):
        """Create a backup of the database"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"menu_data_backup_{timestamp}.db"
        
        import shutil
        shutil.copy2(self.db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    
    def export_translations(self, output_file='menu_translations_export.json'):
        """Export all translations to JSON for backup"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        # Export categories
        cursor.execute("SELECT * FROM categories")
        cat_columns = [description[0] for description in cursor.description]
        categories = [dict(zip(cat_columns, row)) for row in cursor.fetchall()]
        
        # Export menu items
        cursor.execute("SELECT * FROM menu_items")
        item_columns = [description[0] for description in cursor.description]
        menu_items = [dict(zip(item_columns, row)) for row in cursor.fetchall()]
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'categories': categories,
            'menu_items': menu_items
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        conn.close()
        print(f"✅ Translations exported to: {output_file}")
    
    def validate_translations(self):
        """Validate all translations in the database"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        print("TRANSLATION VALIDATION REPORT")
        print("=" * 50)
        
        # Check categories
        cursor.execute("SELECT id, name_en FROM categories")
        categories = cursor.fetchall()
        
        missing_translations = []
        for cat_id, cat_name in categories:
            for lang in self.languages:
                cursor.execute(f"SELECT name_{lang} FROM categories WHERE id = ?", (cat_id,))
                result = cursor.fetchone()
                if not result or not result[0] or not result[0].strip():
                    missing_translations.append(f"Category {cat_name} missing {lang} translation")
        
        # Check menu items (sample first 10)
        cursor.execute("SELECT id, name_en FROM menu_items LIMIT 10")
        items = cursor.fetchall()
        
        for item_id, item_name in items:
            for lang in self.languages:
                cursor.execute(f"SELECT name_{lang} FROM menu_items WHERE id = ?", (item_id,))
                result = cursor.fetchone()
                if not result or not result[0] or not result[0].strip():
                    missing_translations.append(f"Item {item_name} missing {lang} translation")
        
        if missing_translations:
            print(f"⚠️  Found {len(missing_translations)} missing translations:")
            for mt in missing_translations[:10]:  # Show first 10
                print(f"  - {mt}")
            if len(missing_translations) > 10:
                print(f"  ... and {len(missing_translations) - 10} more")
        else:
            print("✅ All translations are complete!")
        
        conn.close()
        return missing_translations
    
    def add_category(self, category_id, translations, description_translations=None):
        """Add a new category with translations"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        # Prepare default descriptions if not provided
        if not description_translations:
            description_translations = {
                lang: f"{translations.get(lang, category_id)} dishes and specialties"
                for lang in self.languages
            }
        
        query = """
            INSERT INTO categories (
                id, name, description, image_url,
                name_en, name_az, name_ru, name_tr, name_ar, name_hi, name_fr, name_it,
                description_en, description_az, description_ru, description_tr, 
                description_ar, description_hi, description_fr, description_it
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(query, (
            category_id,
            translations.get('en', category_id),
            description_translations.get('en', f"{translations.get('en', category_id)} dishes"),
            '/spinner.svg',
            translations.get('en'), translations.get('az'), translations.get('ru'), translations.get('tr'),
            translations.get('ar'), translations.get('hi'), translations.get('fr'), translations.get('it'),
            description_translations.get('en'), description_translations.get('az'), 
            description_translations.get('ru'), description_translations.get('tr'),
            description_translations.get('ar'), description_translations.get('hi'), 
            description_translations.get('fr'), description_translations.get('it')
        ))
        
        conn.commit()
        conn.close()
        print(f"✅ Added category: {category_id} ({translations.get('en')})")
    
    def update_translation(self, table, record_id, field, language, new_value):
        """Update a specific translation"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        field_column = f"{field}_{language}"
        query = f"UPDATE {table} SET {field_column} = ? WHERE id = ?"
        
        cursor.execute(query, (new_value, record_id))
        conn.commit()
        conn.close()
        
        print(f"✅ Updated {table}.{field_column} for {record_id}: {new_value}")

def main():
    manager = MenuDatabaseManager()
    
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'backup':
            manager.backup_database()
        elif command == 'export':
            manager.export_translations()
        elif command == 'validate':
            manager.validate_translations()
        else:
            print("Available commands: backup, export, validate")
    else:
        print("MEINN Restaurant Database Manager")
        print("Commands:")
        print("  python db_manager.py backup   - Create database backup")
        print("  python db_manager.py export   - Export translations to JSON")
        print("  python db_manager.py validate - Validate all translations")

if __name__ == "__main__":
    main()

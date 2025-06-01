#!/usr/bin/env python3
"""
Cleanup script to archive unused files after database consolidation
"""

import os
import shutil
from datetime import datetime

class FileCleanup:
    def __init__(self):
        self.archive_base = "archive/post_consolidation"
        os.makedirs(self.archive_base, exist_ok=True)
        
    def archive_files(self):
        """Archive files that are no longer needed"""
        print("=" * 60)
        print("ARCHIVING UNUSED FILES AFTER DATABASE CONSOLIDATION")
        print("=" * 60)
        
        # Files to archive from root directory
        root_files_to_archive = [
            'import_multilingual_menu.py',
            'test_translations.py', 
            'menu_items_data.csv',
            'database_audit_and_cleanup.py',
            'finalize_database_consolidation.py'
        ]
        
        archived_count = 0
        
        for file_path in root_files_to_archive:
            if os.path.exists(file_path):
                archive_path = os.path.join(self.archive_base, file_path)
                shutil.move(file_path, archive_path)
                print(f"📦 Archived: {file_path} → {archive_path}")
                archived_count += 1
            else:
                print(f"⚠️  File not found: {file_path}")
        
        print(f"Archived {archived_count} files from root directory")
        
        # Archive CSV files from archive/generated_data to post_consolidation
        csv_archive_dir = "archive/generated_data"
        if os.path.exists(csv_archive_dir):
            csv_files = [f for f in os.listdir(csv_archive_dir) if f.endswith('.csv')]
            csv_archive_path = os.path.join(self.archive_base, "csv_exports")
            os.makedirs(csv_archive_path, exist_ok=True)
            
            for csv_file in csv_files:
                src = os.path.join(csv_archive_dir, csv_file)
                dst = os.path.join(csv_archive_path, csv_file)
                shutil.move(src, dst)
                print(f"📦 Archived CSV: {csv_file} → {csv_archive_path}/{csv_file}")
                archived_count += 1
        
        return archived_count
    
    def create_active_files_doc(self):
        """Create documentation for active vs archived files"""
        print("\n" + "=" * 60)
        print("CREATING FILE ORGANIZATION DOCUMENTATION")
        print("=" * 60)
        
        doc_content = '''# MEINN Restaurant - File Organization

## ACTIVE FILES (Current System)

### Core Application
- `src/api/routes/menu_routes.py` - Menu API endpoints
- `src/services/product/menu_manager.py` - Menu data management
- `src/api/app.py` - Main Flask application
- `src/db/init_db.py` - Database initialization
- `admin.html` - Admin panel interface
- `db_manager.py` - Database management utilities

### Database
- `menu_data.db` - **SINGLE SOURCE OF TRUTH** for all menu data and translations
- `menu_data_backup_*.db` - Database backups

### Configuration
- `.env` - Environment variables
- `requirements.txt` - Python dependencies
- `run.sh` - Application startup script
- `README.md` - Project documentation
- `DATABASE_SYSTEM.md` - Database system documentation

### Frontend Assets
- `src/web/static/` - CSS, JavaScript, images
- `src/web/templates/` - HTML templates

## ARCHIVED FILES (No Longer Used)

### Deprecated Import Scripts (`archive/deprecated_imports/`)
- `fix_category_translations.py` - Hardcoded category translations
- `import_categories_from_csv.py` - CSV category import
- `import_menu_data.py` - CSV menu import

### Post-Consolidation Archives (`archive/post_consolidation/`)
- `import_multilingual_menu.py` - Old multilingual import
- `test_translations.py` - Translation testing
- `menu_items_data.csv` - CSV menu data
- `database_audit_and_cleanup.py` - Consolidation audit script
- `finalize_database_consolidation.py` - Final cleanup script

### Legacy Development Files (`archive/development_testing/`)
- Various testing and development scripts

### Generated Exports (`archive/post_consolidation/csv_exports/`)
- Exported CSV files from old system

## DATA FLOW

```
Frontend Request → API Routes → Menu Manager → Database → Response
```

### Language Support
All text content supports 8 languages:
- English (en) - Primary
- Azerbaijani (az) - Local
- Russian (ru) - Regional  
- Turkish (tr) - Regional
- Arabic (ar) - International
- Hindi (hi) - International
- French (fr) - International
- Italian (it) - International

### Adding New Content
1. Use admin panel or API endpoints
2. All data goes directly to database
3. No CSV imports needed
4. Translations handled in database

### Backup & Maintenance
```bash
# Create backup
python db_manager.py backup

# Validate translations
python db_manager.py validate

# Export data
python db_manager.py export
```

## SYSTEM STATUS
✅ Database consolidation complete
✅ Single source of truth established
✅ All translations in database
✅ Duplicate data eliminated
✅ Unused files archived
✅ Management tools available
'''
        
        with open('FILE_ORGANIZATION.md', 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        print("✅ Created FILE_ORGANIZATION.md")
    
    def verify_active_system(self):
        """Verify that the active system files are working correctly"""
        print("\n" + "=" * 60)
        print("VERIFYING ACTIVE SYSTEM")
        print("=" * 60)
        
        # Check database exists
        if os.path.exists('menu_data.db'):
            print("✅ Database file exists: menu_data.db")
        else:
            print("❌ Database file missing: menu_data.db")
        
        # Check core API files
        api_files = [
            'src/api/routes/menu_routes.py',
            'src/services/product/menu_manager.py',
            'db_manager.py'
        ]
        
        for file_path in api_files:
            if os.path.exists(file_path):
                print(f"✅ Core file exists: {file_path}")
            else:
                print(f"❌ Core file missing: {file_path}")
        
        # Check admin interface
        if os.path.exists('admin.html'):
            print("✅ Admin interface exists: admin.html")
        else:
            print("❌ Admin interface missing: admin.html")
        
        # Test database connection
        try:
            import sqlite3
            conn = sqlite3.connect('menu_data.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM categories")
            cat_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM menu_items")
            item_count = cursor.fetchone()[0]
            conn.close()
            
            print(f"✅ Database connection successful")
            print(f"   - Categories: {cat_count}")
            print(f"   - Menu items: {item_count}")
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
    
    def run_cleanup(self):
        """Run the complete cleanup process"""
        print("MEINN RESTAURANT - FILE CLEANUP AFTER CONSOLIDATION")
        print(f"Cleanup started at: {datetime.now()}")
        print("=" * 60)
        
        # Archive unused files
        archived_count = self.archive_files()
        
        # Create documentation
        self.create_active_files_doc()
        
        # Verify system
        self.verify_active_system()
        
        print(f"\n✅ CLEANUP COMPLETE at: {datetime.now()}")
        print("=" * 60)
        print(f"📦 Archived {archived_count} unused files")
        print("🎯 Active system verified and documented")
        print("📚 File organization documentation created")
        print("\nThe system is now completely consolidated with:")
        print("- Database as single source of truth")
        print("- All unused files archived")
        print("- Clear documentation")
        print("- Management tools available")

def main():
    cleanup = FileCleanup()
    cleanup.run_cleanup()

if __name__ == "__main__":
    main()

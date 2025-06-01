# MEINN Restaurant - File Organization

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

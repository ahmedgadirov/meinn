# MEINN Restaurant - Database Translation System

## Overview
The restaurant menu now uses a **single source of truth** - the SQLite database (`menu_data.db`). All translations and menu data are stored and managed through the database only.

## Database Structure

### Categories Table
- `id` - Unique category identifier
- `name`, `description`, `image_url` - Default fields
- `name_en`, `name_az`, `name_ru`, `name_tr`, `name_ar`, `name_hi`, `name_fr`, `name_it` - Category names in 8 languages
- `description_en`, `description_az`, etc. - Category descriptions in 8 languages

### Menu Items Table  
- `id` - Unique item identifier
- `name`, `description`, `category_id`, `price`, etc. - Default fields
- `name_en`, `name_az`, `name_ru`, `name_tr`, `name_ar`, `name_hi`, `name_fr`, `name_it` - Item names in 8 languages
- `description_en`, `description_az`, etc. - Item descriptions in 8 languages

## Supported Languages
1. **English (en)** - Primary language
2. **Azerbaijani (az)** - Local language
3. **Russian (ru)** - Regional language
4. **Turkish (tr)** - Regional language
5. **Arabic (ar)** - International
6. **Hindi (hi)** - International
7. **French (fr)** - International
8. **Italian (it)** - International

## Management Tools

### Database Manager (`db_manager.py`)
```bash
# Create backup
python db_manager.py backup

# Export translations to JSON
python db_manager.py export

# Validate all translations
python db_manager.py validate
```

### Direct Database Access
```python
import sqlite3

conn = sqlite3.connect('menu_data.db')
cursor = conn.cursor()

# Get all categories with English names
cursor.execute("SELECT id, name_en FROM categories")
categories = cursor.fetchall()

# Update a translation
cursor.execute("UPDATE categories SET name_fr = ? WHERE id = ?", ("Nouvelle traduction", "cat-1"))
conn.commit()

conn.close()
```

## Admin Panel Integration
The admin panel should connect directly to the database:

```python
# Example: Get menu for specific language
def get_menu_for_language(language='en'):
    conn = sqlite3.connect('menu_data.db')
    cursor = conn.cursor()
    
    # Get categories
    cursor.execute(f"SELECT id, name_{language} FROM categories ORDER BY name_{language}")
    categories = cursor.fetchall()
    
    # Get items for each category
    menu = {}
    for cat_id, cat_name in categories:
        cursor.execute(f"""
            SELECT id, name_{language}, description_{language}, price 
            FROM menu_items 
            WHERE category_id = ? 
            ORDER BY name_{language}
        """, (cat_id,))
        
        menu[cat_name] = cursor.fetchall()
    
    conn.close()
    return menu
```

## Maintenance Notes

### ✅ ACTIVE SYSTEM
- **Database**: `menu_data.db` - Single source of truth
- **Manager**: `db_manager.py` - Database management tools
- **API**: Direct database connections in `src/api/`
- **Admin**: Direct database connections in admin panel

### 🗑️ DEPRECATED (Archived)
- `fix_category_translations.py` - Hardcoded translations
- `import_categories_from_csv.py` - CSV imports
- `import_menu_data.py` - CSV imports
- All CSV import methods

### 🔒 DATA INTEGRITY
- Always backup before major changes: `python db_manager.py backup`
- Validate after updates: `python db_manager.py validate`
- Export regularly: `python db_manager.py export`

## Migration Complete
- ✅ All hardcoded translations merged into database
- ✅ All duplicate data removed
- ✅ All import scripts archived
- ✅ Database is now single source of truth
- ✅ Management tools created

#!/usr/bin/env python3
"""
Fix category translations in the database
"""

import sqlite3

def fix_category_translations():
    """Add proper translations for categories"""
    
    # Category translations mapping
    category_translations = {
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
    
    conn = sqlite3.connect('menu_data.db')
    cursor = conn.cursor()
    
    print("Updating category translations...")
    
    # Get all categories
    cursor.execute("SELECT id FROM categories")
    categories = cursor.fetchall()
    
    for category_row in categories:
        category_id = category_row[0]
        
        if category_id in category_translations:
            translations = category_translations[category_id]
            
            # Update all language columns
            cursor.execute("""
                UPDATE categories SET 
                    name_en = ?, name_az = ?, name_ru = ?, name_tr = ?,
                    name_ar = ?, name_hi = ?, name_fr = ?, name_it = ?
                WHERE id = ?
            """, (
                translations['en'], translations['az'], translations['ru'], translations['tr'],
                translations['ar'], translations['hi'], translations['fr'], translations['it'],
                category_id
            ))
            
            print(f"Updated translations for: {category_id} -> {translations['en']}")
        else:
            print(f"Warning: No translations found for category {category_id}")
    
    conn.commit()
    conn.close()
    
    print("Category translations updated successfully!")

def verify_translations():
    """Verify the translations were applied correctly"""
    conn = sqlite3.connect('menu_data.db')
    cursor = conn.cursor()
    
    print("\nVerifying category translations:")
    cursor.execute("SELECT id, name_en, name_az, name_ru FROM categories ORDER BY name_en")
    categories = cursor.fetchall()
    
    for cat in categories:
        print(f"{cat[1]:15} | {cat[2]:20} | {cat[3]:15}")
    
    conn.close()

if __name__ == "__main__":
    fix_category_translations()
    verify_translations()

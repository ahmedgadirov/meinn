#!/usr/bin/env python3
"""
Export menu items from admin panel database to various formats
"""

import sqlite3
import csv
import json
from datetime import datetime

def get_all_menu_data():
    """Get all menu items and categories from database"""
    conn = sqlite3.connect('menu_data.db')
    cursor = conn.cursor()
    
    # Get categories
    cursor.execute("""
        SELECT id, name, description, image_url, name_en, name_az, name_ru
        FROM categories
        ORDER BY name
    """)
    categories = cursor.fetchall()
    
    # Get menu items with category names
    cursor.execute("""
        SELECT m.id, m.name, m.description, m.category_id, c.name as category_name,
               m.price, m.available, m.image_url, m.popular, m.preparation_time,
               m.name_en, m.name_az, m.name_ru, m.name_tr, m.name_ar, m.name_hi, m.name_fr, m.name_it,
               m.description_en, m.description_az, m.description_ru, m.description_tr, m.description_ar, m.description_hi, m.description_fr, m.description_it,
               m.created_at, m.updated_at
        FROM menu_items m
        LEFT JOIN categories c ON m.category_id = c.id
        ORDER BY c.name, m.name
    """)
    menu_items = cursor.fetchall()
    
    conn.close()
    return categories, menu_items

def export_to_csv(categories, menu_items):
    """Export menu items to CSV format"""
    
    # Export categories
    with open('menu_categories_export.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'Name', 'Description', 'Image URL', 'Name EN', 'Name AZ', 'Name RU'])
        for cat in categories:
            writer.writerow(cat)
    
    # Export menu items
    with open('menu_items_export.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'Name', 'Description', 'Category ID', 'Category Name', 
                        'Price', 'Available', 'Image URL', 'Popular', 'Preparation Time',
                        'Name EN', 'Name AZ', 'Name RU', 'Name TR', 'Name AR', 'Name HI', 'Name FR', 'Name IT',
                        'Description EN', 'Description AZ', 'Description RU', 'Description TR', 'Description AR', 'Description HI', 'Description FR', 'Description IT',
                        'Created At', 'Updated At'])
        for item in menu_items:
            writer.writerow(item)
    
    print("✓ CSV files exported: menu_categories_export.csv, menu_items_export.csv")

def export_to_txt(categories, menu_items):
    """Export menu items to TXT format"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open('menu_export.txt', 'w', encoding='utf-8') as f:
        f.write("MEINN RESTAURANT MENU EXPORT\n")
        f.write("=" * 50 + "\n")
        f.write(f"Export Date: {timestamp}\n")
        f.write(f"Total Categories: {len(categories)}\n")
        f.write(f"Total Menu Items: {len(menu_items)}\n")
        f.write("=" * 50 + "\n\n")
        
        # Group items by category
        current_category = None
        for item in menu_items:
            category_name = item[4]  # category_name
            
            if category_name != current_category:
                current_category = category_name
                f.write(f"\n{'='*20} {category_name} {'='*20}\n\n")
            
            f.write(f"• {item[1]}\n")  # name
            if item[2]:  # description
                f.write(f"  Description: {item[2]}\n")
            f.write(f"  Price: ${item[5]}\n")  # price
            f.write(f"  Available: {'Yes' if item[6] else 'No'}\n")  # available
            f.write(f"  Popular: {'Yes' if item[8] else 'No'}\n")  # popular
            f.write(f"  Preparation Time: {item[9]} minutes\n")  # preparation_time
            if item[10]:  # name_en
                f.write(f"  English Name: {item[10]}\n")
            if item[11]:  # name_az
                f.write(f"  Azerbaijani Name: {item[11]}\n")
            if item[12]:  # name_ru
                f.write(f"  Russian Name: {item[12]}\n")
            f.write(f"  ID: {item[0]}\n")  # id
            f.write("\n")
    
    print("✓ TXT file exported: menu_export.txt")

def export_to_markdown(categories, menu_items):
    """Export menu items to Markdown format"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open('menu_export.md', 'w', encoding='utf-8') as f:
        f.write("# MEINN Restaurant Menu\n\n")
        f.write(f"**Export Date:** {timestamp}\n\n")
        f.write(f"**Statistics:**\n")
        f.write(f"- Categories: {len(categories)}\n")
        f.write(f"- Menu Items: {len(menu_items)}\n\n")
        f.write("---\n\n")
        
        # Table of contents
        f.write("## Table of Contents\n\n")
        for cat in categories:
            cat_name = cat[1]
            anchor = cat_name.lower().replace(' ', '-').replace('ə', 'e').replace('ı', 'i').replace('ö', 'o').replace('ü', 'u').replace('ç', 'c').replace('ş', 's').replace('ğ', 'g')
            f.write(f"- [{cat_name}](#{anchor})\n")
        f.write("\n---\n\n")
        
        # Group items by category
        current_category = None
        for item in menu_items:
            category_name = item[4]  # category_name
            
            if category_name != current_category:
                current_category = category_name
                anchor = category_name.lower().replace(' ', '-').replace('ə', 'e').replace('ı', 'i').replace('ö', 'o').replace('ü', 'u').replace('ç', 'c').replace('ş', 's').replace('ğ', 'g')
                f.write(f"## {category_name}\n\n")
            
            f.write(f"### {item[1]}\n\n")  # name
            
            # Create info table
            f.write("| Property | Value |\n")
            f.write("|----------|-------|\n")
            f.write(f"| **Price** | ${item[5]} |\n")  # price
            f.write(f"| **Available** | {'✅ Yes' if item[6] else '❌ No'} |\n")  # available
            f.write(f"| **Popular** | {'⭐ Yes' if item[8] else 'No'} |\n")  # popular
            f.write(f"| **Preparation Time** | {item[9]} minutes |\n")  # preparation_time
            
            if item[2]:  # description
                f.write(f"| **Description** | {item[2]} |\n")
            
            # Translations
            if item[10]:  # name_en
                f.write(f"| **English Name** | {item[10]} |\n")
            if item[11]:  # name_az
                f.write(f"| **Azerbaijani Name** | {item[11]} |\n")
            if item[12]:  # name_ru
                f.write(f"| **Russian Name** | {item[12]} |\n")
            
            f.write(f"| **Item ID** | `{item[0]}` |\n")
            f.write(f"| **Category ID** | `{item[3]}` |\n\n")
            
            f.write("---\n\n")
    
    print("✓ Markdown file exported: menu_export.md")

def export_to_json(categories, menu_items):
    """Export menu items to JSON format"""
    
    # Convert categories to dict
    categories_dict = []
    for cat in categories:
        categories_dict.append({
            'id': cat[0],
            'name': cat[1],
            'description': cat[2],
            'image_url': cat[3],
            'translations': {
                'en': cat[4],
                'az': cat[5],
                'ru': cat[6]
            }
        })
    
    # Convert menu items to dict
    menu_items_dict = []
    for item in menu_items:
        menu_items_dict.append({
            'id': item[0],
            'name': item[1],
            'description': item[2],
            'category_id': item[3],
            'category_name': item[4],
            'price': item[5],
            'available': bool(item[6]),
            'image_url': item[7],
            'popular': bool(item[8]),
            'preparation_time': item[9],
            'translations': {
                'names': {
                    'en': item[10],
                    'az': item[11],
                    'ru': item[12],
                    'tr': item[13],
                    'ar': item[14],
                    'hi': item[15],
                    'fr': item[16],
                    'it': item[17]
                },
                'descriptions': {
                    'en': item[18],
                    'az': item[19],
                    'ru': item[20],
                    'tr': item[21],
                    'ar': item[22],
                    'hi': item[23],
                    'fr': item[24],
                    'it': item[25]
                }
            },
            'created_at': item[26],
            'updated_at': item[27]
        })
    
    # Create complete export structure
    export_data = {
        'export_info': {
            'timestamp': datetime.now().isoformat(),
            'total_categories': len(categories),
            'total_menu_items': len(menu_items)
        },
        'categories': categories_dict,
        'menu_items': menu_items_dict
    }
    
    with open('menu_export.json', 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print("✓ JSON file exported: menu_export.json")

def main():
    """Main export function"""
    print("MEINN Restaurant Menu Exporter")
    print("=" * 40)
    
    try:
        # Get data from database
        print("📊 Fetching data from database...")
        categories, menu_items = get_all_menu_data()
        
        print(f"✓ Found {len(categories)} categories and {len(menu_items)} menu items")
        print()
        
        # Export to different formats
        print("📁 Exporting to different formats...")
        export_to_csv(categories, menu_items)
        export_to_txt(categories, menu_items)
        export_to_markdown(categories, menu_items)
        export_to_json(categories, menu_items)
        
        print()
        print("🎉 Export completed successfully!")
        print()
        print("Generated files:")
        print("- menu_categories_export.csv (Categories in CSV format)")
        print("- menu_items_export.csv (Menu items in CSV format)")
        print("- menu_export.txt (Complete menu in text format)")
        print("- menu_export.md (Complete menu in Markdown format)")
        print("- menu_export.json (Complete menu in JSON format)")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Export error: {e}")

if __name__ == "__main__":
    main()

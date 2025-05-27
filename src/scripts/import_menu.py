#!/usr/bin/env python
"""
Import menu data from HTML into the menu_data.db database.
This script extracts categories and menu items from the provided HTML content
and inserts them into the database.
"""

import os
import sys
import sqlite3
import json
from bs4 import BeautifulSoup
import re

# Add the project root directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, project_root)

# Database path
DB_PATH = os.path.join(project_root, "menu_data.db")

def extract_price(price_text):
    """Extract numeric price from text like '12.5 Azn'"""
    match = re.search(r'(\d+\.?\d*)', price_text)
    if match:
        return float(match.group(1))
    return 0.0

def clean_text(text):
    """Clean text by removing extra whitespace"""
    if text:
        return re.sub(r'\s+', ' ', text).strip()
    return ""

def extract_menu_data(html_content):
    """Extract menu categories and items from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    categories = []
    menu_items = []
    
    # Find all category groups
    category_groups = soup.find_all('div', class_='foods-group-subcategory')
    
    for idx, category_group in enumerate(category_groups):
        # Extract category data
        category_title_div = category_group.find('div', class_='foods-group-title')
        if not category_title_div:
            continue
        
        category_name = category_title_div.get_text().strip()
        category_id = f"cat-{idx+1}-{re.sub(r'[^a-zA-Z0-9]', '-', category_name.lower())}"
        
        category = {
            "id": category_id,
            "name": category_name,
            "description": f"{category_name} menu items",
            "image_url": "/static/images/categories/placeholder.jpg"
        }
        categories.append(category)
        
        # Extract menu items for this category
        items_div = category_group.find('div', class_='foods-group-items')
        if not items_div:
            continue
            
        food_items = items_div.find_all('a', class_='foods-item')
        
        for item_idx, food_item in enumerate(food_items):
            try:
                # Extract item data
                title_div = food_item.find('div', class_='foods-item-title')
                desc_div = food_item.find('div', class_='foods-item-desc')
                price_div = food_item.find('div', class_='foods-item-bottom-price')
                img_tag = food_item.find('img')
                
                if not title_div or not price_div:
                    continue
                    
                # Generate a unique ID for the item
                title_text = title_div.get_text().strip()
                item_id = f"{category_id}-{item_idx+1}-{re.sub(r'[^a-zA-Z0-9]', '-', title_text.lower())}"
                
                # Extract item details
                title = clean_text(title_div.get_text())
                description = clean_text(desc_div.get_text()) if desc_div else ""
                price = extract_price(price_div.get_text())
                image_url = img_tag.get('src') if img_tag else "/static/images/menu-placeholder.svg"
                
                menu_item = {
                    "id": item_id,
                    "name": title,
                    "description": description,
                    "category_id": category_id,
                    "price": price,
                    "image_url": image_url,
                    "available": True,
                    "popular": False,
                    "preparation_time": 15,  # Default value
                    "allergens": [],
                    "ingredients": [],
                    "nutrition": {
                        "calories": 0,
                        "protein": 0,
                        "carbs": 0,
                        "fat": 0
                    }
                }
                menu_items.append(menu_item)
                
            except Exception as e:
                print(f"Error processing menu item: {e}")
    
    return categories, menu_items

def import_to_database(categories, menu_items):
    """Import categories and menu items into the database"""
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Insert categories
        for category in categories:
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO categories (id, name, description, image_url) VALUES (?, ?, ?, ?)",
                    (category['id'], category['name'], category['description'], category['image_url'])
                )
            except sqlite3.IntegrityError:
                print(f"Category {category['id']} already exists, skipping.")
            except Exception as e:
                print(f"Error inserting category {category['id']}: {e}")
        
        # Insert menu items
        for item in menu_items:
            try:
                # Check if item with this ID already exists
                cursor.execute("SELECT id FROM menu_items WHERE id = ?", (item['id'],))
                if cursor.fetchone():
                    print(f"Item {item['id']} already exists, skipping.")
                    continue
                    
                # Insert into menu_items table
                cursor.execute(
                    """INSERT INTO menu_items 
                       (id, name, description, category_id, price, image_url, available, popular, preparation_time) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        item['id'],
                        item['name'],
                        item['description'],
                        item['category_id'],
                        item['price'],
                        item['image_url'],
                        1 if item['available'] else 0,
                        1 if item['popular'] else 0,
                        item['preparation_time']
                    )
                )
                
                # Insert into item_details table
                cursor.execute(
                    "INSERT INTO item_details (item_id, allergens, ingredients, nutrition) VALUES (?, ?, ?, ?)",
                    (
                        item['id'],
                        json.dumps(item['allergens']),
                        json.dumps(item['ingredients']),
                        json.dumps(item['nutrition'])
                    )
                )
            except Exception as e:
                print(f"Error inserting menu item {item['id']}: {e}")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print(f"Successfully imported {len(categories)} categories and {len(menu_items)} menu items")
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False

def main():
    """Main function to run the import process"""
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        print("Make sure the application is initialized correctly before running this script.")
        return False
    
    # Get HTML content from file
    html_file = os.path.join(current_dir, "menu_html.txt")
    
    try:
        if not os.path.exists(html_file):
            print(f"HTML file not found at {html_file}")
            print("Creating a new file. Please paste the menu HTML content into this file.")
            
            # Get the HTML content from the user
            print("Enter/paste the menu HTML content (press Ctrl+D or Ctrl+Z to finish):")
            html_content = sys.stdin.read()
            
            # Save the content to a file for future reference
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
        else:
            # Read the HTML content from the file
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
        
        # Extract menu data
        categories, menu_items = extract_menu_data(html_content)
        
        # Print summary
        print(f"Extracted {len(categories)} categories and {len(menu_items)} menu items")
        
        # Import to database
        import_to_database(categories, menu_items)
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    main()

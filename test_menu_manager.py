#!/usr/bin/env python3

from src.services.product.menu_manager import MenuManager

def test_menu_manager():
    print("Testing MenuManager...")
    
    manager = MenuManager()
    
    # Test categories
    categories = manager.get_categories()
    print(f'Categories: {len(categories)}')
    for cat in categories[:3]:
        print(f'  - {cat["id"]}: {cat["name"]}')
    
    # Test items
    items = manager.get_menu_items()
    print(f'Items: {len(items)}')
    for item in items[:3]:
        print(f'  - {item["id"]}: {item["name"]} (${item["price"]})')

if __name__ == "__main__":
    test_menu_manager()

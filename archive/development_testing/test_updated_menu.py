#!/usr/bin/env python3
"""
Test script to verify the updated menu system with multilingual support.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.services.product.menu_manager import MenuManager

def test_menu_system():
    """Test the updated menu system"""
    print("Testing Updated Menu System with Multilingual Support")
    print("=" * 60)
    
    # Initialize menu manager
    menu_manager = MenuManager()
    
    # Test categories in different languages
    print("\n1. Testing Categories:")
    print("-" * 30)
    
    languages = ['en', 'az', 'ru', 'tr']
    for lang in languages:
        print(f"\nCategories in {lang.upper()}:")
        categories = menu_manager.get_categories(language=lang)
        for cat in categories[:3]:  # Show first 3 categories
            print(f"  - {cat['name']}: {cat['description'][:50]}...")
    
    # Test menu items in different languages
    print("\n\n2. Testing Menu Items:")
    print("-" * 30)
    
    for lang in languages:
        print(f"\nMenu Items in {lang.upper()} (first 5):")
        items = menu_manager.get_menu_items(available_only=True, language=lang)
        for item in items[:5]:
            print(f"  - {item['name']} (${item['price']}) - {item['description'][:40]}...")
    
    # Test search functionality
    print("\n\n3. Testing Search:")
    print("-" * 30)
    
    search_terms = ['pizza', 'chicken', 'drink']
    for term in search_terms:
        print(f"\nSearching for '{term}' in English:")
        results = menu_manager.search_menu(term, language='en')
        for result in results[:3]:
            print(f"  - {result['name']} (${result['price']})")
    
    # Test menu summary
    print("\n\n4. Testing Menu Summary:")
    print("-" * 30)
    
    summary = menu_manager.get_menu_summary(language='en')
    print(f"Total Categories: {summary['total_categories']}")
    print(f"Total Items: {summary['total_items']}")
    print(f"Popular Items: {len(summary['popular_items'])}")
    
    print("\nCategory breakdown:")
    for cat_name, cat_data in summary['categories'].items():
        print(f"  - {cat_name}: {cat_data['item_count']} items")
    
    # Test specific item retrieval
    print("\n\n5. Testing Item Retrieval:")
    print("-" * 30)
    
    # Get first item ID
    all_items = menu_manager.get_menu_items(available_only=True, language='en')
    if all_items:
        item_id = all_items[0]['id']
        print(f"\nGetting details for item: {item_id}")
        
        for lang in ['en', 'az']:
            item = menu_manager.get_item_by_id(item_id, language=lang)
            if item:
                print(f"  {lang.upper()}: {item['name']} - ${item['price']}")
                if item.get('suggested_pairings'):
                    print(f"    Suggested pairings: {len(item['suggested_pairings'])}")
    
    print("\n" + "=" * 60)
    print("Menu system test completed!")

if __name__ == "__main__":
    test_menu_system()

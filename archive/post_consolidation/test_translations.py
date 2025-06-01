#!/usr/bin/env python3
"""
Test script to verify multilingual functionality is working correctly
"""

import sys
import os
sys.path.append('src')

from services.product.menu_manager import MenuManager

def test_translation_functionality():
    """Test if MenuManager correctly handles different languages"""
    print("=== Testing MenuManager Translation Functionality ===\n")
    
    # Test languages
    languages = ['en', 'az', 'ru', 'tr', 'ar', 'hi', 'fr', 'it']
    lang_names = ['English', 'Azerbaijani', 'Russian', 'Turkish', 'Arabic', 'Hindi', 'French', 'Italian']
    
    menu_manager = MenuManager()
    
    # Test 1: Check multilingual support detection
    print("1. Testing multilingual support detection...")
    supports_multilingual = menu_manager._check_multilingual_support()
    print(f"   Multilingual support detected: {supports_multilingual}")
    
    if not supports_multilingual:
        print("   ERROR: MenuManager is not detecting multilingual support!")
        return False
    
    # Test 2: Test translation columns for each language
    print("\n2. Testing translation column detection...")
    for i, lang in enumerate(languages):
        name_col, desc_col = menu_manager._get_translation_columns(lang)
        print(f"   {lang_names[i]} ({lang}): {name_col}, {desc_col}")
    
    # Test 3: Get categories in different languages
    print("\n3. Testing category retrieval in different languages...")
    for i, lang in enumerate(languages):
        try:
            categories = menu_manager.get_categories(language=lang)
            if categories:
                sample_cat = categories[0]
                print(f"   {lang_names[i]} ({lang}): {sample_cat.get('name', 'N/A')}")
            else:
                print(f"   {lang_names[i]} ({lang}): No categories found")
        except Exception as e:
            print(f"   {lang_names[i]} ({lang}): ERROR - {str(e)}")
    
    # Test 4: Get a specific menu item in different languages
    print("\n4. Testing menu item retrieval in different languages...")
    
    # First, get any menu item ID
    try:
        items_en = menu_manager.get_menu_items(language='en')
        if items_en:
            test_item_id = items_en[0]['id']
            print(f"   Testing with item ID: {test_item_id}")
            
            for i, lang in enumerate(languages):
                try:
                    item = menu_manager.get_menu_item(test_item_id, language=lang)
                    if item:
                        print(f"   {lang_names[i]} ({lang}): {item.get('name', 'N/A')}")
                    else:
                        print(f"   {lang_names[i]} ({lang}): Item not found")
                except Exception as e:
                    print(f"   {lang_names[i]} ({lang}): ERROR - {str(e)}")
        else:
            print("   No menu items found for testing")
    except Exception as e:
        print(f"   ERROR getting menu items: {str(e)}")
    
    # Test 5: Get full menu for a specific language
    print("\n5. Testing full menu retrieval...")
    try:
        # Test with Azerbaijani
        menu_az = menu_manager.get_menu_items(language='az')
        print(f"   Azerbaijani menu items: {len(menu_az)} found")
        if menu_az:
            print(f"   Sample item: {menu_az[0].get('name', 'N/A')}")
        
        # Test with Russian
        menu_ru = menu_manager.get_menu_items(language='ru')
        print(f"   Russian menu items: {len(menu_ru)} found")
        if menu_ru:
            print(f"   Sample item: {menu_ru[0].get('name', 'N/A')}")
            
    except Exception as e:
        print(f"   ERROR: {str(e)}")
    
    print("\n=== Translation Test Complete ===")
    return True

if __name__ == "__main__":
    test_translation_functionality()

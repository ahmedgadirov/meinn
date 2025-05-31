#!/usr/bin/env python3
"""
Test script for multilingual API functionality
Tests all the updated menu routes with different language parameters
"""

import requests
import json
import sys

# Test configuration
BASE_URL = "http://localhost:5002"
API_BASE = f"{BASE_URL}/api/menu"

def test_endpoint(endpoint, params=None, method='GET'):
    """Test an API endpoint and return the response"""
    try:
        if method == 'GET':
            response = requests.get(f"{API_BASE}{endpoint}", params=params)
        else:
            response = requests.request(method, f"{API_BASE}{endpoint}", params=params)
        
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the server is running on http://localhost:5000")
        return None, None
    except Exception as e:
        print(f"❌ Error testing {endpoint}: {str(e)}")
        return None, None

def print_test_result(test_name, status_code, data, expected_status=200):
    """Print formatted test results"""
    if status_code is None:
        print(f"❌ {test_name}: Failed to connect")
        return False
    
    if status_code == expected_status:
        print(f"✅ {test_name}: Status {status_code}")
        return True
    else:
        print(f"❌ {test_name}: Status {status_code} (expected {expected_status})")
        if 'error' in data:
            print(f"   Error: {data['error']}")
        return False

def test_multilingual_categories():
    """Test categories endpoint with different languages"""
    print("\n=== Testing Categories Endpoint ===")
    
    languages = ['en', 'az', 'ru', 'tr']
    
    for lang in languages:
        status_code, data = test_endpoint("/categories", params={'language': lang})
        success = print_test_result(f"Categories ({lang})", status_code, data)
        
        if success and data.get('success'):
            categories = data.get('categories', [])
            print(f"   Found {len(categories)} categories")
            
            # Show sample category names for verification
            if categories:
                sample_cat = categories[0]
                print(f"   Sample: {sample_cat.get('name', 'N/A')} (ID: {sample_cat.get('id', 'N/A')})")

def test_multilingual_items():
    """Test menu items endpoint with different languages"""
    print("\n=== Testing Menu Items Endpoint ===")
    
    languages = ['en', 'az', 'ru', 'tr']
    
    for lang in languages:
        status_code, data = test_endpoint("/items", params={'language': lang})
        success = print_test_result(f"Menu Items ({lang})", status_code, data)
        
        if success and data.get('success'):
            items = data.get('items', [])
            print(f"   Found {len(items)} items")
            
            # Show sample item names for verification
            if items:
                sample_item = items[0]
                print(f"   Sample: {sample_item.get('name', 'N/A')} - {sample_item.get('category', 'N/A')}")

def test_search_functionality():
    """Test search with different languages"""
    print("\n=== Testing Search Functionality ===")
    
    search_terms = {
        'en': 'burger',
        'az': 'burger',
        'ru': 'бургер',
        'tr': 'burger'
    }
    
    for lang, term in search_terms.items():
        status_code, data = test_endpoint("/items", params={'language': lang, 'search': term})
        success = print_test_result(f"Search '{term}' ({lang})", status_code, data)
        
        if success and data.get('success'):
            items = data.get('items', [])
            print(f"   Found {len(items)} matching items")

def test_item_details():
    """Test individual item details with language support"""
    print("\n=== Testing Item Details ===")
    
    # First get a sample item ID
    status_code, data = test_endpoint("/items")
    if status_code == 200 and data.get('success'):
        items = data.get('items', [])
        if items:
            sample_item_id = items[0]['id']
            print(f"   Testing with item ID: {sample_item_id}")
            
            for lang in ['en', 'az', 'ru']:
                status_code, data = test_endpoint(f"/items/{sample_item_id}", params={'language': lang})
                success = print_test_result(f"Item Details ({lang})", status_code, data)
                
                if success and data.get('success'):
                    item = data.get('item', {})
                    print(f"   {lang}: {item.get('name', 'N/A')}")
        else:
            print("   ❌ No items found for testing")
    else:
        print("   ❌ Could not get items for testing")

def test_recommendations():
    """Test recommendations with language support"""
    print("\n=== Testing Recommendations ===")
    
    for lang in ['en', 'az']:
        status_code, data = test_endpoint("/recommendations", params={'language': lang})
        success = print_test_result(f"Recommendations ({lang})", status_code, data)
        
        if success and data.get('success'):
            recs = data.get('recommendations', {})
            popular_count = len(recs.get('popular', []))
            print(f"   Found {popular_count} popular recommendations")

def test_category_filtering():
    """Test category filtering with language support"""
    print("\n=== Testing Category Filtering ===")
    
    # First get categories to test with
    status_code, data = test_endpoint("/categories")
    if status_code == 200 and data.get('success'):
        categories = data.get('categories', [])
        if categories:
            test_category_id = categories[0]['id']
            print(f"   Testing with category ID: {test_category_id}")
            
            for lang in ['en', 'az']:
                status_code, data = test_endpoint("/items", params={
                    'language': lang, 
                    'category': test_category_id
                })
                success = print_test_result(f"Category Filter ({lang})", status_code, data)
                
                if success and data.get('success'):
                    items = data.get('items', [])
                    print(f"   Found {len(items)} items in category")
        else:
            print("   ❌ No categories found for testing")
    else:
        print("   ❌ Could not get categories for testing")

def main():
    """Run all multilingual API tests"""
    print("🌍 Testing Multilingual Menu API")
    print("=" * 50)
    
    # Test basic connectivity
    status_code, data = test_endpoint("/categories")
    if status_code is None:
        print("❌ Server is not running. Please start the server first.")
        print("   Run: python src/api/main.py")
        return False
    
    print("✅ Server is running")
    
    # Run all tests
    test_multilingual_categories()
    test_multilingual_items()
    test_search_functionality()
    test_item_details()
    test_recommendations()
    test_category_filtering()
    
    print("\n" + "=" * 50)
    print("🎉 Multilingual API testing completed!")
    print("\nTo test manually, try these URLs:")
    print(f"• {API_BASE}/categories?language=az")
    print(f"• {API_BASE}/items?language=ru")
    print(f"• {API_BASE}/items?language=tr&search=burger")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

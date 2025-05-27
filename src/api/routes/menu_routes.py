"""
Menu routes for the Meinn Restaurant Menu AI Assistant.
Handles all API routes related to menu items and categories.
"""

import logging
from flask import Blueprint, request, jsonify
import json

# Set up logger
logger = logging.getLogger("meinn_ai.menu")

# Create a blueprint for menu routes
menu_bp = Blueprint('menu', __name__, url_prefix='/api/menu')

@menu_bp.route('/items', methods=['GET'])
def get_menu_items():
    """Get menu items with optional filtering"""
    try:
        # Get query parameters for filtering
        category = request.args.get('category')
        availability = request.args.get('available', 'true').lower() == 'true'
        search = request.args.get('search')
        language = request.args.get('language', 'en')  # Default to English
        
        # Import and use the menu manager to get items from the database
        from src.services.product.menu_manager import MenuManager
        menu_manager = MenuManager()
        
        try:
            # Get items from the database with language support
            if search:
                # Use search method for search queries
                menu_items_db = menu_manager.search_menu(search, language=language)
                # Filter by category if specified
                if category:
                    menu_items_db = [item for item in menu_items_db if item['category_id'] == category]
            else:
                # Use regular get_menu_items method
                menu_items_db = menu_manager.get_menu_items(
                    category_id=category, 
                    available_only=availability,
                    language=language
                )
            
            # Convert to the desired format for the API response
            sample_menu_items = []
            for item in menu_items_db:
                if 'category_name' in item:  # If using database format
                    sample_menu_items.append({
                        "id": item["id"],
                        "name": item["name"],
                        "description": item["description"],
                        "category": item["category_name"],
                        "category_id": item["category_id"],  # Include category_id for reference
                        "price": item["price"],
                        "image_url": item["image_url"],
                        "available": item["available"],
                        "popular": item["popular"],
                        "allergens": item["allergens"],
                        "nutrition": item["nutrition"]
                    })
                else:  # If using the sample data format
                    sample_menu_items.append({
                        "id": item["id"],
                        "name": item["name"],
                        "description": item["description"],
                        "category": item.get("category", item.get("category_id", "")),
                        "category_id": item.get("category_id", ""),
                        "price": item["price"],
                        "image_url": item.get("image_url", ""),
                        "available": item["available"],
                        "popular": item["popular"],
                        "allergens": item.get("allergens", []),
                        "nutrition": item.get("nutrition", {})
                    })
                    
        except Exception as e:
            # If there's an error, use hardcoded sample data as a fallback
            logger.error(f"Error retrieving data from database: {str(e)}. Using sample data instead.")
            sample_menu_items = [
                {
                    "id": "pizza-001",
                    "name": "Margherita Pizza",
                    "description": "Classic pizza with tomato sauce, mozzarella, and basil",
                    "category": "Pizza",
                    "category_id": "pizza",
                    "price": 12.99,
                    "image_url": "/static/images/margherita.jpg",
                    "available": True,
                    "popular": True,
                    "allergens": ["dairy", "gluten"],
                    "nutrition": {
                        "calories": 850,
                        "protein": 35,
                        "carbs": 100,
                        "fat": 25
                    }
                },
                {
                    "id": "pizza-002",
                    "name": "Pepperoni Pizza",
                    "description": "Tomato sauce, mozzarella, and pepperoni slices",
                    "category": "Pizza",
                    "category_id": "pizza",
                    "price": 14.99,
                    "image_url": "/static/images/pepperoni.jpg",
                    "available": True,
                    "popular": True,
                    "allergens": ["dairy", "gluten"],
                    "nutrition": {
                        "calories": 950,
                        "protein": 40,
                        "carbs": 98,
                        "fat": 30
                    }
                },
                {
                    "id": "pasta-001",
                    "name": "Spaghetti Carbonara",
                    "description": "Spaghetti with creamy egg sauce, pancetta, and parmesan",
                    "category": "Pasta",
                    "category_id": "pasta",
                    "price": 13.99,
                    "image_url": "/static/images/carbonara.jpg",
                    "available": True,
                    "popular": False,
                    "allergens": ["dairy", "gluten", "egg"],
                    "nutrition": {
                        "calories": 1050,
                        "protein": 35,
                        "carbs": 130,
                        "fat": 40
                    }
                }
            ]
        
        # Note: We've removed the category filtering here because the MenuManager.get_menu_items
        # already filters by category_id when that parameter is provided
            
        # Filter by search term if provided
        if search:
            search = search.lower()
            sample_menu_items = [item for item in sample_menu_items 
                               if search in item['name'].lower() or search in item['description'].lower()]
        
        return jsonify({
            "success": True,
            "items": sample_menu_items,
            "count": len(sample_menu_items)
        })
        
    except Exception as e:
        logger.error(f"Error retrieving menu items: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to retrieve menu items",
            "message": str(e)
        }), 500

@menu_bp.route('/categories', methods=['GET'])
def get_menu_categories():
    """Get all menu categories with language support"""
    try:
        # Get language parameter (default to English)
        language = request.args.get('language', 'en')
        
        # Use MenuManager to get categories with translations
        from src.services.product.menu_manager import MenuManager
        menu_manager = MenuManager()
        
        try:
            # Get categories from MenuManager
            categories_data = menu_manager.get_categories(language=language)
            
            # Convert to API response format
            categories = []
            for category in categories_data:
                categories.append({
                    "id": category["id"],
                    "name": category["name"],
                    "description": category.get("description", ""),
                    "image_url": category.get("image_url", "/static/images/categories/placeholder.jpg")
                })
                
        except Exception as e:
            logger.error(f"Error retrieving categories from MenuManager: {str(e)}")
            categories = []
            
        return jsonify({
            "success": True,
            "categories": categories
        })
        
    except Exception as e:
        logger.error(f"Error retrieving menu categories: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to retrieve menu categories",
            "message": str(e)
        }), 500

@menu_bp.route('/items/<item_id>', methods=['GET'])
def get_menu_item(item_id):
    """Get detailed information about a specific menu item"""
    try:
        # Get language parameter (default to English)
        language = request.args.get('language', 'en')
        
        # Use MenuManager to get item with translations
        from src.services.product.menu_manager import MenuManager
        menu_manager = MenuManager()
        
        item = menu_manager.get_item_by_id(item_id, language=language)
        
        if item:
            # Convert to API response format
            response_item = {
                "id": item["id"],
                "name": item["name"],
                "description": item["description"],
                "category": item["category_name"],
                "category_id": item["category_id"],
                "price": item["price"],
                "image_url": item["image_url"],
                "available": item["available"],
                "popular": item["popular"],
                "allergens": item["allergens"],
                "ingredients": item.get("ingredients", []),
                "nutrition": item["nutrition"],
                "preparation_time": item.get("preparation_time", 15),
                "suggested_pairings": item.get("suggested_pairings", [])
            }
            
            return jsonify({
                "success": True,
                "item": response_item
            })
        else:
            return jsonify({
                "success": False,
                "error": "Item not found"
            }), 404
        
    except Exception as e:
        logger.error(f"Error retrieving menu item {item_id}: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Failed to retrieve menu item {item_id}",
            "message": str(e)
        }), 500

@menu_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Get menu item recommendations based on various criteria"""
    try:
        # Get query parameters
        base_item_id = request.args.get('item_id')  # For pairing recommendations
        meal_time = request.args.get('meal_time')   # breakfast, lunch, dinner
        user_id = request.args.get('user_id')       # For personalized recommendations
        language = request.args.get('language', 'en')  # Default to English
        
        # Use MenuManager to get recommendations with language support
        from src.services.product.menu_manager import MenuManager
        menu_manager = MenuManager()
        
        try:
            recommendations = menu_manager.get_recommendations(
                base_item_id=base_item_id,
                user_id=user_id,
                meal_time=meal_time,
                language=language
            )
            
            return jsonify({
                "success": True,
                "recommendations": recommendations
            })
            
        except Exception as e:
            logger.error(f"Error getting recommendations from MenuManager: {str(e)}")
            
            # Fallback to placeholder recommendations if MenuManager fails
            recommendations = {
                "pairings": [],
                "popular": [],
                "time_based": [],
                "personalized": []
            }
            
            return jsonify({
                "success": True,
                "recommendations": recommendations
            })
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to generate recommendations",
            "message": str(e)
        }), 500

# Category management routes
@menu_bp.route('/admin/categories', methods=['POST'])
def add_category():
    """Add a new category (admin only)"""
    try:
        # TODO: Implement authentication check
        
        # Get category data from request body
        category_data = request.json
        
        # Validate required fields - check translations structure
        if 'id' not in category_data:
            return jsonify({
                "success": False,
                "error": "Missing required field: id"
            }), 400
            
        if 'translations' not in category_data or not category_data['translations']:
            return jsonify({
                "success": False,
                "error": "Missing required field: translations"
            }), 400
        
        # Validate that at least English translation exists
        if 'en' not in category_data['translations'] or not category_data['translations']['en'].get('name'):
            return jsonify({
                "success": False,
                "error": "English name is required"
            }), 400
                
        # Log received data for debugging
        logger.info(f"Add category request received: {category_data}")
        
        # Connect to the database
        import sqlite3
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        try:
            # Check if category ID already exists
            cursor.execute("SELECT id FROM categories WHERE id = ?", (category_data['id'],))
            if cursor.fetchone() is not None:
                return jsonify({
                    "success": False,
                    "error": f"Category ID already exists: {category_data['id']}"
                }), 400
            
            # Prepare translation data
            translations = category_data['translations']
            supported_languages = ['az', 'en', 'ru', 'tr', 'ar', 'hi', 'fr', 'it']
            
            # Use English as fallback for primary name and description
            primary_name = translations.get('en', {}).get('name', '')
            primary_description = translations.get('en', {}).get('description', '')
            
            # Build the INSERT query with all translation columns
            columns = ['id', 'name', 'description', 'image_url']
            values = [category_data['id'], primary_name, primary_description, 
                     category_data.get('image_url', '/static/images/categories/placeholder.jpg')]
            
            # Add translation columns
            for lang in supported_languages:
                columns.extend([f'name_{lang}', f'description_{lang}'])
                lang_data = translations.get(lang, {})
                values.extend([
                    lang_data.get('name', primary_name),
                    lang_data.get('description', primary_description)
                ])
            
            # Insert into categories table
            placeholders = ', '.join(['?' for _ in values])
            column_names = ', '.join(columns)
            cursor.execute(
                f"INSERT INTO categories ({column_names}) VALUES ({placeholders})",
                values
            )
            
            # Commit changes
            conn.commit()
            logger.info(f"Category added successfully: {category_data['id']}")
            
        except Exception as db_error:
            conn.rollback()
            logger.error(f"Database error: {str(db_error)}")
            return jsonify({
                "success": False,
                "error": "Database error",
                "message": str(db_error)
            }), 500
            
        finally:
            conn.close()
        
        return jsonify({
            "success": True,
            "message": "Category added successfully",
            "category_id": category_data['id']
        })
        
    except Exception as e:
        logger.error(f"Error adding category: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to add category",
            "message": str(e)
        }), 500

@menu_bp.route('/admin/categories/<category_id>', methods=['PUT'])
def update_category(category_id):
    """Update an existing category (admin only)"""
    try:
        # TODO: Implement authentication check
        
        # Get updated category data from request body
        category_data = request.json
        
        # Check if using translations structure
        if 'translations' in category_data:
            # Validate that at least English translation exists
            if 'en' not in category_data['translations'] or not category_data['translations']['en'].get('name'):
                return jsonify({
                    "success": False,
                    "error": "English name is required"
                }), 400
        else:
            # Legacy format validation
            if 'name' not in category_data:
                return jsonify({
                    "success": False,
                    "error": "Missing required field: name"
                }), 400
        
        # Connect to the database
        import sqlite3
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        try:
            # Check if category exists
            cursor.execute("SELECT id FROM categories WHERE id = ?", (category_id,))
            if cursor.fetchone() is None:
                return jsonify({
                    "success": False,
                    "error": f"Category with ID {category_id} not found"
                }), 404
            
            if 'translations' in category_data:
                # Handle translations structure
                translations = category_data['translations']
                supported_languages = ['az', 'en', 'ru', 'tr', 'ar', 'hi', 'fr', 'it']
                
                # Use English as fallback for primary name and description
                primary_name = translations.get('en', {}).get('name', '')
                primary_description = translations.get('en', {}).get('description', '')
                
                # Build the update query with all translation columns
                update_parts = ['name = ?', 'description = ?', 'image_url = ?']
                values = [primary_name, primary_description, 
                         category_data.get('image_url', '/static/images/categories/placeholder.jpg')]
                
                # Add translation columns
                for lang in supported_languages:
                    update_parts.extend([f'name_{lang} = ?', f'description_{lang} = ?'])
                    lang_data = translations.get(lang, {})
                    values.extend([
                        lang_data.get('name', primary_name),
                        lang_data.get('description', primary_description)
                    ])
                
                values.append(category_id)
                
                # Update categories table
                cursor.execute(
                    f"UPDATE categories SET {', '.join(update_parts)} WHERE id = ?",
                    values
                )
            else:
                # Legacy format update
                cursor.execute(
                    """UPDATE categories 
                       SET name = ?, description = ?, image_url = ?
                       WHERE id = ?""",
                    (
                        category_data['name'],
                        category_data.get('description', ''),
                        category_data.get('image_url', '/static/images/categories/placeholder.jpg'),
                        category_id
                    )
                )
            
            # Commit changes
            conn.commit()
            logger.info(f"Category updated successfully: {category_id}")
            
        except Exception as db_error:
            conn.rollback()
            logger.error(f"Database error: {str(db_error)}")
            return jsonify({
                "success": False,
                "error": "Database error",
                "message": str(db_error)
            }), 500
            
        finally:
            conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Category {category_id} updated successfully"
        })
        
    except Exception as e:
        logger.error(f"Error updating category {category_id}: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Failed to update category {category_id}",
            "message": str(e)
        }), 500

@menu_bp.route('/admin/categories/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete a category (admin only)"""
    try:
        # TODO: Implement authentication check
        
        # Connect to the database
        import sqlite3
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        try:
            # Check if category exists
            cursor.execute("SELECT id FROM categories WHERE id = ?", (category_id,))
            if cursor.fetchone() is None:
                return jsonify({
                    "success": False,
                    "error": f"Category with ID {category_id} not found"
                }), 404
            
            # Check if there are menu items in this category
            cursor.execute("SELECT COUNT(*) FROM menu_items WHERE category_id = ?", (category_id,))
            if cursor.fetchone()[0] > 0:
                return jsonify({
                    "success": False,
                    "error": f"Cannot delete category {category_id} because it contains menu items. Move or delete these items first."
                }), 400
            
            # Delete the category
            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            
            # Commit changes
            conn.commit()
            logger.info(f"Category deleted successfully: {category_id}")
            
        except Exception as db_error:
            conn.rollback()
            logger.error(f"Database error: {str(db_error)}")
            return jsonify({
                "success": False,
                "error": "Database error",
                "message": str(db_error)
            }), 500
            
        finally:
            conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Category {category_id} deleted successfully"
        })
        
    except Exception as e:
        logger.error(f"Error deleting category {category_id}: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Failed to delete category {category_id}",
            "message": str(e)
        }), 500

# Admin-only routes for menu management
@menu_bp.route('/admin/items', methods=['POST'])
def add_menu_item():
    """Add a new menu item (admin only)"""
    try:
        # TODO: Implement authentication check
        
        # Get item data from request body
        item_data = request.json
        
        # Check if using translations structure
        if 'translations' in item_data:
            # Validate translations structure
            if 'en' not in item_data['translations'] or not item_data['translations']['en'].get('name'):
                return jsonify({
                    "success": False,
                    "error": "English name is required"
                }), 400
            
            # Validate required fields for translations structure
            if 'category' not in item_data or 'price' not in item_data:
                return jsonify({
                    "success": False,
                    "error": "Missing required fields: category and price"
                }), 400
        else:
            # Legacy format validation
            required_fields = ['name', 'category', 'price']
            for field in required_fields:
                if field not in item_data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
                
        # Log received data for debugging
        logger.info(f"Add menu item request received: {item_data}")
        
        # Generate an item ID based on the category and timestamp
        import time
        item_id = f"{item_data['category']}-{int(time.time())}"
        
        # Prepare the item data based on format
        if 'translations' in item_data:
            # Use translations structure
            translations = item_data['translations']
            primary_name = translations.get('en', {}).get('name', '')
            primary_description = translations.get('en', {}).get('description', '')
        else:
            # Legacy format
            primary_name = item_data['name']
            primary_description = item_data.get('description', '')
        
        new_item = {
            "id": item_id,
            "name": primary_name,
            "description": primary_description,
            "category_id": item_data['category'],
            "price": item_data['price'],
            "image_url": item_data.get('image_url', '/static/images/placeholder.svg'),
            "available": item_data.get('available', True),
            "popular": item_data.get('popular', False),
            "preparation_time": item_data.get('preparation_time', 15),
            "allergens": item_data.get('allergens', []),
            "nutrition": item_data.get('nutrition', {
                "calories": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0
            }),
            "ingredients": item_data.get('ingredients', [])
        }
        
        # Connect to the database
        import sqlite3
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        try:
            if 'translations' in item_data:
                # Handle translations structure
                translations = item_data['translations']
                supported_languages = ['az', 'en', 'ru', 'tr', 'ar', 'hi', 'fr', 'it']
                
                # Build the INSERT query with all translation columns
                columns = ['id', 'name', 'description', 'category_id', 'price', 'image_url', 
                          'available', 'popular', 'preparation_time']
                values = [
                    new_item["id"], new_item["name"], new_item["description"],
                    new_item["category_id"], new_item["price"], new_item["image_url"],
                    1 if new_item["available"] else 0,
                    1 if new_item["popular"] else 0,
                    new_item["preparation_time"]
                ]
                
                # Add translation columns
                for lang in supported_languages:
                    columns.extend([f'name_{lang}', f'description_{lang}'])
                    lang_data = translations.get(lang, {})
                    values.extend([
                        lang_data.get('name', primary_name),
                        lang_data.get('description', primary_description)
                    ])
                
                # Insert into menu_items table
                placeholders = ', '.join(['?' for _ in values])
                column_names = ', '.join(columns)
                cursor.execute(
                    f"INSERT INTO menu_items ({column_names}) VALUES ({placeholders})",
                    values
                )
            else:
                # Legacy format insert
                cursor.execute(
                    """INSERT INTO menu_items 
                       (id, name, description, category_id, price, image_url, available, popular, preparation_time)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        new_item["id"], new_item["name"], new_item["description"],
                        new_item["category_id"], new_item["price"], new_item["image_url"],
                        1 if new_item["available"] else 0,
                        1 if new_item["popular"] else 0,
                        new_item["preparation_time"]
                    )
                )
            
            # Insert into item_details table
            import json
            cursor.execute(
                "INSERT INTO item_details (item_id, allergens, ingredients, nutrition) VALUES (?, ?, ?, ?)",
                (
                    new_item["id"],
                    json.dumps(new_item["allergens"]),
                    json.dumps(new_item["ingredients"]),
                    json.dumps(new_item["nutrition"])
                )
            )
            
            # Commit changes
            conn.commit()
            logger.info(f"Menu item added successfully: {item_id}")
            
        except Exception as db_error:
            conn.rollback()
            logger.error(f"Database error: {str(db_error)}")
            return jsonify({
                "success": False,
                "error": "Database error",
                "message": str(db_error)
            }), 500
            
        finally:
            conn.close()
        
        return jsonify({
            "success": True,
            "message": "Menu item added successfully",
            "item_id": item_id
        })
        
    except Exception as e:
        logger.error(f"Error adding menu item: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to add menu item",
            "message": str(e)
        }), 500

@menu_bp.route('/admin/items/<item_id>', methods=['PUT'])
def update_menu_item(item_id):
    """Update an existing menu item (admin only)"""
    try:
        # TODO: Implement authentication check
        
        # Log request info for debugging
        logger.info(f"Update request received for item ID: {item_id}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request headers: {request.headers}")
        logger.info(f"Request data: {request.data}")
        
        # Get updated item data from request body
        item_data = request.json
        logger.info(f"Parsed JSON data: {item_data}")
        
        # Check if using translations structure
        if 'translations' in item_data:
            # Validate translations structure
            if 'en' not in item_data['translations'] or not item_data['translations']['en'].get('name'):
                return jsonify({
                    "success": False,
                    "error": "English name is required"
                }), 400
            
            # Validate required fields for translations structure
            if 'category' not in item_data or 'price' not in item_data:
                return jsonify({
                    "success": False,
                    "error": "Missing required fields: category and price"
                }), 400
        else:
            # Legacy format validation
            required_fields = ['name', 'category', 'price']
            for field in required_fields:
                if field not in item_data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
        
        # Connect to the database
        import sqlite3
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        try:
            # Check if item exists
            cursor.execute("SELECT id FROM menu_items WHERE id = ?", (item_id,))
            if cursor.fetchone() is None:
                return jsonify({
                    "success": False,
                    "error": f"Menu item with ID {item_id} not found"
                }), 404
            
            # Prepare data based on format
            if 'translations' in item_data:
                # Use translations structure
                translations = item_data['translations']
                primary_name = translations.get('en', {}).get('name', '')
                primary_description = translations.get('en', {}).get('description', '')
                supported_languages = ['az', 'en', 'ru', 'tr', 'ar', 'hi', 'fr', 'it']
                
                # Build the update query with all translation columns
                update_parts = ['name = ?', 'description = ?', 'category_id = ?', 'price = ?', 
                               'image_url = ?', 'available = ?', 'popular = ?']
                values = [
                    primary_name, primary_description, item_data['category'], item_data['price'],
                    item_data.get('image_url', '/static/images/placeholder.svg'),
                    1 if item_data.get('available', True) else 0,
                    1 if item_data.get('popular', False) else 0
                ]
                
                # Add translation columns
                for lang in supported_languages:
                    update_parts.extend([f'name_{lang} = ?', f'description_{lang} = ?'])
                    lang_data = translations.get(lang, {})
                    values.extend([
                        lang_data.get('name', primary_name),
                        lang_data.get('description', primary_description)
                    ])
                
                values.append(item_id)
                
                # Update menu_items table
                cursor.execute(
                    f"UPDATE menu_items SET {', '.join(update_parts)} WHERE id = ?",
                    values
                )
            else:
                # Legacy format update
                cursor.execute(
                    """UPDATE menu_items 
                       SET name = ?, description = ?, category_id = ?, price = ?, 
                           image_url = ?, available = ?, popular = ?
                       WHERE id = ?""",
                    (
                        item_data['name'],
                        item_data.get('description', ''),
                        item_data['category'],
                        item_data['price'],
                        item_data.get('image_url', '/static/images/placeholder.svg'),
                        1 if item_data.get('available', True) else 0,
                        1 if item_data.get('popular', False) else 0,
                        item_id
                    )
                )
            
            # Update item_details table
            import json
            allergens = item_data.get('allergens', [])
            ingredients = item_data.get('ingredients', [])
            nutrition = item_data.get('nutrition', {"calories": 0, "protein": 0, "carbs": 0, "fat": 0})
            
            cursor.execute(
                """UPDATE item_details 
                   SET allergens = ?, ingredients = ?, nutrition = ?
                   WHERE item_id = ?""",
                (
                    json.dumps(allergens),
                    json.dumps(ingredients),
                    json.dumps(nutrition),
                    item_id
                )
            )
            
            # Commit changes
            conn.commit()
            logger.info(f"Menu item updated successfully: {item_id}")
            
        except Exception as db_error:
            conn.rollback()
            logger.error(f"Database error: {str(db_error)}")
            return jsonify({
                "success": False,
                "error": "Database error",
                "message": str(db_error)
            }), 500
            
        finally:
            conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Menu item {item_id} updated successfully"
        })
        
    except Exception as e:
        logger.error(f"Error updating menu item {item_id}: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Failed to update menu item {item_id}",
            "message": str(e)
        }), 500

@menu_bp.route('/admin/items/<item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    """Delete a menu item (admin only)"""
    try:
        # TODO: Implement authentication check
        
        # Connect to the database
        import sqlite3
        conn = sqlite3.connect('menu_data.db')
        cursor = conn.cursor()
        
        try:
            # Check if item exists
            cursor.execute("SELECT id FROM menu_items WHERE id = ?", (item_id,))
            if cursor.fetchone() is None:
                return jsonify({
                    "success": False,
                    "error": f"Menu item with ID {item_id} not found"
                }), 404
            
            # Delete from item_details table first (foreign key constraint)
            cursor.execute("DELETE FROM item_details WHERE item_id = ?", (item_id,))
            
            # Then delete from menu_items table
            cursor.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
            
            # Also delete any pairings
            cursor.execute("DELETE FROM item_pairings WHERE item_id = ? OR paired_with_id = ?", (item_id, item_id))
            
            # Commit changes
            conn.commit()
            logger.info(f"Menu item deleted successfully: {item_id}")
            
        except Exception as db_error:
            conn.rollback()
            logger.error(f"Database error: {str(db_error)}")
            return jsonify({
                "success": False,
                "error": "Database error",
                "message": str(db_error)
            }), 500
            
        finally:
            conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Menu item {item_id} deleted successfully"
        })
        
    except Exception as e:
        logger.error(f"Error deleting menu item {item_id}: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Failed to delete menu item {item_id}",
            "message": str(e)
        }), 500

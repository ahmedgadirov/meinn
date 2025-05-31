"""
Menu Manager for the Meinn Restaurant Menu AI Assistant.
Handles menu items, categories, and recommendations with multilingual support.
"""

import logging
import json
import sqlite3
import os
from datetime import datetime, time
import random

# Set up logger
logger = logging.getLogger("meinn_ai.menu_manager")

class MenuManager:
    """
    Manages restaurant menu items, categories, and recommendations.
    Provides methods for retrieving, filtering, and recommending menu items with multilingual support.
    """
    
    def __init__(self):
        """Initialize the menu manager"""
        # Get the absolute path to the database file in the project root
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(current_dir, '..', '..', '..')
        self.db_path = os.path.join(project_root, "menu_data.db")
        logger.info("Menu Manager initialized with multilingual support")
        logger.info(f"Database path: {self.db_path}")
        
        # Check if multilingual columns exist
        self._multilingual_support = self._check_multilingual_support()
    
    def _check_multilingual_support(self):
        """Check if the database has multilingual columns"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if multilingual columns exist in categories table
            cursor.execute("PRAGMA table_info(categories)")
            columns = [column[1] for column in cursor.fetchall()]
            
            conn.close()
            
            has_multilingual = 'name_en' in columns
            logger.info(f"Multilingual support detected: {has_multilingual}")
            return has_multilingual
            
        except Exception as e:
            logger.error(f"Error checking multilingual support: {str(e)}")
            return False
    
    def _build_multilingual_category_columns(self):
        """Build category column selection based on multilingual support"""
        if self._multilingual_support:
            return "c.name_en as cat_name_en, c.name_az as cat_name_az, c.name_ru as cat_name_ru, c.name_tr as cat_name_tr, c.name_ar as cat_name_ar, c.name_hi as cat_name_hi, c.name_fr as cat_name_fr, c.name_it as cat_name_it"
        else:
            return "NULL as cat_name_en, NULL as cat_name_az, NULL as cat_name_ru, NULL as cat_name_tr, NULL as cat_name_ar, NULL as cat_name_hi, NULL as cat_name_fr, NULL as cat_name_it"
    
    def _get_translation_columns(self, language='en'):
        """
        Get the appropriate column names for the specified language
        
        Args:
            language (str): Language code (az, en, ru, tr, ar, hi, fr, it)
            
        Returns:
            tuple: (name_column, description_column)
        """
        if language == 'en':
            return ('name_en', 'description_en')
        elif language == 'az':
            return ('name_az', 'description_az')
        elif language == 'ru':
            return ('name_ru', 'description_ru')
        elif language == 'tr':
            return ('name_tr', 'description_tr')
        elif language == 'ar':
            return ('name_ar', 'description_ar')
        elif language == 'hi':
            return ('name_hi', 'description_hi')
        elif language == 'fr':
            return ('name_fr', 'description_fr')
        elif language == 'it':
            return ('name_it', 'description_it')
        else:
            # Default to English
            return ('name_en', 'description_en')
    
    def _apply_translation(self, item, language='en', category_data=None):
        """
        Apply language-specific translation to an item using direct columns
        
        Args:
            item (dict): The item dictionary containing all language columns
            language (str): Language code to use
            category_data (dict, optional): Category data for translating category names
            
        Returns:
            dict: Item with translated name and description
        """
        name_col, desc_col = self._get_translation_columns(language)
        
        # Use translated name if available, otherwise fall back to default
        if name_col in item and item[name_col]:
            item['name'] = item[name_col]
        
        # Use translated description if available, otherwise fall back to default
        if desc_col in item and item[desc_col]:
            item['description'] = item[desc_col]
        
        # Apply category translation if category data is provided
        if category_data and 'category_name' in item:
            if name_col in category_data and category_data[name_col]:
                item['category_name'] = category_data[name_col]
                
        return item
            
    def get_menu_items(self, category_id=None, available_only=True, language='en'):
        """
        Get menu items with optional filtering and language support
        
        Args:
            category_id (str, optional): Filter by category ID
            available_only (bool): Only return available items
            language (str): Language code (az, en, ru, tr, ar, hi, fr, it)
            
        Returns:
            list: List of menu items matching the criteria with translations
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            multilingual_cols = self._build_multilingual_category_columns()
            query = f"""
                SELECT m.*, c.name as category_name,
                       {multilingual_cols},
                       d.allergens, d.ingredients, d.nutrition
                FROM menu_items m
                JOIN categories c ON m.category_id = c.id
                JOIN item_details d ON m.id = d.item_id
            """
            
            params = []
            where_clauses = []
            
            if category_id:
                where_clauses.append("m.category_id = ?")
                params.append(category_id)
                
            if available_only:
                where_clauses.append("m.available = 1")
                
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
                
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                item = dict(row)
                item["allergens"] = json.loads(item["allergens"]) if item["allergens"] else []
                item["ingredients"] = json.loads(item["ingredients"]) if item["ingredients"] else []
                item["nutrition"] = json.loads(item["nutrition"]) if item["nutrition"] else {}
                item["available"] = bool(item["available"])
                item["popular"] = bool(item["popular"])
                
                # Extract category data for translation
                category_data = {
                    'name_en': item.get('cat_name_en'),
                    'name_az': item.get('cat_name_az'),
                    'name_ru': item.get('cat_name_ru'),
                    'name_tr': item.get('cat_name_tr'),
                    'name_ar': item.get('cat_name_ar'),
                    'name_hi': item.get('cat_name_hi'),
                    'name_fr': item.get('cat_name_fr'),
                    'name_it': item.get('cat_name_it'),
                }
                
                # Apply translations
                item = self._apply_translation(item, language, category_data)
                
                # Clean up category translation columns
                for key in list(item.keys()):
                    if key.startswith('cat_name_'):
                        del item[key]
                
                result.append(item)
                
            conn.close()
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving menu items: {str(e)}", exc_info=True)
            return []
    
    def get_item_by_id(self, item_id, language='en'):
        """
        Get a specific menu item by ID with language support
        
        Args:
            item_id (str): The ID of the menu item
            language (str): Language code (az, en, ru, tr, ar, hi, fr, it)
            
        Returns:
            dict: The menu item or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            multilingual_cols = self._build_multilingual_category_columns()
            query = f"""
                SELECT m.*, c.name as category_name,
                       {multilingual_cols},
                       d.allergens, d.ingredients, d.nutrition
                FROM menu_items m
                JOIN categories c ON m.category_id = c.id
                JOIN item_details d ON m.id = d.item_id
                WHERE m.id = ?
            """
            
            cursor.execute(query, (item_id,))
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                return None
                
            item = dict(row)
            item["allergens"] = json.loads(item["allergens"]) if item["allergens"] else []
            item["ingredients"] = json.loads(item["ingredients"]) if item["ingredients"] else []
            item["nutrition"] = json.loads(item["nutrition"]) if item["nutrition"] else {}
            item["available"] = bool(item["available"])
            item["popular"] = bool(item["popular"])
            
            # Extract category data for translation
            category_data = {
                'name_en': item.get('cat_name_en'),
                'name_az': item.get('cat_name_az'),
                'name_ru': item.get('cat_name_ru'),
                'name_tr': item.get('cat_name_tr'),
                'name_ar': item.get('cat_name_ar'),
                'name_hi': item.get('cat_name_hi'),
                'name_fr': item.get('cat_name_fr'),
                'name_it': item.get('cat_name_it'),
            }
            
            # Apply translations
            item = self._apply_translation(item, language, category_data)
            
            # Clean up category translation columns
            for key in list(item.keys()):
                if key.startswith('cat_name_'):
                    del item[key]
            
            # Get pairings (simplified - no translations for pairings for now)
            cursor.execute("""
                SELECT m.id, m.name, m.price, m.image_url, m.category_id, c.name as category_name, p.score
                FROM item_pairings p
                JOIN menu_items m ON p.paired_with_id = m.id
                JOIN categories c ON m.category_id = c.id
                WHERE p.item_id = ? AND m.available = 1
                ORDER BY p.score DESC
                LIMIT 5
            """, (item_id,))
            
            pairing_rows = cursor.fetchall()
            item["suggested_pairings"] = [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "price": row["price"],
                    "image_url": row["image_url"],
                    "category": row["category_name"],
                    "score": row["score"]
                }
                for row in pairing_rows
            ]
            
            conn.close()
            return item
            
        except Exception as e:
            logger.error(f"Error retrieving menu item {item_id}: {str(e)}", exc_info=True)
            return None
            
    def get_categories(self, language='en'):
        """
        Get all menu categories with language support
        
        Args:
            language (str): Language code (az, en, ru, tr, ar, hi, fr, it)
        
        Returns:
            list: List of menu categories with translated names and descriptions
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM categories ORDER BY id")
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                category = dict(row)
                
                # Apply translation
                category = self._apply_translation(category, language)
                
                result.append(category)
                
            conn.close()
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving categories: {str(e)}", exc_info=True)
            return []
            
    def get_recommendations(self, base_item_id=None, user_id=None, meal_time=None, language='en'):
        """
        Get menu recommendations based on various criteria
        
        Args:
            base_item_id (str, optional): Item to base pairing recommendations on
            user_id (str, optional): User ID for personalized recommendations
            meal_time (str, optional): Time of day for contextual recommendations
            language (str): Language code for translations
            
        Returns:
            dict: Dictionary with different recommendation categories
        """
        recommendations = {
            "pairings": [],
            "popular": [],
            "time_based": [],
            "personalized": []
        }
        
        try:
            # Get popular items
            popular_items = self.get_menu_items(available_only=True, language=language)
            popular_items = [item for item in popular_items if item["popular"]]
            popular_items = sorted(popular_items, key=lambda x: random.random())[:3]
            
            recommendations["popular"] = [
                {
                    "id": item["id"],
                    "name": item["name"],
                    "price": item["price"],
                    "image_url": item["image_url"],
                    "category": item["category_name"]
                }
                for item in popular_items
            ]
            
            # Time-based recommendations
            if meal_time:
                time_items = self.get_menu_items(available_only=True, language=language)
                time_items = sorted(time_items, key=lambda x: random.random())[:2]
                
                recommendations["time_based"] = [
                    {
                        "id": item["id"],
                        "name": item["name"],
                        "price": item["price"],
                        "image_url": item["image_url"],
                        "category": item["category_name"]
                    }
                    for item in time_items
                ]
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}", exc_info=True)
            return recommendations
            
    def search_menu(self, query, language='en'):
        """
        Search menu items by name or description with language support
        
        Args:
            query (str): Search term
            language (str): Language code for translations
            
        Returns:
            list: Matching menu items
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get name and description columns for the language
            name_col, desc_col = self._get_translation_columns(language)
            
            # Search in both default and translated columns
            search_term = f"%{query}%"
            
            multilingual_cols = self._build_multilingual_category_columns()
            
            # Build search conditions based on multilingual support
            if self._multilingual_support:
                search_conditions = f"m.name LIKE ? OR m.description LIKE ? OR m.{name_col} LIKE ? OR m.{desc_col} LIKE ? OR c.name LIKE ?"
                search_params = (search_term, search_term, search_term, search_term, search_term)
            else:
                search_conditions = "m.name LIKE ? OR m.description LIKE ? OR c.name LIKE ?"
                search_params = (search_term, search_term, search_term)
            
            query_sql = f"""
                SELECT m.*, c.name as category_name,
                       {multilingual_cols},
                       d.allergens, d.ingredients, d.nutrition
                FROM menu_items m
                JOIN categories c ON m.category_id = c.id
                JOIN item_details d ON m.id = d.item_id
                WHERE m.available = 1 AND ({search_conditions})
                ORDER BY m.popular DESC, m.name ASC
            """
            
            cursor.execute(query_sql, search_params)
            rows = cursor.fetchall()
            result = []
            
            for row in rows:
                item = dict(row)
                item["allergens"] = json.loads(item["allergens"]) if item["allergens"] else []
                item["ingredients"] = json.loads(item["ingredients"]) if item["ingredients"] else []
                item["nutrition"] = json.loads(item["nutrition"]) if item["nutrition"] else {}
                item["available"] = bool(item["available"])
                item["popular"] = bool(item["popular"])
                
                # Extract category data for translation
                category_data = {
                    'name_en': item.get('cat_name_en'),
                    'name_az': item.get('cat_name_az'),
                    'name_ru': item.get('cat_name_ru'),
                    'name_tr': item.get('cat_name_tr'),
                    'name_ar': item.get('cat_name_ar'),
                    'name_hi': item.get('cat_name_hi'),
                    'name_fr': item.get('cat_name_fr'),
                    'name_it': item.get('cat_name_it'),
                }
                
                # Apply translations
                item = self._apply_translation(item, language, category_data)
                
                # Clean up category translation columns
                for key in list(item.keys()):
                    if key.startswith('cat_name_'):
                        del item[key]
                
                result.append(item)
                
            conn.close()
            return result
            
        except Exception as e:
            logger.error(f"Error searching menu: {str(e)}", exc_info=True)
            return []

    def get_menu_summary(self, language='en'):
        """
        Get a summary of the menu for AI assistant context
        
        Args:
            language (str): Language code for translations
            
        Returns:
            dict: Menu summary with categories and sample items
        """
        try:
            categories = self.get_categories(language)
            
            summary = {
                "total_categories": len(categories),
                "categories": {},
                "total_items": 0,
                "popular_items": []
            }
            
            for category in categories:
                items = self.get_menu_items(category_id=category['id'], available_only=True, language=language)
                summary["categories"][category['name']] = {
                    "id": category['id'],
                    "description": category['description'],
                    "item_count": len(items),
                    "sample_items": [
                        {
                            "name": item['name'],
                            "price": item['price'],
                            "description": item['description'][:50] + "..." if len(item['description']) > 50 else item['description']
                        }
                        for item in items[:3]  # Just first 3 items
                    ]
                }
                summary["total_items"] += len(items)
            
            # Get popular items across all categories
            popular_items = self.get_menu_items(available_only=True, language=language)
            popular_items = [item for item in popular_items if item["popular"]][:5]
            
            summary["popular_items"] = [
                {
                    "name": item['name'],
                    "category": item['category_name'],
                    "price": item['price'],
                    "description": item['description'][:50] + "..." if len(item['description']) > 50 else item['description']
                }
                for item in popular_items
            ]
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting menu summary: {str(e)}", exc_info=True)
            return {"error": "Unable to generate menu summary"}

"""
Menu manager module for Meinn Restaurant AI Assistant.
This module handles menu items and categories management.
Firebase implementation for serverless deployment.
"""

import logging
import json
import os
from firebase_admin import firestore
from firebase_config import get_firestore_client

logger = logging.getLogger("meinn_ai.menu_manager")

class MenuManager:
    """Manages menu items and categories using Firestore"""
    
    def __init__(self):
        """Initialize the menu manager with Firestore database"""
        self.db = None
        self.menu_collection = "menu_items"
        self.category_collection = "menu_categories"
        
    def _init_database(self):
        """Initialize Firestore database connection"""
        try:
            self.db = get_firestore_client()
            logger.info("Menu manager Firestore initialized")
        except Exception as e:
            logger.error(f"Error initializing Firestore: {str(e)}")
            raise
    
    def add_menu_item(self, item_data):
        """
        Add a new menu item to Firestore
        
        Args:
            item_data (dict): Menu item data
            
        Returns:
            str: ID of the new menu item
        """
        if not self.db:
            self._init_database()
            
        try:
            # Add timestamp
            item_data['created_at'] = firestore.SERVER_TIMESTAMP
            item_data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            # Add to Firestore
            item_ref = self.db.collection(self.menu_collection).document()
            item_ref.set(item_data)
            
            logger.info(f"Added menu item {item_data.get('name')} with ID {item_ref.id}")
            return item_ref.id
        except Exception as e:
            logger.error(f"Error adding menu item: {str(e)}")
            return None
    
    def update_menu_item(self, item_id, item_data):
        """
        Update an existing menu item in Firestore
        
        Args:
            item_id (str): ID of the menu item to update
            item_data (dict): Updated menu item data
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.db:
            self._init_database()
            
        try:
            # Update timestamp
            item_data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            # Update in Firestore
            item_ref = self.db.collection(self.menu_collection).document(item_id)
            item_ref.update(item_data)
            
            logger.info(f"Updated menu item {item_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating menu item {item_id}: {str(e)}")
            return False
    
    def delete_menu_item(self, item_id):
        """
        Delete a menu item from Firestore
        
        Args:
            item_id (str): ID of the menu item to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.db:
            self._init_database()
            
        try:
            # Delete from Firestore
            self.db.collection(self.menu_collection).document(item_id).delete()
            
            logger.info(f"Deleted menu item {item_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting menu item {item_id}: {str(e)}")
            return False
    
    def get_menu_item(self, item_id):
        """
        Get a specific menu item from Firestore
        
        Args:
            item_id (str): ID of the menu item to retrieve
            
        Returns:
            dict: Menu item data or None if not found
        """
        if not self.db:
            self._init_database()
            
        try:
            # Get from Firestore
            item_ref = self.db.collection(self.menu_collection).document(item_id)
            item = item_ref.get()
            
            if item.exists:
                data = item.to_dict()
                data['id'] = item.id
                logger.info(f"Retrieved menu item {item_id}")
                return data
            else:
                logger.warning(f"Menu item {item_id} not found")
                return None
        except Exception as e:
            logger.error(f"Error retrieving menu item {item_id}: {str(e)}")
            return None
    
    def get_all_menu_items(self, category=None):
        """
        Get all menu items, optionally filtered by category
        
        Args:
            category (str, optional): Category to filter by
            
        Returns:
            list: List of menu item dictionaries
        """
        if not self.db:
            self._init_database()
            
        try:
            # Query Firestore
            if category:
                items = (
                    self.db.collection(self.menu_collection)
                    .where("category", "==", category)
                    .order_by("name")
                    .stream()
                )
            else:
                items = self.db.collection(self.menu_collection).order_by("name").stream()
            
            # Convert to list of dictionaries
            result = []
            for item in items:
                data = item.to_dict()
                data['id'] = item.id
                result.append(data)
            
            logger.info(f"Retrieved {len(result)} menu items" + (f" in category {category}" if category else ""))
            return result
        except Exception as e:
            logger.error(f"Error retrieving menu items: {str(e)}")
            return []
    
    def add_category(self, category_data):
        """
        Add a new menu category to Firestore
        
        Args:
            category_data (dict): Category data
            
        Returns:
            str: ID of the new category
        """
        if not self.db:
            self._init_database()
            
        try:
            # Add timestamp
            category_data['created_at'] = firestore.SERVER_TIMESTAMP
            
            # Add to Firestore
            category_ref = self.db.collection(self.category_collection).document()
            category_ref.set(category_data)
            
            logger.info(f"Added category {category_data.get('name')} with ID {category_ref.id}")
            return category_ref.id
        except Exception as e:
            logger.error(f"Error adding category: {str(e)}")
            return None
    
    def get_all_categories(self):
        """
        Get all menu categories
        
        Returns:
            list: List of category dictionaries
        """
        if not self.db:
            self._init_database()
            
        try:
            # Query Firestore
            categories = self.db.collection(self.category_collection).order_by("name").stream()
            
            # Convert to list of dictionaries
            result = []
            for category in categories:
                data = category.to_dict()
                data['id'] = category.id
                result.append(data)
            
            logger.info(f"Retrieved {len(result)} categories")
            return result
        except Exception as e:
            logger.error(f"Error retrieving categories: {str(e)}")
            return []
    
    def search_menu_items(self, query):
        """
        Search menu items by name or description
        
        Args:
            query (str): Search query
            
        Returns:
            list: List of matching menu item dictionaries
        """
        if not self.db:
            self._init_database()
            
        try:
            # Get all items (Firestore doesn't support text search directly)
            items = self.db.collection(self.menu_collection).stream()
            
            # Filter locally
            query = query.lower()
            result = []
            
            for item in items:
                data = item.to_dict()
                name = data.get('name', '').lower()
                description = data.get('description', '').lower()
                
                if query in name or query in description:
                    data['id'] = item.id
                    result.append(data)
            
            logger.info(f"Found {len(result)} menu items matching '{query}'")
            return result
        except Exception as e:
            logger.error(f"Error searching menu items: {str(e)}")
            return []
    
    def import_menu_from_json(self, json_file):
        """
        Import menu items from a JSON file
        
        Args:
            json_file (str): Path to JSON file
            
        Returns:
            int: Number of items imported
        """
        if not self.db:
            self._init_database()
            
        try:
            # Check if file exists
            if not os.path.exists(json_file):
                logger.error(f"Import file {json_file} not found")
                return 0
            
            # Read JSON file
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Batch import
            batch = self.db.batch()
            count = 0
            
            for item in data:
                # Add timestamp
                item['created_at'] = firestore.SERVER_TIMESTAMP
                item['updated_at'] = firestore.SERVER_TIMESTAMP
                
                # Add to batch
                item_ref = self.db.collection(self.menu_collection).document()
                batch.set(item_ref, item)
                count += 1
            
            # Commit batch
            batch.commit()
            
            logger.info(f"Imported {count} menu items from {json_file}")
            return count
        except Exception as e:
            logger.error(f"Error importing menu: {str(e)}")
            return 0

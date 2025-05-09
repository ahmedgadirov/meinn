"""
Menu routes for the Meinn Restaurant AI Assistant.
This module handles API endpoints for menu functionality.
"""

import logging
from flask import Blueprint, request, jsonify
from src.services.product.menu_manager import MenuManager
from src.services.translation.translation_agent import TranslationAgent

# Configure logging
logger = logging.getLogger("meinn_ai.routes.menu")

# Create blueprint
menu_bp = Blueprint('menu', __name__, url_prefix='/api/menu')

# Initialize services
menu_manager = MenuManager()
translator = TranslationAgent()

@menu_bp.route('/items', methods=['GET'])
def get_menu_items():
    """Get all menu items, optionally filtered by category"""
    try:
        category = request.args.get('category')
        items = menu_manager.get_all_menu_items(category)
        
        # Check if translation is requested
        lang = request.args.get('lang')
        if lang and lang != 'en':
            # Translate each item
            translated_items = []
            for item in items:
                translated_item = translator.translate_menu_item(item, lang)
                translated_items.append(translated_item)
            items = translated_items
        
        return jsonify({
            'status': 'success',
            'count': len(items),
            'items': items
        })
    except Exception as e:
        logger.error(f"Error in get_menu_items: {str(e)}")
        return jsonify({'error': str(e)}), 500

@menu_bp.route('/item/<item_id>', methods=['GET'])
def get_menu_item(item_id):
    """Get a specific menu item"""
    try:
        item = menu_manager.get_menu_item(item_id)
        
        if not item:
            return jsonify({'error': 'Menu item not found'}), 404
            
        # Check if translation is requested
        lang = request.args.get('lang')
        if lang and lang != 'en':
            item = translator.translate_menu_item(item, lang)
        
        return jsonify({
            'status': 'success',
            'item': item
        })
    except Exception as e:
        logger.error(f"Error in get_menu_item: {str(e)}")
        return jsonify({'error': str(e)}), 500

@menu_bp.route('/search', methods=['GET'])
def search_menu():
    """Search menu items"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
            
        items = menu_manager.search_menu_items(query)
        
        # Check if translation is requested
        lang = request.args.get('lang')
        if lang and lang != 'en':
            # Translate each item
            translated_items = []
            for item in items:
                translated_item = translator.translate_menu_item(item, lang)
                translated_items.append(translated_item)
            items = translated_items
        
        return jsonify({
            'status': 'success',
            'count': len(items),
            'items': items
        })
    except Exception as e:
        logger.error(f"Error in search_menu: {str(e)}")
        return jsonify({'error': str(e)}), 500

@menu_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all menu categories"""
    try:
        categories = menu_manager.get_all_categories()
        
        # Check if translation is requested
        lang = request.args.get('lang')
        if lang and lang != 'en':
            # Translate each category name
            for category in categories:
                if 'name' in category:
                    category['name'] = translator.translate_text(category['name'], lang)
        
        return jsonify({
            'status': 'success',
            'count': len(categories),
            'categories': categories
        })
    except Exception as e:
        logger.error(f"Error in get_categories: {str(e)}")
        return jsonify({'error': str(e)}), 500

@menu_bp.route('/item', methods=['POST'])
def add_menu_item():
    """Add a new menu item"""
    try:
        # Check authentication
        token = request.headers.get('X-API-Token')
        if not token or token != 'your_admin_token_here':  # This should be properly secured in production
            return jsonify({'error': 'Unauthorized'}), 401
            
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Validate required fields
        if not data.get('name') or not data.get('price'):
            return jsonify({'error': 'Name and price are required'}), 400
            
        item_id = menu_manager.add_menu_item(data)
        
        if item_id:
            return jsonify({
                'status': 'success',
                'item_id': item_id
            })
        else:
            return jsonify({'error': 'Failed to add menu item'}), 500
    except Exception as e:
        logger.error(f"Error in add_menu_item: {str(e)}")
        return jsonify({'error': str(e)}), 500

@menu_bp.route('/item/<item_id>', methods=['PUT'])
def update_menu_item(item_id):
    """Update an existing menu item"""
    try:
        # Check authentication
        token = request.headers.get('X-API-Token')
        if not token or token != 'your_admin_token_here':  # This should be properly secured in production
            return jsonify({'error': 'Unauthorized'}), 401
            
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        success = menu_manager.update_menu_item(item_id, data)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Menu item {item_id} updated'
            })
        else:
            return jsonify({'error': 'Failed to update menu item'}), 500
    except Exception as e:
        logger.error(f"Error in update_menu_item: {str(e)}")
        return jsonify({'error': str(e)}), 500

@menu_bp.route('/item/<item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    """Delete a menu item"""
    try:
        # Check authentication
        token = request.headers.get('X-API-Token')
        if not token or token != 'your_admin_token_here':  # This should be properly secured in production
            return jsonify({'error': 'Unauthorized'}), 401
            
        success = menu_manager.delete_menu_item(item_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Menu item {item_id} deleted'
            })
        else:
            return jsonify({'error': 'Failed to delete menu item'}), 500
    except Exception as e:
        logger.error(f"Error in delete_menu_item: {str(e)}")
        return jsonify({'error': str(e)}), 500

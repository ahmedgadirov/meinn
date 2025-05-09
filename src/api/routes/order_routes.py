"""
Order routes for the Meinn Restaurant AI Assistant.
This module handles API endpoints for order functionality.
"""

import logging
from flask import Blueprint, request, jsonify
from firebase_admin import firestore
from firebase_config import get_firestore_client

# Configure logging
logger = logging.getLogger("meinn_ai.routes.order")

# Create blueprint
order_bp = Blueprint('order', __name__, url_prefix='/api/order')

# Initialize Firestore
db = None

def get_db():
    global db
    if not db:
        db = get_firestore_client()
    return db

@order_bp.route('/', methods=['POST'])
def create_order():
    """Create a new order"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Validate required fields
        if not data.get('items') or not data.get('customer'):
            return jsonify({'error': 'Items and customer information are required'}), 400
            
        # Add timestamp and status
        data['created_at'] = firestore.SERVER_TIMESTAMP
        data['updated_at'] = firestore.SERVER_TIMESTAMP
        data['status'] = data.get('status', 'pending')
        
        # Add to Firestore
        db = get_db()
        order_ref = db.collection('orders').document()
        order_ref.set(data)
        
        # Return the new order ID
        return jsonify({
            'status': 'success',
            'order_id': order_ref.id
        })
    except Exception as e:
        logger.error(f"Error in create_order: {str(e)}")
        return jsonify({'error': str(e)}), 500

@order_bp.route('/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order"""
    try:
        # Get from Firestore
        db = get_db()
        order_ref = db.collection('orders').document(order_id)
        order = order_ref.get()
        
        if order.exists:
            data = order.to_dict()
            data['id'] = order.id
            return jsonify({
                'status': 'success',
                'order': data
            })
        else:
            return jsonify({'error': 'Order not found'}), 404
    except Exception as e:
        logger.error(f"Error in get_order: {str(e)}")
        return jsonify({'error': str(e)}), 500

@order_bp.route('/customer/<customer_id>', methods=['GET'])
def get_customer_orders(customer_id):
    """Get all orders for a customer"""
    try:
        # Query Firestore
        db = get_db()
        orders = (
            db.collection('orders')
            .where("customer.id", "==", customer_id)
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .stream()
        )
        
        # Convert to list of dictionaries
        result = []
        for order in orders:
            data = order.to_dict()
            data['id'] = order.id
            result.append(data)
            
        return jsonify({
            'status': 'success',
            'count': len(result),
            'orders': result
        })
    except Exception as e:
        logger.error(f"Error in get_customer_orders: {str(e)}")
        return jsonify({'error': str(e)}), 500

@order_bp.route('/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update the status of an order"""
    try:
        # Check authentication
        token = request.headers.get('X-API-Token')
        if not token or token != 'your_admin_token_here':  # This should be properly secured in production
            return jsonify({'error': 'Unauthorized'}), 401
            
        data = request.json
        if not data or 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
            
        # Update in Firestore
        db = get_db()
        order_ref = db.collection('orders').document(order_id)
        
        # Check if order exists
        if not order_ref.get().exists:
            return jsonify({'error': 'Order not found'}), 404
            
        # Update status and timestamp
        order_ref.update({
            'status': data['status'],
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({
            'status': 'success',
            'message': f'Order {order_id} status updated to {data["status"]}'
        })
    except Exception as e:
        logger.error(f"Error in update_order_status: {str(e)}")
        return jsonify({'error': str(e)}), 500

"""
Chat routes for the Meinn Restaurant AI Assistant.
This module handles API endpoints for chat functionality.
"""

import logging
from flask import Blueprint, request, jsonify
from src.services.chat.conversation_learner import ConversationLearner

# Configure logging
logger = logging.getLogger("meinn_ai.routes.chat")

# Create blueprint
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# Initialize services
conversation_learner = ConversationLearner()

@chat_bp.route('/conversation', methods=['POST'])
def save_conversation():
    """Save a new conversation"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        user_id = data.get('user_id')
        conversation_data = data.get('conversation')
        
        if not user_id or not conversation_data:
            return jsonify({'error': 'Missing required fields'}), 400
            
        conversation_id = conversation_learner.save_conversation(user_id, conversation_data)
        
        if conversation_id:
            return jsonify({
                'status': 'success',
                'conversation_id': conversation_id
            })
        else:
            return jsonify({'error': 'Failed to save conversation'}), 500
    except Exception as e:
        logger.error(f"Error in save_conversation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/conversations/<user_id>', methods=['GET'])
def get_user_conversations(user_id):
    """Get all conversations for a user"""
    try:
        limit = request.args.get('limit', default=10, type=int)
        conversations = conversation_learner.get_user_conversations(user_id, limit)
        
        return jsonify({
            'status': 'success',
            'count': len(conversations),
            'conversations': conversations
        })
    except Exception as e:
        logger.error(f"Error in get_user_conversations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get a specific conversation"""
    try:
        conversation = conversation_learner.get_conversation(conversation_id)
        
        if conversation:
            return jsonify({
                'status': 'success',
                'conversation': conversation
            })
        else:
            return jsonify({'error': 'Conversation not found'}), 404
    except Exception as e:
        logger.error(f"Error in get_conversation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/conversation/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a specific conversation"""
    try:
        success = conversation_learner.delete_conversation(conversation_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Conversation {conversation_id} deleted'
            })
        else:
            return jsonify({'error': 'Failed to delete conversation'}), 500
    except Exception as e:
        logger.error(f"Error in delete_conversation: {str(e)}")
        return jsonify({'error': str(e)}), 500

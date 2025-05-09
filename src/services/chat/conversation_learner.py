"""
Conversation learner module for Meinn Restaurant AI Assistant.
This module handles storing and retrieving customer conversations.
Firebase implementation for serverless deployment.
"""

import logging
import datetime
import json
from firebase_admin import firestore
from firebase_config import get_firestore_client

logger = logging.getLogger("meinn_ai.conversation_learner")

class ConversationLearner:
    """Manages conversation history using Firestore"""
    
    def __init__(self):
        """Initialize the conversation learner with Firestore database"""
        self.db = None
        self.collection_name = "conversations"
        
    def _init_database(self):
        """Initialize Firestore database connection"""
        try:
            self.db = get_firestore_client()
            logger.info("Conversation learner Firestore initialized")
        except Exception as e:
            logger.error(f"Error initializing Firestore: {str(e)}")
            raise
    
    def save_conversation(self, user_id, conversation_data):
        """
        Save a conversation to Firestore
        
        Args:
            user_id (str): Unique identifier for the user
            conversation_data (dict): Conversation data to save
        
        Returns:
            str: ID of the saved conversation
        """
        if not self.db:
            self._init_database()
            
        try:
            # Add timestamp
            conversation_data['timestamp'] = firestore.SERVER_TIMESTAMP
            conversation_data['user_id'] = user_id
            
            # Add to Firestore
            conversation_ref = self.db.collection(self.collection_name).document()
            conversation_ref.set(conversation_data)
            
            logger.info(f"Saved conversation for user {user_id} with ID {conversation_ref.id}")
            return conversation_ref.id
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
            return None
    
    def get_user_conversations(self, user_id, limit=10):
        """
        Retrieve conversations for a specific user
        
        Args:
            user_id (str): Unique identifier for the user
            limit (int): Maximum number of conversations to retrieve
        
        Returns:
            list: List of conversation dictionaries
        """
        if not self.db:
            self._init_database()
            
        try:
            # Query Firestore
            conversations = (
                self.db.collection(self.collection_name)
                .where("user_id", "==", user_id)
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )
            
            # Convert to list of dictionaries
            result = []
            for conv in conversations:
                data = conv.to_dict()
                data['id'] = conv.id
                result.append(data)
                
            logger.info(f"Retrieved {len(result)} conversations for user {user_id}")
            return result
        except Exception as e:
            logger.error(f"Error retrieving conversations: {str(e)}")
            return []
    
    def get_conversation(self, conversation_id):
        """
        Retrieve a specific conversation by ID
        
        Args:
            conversation_id (str): ID of the conversation to retrieve
        
        Returns:
            dict: Conversation data or None if not found
        """
        if not self.db:
            self._init_database()
            
        try:
            # Get from Firestore
            conversation_ref = self.db.collection(self.collection_name).document(conversation_id)
            conversation = conversation_ref.get()
            
            if conversation.exists:
                data = conversation.to_dict()
                data['id'] = conversation.id
                return data
            else:
                logger.warning(f"Conversation {conversation_id} not found")
                return None
        except Exception as e:
            logger.error(f"Error retrieving conversation {conversation_id}: {str(e)}")
            return None
    
    def delete_conversation(self, conversation_id):
        """
        Delete a conversation from Firestore
        
        Args:
            conversation_id (str): ID of the conversation to delete
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.db:
            self._init_database()
            
        try:
            # Delete from Firestore
            self.db.collection(self.collection_name).document(conversation_id).delete()
            logger.info(f"Deleted conversation {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting conversation {conversation_id}: {str(e)}")
            return False

"""
Conversation Learner for the Meinn Restaurant Menu AI Assistant.
Handles conversation history, context, and learning from user interactions.
"""

import logging
import json
import sqlite3
import os
import uuid
from datetime import datetime

# Set up logger
logger = logging.getLogger("meinn_ai.conversation_learner")

class ConversationLearner:
    """
    Manages conversation history, context, and learning from user interactions.
    Provides methods for retrieving and storing conversations, as well as
    extracting patterns and preferences from user interactions.
    """
    
    def __init__(self):
        """Initialize the conversation learner"""
        self.db_path = "conversations.db"
        logger.info("Conversation Learner initialized")
        
    def _init_database(self):
        """Initialize the conversation database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                language TEXT DEFAULT 'az',
                session_id TEXT
            )
            ''')
            
            # Create messages table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                sender TEXT NOT NULL, -- 'user' or 'bot'
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Conversation database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing conversation database: {str(e)}", exc_info=True)
            raise
            
    def create_conversation(self, user_id=None, language='az'):
        """
        Create a new conversation
        
        Args:
            user_id (str, optional): User identifier
            language (str): Conversation language code
            
        Returns:
            str: Conversation ID
        """
        try:
            conversation_id = str(uuid.uuid4())
            session_id = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO conversations (id, user_id, language, session_id) VALUES (?, ?, ?, ?)",
                (conversation_id, user_id, language, session_id)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Created new conversation: {conversation_id}")
            return conversation_id
            
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}", exc_info=True)
            return None
            
    def add_message(self, conversation_id, sender, content):
        """
        Add a message to a conversation
        
        Args:
            conversation_id (str): Conversation identifier
            sender (str): Message sender ('user' or 'bot')
            content (str): Message content
            
        Returns:
            bool: Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO messages (conversation_id, sender, content) VALUES (?, ?, ?)",
                (conversation_id, sender, content)
            )
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}", exc_info=True)
            return False
            
    def get_conversation_history(self, conversation_id, limit=10):
        """
        Get conversation history
        
        Args:
            conversation_id (str): Conversation identifier
            limit (int): Maximum number of messages to retrieve
            
        Returns:
            list: List of message dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT * FROM messages 
                   WHERE conversation_id = ? 
                   ORDER BY timestamp DESC LIMIT ?""",
                (conversation_id, limit)
            )
            
            rows = cursor.fetchall()
            messages = [dict(row) for row in rows]
            messages.reverse()  # Return in chronological order
            
            conn.close()
            return messages
            
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}", exc_info=True)
            return []
            
    def end_conversation(self, conversation_id):
        """
        Mark a conversation as ended
        
        Args:
            conversation_id (str): Conversation identifier
            
        Returns:
            bool: Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE conversations SET end_time = CURRENT_TIMESTAMP WHERE id = ?",
                (conversation_id,)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Ended conversation: {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error ending conversation: {str(e)}", exc_info=True)
            return False
            
    def extract_order_intent(self, message):
        """
        Extract order intent from a message
        
        Args:
            message (str): User message
            
        Returns:
            dict: Extracted intent information or None
        """
        # In a real implementation, this would use NLP to extract
        # order intent, quantities, preferences, etc.
        # For now, we'll use a simple keyword-based approach
        
        message = message.lower()
        
        # Check for ordering intent
        ordering_keywords = [
            'order', 'get', 'want', 'like', 'sifariş', 'istəyirəm', 'almaq'
        ]
        
        has_order_intent = any(keyword in message for keyword in ordering_keywords)
        
        if not has_order_intent:
            return None
            
        # Extract quantities and items (simplified)
        result = {
            'has_order_intent': True,
            'items': []
        }
        
        # For simplification, just look for pizza, pasta, etc.
        if 'pizza' in message:
            result['items'].append({
                'type': 'pizza',
                'quantity': 1
            })
            
        if 'pasta' in message or 'spaghetti' in message:
            result['items'].append({
                'type': 'pasta',
                'quantity': 1
            })
            
        if 'water' in message or 'su' in message:
            result['items'].append({
                'type': 'drink',
                'quantity': 1
            })
            
        if 'dessert' in message or 'tiramisu' in message:
            result['items'].append({
                'type': 'dessert',
                'quantity': 1
            })
            
        return result if result['items'] else None
        
    def extract_food_preferences(self, conversation_id):
        """
        Extract food preferences from conversation history
        
        Args:
            conversation_id (str): Conversation identifier
            
        Returns:
            dict: Extracted preferences
        """
        # This would be a more sophisticated analysis in a real implementation
        # For now, we'll use a simplified approach
        
        try:
            history = self.get_conversation_history(conversation_id, limit=50)
            user_messages = [msg['content'] for msg in history if msg['sender'] == 'user']
            
            preferences = {
                'dietary': [],
                'liked_items': [],
                'disliked_items': []
            }
            
            # Simple keyword extraction
            all_text = ' '.join(user_messages).lower()
            
            # Check for dietary preferences
            if 'vegetarian' in all_text or 'vegetariana' in all_text:
                preferences['dietary'].append('vegetarian')
                
            if 'vegan' in all_text:
                preferences['dietary'].append('vegan')
                
            if 'gluten' in all_text and ('free' in all_text or 'allergy' in all_text):
                preferences['dietary'].append('gluten-free')
                
            if 'lactose' in all_text and ('free' in all_text or 'allergy' in all_text):
                preferences['dietary'].append('lactose-free')
                
            # Liked/disliked items (very simplified)
            if 'like pizza' in all_text or 'love pizza' in all_text:
                preferences['liked_items'].append('pizza')
                
            if 'like pasta' in all_text or 'love pasta' in all_text:
                preferences['liked_items'].append('pasta')
                
            if 'don\'t like' in all_text and 'spicy' in all_text:
                preferences['disliked_items'].append('spicy')
                
            return preferences
            
        except Exception as e:
            logger.error(f"Error extracting food preferences: {str(e)}", exc_info=True)
            return {'dietary': [], 'liked_items': [], 'disliked_items': []}

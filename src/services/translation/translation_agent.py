"""
Translation agent module for Meinn Restaurant AI Assistant.
This module handles language detection and translation services.
Firebase implementation for serverless deployment.
"""

import logging
import langid
from googletrans import Translator as GoogleTranslator
from firebase_admin import firestore
from firebase_config import get_firestore_client

logger = logging.getLogger("meinn_ai.translation_agent")

class TranslationAgent:
    """Manages translations and language detection using Firestore"""
    
    def __init__(self):
        """Initialize the translation agent with Firestore database"""
        self.db = None
        self.collection_name = "translations"
        self.translator = GoogleTranslator()
        
    def _init_database(self):
        """Initialize Firestore database connection"""
        try:
            self.db = get_firestore_client()
            logger.info("Translation agent Firestore initialized")
        except Exception as e:
            logger.error(f"Error initializing Firestore: {str(e)}")
            raise
    
    def detect_language(self, text):
        """
        Detect the language of the provided text
        
        Args:
            text (str): Text to detect language for
            
        Returns:
            str: ISO 639-1 language code
        """
        try:
            lang, confidence = langid.classify(text)
            logger.info(f"Detected language: {lang} (confidence: {confidence})")
            return lang
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            return "en"  # Default to English on error
    
    def translate_text(self, text, target_language="en", source_language=None):
        """
        Translate text to the target language
        
        Args:
            text (str): Text to translate
            target_language (str): Target language code (ISO 639-1)
            source_language (str, optional): Source language code, auto-detect if None
            
        Returns:
            str: Translated text
        """
        if not text:
            return ""
            
        # Check cache first
        cache_key = f"{text}:{target_language}"
        cached_translation = self._get_cached_translation(cache_key)
        if cached_translation:
            return cached_translation
            
        # Perform translation
        try:
            translation = self.translator.translate(
                text, 
                dest=target_language,
                src=source_language if source_language else 'auto'
            )
            
            # Cache the result
            self._cache_translation(cache_key, translation.text)
            
            logger.info(f"Translated text from {translation.src} to {target_language}")
            return translation.text
        except Exception as e:
            logger.error(f"Error translating text: {str(e)}")
            return text  # Return original text on error
    
    def _get_cached_translation(self, cache_key):
        """
        Get a cached translation from Firestore
        
        Args:
            cache_key (str): Cache key to look up
            
        Returns:
            str: Cached translation or None if not found
        """
        if not self.db:
            self._init_database()
            
        try:
            doc_ref = self.db.collection(self.collection_name).document(cache_key)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                logger.info(f"Retrieved cached translation for key {cache_key}")
                return data.get('translation')
            return None
        except Exception as e:
            logger.error(f"Error retrieving cached translation: {str(e)}")
            return None
    
    def _cache_translation(self, cache_key, translation):
        """
        Cache a translation in Firestore
        
        Args:
            cache_key (str): Cache key to store under
            translation (str): Translated text to cache
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.db:
            self._init_database()
            
        try:
            doc_ref = self.db.collection(self.collection_name).document(cache_key)
            doc_ref.set({
                'translation': translation,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            logger.info(f"Cached translation for key {cache_key}")
            return True
        except Exception as e:
            logger.error(f"Error caching translation: {str(e)}")
            return False
    
    def translate_menu_item(self, menu_item, target_language="en"):
        """
        Translate a menu item's name and description
        
        Args:
            menu_item (dict): Menu item with name and description
            target_language (str): Target language code
            
        Returns:
            dict: Translated menu item
        """
        if not menu_item:
            return {}
            
        result = menu_item.copy()
        
        if 'name' in menu_item:
            result['name'] = self.translate_text(menu_item['name'], target_language)
            
        if 'description' in menu_item:
            result['description'] = self.translate_text(menu_item['description'], target_language)
            
        return result

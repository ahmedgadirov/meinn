"""
Translation Agent for the Meinn Restaurant Menu AI Assistant.
Handles language detection and translation for multilingual support.
"""

import logging
import json
import sqlite3
import os
import uuid
from datetime import datetime
import traceback

# Set up logger
logger = logging.getLogger("meinn_ai.translation_agent")

class TranslationAgent:
    """
    Manages language detection and translation for multilingual support.
    Provides methods for detecting languages, translating text, and
    maintaining a translation cache.
    """
    
    def __init__(self):
        """Initialize the translation agent"""
        self.db_path = "translation_data.db"
        self.supported_languages = {
            'az': 'Azerbaijani',
            'en': 'English',
            'ru': 'Russian',
            'tr': 'Turkish',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'fr': 'French',
            'it': 'Italian'
        }
        self.default_language = 'az'
        logger.info("Translation Agent initialized")
        
    def _init_database(self):
        """Initialize the translation database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create translations table for static content
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS translations (
                key TEXT NOT NULL,
                language TEXT NOT NULL,
                translation TEXT NOT NULL,
                context TEXT,
                PRIMARY KEY (key, language)
            )
            ''')
            
            # Create translation cache table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS translation_cache (
                source_text TEXT NOT NULL,
                source_language TEXT NOT NULL,
                target_language TEXT NOT NULL,
                translated_text TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (source_text, source_language, target_language)
            )
            ''')
            
            # Create language detection cache table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS language_detection_cache (
                text TEXT PRIMARY KEY,
                detected_language TEXT NOT NULL,
                confidence REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            conn.commit()
            conn.close()
            
            # Insert some initial translations for common phrases
            self._insert_default_translations()
            
            logger.info("Translation database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing translation database: {str(e)}", exc_info=True)
            raise
            
    def _insert_default_translations(self):
        """Insert default translations for common phrases"""
        try:
            # Common menu-related phrases
            default_translations = [
                # Welcome message
                {
                    'key': 'welcome_message',
                    'translations': {
                        'az': 'Salam! Mən Pizza Inn-in menyu köməkçisiyəm. Sizə necə kömək edə bilərəm?',
                        'en': 'Hello! I\'m the Pizza Inn menu assistant. How can I help you today?',
                        'ru': 'Привет! Я помощник меню Pizza Inn. Чем я могу вам помочь?',
                        'tr': 'Merhaba! Ben Pizza Inn menü asistanıyım. Size nasıl yardımcı olabilirim?',
                        'ar': 'مرحبا! أنا مساعد قائمة بيتزا إن. كيف يمكنني مساعدتك اليوم؟',
                        'hi': 'नमस्ते! मैं पिज़्ज़ा इन मेनू सहायक हूँ। आज मैं आपकी कैसे मदद कर सकता हूँ?',
                        'fr': 'Bonjour! Je suis l\'assistant menu de Pizza Inn. Comment puis-je vous aider aujourd\'hui?',
                        'it': 'Ciao! Sono l\'assistente del menu di Pizza Inn. Come posso aiutarti oggi?'
                    }
                },
                # Order confirmation
                {
                    'key': 'order_confirmation',
                    'translations': {
                        'az': 'Sifarişinizi təsdiq etmək istəyirsiniz?',
                        'en': 'Would you like to confirm your order?',
                        'ru': 'Вы хотите подтвердить ваш заказ?',
                        'tr': 'Siparişinizi onaylamak istiyor musunuz?',
                        'ar': 'هل ترغب في تأكيد طلبك؟',
                        'hi': 'क्या आप अपने ऑर्डर की पुष्टि करना चाहते हैं?',
                        'fr': 'Souhaitez-vous confirmer votre commande?',
                        'it': 'Vuoi confermare il tuo ordine?'
                    }
                },
                # Menu categories
                {
                    'key': 'menu_category_pizza',
                    'translations': {
                        'az': 'Pizzalar',
                        'en': 'Pizzas',
                        'ru': 'Пиццы',
                        'tr': 'Pizzalar',
                        'ar': 'البيتزا',
                        'hi': 'पिज्जा',
                        'fr': 'Pizzas',
                        'it': 'Pizze'
                    }
                },
                {
                    'key': 'menu_category_pasta',
                    'translations': {
                        'az': 'Pastalar',
                        'en': 'Pasta',
                        'ru': 'Паста',
                        'tr': 'Makarnalar',
                        'ar': 'المعكرونة',
                        'hi': 'पास्ता',
                        'fr': 'Pâtes',
                        'it': 'Pasta'
                    }
                },
                {
                    'key': 'menu_category_drinks',
                    'translations': {
                        'az': 'İçkilər',
                        'en': 'Drinks',
                        'ru': 'Напитки',
                        'tr': 'İçecekler',
                        'ar': 'المشروبات',
                        'hi': 'पेय',
                        'fr': 'Boissons',
                        'it': 'Bevande'
                    }
                },
                {
                    'key': 'menu_category_desserts',
                    'translations': {
                        'az': 'Desertlər',
                        'en': 'Desserts',
                        'ru': 'Десерты',
                        'tr': 'Tatlılar',
                        'ar': 'الحلويات',
                        'hi': 'मिठाई',
                        'fr': 'Desserts',
                        'it': 'Dolci'
                    }
                }
            ]
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for item in default_translations:
                key = item['key']
                for lang, translation in item['translations'].items():
                    cursor.execute(
                        """INSERT OR REPLACE INTO translations 
                           (key, language, translation) VALUES (?, ?, ?)""",
                        (key, lang, translation)
                    )
            
            conn.commit()
            conn.close()
            
            logger.info("Default translations inserted")
        except Exception as e:
            logger.error(f"Error inserting default translations: {str(e)}", exc_info=True)
            
    def get_translation(self, key, language):
        """
        Get a translation for a specific key and language
        
        Args:
            key (str): Translation key
            language (str): Language code
            
        Returns:
            str: Translated text or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT translation FROM translations WHERE key = ? AND language = ?",
                (key, language)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
                
            # If translation not found in requested language, fall back to English
            if language != 'en':
                return self.get_translation(key, 'en')
                
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving translation: {str(e)}", exc_info=True)
            return None
            
    def detect_language(self, text):
        """
        Detect the language of a text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Detected language code or default language if detection fails
        """
        # In a real implementation, this would use a language detection library
        # For this demo, we'll use a very simplistic approach based on common words
        
        # Check cache first
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT detected_language FROM language_detection_cache WHERE text = ?",
                (text[:100],)  # Use first 100 chars as key
            )
            
            result = cursor.fetchone()
            
            if result:
                conn.close()
                return result[0]
                
            # For demo purposes, use a simple keyword-based approach
            text = text.lower()
            
            # Define language indicators (common words/characters)
            indicators = {
                'az': ['salam', 'necə', 'və', 'üçün', 'istəyirəm', 'edir', 'olur', 'mən', 'siz', 'biz', 'ə', 'ı', 'ö', 'ü'],
                'en': ['the', 'and', 'for', 'is', 'in', 'to', 'hello', 'want', 'please', 'thank', 'would', 'like'],
                'ru': ['и', 'в', 'не', 'что', 'привет', 'пожалуйста', 'спасибо', 'хочу', 'меню', 'ы', 'э', 'я', 'ю'],
                'tr': ['ve', 'için', 'bir', 'bu', 'merhaba', 'lütfen', 'teşekkür', 'istiyorum', 'menü', 'ı', 'ğ', 'ş', 'ç', 'ö', 'ü'],
                'ar': ['و', 'في', 'من', 'هذا', 'مرحبا', 'شكرا', 'أريد', 'قائمة', 'ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د'],
                'hi': ['और', 'के', 'में', 'है', 'नमस्ते', 'धन्यवाद', 'चाहते', 'मेनू', 'ा', 'ि', 'ी', 'ु', 'ू', 'े', 'ै', 'ो', 'ौ'],
                'fr': ['et', 'le', 'la', 'les', 'pour', 'dans', 'bonjour', 'merci', 'voudrais', 'menu', 'é', 'è', 'ê', 'à', 'ç', 'ù'],
                'it': ['e', 'il', 'la', 'per', 'in', 'ciao', 'grazie', 'vorrei', 'menu', 'à', 'è', 'ì', 'ò', 'ù']
            }
            
            # Count matches for each language
            scores = {lang: 0 for lang in indicators.keys()}
            
            for lang, words in indicators.items():
                for word in words:
                    if word in text:
                        scores[lang] += 1
                        
            # Get the language with the highest score
            detected_lang = max(scores.items(), key=lambda x: x[1])
            
            # Default to English if no clear winner
            if detected_lang[1] == 0:
                detected_lang = (self.default_language, 0)
                
            # Save to cache
            cursor.execute(
                """INSERT OR REPLACE INTO language_detection_cache 
                   (text, detected_language, confidence) VALUES (?, ?, ?)""",
                (text[:100], detected_lang[0], detected_lang[1])
            )
            
            conn.commit()
            conn.close()
            
            return detected_lang[0]
            
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}", exc_info=True)
            return self.default_language
            
    def translate_text(self, text, source_language=None, target_language='en'):
        """
        Translate text from source language to target language
        
        Args:
            text (str): Text to translate
            source_language (str, optional): Source language code (auto-detect if None)
            target_language (str): Target language code
            
        Returns:
            str: Translated text or original text if translation fails
        """
        try:
            # Auto-detect language if not specified
            if not source_language:
                source_language = self.detect_language(text)
                
            # If source and target are the same, return original text
            if source_language == target_language:
                return text
                
            # Check cache first
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT translated_text FROM translation_cache 
                   WHERE source_text = ? AND source_language = ? AND target_language = ?""",
                (text, source_language, target_language)
            )
            
            result = cursor.fetchone()
            
            if result:
                conn.close()
                return result[0]
                
            # In a real implementation, this would call a translation API
            # For this demo, we'll handle a few hardcoded cases and return the original for others
            
            translated_text = text  # Default to original text
            
            # Add translation logic here (in real implementation, call API)
            # For demo, we'll just use our default translations if they match
            
            # TODO: Add more sophisticated translation logic
            
            # Save to cache
            cursor.execute(
                """INSERT OR REPLACE INTO translation_cache 
                   (source_text, source_language, target_language, translated_text) 
                   VALUES (?, ?, ?, ?)""",
                (text, source_language, target_language, translated_text)
            )
            
            conn.commit()
            conn.close()
            
            return translated_text
            
        except Exception as e:
            logger.error(f"Error translating text: {str(e)}", exc_info=True)
            return text

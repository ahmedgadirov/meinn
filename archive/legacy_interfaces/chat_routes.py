"""
Chat routes for the Meinn Restaurant Menu AI Assistant.
Handles all API routes related to chatbot interactions.
"""

import logging
import json
from flask import Blueprint, request, jsonify
import time
import random
import uuid

from src.services.chat.conversation_learner import ConversationLearner
from src.services.translation.translation_agent import TranslationAgent
from src.services.product.menu_manager import MenuManager

# Set up logger
logger = logging.getLogger("meinn_ai.chat_routes")

# Create a blueprint for chat routes
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# Initialize services
conversation_learner = ConversationLearner()
translator = TranslationAgent()
menu_manager = MenuManager()

@chat_bp.route('/message', methods=['POST'])
def handle_message():
    """Handle a new chat message from the user"""
    try:
        # Get message data from request body
        data = request.json
        message = data.get('message')
        conversation_id = data.get('conversation_id')
        language = data.get('language', 'az')
        
        if not message:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400
            
        # Create a new conversation if one doesn't exist
        if not conversation_id:
            conversation_id = conversation_learner.create_conversation(language=language)
            
        # Add user message to conversation history
        conversation_learner.add_message(conversation_id, 'user', message)
        
        # Detect language if not provided
        if language == 'auto':
            language = translator.detect_language(message)
            
        # Process the message
        response = process_message(message, conversation_id, language)
        
        # Add bot response to conversation history
        conversation_learner.add_message(conversation_id, 'bot', response)
        
        return jsonify({
            "success": True,
            "conversation_id": conversation_id,
            "response": response,
            "detected_language": language
        })
        
    except Exception as e:
        logger.error(f"Error handling chat message: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to process message",
            "message": str(e)
        }), 500

@chat_bp.route('/start', methods=['POST'])
def start_conversation():
    """Start a new conversation"""
    try:
        # Get language from request body
        data = request.json
        language = data.get('language', 'az')
        user_id = data.get('user_id')
        
        # Create a new conversation
        conversation_id = conversation_learner.create_conversation(
            user_id=user_id,
            language=language
        )
        
        # Get welcome message
        welcome_message = translator.get_translation('welcome_message', language)
        
        # Add bot message to conversation history
        conversation_learner.add_message(conversation_id, 'bot', welcome_message)
        
        return jsonify({
            "success": True,
            "conversation_id": conversation_id,
            "welcome_message": welcome_message
        })
        
    except Exception as e:
        logger.error(f"Error starting conversation: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to start conversation",
            "message": str(e)
        }), 500

@chat_bp.route('/history/<conversation_id>', methods=['GET'])
def get_conversation_history(conversation_id):
    """Get conversation history"""
    try:
        # Get limit from query parameters
        limit = request.args.get('limit', 10, type=int)
        
        # Get conversation history
        history = conversation_learner.get_conversation_history(conversation_id, limit)
        
        return jsonify({
            "success": True,
            "history": history
        })
        
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to retrieve conversation history",
            "message": str(e)
        }), 500

@chat_bp.route('/end/<conversation_id>', methods=['POST'])
def end_conversation(conversation_id):
    """End a conversation"""
    try:
        # End the conversation
        success = conversation_learner.end_conversation(conversation_id)
        
        return jsonify({
            "success": success
        })
        
    except Exception as e:
        logger.error(f"Error ending conversation: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to end conversation",
            "message": str(e)
        }), 500

def process_message(message, conversation_id, language):
    """
    Process a message and generate a response
    
    Args:
        message (str): User message
        conversation_id (str): Conversation ID
        language (str): Language code
        
    Returns:
        str: Response message
    """
    # In a full implementation, this would use a more sophisticated NLP approach
    # and possibly call an external AI service
    
    try:
        # Check for order intent
        order_intent = conversation_learner.extract_order_intent(message)
        
        if order_intent:
            # Handle order intent
            return handle_order_intent(order_intent, language)
            
        # Check for menu-related queries
        if is_menu_query(message):
            return handle_menu_query(message, language)
            
        # Check for general questions
        response = handle_general_query(message, language)
        if response:
            return response
            
        # Default responses
        default_responses = {
            'az': "Üzr istəyirəm, tam başa düşə bilmədim. Menyu haqqında sual vermək və ya sifariş vermək istəyirsiniz?",
            'en': "I'm sorry, I didn't quite understand that. Would you like to ask about the menu or place an order?",
            'ru': "Извините, я не совсем понял. Вы хотите узнать о меню или сделать заказ?",
            'tr': "Özür dilerim, tam olarak anlayamadım. Menü hakkında soru sormak mı yoksa sipariş vermek mi istiyorsunuz?",
            'ar': "آسف، لم أفهم تمامًا. هل تريد السؤال عن القائمة أو تقديم طلب؟",
            'hi': "मुझे माफ करें, मैं पूरी तरह समझ नहीं पाया। क्या आप मेनू के बारे में पूछना चाहते हैं या ऑर्डर देना चाहते हैं?",
            'fr': "Je suis désolé, je n'ai pas bien compris. Souhaitez-vous vous renseigner sur le menu ou passer une commande ?",
            'it': "Mi dispiace, non ho capito bene. Vorresti chiedere informazioni sul menu o effettuare un ordine?"
        }
        
        return default_responses.get(language, default_responses['en'])
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        return "I'm sorry, I'm having trouble processing your request right now."

def is_menu_query(message):
    """Check if the message is a menu-related query"""
    menu_keywords = [
        'menu', 'food', 'eat', 'pizza', 'pasta', 'drink', 'dessert',
        'menyu', 'yemək', 'içki', 'desert', 'pitsa', 'пицца', 'меню'
    ]
    
    message = message.lower()
    return any(keyword in message for keyword in menu_keywords)

def handle_menu_query(message, language):
    """Handle a menu-related query"""
    message = message.lower()
    
    # Check for specific categories
    if 'pizza' in message:
        pizza_items = menu_manager.get_menu_items(category_id='pizza')
        
        # Format response based on language
        if language == 'az':
            response = "Pizzalarımız: "
        elif language == 'ru':
            response = "Наши пиццы: "
        elif language == 'tr':
            response = "Pizzalarımız: "
        else:
            response = "Our pizzas: "
            
        items = [f"{item['name']} (${item['price']:.2f})" for item in pizza_items]
        return response + ", ".join(items)
        
    elif 'pasta' in message or 'spaghetti' in message:
        pasta_items = menu_manager.get_menu_items(category_id='pasta')
        
        # Format response based on language
        if language == 'az':
            response = "Pastalarımız: "
        elif language == 'ru':
            response = "Наши пасты: "
        elif language == 'tr':
            response = "Makarnalarımız: "
        else:
            response = "Our pasta dishes: "
            
        items = [f"{item['name']} (${item['price']:.2f})" for item in pasta_items]
        return response + ", ".join(items)
        
    elif 'drink' in message or 'beverage' in message or 'içki' in message:
        drink_items = menu_manager.get_menu_items(category_id='drinks')
        
        # Format response based on language
        if language == 'az':
            response = "İçkilərimiz: "
        elif language == 'ru':
            response = "Наши напитки: "
        elif language == 'tr':
            response = "İçeceklerimiz: "
        else:
            response = "Our drinks: "
            
        items = [f"{item['name']} (${item['price']:.2f})" for item in drink_items]
        return response + ", ".join(items)
        
    elif 'dessert' in message or 'tatlı' in message or 'desert' in message:
        dessert_items = menu_manager.get_menu_items(category_id='desserts')
        
        # Format response based on language
        if language == 'az':
            response = "Desertlərimiz: "
        elif language == 'ru':
            response = "Наши десерты: "
        elif language == 'tr':
            response = "Tatlılarımız: "
        else:
            response = "Our desserts: "
            
        items = [f"{item['name']} (${item['price']:.2f})" for item in dessert_items]
        return response + ", ".join(items)
        
    # General menu query
    popular_items = [item for item in menu_manager.get_menu_items() if item.get('popular')]
    
    # Format response based on language
    if language == 'az':
        response = "Ən populyar yeməklərimiz: "
    elif language == 'ru':
        response = "Наши самые популярные блюда: "
    elif language == 'tr':
        response = "En popüler yemeklerimiz: "
    else:
        response = "Our most popular items: "
        
    items = [f"{item['name']} (${item['price']:.2f})" for item in popular_items[:3]]
    return response + ", ".join(items)

def handle_order_intent(order_intent, language):
    """Handle an order intent"""
    items = order_intent.get('items', [])
    
    if not items:
        if language == 'az':
            return "Nə sifariş etmək istədiyinizi dəqiqləşdirə bilərsinizmi?"
        elif language == 'ru':
            return "Можете ли вы уточнить, что вы хотите заказать?"
        elif language == 'tr':
            return "Ne sipariş etmek istediğinizi açıklayabilir misiniz?"
        else:
            return "Could you clarify what you'd like to order?"
    
    # Format order confirmation
    if language == 'az':
        response = "Sifarişinizi təsdiqləyirəm: "
    elif language == 'ru':
        response = "Подтверждаю ваш заказ: "
    elif language == 'tr':
        response = "Siparişinizi onaylıyorum: "
    else:
        response = "I'm confirming your order: "
        
    order_items = []
    for item in items:
        item_type = item.get('type')
        quantity = item.get('quantity', 1)
        
        if item_type == 'pizza':
            order_items.append(f"Pizza x{quantity}")
        elif item_type == 'pasta':
            order_items.append(f"Pasta x{quantity}")
        elif item_type == 'drink':
            order_items.append(f"İçki x{quantity}")
        elif item_type == 'dessert':
            order_items.append(f"Desert x{quantity}")
    
    response += ", ".join(order_items)
    
    # Add order confirmation question
    if language == 'az':
        response += ". Təsdiqləmək istəyirsiniz?"
    elif language == 'ru':
        response += ". Хотите подтвердить?"
    elif language == 'tr':
        response += ". Onaylamak istiyor musunuz?"
    else:
        response += ". Would you like to confirm?"
        
    return response

def handle_general_query(message, language):
    """Handle general queries"""
    message = message.lower()
    
    # Check for common questions
    if 'hours' in message or 'open' in message or 'açıq' in message or 'saat' in message:
        if language == 'az':
            return "Biz hər gün saat 10:00-dan 22:00-a qədər açığıq."
        elif language == 'ru':
            return "Мы открыты ежедневно с 10:00 до 22:00."
        elif language == 'tr':
            return "Her gün 10:00 - 22:00 saatleri arasında açığız."
        else:
            return "We are open daily from 10:00 AM to 10:00 PM."
            
    elif 'location' in message or 'address' in message or 'ünvan' in message or 'adres' in message:
        if language == 'az':
            return "Biz Bakı şəhəri, Nizami küçəsi 42 ünvanında yerləşirik."
        elif language == 'ru':
            return "Мы находимся по адресу: ул. Низами 42, город Баку."
        elif language == 'tr':
            return "Bakü şehri, Nizami caddesi 42 adresinde bulunuyoruz."
        else:
            return "We are located at 42 Nizami Street, Baku."
            
    elif 'delivery' in message or 'çatdırılma' in message or 'доставка' in message:
        if language == 'az':
            return "Bəli, şəhər daxilində 5 km radiusda çatdırılma xidmətimiz var. Minimal sifariş məbləği 20 manatdır."
        elif language == 'ru':
            return "Да, у нас есть доставка в радиусе 5 км по городу. Минимальная сумма заказа составляет 20 манатов."
        elif language == 'tr':
            return "Evet, şehir içinde 5 km yarıçapında teslimat hizmetimiz var. Minimum sipariş tutarı 20 manat."
        else:
            return "Yes, we offer delivery within a 5 km radius in the city. The minimum order amount is 20 AZN."
            
    elif 'payment' in message or 'ödəniş' in message or 'оплата' in message:
        if language == 'az':
            return "Nağd, kredit kartı və mobil ödəniş qəbul edirik."
        elif language == 'ru':
            return "Мы принимаем наличные, кредитные карты и мобильные платежи."
        elif language == 'tr':
            return "Nakit, kredi kartı ve mobil ödeme kabul ediyoruz."
        else:
            return "We accept cash, credit cards, and mobile payments."
            
    elif 'reservation' in message or 'book' in message or 'rezervasiya' in message:
        if language == 'az':
            return "Masa rezervasiyası üçün (012) 345-67-89 nömrəsi ilə əlaqə saxlaya bilərsiniz."
        elif language == 'ru':
            return "Для бронирования столика, пожалуйста, свяжитесь с нами по номеру (012) 345-67-89."
        elif language == 'tr':
            return "Masa rezervasyonu için lütfen (012) 345-67-89 numarasıyla iletişime geçin."
        else:
            return "For table reservations, please contact us at (012) 345-67-89."
            
    return None

"""
Main application entry point for the Meinn Restaurant Menu AI Assistant.
This file initializes the Flask application and starts the server.
"""

import logging
import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from flask_cors import CORS
from src.api.app import create_app
from src.services.translation.translation_agent import TranslationAgent
from src.services.product.menu_manager import MenuManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('meinn_assistant.log')
    ]
)
logger = logging.getLogger("meinn_ai")

def initialize_services():
    """Initialize all required services"""
    try:
        # Initialize translation agent
        translator = TranslationAgent()
        translator._init_database()
        logger.info("Translation agent initialized")
        
        # Initialize menu manager
        menu_manager = MenuManager()
        logger.info("Menu manager initialized")

    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    # Initialize services
    initialize_services()
    
    # Create the Flask app
    app = create_app()
    
    # Configure CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Configure server
    port = int(os.environ.get("PORT", 5002))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    
    restaurant_name = os.environ.get("RESTAURANT_NAME", "Pizza Inn")
    logger.info(f"Initializing Meinn AI for {restaurant_name}")

    # Start the Flask app
    logger.info(f"Starting Meinn Restaurant Menu AI Assistant on port {port} (debug={debug})")
    app.run(host='0.0.0.0', port=port, debug=debug)

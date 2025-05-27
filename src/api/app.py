"""
Flask application for the Meinn Restaurant Menu AI Assistant.
This module handles the main application setup and route configuration.
"""

import os
import logging
from flask import Flask, render_template, send_from_directory, redirect

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('meinn_assistant.log')
    ]
)
logger = logging.getLogger("meinn_ai.app")

def create_app():
    """Create and configure the Flask application"""
    # Set the correct static folder and template folder paths
    static_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/web/static"))
    template_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/web/templates"))
    
    app = Flask(__name__, 
                static_folder=static_folder_path,
                static_url_path='/static',
                template_folder=template_folder_path)
    
    # Import routes after creating the app
    from src.api.routes.chat_routes import chat_bp
    from src.api.routes.menu_routes import menu_bp
    from src.api.routes.order_routes import order_bp
    from src.api.routes.analytics_routes import analytics_bp
    
    # Register blueprints
    app.register_blueprint(chat_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(analytics_bp)
    
    # Home route - uses the new template
    @app.route('/')
    def home():
        return render_template('index.html')
    
    # Legacy chatbot route
    @app.route('/chatbot')
    def chatbot():
        # Use the absolute path to serve files from project root
        return send_from_directory(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")), 'chatbot.html')
    
    # Admin route
    @app.route('/admin')
    def admin():
        # Use the absolute path to serve files from project root
        return send_from_directory(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")), 'admin.html')
    
    # Health check route
    @app.route('/health')
    def health():
        return {"status": "ok", "service": "Meinn AI", "version": "1.1.0"}
    
    return app

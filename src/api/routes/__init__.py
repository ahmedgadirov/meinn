"""
Routes package for Meinn Restaurant Menu AI Assistant.
This module handles the registration of all route blueprints.
"""

from flask import Flask

def register_blueprints(app: Flask):
    """
    Register all route blueprints with the Flask application
    
    Args:
        app (Flask): The Flask application instance
    """
    # Import blueprints
    from src.api.routes.chat_routes import chat_bp
    from src.api.routes.admin_routes import admin_bp
    from src.api.routes.health_routes import health_bp
    from src.api.routes.menu_routes import menu_bp  # New for restaurant menu
    from src.api.routes.order_routes import order_bp  # New for order management
    from src.api.routes.analytics_routes import analytics_bp
    
    # Register blueprints
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(analytics_bp)

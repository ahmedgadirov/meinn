import sys
import os

# Add project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.app import create_app
from flask import Flask, request

# Create the Flask app
app = create_app()

# Vercel uses WSGI and expects the app object directly
# No need for a handler function

# For local development
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)

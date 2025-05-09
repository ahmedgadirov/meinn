import sys
import os

# Add project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.app import create_app
from flask import Flask, request

app = create_app()

# For Vercel serverless function
def handler(request, context):
    return app(request, context)

# For local development
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)

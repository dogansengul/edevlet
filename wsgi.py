#!/usr/bin/env python3
"""
Production WSGI entry point for E-Devlet Event Receiver.
This file is used by Gunicorn to serve the Flask application.
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import the Flask application
from src.core.event_receiver import app

# Configure for production
if __name__ == "__main__":
    # This runs only during development - production uses Gunicorn
    app.run(debug=False, host='127.0.0.1', port=5001) 
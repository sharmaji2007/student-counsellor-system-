# Vercel serverless function entry point
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.app.main import app

# Export the FastAPI app for Vercel
handler = app
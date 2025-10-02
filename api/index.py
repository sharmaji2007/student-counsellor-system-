from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# Import the main app
try:
    from app.main import app
except ImportError:
    # Fallback: create a simple app if import fails
    app = FastAPI(title="Student Platform API")
    
    @app.get("/")
    async def root():
        return {"message": "Student Platform API is running on Vercel!"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "platform": "vercel"}

# Add CORS middleware for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Export for Vercel
handler = app
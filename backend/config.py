"""
Configuration file for the Mkulima-Bora backend
"""
import os
from dotenv import load_dotenv

# Load .env file if it exists (for local development)
# In production (Vercel), environment variables are set directly
# This won't fail if .env doesn't exist
try:
    # Try to load from project root (one level up from backend/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    env_path = os.path.join(project_root, '.env')
    
    # Load .env if it exists, otherwise use environment variables directly
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        # Try loading from current directory as fallback
        load_dotenv()
except Exception:
    # If .env loading fails, continue - environment variables will be used
    # This is expected in production deployments like Vercel
    pass

class Config:
    """Application configuration"""
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Firebase Configuration
    FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY', 'AIzaSyDEX2PIAw5ZhSp84OiZgRK35WfGhTeT-0E')
    FIREBASE_AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN', 'agriculture-43eaf.firebaseapp.com')
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', 'agriculture-43eaf')
    FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET', 'agriculture-43eaf.firebasestorage.app')
    FIREBASE_MESSAGING_SENDER_ID = os.getenv('FIREBASE_MESSAGING_SENDER_ID', '340310533875')
    FIREBASE_APP_ID = os.getenv('FIREBASE_APP_ID', '1:340310533875:web:54c8b2d5e28bf32d437986')
    
    # Application Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('API_SECRET')
    CLOUDINARY_URL = os.getenv('CLOUDINARY_URL')


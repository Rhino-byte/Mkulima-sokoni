"""
Main Flask application for Mkulima-Bora backend
"""
import sys
import os

# Add the backend directory to Python path for Vercel deployment
# 
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from routes.auth import auth_bp
from routes.profiles import profiles_bp
from routes.uploads import uploads_bp
from routes.products import products_bp
from asgiref.wsgi import WsgiToAsgi
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app, origins=Config.CORS_ORIGINS)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(profiles_bp)
app.register_blueprint(uploads_bp)
app.register_blueprint(products_bp)

@app.route('/api/health')
def health():
    """Detailed health check"""
    return {
        'status': 'ok',
        'service': 'Mkulima-Bora Authentication API',
        'version': '1.0.0'
    }, 200

@app.route('/assets/<path:filename>')
def serve_assets(filename: str):
    """
    Serve shared assets (e.g. logos) from the project-level assets directory.
    Frontend HTML can safely reference /assets/img/sokosafi_logo.png.
    """
    project_root = os.path.dirname(backend_dir)
    assets_dir = os.path.join(project_root, 'assets')
    return send_from_directory(assets_dir, filename)

# Serve frontend static files
@app.route('/')
def serve_index():
    """Serve frontend index (index.html)"""
    project_root = os.path.dirname(backend_dir)
    frontend_dir = os.path.join(project_root, 'frontend')
    return send_from_directory(frontend_dir, 'index.html')

@app.route('/<path:path>')
def serve_frontend(path):
    """Serve frontend files - exclude API routes"""
    # Don't serve API routes through this handler
    if path.startswith('api/'):
        return {'error': 'Not found'}, 404
    
    # Get the project root directory (one level up from backend)
    project_root = os.path.dirname(backend_dir)
    frontend_dir = os.path.join(project_root, 'frontend')
    
    # Check if it's a file in frontend directory
    file_path = os.path.join(frontend_dir, path)
    if os.path.isfile(file_path):
        return send_from_directory(frontend_dir, path)
    
    # Try to serve from frontend/js
    if path.startswith('js/'):
        js_file = os.path.join(frontend_dir, 'js', path[3:])
        if os.path.isfile(js_file):
            return send_from_directory(os.path.join(frontend_dir, 'js'), path[3:])
    
    # For HTML files that don't exist, serve index.html
    if path.endswith('.html') or '/' not in path:
        return send_from_directory(frontend_dir, 'index.html')
    
    # Default: serve index.html for SPA routing
    return send_from_directory(frontend_dir, 'index.html')

# Wrap Flask app with ASGI adapter for uvicorn
asgi_app = WsgiToAsgi(app)

# Export app for Vercel (Vercel expects 'app' variable)
# For local uvicorn: use 'asgi_app'
# For Vercel: use 'app' (WSGI)

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)


"""
iAmSmartGate Backend Access Control Server
Main Flask application
"""
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import logging
from models import db, init_db
from api_routes import api_bp
from admin_routes import admin_bp
from background_jobs import start_background_jobs
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure Flask app"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for all origins (for demo purposes)
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Initialize database
    db.init_app(app)
    with app.app_context():
        init_db()
        logger.info("Database initialized")
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()})
    
    # Start background jobs
    start_background_jobs(app)
    
    logger.info("iAmSmartGate Backend Server started")
    return app

# Create app instance for gunicorn
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

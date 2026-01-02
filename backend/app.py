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
    try:
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
        
        # Root endpoint
        @app.route('/')
        def index():
            return jsonify({'message': 'iAmSmartGate Backend API', 'status': 'running'})
        
        # Start background jobs
        start_background_jobs(app)
        
        logger.info("iAmSmartGate Backend Server started")
        return app
    except Exception as e:
        logger.error(f"Error creating app: {str(e)}", exc_info=True)
        raise

# Create app instance for gunicorn
try:
    app = create_app()
except Exception as e:
    logger.error(f"Failed to create app instance: {str(e)}")
    # Create a minimal app for gunicorn to use
    app = Flask(__name__)
    @app.route('/')
    def error():
        return jsonify({'error': 'Failed to initialize app'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

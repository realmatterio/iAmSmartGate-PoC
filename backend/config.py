"""
Configuration for iAmSmartGate Backend
"""
import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///iamsmartgate.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_EXPIRATION_HOURS = 24
    
    # QR Code settings
    QR_EXPIRATION_SECONDS = 60  # 1 minute
    
    # Debug mode
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    TEST_MODE = os.environ.get('TEST_MODE', 'True').lower() == 'true'
    
    # HSM settings (dummy for demo)
    HSM_ENABLED = False  # Dummy HSM
    
    # Background job settings
    PASS_EXPIRATION_CHECK_INTERVAL = 300  # 5 minutes
    AUDIT_LOG_RETENTION_DAYS = 30
    
    # Site definitions
    SITES = {
        'SITE001': 'Main Campus',
        'SITE002': 'Student Halls',
        'SITE003': 'Research Center',
        'SITE004': 'Library'
    }
    
    # Purpose definitions
    PURPOSES = {
        'PURP001': 'Meeting',
        'PURP002': 'Tour',
        'PURP003': 'Delivery',
        'PURP004': 'Maintenance'
    }

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'True').lower() in ['true', '1', 't']
    APP_USERNAME = os.environ.get('APP_USERNAME')
    APP_PASSWORD = os.environ.get('APP_PASSWORD')
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    WTF_CSRF_ENABLED = False
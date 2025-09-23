import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///watchdog.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OAuth2 Configuration
    OAUTH_CLIENT_ID = os.environ.get('OAUTH_CLIENT_ID')
    OAUTH_CLIENT_SECRET = os.environ.get('OAUTH_CLIENT_SECRET')
    OAUTH_DISCOVERY_URL = os.environ.get('OAUTH_DISCOVERY_URL') or 'https://login.microsoftonline.com/common/v2.0/.well-known/openid_configuration'
    
    # Email Configuration
    SMTP_SERVER = os.environ.get('SMTP_SERVER') or 'localhost'
    SMTP_PORT = int(os.environ.get('SMTP_PORT') or 587)
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    EMAIL_FROM = os.environ.get('EMAIL_FROM')
    
    # Monitoring Configuration
    DEFAULT_CHECK_INTERVAL = int(os.environ.get('DEFAULT_CHECK_INTERVAL') or 300)
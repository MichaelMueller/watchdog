from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, User
from auth import auth_bp, init_oauth
from routes import main_bp
from monitoring import MonitoringService
from notifications import NotificationService
import logging
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    # Initialize OAuth
    oauth = init_oauth(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    
    # Initialize notification service
    notification_service = NotificationService(
        smtp_server=app.config['SMTP_SERVER'],
        smtp_port=app.config['SMTP_PORT'],
        username=app.config['SMTP_USERNAME'],
        password=app.config['SMTP_PASSWORD'],
        from_email=app.config['EMAIL_FROM']
    )
    
    # Initialize monitoring service
    monitoring_service = MonitoringService(app, notification_service)
    
    # Store services in app extensions
    app.extensions['notification_service'] = notification_service
    app.extensions['monitoring_service'] = monitoring_service
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.FileHandler('logs/watchdog.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Watchdog startup')
    
    return app, monitoring_service

if __name__ == '__main__':
    app, monitoring_service = create_app()
    
    # Start monitoring service in development
    if app.debug:
        monitoring_service.start()
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        monitoring_service.stop()
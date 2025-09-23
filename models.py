from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.String(100), primary_key=True)  # OAuth subject ID
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

class ServiceStatus(Enum):
    UP = "up"
    DOWN = "down"
    UNKNOWN = "unknown"

class ServiceEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    host = db.Column(db.String(255), nullable=False)  # IP or DNS
    port = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    admin_email = db.Column(db.String(100), nullable=False)
    check_interval = db.Column(db.Integer, default=300)  # seconds
    check_type = db.Column(db.String(50), default='tcp')  # tcp, http, https
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100), db.ForeignKey('user.id'), nullable=False)
    
    # Relationship
    creator = db.relationship('User', backref=db.backref('services', lazy=True))

class ServiceCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service_entry.id'), nullable=False)
    status = db.Column(db.Enum(ServiceStatus), nullable=False)
    response_time = db.Column(db.Float)  # in seconds
    error_message = db.Column(db.Text)
    checked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    service = db.relationship('ServiceEntry', backref=db.backref('checks', lazy=True, order_by='ServiceCheck.checked_at.desc()'))

class NotificationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service_entry.id'), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # email, slack, etc.
    recipient = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255))
    message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    
    # Relationship
    service = db.relationship('ServiceEntry', backref=db.backref('notifications', lazy=True))
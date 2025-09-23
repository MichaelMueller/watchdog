import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any
import logging
from models import db, NotificationLog, ServiceEntry

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending notifications about service status changes."""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, from_email: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
    
    def send_email(self, to_email: str, subject: str, message: str, service_id: int = None) -> bool:
        """Send email notification."""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            # Log successful notification
            if service_id:
                log = NotificationLog(
                    service_id=service_id,
                    notification_type='email',
                    recipient=to_email,
                    subject=subject,
                    message=message,
                    success=True
                )
                db.session.add(log)
                db.session.commit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to send email to {to_email}: {str(e)}"
            logger.error(error_msg)
            
            # Log failed notification
            if service_id:
                log = NotificationLog(
                    service_id=service_id,
                    notification_type='email',
                    recipient=to_email,
                    subject=subject,
                    message=message,
                    success=False,
                    error_message=str(e)
                )
                db.session.add(log)
                db.session.commit()
            
            return False
    
    def send_service_down_notification(self, service: ServiceEntry, error_message: str) -> bool:
        """Send notification when a service goes down."""
        subject = f"Service Alert: {service.name} is DOWN"
        
        message = f"""
Service Alert: {service.name} is DOWN

Service Details:
- Name: {service.name}
- Host: {service.host}
- Port: {service.port}
- Description: {service.description}
- Error: {error_message}
- Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

Please investigate and resolve the issue as soon as possible.

--
Watchdog Service Monitor
        """.strip()
        
        return self.send_email(service.admin_email, subject, message, service.id)
    
    def send_service_recovery_notification(self, service: ServiceEntry) -> bool:
        """Send notification when a service recovers."""
        subject = f"Service Recovery: {service.name} is UP"
        
        message = f"""
Service Recovery: {service.name} is now UP

Service Details:
- Name: {service.name}
- Host: {service.host}
- Port: {service.port}
- Description: {service.description}
- Recovery Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

The service has recovered and is now responding normally.

--
Watchdog Service Monitor
        """.strip()
        
        return self.send_email(service.admin_email, subject, message, service.id)
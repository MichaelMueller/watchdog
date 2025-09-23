import time
import logging
import threading
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from models import db, ServiceEntry, ServiceCheck, ServiceStatus
from service_checker import ServiceCheckerFactory
from notifications import NotificationService

logger = logging.getLogger(__name__)

class MonitoringService:
    """Background service that monitors registered services."""
    
    def __init__(self, app, notification_service: NotificationService):
        self.app = app
        self.notification_service = notification_service
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self._lock = threading.Lock()
    
    def start(self):
        """Start the monitoring service."""
        with self._lock:
            if self.is_running:
                logger.warning("Monitoring service is already running")
                return
            
            self.scheduler.start()
            self.is_running = True
            logger.info("Monitoring service started")
            
            # Schedule initial check of all services
            self._schedule_all_services()
    
    def stop(self):
        """Stop the monitoring service."""
        with self._lock:
            if not self.is_running:
                logger.warning("Monitoring service is not running")
                return
            
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Monitoring service stopped")
    
    def _schedule_all_services(self):
        """Schedule monitoring for all active services."""
        with self.app.app_context():
            services = ServiceEntry.query.all()
            for service in services:
                self._schedule_service_check(service)
    
    def _schedule_service_check(self, service: ServiceEntry):
        """Schedule periodic checks for a specific service."""
        job_id = f"service_check_{service.id}"
        
        # Remove existing job if it exists
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
        
        # Add new job
        trigger = IntervalTrigger(seconds=service.check_interval)
        self.scheduler.add_job(
            func=self._check_service,
            trigger=trigger,
            args=[service.id],
            id=job_id,
            name=f"Check service: {service.name}",
            replace_existing=True
        )
        
        logger.info(f"Scheduled checks for service '{service.name}' every {service.check_interval} seconds")
    
    def _check_service(self, service_id: int):
        """Check a specific service and handle notifications."""
        with self.app.app_context():
            try:
                service = ServiceEntry.query.get(service_id)
                if not service:
                    logger.error(f"Service with ID {service_id} not found")
                    return
                
                # Create appropriate checker
                checker = ServiceCheckerFactory.create_checker(
                    service.check_type,
                    service.host,
                    service.port
                )
                
                # Perform the check
                status, response_time, error_message = checker.check()
                
                # Save the check result
                check = ServiceCheck(
                    service_id=service.id,
                    status=status,
                    response_time=response_time,
                    error_message=error_message if error_message else None
                )
                db.session.add(check)
                
                # Get previous status to detect status changes
                previous_check = ServiceCheck.query.filter_by(service_id=service.id)\
                    .filter(ServiceCheck.id != check.id)\
                    .order_by(ServiceCheck.checked_at.desc())\
                    .first()
                
                previous_status = previous_check.status if previous_check else ServiceStatus.UNKNOWN
                
                # Handle status changes
                if status != previous_status:
                    if status == ServiceStatus.DOWN:
                        logger.warning(f"Service '{service.name}' went DOWN: {error_message}")
                        self.notification_service.send_service_down_notification(service, error_message)
                    elif status == ServiceStatus.UP and previous_status == ServiceStatus.DOWN:
                        logger.info(f"Service '{service.name}' recovered")
                        self.notification_service.send_service_recovery_notification(service)
                
                db.session.commit()
                
                logger.debug(f"Checked service '{service.name}': {status.value} ({response_time:.2f}s)")
                
            except Exception as e:
                logger.error(f"Error checking service {service_id}: {str(e)}")
                db.session.rollback()
    
    def add_service(self, service: ServiceEntry):
        """Add monitoring for a new service."""
        if self.is_running:
            self._schedule_service_check(service)
    
    def update_service(self, service: ServiceEntry):
        """Update monitoring for an existing service."""
        if self.is_running:
            self._schedule_service_check(service)
    
    def remove_service(self, service_id: int):
        """Remove monitoring for a service."""
        job_id = f"service_check_{service_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed monitoring for service ID {service_id}")
    
    def get_status(self) -> dict:
        """Get the current status of the monitoring service."""
        jobs = self.scheduler.get_jobs()
        return {
            'is_running': self.is_running,
            'active_jobs': len(jobs),
            'jobs': [{'id': job.id, 'name': job.name, 'next_run': job.next_run_time} for job in jobs]
        }
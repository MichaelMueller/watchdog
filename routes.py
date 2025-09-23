from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, ServiceEntry, ServiceCheck, ServiceStatus
from forms import ServiceForm
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard showing all services."""
    services = ServiceEntry.query.filter_by(created_by=current_user.id).all()
    
    # Get latest status for each service
    service_stats = []
    for service in services:
        latest_check = ServiceCheck.query.filter_by(service_id=service.id)\
            .order_by(ServiceCheck.checked_at.desc()).first()
        
        service_stats.append({
            'service': service,
            'latest_check': latest_check,
            'status': latest_check.status if latest_check else ServiceStatus.UNKNOWN
        })
    
    return render_template('dashboard.html', service_stats=service_stats)

@main_bp.route('/services')
@login_required
def services():
    """List all services."""
    services = ServiceEntry.query.filter_by(created_by=current_user.id).all()
    return render_template('services.html', services=services)

@main_bp.route('/services/add', methods=['GET', 'POST'])
@login_required
def add_service():
    """Add a new service."""
    form = ServiceForm()
    
    if form.validate_on_submit():
        service = ServiceEntry(
            name=form.name.data,
            host=form.host.data,
            port=form.port.data,
            description=form.description.data,
            admin_email=form.admin_email.data,
            check_interval=form.check_interval.data,
            check_type=form.check_type.data,
            created_by=current_user.id
        )
        
        db.session.add(service)
        db.session.commit()
        
        # Add to monitoring service
        from flask import current_app
        monitoring_service = current_app.extensions.get('monitoring_service')
        if monitoring_service:
            monitoring_service.add_service(service)
        
        flash(f'Service "{service.name}" added successfully!', 'success')
        return redirect(url_for('main.services'))
    
    return render_template('add_service.html', form=form)

@main_bp.route('/services/<int:service_id>')
@login_required
def service_detail(service_id):
    """Show service details and check history."""
    service = ServiceEntry.query.get_or_404(service_id)
    
    # Check if user owns this service
    if service.created_by != current_user.id:
        flash('You do not have permission to view this service.', 'error')
        return redirect(url_for('main.services'))
    
    # Get recent checks (last 24 hours)
    since = datetime.utcnow() - timedelta(hours=24)
    recent_checks = ServiceCheck.query.filter_by(service_id=service.id)\
        .filter(ServiceCheck.checked_at >= since)\
        .order_by(ServiceCheck.checked_at.desc())\
        .limit(100).all()
    
    # Calculate uptime percentage
    if recent_checks:
        up_checks = [c for c in recent_checks if c.status == ServiceStatus.UP]
        uptime_percentage = (len(up_checks) / len(recent_checks)) * 100
    else:
        uptime_percentage = 0
    
    return render_template('service_detail.html', 
                         service=service, 
                         recent_checks=recent_checks,
                         uptime_percentage=uptime_percentage)

@main_bp.route('/services/<int:service_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    """Edit an existing service."""
    service = ServiceEntry.query.get_or_404(service_id)
    
    # Check if user owns this service
    if service.created_by != current_user.id:
        flash('You do not have permission to edit this service.', 'error')
        return redirect(url_for('main.services'))
    
    form = ServiceForm(obj=service)
    
    if form.validate_on_submit():
        form.populate_obj(service)
        service.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Update monitoring service
        from flask import current_app
        monitoring_service = current_app.extensions.get('monitoring_service')
        if monitoring_service:
            monitoring_service.update_service(service)
        
        flash(f'Service "{service.name}" updated successfully!', 'success')
        return redirect(url_for('main.service_detail', service_id=service.id))
    
    return render_template('edit_service.html', form=form, service=service)

@main_bp.route('/services/<int:service_id>/delete', methods=['POST'])
@login_required
def delete_service(service_id):
    """Delete a service."""
    service = ServiceEntry.query.get_or_404(service_id)
    
    # Check if user owns this service
    if service.created_by != current_user.id:
        flash('You do not have permission to delete this service.', 'error')
        return redirect(url_for('main.services'))
    
    # Remove from monitoring service
    from flask import current_app
    monitoring_service = current_app.extensions.get('monitoring_service')
    if monitoring_service:
        monitoring_service.remove_service(service.id)
    
    # Delete service and all associated checks
    ServiceCheck.query.filter_by(service_id=service.id).delete()
    db.session.delete(service)
    db.session.commit()
    
    flash(f'Service "{service.name}" deleted successfully!', 'success')
    return redirect(url_for('main.services'))

@main_bp.route('/api/services/<int:service_id>/check')
@login_required
def manual_check(service_id):
    """Manually trigger a service check."""
    service = ServiceEntry.query.get_or_404(service_id)
    
    # Check if user owns this service
    if service.created_by != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        from service_checker import ServiceCheckerFactory
        
        checker = ServiceCheckerFactory.create_checker(
            service.check_type,
            service.host,
            service.port
        )
        
        status, response_time, error_message = checker.check()
        
        # Save the check result
        check = ServiceCheck(
            service_id=service.id,
            status=status,
            response_time=response_time,
            error_message=error_message if error_message else None
        )
        db.session.add(check)
        db.session.commit()
        
        return jsonify({
            'status': status.value,
            'response_time': response_time,
            'error_message': error_message,
            'checked_at': check.checked_at.isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/monitoring/status')
@login_required
def monitoring_status():
    """Get monitoring service status."""
    from flask import current_app
    monitoring_service = current_app.extensions.get('monitoring_service')
    
    if monitoring_service:
        status = monitoring_service.get_status()
        return jsonify(status)
    else:
        return jsonify({'error': 'Monitoring service not available'}), 503
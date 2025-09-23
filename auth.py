from flask import Blueprint, request, redirect, url_for, session, flash
from flask_login import login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from models import db, User
import json

auth_bp = Blueprint('auth', __name__)

def init_oauth(app):
    oauth = OAuth(app)
    
    oauth.register(
        name='microsoft',
        client_id=app.config['OAUTH_CLIENT_ID'],
        client_secret=app.config['OAUTH_CLIENT_SECRET'],
        server_metadata_url=app.config['OAUTH_DISCOVERY_URL'],
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    
    return oauth

@auth_bp.route('/login')
def login():
    from flask import current_app
    oauth = current_app.extensions.get('authlib.integrations.flask_client')
    if not oauth:
        flash('OAuth not configured', 'error')
        return redirect(url_for('main.index'))
    
    microsoft = oauth.create_client('microsoft')
    redirect_uri = url_for('auth.callback', _external=True)
    return microsoft.authorize_redirect(redirect_uri)

@auth_bp.route('/callback')
def callback():
    from flask import current_app
    oauth = current_app.extensions.get('authlib.integrations.flask_client')
    if not oauth:
        flash('OAuth not configured', 'error')
        return redirect(url_for('main.index'))
    
    microsoft = oauth.create_client('microsoft')
    token = microsoft.authorize_access_token()
    user_info = token.get('userinfo')
    
    if user_info:
        # Get or create user
        user = User.query.filter_by(id=user_info['sub']).first()
        if not user:
            user = User(
                id=user_info['sub'],
                email=user_info['email'],
                name=user_info['name']
            )
            db.session.add(user)
            db.session.commit()
        else:
            # Update user info
            user.email = user_info['email']
            user.name = user_info['name']
            db.session.commit()
        
        login_user(user)
        flash(f'Welcome, {user.name}!', 'success')
        return redirect(url_for('main.dashboard'))
    
    flash('Login failed', 'error')
    return redirect(url_for('main.index'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))
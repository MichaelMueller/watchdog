# Watchdog Service Monitor

A comprehensive web application for monitoring services with automated health checks, notifications, and Microsoft Office 365 SSO authentication.

## Features

- **Secure Authentication**: OpenID Connect integration with Microsoft Office 365
- **Service Management**: Add, edit, and delete monitored services (IP/DNS, port, descriptions)
- **Multiple Check Types**: TCP port checks, HTTP/HTTPS health checks
- **Automated Monitoring**: Background daemon with configurable check intervals
- **Email Notifications**: Automatic alerts when services go down or recover
- **Web Dashboard**: Real-time service status and monitoring history
- **Extensible Architecture**: Abstract service checker pattern for custom implementations

## Quick Start

### Prerequisites

- Python 3.8+
- Microsoft Azure AD application for OAuth2 authentication
- SMTP server credentials for email notifications

### Installation

1. Clone the repository:
```bash
git clone https://github.com/MichaelMueller/watchdog.git
cd watchdog
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Run the application:
```bash
python app.py
```

The application will be available at http://localhost:5000

### Configuration

Copy `.env.example` to `.env` and configure:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///watchdog.db

# OAuth2 Configuration (Microsoft Office 365)
OAUTH_CLIENT_ID=your-azure-app-client-id
OAUTH_CLIENT_SECRET=your-azure-app-client-secret

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@domain.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@domain.com

# Monitoring Configuration
DEFAULT_CHECK_INTERVAL=300
```

### Microsoft Azure AD Setup

1. Go to Azure Portal > Azure Active Directory > App registrations
2. Create a new application registration
3. Add redirect URI: `https://your-domain.com/auth/callback`
4. Copy the Application (client) ID and create a client secret
5. Configure API permissions for OpenID Connect

## Usage

### Adding Services

1. Login with your Microsoft account
2. Click "Add Service" on the dashboard
3. Configure:
   - Service name and description
   - Host (IP address or domain name)
   - Port number
   - Check type (TCP, HTTP, HTTPS)
   - Admin email for notifications
   - Check interval (30-86400 seconds)

### Monitoring

The application automatically monitors services in the background:

- Performs health checks at configured intervals
- Sends email notifications when services go down
- Sends recovery notifications when services come back up
- Maintains check history and uptime statistics

### Service Check Types

#### TCP Check
- Tests basic TCP connectivity to a port
- Best for: Database servers, SSH, custom protocols

#### HTTP Check
- Performs HTTP GET request to service
- Returns UP for 2xx-3xx response codes
- Best for: Web applications, REST APIs

#### HTTPS Check
- Same as HTTP but with SSL/TLS
- Best for: Secure web applications

## Architecture

### Core Components

1. **Flask Web Application** (`app.py`)
   - Main application factory and configuration
   - Route registration and middleware setup

2. **Authentication System** (`auth.py`)
   - OpenID Connect integration
   - User session management
   - Microsoft Office 365 SSO

3. **Service Management** (`routes.py`)
   - CRUD operations for services
   - Dashboard and monitoring views
   - Manual service checking API

4. **Service Checkers** (`service_checker.py`)
   - Abstract base class for extensible checks
   - TCP, HTTP, and HTTPS implementations
   - Factory pattern for checker creation

5. **Monitoring Service** (`monitoring.py`)
   - Background daemon using APScheduler
   - Automated service checking
   - Status change detection

6. **Notification System** (`notifications.py`)
   - SMTP email notifications
   - Service down/recovery alerts
   - Notification logging

7. **Database Models** (`models.py`)
   - User management
   - Service configuration
   - Check history and notifications

### Database Schema

- **User**: OAuth user information and admin status
- **ServiceEntry**: Service configuration and metadata
- **ServiceCheck**: Individual check results and timing
- **NotificationLog**: Notification history and delivery status

## Deployment

### Development
```bash
python app.py
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn --workers 4 --bind 0.0.0.0:8000 wsgi:app
```

### Docker
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:app"]
```

### Service/Daemon Setup

For running the monitoring service as a system service, create a systemd service file:

```ini
[Unit]
Description=Watchdog Service Monitor
After=network.target

[Service]
Type=simple
User=watchdog
WorkingDirectory=/opt/watchdog
ExecStart=/opt/watchdog/venv/bin/gunicorn --bind 0.0.0.0:8000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## Extending Service Checkers

To add custom service checks, extend the `ServiceChecker` abstract class:

```python
from service_checker import ServiceChecker
from models import ServiceStatus
from typing import Tuple

class MyCustomChecker(ServiceChecker):
    def check(self) -> Tuple[ServiceStatus, float, str]:
        start_time = time.time()
        try:
            # Your custom check logic here
            # Return ServiceStatus.UP or ServiceStatus.DOWN
            response_time = time.time() - start_time
            return ServiceStatus.UP, response_time, ""
        except Exception as e:
            response_time = time.time() - start_time
            return ServiceStatus.DOWN, response_time, str(e)
```

Then update the `ServiceCheckerFactory` to include your new checker.

## Security

- All authentication is handled via Microsoft OAuth2
- Session management with Flask-Login
- CSRF protection on all forms
- Input validation and sanitization
- SQL injection protection via SQLAlchemy

## License

Licensed under the Apache License 2.0. See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and feature requests, please use the GitHub issue tracker.

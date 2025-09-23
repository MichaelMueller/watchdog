#!/usr/bin/env python3
"""
Production WSGI entry point for the Watchdog application.
Use with Gunicorn or other WSGI servers.
"""
from app import create_app
import os

app, monitoring_service = create_app()

# Start monitoring service in production
if not app.debug:
    monitoring_service.start()

if __name__ == "__main__":
    # For development only
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
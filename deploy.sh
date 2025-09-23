#!/bin/bash
# Simple deployment script for Watchdog Service Monitor

set -e

echo "🐕 Watchdog Service Monitor Deployment Script"
echo "=============================================="

# Check if Python 3.8+ is available
python_version=$(python3 --version | cut -d ' ' -f 2 | cut -d '.' -f 1-2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8 or higher is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "✏️  Please edit .env file with your configuration before running the application!"
fi

# Initialize database (if needed)
echo "🗄️  Initializing database..."
python3 -c "
from app import create_app
app, _ = create_app()
with app.app_context():
    from models import db
    db.create_all()
    print('Database initialized successfully')
"

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your OAuth and SMTP configuration"
echo "2. For development: python app.py"
echo "3. For production: gunicorn --bind 0.0.0.0:8000 wsgi:app"
echo ""
echo "Visit http://localhost:5000 (development) or http://localhost:8000 (production)"
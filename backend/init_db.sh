#!/bin/bash

echo "🚀 Smart Bus Management System - Database Initialization"
echo "========================================================"

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements_updated.txt

# Run migrations
echo "🔨 Initializing database..."
python migrations.py

# Create uploads directory
mkdir -p uploads

echo ""
echo "✅ Database initialization complete!"
echo ""
echo "To start the server, run:"
echo "   python app_updated.py"
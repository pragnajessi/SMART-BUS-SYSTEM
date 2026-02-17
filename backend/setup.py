#!/usr/bin/env python
"""
Smart Bus Management System - Setup Script
Initialize the database and install dependencies
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a shell command"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        return False


def main():
    print("\n" + "="*60)
    print("🚀 Smart Bus Management System - Setup")
    print("="*60)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists('venv'):
        print("\n📦 Creating virtual environment...")
        os.system('python -m venv venv')
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment already exists")
    
    # Install requirements
    if not run_command(
        f'pip install -r requirements_updated.txt',
        'Installing Python dependencies'
    ):
        sys.exit(1)
    
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('backups', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    print("✅ Created necessary directories")
    
    # Initialize database
    print("\n" + "="*60)
    print("🗄️  Initializing Database")
    print("="*60)
    
    try:
        from app import app, init_db
        with app.app_context():
            init_db()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)
    
    # Summary
    print("\n" + "="*60)
    print("✅ Setup completed successfully!")
    print("="*60)
    print("\n📋 Next steps:")
    print("   1. Update .env file with your configuration")
    print("   2. Run: python app.py")
    print("   3. API will be available at: http://localhost:5000")
    print("\n📚 Documentation:")
    print("   - Database: DATABASE_README.md")
    print("   - API: See routes in app.py")
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    main()
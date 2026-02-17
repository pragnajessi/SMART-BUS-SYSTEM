import os
from datetime import timedelta

class DatabaseConfig:
    """Database configuration"""
    
    # SQLite
    SQLITE_DB = 'sqlite:///smart_bus_management.db'
    
    # PostgreSQL (for production)
    POSTGRESQL_DB = 'postgresql://user:password@localhost:5432/smart_bus_db'
    
    # MySQL
    MYSQL_DB = 'mysql+pymysql://user:password@localhost:3306/smart_bus_db'
    
    @staticmethod
    def get_database_url():
        """Get database URL based on environment"""
        env = os.environ.get('FLASK_ENV', 'development')
        db_type = os.environ.get('DB_TYPE', 'sqlite')
        
        if db_type == 'postgresql':
            return os.environ.get('DATABASE_URL', DatabaseConfig.POSTGRESQL_DB)
        elif db_type == 'mysql':
            return os.environ.get('DATABASE_URL', DatabaseConfig.MYSQL_DB)
        else:
            return DatabaseConfig.SQLITE_DB


class AppConfig:
    """Application configuration"""
    
    # Database
    SQLALCHEMY_DATABASE_URI = DatabaseConfig.get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO', 'False') == 'True'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'localhost:3000')
    
    # Upload
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # JWT
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Pagination
    ITEMS_PER_PAGE = 10


class DevelopmentConfig(AppConfig):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(AppConfig):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(AppConfig):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
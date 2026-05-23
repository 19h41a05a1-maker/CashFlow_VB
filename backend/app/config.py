"""
Application Configuration Management
Handles development, staging, and production configurations
"""

import os
from datetime import timedelta

from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    Configuration can be overridden via .env files or environment variables.
    """
    
    # Application
    APP_NAME: str = "Cash Management - 5 Days Hold Checking System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # API Configuration
    API_VERSION: str = "v1"
    API_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = "sqlite:///./cash_management.db"
    SQLALCHEMY_ECHO: bool = False
    SQLALCHEMY_POOL_SIZE: int = 10
    SQLALCHEMY_POOL_RECYCLE: int = 3600
    SQLALCHEMY_POOL_PRE_PING: bool = True
    
    # JWT & Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password Configuration
    PASSWORD_MIN_LENGTH: int = 12
    PASSWORD_HASH_ROUNDS: int = 12
    
    # Session Configuration
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_SESSION_DURATION_HOURS: int = 8
    MAX_CONCURRENT_SESSIONS: int = 3
    
    # Business Configuration
    HOLD_PERIOD_DAYS: int = 5
    MAX_TRANSACTION_AMOUNT: float = 1000000.00
    MIN_TRANSACTION_AMOUNT: float = 0.01
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 10000
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100
    LOGIN_RATE_LIMIT_PER_HOUR: int = 10
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE_PATH: str = "logs/app.log"
    LOG_MAX_SIZE_MB: int = 100
    LOG_BACKUP_COUNT: int = 30
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        """Pydantic v1 configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


class DevelopmentSettings(Settings):
    """Development environment settings."""
    
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SQLALCHEMY_ECHO: bool = True
    LOG_LEVEL: str = "DEBUG"
    DATABASE_URL: str = "sqlite:///./cash_management_dev.db"


class StagingSettings(Settings):
    """Staging environment settings."""
    
    ENVIRONMENT: str = "staging"
    DEBUG: bool = False
    SQLALCHEMY_ECHO: bool = False
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "sqlite:///./cash_management_staging.db"


class ProductionSettings(Settings):
    """Production environment settings."""
    
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    SQLALCHEMY_ECHO: bool = False
    LOG_LEVEL: str = "WARNING"
    DATABASE_URL: str = "sqlite:///./cash_management.db"


def get_settings() -> Settings:
    """
    Get settings instance based on environment.
    
    Returns:
        Settings: Configuration object for the current environment
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "staging":
        return StagingSettings()
    else:
        return DevelopmentSettings()


# Global settings instance
settings = get_settings()

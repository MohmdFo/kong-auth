"""
Configuration management for Kong Auth Service
Centralizes environment variables and provides type-safe configuration
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Service Configuration
    SERVICE_NAME: str = Field(default="kong-auth", env="SERVICE_NAME")
    APP_RELEASE: str = Field(default="1.0.0", env="APP_RELEASE")
    
    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Sentry Configuration
    SENTRY_ENABLED: bool = Field(default=False, env="SENTRY_ENABLED")
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    SENTRY_ENV: str = Field(default="development", env="SENTRY_ENV")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(default=1.0, env="SENTRY_TRACES_SAMPLE_RATE")
    SENTRY_PROFILES_SAMPLE_RATE: float = Field(default=1.0, env="SENTRY_PROFILES_SAMPLE_RATE")
    
    # Kong Configuration
    KONG_ADMIN_URL: str = Field(default="http://localhost:8001", env="KONG_ADMIN_URL")
    JWT_EXPIRATION_SECONDS: int = Field(default=31536000, env="JWT_EXPIRATION_SECONDS")
    
    # Casdoor Configuration
    CASDOOR_ENDPOINT: str = Field(default="https://iam.ai-lab.ir", env="CASDOOR_ENDPOINT")
    CASDOOR_CLIENT_ID: str = Field(default="f83fb202807419aee818", env="CASDOOR_CLIENT_ID")
    CASDOOR_CLIENT_SECRET: str = Field(default="33189aeb03ec21c7fe65ab0d9b00f4ba198bc640", env="CASDOOR_CLIENT_SECRET")
    CASDOOR_ORG_NAME: str = Field(default="built-in", env="CASDOOR_ORG_NAME")
    CASDOOR_APP_NAME: str = Field(default="app-built-in", env="CASDOOR_APP_NAME")
    CASDOOR_CERT_PATH: str = Field(default="casdoor_cert.pem", env="CASDOOR_CERT_PATH")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    LOGS_DIR: str = Field(default="logs", env="LOGS_DIR")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    RELOAD: bool = Field(default=False, env="RELOAD")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() in ["production", "prod"]
    
    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment"""
        return self.ENVIRONMENT.lower() in ["staging", "stage"]
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() in ["development", "dev"]
    
    @property
    def should_send_default_pii(self) -> bool:
        """Determine if PII should be sent to Sentry based on environment"""
        return not self.is_production


# Global settings instance
settings = Settings()

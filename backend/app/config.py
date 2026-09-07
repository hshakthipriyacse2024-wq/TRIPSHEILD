"""Configuration settings for TripShield AI backend."""
import os

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel as BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./tripshield.db')
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'tripshield-secret-key-change-in-production')
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    CORS_ORIGINS: list = ['http://localhost:3000', 'http://127.0.0.1:3000']
    AI_PROVIDER: str = 'mock'
    LOG_LEVEL: str = 'INFO'

settings = Settings()

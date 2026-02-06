#config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./the_vault.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Argon2
    ARGON2_TIME_COST: int = 2
    ARGON2_MEMORY_COST: int = 65536
    ARGON2_PARALLELISM: int = 1
    ARGON2_HASH_LENGTH: int = 32
    ARGON2_SALT_LENGTH: int = 16
    
    # Rate Limiting
    REDIS_URL: Optional[str] = None  # Use None for in-memory storage
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_TIMEFRAME_MINUTES: int = 15
    BLOCK_DURATION_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
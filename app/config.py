"""
Application configuration
Manages all environment variables and settings
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str = "sqlite:///./test.db"
    
    # JWT
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Application
    app_name: str = "Storage Rental Users Service"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:8080"
    
    # Other Services
    facilities_service_url: str = "http://localhost:8001"
    orders_service_url: str = "http://localhost:8002"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    @property
    def origins_list(self) -> List[str]:
        """Convert comma-separated origins to list"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()

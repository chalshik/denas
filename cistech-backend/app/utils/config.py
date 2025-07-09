from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/cistech_marketplace"
    
    # Firebase
    firebase_service_account_key: str = "config/cistech-kg-firebase-adminsdk-fbsvc-bd761a39b2.json"
    
    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_verify_service_sid: str = ""
    
    # Application
    app_name: str = "CisTech Marketplace API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Security
    cors_origins: str = "*"
    allowed_hosts: str = "*"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert cors_origins string to list"""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        """Convert allowed_hosts string to list"""
        if self.allowed_hosts == "*":
            return ["*"]
        return [host.strip() for host in self.allowed_hosts.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"

@lru_cache()
def get_settings():
    return Settings() 
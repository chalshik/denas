import os
from typing import Optional
from pydantic_settings import BaseSettings


def get_env_file() -> str:
    """
    Determine which environment file to use based on environment variables
    Priority: DB_ENV > ENVIRONMENT > default to local
    """
    # Check for specific database environment override
    db_env = os.getenv("DB_ENV", "").lower()
    if db_env in ["local", "supabase", "production"]:
        return f"env/.env.{db_env}"
    
    # Check general environment setting
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if environment == "production":
        return "env/.env.production"
    
    # Default to local for development
    return "env/.env.local"


class Settings(BaseSettings):
    PROJECT_NAME: str = "Denas Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "denas_db")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    # You can also directly use DATABASE_URL if provided
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # Supabase Storage Configuration
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    SUPABASE_STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET", "product-images")
    
    @property
    def database_url(self) -> str:
        # Use DATABASE_URL if provided, otherwise construct from components
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def current_env_file(self) -> str:
        """Return the current environment file being used"""
        return get_env_file()
    
    @property
    def has_supabase_storage(self) -> bool:
        """Check if Supabase storage is properly configured"""
        return bool(self.SUPABASE_URL and self.SUPABASE_SERVICE_ROLE_KEY and self.SUPABASE_STORAGE_BUCKET)
    
    class Config:
        env_file = get_env_file()
        case_sensitive = True
        extra = "ignore"


settings = Settings() 
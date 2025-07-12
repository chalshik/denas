from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.api.v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FastAPI Backend with PostgreSQL and Alembic",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
# Configure allowed origins based on environment
if settings.is_production:
    # Production: specify exact origins
    allowed_origins = [
        "https://your-frontend-domain.com",  # Replace with your actual frontend domain
        "https://www.your-frontend-domain.com",  # Replace with your actual frontend domain
    ]
else:
    # Development: allow localhost and common dev ports
    allowed_origins = [
        "http://localhost:3000",  # Next.js default dev port
        "http://localhost:3001",  # Alternative dev port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,  # Required for cookies
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to Denas Backend API"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    return {
        "status": "healthy", 
        "database": "connected",
        "environment": settings.ENVIRONMENT,
        "env_file": settings.current_env_file,
        "database_host": settings.POSTGRES_HOST,
        "firebase_configured": settings.has_firebase_config
    } 
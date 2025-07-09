from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import os
import logging
from dotenv import load_dotenv

# Import app components
from app.database import engine, Base
from app.api.routers.auth import router as auth_router
from app.api.routers.vendor import router as vendor_router
from app.api.routers.admin import router as admin_router
from app.api.routers.product import router as product_router
from app.api.routers.public_product import router as public_product_router
from app.api.routers.variation import router as variation_router
from app.api.routers.metadata import router as metadata_router
from app.api.routers.favorites import router as favorite_router
from app.api.routers.basket import router as basket_router

from app.utils.config import get_settings
# Import all models to ensure they are registered with SQLAlchemy
import app.models

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Multi-vendor marketplace API with Firebase authentication and SMS verification",
    version=settings.app_version,
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.allowed_hosts_list
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000", "http://127.0.0.1:8000", "https://cistech.store", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(vendor_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(product_router, prefix="/api/v1")
app.include_router(public_product_router, prefix="/api/v1")
app.include_router(variation_router, prefix="/api/v1")
app.include_router(metadata_router, prefix="/api/v1")
app.include_router(favorite_router, prefix="/api/v1")
app.include_router(basket_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "CisTech Marketplace API is running!", 
        "version": settings.app_version,
        "auth_method": "Firebase Authentication with SMS verification",
        "endpoints": {
            "auth": "/auth/",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "auth_flow": "Frontend handles Firebase authentication, backend validates tokens"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": settings.app_name,
        "version": settings.app_version,
        "auth_method": "Firebase with Twilio SMS"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error", 
            "message": str(exc) if settings.debug else "Something went wrong"
        }
    )

# Server startup

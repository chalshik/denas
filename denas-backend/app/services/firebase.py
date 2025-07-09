# auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth, credentials
import firebase_admin
import os
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_firebase():
    """Initialize Firebase Admin SDK with multi-environment support"""
    try:
        # Check if Firebase app is already initialized
        firebase_admin.get_app()
        logger.info("Firebase app already initialized")
    except ValueError:
        # Initialize Firebase app
        try:
            # Check environment type
            is_cloud_run = os.getenv("K_SERVICE") is not None
            is_gcp = os.getenv("GOOGLE_CLOUD_PROJECT") is not None or os.getenv("GCP_PROJECT") is not None
            
            if is_cloud_run or is_gcp:
                logger.info("Detected Google Cloud environment")
                # Use Application Default Credentials for cloud deployment
                project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
                if project_id:
                    cred = credentials.ApplicationDefault()
                    firebase_admin.initialize_app(cred, {'projectId': project_id})
                    logger.info(f"Firebase initialized with ADC for project: {project_id}")
                else:
                    cred = credentials.ApplicationDefault()
                    firebase_admin.initialize_app(cred)
                    logger.info("Firebase initialized with ADC")
                return
            
            # For local development, try service account key first
            service_account_path = "denas-20261-firebase-adminsdk-fbsvc-3d5c2b4e73.json"
            if os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                logger.info(f"Firebase initialized with service account: {service_account_path}")
                return
                
            # Try GOOGLE_APPLICATION_CREDENTIALS environment variable
            google_creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if google_creds_path and os.path.exists(google_creds_path):
                cred = credentials.Certificate(google_creds_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized with GOOGLE_APPLICATION_CREDENTIALS")
                return
            
            # Fallback to Application Default Credentials
            try:
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized with ADC fallback")
                return
            except Exception as adc_error:
                logger.warning(f"ADC fallback failed: {adc_error}")
            
            raise ValueError("No valid Firebase credentials found")
            
        except Exception as init_error:
            logger.error(f"Failed to initialize Firebase: {init_error}")
            raise init_error

# Initialize Firebase on import
initialize_firebase()

# Security scheme
security = HTTPBearer()

class FirebaseService:
    """Firebase Authentication Service - focused only on token validation"""
    
    @staticmethod
    async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
        """
        Verify Firebase JWT token and return user UID
        Returns: firebase_uid
        """
        try:
            token = credentials.credentials
            logger.debug(f"Verifying Firebase token, length: {len(token)}")
            
            # Verify the token with Firebase Admin SDK
            decoded_token = auth.verify_id_token(token)
            firebase_uid = decoded_token.get("uid")
            
            if not firebase_uid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            
            logger.debug(f"Token verified successfully for user: {firebase_uid}")
            return firebase_uid
            
        except auth.InvalidIdTokenError:
            logger.error("Invalid Firebase ID token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except auth.ExpiredIdTokenError:
            logger.error("Expired Firebase ID token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    async def verify_token_optional(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
    ) -> Optional[str]:
        """
        Optional token verification - returns None if no token provided or invalid
        Returns: firebase_uid or None
        """
        if not credentials:
            return None
        
        try:
            return await FirebaseService.verify_token(credentials)
        except HTTPException:
            return None

# Authentication Dependencies
async def get_current_user_uid(firebase_uid: str = Depends(FirebaseService.verify_token)) -> str:
    """
    Get current user's Firebase UID from verified token
    Returns: firebase_uid
    """
    return firebase_uid

async def get_current_user_uid_optional(
    firebase_uid: Optional[str] = Depends(FirebaseService.verify_token_optional)
) -> Optional[str]:
    """
    Optional authentication - returns None if no token provided or invalid
    Returns: firebase_uid or None
    """
    return firebase_uid

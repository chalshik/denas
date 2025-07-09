from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth, credentials
import firebase_admin
import os
import logging
from typing import Optional
from app.services.firebase_service import FirebaseService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
def initialize_firebase():
    try:
        # Check if Firebase app is already initialized
        firebase_admin.get_app()
        logger.info("Firebase app already initialized")
    except ValueError:
        # Initialize Firebase app optimized for Google Cloud Run
        try:
            # Check if running on Google Cloud
            is_cloud_run = os.getenv("K_SERVICE") is not None
            is_gcp = os.getenv("GOOGLE_CLOUD_PROJECT") is not None or os.getenv("GCP_PROJECT") is not None
            
            if is_cloud_run:
                logger.info("Detected Google Cloud Run environment")
            elif is_gcp:
                logger.info("Detected Google Cloud Platform environment")
            
            # Method 1: Application Default Credentials (Priority for Cloud Run)
            # This uses the service account attached to the Cloud Run service
            if is_cloud_run or is_gcp:
                try:
                    # For Cloud Run, we can specify the project ID explicitly
                    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
                    if project_id:
                        cred = credentials.ApplicationDefault()
                        firebase_admin.initialize_app(cred, {
                            'projectId': project_id
                        })
                        logger.info(f"Firebase initialized with Application Default Credentials for project: {project_id}")
                    else:
                        cred = credentials.ApplicationDefault()
                        firebase_admin.initialize_app(cred)
                        logger.info("Firebase initialized with Application Default Credentials")
                    return
                except Exception as adc_error:
                    logger.warning(f"Application Default Credentials failed: {adc_error}")
            

            # Method 3: GOOGLE_APPLICATION_CREDENTIALS (for local development)
            google_creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if google_creds_path and os.path.exists(google_creds_path):
                cred = credentials.Certificate(google_creds_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized with GOOGLE_APPLICATION_CREDENTIALS")
                return
            
            # Method 4: Try Application Default Credentials as fallback (for any environment)
            if not is_cloud_run and not is_gcp:
                try:
                    cred = credentials.ApplicationDefault()
                    firebase_admin.initialize_app(cred)
                    logger.info("Firebase initialized with Application Default Credentials (fallback)")
                    return
                except Exception as adc_error:
                    logger.warning(f"Application Default Credentials fallback failed: {adc_error}")
            
            # If all methods fail, provide specific guidance
            if is_cloud_run:
                error_msg = """
                Firebase initialization failed in Cloud Run environment.
                Please ensure:
                1. Your Cloud Run service has a service account attached
                2. The service account has Firebase Admin SDK permissions
                3. Or set FIREBASE_SERVICE_ACCOUNT_KEY_JSON environment variable with service account JSON
                """
            else:
                error_msg = """
                No valid Firebase credentials found. For Cloud Run deployment:
                1. Attach a service account with Firebase permissions to your Cloud Run service
                2. Or set FIREBASE_SERVICE_ACCOUNT_KEY_JSON environment variable
                3. Or set GOOGLE_APPLICATION_CREDENTIALS for local development
                """
            
            raise ValueError(error_msg.strip())
            
        except Exception as init_error:
            logger.error(f"Failed to initialize Firebase: {init_error}")
            raise init_error

# Initialize Firebase on import
initialize_firebase()

# Security scheme
security = HTTPBearer()

class FirebaseAuthMiddleware:
    """Firebase Authentication Middleware"""
    
    @staticmethod
    async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
        """
        Verify Firebase JWT token and return decoded token
        """
        try:
            # Extract token from Authorization header
            token = credentials.credentials
            logger.info(f"Verifying Firebase token, length: {len(token)}")
            
            # Verify the token with Firebase Admin SDK
            decoded_token = auth.verify_id_token(token)
            logger.info(f"Token verified successfully for user: {decoded_token.get('uid')}")
            
            return decoded_token
            
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

async def get_current_user(token_data: dict = Depends(FirebaseAuthMiddleware.verify_token)) -> str:
    """
    Get current user's Firebase UID from verified token
    """
    firebase_uid = token_data.get("uid")
    if not firebase_uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    return firebase_uid

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[str]:
    """
    Optional authentication - returns None if no token provided
    """
    if not credentials:
        return None
    
    try:
        decoded_token = await FirebaseAuthMiddleware.verify_token(credentials)
        return decoded_token.get("uid")
    except HTTPException:
        return None

# New functions for role-based authentication
async def get_current_user_with_role(token_data: dict = Depends(FirebaseAuthMiddleware.verify_token)) -> tuple[str, dict]:
    """
    Get current user's Firebase UID and custom claims from verified token
    Returns: (firebase_uid, custom_claims)
    """
    firebase_uid = token_data.get("uid")
    if not firebase_uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get custom claims from token
    custom_claims = {
        "user_type": token_data.get("user_type", "USER"),
        "vendor_status": token_data.get("vendor_status"),
        "permissions": token_data.get("permissions", [])
    }
    
    logger.info(f"User {firebase_uid} has claims: {custom_claims}")
    return firebase_uid, custom_claims

async def require_vendor_role(user_data: tuple = Depends(get_current_user_with_role)) -> tuple[str, dict]:
    """
    Require VENDOR role - raises 403 if user is not a vendor
    Returns: (firebase_uid, custom_claims)
    """
    firebase_uid, custom_claims = user_data
    user_type = custom_claims.get("user_type", "USER")
    
    if user_type != "VENDOR":
        logger.warning(f"Access denied for user {firebase_uid}: not a vendor (type: {user_type})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Vendor role required."
        )
    
    return firebase_uid, custom_claims

async def require_approved_vendor(user_data: tuple = Depends(require_vendor_role)) -> tuple[str, dict]:
    """
    Require APPROVED vendor status - raises 403 if vendor is not approved
    Returns: (firebase_uid, custom_claims)
    """
    firebase_uid, custom_claims = user_data
    vendor_status = custom_claims.get("vendor_status", "PENDING")
    
    if vendor_status != "APPROVED":
        logger.warning(f"Access denied for vendor {firebase_uid}: status {vendor_status}, need APPROVED")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Vendor approval required. Current status: {vendor_status}"
        )
    
    return firebase_uid, custom_claims

async def get_user_role(token_data: dict = Depends(FirebaseAuthMiddleware.verify_token)) -> str:
    """
    Get user role from token
    Returns: user_type (USER, VENDOR, ADMIN)
    """
    return token_data.get("user_type", "USER")

async def is_vendor(token_data: dict = Depends(FirebaseAuthMiddleware.verify_token)) -> bool:
    """
    Check if user is a vendor
    Returns: True if user is vendor, False otherwise
    """
    user_type = token_data.get("user_type", "USER")
    return user_type == "VENDOR"

async def is_approved_vendor(token_data: dict = Depends(FirebaseAuthMiddleware.verify_token)) -> bool:
    """
    Check if user is an approved vendor
    Returns: True if user is approved vendor, False otherwise
    """
    user_type = token_data.get("user_type", "USER")
    vendor_status = token_data.get("vendor_status", "PENDING")
    return user_type == "VENDOR" and vendor_status == "APPROVED"

# Add these functions to your existing middleware file

async def require_superadmin_role(user_data: tuple = Depends(get_current_user_with_role)) -> tuple[str, dict]:
    """
    Require SUPERADMIN role - raises 403 if user is not a superadmin
    Returns: (firebase_uid, custom_claims)
    """
    firebase_uid, custom_claims = user_data
    user_type = custom_claims.get("user_type", "USER")
    
    if user_type != "SUPERADMIN":
        logger.warning(f"Access denied for user {firebase_uid}: not a superadmin (type: {user_type})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Super admin role required."
        )
    
    return firebase_uid, custom_claims

async def require_admin_or_superadmin_role(user_data: tuple = Depends(get_current_user_with_role)) -> tuple[str, dict]:
    """
    Require ADMIN or SUPERADMIN role - raises 403 if user is neither
    Returns: (firebase_uid, custom_claims)
    """
    firebase_uid, custom_claims = user_data
    user_type = custom_claims.get("user_type", "USER")
    
    if user_type not in ["ADMIN", "SUPERADMIN"]:
        logger.warning(f"Access denied for user {firebase_uid}: not an admin (type: {user_type})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    
    return firebase_uid, custom_claims

def check_admin_permission(required_permission: str):
    """
    Decorator factory for checking specific admin permissions
    """
    async def permission_checker(user_data: tuple = Depends(require_admin_or_superadmin_role)) -> tuple[str, dict]:
        firebase_uid, custom_claims = user_data
        user_type = custom_claims.get("user_type", "USER")
        
        # Get permissions based on user type
        permissions = await FirebaseService.get_admin_permissions(firebase_uid)
        
        if not permissions.get(required_permission, False):
            logger.warning(f"Permission denied for user {firebase_uid}: missing {required_permission}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. {required_permission} permission required."
            )
        
        return firebase_uid, custom_claims
    
    return permission_checker

# Specific permission checkers for easy use
require_user_management = check_admin_permission("can_manage_users")
require_vendor_management = check_admin_permission("can_manage_vendors")
require_product_management = check_admin_permission("can_manage_products")
require_admin_management = check_admin_permission("can_manage_admins") 
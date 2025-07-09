from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import (
    PhoneVerificationRequest, 
    PhoneVerificationResponse,
    VerifyPhoneRequest,
    VerifyPhoneResponse,
    CompleteProfileRequest,
    CompleteProfileResponse,
    CheckUserRequest,
    CheckUserResponse
)
from app.schemas.vendor import ApplyVendorRequest, ApplyVendorResponse
from app.schemas.user import UserResponse
from app.services.twilio_service import TwilioService
from app.services.firebase_service import FirebaseService
from app.services.auth_service import AuthService
from app.middleware.firebase_auth import get_current_user
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Initialize services
twilio_service = TwilioService()

@router.post("/request-verification", response_model=PhoneVerificationResponse)
async def request_phone_verification(
    request: PhoneVerificationRequest,
    db: Session = Depends(get_db)
) -> PhoneVerificationResponse:
    """
    Send SMS verification code to phone number (only if user doesn't exist)
    """
    try:
        # First check if user already exists
        user = await AuthService.get_user_by_phone(db, request.phone)
        if user is not None:
            return PhoneVerificationResponse(
                success=False,
                message="Пользователь с таким номером уже существует. Попробуйте войти.",
                verification_sid=None
            )
        
        # Send SMS only if user doesn't exist
        success, message, verification_sid = await twilio_service.send_verification_code(
            request.phone
        )
        
        return PhoneVerificationResponse(
            success=success,
            message=message,
            verification_sid=verification_sid
        )
        
    except Exception as e:
        logger.error(f"Error in request verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification code"
        )

@router.post("/verify-phone", response_model=VerifyPhoneResponse)
async def verify_phone_number(
    request: VerifyPhoneRequest,
    db: Session = Depends(get_db)
) -> VerifyPhoneResponse:
    """
    Verify SMS code and create/get Firebase user
    """
    try:
        # First verify the SMS code with Twilio
        sms_success, sms_message = await twilio_service.verify_code(
            request.phone, 
            request.verification_code
        )
        
        if not sms_success:
            return VerifyPhoneResponse(
                success=False,
                message=sms_message,
                firebase_token=None,
                user_exists=False
            )
        
        # Check if user already exists in our database
        user = await AuthService.get_user_by_phone(db, request.phone)
        user_exists = user is not None
        
        # Create or get Firebase user with password
        firebase_success, firebase_message, firebase_uid = await FirebaseService.create_user_with_phone_and_password(
            request.phone, request.password
        )
        
        if not firebase_success:
            return VerifyPhoneResponse(
                success=False,
                message=firebase_message,
                firebase_token=None,
                user_exists=user_exists
            )
        
        # Create custom token for the user
        token_success, token_message, custom_token = await FirebaseService.create_custom_token(
            firebase_uid
        )
        
        if not token_success:
            return VerifyPhoneResponse(
                success=False,
                message=token_message,
                firebase_token=None,
                user_exists=user_exists
            )
        
        return VerifyPhoneResponse(
            success=True,
            message="Phone verification successful",
            firebase_token=custom_token,
            user_exists=user_exists
        )
        
    except Exception as e:
        logger.error(f"Error in verify phone: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Phone verification failed"
        )

@router.post("/complete-profile", response_model=CompleteProfileResponse)
async def complete_user_profile(
    request: CompleteProfileRequest,
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user)
) -> CompleteProfileResponse:
    """
    Complete user profile after phone verification (requires Firebase token)
    """
    try:
        # Check if user already exists
        existing_user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
        
        if existing_user:
            # Update existing user profile
            success, message, user = await AuthService.update_user_profile(
                db, existing_user, request
            )
        else:
            # Get phone number from Firebase
            from firebase_admin import auth
            firebase_user = auth.get_user(firebase_uid)
            
            if not firebase_user.phone_number:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number not found in Firebase user"
                )
            
            # Create new user
            success, message, user = await AuthService.create_user(
                db, firebase_uid, firebase_user.phone_number, request
            )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return CompleteProfileResponse(
            success=True,
            message=message,
            user_id=user.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete profile"
        )

@router.post("/apply-vendor", response_model=ApplyVendorResponse)
async def apply_for_vendor(
    request: ApplyVendorRequest,
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user)
) -> ApplyVendorResponse:
    """
    Apply to become a vendor (requires Firebase token)
    """
    try:
        # Get current user or create if doesn't exist
        user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
        if not user:
            # Get phone number from Firebase
            from firebase_admin import auth as firebase_auth
            try:
                firebase_user = firebase_auth.get_user(firebase_uid)
                phone_number = firebase_user.phone_number
                
                if not phone_number:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Phone number not found in Firebase user. Please complete your profile first."
                    )
                
                # Create user with minimal profile data
                from app.schemas.auth import CompleteProfileRequest
                minimal_profile = CompleteProfileRequest(
                    first_name="User",  # Will be updated later
                    last_name="User",   # Will be updated later
                    email=firebase_user.email
                )
                
                success, message, user = await AuthService.create_user(
                    db, firebase_uid, phone_number, minimal_profile
                )
                
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to create user: {message}"
                    )
                    
            except Exception as e:
                logger.error(f"Error creating user for vendor application: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user profile"
                )
        
        # Create vendor application
        success, message, vendor_profile = await AuthService.apply_for_vendor(
            db, user, request
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Update Firebase custom claims
        await FirebaseService.update_user_claims(firebase_uid, {
            "user_type": "VENDOR",
            "vendor_status": vendor_profile.status.value
        })
        
        return ApplyVendorResponse(
            success=True,
            message=message,
            vendor_profile_id=vendor_profile.id,
            status=vendor_profile.status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying for vendor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit vendor application"
        )

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user)
) -> UserResponse:
    """
    Get current user profile (requires Firebase token)
    """
    try:
        user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=user.id,
            firebase_uid=user.firebase_uid,
            phone=user.phone,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            user_type=user.user_type,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )

@router.get("/debug/claims")
async def get_user_claims_debug(
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Debug endpoint to check current user's Firebase claims
    """
    try:
        success, message, claims = await FirebaseService.get_user_claims(firebase_uid)
        
        # Also get user from database
        user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
        vendor_profile = None
        
        if user:
            from app.models.vendor_profile import VendorProfile
            vendor_profile = db.query(VendorProfile).filter(VendorProfile.user_id == user.id).first()
        
        return {
            "firebase_uid": firebase_uid,
            "firebase_claims": claims if success else None,
            "claims_error": message if not success else None,
            "database_user": {
                "id": user.id if user else None,
                "user_type": user.user_type.value if user else None,
                "phone": user.phone if user else None
            } if user else None,
            "vendor_profile": {
                "id": vendor_profile.id if vendor_profile else None,
                "status": vendor_profile.status.value if vendor_profile else None,
                "business_type": vendor_profile.business_type if vendor_profile else None
            } if vendor_profile else None
        }
        
    except Exception as e:
        logger.error(f"Error in debug claims: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug error: {str(e)}"
        )

@router.post("/debug/set-vendor-claims")
async def set_vendor_claims_debug(
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Debug endpoint to manually set vendor claims for current user
    WARNING: This is for development/testing only
    """
    try:
        # Check if user has vendor profile in database
        user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in database"
            )
        
        from app.models.vendor_profile import VendorProfile
        vendor_profile = db.query(VendorProfile).filter(VendorProfile.user_id == user.id).first()
        
        if not vendor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No vendor profile found. Please apply to become a vendor first."
            )
        
        # Set Firebase claims
        success, message = await FirebaseService.set_vendor_status(
            firebase_uid, 
            vendor_profile.status.value
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to set Firebase claims: {message}"
            )
        
        return {
            "success": True,
            "message": "Vendor claims set successfully",
            "firebase_uid": firebase_uid,
            "vendor_status": vendor_profile.status.value,
            "user_type": "VENDOR"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting vendor claims: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set vendor claims: {str(e)}"
        )

@router.post("/check-user", response_model=CheckUserResponse)
async def check_user_exists(
    request: CheckUserRequest,
    db: Session = Depends(get_db)
) -> CheckUserResponse:
    """
    Check if user exists with given phone number
    """
    try:
        # Check if user exists in our database
        user = await AuthService.get_user_by_phone(db, request.phone_number)
        user_exists = user is not None
        
        if user_exists:
            return CheckUserResponse(
                exists=True,
                message="Пользователь с таким номером уже существует. Войдите в аккаунт."
            )
        else:
            return CheckUserResponse(
                exists=False,
                message="Пользователь не найден. Можно зарегистрироваться."
            )
        
    except Exception as e:
        logger.error(f"Error checking user existence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check user existence"
        ) 
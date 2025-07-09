from firebase_admin import auth
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class FirebaseService:
    """Service for handling Firebase authentication operations"""
    
    @staticmethod
    async def create_user_with_phone(phone_number: str) -> Tuple[bool, str, Optional[str]]:
        """
        Create a Firebase user with phone number (deprecated - use create_user_with_phone_and_password)
        Returns: (success, message, firebase_uid)
        """
        try:
            # Create user with phone number
            user_record = auth.create_user(
                phone_number=phone_number
            )
            
            logger.info(f"Firebase user created: {user_record.uid}")
            return True, "User created successfully", user_record.uid
            
        except auth.PhoneNumberAlreadyExistsError:
            logger.warning(f"Phone number already exists: {phone_number}")
            try:
                # Get existing user by phone
                user_record = auth.get_user_by_phone_number(phone_number)
                return True, "User already exists", user_record.uid
            except Exception as e:
                logger.error(f"Error getting existing user: {str(e)}")
                return False, "Failed to retrieve user", None
                
        except Exception as e:
            logger.error(f"Error creating Firebase user: {str(e)}")
            return False, f"Failed to create user: {str(e)}", None
    
    @staticmethod
    async def create_user_with_phone_and_password(phone_number: str, password: str) -> Tuple[bool, str, Optional[str]]:
        """
        Create a Firebase user with phone number and password
        Sets phone number as email for login compatibility
        Returns: (success, message, firebase_uid)
        """
        try:
            # Create user with phone number and password
            # Use phone number with @phone.local domain as email for login compatibility
            phone_email = f"{phone_number.replace('+', '').replace(' ', '')}@phone.local"
            
            user_record = auth.create_user(
                phone_number=phone_number,
                email=phone_email,
                password=password,
                email_verified=True  # Mark as verified since we verified via SMS
            )
            
            logger.info(f"Firebase user created with phone+password: {user_record.uid}")
            return True, "User created successfully", user_record.uid
            
        except auth.PhoneNumberAlreadyExistsError:
            logger.warning(f"Phone number already exists: {phone_number}")
            try:
                # Get existing user by phone
                user_record = auth.get_user_by_phone_number(phone_number)
                return True, "User already exists", user_record.uid
            except Exception as e:
                logger.error(f"Error getting existing user: {str(e)}")
                return False, "Failed to retrieve user", None
                
        except Exception as e:
            logger.error(f"Error creating Firebase user with password: {str(e)}")
            return False, f"Failed to create user: {str(e)}", None
    
    @staticmethod
    async def get_user_by_phone(phone_number: str) -> Tuple[bool, str, Optional[str]]:
        """
        Get user by phone number
        Returns: (success, message, firebase_uid)
        """
        try:
            user_record = auth.get_user_by_phone_number(phone_number)
            return True, "User found", user_record.uid
        except auth.UserNotFoundError:
            return False, "User not found", None
        except Exception as e:
            logger.error(f"Error getting user by phone: {str(e)}")
            return False, f"Error retrieving user: {str(e)}", None
    
    @staticmethod
    async def create_custom_token(firebase_uid: str) -> Tuple[bool, str, Optional[str]]:
        """
        Create a custom token for user
        Returns: (success, message, custom_token)
        """
        try:
            custom_token = auth.create_custom_token(firebase_uid)
            return True, "Token created successfully", custom_token.decode('utf-8')
        except Exception as e:
            logger.error(f"Error creating custom token: {str(e)}")
            return False, f"Failed to create token: {str(e)}", None
    
    @staticmethod
    async def update_user_claims(firebase_uid: str, claims: dict) -> Tuple[bool, str]:
        """
        Update user's custom claims
        Returns: (success, message)
        """
        try:
            auth.set_custom_user_claims(firebase_uid, claims)
            logger.info(f"Updated claims for user {firebase_uid}: {claims}")
            return True, "Claims updated successfully"
        except Exception as e:
            logger.error(f"Error updating user claims: {str(e)}")
            return False, f"Failed to update claims: {str(e)}"
    
    @staticmethod
    def phone_to_email(phone_number: str) -> str:
        """
        Convert phone number to email format for Firebase login
        Example: +1234567890 -> 1234567890@phone.local
        """
        return f"{phone_number.replace('+', '').replace(' ', '').replace('-', '')}@phone.local"

    @staticmethod
    async def set_user_role(firebase_uid: str, user_type: str) -> Tuple[bool, str]:
        """
        Set user role (USER, VENDOR, ADMIN)
        Returns: (success, message)
        """
        try:
            claims = {"user_type": user_type}
            auth.set_custom_user_claims(firebase_uid, claims)
            logger.info(f"Set user role for {firebase_uid}: {user_type}")
            return True, f"User role set to {user_type}"
        except Exception as e:
            logger.error(f"Error setting user role: {str(e)}")
            return False, f"Failed to set user role: {str(e)}"

    @staticmethod
    async def set_vendor_status(firebase_uid: str, vendor_status: str) -> Tuple[bool, str]:
        """
        Set vendor status (PENDING, APPROVED, REJECTED)
        Returns: (success, message)
        """
        try:
            # Get current claims
            user = auth.get_user(firebase_uid)
            current_claims = user.custom_claims or {}
            
            # Update claims with new vendor status
            claims = {
                **current_claims,
                "user_type": "VENDOR",
                "vendor_status": vendor_status
            }
            
            auth.set_custom_user_claims(firebase_uid, claims)
            logger.info(f"Set vendor status for {firebase_uid}: {vendor_status}")
            return True, f"Vendor status set to {vendor_status}"
        except Exception as e:
            logger.error(f"Error setting vendor status: {str(e)}")
            return False, f"Failed to set vendor status: {str(e)}"

    @staticmethod
    async def approve_vendor(firebase_uid: str) -> Tuple[bool, str]:
        """
        Approve vendor (set status to APPROVED)
        Returns: (success, message)
        """
        return await FirebaseService.set_vendor_status(firebase_uid, "APPROVED")

    @staticmethod
    async def reject_vendor(firebase_uid: str) -> Tuple[bool, str]:
        """
        Reject vendor (set status to REJECTED)
        Returns: (success, message)
        """
        return await FirebaseService.set_vendor_status(firebase_uid, "REJECTED")

    @staticmethod
    async def revoke_vendor_access(firebase_uid: str) -> Tuple[bool, str]:
        """
        Revoke vendor access (set back to USER)
        Returns: (success, message)
        """
        try:
            claims = {"user_type": "USER"}
            auth.set_custom_user_claims(firebase_uid, claims)
            logger.info(f"Revoked vendor access for {firebase_uid}")
            return True, "Vendor access revoked"
        except Exception as e:
            logger.error(f"Error revoking vendor access: {str(e)}")
            return False, f"Failed to revoke vendor access: {str(e)}"

    @staticmethod
    async def get_user_claims(firebase_uid: str) -> Tuple[bool, str, dict]:
        """
        Get user's custom claims
        Returns: (success, message, claims)
        """
        try:
            user = auth.get_user(firebase_uid)
            claims = user.custom_claims or {}
            return True, "Claims retrieved successfully", claims
        except Exception as e:
            logger.error(f"Error getting user claims: {str(e)}")
            return False, f"Failed to get claims: {str(e)}", {}

    @staticmethod
    async def is_user_vendor(firebase_uid: str) -> bool:
        """
        Check if user is a vendor
        Returns: True if vendor, False otherwise
        """
        try:
            success, _, claims = await FirebaseService.get_user_claims(firebase_uid)
            if success:
                return claims.get("user_type") == "VENDOR"
            return False
        except Exception:
            return False

    @staticmethod
    async def is_vendor_approved(firebase_uid: str) -> bool:
        """
        Check if vendor is approved
        Returns: True if approved vendor, False otherwise
        """
        try:
            success, _, claims = await FirebaseService.get_user_claims(firebase_uid)
            if success:
                return (claims.get("user_type") == "VENDOR" and 
                       claims.get("vendor_status") == "APPROVED")
            return False
        except Exception:
            return False

    @staticmethod
    async def set_admin_role(firebase_uid: str, admin_type: str = "ADMIN") -> Tuple[bool, str]:
        """
        Set user as admin (ADMIN or SUPERADMIN)
        Returns: (success, message)
        """
        try:
            if admin_type not in ["ADMIN", "SUPERADMIN"]:
                return False, "Invalid admin type. Must be ADMIN or SUPERADMIN"
            
            claims = {
                "user_type": admin_type,
                "admin_level": admin_type,
                "created_at": auth.get_user(firebase_uid).user_metadata.creation_timestamp
            }
            
            auth.set_custom_user_claims(firebase_uid, claims)
            logger.info(f"Set admin role for {firebase_uid}: {admin_type}")
            return True, f"User promoted to {admin_type}"
        except Exception as e:
            logger.error(f"Error setting admin role: {str(e)}")
            return False, f"Failed to set admin role: {str(e)}"

    @staticmethod
    async def revoke_admin_access(firebase_uid: str) -> Tuple[bool, str]:
        """
        Revoke admin access (set back to USER)
        Returns: (success, message)
        """
        try:
            claims = {"user_type": "USER"}
            auth.set_custom_user_claims(firebase_uid, claims)
            logger.info(f"Revoked admin access for {firebase_uid}")
            return True, "Admin access revoked"
        except Exception as e:
            logger.error(f"Error revoking admin access: {str(e)}")
            return False, f"Failed to revoke admin access: {str(e)}"

    @staticmethod
    async def is_user_admin(firebase_uid: str) -> bool:
        """
        Check if user is admin (ADMIN or SUPERADMIN)
        Returns: boolean
        """
        try:
            user = auth.get_user(firebase_uid)
            claims = user.custom_claims or {}
            user_type = claims.get("user_type", "USER")
            return user_type in ["ADMIN", "SUPERADMIN"]
        except Exception as e:
            logger.error(f"Error checking admin status: {str(e)}")
            return False

    @staticmethod
    async def is_user_superadmin(firebase_uid: str) -> bool:
        """
        Check if user is superadmin
        Returns: boolean
        """
        try:
            user = auth.get_user(firebase_uid)
            claims = user.custom_claims or {}
            return claims.get("user_type") == "SUPERADMIN"
        except Exception as e:
            logger.error(f"Error checking superadmin status: {str(e)}")
            return False

    @staticmethod
    async def get_admin_permissions(firebase_uid: str) -> dict:
        """
        Get admin permissions based on user type
        Returns: permissions dictionary
        """
        try:
            user = auth.get_user(firebase_uid)
            claims = user.custom_claims or {}
            user_type = claims.get("user_type", "USER")
            
            if user_type == "SUPERADMIN":
                return {
                    "can_manage_users": True,
                    "can_manage_vendors": True,
                    "can_manage_products": True,
                    "can_manage_admins": True,
                    "can_view_analytics": True,
                    "can_export_data": True,
                    "can_modify_system_settings": True
                }
            elif user_type == "ADMIN":
                return {
                    "can_manage_users": False,  # Only superadmin can manage users
                    "can_manage_vendors": True,
                    "can_manage_products": True,
                    "can_manage_admins": False,
                    "can_view_analytics": True,
                    "can_export_data": True,
                    "can_modify_system_settings": False
                }
            else:
                return {
                    "can_manage_users": False,
                    "can_manage_vendors": False,
                    "can_manage_products": False,
                    "can_manage_admins": False,
                    "can_view_analytics": False,
                    "can_export_data": False,
                    "can_modify_system_settings": False
                }
        except Exception as e:
            logger.error(f"Error getting admin permissions: {str(e)}")
            return {} 
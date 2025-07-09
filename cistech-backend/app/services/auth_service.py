from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User, UserType
from app.models.vendor_profile import VendorProfile
from app.schemas.auth import CompleteProfileRequest
from app.schemas.vendor import ApplyVendorRequest
import logging
from typing import Optional, Tuple, List
import datetime
from sqlalchemy import func, and_

logger = logging.getLogger(__name__)

class AuthService:
    """Service for handling authentication and user management"""
    
    @staticmethod
    async def get_user_by_firebase_uid(db: Session, firebase_uid: str) -> Optional[User]:
        """Get user by Firebase UID"""
        return db.query(User).filter(User.firebase_uid == firebase_uid).first()
    
    @staticmethod
    async def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
        """Get user by phone number"""
        return db.query(User).filter(User.phone == phone).first()
    
    @staticmethod
    async def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    async def create_user(
        db: Session, 
        firebase_uid: str, 
        phone: str, 
        profile_data: CompleteProfileRequest
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Create a new user in the database
        Returns: (success, message, user)
        """
        try:
            # Check if user already exists
            existing_user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
            if existing_user:
                return False, "User already exists", None
            
            # Check if phone number is already used
            phone_user = await AuthService.get_user_by_phone(db, phone)
            if phone_user:
                return False, "Phone number already registered", None
            
            # Create new user
            user = User(
                firebase_uid=firebase_uid,
                phone=phone,
                first_name=profile_data.first_name,
                last_name=profile_data.last_name,
                email=profile_data.email,
                user_type=UserType.USER
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"User created successfully: {user.id}")
            return True, "User created successfully", user
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error creating user: {str(e)}")
            return False, "User with this information already exists", None
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            return False, f"Failed to create user: {str(e)}", None
    
    @staticmethod
    async def update_user_profile(
        db: Session,
        user: User,
        profile_data: CompleteProfileRequest
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Update existing user profile
        Returns: (success, message, user)
        """
        try:
            user.first_name = profile_data.first_name
            user.last_name = profile_data.last_name
            user.email = profile_data.email
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"User profile updated: {user.id}")
            return True, "Profile updated successfully", user
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user profile: {str(e)}")
            return False, f"Failed to update profile: {str(e)}", None
    
    @staticmethod
    async def apply_for_vendor(
        db: Session,
        user: User,
        vendor_data: ApplyVendorRequest
    ) -> Tuple[bool, str, Optional[VendorProfile]]:
        """
        Create vendor application
        Returns: (success, message, vendor_profile)
        """
        try:
            # Check if user already has a vendor profile
            existing_profile = db.query(VendorProfile).filter(VendorProfile.user_id == user.id).first()
            if existing_profile:
                return False, "User already has a vendor application", None
            
            # Create vendor profile
            vendor_profile = VendorProfile(
                user_id=user.id,
                business_type=vendor_data.business_type,
                business_name=vendor_data.business_name,
                organization_name=vendor_data.organization_name,
                legal_form=vendor_data.legal_form,
                inn=vendor_data.inn,
                registration_country=vendor_data.registration_country,
                registration_date=vendor_data.registration_date,
                passport_front_url=vendor_data.passport_front_url,
                passport_back_url=vendor_data.passport_back_url
            )
            
            db.add(vendor_profile)
            
            # Update user type to VENDOR
            user.user_type = UserType.VENDOR
            
            db.commit()
            db.refresh(vendor_profile)
            
            logger.info(f"Vendor application created: {vendor_profile.id}")
            return True, "Vendor application submitted successfully", vendor_profile
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating vendor application: {str(e)}")
            logger.error(f"Vendor data: {vendor_data}")
            logger.error(f"User data: {user.id}, {user.firebase_uid}")
            return False, f"Failed to submit vendor application: {str(e)}", None

    @staticmethod
    async def get_all_users(
        db: Session, 
        limit: Optional[int] = 100, 
        offset: Optional[int] = 0,
        user_type_filter: Optional[UserType] = None
    ) -> Tuple[List[User], int]:
        """
        Get all users with pagination and filtering
        Returns: (users_list, total_count)
        """
        try:
            query = db.query(User)
            
            # Apply user type filter if provided
            if user_type_filter:
                query = query.filter(User.user_type == user_type_filter)
            
            # Get total count before pagination
            total_count = query.count()
            
            # Apply pagination
            users = query.offset(offset).limit(limit).all()
            
            return users, total_count
            
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            raise e

    @staticmethod
    async def get_user_stats(db: Session) -> dict:
        """
        Get user statistics for the admin dashboard.
        """
        try:
            total_users = db.query(User).count()
            total_vendors = db.query(User).filter(User.user_type == UserType.VENDOR).count()
            total_admins = db.query(User).filter(User.user_type.in_([UserType.ADMIN, UserType.SUPERADMIN])).count()

            # New users this month
            current_month = datetime.datetime.utcnow().month
            current_year = datetime.datetime.utcnow().year
            new_users_this_month = db.query(User).filter(
                and_(
                    func.extract('month', User.created_at) == current_month,
                    func.extract('year', User.created_at) == current_year
                )
            ).count()
            
            # NOTE: "active_users" is a placeholder for now. 
            # This would typically be defined by recent login activity, which we aren't tracking yet.
            active_users = total_users 

            return {
                "total_users": total_users,
                "total_vendors": total_vendors,
                "total_admins": total_admins,
                "new_users_this_month": new_users_this_month,
                "active_users": active_users
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return {
                "total_users": 0, "total_vendors": 0, "total_admins": 0,
                "new_users_this_month": 0, "active_users": 0
            }

    @staticmethod
    async def update_user_type(
        db: Session, 
        user_id: int, 
        new_user_type: UserType
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Update user type (admin only)
        Returns: (success, message, user)
        """
        try:
            user = await AuthService.get_user_by_id(db, user_id)
            if not user:
                return False, "User not found", None
            
            # Prevent creating superadmin through API (should be done manually)
            if new_user_type == UserType.SUPERADMIN:
                return False, "Cannot create SUPERADMIN users through API", None
            
            old_type = user.user_type
            user.user_type = new_user_type
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"User {user_id} type changed from {old_type} to {new_user_type}")
            return True, f"User type updated to {new_user_type.value}", user
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user type: {str(e)}")
            return False, f"Failed to update user type: {str(e)}", None

    @staticmethod
    async def delete_user(db: Session, user_id: int) -> Tuple[bool, str]:
        """
        Delete user (admin only) - soft delete by setting user_type to INACTIVE
        Returns: (success, message)
        """
        try:
            user = await AuthService.get_user_by_id(db, user_id)
            if not user:
                return False, "User not found"
            
            if user.user_type == UserType.SUPERADMIN:
                return False, "Cannot delete SUPERADMIN users"
            
            # For now, we'll actually delete the user
            # In production, you might want to implement soft delete
            db.delete(user)
            db.commit()
            
            logger.info(f"User {user_id} deleted successfully")
            return True, "User deleted successfully"
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting user: {str(e)}")
            return False, f"Failed to delete user: {str(e)}"

    @staticmethod
    async def search_users(
        db: Session,
        search_term: str,
        limit: Optional[int] = 50
    ) -> List[User]:
        """
        Search users by phone, email, first_name, or last_name
        Returns: list of matching users
        """
        try:
            search_pattern = f"%{search_term}%"
            
            users = db.query(User).filter(
                (User.phone.ilike(search_pattern)) |
                (User.email.ilike(search_pattern)) |
                (User.first_name.ilike(search_pattern)) |
                (User.last_name.ilike(search_pattern))
            ).limit(limit).all()
            
            return users
            
        except Exception as e:
            logger.error(f"Error searching users: {str(e)}")
            return [] 
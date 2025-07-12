from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User, UserRole
import logging
from typing import Optional, List
import datetime
from sqlalchemy import func, and_

logger = logging.getLogger(__name__)

class UserService:
    """Service for handling user management operations"""
    
    @staticmethod
    async def get_user_by_uid(db: Session, uid: str) -> Optional[User]:
        """Get user by Firebase UID"""
        return db.query(User).filter(User.uid == uid).first()
    
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
        uid: str, 
        phone: str,
        role: UserRole = UserRole.USER
    ) -> User:
        """
        Create a new user in the database
        Returns: created user
        Raises: IntegrityError if user already exists
        """
        try:
            user = User(
                uid=uid,
                phone=phone,
                role=role
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"User created successfully: {user.id} with UID: {uid}")
            return user
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error creating user: {str(e)}")
            raise e
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise e
    
    @staticmethod
    async def get_or_create_user(
        db: Session,
        uid: str,
        phone: str
    ) -> User:
        """
        Get existing user or create new user if doesn't exist
        Returns: user (existing or newly created)
        """
        try:
            # Try to find existing user
            user = await UserService.get_user_by_uid(db, uid)
            
            if user:
                logger.info(f"Existing user found: {user.id} with UID: {uid}")
                return user
            else:
                # User doesn't exist - create new user
                user = await UserService.create_user(db, uid, phone)
                logger.info(f"New user created: {user.id} with UID: {uid}")
                return user
                    
        except Exception as e:
            logger.error(f"Error in get_or_create_user: {str(e)}")
            raise e
    
    @staticmethod
    async def update_user_role(
        db: Session, 
        user_id: int, 
        new_role: UserRole
    ) -> User:
        """
        Update user role
        Returns: updated user
        Raises: ValueError if user not found
        """
        try:
            user = await UserService.get_user_by_id(db, user_id)
            if not user:
                raise ValueError("User not found")
            
            old_role = user.role
            user.role = new_role
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"User {user_id} role changed from {old_role} to {new_role}")
            return user
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user role: {str(e)}")
            raise e

    @staticmethod
    async def delete_user(db: Session, user_id: int) -> None:
        """
        Delete user
        Raises: ValueError if user not found
        """
        try:
            user = await UserService.get_user_by_id(db, user_id)
            if not user:
                raise ValueError("User not found")
            
            db.delete(user)
            db.commit()
            
            logger.info(f"User {user_id} deleted successfully")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting user: {str(e)}")
            raise e

    @staticmethod
    async def get_all_users(
        db: Session, 
        limit: Optional[int] = 100, 
        offset: Optional[int] = 0,
        role_filter: Optional[UserRole] = None
    ) -> tuple[List[User], int]:
        """
        Get all users with pagination and filtering
        Returns: (users_list, total_count)
        """
        try:
            query = db.query(User)
            
            # Apply role filter if provided
            if role_filter:
                query = query.filter(User.role == role_filter)
            
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
            total_admins = db.query(User).filter(User.role.in_([UserRole.ADMIN, UserRole.MANAGER])).count()
            regular_users = db.query(User).filter(User.role == UserRole.USER).count()

            # New users this month
            current_month = datetime.datetime.utcnow().month
            current_year = datetime.datetime.utcnow().year
            new_users_this_month = db.query(User).filter(
                and_(
                    func.extract('month', User.created_at) == current_month,
                    func.extract('year', User.created_at) == current_year
                )
            ).count()
            
            return {
                "total_users": total_users,
                "regular_users": regular_users,
                "total_admins": total_admins,
                "new_users_this_month": new_users_this_month,
                "active_users": total_users  # Placeholder - could be enhanced with actual activity tracking
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return {
                "total_users": 0, "regular_users": 0, "total_admins": 0,
                "new_users_this_month": 0, "active_users": 0
            }

    @staticmethod
    async def search_users(
        db: Session,
        search_term: str,
        limit: Optional[int] = 50
    ) -> List[User]:
        """
        Search users by phone or UID
        """
        try:
            search_pattern = f"%{search_term}%"
            
            users = db.query(User).filter(
                (User.phone.ilike(search_pattern)) |
                (User.uid.ilike(search_pattern))
            ).limit(limit).all()
            
            return users
            
        except Exception as e:
            logger.error(f"Error searching users: {str(e)}")
            raise e

from typing import Optional
from sqlalchemy.orm import Session

from app.models.vendor_profile import VendorProfile
from app.services.auth_service import AuthService


async def get_vendor_profile_id_from_firebase_uid(db: Session, firebase_uid: str) -> Optional[int]:
    """Get vendor profile ID from Firebase UID"""
    # Step 1: Get user by Firebase UID
    user = await AuthService.get_user_by_firebase_uid(db, firebase_uid)
    if not user:
        return None
    
    # Step 2: Get vendor profile using user ID
    vendor_profile = db.query(VendorProfile).filter(VendorProfile.user_id == user.id).first()
    if not vendor_profile:
        return None
    
    return vendor_profile.id
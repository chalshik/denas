import logging
from sqlalchemy.orm import Session
from app.models.vendor_profile import VendorProfile, VendorStatus
from app.models.user import User, UserType
import datetime
from sqlalchemy import func, and_

logger = logging.getLogger(__name__)

class VendorService:

    @staticmethod
    async def get_vendor_stats(db: Session) -> dict:
        """
        Get vendor statistics for the admin dashboard.
        """
        try:
            total_vendors = db.query(VendorProfile).count()
            pending_vendors = db.query(VendorProfile).filter(VendorProfile.status == VendorStatus.PENDING).count()
            approved_vendors = db.query(VendorProfile).filter(VendorProfile.status == VendorStatus.APPROVED).count()
            rejected_vendors = db.query(VendorProfile).filter(VendorProfile.status == VendorStatus.REJECTED).count()

            current_month = datetime.datetime.utcnow().month
            current_year = datetime.datetime.utcnow().year
            new_applications_this_month = db.query(VendorProfile).filter(
                and_(
                    func.extract('month', VendorProfile.created_at) == current_month,
                    func.extract('year', VendorProfile.created_at) == current_year
                )
            ).count()

            return {
                "total_vendors": total_vendors,
                "pending_vendors": pending_vendors,
                "approved_vendors": approved_vendors,
                "rejected_vendors": rejected_vendors,
                "new_applications_this_month": new_applications_this_month,
            }
        except Exception as e:
            logger.error(f"Error getting vendor stats: {str(e)}")
            return {
                "total_vendors": 0, "pending_vendors": 0, "approved_vendors": 0,
                "rejected_vendors": 0, "new_applications_this_month": 0
            } 
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.user import UserType
from app.models.vendor_profile import VendorStatus
from app.schemas.user import UserListResponse
from app.schemas.vendor import VendorProfileResponse

class UserStats(BaseModel):
    total_users: int
    total_vendors: int
    total_admins: int
    new_users_this_month: int
    active_users: int

class VendorStats(BaseModel):
    total_vendors: int
    pending_vendors: int
    approved_vendors: int
    rejected_vendors: int
    new_applications_this_month: int

class TopCategory(BaseModel):
    category_name: str
    product_count: int

class ProductStats(BaseModel):
    total_products: int
    pending_products: int
    approved_products: int
    rejected_products: int
    new_products_this_month: int
    top_categories: List[TopCategory]

class AdminDashboardStats(BaseModel):
    """Complete dashboard statistics for admin"""
    users: UserStats
    vendors: VendorStats
    products: ProductStats
    # recent_activity: List[dict] = [] # Optional: for future use

class AdminUserManagement(BaseModel):
    """User management data for admin"""
    id: int
    firebase_uid: str
    phone: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    user_type: UserType
    created_at: str
    total_products: int = 0
    total_orders: int = 0
    vendor_status: Optional[VendorStatus] = None

class AdminActivityLog(BaseModel):
    """Activity log entry for admin tracking"""
    id: int
    admin_id: int
    action: str
    target_type: str  # 'user', 'vendor', 'product'
    target_id: int
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    
class AdminPermissions(BaseModel):
    """Admin permissions schema"""
    can_manage_users: bool = True
    can_manage_vendors: bool = True
    can_manage_products: bool = True
    can_manage_admins: bool = False  # Only superadmin
    can_view_analytics: bool = True
    can_export_data: bool = True

class AdminProfile(BaseModel):
    """Extended admin profile information"""
    user: UserListResponse
    permissions: AdminPermissions
    created_at: datetime
    last_login: Optional[datetime] = None
    login_count: int = 0

class AdminProductSummary(BaseModel):
    """Product summary for admin"""
    id: int
    name: str
    vendor_name: str
    vendor_id: int
    status: str
    price: float
    created_at: str
    category: Optional[str] = None 
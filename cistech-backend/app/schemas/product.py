from enum import Enum as PyEnum
from pydantic import BaseModel, Field, field_validator, computed_field
from typing import Optional, List, Union, Dict, Any
from datetime import datetime

class ProductStatus(str, PyEnum):
    draft = 'draft'
    pending = 'pending'
    approved = 'approved'
    rejected = 'rejected'

# Base schemas
class CategoryBase(BaseModel):
    name: str

class CategoryResponse(CategoryBase):
    id: int
    class Config:
        from_attributes = True

# User response for vendor profile
class UserResponse(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    
    class Config:
        from_attributes = True

# Vendor profile response for products
class ProductVendorProfileResponse(BaseModel):
    id: int
    user_id: int
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    status: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    description: Optional[str] = None
    user: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True

class ImageBase(BaseModel):
    url: str
    alt_text: Optional[str] = None
    order: Optional[int] = 0

class ProductImageResponse(ImageBase):
    id: int
    product_id: int
    class Config:
        from_attributes = True

class VariationImageResponse(ImageBase):
    id: int
    variation_id: int
    class Config:
        from_attributes = True

class FilterOptionResponse(BaseModel):
    id: int
    value: str
    filter_type: Optional[Dict[str, Any]] = None

class FilterTypeResponse(BaseModel):
    id: int
    options: List[FilterOptionResponse]

class CategoryFiltersResponse(BaseModel):
    id: int
    filters: Dict[str, FilterTypeResponse]

class MetadataResponse(BaseModel):
    data: Dict[str, CategoryFiltersResponse]

# Enhanced characteristic schemas - using names instead of IDs
class CharacteristicInput(BaseModel):
    type_name: str  # e.g., "Size", "Color"
    value: str      # e.g., "Large", "Red"

class CharacteristicResponse(BaseModel):
    id: int
    characteristic_type_id: int
    value: str
    type_name: str = ""
    type: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Enhanced variation schemas
class VariationImageInput(BaseModel):
    url: str
    alt_text: Optional[str] = None
    order: Optional[int] = 0

class VariationInput(BaseModel):
    name: str
    price: float
    sku: Optional[str] = None
    status: Optional[ProductStatus] = ProductStatus.approved  # Changed to approved as default
    quantity: Optional[int] = 0
    characteristics: Optional[List[CharacteristicInput]] = []
    images: Optional[List[VariationImageInput]] = []

class VariationResponse(BaseModel):
    id: int
    product_id: int
    name: str
    price: float
    sku: Optional[str] = None
    status: ProductStatus
    quantity: int
    created_at: str
    characteristics: List[CharacteristicResponse] = []
    images: List[VariationImageResponse] = []
    
    @field_validator('created_at', mode='before')
    @classmethod
    def serialize_datetime(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v
    
    class Config:
        from_attributes = True

# Main product image input
class ProductImageInput(BaseModel):
    url: str
    alt_text: Optional[str] = None
    order: Optional[int] = 0

# Comprehensive product creation/update schema
class ProductCreateComplete(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: int  # Category must exist
    vendor_profile_id: Optional[str] = None  # Will be set from auth
    price: float  # Add price field
    status: Optional[ProductStatus] = ProductStatus.approved  # Changed to approved as default
    quantity: Optional[int] = 0
    main_image_url: Optional[str] = None
    filter_option_ids: Optional[List[int]] = []  # Filter options must exist
    images: Optional[List[ProductImageInput]] = []
    characteristics: Optional[List[CharacteristicInput]] = []  # Add characteristics
    variations: Optional[List[VariationInput]] = []

class ProductUpdateComplete(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[float] = None  # Add price field
    status: Optional[ProductStatus] = None
    quantity: Optional[int] = None
    main_image_url: Optional[str] = None
    filter_option_ids: Optional[List[int]] = None
    images: Optional[List[ProductImageInput]] = None
    characteristics: Optional[List[CharacteristicInput]] = None  # Add characteristics
    variations: Optional[List[VariationInput]] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    main_image_url: Optional[str] = None
    price: float  # Add price field
    
    class Config:
        from_attributes = True

class ProductResponseSpecific(BaseModel):
    id: int
    vendor_profile_id: int
    category_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    main_image_url: Optional[str] = None
    price: float
    status: ProductStatus
    quantity: int
    created_at: str
    updated_at: str
    category: Optional[CategoryResponse] = None
    vendor_profile: Optional[ProductVendorProfileResponse] = None
    description_images: List[ProductImageResponse] = []
    filters: List[FilterOptionResponse] = []
    characteristics: List[CharacteristicResponse] = []
    variations: List[VariationResponse] = []
    favorites_count: Optional[int] = None
    
    @field_validator('created_at', 'updated_at', mode='before')
    @classmethod
    def serialize_datetime(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v
    
    class Config:
        from_attributes = True
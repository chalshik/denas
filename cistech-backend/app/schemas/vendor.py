from pydantic import BaseModel, Field, validator, model_validator
from typing import Optional
from datetime import date
from app.models.vendor_profile import BusinessType, LegalForm, VendorStatus

class ApplyVendorRequest(BaseModel):
    business_type: BusinessType
    business_name: Optional[str] = None
    organization_name: Optional[str] = None
    legal_form: Optional[LegalForm] = None
    inn: Optional[str] = None
    registration_country: Optional[str] = None
    registration_date: Optional[date] = None
    passport_front_url: Optional[str] = Field(None, description="URL to passport front photo")
    passport_back_url: Optional[str] = Field(None, description="URL to passport back photo")
    
    @validator('inn')
    def validate_inn(cls, v, values):
        if v is not None:
            # Basic INN validation (Russian tax number)
            v = v.replace(' ', '').replace('-', '')
            if not v.isdigit():
                raise ValueError('INN must contain only digits')
            if len(v) not in [10, 12]:
                raise ValueError('INN must be 10 or 12 digits long')
        return v
    
    @model_validator(mode='after')
    def validate_business_type_requirements(cls, values):
        business_type = values.business_type if hasattr(values, 'business_type') else None
        
        if business_type == BusinessType.INDIVIDUAL:
            # INDIVIDUAL (Самозанятый) requirements
            if not values.business_name:
                raise ValueError('business_name is required for INDIVIDUAL business type')
            
        elif business_type == BusinessType.IP:
            # IP requirements
            required_fields = ['organization_name', 'inn', 'registration_country', 'registration_date']
            for field in required_fields:
                if not getattr(values, field, None):
                    raise ValueError(f'{field} is required for IP business type')
                    
        elif business_type == BusinessType.LEGAL_ENTITY:
            # LEGAL_ENTITY requirements
            required_fields = ['legal_form', 'organization_name', 'inn', 'registration_country', 'registration_date']
            for field in required_fields:
                if not getattr(values, field, None):
                    raise ValueError(f'{field} is required for LEGAL_ENTITY business type')
        
        # All business types require passport documents (optional for now)
        # if not values.passport_front_url:
        #     raise ValueError('passport_front_url is required for all business types')
        # if not values.passport_back_url:
        #     raise ValueError('passport_back_url is required for all business types')
            
        return values

class ApplyVendorResponse(BaseModel):
    success: bool
    message: str
    vendor_profile_id: int
    status: VendorStatus

class VendorProfileUpdateRequest(BaseModel):
    """Schema for updating vendor profile - only business info, not registration data"""
    business_name: Optional[str] = None
    organization_name: Optional[str] = None
    description: Optional[str] = None  # Add description field for store info
    
    @validator('business_name', 'organization_name', 'description')
    def strip_strings(cls, v):
        return v.strip() if v else v

class VendorProfileResponse(BaseModel):
    id: int
    user_id: int
    business_type: BusinessType
    business_name: Optional[str]
    organization_name: Optional[str]
    legal_form: Optional[LegalForm]
    inn: Optional[str]
    registration_country: Optional[str]
    registration_date: Optional[date]
    passport_front_url: Optional[str] = None  # Add passport photo fields for admin verification
    passport_back_url: Optional[str] = None
    status: VendorStatus
    created_at: str
    description: Optional[str] = None  # Add description field
    reject_reason: Optional[str] = None  # Add rejection reason field
    
    class Config:
        from_attributes = True 
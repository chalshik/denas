from pydantic import BaseModel, Field, validator
import phonenumbers
from typing import Optional

class PhoneVerificationRequest(BaseModel):
    phone: str = Field(..., description="Phone number in international format")
    
    @validator('phone')
    def validate_phone(cls, v):
        try:
            parsed = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError('Invalid phone number')
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except Exception:
            raise ValueError('Invalid phone number format')

class PhoneVerificationResponse(BaseModel):
    success: bool
    message: str
    verification_sid: Optional[str] = None

class VerifyPhoneRequest(BaseModel):
    phone: str = Field(..., description="Phone number in international format")
    verification_code: str = Field(..., min_length=4, max_length=10)
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    
    @validator('phone')
    def validate_phone(cls, v):
        try:
            parsed = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError('Invalid phone number')
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except Exception:
            raise ValueError('Invalid phone number format')
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for at least one digit
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        
        # Check for at least one letter
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        
        return v

class VerifyPhoneResponse(BaseModel):
    success: bool
    message: str
    firebase_token: Optional[str] = None
    user_exists: bool = False

class CompleteProfileRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

class CompleteProfileResponse(BaseModel):
    success: bool
    message: str
    user_id: int

class CheckUserRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number in international format")
    
    @validator('phone_number')
    def validate_phone(cls, v):
        try:
            parsed = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError('Invalid phone number')
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except Exception:
            raise ValueError('Invalid phone number format')

class CheckUserResponse(BaseModel):
    exists: bool
    message: str 
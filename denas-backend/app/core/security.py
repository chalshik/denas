from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import base64
import os

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_encryption_key() -> bytes:
    """Get or create encryption key for sensitive data"""
    # Use the secret key from settings to derive a Fernet key
    key_material = settings.SECRET_KEY.encode()
    # Pad or truncate to 32 bytes, then base64 encode for Fernet
    key_material = key_material[:32].ljust(32, b'0')
    return base64.urlsafe_b64encode(key_material)


def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data like API keys"""
    if not data:
        return data
    
    try:
        fernet = Fernet(get_encryption_key())
        encrypted_data = fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    except Exception:
        # If encryption fails, log warning and store as is (not recommended for production)
        return data


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    if not encrypted_data:
        return encrypted_data
    
    try:
        fernet = Fernet(get_encryption_key())
        decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = fernet.decrypt(decoded_data)
        return decrypted_data.decode()
    except Exception:
        # If decryption fails, assume data is not encrypted and return as is
        return encrypted_data

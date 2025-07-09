from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class BusinessType(enum.Enum):
    INDIVIDUAL = "INDIVIDUAL"  # Самозанятый
    IP = "IP"  # Индивидуальный предприниматель
    LEGAL_ENTITY = "LEGAL_ENTITY"  # Юридическое лицо

class VendorStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class LegalForm(enum.Enum):
    OOO = "OOO"  # Общество с ограниченной ответственностью
    AO = "AO"    # Акционерное общество
    COOPERATIVE = "COOPERATIVE"  # Кооператив
    FARM = "FARM"  # Фермерское хозяйство

class VendorProfile(Base):
    __tablename__ = "vendor_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_type = Column(Enum(BusinessType), nullable=False)
    business_name = Column(String, nullable=True)  # Required for INDIVIDUAL
    organization_name = Column(String, nullable=True)  # Required for IP and LEGAL_ENTITY
    legal_form = Column(Enum(LegalForm), nullable=True)  # Required for LEGAL_ENTITY
    inn = Column(String, nullable=True)  # Required for IP and LEGAL_ENTITY
    registration_country = Column(String, nullable=True)  # Required for IP and LEGAL_ENTITY
    registration_date = Column(Date, nullable=True)  # Required for IP and LEGAL_ENTITY
    passport_front_url = Column(String, nullable=True)  # Required for all types
    passport_back_url = Column(String, nullable=True)  # Required for all types
    description = Column(String, nullable=True)  # Store description for public display
    status = Column(Enum(VendorStatus), default=VendorStatus.PENDING, nullable=False)
    reject_reason = Column(String, nullable=True)  # Store admin rejection reason
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="vendor_profile") 
    products = relationship(
        "Product",
        back_populates="vendor_profile",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
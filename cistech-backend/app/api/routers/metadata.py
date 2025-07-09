from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.metadata_service import MetadataService
from app.schemas.product import MetadataResponse

router = APIRouter(prefix="/get_catalogs_filter", tags=["Catalogs & Filter"])

@router.get("/", response_model=MetadataResponse)
def get_metadata(db: Session = Depends(get_db)):
    """Get all categories and filter types with options in JSON format with IDs"""
    metadata_service = MetadataService(db)
    return metadata_service.get_all_metadata()
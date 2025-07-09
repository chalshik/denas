from sqlalchemy.orm import Session
from app.models.product.category import Category
from app.models.product.filter import FilterType, FilterOption
from app.schemas.product import MetadataResponse
from typing import Dict, List, Any

class MetadataService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_metadata(self) -> MetadataResponse:
        """Get all categories and filter types with options in JSON format like filter.json but with IDs"""
        
        # Get all categories with their filter types
        categories = self.db.query(Category).all()
        
        result = {}
        
        for category in categories:
            # Get filter types for this category
            filter_types = self.db.query(FilterType).filter(
                FilterType.category_id == category.id
            ).all()
            
            category_filters = {}
            
            for filter_type in filter_types:
                # Get options for this filter type
                options = self.db.query(FilterOption).filter(
                    FilterOption.filter_type_id == filter_type.id
                ).all()
                
                # Create options list with IDs and values
                options_list = [
                    {
                        "id": option.id,
                        "value": option.value
                    }
                    for option in options
                ]
                
                category_filters[filter_type.name] = {
                    "id": filter_type.id,
                    "options": options_list
                }
            
            result[category.name] = {
                "id": category.id,
                "filters": category_filters
            }
        
        return MetadataResponse(data=result)
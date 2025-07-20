from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
import logging
from sqlalchemy.orm import Session

from app.services.supabase_storage import get_supabase_storage, SupabaseStorageService
from app.api.dependencies import get_current_user, require_admin_access
from app.models.user import User
from app.models.product_image import ProductImage
from app.db.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/single", response_model=dict)
async def upload_single_file(
    file: UploadFile = File(...),
    folder: str = Form(default="uploads"),
    current_user: User = Depends(get_current_user),
    storage: SupabaseStorageService = Depends(get_supabase_storage)
):
    """
    Upload a single file to Supabase Storage
    
    Args:
        file: The file to upload
        folder: Storage folder (default: "uploads")
        current_user: Authenticated user
        storage: Supabase storage service
        
    Returns:
        Dict with file URL and metadata
    """
    try:
        # Validate file type (you can customize this)
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Upload file
        file_url = await storage.upload_file(file, folder)
        
        logger.info(f"File uploaded by user {current_user.id}: {file.filename}")
        
        return {
            "success": True,
            "file_url": file_url,
            "filename": file.filename,
            "content_type": file.content_type,
            "folder": folder
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to upload file"
        )

@router.post("/multiple", response_model=dict)
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    folder: str = Form(default="uploads"),
    current_user: User = Depends(get_current_user),
    storage: SupabaseStorageService = Depends(get_supabase_storage)
):
    """
    Upload multiple files to Supabase Storage
    
    Args:
        files: List of files to upload
        folder: Storage folder (default: "uploads")
        current_user: Authenticated user
        storage: Supabase storage service
        
    Returns:
        Dict with file URLs and metadata
    """
    try:
        # Validate file count
        if len(files) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 files allowed per upload"
            )
        
        # Validate file types
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        for file in files:
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type not allowed for {file.filename}. Allowed types: {', '.join(allowed_types)}"
                )
        
        # Upload files
        file_urls = await storage.upload_multiple_files(files, folder)
        
        logger.info(f"Multiple files uploaded by user {current_user.id}: {len(files)} files")
        
        return {
            "success": True,
            "files": [
                {
                    "file_url": url,
                    "filename": file.filename,
                    "content_type": file.content_type
                }
                for url, file in zip(file_urls, files)
            ],
            "folder": folder,
            "total_files": len(files)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Multiple upload error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to upload files"
        )

@router.post("/product-images", response_model=dict)
async def upload_product_images(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    storage: SupabaseStorageService = Depends(get_supabase_storage)
):
    """
    Upload product images specifically to the product-images folder
    
    Args:
        files: List of image files to upload
        current_user: Authenticated user (should be admin)
        storage: Supabase storage service
        
    Returns:
        Dict with image URLs ready for product creation
    """
    try:
        # Check if user has admin privileges (you might want to use admin dependency)
        if current_user.role.value not in ["Admin", "Manager"]:
            raise HTTPException(
                status_code=403,
                detail="Only admins can upload product images"
            )
        
        # Validate file count
        if len(files) > 5:
            raise HTTPException(
                status_code=400,
                detail="Maximum 5 product images allowed"
            )
        
        # Validate file types - stricter for product images
        allowed_types = ["image/jpeg", "image/png", "image/webp"]
        for file in files:
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type not allowed for {file.filename}. Allowed types: {', '.join(allowed_types)}"
                )
        
        # Upload to product-images folder
        file_urls = await storage.upload_multiple_files(files, "product-images", max_size_mb=10)
        
        logger.info(f"Product images uploaded by admin {current_user.id}: {len(files)} images")
        
        return {
            "success": True,
            "image_urls": file_urls,
            "total_images": len(files),
            "message": "Product images uploaded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Product image upload error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to upload product images"
        )


@router.post("/cleanup-orphaned-images", response_model=dict)
async def cleanup_orphaned_images(
    dry_run: bool = True,
    admin_user: User = Depends(require_admin_access),
    storage: SupabaseStorageService = Depends(get_supabase_storage),
    db: Session = Depends(get_db)
):
    """
    Clean up orphaned images from Supabase storage that are no longer referenced in database
    
    Args:
        dry_run: If True, only report what would be deleted without actually deleting
        admin_user: Admin user (required)
        storage: Supabase storage service
        db: Database session
        
    Returns:
        Dict with cleanup results and statistics
    """
    try:
        # Get all image URLs currently referenced in database
        db_images = db.query(ProductImage.image_url).all()
        db_image_urls = {img.image_url for img in db_images}
        
        logger.info(f"Found {len(db_image_urls)} images referenced in database")
        
        # Get all files from Supabase storage product-images folder
        try:
            # Note: This is a simplified approach. In practice, you'd need to implement
            # a method to list all files in storage, which depends on your Supabase setup
            logger.warning("Storage file listing not implemented. This cleanup is database-only.")
            
            # For now, we can only clean up based on known bad URLs
            # A complete implementation would require listing storage files and comparing
            
            return {
                "success": True,
                "dry_run": dry_run,
                "message": "Cleanup endpoint ready - storage file listing needs implementation",
                "database_images_count": len(db_image_urls),
                "recommendation": "Implement storage.list_files() method for complete cleanup"
            }
            
        except Exception as storage_error:
            logger.error(f"Storage listing error: {str(storage_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to access storage: {str(storage_error)}"
            )
        
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to perform cleanup operation"
        )


@router.delete("/force-delete-image", response_model=dict) 
async def force_delete_image_from_storage(
    image_url: str,
    admin_user: User = Depends(require_admin_access),
    storage: SupabaseStorageService = Depends(get_supabase_storage)
):
    """
    Force delete a specific image from Supabase storage (admin only)
    Use with caution - this bypasses database checks
    
    Args:
        image_url: Full URL of the image to delete
        admin_user: Admin user (required)
        storage: Supabase storage service
        
    Returns:
        Dict with deletion result
    """
    try:
        file_path = storage.extract_file_path_from_url(image_url)
        success = storage.delete_file(file_path)
        
        if success:
            logger.info(f"Force deleted image from storage: {image_url} by admin {admin_user.id}")
            return {
                "success": True,
                "message": "Image deleted from storage",
                "image_url": image_url,
                "file_path": file_path
            }
        else:
            return {
                "success": False,
                "message": "Failed to delete image from storage",
                "image_url": image_url,
                "file_path": file_path
            }
            
    except Exception as e:
        logger.error(f"Force delete error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete image: {str(e)}"
        ) 
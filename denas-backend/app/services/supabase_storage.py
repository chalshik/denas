import os
import uuid
from typing import Optional, List
from fastapi import HTTPException, UploadFile
from supabase import create_client, Client
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class SupabaseStorageService:
    """Service for handling file uploads to Supabase Storage"""
    
    def __init__(self):
        logger.info(f"Initializing Supabase Storage Service")
        logger.info(f"SUPABASE_URL: {settings.SUPABASE_URL}")
        logger.info(f"SUPABASE_SERVICE_ROLE_KEY: {'***' if settings.SUPABASE_SERVICE_ROLE_KEY else 'None'}")
        logger.info(f"SUPABASE_STORAGE_BUCKET: {settings.SUPABASE_STORAGE_BUCKET}")
        logger.info(f"has_supabase_storage: {settings.has_supabase_storage}")
        
        if not settings.has_supabase_storage:
            raise ValueError("Supabase storage is not properly configured")
        
        try:
            self.supabase: Client = create_client(
                settings.SUPABASE_URL, 
                settings.SUPABASE_SERVICE_ROLE_KEY
            )
            self.bucket_name = settings.SUPABASE_STORAGE_BUCKET
            logger.info(f"Supabase client created successfully")
        except Exception as e:
            logger.error(f"Failed to create Supabase client: {str(e)}")
            raise
        
    async def upload_file(
        self, 
        file: UploadFile, 
        folder: str = "uploads",
        max_size_mb: int = 5
    ) -> str:
        """
        Upload a file to Supabase Storage
        
        Args:
            file: The uploaded file
            folder: Folder within the bucket (default: "uploads")
            max_size_mb: Maximum file size in MB (default: 5MB)
            
        Returns:
            Public URL of the uploaded file
            
        Raises:
            HTTPException: If upload fails
        """
        try:
            # Validate file size
            if file.size and file.size > max_size_mb * 1024 * 1024:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size is {max_size_mb}MB"
                )
            
            # Generate unique filename
            file_extension = file.filename.split('.')[-1] if file.filename and '.' in file.filename else ''
            unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
            # Don't add folder prefix if it's already the bucket name
            if folder == self.bucket_name:
                file_path = unique_filename
            else:
                file_path = f"{folder}/{unique_filename}"
            
            # Read file content
            file_content = await file.read()
            
            # Reset file position for potential re-reading
            try:
                await file.seek(0)
            except:
                # If seek fails, it's okay, we already have the content
                pass
            
            try:
                # Upload to Supabase Storage
                result = self.supabase.storage.from_(self.bucket_name).upload(
                    file_path,
                    file_content,
                    file_options={
                        "content-type": file.content_type or "application/octet-stream",
                        "upsert": "false"
                    }
                )
                
                logger.info(f"Upload result: {result}")
                
                # Get public URL
                public_url = self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)
                
                logger.info(f"File uploaded successfully: {file_path} -> {public_url}")
                return public_url
                
            except Exception as upload_error:
                logger.error(f"Supabase upload error: {str(upload_error)}")
                # Try with different approach
                try:
                    # Alternative upload method
                    result = self.supabase.storage.from_(self.bucket_name).upload(
                        path=file_path,
                        file=file_content,
                        file_options={"content-type": file.content_type or "application/octet-stream"}
                    )
                    
                    public_url = self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)
                    logger.info(f"File uploaded successfully (alternative method): {file_path} -> {public_url}")
                    return public_url
                    
                except Exception as alt_error:
                    logger.error(f"Alternative upload also failed: {str(alt_error)}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to upload file to storage: {str(alt_error)}"
                    )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file: {str(e)}"
            )
    
    async def upload_multiple_files(
        self, 
        files: List[UploadFile], 
        folder: str = "uploads",
        max_size_mb: int = 5
    ) -> List[str]:
        """
        Upload multiple files to Supabase Storage
        
        Args:
            files: List of uploaded files
            folder: Folder within the bucket
            max_size_mb: Maximum file size in MB per file
            
        Returns:
            List of public URLs of uploaded files
        """
        urls = []
        for file in files:
            url = await self.upload_file(file, folder, max_size_mb)
            urls.append(url)
        return urls
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from Supabase Storage
        
        Args:
            file_path: Path to the file in storage
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.supabase.storage.from_(self.bucket_name).remove([file_path])
            return result.status_code == 200
        except Exception as e:
            logger.error(f"Delete error: {str(e)}")
            return False
    
    def get_file_url(self, file_path: str) -> str:
        """
        Get public URL for a file
        
        Args:
            file_path: Path to the file in storage
            
        Returns:
            Public URL of the file
        """
        return self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)

# Global instance
supabase_storage = None

def get_supabase_storage() -> SupabaseStorageService:
    """Get Supabase storage service instance"""
    global supabase_storage
    if supabase_storage is None:
        if settings.has_supabase_storage:
            supabase_storage = SupabaseStorageService()
        else:
            raise HTTPException(
                status_code=500,
                detail="Supabase storage is not configured"
            )
    return supabase_storage 
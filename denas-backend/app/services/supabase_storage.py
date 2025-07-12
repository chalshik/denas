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
        if not settings.has_supabase_storage:
            raise ValueError("Supabase storage is not properly configured")
        
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        self.bucket_name = settings.SUPABASE_STORAGE_BUCKET
        
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
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
            unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
            file_path = f"{folder}/{unique_filename}"
            
            # Read file content
            file_content = await file.read()
            
            # Upload to Supabase Storage
            result = self.supabase.storage.from_(self.bucket_name).upload(
                file_path,
                file_content,
                file_options={
                    "content-type": file.content_type,
                    "upsert": "false"
                }
            )
            
            if result.status_code != 200:
                logger.error(f"Upload failed: {result}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to upload file to storage"
                )
            
            # Get public URL
            public_url = self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)
            
            logger.info(f"File uploaded successfully: {file_path}")
            return public_url
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to upload file"
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
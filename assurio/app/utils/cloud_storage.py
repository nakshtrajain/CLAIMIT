import cloudinary
import cloudinary.uploader
import cloudinary.api
import uuid
from typing import Optional, Dict, Any
from fastapi import UploadFile, HTTPException
import aiofiles
import tempfile
import os
from pathlib import Path
from config import settings

class CloudStorageManager:
    def __init__(self):
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET
        )
        
        # Fallback local storage for development
        self.local_upload_dir = Path("data/uploads")
        self.local_upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def upload_pdf_to_cloudinary(self, file: UploadFile) -> Dict[str, Any]:
        """Upload PDF file to Cloudinary and return file info"""
        try:
            # Validate file type
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400, 
                    detail="Only PDF files are supported"
                )
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            cloudinary_filename = f"assurio/{file_id}_{file.filename}"
            
            # Read file content
            content = await file.read()
            
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                content,
                public_id=cloudinary_filename,
                resource_type="raw",
                format="pdf",
                folder="assurio"
            )
            
            return {
                "file_id": file_id,
                "original_filename": file.filename,
                "cloudinary_url": upload_result.get("secure_url"),
                "cloudinary_public_id": upload_result.get("public_id"),
                "file_size": len(content),
                "storage_type": "cloudinary"
            }
            
        except Exception as e:
            # Fallback to local storage if cloud upload fails
            return await self._fallback_local_upload(file)
    
    async def _fallback_local_upload(self, file: UploadFile) -> Dict[str, Any]:
        """Fallback to local storage if cloud upload fails"""
        try:
            file_id = str(uuid.uuid4())
            filename = f"{file_id}_{file.filename}"
            file_path = self.local_upload_dir / filename
            
            # Save file locally
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            return {
                "file_id": file_id,
                "original_filename": file.filename,
                "local_path": str(file_path),
                "file_size": len(content),
                "storage_type": "local"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error saving file: {str(e)}"
            )
    
    async def validate_pdf_file(self, file: UploadFile) -> bool:
        """Validate PDF file before processing"""
        try:
            # Check file extension
            if not file.filename.lower().endswith('.pdf'):
                return False
            
            # Check file size (max 50MB)
            content = await file.read()
            if len(content) > 50 * 1024 * 1024:  # 50MB
                return False
            
            # Reset file pointer for later reading
            await file.seek(0)
            
            return True
            
        except Exception:
            return False
    
    def get_file_info(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about a saved file"""
        try:
            if file_data.get("storage_type") == "cloudinary":
                return {
                    "filename": file_data.get("original_filename", "unknown"),
                    "size": file_data.get("file_size", 0),
                    "url": file_data.get("cloudinary_url", ""),
                    "storage_type": "cloudinary",
                    "file_id": file_data.get("file_id", "")
                }
            else:
                # Local file
                path = Path(file_data.get("local_path", ""))
                if path.exists():
                    return {
                        "filename": path.name,
                        "size": path.stat().st_size,
                        "created": path.stat().st_ctime,
                        "path": str(path),
                        "storage_type": "local",
                        "file_id": file_data.get("file_id", "")
                    }
                else:
                    return {
                        "filename": file_data.get("original_filename", "unknown"),
                        "size": file_data.get("file_size", 0),
                        "path": str(path),
                        "storage_type": "local",
                        "file_id": file_data.get("file_id", ""),
                        "error": "File not found on disk"
                    }
        except Exception as e:
            return {
                "filename": file_data.get("original_filename", "unknown"),
                "size": file_data.get("file_size", 0),
                "storage_type": "unknown",
                "file_id": file_data.get("file_id", ""),
                "error": str(e)
            }
    
    async def delete_file(self, file_data: Dict[str, Any]) -> bool:
        """Delete file from storage"""
        try:
            if file_data.get("storage_type") == "cloudinary":
                # Delete from Cloudinary
                public_id = file_data.get("cloudinary_public_id")
                if public_id:
                    cloudinary.uploader.destroy(public_id)
                return True
            else:
                # Delete local file
                path = Path(file_data.get("local_path", ""))
                if path.exists():
                    path.unlink()
                    return True
            return False
        except Exception:
            return False 
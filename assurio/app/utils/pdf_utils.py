import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
import aiofiles

class PDFUtils:
    def __init__(self, upload_dir: str = "data/uploads"):
        self.upload_dir = Path(upload_dir)
        try:
            self.upload_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            # Fallback to /tmp if data directory is not writable (common on cloud platforms)
            import tempfile
            self.upload_dir = Path(tempfile.gettempdir()) / "assurio_uploads"
            self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_pdf_file(self, file: UploadFile) -> str:
        """Save uploaded PDF file and return the file path"""
        try:
            # Validate file type
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400, 
                    detail="Only PDF files are supported"
                )
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            filename = f"{file_id}_{file.filename}"
            file_path = self.upload_dir / filename
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            return str(file_path)
            
        except HTTPException:
            raise
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
    
    def get_file_info(self, file_path: str) -> dict:
        """Get information about a saved file"""
        path = Path(file_path)
        if path.exists():
            return {
                "filename": path.name,
                "size": path.stat().st_size,
                "created": path.stat().st_ctime,
                "path": str(path)
            }
        return None
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old uploaded files"""
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for file_path in self.upload_dir.glob("*.pdf"):
            if current_time - file_path.stat().st_ctime > max_age_seconds:
                try:
                    file_path.unlink()
                except Exception:
                    pass  # Ignore cleanup errors 
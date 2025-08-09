from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
import aiofiles

from ..utils.pdf_loader import PDFLoader
from ..utils.embeddings import EmbeddingManager
from ..utils.pinecone_vectorstore import PineconeVectorStore
from ..utils.cloud_storage import CloudStorageManager
from config import settings

router = APIRouter()

# Global instances (in production, use dependency injection)
embedding_manager = None
vector_store = None
pdf_loader = None
cloud_storage = None

class UploadResponse(BaseModel):
    status: str
    message: str
    filename: str
    chunks_indexed: int
    total_documents: int
    file_info: Dict[str, Any]

class UploadStatusResponse(BaseModel):
    status: str
    progress: float
    message: str
    chunks_processed: int
    total_chunks: int

async def get_services():
    """Initialize services if not already done"""
    global embedding_manager, vector_store, pdf_loader, cloud_storage
    
    if embedding_manager is None:
        embedding_manager = EmbeddingManager(settings.EMBEDDING_MODEL)
    
    if vector_store is None:
        vector_store = PineconeVectorStore(embedding_manager)
    
    if pdf_loader is None:
        pdf_loader = PDFLoader(settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    
    if cloud_storage is None:
        cloud_storage = CloudStorageManager()

@router.post("/upload_pdf", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF document with cloud storage"""
    try:
        print(f"Starting upload for file: {file.filename}")
        await get_services()
        print("Services initialized successfully")
        
        # Validate file
        if not await cloud_storage.validate_pdf_file(file):
            print("File validation failed")
            raise HTTPException(
                status_code=400, 
                detail="Invalid PDF file. Please check file type and size."
            )
        print("File validation passed")
        
        # Upload file to cloud storage
        file_data = await cloud_storage.upload_pdf_to_cloudinary(file)
        print(f"File uploaded to cloud storage: {file_data}")
        
        # Process PDF based on storage type
        if file_data.get("storage_type") == "cloudinary":
            # Process from Cloudinary URL
            documents = await pdf_loader.load_pdf_from_cloudinary(
                file_data["cloudinary_url"],
                file_id=file_data["file_id"],
                filename=file_data["original_filename"]
            )
        else:
            # Process from local file
            documents = await pdf_loader.load_pdf(
                file_data["local_path"],
                file_id=file_data["file_id"],
                filename=file_data["original_filename"]
            )
        
        print(f"PDF processed, {len(documents)} chunks created")
        
        # Add to vector store
        print("Adding documents to vector store")
        await vector_store.add_documents(documents)
        
        result = UploadResponse(
            status="uploaded",
            message="Document uploaded and indexed successfully",
            filename=file.filename,
            chunks_indexed=len(documents),
            total_documents=vector_store.get_document_count(),
            file_info=cloud_storage.get_file_info(file_data)
        )
        print(f"Upload completed successfully: {result}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = f"Error uploading document: {str(e)}\nTraceback: {traceback.format_exc()}"
        print(error_details)  # Log the error for debugging
        
        # Return a proper JSON response instead of raising HTTPException
        return UploadResponse(
            status="error",
            message=f"Error uploading document: {str(e)}",
            filename=file.filename if file else "unknown",
            chunks_indexed=0,
            total_documents=0,
            file_info={"error": str(e)}
        )

@router.post("/upload_pdf_async", response_model=Dict[str, Any])
async def upload_pdf_async(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """Upload PDF and process in background"""
    try:
        await get_services()
        
        # Validate file
        if not await cloud_storage.validate_pdf_file(file):
            raise HTTPException(
                status_code=400, 
                detail="Invalid PDF file. Please check file type and size."
            )
        
        # Upload file to cloud storage
        file_data = await cloud_storage.upload_pdf_to_cloudinary(file)
        
        # Start background processing
        if background_tasks:
            background_tasks.add_task(process_pdf_background, file_data)
        
        return {
            "status": "processing",
            "message": "Document uploaded. Processing in background...",
            "filename": file.filename,
            "task_id": file_data["file_id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error uploading document: {str(e)}"
        )

async def process_pdf_background(file_data: Dict[str, Any]):
    """Background task to process PDF"""
    try:
        await get_services()
        
        # Process PDF based on storage type
        if file_data.get("storage_type") == "cloudinary":
            documents = await pdf_loader.load_pdf_from_cloudinary(
                file_data["cloudinary_url"],
                file_id=file_data["file_id"],
                filename=file_data["original_filename"]
            )
        else:
            documents = await pdf_loader.load_pdf(
                file_data["local_path"],
                file_id=file_data["file_id"],
                filename=file_data["original_filename"]
            )
        
        # Add to vector store
        await vector_store.add_documents(documents)
        
        print(f"Background processing completed for {file_data['original_filename']}: {len(documents)} chunks indexed")
        
    except Exception as e:
        print(f"Background processing failed for {file_data.get('original_filename', 'unknown')}: {str(e)}")

@router.get("/upload_status/{task_id}", response_model=UploadStatusResponse)
async def get_upload_status(task_id: str):
    """Get status of background upload processing"""
    # This is a simplified implementation
    # In production, you'd use a proper task queue like Celery
    return UploadStatusResponse(
        status="completed",
        progress=100.0,
        message="Processing completed",
        chunks_processed=0,
        total_chunks=0
    )

@router.get("/uploaded_files", response_model=List[Dict[str, Any]])
async def get_uploaded_files():
    """Get list of uploaded files"""
    await get_services()
    
    # For cloud storage, we can't easily list all files
    # This would require maintaining a separate database of uploaded files
    return [
        {
            "message": "Cloud storage - file listing not implemented",
            "note": "Files are stored in Cloudinary and indexed in Pinecone"
        }
    ]

@router.delete("/uploaded_files/{file_id}")
async def delete_uploaded_file(file_id: str):
    """Delete an uploaded file and its vectors"""
    await get_services()
    
    try:
        # Delete vectors from Pinecone
        await vector_store.delete_documents_by_file_id(file_id)
        
        return {"message": f"File {file_id} and associated vectors deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error deleting file: {str(e)}"
        )

@router.get("/vector_stats", response_model=Dict[str, Any])
async def get_vector_stats():
    """Get vector store statistics"""
    await get_services()
    
    try:
        stats = vector_store.get_index_stats()
        return {
            "vector_store_stats": stats,
            "embedding_model": settings.EMBEDDING_MODEL,
            "use_remote_embeddings": settings.USE_REMOTE_EMBEDDINGS,
            "storage_mode": settings.STORAGE_MODE
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error getting vector stats: {str(e)}"
        )

@router.get("/test_upload")
async def test_upload_endpoint():
    """Test endpoint to check if upload route is accessible"""
    return {
        "status": "ok",
        "message": "Upload endpoint is accessible",
        "timestamp": "2024-08-01T16:00:00Z"
    }

@router.get("/health_check")
async def health_check():
    """Simple health check for Render"""
    return {
        "status": "healthy",
        "service": "ASSURIO Cloud",
        "timestamp": "2024-08-01T16:00:00Z"
    }

@router.get("/debug_upload")
async def debug_upload():
    """Debug endpoint to test upload response"""
    return {
        "status": "ok",
        "message": "Debug upload endpoint working",
        "test_data": {
            "filename": "test.pdf",
            "size": 1024,
            "chunks": 5
        }
    } 
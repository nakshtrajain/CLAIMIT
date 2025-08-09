from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio

from ..utils.pdf_loader import PDFLoader
from ..utils.embeddings import EmbeddingManager
from ..utils.pinecone_vectorstore import PineconeVectorStore
from ..utils.llm_reasoner import LLMReasoner
from config import settings

router = APIRouter()

# Global instances (in production, use dependency injection)
embedding_manager = None
vector_store = None
llm_reasoner = None
pdf_loader = None

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class QueryResponse(BaseModel):
    query: str
    extracted_entities: Dict[str, Any]
    decision: Optional[str] = "N/A"
    amount: Optional[str] = "N/A"
    justification: Optional[str] = "N/A"
    referenced_clauses: List[str] = []
    retrieved_chunks: List[Dict[str, Any]] = []

class HealthResponse(BaseModel):
    status: str
    message: str
    document_count: int

async def get_services():
    """Initialize services if not already done"""
    global embedding_manager, vector_store, llm_reasoner, pdf_loader
    
    if embedding_manager is None:
        embedding_manager = EmbeddingManager(settings.EMBEDDING_MODEL)
    
    if vector_store is None:
        vector_store = PineconeVectorStore(embedding_manager)
    
    if llm_reasoner is None:
        llm_reasoner = LLMReasoner()
    
    if pdf_loader is None:
        pdf_loader = PDFLoader(settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    await get_services()
    
    return HealthResponse(
        status="healthy",
        message="ClauseMind API is running",
        document_count=vector_store.get_document_count() if vector_store else 0
    )

@router.post("/upload", response_model=Dict[str, Any])
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a PDF document"""
    try:
        await get_services()
        
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        content = await file.read()
        
        # Process PDF
        documents = await pdf_loader.load_pdf_from_bytes(
            content, 
            file.filename
        )
        
        # Add to vector store
        await vector_store.add_documents(documents)
        
        return {
            "message": "Document uploaded successfully",
            "filename": file.filename,
            "chunks_processed": len(documents),
            "total_documents": vector_store.get_document_count()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a natural language query and return decision"""
    try:
        await get_services()
        
        if vector_store.get_document_count() == 0:
            raise HTTPException(
                status_code=400, 
                detail="No documents uploaded. Please upload a document first."
            )
        
        # Extract entities from query
        entities = await llm_reasoner.extract_entities(request.query)
        
        # Retrieve relevant chunks
        retrieved_results = await vector_store.similarity_search(
            request.query, 
            request.top_k
        )
        
        # Extract documents and scores
        retrieved_docs = [doc for doc, score in retrieved_results]
        scores = [score for doc, score in retrieved_results]
        
        # Reason over retrieved documents
        reasoning_result = await llm_reasoner.reason(request.query, retrieved_docs)
        
        # Prepare response with fallback handling for None values
        response = QueryResponse(
            query=request.query,
            extracted_entities=entities,
            decision=reasoning_result.get("decision") or "error",
            amount=reasoning_result.get("amount") or "N/A",
            justification=reasoning_result.get("justification") or "N/A",
            referenced_clauses=reasoning_result.get("referenced_clauses") or [],
            retrieved_chunks=[
                {
                    "content": doc.page_content,
                    "score": float(score),
                    "metadata": doc.metadata
                }
                for doc, score in retrieved_results
            ]
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.get("/documents", response_model=Dict[str, Any])
async def get_document_info():
    """Get information about uploaded documents"""
    await get_services()
    
    return {
        "document_count": vector_store.get_document_count(),
        "is_initialized": vector_store.is_initialized(),
        "vector_store_type": "Pinecone",
        "embedding_model": settings.EMBEDDING_MODEL,
        "use_remote_embeddings": settings.USE_REMOTE_EMBEDDINGS
    } 
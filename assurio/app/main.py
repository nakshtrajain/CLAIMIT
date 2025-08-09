from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn

from .routes.query_router import router as query_router
from .routes.upload_router import router as upload_router

# Create FastAPI app
app = FastAPI(
    title="ClauseMind Cloud - Intelligent Clause Retriever & Decision System",
    description="""
    🧠 **ClauseMind Cloud** - An intelligent system that uses LLM-powered semantic search to retrieve relevant clauses from insurance documents and provide automated decision-making with cloud storage.

    ## Features:
    - **Cloud Document Upload**: Upload PDF insurance documents to Cloudinary
    - **Auto Indexing**: Automatic embedding generation and Pinecone indexing
    - **Semantic Search**: Find relevant clauses using Pinecone vector search
    - **LLM Reasoning**: Use Gemini to analyze clauses and make decisions
    - **Entity Extraction**: Automatically extract key information from queries
    - **Real-time Processing**: Background processing for large documents
    - **Cloud Deployment**: Fully deployable on Render, Vercel, or any cloud platform

    ## Pipeline:
    1. PDF Upload → Cloudinary Storage
    2. Text Extraction & Chunking → Local Processing
    3. User Query → Entity Extraction (Gemini)
    4. Query Embedding → Pinecone Vector Search
    5. Retrieved Clauses → LLM Reasoning (Gemini)
    6. Structured Output → Decision + Justification

    ## Tech Stack:
    - **Backend**: FastAPI (Async)
    - **File Storage**: Cloudinary
    - **Vector DB**: Pinecone
    - **Embeddings**: SentenceTransformers (Local) or Hugging Face API (Remote)
    - **LLM**: Google Gemini (via LangChain)
    - **Document Processing**: PyPDF2
    - **Cloud Deployment**: Render/Vercel ready

    ## Environment Variables:
    - `CLOUDINARY_*`: Cloudinary configuration
    - `PINECONE_*`: Pinecone vector database
    - `HUGGINGFACE_API_KEY`: Optional remote embeddings
    - `GEMINI_API_KEY`: Google Gemini API
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(query_router, prefix="/api/v1", tags=["ClauseMind API"])
app.include_router(upload_router, prefix="/api/v1", tags=["Document Upload"])

# Template rendering setup
templates = Jinja2Templates(directory="templates")

# Mount static assets (if any)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve HTML page on root URL
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("enhanced.html", {"request": request})

# JSON API info endpoint
@app.get("/api/v1", response_class=JSONResponse)
async def api_info():
    return {
        "api_name": "ClauseMind Cloud API",
        "version": "2.0.0",
        "architecture": "cloud-native",
        "endpoints": {
            "health": "GET /api/v1/health",
            "upload": "POST /api/v1/upload_pdf",
            "upload_async": "POST /api/v1/upload_pdf_async",
            "query": "POST /api/v1/query",
            "documents": "GET /api/v1/documents",
            "vector_stats": "GET /api/v1/vector_stats"
        },
        "features": [
            "Cloud PDF document upload and processing",
            "Semantic clause retrieval using Pinecone",
            "LLM-powered decision making with Gemini",
            "Entity extraction from natural language queries",
            "Cloud-native deployment ready"
        ],
        "storage": {
            "files": "Cloudinary",
            "vectors": "Pinecone",
            "embeddings": "Local SentenceTransformers or Remote Hugging Face API"
        }
    }

# For local dev
if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

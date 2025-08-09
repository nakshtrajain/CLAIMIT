 Assurio – Intelligent Clause Retriever & Decision System

Assurio is an AI-powered insurance assistant that enables users to upload PDF insurance documents, automatically indexes them using semantic embeddings, and allows natural language querying to retrieve relevant clauses and provide automated decisions.

 🚀 Features

- Drag & Drop PDF Upload: Modern web interface for uploading insurance documents.
- Auto Indexing: Automatic text extraction, chunking, and embedding generation.
- Semantic Search: Fast clause retrieval using FAISS vector search.
- LLM Reasoning: Uses Google Gemini for decision-making and entity extraction.
- Real-time Processing: Background progress indicators for uploads and queries.
- File Management: List, delete, and clean up uploaded documents.
- Health & Status Monitoring: System health and document count endpoints.

 🛠️ Tech Stack

- Backend: FastAPI (Async)
- Frontend: Tailwind CSS, HTML5
- Embeddings: SentenceTransformers (MiniLM)
- Vector DB: FAISS (Local)
- LLM: Google Gemini (via LangChain)
- Document Processing: PyPDF2
- File Handling: aiofiles (Async)

 ⚡ Usage

1. Start the backend:  
   `python start_enhanced.py`
2. Open the enhanced web UI:  
   [http://localhost:8000/frontend/enhanced.html](http://localhost:8000/frontend/enhanced.html)
3. Upload PDF documents and query the system.

 📚 API Endpoints

- `POST /api/v1/upload_pdf` – Upload and index PDF
- `POST /api/v1/query` – Query indexed documents
- `GET /api/v1/documents` – Get document count
- `GET /api/v1/health` – System health check



 📄 License

MIT


import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Existing settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "your_gemini_api_key_here")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "models/gemini-1.5-flash")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "5"))
    
    # Cloud storage settings
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")
    
    # Pinecone settings
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "assurio-documents")
    
    # Hugging Face settings
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    USE_REMOTE_EMBEDDINGS: bool = os.getenv("USE_REMOTE_EMBEDDINGS", "false").lower() == "true"
    
    # Storage mode
    STORAGE_MODE: str = os.getenv("STORAGE_MODE", "cloud")  # "local" or "cloud"

settings = Settings() 
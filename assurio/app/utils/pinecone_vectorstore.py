import os
from pinecone import Pinecone, ServerlessSpec
import numpy as np
import uuid
from typing import List, Tuple, Optional, Dict, Any
from langchain.schema import Document
from .embeddings import EmbeddingManager
from config import settings

class PineconeVectorStore:
    def __init__(self, embedding_manager: EmbeddingManager):
        self.embedding_manager = embedding_manager
        self.index_name = settings.PINECONE_INDEX_NAME
        self.dimension = embedding_manager.get_dimension()
        
        # Initialize Pinecone with new API
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        # Get or create index
        self.index = self._get_or_create_index()
        self._is_initialized = True
    
    def _get_or_create_index(self):
        """Get existing index or create new one"""
        try:
            # Check if index exists
            if self.index_name not in self.pc.list_indexes().names():
                # Create new index
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-west-2"
                    )
                )
            
            return self.pc.Index(self.index_name)
        except Exception as e:
            raise Exception(f"Error initializing Pinecone index: {str(e)}")
    
    async def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store"""
        try:
            if not documents:
                return
            
            # Extract texts from documents
            texts = [doc.page_content for doc in documents]
            
            # Generate embeddings
            embeddings = await self.embedding_manager.get_embeddings(texts)
            
            # Prepare vectors for Pinecone
            vectors = []
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                vector_id = str(uuid.uuid4())
                
                # Prepare metadata
                metadata = {
                    "text": doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                    "chunk_id": doc.metadata.get("chunk_id", i),
                    "file_id": doc.metadata.get("file_id", ""),
                    "filename": doc.metadata.get("filename", "")
                }
                
                vectors.append({
                    "id": vector_id,
                    "values": embedding.tolist(),
                    "metadata": metadata
                })
            
            # Upsert vectors to Pinecone
            self.index.upsert(vectors=vectors)
            
        except Exception as e:
            raise Exception(f"Error adding documents to Pinecone: {str(e)}")
    
    async def similarity_search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Search for similar documents"""
        try:
            # Generate query embedding
            query_embedding = await self.embedding_manager.get_single_embedding(query)
            
            # Search in Pinecone
            search_results = self.index.query(
                vector=query_embedding.tolist(),
                top_k=k,
                include_metadata=True
            )
            
            # Convert results to Document objects
            results = []
            for match in search_results.matches:
                # Recreate Document object from metadata
                doc = Document(
                    page_content=match.metadata.get("text", ""),
                    metadata={
                        "source": match.metadata.get("source", "unknown"),
                        "chunk_id": match.metadata.get("chunk_id", 0),
                        "file_id": match.metadata.get("file_id", ""),
                        "filename": match.metadata.get("filename", ""),
                        "score": match.score
                    }
                )
                results.append((doc, float(match.score)))
            
            return results
            
        except Exception as e:
            raise Exception(f"Error in similarity search: {str(e)}")
    
    async def similarity_search_with_threshold(self, query: str, k: int = 5, threshold: float = 0.5) -> List[Tuple[Document, float]]:
        """Search for similar documents with similarity threshold"""
        results = await self.similarity_search(query, k)
        return [(doc, score) for doc, score in results if score >= threshold]
    
    def get_document_count(self) -> int:
        """Get the number of documents in the vector store"""
        try:
            stats = self.index.describe_index_stats()
            return stats.total_vector_count
        except Exception:
            return 0
    
    async def delete_documents_by_file_id(self, file_id: str) -> bool:
        """Delete all documents associated with a specific file"""
        try:
            # Query for vectors with matching file_id
            query_results = self.index.query(
                vector=[0] * self.dimension,  # Dummy vector
                top_k=10000,  # Large number to get all vectors
                include_metadata=True,
                filter={"file_id": {"$eq": file_id}}
            )
            
            # Extract vector IDs to delete
            vector_ids = [match.id for match in query_results.matches]
            
            if vector_ids:
                self.index.delete(ids=vector_ids)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error deleting documents for file_id {file_id}: {str(e)}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": stats.namespaces
            }
        except Exception as e:
            return {"error": str(e)}
    
    def is_initialized(self) -> bool:
        """Check if vector store is initialized"""
        return self._is_initialized 
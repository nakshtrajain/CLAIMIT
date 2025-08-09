import faiss
import numpy as np
import pickle
import os
from typing import List, Tuple, Optional
from langchain.schema import Document
from .embeddings import EmbeddingManager

class FAISSVectorStore:
    def __init__(self, embedding_manager: EmbeddingManager, index_path: str = "faiss_index"):
        self.embedding_manager = embedding_manager
        self.index_path = index_path
        self.index = None
        self.documents = []
        self.is_initialized = False
    
    async def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store"""
        try:
            # Extract texts from documents
            texts = [doc.page_content for doc in documents]
            
            # Generate embeddings
            embeddings = await self.embedding_manager.get_embeddings(texts)
            
            # Initialize FAISS index if not exists
            if self.index is None:
                dimension = self.embedding_manager.get_dimension()
                self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            
            # Add embeddings to index
            self.index.add(embeddings.astype('float32'))
            
            # Store documents
            self.documents.extend(documents)
            self.is_initialized = True
            
        except Exception as e:
            raise Exception(f"Error adding documents to vector store: {str(e)}")
    
    async def similarity_search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Search for similar documents"""
        try:
            if not self.is_initialized:
                raise Exception("Vector store not initialized. Please add documents first.")
            
            # Generate query embedding
            query_embedding = await self.embedding_manager.get_single_embedding(query)
            query_embedding = query_embedding.reshape(1, -1).astype('float32')
            
            # Search in FAISS index
            scores, indices = self.index.search(query_embedding, k)
            
            # Return documents with scores
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.documents):
                    results.append((self.documents[idx], float(score)))
            
            return results
            
        except Exception as e:
            raise Exception(f"Error in similarity search: {str(e)}")
    
    async def similarity_search_with_threshold(self, query: str, k: int = 5, threshold: float = 0.5) -> List[Tuple[Document, float]]:
        """Search for similar documents with similarity threshold"""
        results = await self.similarity_search(query, k)
        return [(doc, score) for doc, score in results if score >= threshold]
    
    def save_index(self, directory: str = "data") -> None:
        """Save the FAISS index and documents"""
        try:
            os.makedirs(directory, exist_ok=True)
            
            # Save FAISS index
            index_file = os.path.join(directory, f"{self.index_path}.faiss")
            faiss.write_index(self.index, index_file)
            
            # Save documents
            docs_file = os.path.join(directory, f"{self.index_path}_docs.pkl")
            with open(docs_file, 'wb') as f:
                pickle.dump(self.documents, f)
                
        except Exception as e:
            raise Exception(f"Error saving index: {str(e)}")
    
    def load_index(self, directory: str = "data") -> None:
        """Load the FAISS index and documents"""
        try:
            # Load FAISS index
            index_file = os.path.join(directory, f"{self.index_path}.faiss")
            if os.path.exists(index_file):
                self.index = faiss.read_index(index_file)
                
                # Load documents
                docs_file = os.path.join(directory, f"{self.index_path}_docs.pkl")
                with open(docs_file, 'rb') as f:
                    self.documents = pickle.load(f)
                
                self.is_initialized = True
                
        except Exception as e:
            raise Exception(f"Error loading index: {str(e)}")
    
    def get_document_count(self) -> int:
        """Get the number of documents in the vector store"""
        return len(self.documents) if self.is_initialized else 0 
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import asyncio
import requests
import json
from config import settings

class EmbeddingManager:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.use_remote = settings.USE_REMOTE_EMBEDDINGS
        
        if not self.use_remote:
            # Local embedding model
            self.model = SentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
        else:
            # Remote embedding setup
            self.dimension = 384  # Standard dimension for all-MiniLM-L6-v2
            self.hf_api_url = f"https://api-inference.huggingface.co/models/sentence-transformers/{model_name}"
            self.headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
    
    async def get_embeddings(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for text(s)"""
        try:
            if isinstance(texts, str):
                texts = [texts]
            
            if self.use_remote:
                return await self._get_remote_embeddings(texts)
            else:
                return await self._get_local_embeddings(texts)
            
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")
    
    async def _get_local_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using local SentenceTransformers model"""
        try:
            # Run embedding generation in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None, self.model.encode, texts
            )
            
            return embeddings
            
        except Exception as e:
            raise Exception(f"Error generating local embeddings: {str(e)}")
    
    async def _get_remote_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using Hugging Face API"""
        try:
            # Prepare payload for HF API
            payload = {"inputs": texts}
            
            # Make API request
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.post(
                    self.hf_api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
            )
            
            if response.status_code != 200:
                raise Exception(f"HF API error: {response.status_code} - {response.text}")
            
            # Parse response
            embeddings = response.json()
            
            # Convert to numpy array
            if isinstance(embeddings, list):
                return np.array(embeddings)
            else:
                # Single embedding case
                return np.array([embeddings])
                
        except Exception as e:
            raise Exception(f"Error generating remote embeddings: {str(e)}")
    
    async def get_single_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        embeddings = await self.get_embeddings(text)
        return embeddings[0]
    
    def get_dimension(self) -> int:
        """Get the embedding dimension"""
        return self.dimension
    
    def is_remote(self) -> bool:
        """Check if using remote embeddings"""
        return self.use_remote 
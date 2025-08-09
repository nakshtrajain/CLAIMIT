import PyPDF2
import io
import requests
from typing import List, Optional, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class PDFLoader:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    async def load_pdf(self, file_path: str, file_id: str = None, filename: str = None) -> List[Document]:
        """Load and split PDF into chunks"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                # Split text into chunks
                chunks = self.text_splitter.split_text(text)
                
                # Convert to Document objects with enhanced metadata
                documents = [
                    Document(
                        page_content=chunk,
                        metadata={
                            "source": file_path,
                            "chunk_id": i,
                            "file_id": file_id or "unknown",
                            "filename": filename or file_path.split("/")[-1]
                        }
                    )
                    for i, chunk in enumerate(chunks)
                ]
                
                return documents
                
        except Exception as e:
            raise Exception(f"Error loading PDF {file_path}: {str(e)}")
    
    async def load_pdf_from_bytes(self, pdf_bytes: bytes, source_name: str = "uploaded_document", file_id: str = None, filename: str = None) -> List[Document]:
        """Load and split PDF from bytes"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Convert to Document objects with enhanced metadata
            documents = [
                Document(
                    page_content=chunk,
                    metadata={
                        "source": source_name,
                        "chunk_id": i,
                        "file_id": file_id or "unknown",
                        "filename": filename or source_name
                    }
                )
                for i, chunk in enumerate(chunks)
            ]
            
            return documents
            
        except Exception as e:
            raise Exception(f"Error loading PDF from bytes: {str(e)}")
    
    async def load_pdf_from_url(self, url: str, file_id: str = None, filename: str = None) -> List[Document]:
        """Load and split PDF from URL"""
        try:
            # Download PDF from URL
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            pdf_bytes = response.content
            return await self.load_pdf_from_bytes(
                pdf_bytes, 
                source_name=url,
                file_id=file_id,
                filename=filename
            )
            
        except Exception as e:
            raise Exception(f"Error loading PDF from URL {url}: {str(e)}")
    
    async def load_pdf_from_cloudinary(self, cloudinary_url: str, file_id: str = None, filename: str = None) -> List[Document]:
        """Load and split PDF from Cloudinary URL"""
        try:
            # Download PDF from Cloudinary URL
            response = requests.get(cloudinary_url, timeout=30)
            response.raise_for_status()
            
            pdf_bytes = response.content
            return await self.load_pdf_from_bytes(
                pdf_bytes,
                source_name=cloudinary_url,
                file_id=file_id,
                filename=filename
            )
            
        except Exception as e:
            raise Exception(f"Error loading PDF from Cloudinary URL {cloudinary_url}: {str(e)}") 
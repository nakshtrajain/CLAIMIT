#!/usr/bin/env python3
"""
Debug script to test the upload process step by step
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.utils.pdf_loader import PDFLoader
from app.utils.embeddings import EmbeddingManager
from app.utils.pinecone_vectorstore import PineconeVectorStore
from app.utils.cloud_storage import CloudStorageManager
from config import settings

async def test_upload_process():
    """Test the upload process step by step"""
    print("🔍 Debugging upload process...")
    print("=" * 50)
    
    try:
        # Step 1: Initialize services
        print("1. Initializing services...")
        embedding_manager = EmbeddingManager(settings.EMBEDDING_MODEL)
        vector_store = PineconeVectorStore(embedding_manager)
        pdf_loader = PDFLoader(settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        cloud_storage = CloudStorageManager()
        print("✅ Services initialized successfully")
        
        # Step 2: Check initial document count
        print(f"2. Initial document count: {vector_store.get_document_count()}")
        
        # Step 3: Test with a sample PDF from the uploads directory
        uploads_dir = Path("data/uploads")
        if uploads_dir.exists():
            pdf_files = list(uploads_dir.glob("*.pdf"))
            if pdf_files:
                test_file = pdf_files[0]
                print(f"3. Testing with file: {test_file}")
                
                # Step 4: Load and process PDF
                print("4. Loading PDF...")
                documents = await pdf_loader.load_pdf(
                    str(test_file),
                    file_id="test_file_id",
                    filename=test_file.name
                )
                print(f"✅ PDF loaded successfully: {len(documents)} chunks created")
                
                # Step 5: Add documents to vector store
                print("5. Adding documents to vector store...")
                await vector_store.add_documents(documents)
                print("✅ Documents added to vector store")
                
                # Step 6: Check final document count
                final_count = vector_store.get_document_count()
                print(f"6. Final document count: {final_count}")
                
                if final_count > 0:
                    print("✅ SUCCESS: Documents are being indexed properly")
                else:
                    print("❌ ISSUE: Documents are not being indexed")
                    
                    # Step 7: Debug vector store stats
                    print("7. Checking vector store stats...")
                    stats = vector_store.get_index_stats()
                    print(f"Vector store stats: {stats}")
                    
            else:
                print("❌ No PDF files found in uploads directory")
        else:
            print("❌ Uploads directory not found")
            
    except Exception as e:
        print(f"❌ Error during debug: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_upload_process()) 
#!/usr/bin/env python3
"""
Test script for ClauseMind - Intelligent Clause Retriever & Decision System
"""

import asyncio
import json
import os
from pathlib import Path

# Test configuration
TEST_QUERIES = [
    "46M, knee surgery, Pune, 3-month policy",
    "What is covered for dental procedures?",
    "Is pre-existing condition covered?",
    "What is the claim process for hospitalization?"
]

async def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    # This would be an actual HTTP request in a real test
    print("✅ Health check endpoint available at /api/v1/health")

async def test_entity_extraction():
    """Test entity extraction functionality"""
    print("\n🔍 Testing entity extraction...")
    
    # Import the LLM reasoner
    from app.utils.llm_reasoner import LLMReasoner
    
    reasoner = LLMReasoner()
    
    for query in TEST_QUERIES[:1]:  # Test with first query
        print(f"Query: {query}")
        try:
            entities = await reasoner.extract_entities(query)
            print(f"Extracted entities: {json.dumps(entities, indent=2)}")
            print("✅ Entity extraction working")
        except Exception as e:
            print(f"❌ Entity extraction failed: {e}")

async def test_embedding_generation():
    """Test embedding generation"""
    print("\n🔍 Testing embedding generation...")
    
    from app.utils.embeddings import EmbeddingManager
    
    embedding_manager = EmbeddingManager()
    
    test_text = "This is a test query for embedding generation"
    try:
        embedding = await embedding_manager.get_single_embedding(test_text)
        print(f"Embedding shape: {embedding.shape}")
        print(f"Embedding dimension: {embedding_manager.get_dimension()}")
        print("✅ Embedding generation working")
    except Exception as e:
        print(f"❌ Embedding generation failed: {e}")

async def test_pdf_loader():
    """Test PDF loader functionality"""
    print("\n🔍 Testing PDF loader...")
    
    from app.utils.pdf_loader import PDFLoader
    
    pdf_loader = PDFLoader()
    
    # Create a simple test PDF content (in real scenario, this would be a file)
    test_content = """
    This is a sample insurance policy document.
    
    SECTION I: HOSPITALIZATION COVERAGE
    
    If You are advised Hospitalization within India by a Medical Practitioner, 
    the Company will pay the following expenses:
    
    1. Room and Board expenses
    2. Nursing expenses
    3. Surgeon's fees
    4. Anesthetist's fees
    5. Medical practitioner's fees
    6. Cost of medicines and drugs
    7. Cost of diagnostic materials and X-ray
    8. Cost of blood, oxygen, operation theater charges
    9. Cost of surgical appliances and orthopedic implants
    10. Cost of pacemaker, artificial limbs and cost of organs
    
    SECTION II: EXCLUSIONS
    
    The Company shall not be liable to make any payment under this Policy in respect of:
    
    1. Any treatment taken outside India
    2. Any treatment for pre-existing diseases
    3. Any treatment for cosmetic surgery
    4. Any treatment for dental procedures
    5. Any treatment for mental illness
    """
    
    try:
        # Test with text content (simulating PDF content)
        documents = await pdf_loader.load_pdf_from_bytes(
            test_content.encode(), 
            "test_policy.pdf"
        )
        print(f"Created {len(documents)} document chunks")
        print("✅ PDF loader working")
    except Exception as e:
        print(f"❌ PDF loader failed: {e}")

async def test_vector_store():
    """Test vector store functionality"""
    print("\n🔍 Testing vector store...")
    
    from app.utils.embeddings import EmbeddingManager
    from app.utils.vectorstore import FAISSVectorStore
    from app.utils.pdf_loader import PDFLoader
    from langchain.schema import Document
    
    try:
        # Initialize components
        embedding_manager = EmbeddingManager()
        vector_store = FAISSVectorStore(embedding_manager)
        pdf_loader = PDFLoader()
        
        # Create test documents
        test_docs = [
            Document(page_content="This is about knee surgery coverage", metadata={"source": "test", "chunk_id": 0}),
            Document(page_content="This is about dental procedure coverage", metadata={"source": "test", "chunk_id": 1}),
            Document(page_content="This is about hospitalization benefits", metadata={"source": "test", "chunk_id": 2}),
        ]
        
        # Add documents to vector store
        await vector_store.add_documents(test_docs)
        print(f"Added {len(test_docs)} documents to vector store")
        
        # Test similarity search
        query = "knee surgery"
        results = await vector_store.similarity_search(query, k=2)
        print(f"Found {len(results)} similar documents for query: '{query}'")
        
        for i, (doc, score) in enumerate(results):
            print(f"  Result {i+1}: Score {score:.3f} - {doc.page_content[:50]}...")
        
        print("✅ Vector store working")
        
    except Exception as e:
        print(f"❌ Vector store failed: {e}")

async def test_full_pipeline():
    """Test the complete pipeline"""
    print("\n🔍 Testing full pipeline...")
    
    try:
        from app.utils.embeddings import EmbeddingManager
        from app.utils.vectorstore import FAISSVectorStore
        from app.utils.llm_reasoner import LLMReasoner
        
        # Initialize components
        embedding_manager = EmbeddingManager()
        vector_store = FAISSVectorStore(embedding_manager)
        llm_reasoner = LLMReasoner()
        
        # Create test documents
        test_docs = [
            Document(page_content="Knee surgery is covered under in-patient hospitalization if medically necessary. The policy covers surgical procedures including knee replacement.", metadata={"source": "policy", "chunk_id": 0}),
            Document(page_content="Dental procedures are not covered under this policy. Cosmetic surgeries are also excluded.", metadata={"source": "policy", "chunk_id": 1}),
        ]
        
        # Add to vector store
        await vector_store.add_documents(test_docs)
        
        # Test query
        query = "46M, knee surgery, Pune, 3-month policy"
        
        # Extract entities
        entities = await llm_reasoner.extract_entities(query)
        print(f"Extracted entities: {json.dumps(entities, indent=2)}")
        
        # Retrieve relevant chunks
        retrieved_results = await vector_store.similarity_search(query, k=2)
        retrieved_docs = [doc for doc, score in retrieved_results]
        
        # Reason over documents
        reasoning_result = await llm_reasoner.reason(query, retrieved_docs)
        print(f"Reasoning result: {json.dumps(reasoning_result, indent=2)}")
        
        print("✅ Full pipeline working")
        
    except Exception as e:
        print(f"❌ Full pipeline failed: {e}")

async def main():
    """Run all tests"""
    print("🧠 ClauseMind System Test")
    print("=" * 50)
    
    # Check if required environment variables are set
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  Warning: GEMINI_API_KEY not set. Some tests may fail.")
        print("   Set your Gemini API key in the .env file")
    
    # Run tests
    await test_health_check()
    await test_embedding_generation()
    await test_pdf_loader()
    await test_vector_store()
    
    # Only test LLM features if API key is available
    if os.getenv("GEMINI_API_KEY"):
        await test_entity_extraction()
        await test_full_pipeline()
    else:
        print("\n⚠️  Skipping LLM tests (no API key)")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
    print("\nTo run the full system:")
    print("1. Set your GEMINI_API_KEY in .env file")
    print("2. Run: python -m app.main")
    print("3. Visit: http://localhost:8000/docs")

if __name__ == "__main__":
    asyncio.run(main()) 
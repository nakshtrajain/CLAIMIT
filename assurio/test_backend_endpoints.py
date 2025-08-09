#!/usr/bin/env python3
"""
ClauseMind Backend Endpoints Test Script
========================================

This script tests all backend endpoints of the ClauseMind FastAPI project.
It validates the health, upload, query, and management endpoints.
"""

import requests
import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional

class ClauseMindTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, endpoint: str, status: str, details: str = ""):
        """Log test results"""
        result = {
            "endpoint": endpoint,
            "status": status,
            "details": details,
            "timestamp": time.strftime("%H:%M:%S")
        }
        self.test_results.append(result)
        print(f"[{result['timestamp']}] {status.upper()}: {endpoint} - {details}")
        
    def test_health_endpoint(self) -> bool:
        """Test the health check endpoint"""
        try:
            print("\n🔍 Testing Health Endpoint...")
            response = self.session.get(f"{self.base_url}/api/v1/health")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "/api/v1/health", 
                    "PASS", 
                    f"Status: {data.get('status')}, Documents: {data.get('document_count')}"
                )
                return True
            else:
                self.log_test("/api/v1/health", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("/api/v1/health", "ERROR", str(e))
            return False
    
    def test_documents_endpoint(self) -> bool:
        """Test the documents info endpoint"""
        try:
            print("\n📄 Testing Documents Endpoint...")
            response = self.session.get(f"{self.base_url}/api/v1/documents")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "/api/v1/documents", 
                    "PASS", 
                    f"Document count: {data.get('document_count')}, Initialized: {data.get('is_initialized')}"
                )
                return True
            else:
                self.log_test("/api/v1/documents", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("/api/v1/documents", "ERROR", str(e))
            return False
    
    def test_uploaded_files_endpoint(self) -> bool:
        """Test the uploaded files listing endpoint"""
        try:
            print("\n📁 Testing Uploaded Files Endpoint...")
            response = self.session.get(f"{self.base_url}/api/v1/uploaded_files")
            
            if response.status_code == 200:
                files = response.json()
                self.log_test(
                    "/api/v1/uploaded_files", 
                    "PASS", 
                    f"Found {len(files)} uploaded files"
                )
                return True
            else:
                self.log_test("/api/v1/uploaded_files", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("/api/v1/uploaded_files", "ERROR", str(e))
            return False
    
    def test_upload_pdf_endpoint(self, pdf_path: str) -> Optional[str]:
        """Test the PDF upload endpoint"""
        try:
            print(f"\n📤 Testing PDF Upload Endpoint...")
            print(f"Uploading: {pdf_path}")
            
            if not os.path.exists(pdf_path):
                self.log_test("/api/v1/upload_pdf", "FAIL", f"File not found: {pdf_path}")
                return None
            
            with open(pdf_path, 'rb') as f:
                files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
                response = self.session.post(f"{self.base_url}/api/v1/upload_pdf", files=files)
            
            if response.status_code == 200:
                data = response.json()
                filename = data.get('filename', 'unknown')
                self.log_test(
                    "/api/v1/upload_pdf", 
                    "PASS", 
                    f"Uploaded: {filename}, Chunks: {data.get('chunks_indexed')}"
                )
                return filename
            else:
                self.log_test("/api/v1/upload_pdf", "FAIL", f"Status code: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("/api/v1/upload_pdf", "ERROR", str(e))
            return None
    
    def test_query_endpoint(self, query: str, top_k: int = 5) -> bool:
        """Test the query processing endpoint"""
        try:
            print(f"\n🔍 Testing Query Endpoint...")
            print(f"Query: {query}")
            
            payload = {
                "query": query,
                "top_k": top_k
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/query", 
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                decision = data.get('decision', 'N/A')
                amount = data.get('amount', 'N/A')
                chunks = len(data.get('retrieved_chunks', []))
                
                self.log_test(
                    "/api/v1/query", 
                    "PASS", 
                    f"Decision: {decision}, Amount: {amount[:50]}..., Chunks: {chunks}"
                )
                return True
            else:
                self.log_test("/api/v1/query", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("/api/v1/query", "ERROR", str(e))
            return False
    
    def test_delete_file_endpoint(self, filename: str) -> bool:
        """Test the file deletion endpoint"""
        try:
            print(f"\n🗑️ Testing Delete File Endpoint...")
            print(f"Deleting: {filename}")
            
            response = self.session.delete(f"{self.base_url}/api/v1/uploaded_files/{filename}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "/api/v1/uploaded_files/{filename}", 
                    "PASS", 
                    f"Deleted: {filename}"
                )
                return True
            else:
                self.log_test("/api/v1/uploaded_files/{filename}", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("/api/v1/uploaded_files/{filename}", "ERROR", str(e))
            return False
    
    def test_cleanup_files_endpoint(self) -> bool:
        """Test the cleanup files endpoint"""
        try:
            print("\n🧹 Testing Cleanup Files Endpoint...")
            
            response = self.session.post(f"{self.base_url}/api/v1/cleanup_files")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "/api/v1/cleanup_files", 
                    "PASS", 
                    f"Cleanup completed: {data.get('message', 'Success')}"
                )
                return True
            else:
                self.log_test("/api/v1/cleanup_files", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("/api/v1/cleanup_files", "ERROR", str(e))
            return False
    
    def test_frontend_accessibility(self) -> bool:
        """Test if the frontend is accessible"""
        try:
            print("\n🌐 Testing Frontend Accessibility...")
            
            response = self.session.get(f"{self.base_url}/frontend/enhanced.html")
            
            if response.status_code == 200:
                content_length = len(response.text)
                self.log_test(
                    "/frontend/enhanced.html", 
                    "PASS", 
                    f"Frontend accessible, Content length: {content_length} characters"
                )
                return True
            else:
                self.log_test("/frontend/enhanced.html", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("/frontend/enhanced.html", "ERROR", str(e))
            return False
    
    def test_api_documentation(self) -> bool:
        """Test if the API documentation is accessible"""
        try:
            print("\n📚 Testing API Documentation...")
            
            response = self.session.get(f"{self.base_url}/docs")
            
            if response.status_code == 200:
                self.log_test(
                    "/docs", 
                    "PASS", 
                    "API documentation accessible"
                )
                return True
            else:
                self.log_test("/docs", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("/docs", "ERROR", str(e))
            return False
    
    def run_all_tests(self, pdf_path: str, test_query: str):
        """Run all tests in sequence"""
        print("🧠 ClauseMind Backend Endpoints Test Suite")
        print("=" * 50)
        print(f"Base URL: {self.base_url}")
        print(f"Test PDF: {pdf_path}")
        print(f"Test Query: {test_query}")
        print("=" * 50)
        
        # Test basic endpoints
        self.test_health_endpoint()
        self.test_documents_endpoint()
        self.test_uploaded_files_endpoint()
        
        # Test frontend and docs
        self.test_frontend_accessibility()
        self.test_api_documentation()
        
        # Test upload functionality
        uploaded_filename = self.test_upload_pdf_endpoint(pdf_path)
        
        # Test query functionality
        self.test_query_endpoint(test_query)
        
        # Test cleanup functionality
        if uploaded_filename:
            self.test_delete_file_endpoint(uploaded_filename)
        self.test_cleanup_files_endpoint()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        error_tests = len([r for r in self.test_results if r['status'] == 'ERROR'])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Errors: {error_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0 or error_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result['status'] in ['FAIL', 'ERROR']:
                    print(f"  - {result['endpoint']}: {result['details']}")
        
        print("\n" + "=" * 50)

def main():
    """Main function to run the test suite"""
    # Configuration
    base_url = "http://localhost:8000"
    pdf_path = "data/uploads/1d83a37c-bde9-44d9-9efd-7423a1c8394c_sample doc 1.pdf"
    test_query = "46-year-old male, knee surgery in Pune, 3-month-old insurance policy"
    
    # Check if server is running
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=5)
        if response.status_code != 200:
            print("❌ Error: ClauseMind server is not running or not accessible")
            print(f"   Please start the server first: python start_enhanced.py")
            return
    except requests.exceptions.RequestException:
        print("❌ Error: Cannot connect to ClauseMind server")
        print(f"   Please start the server first: python start_enhanced.py")
        return
    
    # Check if test PDF exists
    if not os.path.exists(pdf_path):
        print(f"❌ Error: Test PDF not found at {pdf_path}")
        print("   Using existing PDF from uploads directory...")
        # Use any existing PDF
        uploads_dir = Path("data/uploads")
        pdf_files = list(uploads_dir.glob("*.pdf"))
        if pdf_files:
            pdf_path = str(pdf_files[0])
            print(f"   Using: {pdf_path}")
        else:
            print("   No PDF files found in uploads directory")
            return
    
    # Run tests
    tester = ClauseMindTester(base_url)
    tester.run_all_tests(pdf_path, test_query)

if __name__ == "__main__":
    main() 
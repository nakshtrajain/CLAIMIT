# Render Deployment Guide for ASSURIO

## ✅ **FIXES APPLIED**

### 1. **Dynamic API Base URL**
- **Fixed**: Frontend now uses `window.location.origin + '/api/v1'` instead of hardcoded `localhost:8000`
- **Files Updated**: 
  - `templates/enhanced.html`
  - `frontend/index.html`

### 2. **Environment-Based Port Configuration**
- **Fixed**: Server now uses `$PORT` environment variable from Render
- **File Updated**: `app/main.py`

## 🚨 **REMAINING ISSUES FOR RENDER**

### **Critical Storage Problems**
1. **PDF Storage**: Files stored in `data/uploads/` will be **LOST** on redeploy
2. **FAISS Database**: 8,371 indexed documents will be **LOST** on redeploy
3. **No Persistent Storage**: Render has ephemeral file system

### **Solutions Needed**
1. **Cloud Storage** for PDFs (AWS S3, Firebase, Supabase)
2. **Managed Vector Database** (Pinecone, Weaviate, ChromaDB Cloud)
3. **Database Integration** for persistent data

## 🚀 **DEPLOYMENT STEPS**

### **Step 1: Push Changes to Git**
```bash
git add .
git commit -m "Fix: Dynamic API URLs and environment port configuration"
git push origin main
```

### **Step 2: Deploy to Render**
1. Connect your GitHub repository to Render
2. Set environment variables:
   - `GEMINI_API_KEY`: Your Gemini API key
   - `PORT`: Render will set this automatically

### **Step 3: Test Deployment**
- Your Render URL should now work independently
- Frontend will connect to Render's API, not localhost

## ⚠️ **IMPORTANT WARNINGS**

### **What Will Break on Render:**
- ✅ **Frontend**: Will work (fixed)
- ✅ **API Endpoints**: Will work
- ❌ **Document Storage**: Will be lost on redeploy
- ❌ **Vector Database**: Will be lost on redeploy
- ❌ **Uploaded Files**: Will be lost on redeploy

### **Current Status:**
- **Frontend**: ✅ Fixed (dynamic URLs)
- **Backend**: ✅ Fixed (environment port)
- **Storage**: ❌ Still needs cloud solution
- **Database**: ❌ Still needs managed vector DB

## 🔧 **NEXT STEPS FOR FULL FUNCTIONALITY**

1. **Implement Cloud Storage** for PDF uploads
2. **Migrate to Managed Vector DB** (Pinecone/Weaviate)
3. **Add Database** for persistent data storage
4. **Update CORS** for production domains

## 📞 **SUPPORT**
If you need help implementing the cloud storage solutions, let me know! 
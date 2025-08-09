# ASSURIO Cloud Deployment Guide

This guide explains how to deploy the ASSURIO project with cloud storage and vector database support.

## 🚀 Quick Start

1. **Set up cloud services** (Cloudinary, Pinecone, Hugging Face)
2. **Configure environment variables**
3. **Deploy to your preferred platform**

## 📋 Prerequisites

### Required Services

#### 1. Cloudinary (File Storage)
- Sign up at [cloudinary.com](https://cloudinary.com)
- Get your Cloud Name, API Key, and API Secret
- Free tier includes 25GB storage

#### 2. Pinecone (Vector Database)
- Sign up at [pinecone.io](https://pinecone.io)
- Create a new index with dimension 384 (for all-MiniLM-L6-v2)
- Get your API Key and Environment

#### 3. Google Gemini (LLM)
- Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

#### 4. Hugging Face (Optional - Remote Embeddings)
- Sign up at [huggingface.co](https://huggingface.co)
- Get API key from settings
- Only needed if using remote embeddings

## 🔧 Environment Configuration

Create a `.env` file in the project root:

```bash
# Copy the template
cp env_example.txt .env
```

Fill in your API keys:

```env
# Existing settings
GEMINI_API_KEY=your_actual_gemini_api_key
MODEL_NAME=models/gemini-1.5-flash
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=5

# Cloud storage settings
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret

# Pinecone settings
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=assurio-documents

# Hugging Face settings (optional)
HUGGINGFACE_API_KEY=your_huggingface_api_key
USE_REMOTE_EMBEDDINGS=false

# Storage mode
STORAGE_MODE=cloud
```

## 🐳 Local Development

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Locally

```bash
python run.py
```

Or directly:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## ☁️ Cloud Deployment

### Option 1: Render

1. **Connect your repository** to Render
2. **Create a new Web Service**
3. **Configure environment variables** in Render dashboard
4. **Set build command**: `pip install -r requirements.txt`
5. **Set start command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Option 2: Vercel

1. **Install Vercel CLI**: `npm i -g vercel`
2. **Deploy**: `vercel --prod`
3. **Set environment variables** in Vercel dashboard

### Option 3: Railway

1. **Connect your repository** to Railway
2. **Add environment variables** in Railway dashboard
3. **Deploy automatically**

### Option 4: Heroku

1. **Create Procfile** (already included)
2. **Set environment variables** in Heroku dashboard
3. **Deploy**: `git push heroku main`

## 🔍 Service Setup Details

### Cloudinary Setup

1. **Create Account**: Sign up at cloudinary.com
2. **Get Credentials**: 
   - Cloud Name (found in dashboard)
   - API Key (found in dashboard)
   - API Secret (found in dashboard)
3. **Configure**: Add credentials to `.env` file

### Pinecone Setup

1. **Create Account**: Sign up at pinecone.io
2. **Create Index**:
   - Name: `assurio-documents`
   - Dimension: `384`
   - Metric: `cosine`
   - Cloud: `aws`
   - Region: `us-west-2`
3. **Get Credentials**:
   - API Key (found in console)
4. **Configure**: Add API key to `.env` file

### Hugging Face Setup (Optional)

1. **Create Account**: Sign up at huggingface.co
2. **Get API Key**: Go to Settings → Access Tokens
3. **Configure**: Add to `.env` file
4. **Enable Remote Embeddings**: Set `USE_REMOTE_EMBEDDINGS=true`

## 🧪 Testing

### Test Upload

```bash
curl -X POST "http://localhost:8000/api/v1/upload_pdf" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.pdf"
```

### Test Query

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is covered under dental insurance?"}'
```

### Test Health

```bash
curl "http://localhost:8000/api/v1/health"
```

## 📊 Monitoring

### Vector Store Stats

```bash
curl "http://localhost:8000/api/v1/vector_stats"
```

### Document Count

```bash
curl "http://localhost:8000/api/v1/documents"
```

## 🔧 Troubleshooting

### Common Issues

1. **Pinecone Connection Error**
   - Check API key
   - Ensure index exists and is active

2. **Cloudinary Upload Error**
   - Verify cloud name, API key, and secret
   - Check file size limits

3. **Embedding Generation Error**
   - For local: Ensure SentenceTransformers is installed
   - For remote: Check Hugging Face API key

4. **Memory Issues**
   - Use remote embeddings (`USE_REMOTE_EMBEDDINGS=true`)
   - Reduce chunk size in config

### Environment Variables Checklist

- [ ] `GEMINI_API_KEY` - Google Gemini API key
- [ ] `CLOUDINARY_CLOUD_NAME` - Cloudinary cloud name
- [ ] `CLOUDINARY_API_KEY` - Cloudinary API key
- [ ] `CLOUDINARY_API_SECRET` - Cloudinary API secret
- [ ] `PINECONE_API_KEY` - Pinecone API key
- [ ] `PINECONE_INDEX_NAME` - Pinecone index name
- [ ] `HUGGINGFACE_API_KEY` - Hugging Face API key (optional)
- [ ] `USE_REMOTE_EMBEDDINGS` - Set to "true" for remote embeddings

## 💰 Cost Estimation

### Free Tier Limits

- **Cloudinary**: 25GB storage, 25GB bandwidth/month
- **Pinecone**: 1 index, 100K vectors
- **Hugging Face**: 30K requests/month
- **Google Gemini**: 15 requests/minute

### Paid Tiers

- **Cloudinary**: $89/month for 225GB storage
- **Pinecone**: $0.096 per 1000 operations
- **Hugging Face**: $9/month for 1M requests
- **Google Gemini**: $0.0005 per 1K characters

## 🚀 Production Considerations

1. **Database**: Consider adding a database for file metadata
2. **Caching**: Add Redis for query caching
3. **Monitoring**: Set up logging and monitoring
4. **Backup**: Implement backup strategies
5. **Security**: Add authentication and rate limiting

## 📚 API Documentation

Once deployed, visit:
- **Swagger UI**: `https://your-domain.com/docs`
- **ReDoc**: `https://your-domain.com/redoc`

## 🤝 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Check service status pages
4. Open an issue in the repository 
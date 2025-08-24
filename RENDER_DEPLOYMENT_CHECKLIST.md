# 🚀 Render Deployment Checklist for IntelliClaim

## ✅ Pre-Deployment Checklist

### 1. Repository Preparation
- [ ] Project is committed to Git repository
- [ ] All sensitive files are in `.gitignore`
- [ ] No API keys or secrets are committed
- [ ] Repository is accessible from Render

### 2. Environment Variables
- [ ] `GOOGLE_API_KEY` is ready (Gemini API key)
- [ ] `ENVIRONMENT` set to `production`
- [ ] `RENDER` set to `true`
- [ ] Storage directories configured:
  - [ ] `CHROMA_PERSIST_DIR=./chroma_db`
  - [ ] `UPLOAD_DIR=./uploads`
  - [ ] `FAISS_CACHE_DIR=./faiss_cache`

### 3. Code Validation
- [ ] `backend/app.py` has health check endpoint (`/health`)
- [ ] `backend/config.py` supports environment variables
- [ ] `backend/setup_storage.py` exists and is executable
- [ ] `backend/build.sh` exists and is executable
- [ ] `render.yaml` is configured correctly with Python 3.13
- [ ] `backend/requirements.txt` has Python 3.13 compatible versions (no Rust dependencies)
- [ ] Uses lightweight HuggingFace embeddings (`sentence-transformers/all-MiniLM-L6-v2`)
- [ ] PDF processing uses PyPDF2 instead of PyMuPDF (fitz)
- [ ] Frontend UI components use correct import paths (relative paths, not `src/` paths)
- [ ] Frontend API configuration uses environment variables
- [ ] Frontend builds successfully locally (`npm run build`)

## 🚀 Deployment Steps

### Step 1: Backend Deployment
1. **Go to Render Dashboard**
   - Visit [render.com](https://render.com)
   - Sign in or create account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your Git repository
   - Select the repository branch (usually `main` or `master`)

3. **Configure Backend Service**
   - **Name:** `intelliclaim-backend`
   - **Environment:** `Python 3`
   - **Region:** Choose closest to your users
   - **Branch:** `main` (or your default branch)
   - **Build Command:** `cd backend && chmod +x build.sh && ./build.sh`
   - **Start Command:** `cd backend && python setup_storage.py && uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Starter (Free tier)

4. **Set Environment Variables**
   - `GOOGLE_API_KEY`: Your actual Gemini API key
   - `ENVIRONMENT`: `production`
   - `RENDER`: `true`
   - `CHROMA_PERSIST_DIR`: `./chroma_db`
   - `UPLOAD_DIR`: `./uploads`
   - `FAISS_CACHE_DIR`: `./faiss_cache`

5. **Deploy**
   - Click "Create Web Service"
   - Wait for build and deployment (5-10 minutes)
   - Note the service URL (e.g., `https://intelliclaim-backend.onrender.com`)

### Step 2: Frontend Deployment
1. **Create Static Site**
   - Click "New +" → "Static Site"
   - Connect same Git repository

2. **Configure Frontend Service**
   - **Name:** `intelliclaim-frontend`
   - **Branch:** `main` (or your default branch)
   - **Build Command:** `cd frontend && npm install && npm run build`
   - **Publish Directory:** `frontend/build`
   - **Plan:** Starter (Free tier)

3. **Set Environment Variables**
   - `REACT_APP_API_URL`: Your backend URL from Step 1 (e.g., `https://intelliclaim-backend.onrender.com`)

4. **Deploy**
   - Click "Create Static Site"
   - Wait for build and deployment (3-5 minutes)
   - Note the site URL (e.g., `https://intelliclaim-frontend.onrender.com`)

**Important:** The frontend build should now work correctly after fixing the import paths in the UI components.

## 🔧 Post-Deployment Configuration

### 1. Update CORS Configuration
After getting your frontend URL, update `backend/app.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://intelliclaim-frontend.onrender.com",  # Your actual frontend URL
        "http://localhost:3000"  # Keep for local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Update Frontend API Configuration
Update `frontend/src/config/api.js` with your actual backend URL:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://intelliclaim-backend.onrender.com';
```

### 3. Redeploy Backend
- Push changes to trigger auto-deploy
- Or manually redeploy from Render dashboard

## 🧪 Testing & Validation

### 1. Health Check
Test your backend health endpoint:
```bash
curl https://your-backend-domain.onrender.com/health
```
Expected response:
```json
{"status": "healthy", "timestamp": "2024-01-01T00:00:00"}
```

### 2. Frontend-Backend Integration
1. **Upload Test Document**
   - Go to your frontend URL
   - Upload a test PDF document
   - Verify upload success

2. **Test Query Functionality**
   - Ask a question about the uploaded document
   - Verify response generation
   - Check for any errors in browser console

3. **Monitor Logs**
   - Check Render dashboard for any errors
   - Monitor application logs
   - Verify environment variables are set correctly

## 📊 Monitoring & Maintenance

### 1. Performance Monitoring
- Monitor response times
- Check error rates
- Watch resource usage

### 2. Storage Management
- Monitor upload directory size
- Check ChromaDB performance
- Clean up old files if needed

### 3. API Usage
- Monitor Gemini API usage
- Check rate limits
- Optimize queries if needed

## 🚨 Troubleshooting

### Common Issues

#### 1. Build Failures
- **Python Version Issues**: Ensure `pythonVersion: "3.11"` is set in render.yaml
- **Dependency Conflicts**: Check that requirements.txt has Python 3.11 compatible versions
- **Metadata Preparation Hanging**: Usually caused by Python 3.13 + incompatible packages
- **Rust Dependencies**: PyMuPDF and other Rust-based packages cause build failures on Render
- **Pinecone/Sentence-transformers**: These packages are not compatible with Python 3.13
- Check build logs in Render dashboard for specific error messages
- Verify all dependencies in `requirements.txt`
- Ensure build scripts are executable

#### 2. Runtime Errors
- Check application logs
- Verify environment variables
- Test locally with same configuration

#### 3. CORS Issues
- Verify CORS configuration
- Check frontend-backend URLs
- Test with browser developer tools

#### 4. Frontend Build Issues
- **Import Path Errors**: Ensure all UI components use relative paths (e.g., `../../lib/utils` not `src/lib/utils`)
- **Missing Dependencies**: Check that all required packages are in `package.json`
- **Environment Variables**: Verify `REACT_APP_API_URL` is set correctly
- **Build Logs**: Check Render build logs for specific error messages

#### 4. Storage Issues
- Check directory permissions
- Verify storage paths
- Monitor disk space usage

### Debug Commands
```bash
# Test backend locally with Render config
cd backend
export RENDER=true
export ENVIRONMENT=production
python setup_storage.py
uvicorn app:app --host 0.0.0.0 --port 8000

# Test storage setup
python setup_storage.py
```

## 🔄 Updates & Scaling

### 1. Code Updates
- Push to Git repository
- Render will auto-deploy
- Monitor deployment logs

### 2. Environment Variable Changes
- Update in Render dashboard
- Redeploy service
- Verify changes take effect

### 3. Scaling Considerations
- Upgrade to paid plans for better performance
- Consider managed databases
- Implement caching strategies

## 📞 Support Resources

- [Render Documentation](https://render.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Deployment Guide](https://create-react-app.dev/docs/deployment/)
- [ChromaDB Documentation](https://docs.trychroma.com/)

---

**🎯 Goal**: Successfully deploy IntelliClaim on Render with both backend and frontend services running and connected.

**⏱️ Estimated Time**: 30-45 minutes for initial deployment

**🔍 Success Criteria**: 
- Backend responds to health checks
- Frontend loads without errors
- File uploads work
- Query processing functions correctly
- No CORS errors in browser console

# 🚂 Railway Deployment Guide for IntelliClaim Backend

This guide will help you deploy your IntelliClaim backend on Railway and connect it with your Render-deployed frontend.

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be in a GitHub repo
3. **Google API Key**: For Gemini AI integration
4. **Frontend URL**: Your Render-deployed frontend URL

## 🚀 Step-by-Step Deployment

### 1. **Connect GitHub Repository**
- Go to [railway.app](https://railway.app)
- Click "New Project"
- Select "Deploy from GitHub repo"
- Choose your `intelliclaim-project` repository

### 2. **Configure Backend Service**
- Railway will automatically detect it's a Python project
- Set the **Root Directory** to `backend`
- **Option A (Recommended)**: Leave Build Command empty (Railway will auto-detect)
- **Option B**: Set Build Command to: `python railway_build.py`
- Set the **Start Command** to: `python setup_storage.py && uvicorn app:app --host 0.0.0.0 --port $PORT`

### 3. **Set Environment Variables**
In Railway dashboard, add these environment variables:

```bash
GOOGLE_API_KEY=your_google_api_key_here
ENVIRONMENT=production
RAILWAY=true
CHROMA_PERSIST_DIR=./chroma_db
UPLOAD_DIR=./uploads
FAISS_CACHE_DIR=./faiss_cache
```

### 4. **Deploy**
- Click "Deploy" and wait for the build to complete
- Railway will provide you with a URL like: `https://your-app-name.railway.app`

## 🔗 Connect Frontend to Railway Backend

### 1. **Update Frontend API Configuration**
Once deployed, update your frontend's API configuration:

```javascript
// In frontend/src/config/api.js
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-app-name.railway.app';
```

### 2. **Set Frontend Environment Variable**
In your Render frontend dashboard, add:
```bash
REACT_APP_API_URL=https://your-app-name.railway.app
```

### 3. **Redeploy Frontend**
- Commit and push the changes
- Render will automatically redeploy

## 🔧 Railway-Specific Optimizations

### 1. **Build Process**
- Uses `railway_build.sh` for optimized dependency installation
- Installs packages in stages to avoid memory issues
- Uses Railway's nixpacks builder for better compatibility

### 2. **Runtime Configuration**
- Health check at `/health` endpoint
- Automatic restart on failure
- Optimized for Railway's infrastructure

### 3. **Storage**
- Uses Railway's persistent storage for uploads and databases
- Automatic directory creation and permissions

## 📊 Monitoring & Debugging

### 1. **Railway Dashboard**
- View logs in real-time
- Monitor resource usage
- Check deployment status

### 2. **Health Checks**
- Endpoint: `/health`
- Timeout: 300 seconds
- Automatic restart on failure

### 3. **Common Issues & Solutions**

#### Build Failures
```bash
# Check build logs in Railway dashboard
# Common causes: memory limits, dependency conflicts
```

#### Runtime Errors
```bash
# Check application logs
# Verify environment variables are set
# Ensure Google API key is valid
```

## 🔄 Updating the Backend

### 1. **Automatic Deployment**
- Push to your main branch
- Railway automatically redeploys

### 2. **Manual Deployment**
- Go to Railway dashboard
- Click "Deploy" button
- Monitor build process

## 💰 Cost Considerations

- **Railway**: Pay-per-use, typically $5-20/month for small apps
- **Render**: Free tier available, but limited for ML workloads
- **Combination**: Frontend on Render (free), Backend on Railway (paid)

## ✅ Verification Checklist

- [ ] Backend deploys successfully on Railway
- [ ] Health check endpoint responds
- [ ] Frontend can connect to Railway backend
- [ ] Document upload works
- [ ] AI queries function properly
- [ ] Environment variables are set correctly

## 🆘 Troubleshooting

### Build Issues
- Check `railway_build.sh` logs
- Verify Python version compatibility
- Ensure all dependencies are in `requirements-railway.txt`

### Runtime Issues
- Check application logs in Railway dashboard
- Verify environment variables
- Test endpoints individually

### Connection Issues
- Verify CORS settings in backend
- Check frontend API configuration
- Ensure Railway URL is accessible

## 📞 Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **GitHub Issues**: Create issues in your repository

---

**Happy Deploying! 🚀**

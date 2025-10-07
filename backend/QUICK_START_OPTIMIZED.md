# Quick Start: Optimized Docker Image

## 🎯 Quick Facts

| Metric | Value |
|--------|-------|
| **Image Size** | 1.9GB (was 12.1GB) |
| **Reduction** | 84% smaller |
| **Build Time** | ~8-10 minutes |
| **PyTorch** | 2.1.0+cpu (CPU-only) |
| **Status** | ✅ Production Ready |

## 🚀 Build & Deploy

### Build Locally
```bash
cd backend
docker build -t intelliclaim-backend:optimized .
```

### Run Locally
```bash
docker run -p 8000:8000 \
  -e AIMLAPI_KEY=your_key \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -e AWS_S3_BUCKET=your_bucket \
  -e AWS_RDS_ENDPOINT=your_endpoint \
  -e AWS_RDS_DB_NAME=your_db \
  -e AWS_RDS_USERNAME=your_user \
  -e AWS_RDS_PASSWORD=your_pass \
  intelliclaim-backend:optimized
```

### Deploy to AWS ECR
```bash
# Tag for ECR
docker tag intelliclaim-backend:optimized \
  <account-id>.dkr.ecr.<region>.amazonaws.com/intelliclaim-backend:latest

# Login to ECR
aws ecr get-login-password --region <region> | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.<region>.amazonaws.com

# Push
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/intelliclaim-backend:latest
```

## ✅ Verification

### Check Image Size
```bash
docker images | grep intelliclaim-backend
# Should show ~1.9GB
```

### Test Functionality
```bash
docker run --rm intelliclaim-backend:optimized \
  python -c "import torch; print(f'PyTorch: {torch.__version__}')"
# Should output: PyTorch: 2.1.0+cpu
```

### Health Check
```bash
# Start container
docker run -d -p 8000:8000 --name test-backend intelliclaim-backend:optimized

# Wait 30 seconds for startup
sleep 30

# Check health
curl http://localhost:8000/health

# Cleanup
docker stop test-backend
docker rm test-backend
```

## 📊 What Changed

1. **CPU-Only PyTorch** - Removed GPU support (not needed)
2. **Multi-Stage Build** - Separated build and runtime
3. **.dockerignore** - Excluded unnecessary files
4. **Pinned Versions** - Reproducible builds

## ⚠️ Important Notes

- ✅ **No code changes** required in application
- ✅ **Same functionality** - all features work identically
- ✅ **Faster deployments** - 84% less data to transfer
- ✅ **Lower costs** - reduced ECR storage and transfer

## 📚 More Information

- **Detailed Results**: See `OPTIMIZATION_RESULTS.md`
- **Technical Guide**: See `DOCKER_OPTIMIZATION.md`
- **Build Scripts**: 
  - Windows: `build-optimized.ps1`
  - Linux/Mac: `build-optimized.sh`

## 🆘 Need Help?

### Common Issues

**Build fails with "No matching distribution"**
→ Check internet connection to PyTorch CDN

**Image size still large**
→ Ensure you're building with the new Dockerfile

**Import errors at runtime**
→ Check that all dependencies in requirements.txt

### Support
Check the troubleshooting section in `DOCKER_OPTIMIZATION.md`

---

**Ready to deploy!** 🚀


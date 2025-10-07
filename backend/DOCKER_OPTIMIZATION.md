# Docker Image Optimization Guide

## Problem
The original Docker image was **~7.6GB** in size, primarily due to:
- Full PyTorch installation with CUDA support (~7.31GB)
- Inefficient layer caching
- No build/runtime separation
- Unnecessary files in build context

## Solution Implemented

### 1. CPU-Only PyTorch (Major Size Reduction)
**Reduced from ~7.31GB to ~2GB**

Changed from:
```
torch>=2.0.0
```

To:
```
--extra-index-url https://download.pytorch.org/whl/cpu
torch==2.1.0+cpu
```

**Why this works:**
- The application runs on CPU (set in `chatgpt_app.py`: `self.device = "cpu"`)
- Full PyTorch includes CUDA libraries for GPU support (unnecessary for our deployment)
- CPU-only version provides same functionality at ~70% smaller size

### 2. Multi-Stage Docker Build
**Reduced build dependencies and optimized layers**

**Before:**
- Single stage with all build tools in final image
- Build dependencies (gcc, g++, build-essential) remained in production image

**After:**
- **Builder stage**: Compiles dependencies with build tools
- **Runtime stage**: Clean slim image with only runtime dependencies
- Copies only the compiled virtual environment from builder

**Benefits:**
- Build tools excluded from final image (~300MB savings)
- Cleaner separation of concerns
- Better layer caching

### 3. .dockerignore File
**Reduced build context size**

Excludes:
- Virtual environments (`venv/`)
- Cache directories (`chroma_db/`, `faiss_cache/`)
- Test files and development scripts
- Documentation and temporary files
- Git history

**Benefits:**
- Faster build context transfer to Docker daemon
- Smaller intermediate layers
- Reduced build time

### 4. Optimized Dependency Management
**Pinned versions for reproducibility**

- Changed from `>=` to `==` for critical dependencies
- Ensures consistent builds across environments
- Prevents unexpected version upgrades

## Expected Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Image Size | ~7.6GB | ~2.0GB | **73% reduction** |
| Build Time | ~15-20 min | ~8-12 min | **~40% faster** |
| Layer Efficiency | Poor | Good | Better caching |

## Building the Optimized Image

```bash
# From the backend directory
docker build -t intelliclaim-backend:optimized .

# Check the image size
docker images intelliclaim-backend:optimized

# Run the container
docker run -p 8000:8000 \
  -e AIMLAPI_KEY=your_key_here \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  intelliclaim-backend:optimized
```

## Verification

After building, verify the optimization:

```bash
# Check image size
docker images | grep intelliclaim-backend

# Check layer sizes
docker history intelliclaim-backend:optimized --no-trunc --format "table {{.Size}}\t{{.CreatedBy}}" | head -n 20
```

You should see:
- Total image size: ~2.0-2.5GB (down from 7.6GB)
- Largest layer (pip install): ~2GB (down from 7.31GB)
- No CUDA/GPU libraries in image

## Technical Details

### PyTorch CPU vs Full Version

**Full PyTorch includes:**
- CUDA toolkit (~3GB)
- cuDNN libraries (~1GB)
- NCCL for multi-GPU (~500MB)
- ROCm for AMD GPUs (~2GB)

**CPU-only includes:**
- Core PyTorch functionality
- CPU optimizations (MKL, OpenMP)
- All necessary features for inference

### Why This Doesn't Affect Performance

Our application:
1. **Explicitly uses CPU**: `self.device = "cpu"`
2. **No GPU available** in deployment (ECS Fargate, Render)
3. **Inference-only workload**: No training required
4. **Small model size**: Insurance BERT models are lightweight

### Multi-Stage Build Mechanics

```dockerfile
# Stage 1: Builder (discarded after build)
FROM python:3.11-slim as builder
RUN apt-get install build-essential  # Heavy build tools
RUN pip install -r requirements.txt  # Compile dependencies
# Creates: /opt/venv

# Stage 2: Runtime (final image)
FROM python:3.11-slim as runtime
COPY --from=builder /opt/venv /opt/venv  # Only compiled artifacts
# Result: Clean runtime without build tools
```

## Additional Optimizations Considered

### Not Implemented (Why)

1. **Alpine Linux Base**
   - ❌ Compatibility issues with scientific Python packages
   - ❌ musl vs glibc differences cause segfaults
   - ❌ Slower builds due to compiling from source

2. **Distroless Images**
   - ❌ No shell for debugging
   - ❌ Health checks require shell
   - ❌ Operational complexity

3. **sentence-transformers Only**
   - ❌ Current code uses `transformers.AutoModel`
   - ✅ Could save ~200MB but requires code refactoring

## Maintenance

### Updating Dependencies

When updating Python packages:

1. **Check PyTorch compatibility**:
   ```bash
   pip index versions torch --extra-index-url https://download.pytorch.org/whl/cpu
   ```

2. **Test build size**:
   ```bash
   docker build --target runtime -t test .
   docker images test
   ```

3. **Verify functionality**:
   ```bash
   docker run test python -c "import torch; print(torch.__version__)"
   ```

### Monitoring Image Size

Set up CI/CD checks:
```yaml
- name: Check image size
  run: |
    SIZE=$(docker images --format "{{.Size}}" intelliclaim-backend:latest)
    if [ "$SIZE" -gt "3GB" ]; then
      echo "Warning: Image size exceeded 3GB"
      exit 1
    fi
```

## Troubleshooting

### Build Fails with "No matching distribution"

**Problem**: PyTorch CPU version not found

**Solution**:
```bash
# Verify index URL is accessible
curl https://download.pytorch.org/whl/cpu/

# Try specific version
pip install torch==2.1.0+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html
```

### Runtime Error: "libgomp.so.1 not found"

**Problem**: Missing OpenMP library for CPU PyTorch

**Solution**: Add to Dockerfile runtime stage:
```dockerfile
RUN apt-get install -y libgomp1
```

### Import Error: "No module named 'torch'"

**Problem**: Virtual environment path not in PATH

**Solution**: Verify `ENV PATH="/opt/venv/bin:$PATH"` in runtime stage

## References

- [PyTorch CPU Installation Guide](https://pytorch.org/get-started/locally/)
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Best Practices for Python Docker Images](https://docs.docker.com/language/python/build-images/)


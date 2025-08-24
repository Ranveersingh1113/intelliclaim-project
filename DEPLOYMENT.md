# IntelliClaim Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Gemini API Key
- Git

### 1. Environment Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend Setup
```bash
cd frontend
npm install
```

### 2. Configuration

#### Environment Variables
Create `.env` file in the backend directory:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
ENVIRONMENT=development
```

#### API Key Setup
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

### 3. Running the System

#### Start Backend
```bash
cd backend
python app.py
```
Backend will be available at: http://localhost:8000

#### Start Frontend
```bash
cd frontend
npm start
```
Frontend will be available at: http://localhost:3000

### 4. Testing the System

Run the comprehensive test suite:
```bash
python test_system.py
```

## 🔧 Advanced Configuration

### Production Deployment

#### Using Docker (Recommended)

Create `Dockerfile` for backend:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "app.py"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/chroma_db:/app/chroma_db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

#### Using PM2 (Node.js Process Manager)

Install PM2:
```bash
npm install -g pm2
```

Create `ecosystem.config.js`:
```javascript
module.exports = {
  apps: [{
    name: 'intelliclaim-backend',
    script: 'app.py',
    interpreter: 'python',
    cwd: './backend',
    env: {
      GOOGLE_API_KEY: 'your_api_key'
    }
  }, {
    name: 'intelliclaim-frontend',
    script: 'npm',
    args: 'start',
    cwd: './frontend'
  }]
}
```

Start with PM2:
```bash
pm2 start ecosystem.config.js
```

### Security Considerations

#### 1. API Key Security
- Never commit API keys to version control
- Use environment variables
- Rotate keys regularly

#### 2. CORS Configuration
Update `app.py` for production:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

#### 3. Rate Limiting
Install and configure rate limiting:
```bash
pip install slowapi
```

Add to `app.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/query")
@limiter.limit("10/minute")
async def process_query_endpoint(request: QueryRequest):
    # ... existing code
```

### Monitoring and Logging

#### 1. Application Logging
Configure structured logging:
```python
import structlog

logger = structlog.get_logger()
logger.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

#### 2. Health Checks
Add comprehensive health checks:
```python
@app.get("/health")
async def health_check():
    try:
        # Check vector store
        collection = rag_system.vector_store._collection
        vector_store_healthy = collection is not None
        
        # Check Gemini API
        gemini_healthy = await test_gemini_connection()
        
        return {
            "status": "healthy" if vector_store_healthy and gemini_healthy else "degraded",
            "services": {
                "vector_store": "healthy" if vector_store_healthy else "unhealthy",
                "gemini_api": "healthy" if gemini_healthy else "unhealthy"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
```

### Performance Optimization

#### 1. Caching
Implement Redis caching:
```bash
pip install redis
```

Add caching to `app.py`:
```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@app.post("/query")
async def process_query_endpoint(request: QueryRequest):
    # Check cache first
    cache_key = f"query:{hash(request.query)}"
    cached_result = redis_client.get(cache_key)
    
    if cached_result:
        return json.loads(cached_result)
    
    # Process query
    response = await rag_system.process_query(query=request.query)
    
    # Cache result for 1 hour
    redis_client.setex(cache_key, 3600, json.dumps(response.dict()))
    
    return response
```

#### 2. Database Optimization
- Use connection pooling for vector store
- Implement document indexing
- Add query result caching

#### 3. Frontend Optimization
- Implement lazy loading
- Add service worker for caching
- Optimize bundle size

## 📊 Monitoring Dashboard

### Metrics to Track
- Query processing time
- Success/failure rates
- API response times
- Document upload success rates
- System resource usage

### Recommended Tools
- **Application Monitoring**: Sentry, LogRocket
- **Infrastructure Monitoring**: Prometheus, Grafana
- **Log Management**: ELK Stack, Fluentd

## 🔄 CI/CD Pipeline

### GitHub Actions Example
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy IntelliClaim

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: python test_system.py
        env:
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Add your deployment commands here
          echo "Deploying to production..."
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Gemini API Errors
- Check API key validity
- Verify API quota limits
- Ensure proper error handling

#### 2. Vector Store Issues
- Check disk space for ChromaDB
- Verify document processing
- Monitor embedding model performance

#### 3. Frontend Connection Issues
- Verify CORS configuration
- Check API endpoint URLs
- Ensure backend is running

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Use load balancers
- Implement session management
- Consider microservices architecture

### Vertical Scaling
- Optimize memory usage
- Use faster embedding models
- Implement connection pooling

### Database Scaling
- Consider distributed vector stores
- Implement sharding strategies
- Use read replicas for queries

## 🔐 Security Checklist

- [ ] API keys secured
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] Error messages sanitized
- [ ] HTTPS enabled
- [ ] Regular security updates
- [ ] Access logging enabled
- [ ] Backup strategy in place

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review system logs
3. Run the test suite
4. Create an issue in the repository

---

**Note**: This deployment guide covers the essential aspects of deploying IntelliClaim. Adjust configurations based on your specific infrastructure and requirements. 
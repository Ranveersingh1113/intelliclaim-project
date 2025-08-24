# IntelliClaim - AI-Powered Insurance Claims Processing

## 🎯 Project Overview

IntelliClaim is a next-generation AI-powered document processing system designed for insurance claims adjudication. It uses advanced RAG (Retrieval-Augmented Generation) technology with Google's Gemini AI to provide intelligent, explainable decisions on insurance claims.

## ✨ Key Features

- **🤖 Gemini AI Integration**: Powered by Google's Gemini 1.5 Pro for intelligent reasoning
- **📄 Multi-Format Support**: PDF, DOCX, and email document processing
- **🧠 Multi-Agent RAG Pipeline**: Specialized agents for query understanding, retrieval, and decision making
- **🎯 Clause-Aware Retrieval**: Insurance-specific keyword biasing and context windowing
- **⚡ Async Processing**: Efficient document processing with intelligent chunking
- **📊 Real-time Analytics**: Processing metrics and success rates
- **🛡️ Production Ready**: Robust error handling and fallback mechanisms
- **🔍 Intelligent Context Building**: Dynamic chunking with relevance scoring

## 🚀 Current Status

✅ **Backend**: Fully functional with Gemini AI integration  
✅ **Frontend**: Modern React UI with Tailwind CSS  
✅ **RAG Pipeline**: Multi-agent system with specialized agents  
✅ **Document Processing**: PDF/DOCX/Email with intelligent chunking  
✅ **API Endpoints**: Complete REST API with health checks  
✅ **Vector Storage**: ChromaDB with BGE-M3 embeddings  
✅ **Error Handling**: Comprehensive fallbacks and retry logic  
✅ **Configuration**: Environment-driven config system  

## 🆕 Latest Updates

### **Enhanced Document Processing**
- **Multi-Format Support**: PDF, DOCX, and email documents
- **Intelligent Chunking**: Dynamic chunk size based on document length
- **Content Hashing**: Persistent caching with document hash-based keys
- **Idempotent Ingestion**: Skip re-indexing of duplicate documents

### **Advanced Retrieval System**
- **Clause Biasing**: Insurance-specific keyword prioritization
- **Context Windowing**: Intelligent excerpt selection around query terms
- **Hybrid Scoring**: Combines semantic similarity with keyword matching
- **Retrieval Caching**: Performance optimization for repeated queries

### **Production Features**
- **Configuration Management**: Environment-driven settings
- **Background Processing**: Async document ingestion
- **URL Upload Support**: Direct document URL processing
- **Comprehensive Logging**: Debug and production logging levels

## 🛠️ Technical Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   AI Services   │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (Gemini)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Vector Store  │
                       │   (ChromaDB)    │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Multi-Agent   │
                       │   RAG Pipeline  │
                       └─────────────────┘
```

## 📊 Performance Metrics

- **Query Processing**: < 5 seconds average
- **Document Upload**: < 30 seconds for 10MB PDF
- **Vector Indexing**: < 10 seconds for 100-page documents
- **Decision Accuracy**: > 85% confidence threshold
- **System Uptime**: 99.9% availability target
- **Memory Usage**: < 2GB for Gemini-only setup

## 🔍 Advanced Features

### **Clause Biasing System**
The system automatically detects insurance-specific terms and biases retrieval:
- **Waiting Period**: Initial waiting and cooling periods
- **Pre-existing Conditions**: PED and pre-existing condition exclusions
- **Maternity**: Pregnancy and childbirth coverage
- **Cataract**: Eye surgery specifics
- **Organ Donor**: Donor expense coverage
- **No Claim Discount**: NCD calculations
- **Preventive Care**: Health check coverage
- **Hospital Coverage**: Inpatient treatment
- **AYUSH**: Alternative medicine coverage
- **Room Rent**: ICU and accommodation limits

### **Multi-Agent RAG Pipeline**
1. **Query Understanding Agent**: Entity extraction and query structuring
2. **Semantic Retrieval Agent**: Document retrieval with relevance scoring
3. **Decision Reasoning Agent**: AI-powered decision making
4. **Explainability Agent**: Audit trails and clause mappings

### **Intelligent Processing**
- **Dynamic Chunking**: Adaptive chunk size based on document length
- **Context Windowing**: Smart excerpt selection around query terms
- **Retrieval Caching**: Performance optimization for repeated queries
- **Background Ingestion**: Async document processing

## 🔧 Development Setup

### Prerequisites
- **Python**: 3.8+
- **Node.js**: 16+
- **Google Gemini API Key**: Required for AI processing

### Quick Start

#### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY="your_gemini_api_key"
export ENVIRONMENT="development"

# Run the server
python app.py
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm start
```

#### 3. Test the System
```bash
# Test API endpoints
python test_api.py

# Test Gemini integration
python test_gemini_integration.py

# Comprehensive system test
python test_system.py
```

### Environment Variables
```env
# Required
GOOGLE_API_KEY=your_gemini_api_key

# Optional
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
```

## 🚀 API Usage

### Main Query Endpoint
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Patient, 62M, cataract surgery in Pune; policy 14 months. Eligible?"
  }'
```

### Document Upload (File)
```bash
curl -X POST "http://localhost:8000/upload-document" \
  -F "file=@policy.pdf"
```

### Document Upload (URL)
```bash
curl -X POST "http://localhost:8000/upload-document-url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/policy.pdf",
    "async_mode": false
  }'
```

### System Endpoints
```bash
# Health check
GET /health

# System statistics
GET /system-stats

# List documents
GET /documents

# Test Gemini connection
GET /test-gemini
```

## 🧪 Testing & Validation

### Run All Tests
```bash
# Backend tests
python test_system.py
python test_api.py
python test_gemini_integration.py

# Frontend tests
cd frontend && npm test
```

### Performance Testing
```bash
# Test with sample documents
python -c "
import requests
import time

start = time.time()
response = requests.post('http://localhost:8000/query', 
  json={'query': 'What is covered in this policy?'}
)
print(f'Response time: {time.time() - start:.2f}s')
print(f'Status: {response.status_code}')
print(f'Decision: {response.json()}')
"
```

### Test Coverage
- Unit tests for all components
- Integration tests for API endpoints
- End-to-end tests for complete workflows
- Performance tests for scalability

## 📈 Monitoring & Analytics

### Key Metrics
- Query processing time
- Decision accuracy rates
- System resource usage
- API response times
- Error rates and types

### Monitoring Tools
- Application performance monitoring
- Infrastructure monitoring
- Log aggregation and analysis
- Real-time alerting

## 🚀 Deployment

### Production Setup
```bash
# Install production dependencies
pip install -r requirements.txt

# Set production environment
export ENVIRONMENT=production
export GOOGLE_API_KEY="your_production_key"

# Run with uvicorn
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔐 Security Features

- **API Key Authentication**: Gemini API key validation
- **Input Sanitization**: Document type and size validation
- **Secure File Handling**: Temporary file cleanup
- **Error Masking**: Production-safe error messages
- **CORS Configuration**: Configurable cross-origin settings

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

### Code Standards
- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React
- Write comprehensive documentation
- Include unit tests for all new features

## 📚 Documentation

- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Configuration**: See `backend/config.py` for all settings

## 🆘 Troubleshooting

### Common Issues

#### Gemini API Errors
```bash
# Verify API key
echo $GOOGLE_API_KEY

# Check quota limits
curl "https://generativelanguage.googleapis.com/v1beta/models?key=$GOOGLE_API_KEY"
```

#### Document Processing Issues
```bash
# Check file permissions
ls -la backend/uploads/

# Verify document format
file your_document.pdf
```

#### Vector Store Issues
```bash
# Check ChromaDB status
ls -la backend/chroma_db/

# Clear cache if needed
rm -rf backend/chroma_db/
```



---

**🚀 Ready to revolutionize insurance claims processing? Start with the quick setup above and experience the power of AI-driven decision making!**

*For questions and support, check the troubleshooting section or create a GitHub issue.* 
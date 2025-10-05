"""
Configuration settings for IntelliClaim system
"""

import os
from typing import Dict, Any, Optional

class Config:
    # API Configuration
    API_TITLE = "IntelliClaim RAG API"
    API_VERSION = "1.0.0"
    API_HOST = "0.0.0.0"
    # API_PORT is now handled by the PORT environment variable (see below)
    
    # Model Configuration
    EMBEDDING_MODEL = "llmware/industry-bert-insurance-v0.1"  # Insurance-specific BERT model, 768d
    EMBEDDING_FALLBACK_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Local fallback, 384d
    LLM_MODEL = "openai/gpt-5-2025-08-07"  # Hackathon requirement

    # API Keys
    AIMLAPI_KEY = os.getenv("AIMLAPI_KEY")
    
    # Document Processing
    CHUNK_SIZE = 2000
    CHUNK_OVERLAP = 100
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Vector Store - Updated for Render compatibility
    VECTOR_STORE_PATH = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    UPLOAD_PATH = os.getenv("UPLOAD_DIR", "./uploads")
    FAISS_CACHE_PATH = os.getenv("FAISS_CACHE_DIR", "./faiss_cache")
    
    # Retrieval Settings
    TOP_K_DOCUMENTS = 5
    SIMILARITY_THRESHOLD = 0.7
    
    # Processing Settings
    MAX_PROCESSING_TIME = 30  # seconds
    BATCH_SIZE = 50
    
    # Security
    ALLOWED_ORIGINS = ["*"]  # Configure for production
    API_KEY_HEADER = "X-API-Key"
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Feature Flags
    ENABLE_CACHING = True
    ENABLE_RATE_LIMITING = False
    ENABLE_AUDIT_TRAIL = True
    ENABLE_EXPLAINABILITY = True
    
    # Render-specific configuration
    RENDER_DEPLOYMENT = os.getenv("RENDER", "false").lower() == "true"
    PORT = int(os.getenv("PORT", 8000))  # Render uses $PORT environment variable
    
    # File type restrictions
    ALLOWED_FILE_TYPES = [".pdf", ".docx", ".txt", ".doc"]
    
    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        return {
            "embedding_model": cls.EMBEDDING_MODEL,
            "embedding_fallback_model": cls.EMBEDDING_FALLBACK_MODEL,
            "llm_model": cls.LLM_MODEL,
            "chunk_size": cls.CHUNK_SIZE,
            "chunk_overlap": cls.CHUNK_OVERLAP,
            "top_k": cls.TOP_K_DOCUMENTS,
            "similarity_threshold": cls.SIMILARITY_THRESHOLD
        }
    
    @classmethod
    def get_api_config(cls) -> Dict[str, Any]:
        return {
            "title": cls.API_TITLE,
            "version": cls.API_VERSION,
            "host": cls.API_HOST,
            "port": cls.PORT
        }
    
    @classmethod
    def get_storage_config(cls) -> Dict[str, Any]:
        return {
            "chroma_persist_directory": cls.VECTOR_STORE_PATH,
            "upload_directory": cls.UPLOAD_PATH,
            "faiss_cache_directory": cls.FAISS_CACHE_PATH,
            "max_file_size": cls.MAX_FILE_SIZE,
            "allowed_file_types": cls.ALLOWED_FILE_TYPES,
            "render_deployment": cls.RENDER_DEPLOYMENT
        }

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    ENABLE_RATE_LIMITING = False

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = "WARNING"
    ENABLE_RATE_LIMITING = True
    ALLOWED_ORIGINS = [
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ]

# Environment-based configuration
def get_config():
    env = os.getenv("ENVIRONMENT", "development").lower()
    if env == "production":
        return ProductionConfig()
    return DevelopmentConfig() 
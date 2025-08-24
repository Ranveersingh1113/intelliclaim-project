"""
Performance optimization settings for IntelliClaim system
"""

class PerformanceConfig:
    # Model Performance Settings
    USE_FAST_MODEL = False  # Use GPT-5 as required by hackathon
    GPT5_RETRY_ATTEMPTS = 2  # Number of retries for GPT-5
    GPT5_TIMEOUT = 60  # Timeout in seconds for GPT-5
    MAX_TOKENS = 1000      # Reduced from 2000 for faster responses
    REQUEST_TIMEOUT = 15   # Timeout in seconds
    
    # Context Optimization
    MAX_CONTEXT_CHARS = 1500  # Reduced from 2200
    PER_CLAUSE_WINDOW = 400   # Reduced from 600
    
    # Document Processing
    CHUNK_SIZE_SMALL = 400    # For documents < 100KB
    CHUNK_SIZE_MEDIUM = 800   # For documents < 500KB  
    CHUNK_SIZE_LARGE = 1500   # For documents >= 500KB
    
    # Retrieval Optimization
    TOP_K_DOCUMENTS = 3       # Reduced from 5
    CACHE_ENABLED = True
    CACHE_TTL = 3600          # Cache TTL in seconds
    
    # Processing Optimization
    ENABLE_PARALLEL_PROCESSING = True
    MAX_CONCURRENT_REQUESTS = 5
    
    @classmethod
    def get_optimization_settings(cls):
        return {
            "use_fast_model": cls.USE_FAST_MODEL,
            "max_tokens": cls.MAX_TOKENS,
            "timeout": cls.REQUEST_TIMEOUT,
            "max_context": cls.MAX_CONTEXT_CHARS,
            "top_k": cls.TOP_K_DOCUMENTS,
            "cache_enabled": cls.CACHE_ENABLED
        }

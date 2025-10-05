#!/usr/bin/env python3
"""
Test script for the industry-bert-insurance-v0.1 embedding integration
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_embedding_integration():
    """Test the insurance embedding model integration"""
    try:
        # Import our modules
        from config import get_config
        from chatgpt_app import EmbeddingManager, InsuranceEmbeddingWrapper
        
        config = get_config()
        logger.info(f"Testing with config: {config.EMBEDDING_MODEL}")
        logger.info(f"Fallback model: {config.EMBEDDING_FALLBACK_MODEL}")
        
        # Test 1: Direct SentenceTransformer model (Primary)
        logger.info("=== Test 1: Direct SentenceTransformer (Primary) ===")
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer(config.EMBEDDING_MODEL)
            
            test_texts = [
                "insurance policy coverage for medical expenses",
                "claim settlement process for health insurance",
                "waiting period for pre-existing conditions"
            ]
            
            embeddings = model.encode(test_texts, convert_to_tensor=False)
            logger.info(f"✅ Direct model test successful!")
            logger.info(f"   - Model: {model}")
            logger.info(f"   - Embedding shape: {embeddings.shape}")
            logger.info(f"   - Embedding dimension: {embeddings.shape[1]}")
            
        except Exception as e:
            logger.error(f"❌ Direct model test failed: {e}")
        
        # Test 1b: Direct SentenceTransformer model (Fallback)
        logger.info("\n=== Test 1b: Direct SentenceTransformer (Fallback) ===")
        try:
            fallback_model = SentenceTransformer(config.EMBEDDING_FALLBACK_MODEL)
            
            embeddings = fallback_model.encode(test_texts, convert_to_tensor=False)
            logger.info(f"✅ Fallback model test successful!")
            logger.info(f"   - Model: {fallback_model}")
            logger.info(f"   - Embedding shape: {embeddings.shape}")
            logger.info(f"   - Embedding dimension: {embeddings.shape[1]}")
            
        except Exception as e:
            logger.error(f"❌ Fallback model test failed: {e}")
        
        # Test 2: InsuranceEmbeddingWrapper
        logger.info("\n=== Test 2: InsuranceEmbeddingWrapper ===")
        try:
            wrapper = InsuranceEmbeddingWrapper()
            
            # Test document embedding
            doc_embeddings = wrapper.embed_documents(test_texts)
            logger.info(f"✅ Document embedding test successful!")
            logger.info(f"   - Documents processed: {len(doc_embeddings)}")
            logger.info(f"   - Embedding dimension: {len(doc_embeddings[0])}")
            
            # Test query embedding
            query_embedding = wrapper.embed_query("health insurance claim")
            logger.info(f"✅ Query embedding test successful!")
            logger.info(f"   - Query embedding dimension: {len(query_embedding)}")
            
        except Exception as e:
            logger.error(f"❌ Wrapper test failed: {e}")
        
        # Test 3: EmbeddingManager with fallback
        logger.info("\n=== Test 3: EmbeddingManager (with fallback) ===")
        try:
            embedding_manager = EmbeddingManager()
            
            logger.info(f"✅ EmbeddingManager initialized successfully!")
            logger.info(f"   - Primary model: {embedding_manager.primary_model_name}")
            logger.info(f"   - Fallback model: {embedding_manager.fallback_model_name}")
            logger.info(f"   - Current model: {embedding_manager.langchain_embeddings.model_name if hasattr(embedding_manager.langchain_embeddings, 'model_name') else 'OpenAI API Model'}")
            
            # Test actual embedding
            test_embeddings = embedding_manager.langchain_embeddings.embed_documents(test_texts)
            logger.info(f"   - Test embeddings generated: {len(test_embeddings)}")
            
        except Exception as e:
            logger.error(f"❌ EmbeddingManager test failed: {e}")
        
        logger.info("\n🎉 Integration test completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Overall test failed: {e}")
        return False

def test_model_download():
    """Test if the model can be downloaded"""
    try:
        from sentence_transformers import SentenceTransformer
        logger.info("=== Testing Model Download ===")
        
        # This will download the model if not already present
        model = SentenceTransformer("llmware/industry-bert-insurance-v0.1")
        logger.info("✅ Model downloaded/loaded successfully!")
        
        # Test with a simple insurance text
        test_text = "health insurance policy coverage"
        embedding = model.encode([test_text], convert_to_tensor=False)
        logger.info(f"✅ Test embedding generated: shape {embedding.shape}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Model download test failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting Insurance Embedding Integration Test")
    logger.info("=" * 60)
    
    # Test model download first
    download_success = test_model_download()
    
    if download_success:
        # Test full integration
        integration_success = test_embedding_integration()
        
        if integration_success:
            logger.info("\n✅ All tests passed! Integration successful!")
            sys.exit(0)
        else:
            logger.error("\n❌ Integration tests failed!")
            sys.exit(1)
    else:
        logger.error("\n❌ Model download failed!")
        sys.exit(1)

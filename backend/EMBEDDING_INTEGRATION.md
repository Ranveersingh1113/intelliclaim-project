# Insurance-Specific Embedding Integration

This document describes the integration of the `llmware/industry-bert-insurance-v0.1` embedding model into the IntelliClaim system.

## Overview

The system now uses an insurance-specific BERT model for document embeddings, which should provide significantly better semantic understanding for insurance-related documents compared to generic embedding models.

## Model Details

- **Primary Model**: `llmware/industry-bert-insurance-v0.1`
  - BERT-based Sentence Transformer
  - 768 parameters
  - Fine-tuned specifically for insurance documents
  - Runs locally (no API costs)

- **Fallback Model**: `sentence-transformers/all-MiniLM-L6-v2`
  - Local SentenceTransformer model
  - 384 dimensions
  - Runs locally, no API costs

## Implementation

### 1. New Classes

#### `InsuranceEmbeddingWrapper`
- Wraps SentenceTransformer to be compatible with LangChain's embedding interface
- Handles both document and query embeddings
- Provides error handling and logging

#### Updated `EmbeddingManager`
- Tries insurance-specific model first
- Falls back to all-MiniLM-L6-v2 if insurance model fails
- Final fallback to FakeEmbeddings for development

### 2. Configuration Changes

#### `config.py`
```python
EMBEDDING_MODEL = "llmware/industry-bert-insurance-v0.1"
EMBEDDING_FALLBACK_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

#### `env.example`
```bash
EMBEDDING_MODEL=llmware/industry-bert-insurance-v0.1
EMBEDDING_FALLBACK_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### 3. New API Endpoints

#### `/test-embedding-model`
Tests the current embedding model with insurance-specific text samples.

#### `/model-config` (Updated)
Now shows both LLM and embedding model configurations.

## Benefits

1. **Better Semantic Understanding**: Insurance-specific training means better understanding of:
   - Policy terminology
   - Claim-related concepts
   - Coverage details
   - Medical procedures and conditions

2. **Cost Reduction**: No API costs for embeddings (both models run locally)

3. **Improved Performance**: Better document retrieval for insurance queries

4. **Reliability**: Fallback mechanisms ensure system continues working

5. **Complete Local Processing**: Both primary and fallback models run locally

## Testing

### Run Integration Test
```bash
cd backend
python test_embedding_integration.py
```

### Test via API
```bash
# Test embedding model
curl http://localhost:8000/test-embedding-model

# Check model configuration
curl http://localhost:8000/model-config
```

## Dependencies

The following dependencies are required (already in requirements.txt):
- `sentence-transformers==2.2.2`

## Model Download

The model will be automatically downloaded on first use. It's approximately 400MB and will be cached locally.

## Fallback Behavior

1. **Primary**: `llmware/industry-bert-insurance-v0.1` (local, 768d)
2. **Fallback 1**: `sentence-transformers/all-MiniLM-L6-v2` (local, 384d)
3. **Fallback 2**: `FakeEmbeddings` (development only, 384d)

## Performance Expectations

- **Initial Load**: Slower first load due to model download
- **Subsequent Use**: Fast local inference
- **Memory Usage**: ~400MB for primary model, ~80MB for fallback
- **Quality**: Significantly better for insurance documents
- **Cost**: Zero API costs (both models run locally)

## Monitoring

Check logs for embedding model initialization:
```
INFO - Attempting to initialize insurance-specific embedding model: llmware/industry-bert-insurance-v0.1
INFO - Successfully initialized llmware/industry-bert-insurance-v0.1 - optimized for insurance documents
```

Or if fallback is used:
```
WARNING - Failed to initialize insurance model llmware/industry-bert-insurance-v0.1: ...
INFO - Falling back to all-MiniLM-L6-v2...
INFO - Successfully initialized fallback embeddings: sentence-transformers/all-MiniLM-L6-v2
```

## Troubleshooting

### Model Download Issues
- Ensure internet connectivity for initial download
- Check disk space (model is ~400MB)
- Verify sentence-transformers is installed

### Memory Issues
- Primary model requires ~400MB RAM
- Fallback model requires ~80MB RAM
- Both models run locally, no API dependencies

### Performance Issues
- First run will be slower due to model loading
- Subsequent runs should be fast
- Consider model caching for production

## Production Deployment

For production deployment:
1. Ensure model is downloaded during build
2. Consider pre-warming the model
3. Monitor memory usage
4. Set up proper fallback monitoring

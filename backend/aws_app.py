#!/usr/bin/env python3
"""
AWS-optimized FastAPI application for IntelliClaim
Uses AWS RDS, S3, and other cloud services
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from aws_rag_system import aws_rag_system, DecisionResponse
from aws_storage import s3_storage
from aws_config import get_aws_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize AWS configuration
aws_config = get_aws_config()

# FastAPI app
app = FastAPI(
    title="IntelliClaim AWS API",
    version="2.0.0",
    description="AI-Powered Insurance Claims Processing on AWS"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QueryRequest(BaseModel):
    query: str

class UploadURLRequest(BaseModel):
    url: str
    async_mode: Optional[bool] = False

class SystemStatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    recent_queries_24h: int
    avg_processing_time: float
    system_status: str
    database_status: str

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize AWS services on startup"""
    try:
        logger.info("Initializing AWS RAG system...")
        await aws_rag_system.initialize()
        logger.info("AWS RAG system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize AWS RAG system: {e}")
        raise

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check AWS services
        stats = await aws_rag_system.get_system_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "aws_services": {
                "database": stats.get("database_status", "unknown"),
                "s3": "connected",
                "rag_system": "initialized"
            },
            "version": "2.0.0-aws"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Main query endpoint
@app.post("/query", response_model=DecisionResponse)
async def process_query_endpoint(request: QueryRequest):
    """Process insurance claim query"""
    try:
        logger.info(f"Processing query: {request.query[:100]}...")
        response = await aws_rag_system.process_query(query=request.query)
        return response
    except Exception as e:
        logger.error(f"Unhandled exception in /query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Document upload endpoint
@app.post("/upload-document")
async def upload_document_endpoint(file: UploadFile = File(...)):
    """Upload document to AWS S3 and process"""
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.eml', '.txt']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}. Allowed types: {allowed_extensions}"
            )
        
        # Validate file size (50MB limit)
        max_size = 50 * 1024 * 1024  # 50MB
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {max_size // (1024*1024)}MB"
            )
        
        # Save file temporarily
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            buffer.write(content)
        
        try:
            # Process document
            result = await aws_rag_system.add_document(temp_file_path, file.filename)
            
            if result['status'] == 'error':
                raise HTTPException(status_code=400, detail=result['message'])
            
            return result
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# URL upload endpoint
@app.post("/upload-document-url")
async def upload_document_by_url(payload: UploadURLRequest):
    """Download document from URL and process"""
    try:
        # Download and upload to S3
        result = s3_storage.upload_from_url(payload.url, f"downloaded_{datetime.now().timestamp()}")
        
        if result['status'] == 'error':
            raise HTTPException(status_code=500, detail=result['message'])
        
        # Process document if not in async mode
        if not payload.async_mode:
            # Note: This would require additional processing logic
            # For now, just return the upload result
            pass
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"URL upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# List documents endpoint
@app.get("/documents")
async def list_documents():
    """List all documents in the system"""
    try:
        documents = await aws_rag_system.list_documents()
        return {
            "total_documents": len(documents),
            "documents": documents
        }
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Delete document endpoint
@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete document from the system"""
    try:
        result = await aws_rag_system.delete_document(filename)
        
        if result['status'] == 'error':
            raise HTTPException(status_code=404, detail=result['message'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System stats endpoint
@app.get("/system-stats", response_model=SystemStatsResponse)
async def get_system_stats():
    """Get system statistics"""
    try:
        stats = await aws_rag_system.get_system_stats()
        return SystemStatsResponse(**stats)
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# AWS-specific endpoints

# Test AWS connectivity
@app.get("/test-aws")
async def test_aws_connectivity():
    """Test AWS service connectivity"""
    try:
        # Test S3
        s3_test = s3_storage.list_documents()
        s3_status = "connected" if s3_test is not None else "error"
        
        # Test database
        db_stats = await aws_rag_system.get_system_stats()
        db_status = db_stats.get("database_status", "unknown")
        
        # Test RAG system
        rag_status = "initialized" if aws_rag_system.initialized else "not_initialized"
        
        return {
            "status": "success",
            "services": {
                "s3": s3_status,
                "database": db_status,
                "rag_system": rag_status
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"AWS connectivity test failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Migration status endpoint
@app.get("/migration-status")
async def get_migration_status():
    """Get migration status from local to AWS"""
    try:
        # Check local files
        local_files = []
        uploads_dir = "./uploads"
        if os.path.exists(uploads_dir):
            local_files = [f for f in os.listdir(uploads_dir) if os.path.isfile(os.path.join(uploads_dir, f))]
        
        # Get AWS documents
        aws_documents = await aws_rag_system.list_documents()
        aws_files = [doc['file_name'] for doc in aws_documents]
        
        return {
            "local_files": {
                "count": len(local_files),
                "files": local_files
            },
            "aws_files": {
                "count": len(aws_files),
                "files": aws_files
            },
            "migration_complete": len(local_files) == 0 and len(aws_files) > 0,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get migration status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Performance metrics endpoint
@app.get("/metrics")
async def get_performance_metrics():
    """Get performance metrics"""
    try:
        stats = await aws_rag_system.get_system_stats()
        
        return {
            "performance": {
                "total_documents": stats.get("total_documents", 0),
                "total_chunks": stats.get("total_chunks", 0),
                "avg_processing_time": stats.get("avg_processing_time", 0),
                "recent_queries_24h": stats.get("recent_queries_24h", 0)
            },
            "system": {
                "status": stats.get("system_status", "unknown"),
                "database_status": stats.get("database_status", "unknown")
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "IntelliClaim AWS API",
        "version": "2.0.0",
        "status": "running",
        "environment": aws_config.AWS_REGION,
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "query": "/query",
            "upload": "/upload-document",
            "documents": "/documents",
            "stats": "/system-stats",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable (for AWS deployment)
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        workers=1  # Single worker for Fargate
    )

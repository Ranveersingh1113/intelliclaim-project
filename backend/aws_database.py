"""
AWS RDS PostgreSQL with pgvector integration for IntelliClaim
Replaces local ChromaDB with scalable cloud database
"""

import os
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import asyncpg
import numpy as np
from dataclasses import dataclass
from aws_config import AWSConfig
from aws_storage import s3_storage
import json

logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    """Document chunk representation"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    source: str = ""
    chunk_id: str = ""

class VectorDatabase:
    """AWS RDS PostgreSQL with pgvector for vector operations"""
    
    def __init__(self):
        self.config = AWSConfig()
        self.connection_pool = None
        self.embedding_dimension = 1536  # OpenAI embedding dimension
        
    async def initialize(self):
        """Initialize database connection pool and setup tables"""
        try:
            # Create connection pool
            self.connection_pool = await asyncpg.create_pool(
                host=self.config.RDS_HOST,
                port=self.config.RDS_PORT,
                database=self.config.RDS_DATABASE,
                user=self.config.RDS_USERNAME,
                password=self.config.RDS_PASSWORD,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            
            # Setup database schema
            await self._setup_database_schema()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def _setup_database_schema(self):
        """Setup database tables and extensions"""
        async with self.connection_pool.acquire() as conn:
            # Enable pgvector extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            # Create documents table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    file_name VARCHAR(255) NOT NULL,
                    s3_key VARCHAR(500) NOT NULL,
                    file_hash VARCHAR(64) UNIQUE,
                    content_type VARCHAR(100),
                    file_size BIGINT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'uploaded'
                )
            """)
            
            # Create document_chunks table with vector column
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    metadata JSONB,
                    embedding vector(1536),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding 
                ON document_chunks USING ivfflat (embedding vector_cosine_ops) 
                WITH (lists = 100)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id 
                ON document_chunks(document_id)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_file_hash 
                ON documents(file_hash)
            """)
            
            # Create query_logs table for analytics
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS query_logs (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    query TEXT NOT NULL,
                    structured_query JSONB,
                    retrieved_chunks INTEGER,
                    decision VARCHAR(50),
                    confidence_score FLOAT,
                    processing_time FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            logger.info("Database schema setup completed")
    
    async def add_document(self, file_path: str, file_name: str, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """Add document and its chunks to database"""
        try:
            # Upload file to S3 first
            s3_result = s3_storage.upload_document(file_path, file_name)
            if s3_result["status"] != "success":
                return s3_result
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(file_path)
            
            async with self.connection_pool.acquire() as conn:
                async with conn.transaction():
                    # Check if document already exists
                    existing_doc = await conn.fetchrow(
                        "SELECT id FROM documents WHERE file_hash = $1",
                        file_hash
                    )
                    
                    if existing_doc:
                        return {
                            "status": "skipped",
                            "reason": "already_exists",
                            "document_id": str(existing_doc['id']),
                            "file_name": file_name
                        }
                    
                    # Insert document record
                    document_id = await conn.fetchval("""
                        INSERT INTO documents (file_name, s3_key, file_hash, content_type, file_size, processed_at, status)
                        VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP, 'processed')
                        RETURNING id
                    """, file_name, s3_result["s3_key"], file_hash, 
                        s3_result.get("content_type", "application/octet-stream"),
                        s3_result["size"])
                    
                    # Insert document chunks
                    chunk_count = 0
                    for i, chunk in enumerate(chunks):
                        await conn.execute("""
                            INSERT INTO document_chunks (document_id, chunk_index, content, metadata, embedding)
                            VALUES ($1, $2, $3, $4, $5)
                        """, document_id, i, chunk.content, json.dumps(chunk.metadata), chunk.embedding)
                        chunk_count += 1
                    
                    logger.info(f"Added document {file_name} with {chunk_count} chunks")
                    
                    return {
                        "status": "success",
                        "document_id": str(document_id),
                        "chunks_added": chunk_count,
                        "s3_key": s3_result["s3_key"],
                        "file_name": file_name
                    }
                    
        except Exception as e:
            logger.error(f"Failed to add document {file_name}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def similarity_search(self, query_embedding: List[float], k: int = 5) -> List[DocumentChunk]:
        """Perform similarity search using pgvector"""
        try:
            async with self.connection_pool.acquire() as conn:
                # Use cosine similarity for search
                results = await conn.fetch("""
                    SELECT 
                        dc.id,
                        dc.content,
                        dc.metadata,
                        dc.document_id,
                        dc.chunk_index,
                        d.file_name as source,
                        1 - (dc.embedding <=> $1) as similarity_score
                    FROM document_chunks dc
                    JOIN documents d ON dc.document_id = d.id
                    ORDER BY dc.embedding <=> $1
                    LIMIT $2
                """, query_embedding, k)
                
                chunks = []
                for row in results:
                    chunk = DocumentChunk(
                        id=str(row['id']),
                        content=row['content'],
                        metadata=row['metadata'] or {},
                        embedding=None,  # Don't return embeddings to save bandwidth
                        source=row['source'],
                        chunk_id=str(row['chunk_index'])
                    )
                    chunks.append(chunk)
                
                logger.info(f"Retrieved {len(chunks)} similar chunks")
                return chunks
                
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {e}")
            return []
    
    async def delete_document(self, file_name: str) -> Dict[str, Any]:
        """Delete document and its chunks"""
        try:
            async with self.connection_pool.acquire() as conn:
                async with conn.transaction():
                    # Get document info
                    doc_info = await conn.fetchrow(
                        "SELECT id, s3_key FROM documents WHERE file_name = $1",
                        file_name
                    )
                    
                    if not doc_info:
                        return {
                            "status": "error",
                            "message": "Document not found"
                        }
                    
                    # Delete from S3
                    s3_result = s3_storage.delete_document(doc_info['s3_key'])
                    
                    # Delete chunks and document from database
                    await conn.execute(
                        "DELETE FROM document_chunks WHERE document_id = $1",
                        doc_info['id']
                    )
                    await conn.execute(
                        "DELETE FROM documents WHERE id = $1",
                        doc_info['id']
                    )
                    
                    logger.info(f"Deleted document {file_name}")
                    
                    return {
                        "status": "success",
                        "message": f"Document {file_name} deleted successfully"
                    }
                    
        except Exception as e:
            logger.error(f"Failed to delete document {file_name}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents in the database"""
        try:
            async with self.connection_pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT 
                        file_name,
                        file_size,
                        uploaded_at,
                        processed_at,
                        status,
                        (SELECT COUNT(*) FROM document_chunks WHERE document_id = documents.id) as chunk_count
                    FROM documents
                    ORDER BY uploaded_at DESC
                """)
                
                documents = []
                for row in results:
                    documents.append({
                        "file_name": row['file_name'],
                        "file_size": row['file_size'],
                        "uploaded_at": row['uploaded_at'].isoformat(),
                        "processed_at": row['processed_at'].isoformat() if row['processed_at'] else None,
                        "status": row['status'],
                        "chunk_count": row['chunk_count']
                    })
                
                return documents
                
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return []
    
    async def log_query(self, query: str, structured_query: Dict, 
                       retrieved_chunks: int, decision: str, 
                       confidence_score: float, processing_time: float):
        """Log query for analytics"""
        try:
            async with self.connection_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO query_logs (query, structured_query, retrieved_chunks, decision, confidence_score, processing_time)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, query, json.dumps(structured_query), retrieved_chunks, 
                    decision, confidence_score, processing_time)
                    
        except Exception as e:
            logger.error(f"Failed to log query: {e}")
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            async with self.connection_pool.acquire() as conn:
                # Get document count
                doc_count = await conn.fetchval("SELECT COUNT(*) FROM documents")
                
                # Get chunk count
                chunk_count = await conn.fetchval("SELECT COUNT(*) FROM document_chunks")
                
                # Get recent query count
                recent_queries = await conn.fetchval("""
                    SELECT COUNT(*) FROM query_logs 
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                """)
                
                # Get average processing time
                avg_processing_time = await conn.fetchval("""
                    SELECT AVG(processing_time) FROM query_logs 
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                """)
                
                return {
                    "total_documents": doc_count,
                    "total_chunks": chunk_count,
                    "recent_queries_24h": recent_queries,
                    "avg_processing_time": round(avg_processing_time or 0, 2),
                    "system_status": "healthy",
                    "database_status": "connected"
                }
                
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            return {
                "total_documents": 0,
                "total_chunks": 0,
                "system_status": "degraded",
                "database_status": "error",
                "error": str(e)
            }
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file"""
        import hashlib
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    async def close(self):
        """Close database connection pool"""
        if self.connection_pool:
            await self.connection_pool.close()
            logger.info("Database connection pool closed")

# Global database instance
vector_db = VectorDatabase()

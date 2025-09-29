#!/usr/bin/env python3
"""
Database Migration Script for IntelliClaim
Migrates from local ChromaDB to AWS RDS PostgreSQL with pgvector
"""

import asyncio
import os
import sys
import json
import logging
from typing import List, Dict, Any
from datetime import datetime

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aws_database import vector_db, DocumentChunk
from aws_config import get_aws_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Handles migration from ChromaDB to AWS RDS"""
    
    def __init__(self):
        self.aws_config = get_aws_config()
        self.migration_stats = {
            'documents_processed': 0,
            'chunks_migrated': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
    
    async def initialize_aws_database(self):
        """Initialize AWS database connection"""
        try:
            await vector_db.initialize()
            logger.info("AWS database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AWS database: {e}")
            raise
    
    def get_chromadb_documents(self) -> List[Dict[str, Any]]:
        """Retrieve documents from local ChromaDB"""
        try:
            # Import ChromaDB components
            import chromadb
            from chromadb.config import Settings
            
            # Initialize ChromaDB client
            client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get collection
            collection = client.get_collection("langchain")
            
            # Retrieve all documents
            results = collection.get()
            
            documents = []
            if results and results.get('documents'):
                for i, doc_content in enumerate(results['documents']):
                    metadata = results['metadatas'][i] if results.get('metadatas') else {}
                    doc_id = results['ids'][i] if results.get('ids') else f"doc_{i}"
                    
                    documents.append({
                        'id': doc_id,
                        'content': doc_content,
                        'metadata': metadata
                    })
            
            logger.info(f"Retrieved {len(documents)} documents from ChromaDB")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents from ChromaDB: {e}")
            return []
    
    async def migrate_document(self, doc_data: Dict[str, Any]) -> bool:
        """Migrate a single document to AWS database"""
        try:
            doc_id = doc_data['id']
            content = doc_data['content']
            metadata = doc_data['metadata']
            
            # Create DocumentChunk object
            chunk = DocumentChunk(
                id=doc_id,
                content=content,
                metadata=metadata,
                source=metadata.get('source', 'migrated'),
                chunk_id=metadata.get('chunk_id', '0')
            )
            
            # Add to AWS database
            await vector_db.add_document_chunk(chunk)
            
            self.migration_stats['chunks_migrated'] += 1
            logger.info(f"Migrated document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate document {doc_data.get('id', 'unknown')}: {e}")
            self.migration_stats['errors'] += 1
            return False
    
    async def migrate_all_documents(self):
        """Migrate all documents from ChromaDB to AWS"""
        logger.info("Starting database migration...")
        
        # Get documents from ChromaDB
        documents = self.get_chromadb_documents()
        
        if not documents:
            logger.warning("No documents found in ChromaDB")
            return
        
        # Migrate each document
        for doc_data in documents:
            success = await self.migrate_document(doc_data)
            if success:
                self.migration_stats['documents_processed'] += 1
            
            # Log progress every 10 documents
            if self.migration_stats['documents_processed'] % 10 == 0:
                logger.info(f"Progress: {self.migration_stats['documents_processed']}/{len(documents)} documents migrated")
        
        # Calculate migration time
        migration_time = datetime.now() - self.migration_stats['start_time']
        
        # Log final statistics
        logger.info("=== Migration Complete ===")
        logger.info(f"Total documents processed: {self.migration_stats['documents_processed']}")
        logger.info(f"Total chunks migrated: {self.migration_stats['chunks_migrated']}")
        logger.info(f"Errors encountered: {self.migration_stats['errors']}")
        logger.info(f"Migration time: {migration_time}")
        
        if self.migration_stats['errors'] > 0:
            logger.warning(f"Migration completed with {self.migration_stats['errors']} errors")
        else:
            logger.info("Migration completed successfully!")
    
    async def verify_migration(self):
        """Verify that migration was successful"""
        try:
            # Get system stats from AWS database
            stats = await vector_db.get_system_stats()
            
            logger.info("=== Migration Verification ===")
            logger.info(f"Total documents in AWS database: {stats.get('total_documents', 0)}")
            logger.info(f"Total chunks in AWS database: {stats.get('total_chunks', 0)}")
            logger.info(f"Database status: {stats.get('database_status', 'unknown')}")
            
            # Test similarity search
            test_embedding = [0.1] * 1536  # Dummy embedding for testing
            results = await vector_db.similarity_search(test_embedding, k=1)
            
            if results:
                logger.info(f"Similarity search test successful: found {len(results)} results")
            else:
                logger.warning("Similarity search test returned no results")
            
        except Exception as e:
            logger.error(f"Migration verification failed: {e}")
    
    async def create_backup(self):
        """Create backup of ChromaDB before migration"""
        try:
            import shutil
            import datetime
            
            backup_dir = f"./chroma_db_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copytree("./chroma_db", backup_dir)
            
            logger.info(f"ChromaDB backup created at: {backup_dir}")
            return backup_dir
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None

async def main():
    """Main migration function"""
    migrator = DatabaseMigrator()
    
    try:
        # Create backup first
        logger.info("Creating backup of ChromaDB...")
        backup_dir = await migrator.create_backup()
        if backup_dir:
            logger.info(f"Backup created at: {backup_dir}")
        
        # Initialize AWS database
        await migrator.initialize_aws_database()
        
        # Perform migration
        await migrator.migrate_all_documents()
        
        # Verify migration
        await migrator.verify_migration()
        
        logger.info("Migration process completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)
    
    finally:
        # Close database connections
        await vector_db.close()

if __name__ == "__main__":
    # Check if running in AWS environment
    if not os.getenv("AWS_REGION"):
        logger.warning("AWS_REGION environment variable not set. Make sure you're running in AWS environment.")
    
    # Run migration
    asyncio.run(main())

#!/usr/bin/env python3
"""
Storage Migration Script for IntelliClaim
Migrates local files to AWS S3 with CloudFront CDN
"""

import os
import sys
import logging
from typing import List, Dict, Any
from datetime import datetime

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aws_storage import s3_storage
from aws_config import get_aws_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StorageMigrator:
    """Handles migration from local storage to AWS S3"""
    
    def __init__(self):
        self.aws_config = get_aws_config()
        self.uploads_dir = "./uploads"
        self.migration_stats = {
            'files_processed': 0,
            'files_uploaded': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
    
    def get_local_files(self) -> List[Dict[str, Any]]:
        """Get list of files in local uploads directory"""
        files = []
        
        if not os.path.exists(self.uploads_dir):
            logger.warning(f"Uploads directory {self.uploads_dir} does not exist")
            return files
        
        try:
            for filename in os.listdir(self.uploads_dir):
                file_path = os.path.join(self.uploads_dir, filename)
                
                if os.path.isfile(file_path):
                    file_stat = os.stat(file_path)
                    files.append({
                        'filename': filename,
                        'file_path': file_path,
                        'size': file_stat.st_size,
                        'modified_time': datetime.fromtimestamp(file_stat.st_mtime)
                    })
            
            logger.info(f"Found {len(files)} files in {self.uploads_dir}")
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files in {self.uploads_dir}: {e}")
            return []
    
    def migrate_file(self, file_info: Dict[str, Any]) -> bool:
        """Migrate a single file to S3"""
        try:
            filename = file_info['filename']
            file_path = file_info['file_path']
            
            logger.info(f"Migrating file: {filename} ({file_info['size']} bytes)")
            
            # Upload to S3
            result = s3_storage.upload_document(file_path, filename)
            
            if result["status"] == "success":
                self.migration_stats['files_uploaded'] += 1
                logger.info(f"Successfully uploaded {filename} to S3")
                return True
            else:
                logger.error(f"Failed to upload {filename}: {result.get('message', 'Unknown error')}")
                self.migration_stats['errors'] += 1
                return False
                
        except Exception as e:
            logger.error(f"Failed to migrate file {file_info.get('filename', 'unknown')}: {e}")
            self.migration_stats['errors'] += 1
            return False
    
    def migrate_all_files(self):
        """Migrate all files from local storage to S3"""
        logger.info("Starting storage migration...")
        
        # Get local files
        files = self.get_local_files()
        
        if not files:
            logger.warning("No files found to migrate")
            return
        
        # Migrate each file
        for file_info in files:
            success = self.migrate_file(file_info)
            if success:
                self.migration_stats['files_processed'] += 1
            
            # Log progress every 5 files
            if self.migration_stats['files_processed'] % 5 == 0:
                logger.info(f"Progress: {self.migration_stats['files_processed']}/{len(files)} files processed")
        
        # Calculate migration time
        migration_time = datetime.now() - self.migration_stats['start_time']
        
        # Log final statistics
        logger.info("=== Storage Migration Complete ===")
        logger.info(f"Total files processed: {self.migration_stats['files_processed']}")
        logger.info(f"Total files uploaded: {self.migration_stats['files_uploaded']}")
        logger.info(f"Errors encountered: {self.migration_stats['errors']}")
        logger.info(f"Migration time: {migration_time}")
        
        if self.migration_stats['errors'] > 0:
            logger.warning(f"Migration completed with {self.migration_stats['errors']} errors")
        else:
            logger.info("Storage migration completed successfully!")
    
    def verify_migration(self):
        """Verify that migration was successful"""
        try:
            # List documents in S3
            documents = s3_storage.list_documents()
            
            logger.info("=== Migration Verification ===")
            logger.info(f"Total documents in S3: {len(documents)}")
            
            for doc in documents[:5]:  # Show first 5 documents
                logger.info(f"Document: {doc['file_name']} ({doc['size']} bytes)")
            
            if len(documents) > 5:
                logger.info(f"... and {len(documents) - 5} more documents")
            
        except Exception as e:
            logger.error(f"Storage migration verification failed: {e}")
    
    def create_backup(self):
        """Create backup of local files before migration"""
        try:
            import shutil
            import datetime
            
            backup_dir = f"./uploads_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copytree(self.uploads_dir, backup_dir)
            
            logger.info(f"Local files backup created at: {backup_dir}")
            return backup_dir
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def cleanup_local_files(self, confirm: bool = False):
        """Clean up local files after successful migration"""
        if not confirm:
            logger.info("Skipping local file cleanup (use --cleanup flag to confirm)")
            return
        
        try:
            files = self.get_local_files()
            
            for file_info in files:
                try:
                    os.remove(file_info['file_path'])
                    logger.info(f"Removed local file: {file_info['filename']}")
                except Exception as e:
                    logger.error(f"Failed to remove {file_info['filename']}: {e}")
            
            logger.info("Local files cleanup completed")
            
        except Exception as e:
            logger.error(f"Failed to cleanup local files: {e}")

def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate local storage to AWS S3')
    parser.add_argument('--cleanup', action='store_true', help='Clean up local files after migration')
    parser.add_argument('--verify-only', action='store_true', help='Only verify existing migration')
    
    args = parser.parse_args()
    
    migrator = StorageMigrator()
    
    try:
        if args.verify_only:
            migrator.verify_migration()
            return
        
        # Create backup first
        logger.info("Creating backup of local files...")
        backup_dir = migrator.create_backup()
        if backup_dir:
            logger.info(f"Backup created at: {backup_dir}")
        
        # Perform migration
        migrator.migrate_all_files()
        
        # Verify migration
        migrator.verify_migration()
        
        # Clean up local files if requested
        if args.cleanup:
            migrator.cleanup_local_files(confirm=True)
        
        logger.info("Storage migration process completed successfully!")
        
    except Exception as e:
        logger.error(f"Storage migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check if running in AWS environment
    if not os.getenv("AWS_REGION"):
        logger.warning("AWS_REGION environment variable not set. Make sure you're running in AWS environment.")
    
    main()

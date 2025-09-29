"""
AWS S3 storage implementation for IntelliClaim
Replaces local file storage with S3 for scalability and reliability
"""

import boto3
import os
import hashlib
import tempfile
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError, NoCredentialsError
from aws_config import AWSConfig
import logging

logger = logging.getLogger(__name__)

class S3StorageManager:
    """S3-based storage manager for documents and uploads"""
    
    def __init__(self):
        self.config = AWSConfig()
        self.s3_client = self.config.get_s3_client()
        self.bucket_name = self.config.S3_BUCKET_NAME
        
        # Ensure bucket exists
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure S3 bucket exists, create if it doesn't"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"S3 bucket {self.bucket_name} exists")
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                # Bucket doesn't exist, create it
                try:
                    if self.config.AWS_REGION == 'us-east-1':
                        # us-east-1 doesn't need LocationConstraint
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.config.AWS_REGION}
                        )
                    logger.info(f"Created S3 bucket {self.bucket_name}")
                except ClientError as create_error:
                    logger.error(f"Failed to create S3 bucket: {create_error}")
                    raise
            else:
                logger.error(f"Error checking S3 bucket: {e}")
                raise
    
    def upload_document(self, file_path: str, file_name: Optional[str] = None) -> Dict[str, Any]:
        """Upload document to S3"""
        try:
            if not file_name:
                file_name = os.path.basename(file_path)
            
            # Generate S3 key
            s3_key = f"{self.config.S3_DOCUMENTS_PREFIX}{file_name}"
            
            # Upload file
            with open(file_path, 'rb') as file:
                self.s3_client.upload_fileobj(
                    file,
                    self.bucket_name,
                    s3_key,
                    ExtraArgs={
                        'ContentType': self._get_content_type(file_name),
                        'ServerSideEncryption': 'AES256'
                    }
                )
            
            # Generate presigned URL for access (valid for 1 hour)
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=3600
            )
            
            logger.info(f"Uploaded document {file_name} to S3: {s3_key}")
            
            return {
                "status": "success",
                "s3_key": s3_key,
                "bucket": self.bucket_name,
                "file_name": file_name,
                "presigned_url": presigned_url,
                "size": os.path.getsize(file_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to upload document {file_path}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def download_document(self, s3_key: str, local_path: Optional[str] = None) -> Dict[str, Any]:
        """Download document from S3"""
        try:
            if not local_path:
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                local_path = temp_file.name
                temp_file.close()
            
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            
            logger.info(f"Downloaded document from S3: {s3_key}")
            
            return {
                "status": "success",
                "local_path": local_path,
                "s3_key": s3_key
            }
            
        except ClientError as e:
            logger.error(f"Failed to download document {s3_key}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def delete_document(self, s3_key: str) -> Dict[str, Any]:
        """Delete document from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"Deleted document from S3: {s3_key}")
            
            return {
                "status": "success",
                "s3_key": s3_key
            }
            
        except ClientError as e:
            logger.error(f"Failed to delete document {s3_key}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def list_documents(self, prefix: str = None) -> List[Dict[str, Any]]:
        """List documents in S3 bucket"""
        try:
            if not prefix:
                prefix = self.config.S3_DOCUMENTS_PREFIX
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            documents = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    documents.append({
                        "key": obj['Key'],
                        "size": obj['Size'],
                        "last_modified": obj['LastModified'],
                        "file_name": os.path.basename(obj['Key'])
                    })
            
            return documents
            
        except ClientError as e:
            logger.error(f"Failed to list documents: {e}")
            return []
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for document access"""
        try:
            return self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {s3_key}: {e}")
            return ""
    
    def upload_from_url(self, url: str, file_name: str) -> Dict[str, Any]:
        """Download from URL and upload to S3"""
        try:
            import requests
            
            # Download file from URL
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            # Upload to S3
            result = self.upload_document(temp_path, file_name)
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to upload from URL {url}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _get_content_type(self, file_name: str) -> str:
        """Get content type based on file extension"""
        ext = os.path.splitext(file_name)[1].lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain',
            '.eml': 'message/rfc822'
        }
        return content_types.get(ext, 'application/octet-stream')
    
    def get_document_hash(self, s3_key: str) -> Optional[str]:
        """Get document hash for caching purposes"""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return response.get('ETag', '').strip('"')
        except ClientError as e:
            logger.error(f"Failed to get document hash for {s3_key}: {e}")
            return None

# Global S3 storage instance
s3_storage = S3StorageManager()

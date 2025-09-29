"""
AWS-specific configuration for IntelliClaim system
"""

import os
import boto3
from typing import Dict, Any, Optional
from config import Config

class AWSConfig(Config):
    """AWS-specific configuration extending base Config"""
    
    # AWS Services Configuration
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID")
    
    # S3 Configuration
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "intelliclaim-documents")
    S3_DOCUMENTS_PREFIX = "documents/"
    S3_UPLOADS_PREFIX = "uploads/"
    S3_CACHE_PREFIX = "cache/"
    
    # RDS Configuration
    RDS_HOST = os.getenv("RDS_HOST")
    RDS_PORT = int(os.getenv("RDS_PORT", "5432"))
    RDS_DATABASE = os.getenv("RDS_DATABASE", "intelliclaim")
    RDS_USERNAME = os.getenv("RDS_USERNAME", "postgres")
    RDS_PASSWORD = os.getenv("RDS_PASSWORD")
    
    # ECS Configuration
    ECS_CLUSTER_NAME = os.getenv("ECS_CLUSTER_NAME", "intelliclaim-cluster")
    ECS_SERVICE_NAME = os.getenv("ECS_SERVICE_NAME", "intelliclaim-backend")
    ECS_TASK_DEFINITION = os.getenv("ECS_TASK_DEFINITION", "intelliclaim-backend")
    
    # CloudFront Configuration
    CLOUDFRONT_DOMAIN = os.getenv("CLOUDFRONT_DOMAIN")
    CLOUDFRONT_DISTRIBUTION_ID = os.getenv("CLOUDFRONT_DISTRIBUTION_ID")
    
    # Secrets Manager
    SECRETS_MANAGER_SECRET_NAME = os.getenv("SECRETS_MANAGER_SECRET_NAME", "intelliclaim/secrets")
    
    # Lambda Configuration
    LAMBDA_FUNCTION_NAME = os.getenv("LAMBDA_FUNCTION_NAME", "intelliclaim-processor")
    
    # CloudWatch Configuration
    CLOUDWATCH_LOG_GROUP = os.getenv("CLOUDWATCH_LOG_GROUP", "/aws/ecs/intelliclaim")
    
    # Application Load Balancer
    ALB_DNS_NAME = os.getenv("ALB_DNS_NAME")
    ALB_LISTENER_ARN = os.getenv("ALB_LISTENER_ARN")
    
    @classmethod
    def get_aws_config(cls) -> Dict[str, Any]:
        """Get AWS-specific configuration"""
        return {
            "region": cls.AWS_REGION,
            "s3_bucket": cls.S3_BUCKET_NAME,
            "rds_config": {
                "host": cls.RDS_HOST,
                "port": cls.RDS_PORT,
                "database": cls.RDS_DATABASE,
                "username": cls.RDS_USERNAME
            },
            "ecs_config": {
                "cluster": cls.ECS_CLUSTER_NAME,
                "service": cls.ECS_SERVICE_NAME,
                "task_definition": cls.ECS_TASK_DEFINITION
            },
            "cloudfront": {
                "domain": cls.CLOUDFRONT_DOMAIN,
                "distribution_id": cls.CLOUDFRONT_DISTRIBUTION_ID
            }
        }
    
    @classmethod
    def get_boto3_session(cls) -> boto3.Session:
        """Get configured boto3 session"""
        return boto3.Session(region_name=cls.AWS_REGION)
    
    @classmethod
    def get_s3_client(cls):
        """Get S3 client"""
        return cls.get_boto3_session().client('s3')
    
    @classmethod
    def get_rds_client(cls):
        """Get RDS client"""
        return cls.get_boto3_session().client('rds')
    
    @classmethod
    def get_secrets_client(cls):
        """Get Secrets Manager client"""
        return cls.get_boto3_session().client('secretsmanager')
    
    @classmethod
    def get_cloudwatch_client(cls):
        """Get CloudWatch client"""
        return cls.get_boto3_session().client('cloudwatch')
    
    @classmethod
    def get_secrets(cls) -> Dict[str, str]:
        """Retrieve secrets from AWS Secrets Manager"""
        try:
            client = cls.get_secrets_client()
            response = client.get_secret_value(SecretId=cls.SECRETS_MANAGER_SECRET_NAME)
            import json
            return json.loads(response['SecretString'])
        except Exception as e:
            print(f"Warning: Could not retrieve secrets from AWS Secrets Manager: {e}")
            return {
                "AIMLAPI_KEY": os.getenv("AIMLAPI_KEY"),
                "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
                "RDS_PASSWORD": os.getenv("RDS_PASSWORD")
            }

# Environment-based configuration
def get_aws_config():
    """Get AWS configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    if env == "production":
        return AWSConfig()
    return AWSConfig()

# 🚀 IntelliClaim AWS Cloud-Centric Deployment Guide

This comprehensive guide will help you migrate your IntelliClaim project from Render to AWS with a fully cloud-centric architecture.

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Infrastructure Setup](#infrastructure-setup)
4. [Application Deployment](#application-deployment)
5. [Database Migration](#database-migration)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Security Configuration](#security-configuration)
8. [Monitoring & Alerting](#monitoring--alerting)
9. [Cost Optimization](#cost-optimization)
10. [Troubleshooting](#troubleshooting)

## 🏗️ Architecture Overview

### Current vs. AWS Architecture

**Current (Render):**
- Monolithic deployment on Render
- Local ChromaDB storage
- Local file system for documents
- Manual scaling

**AWS Cloud-Centric:**
- **Frontend**: S3 + CloudFront CDN
- **Backend**: ECS Fargate (serverless containers)
- **Database**: RDS Aurora PostgreSQL with pgvector
- **Storage**: S3 with lifecycle policies
- **CI/CD**: CodePipeline + CodeBuild
- **Security**: WAF, VPC, IAM, Secrets Manager
- **Monitoring**: CloudWatch + X-Ray

### Key Benefits

✅ **Scalability**: Auto-scaling based on demand  
✅ **Cost Optimization**: Pay-per-use with reserved instances  
✅ **Security**: Enterprise-grade security with WAF and VPC  
✅ **Reliability**: Multi-AZ deployment with 99.9% SLA  
✅ **Performance**: Global CDN with edge caching  
✅ **Compliance**: SOC 2, PCI DSS, HIPAA ready  

## 🔧 Prerequisites

### 1. AWS Account Setup
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS CLI
aws configure
```

### 2. Required Tools
```bash
# Install Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Node.js (for frontend builds)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 3. Environment Variables
```bash
# Set required environment variables
export AWS_REGION="us-east-1"
export ENVIRONMENT="dev"  # or "staging", "prod"
export DOMAIN_NAME="your-domain.com"  # optional
export GITHUB_REPOSITORY="your-username/intelliclaim-project"
export GITHUB_BRANCH="main"
```

## 🏗️ Infrastructure Setup

### Step 1: Initialize Terraform

```bash
cd aws-infrastructure/terraform

# Initialize Terraform
terraform init

# Plan the deployment
terraform plan -var-file="terraform.tfvars"

# Apply the infrastructure
terraform apply -var-file="terraform.tfvars"
```

### Step 2: Configure Terraform Variables

Create `terraform.tfvars`:
```hcl
aws_region = "us-east-1"
environment = "dev"
project_name = "intelliclaim"

# Networking
vpc_cidr = "10.0.0.0/16"
availability_zones = 2

# Database
db_instance_class = "db.t3.micro"
db_allocated_storage = 20
db_max_allocated_storage = 100

# ECS
ecs_cpu = 512
ecs_memory = 1024
ecs_desired_count = 1

# Domain (optional)
domain_name = "your-domain.com"
certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/your-cert"

# Security
allowed_cidr_blocks = ["0.0.0.0/0"]

# Monitoring
enable_detailed_monitoring = true

# Cost optimization
enable_spot_instances = false

# Backup
backup_retention_period = 7
```

### Step 3: Set Up GitHub Connection

1. Go to AWS Console → Developer Tools → Settings → Connections
2. Create new connection → GitHub
3. Follow the GitHub OAuth flow
4. Note the connection ARN and update `github_connection_arn` in terraform.tfvars

## 🚀 Application Deployment

### Step 1: Update Backend Configuration

Update `backend/chatgpt_app.py` to use AWS services:

```python
# Add AWS imports
from aws_config import get_aws_config
from aws_database import vector_db
from aws_storage import s3_storage

# Initialize AWS services
aws_config = get_aws_config()

# Update RAG system initialization
class IntelliClaimRAG:
    def __init__(self):
        self.llm = GPT5Client(os.getenv("AIMLAPI_KEY"))
        self.embedding_manager = EmbeddingManager()
        # Use AWS RDS instead of ChromaDB
        self.vector_store = vector_db
        # Initialize AWS storage
        self.s3_storage = s3_storage
        # ... rest of initialization
```

### Step 2: Build and Push Docker Images

```bash
# Build backend image
cd backend
docker build -t intelliclaim-backend:latest .

# Build frontend image
cd ../frontend
docker build -t intelliclaim-frontend:latest .

# Tag and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker tag intelliclaim-backend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/intelliclaim-dev-backend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/intelliclaim-dev-backend:latest

docker tag intelliclaim-frontend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/intelliclaim-dev-frontend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/intelliclaim-dev-frontend:latest
```

### Step 3: Configure Secrets

```bash
# Update secrets in AWS Secrets Manager
aws secretsmanager update-secret \
    --secret-id intelliclaim-dev/application/secrets \
    --secret-string '{"AIMLAPI_KEY":"your-aimlapi-key","OPENAI_API_KEY":"your-openai-key"}'
```

### Step 4: Deploy via ECS

```bash
# Update ECS service to use new image
aws ecs update-service \
    --cluster intelliclaim-dev-cluster \
    --service intelliclaim-dev-service \
    --force-new-deployment
```

## 🗄️ Database Migration

### Step 1: Set Up pgvector Extension

```sql
-- Connect to your RDS instance and run:
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### Step 2: Migrate Data from ChromaDB

Create migration script:

```python
# scripts/migrate_to_aws.py
import asyncio
from backend.aws_database import vector_db
from backend.chatgpt_app import rag_system

async def migrate_data():
    # Initialize AWS database
    await vector_db.initialize()
    
    # Get existing documents from local ChromaDB
    collection = rag_system.vector_store._collection
    documents = collection.get()
    
    # Migrate each document
    for i, doc in enumerate(documents['documents']):
        metadata = documents['metadatas'][i]
        
        # Create DocumentChunk object
        chunk = DocumentChunk(
            id=f"migrated_{i}",
            content=doc,
            metadata=metadata,
            source=metadata.get('source', 'migrated'),
            chunk_id=str(i)
        )
        
        # Add to AWS database
        await vector_db.add_document_chunk(chunk)
        print(f"Migrated document {i+1}/{len(documents['documents'])}")

if __name__ == "__main__":
    asyncio.run(migrate_data())
```

### Step 3: Update Application Code

Replace ChromaDB usage with AWS database:

```python
# In your FastAPI endpoints
@app.post("/query")
async def process_query_endpoint(request: QueryRequest):
    # Use AWS vector database
    results = await vector_db.similarity_search(
        query_embedding, k=5
    )
    # ... rest of processing
```

## 🔄 CI/CD Pipeline

### Step 1: Set Up CodePipeline

The pipeline is automatically created by Terraform. It includes:

1. **Source**: GitHub repository
2. **Build**: Docker image build and push to ECR
3. **Deploy**: ECS service update and S3 sync

### Step 2: Configure Build Specs

Build specs are already configured in:
- `aws-infrastructure/terraform/buildspecs/backend-buildspec.yml`
- `aws-infrastructure/terraform/buildspecs/frontend-buildspec.yml`

### Step 3: Trigger Deployment

```bash
# Push to main branch to trigger deployment
git add .
git commit -m "Deploy to AWS"
git push origin main
```

## 🔒 Security Configuration

### 1. WAF Rules
- Rate limiting (2000 requests/5 minutes)
- AWS Managed Rules (Core Rule Set, SQL Injection, etc.)
- Custom rules for application-specific protection

### 2. VPC Security
- Private subnets for ECS tasks
- NAT Gateway for outbound internet access
- Security groups with least privilege

### 3. IAM Policies
- ECS execution role for container management
- ECS task role for AWS service access
- CodeBuild role for CI/CD operations

### 4. Secrets Management
- API keys stored in AWS Secrets Manager
- Automatic rotation capabilities
- Encrypted at rest and in transit

## 📊 Monitoring & Alerting

### CloudWatch Dashboards

```bash
# Create custom dashboard
aws cloudwatch put-dashboard \
    --dashboard-name IntelliClaim-Monitoring \
    --dashboard-body file://monitoring/dashboard.json
```

### Key Metrics to Monitor

1. **Application Metrics**
   - Request count and latency
   - Error rates
   - ECS task health

2. **Infrastructure Metrics**
   - CPU and memory utilization
   - Database connections
   - S3 request metrics

3. **Business Metrics**
   - Query processing time
   - Document upload success rate
   - Decision accuracy

### Alerting Rules

```bash
# Create CloudWatch alarms
aws cloudwatch put-metric-alarm \
    --alarm-name "IntelliClaim-High-Error-Rate" \
    --alarm-description "High error rate detected" \
    --metric-name "4xxErrorCount" \
    --namespace "AWS/ApplicationELB" \
    --statistic "Sum" \
    --period 300 \
    --threshold 10 \
    --comparison-operator "GreaterThanThreshold"
```

## 💰 Cost Optimization

### 1. Reserved Instances
```bash
# Purchase reserved instances for predictable workloads
aws ec2 describe-reserved-instances-offerings \
    --instance-type t3.micro \
    --product-description "Linux/UNIX"
```

### 2. Spot Instances
Enable spot instances in ECS for cost savings:
```hcl
# In terraform.tfvars
enable_spot_instances = true
```

### 3. S3 Lifecycle Policies
Automatic data archiving:
- Standard → IA (30 days)
- IA → Glacier (90 days)
- Glacier → Delete (365 days)

### 4. CloudWatch Cost Monitoring
```bash
# Set up billing alerts
aws cloudwatch put-metric-alarm \
    --alarm-name "AWS-Billing-Alert" \
    --alarm-description "Monthly billing exceeds $100" \
    --metric-name "EstimatedCharges" \
    --namespace "AWS/Billing" \
    --statistic "Maximum" \
    --period 86400 \
    --threshold 100
```

## 🔧 Troubleshooting

### Common Issues

#### 1. ECS Service Won't Start
```bash
# Check ECS service events
aws ecs describe-services \
    --cluster intelliclaim-dev-cluster \
    --services intelliclaim-dev-service

# Check task definition
aws ecs describe-task-definition \
    --task-definition intelliclaim-dev-task
```

#### 2. Database Connection Issues
```bash
# Test RDS connectivity
aws rds describe-db-clusters \
    --db-cluster-identifier intelliclaim-dev-aurora-cluster

# Check security groups
aws ec2 describe-security-groups \
    --group-ids sg-your-security-group-id
```

#### 3. S3 Access Issues
```bash
# Test S3 bucket access
aws s3 ls s3://intelliclaim-dev-documents-bucket/

# Check bucket policy
aws s3api get-bucket-policy \
    --bucket intelliclaim-dev-documents-bucket
```

### Debug Commands

```bash
# View ECS logs
aws logs tail /aws/ecs/intelliclaim-dev --follow

# Check CodeBuild logs
aws logs describe-log-streams \
    --log-group-name /aws/codebuild/intelliclaim-dev

# Monitor CloudWatch metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/ECS \
    --metric-name CPUUtilization \
    --dimensions Name=ServiceName,Value=intelliclaim-dev-service \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-01T23:59:59Z \
    --period 3600 \
    --statistics Average
```

## 📈 Performance Optimization

### 1. Auto Scaling Configuration
```bash
# Update auto scaling target
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --resource-id service/intelliclaim-dev-cluster/intelliclaim-dev-service \
    --scalable-dimension ecs:service:DesiredCount \
    --min-capacity 1 \
    --max-capacity 10
```

### 2. CloudFront Optimization
- Enable compression
- Configure cache behaviors
- Set up origin request policies

### 3. Database Optimization
- Enable connection pooling
- Configure read replicas for scaling
- Set up automated backups

## 🎯 Next Steps

1. **Set up monitoring dashboards**
2. **Configure automated backups**
3. **Implement disaster recovery**
4. **Set up staging environment**
5. **Configure production deployment**
6. **Set up cost monitoring**
7. **Implement security scanning**

## 📞 Support

For issues and questions:
1. Check AWS CloudWatch logs
2. Review Terraform state
3. Consult AWS documentation
4. Create GitHub issues for application-specific problems

---

**🎉 Congratulations! Your IntelliClaim application is now running on AWS with a fully cloud-centric architecture!**

The migration provides:
- **99.9% uptime** with multi-AZ deployment
- **Auto-scaling** based on demand
- **Global CDN** for fast content delivery
- **Enterprise security** with WAF and VPC
- **Cost optimization** with spot instances and lifecycle policies
- **Full observability** with CloudWatch and X-Ray

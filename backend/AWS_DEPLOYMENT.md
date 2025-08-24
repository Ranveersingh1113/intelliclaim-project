# AWS Lambda Deployment Guide for IntelliClaim Backend

## 🚀 Overview
This guide will help you deploy your IntelliClaim backend to AWS Lambda using the student free tier.

## 📋 Prerequisites
1. **AWS Account** with student verification
2. **AWS CLI** installed and configured
3. **Python 3.11** installed locally
4. **Git** for version control

## 🔑 AWS Free Tier Benefits (12 months)
- **Lambda**: 1M requests/month + 400K GB-seconds
- **API Gateway**: 1M API calls/month
- **S3**: 5GB storage
- **CloudWatch**: Basic monitoring

## 🛠️ Step-by-Step Deployment

### 1. Install and Configure AWS CLI
```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure
# Enter your Access Key ID, Secret Access Key, and region
```

### 2. Create IAM Role for Lambda
```bash
# Create trust policy file
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create the role
aws iam create-role \
  --role-name IntelliClaimLambdaRole \
  --assume-role-policy-document file://trust-policy.json

# Attach basic execution policy
aws iam attach-role-policy \
  --role-name IntelliClaimLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Get the role ARN
aws iam get-role --role-name IntelliClaimLambdaRole --query 'Role.Arn' --output text
```

### 3. Update Environment Variables
Create a `.env` file with your API keys:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 4. Deploy to Lambda
```bash
# Make script executable
chmod +x deploy-aws-lambda.sh

# Update ROLE_ARN in the script with your actual role ARN
# Then run deployment
./deploy-aws-lambda.sh
```

### 5. Create API Gateway
```bash
# Create REST API
aws apigateway create-rest-api \
  --name "IntelliClaim API" \
  --description "API for IntelliClaim Backend"

# Get API ID and root resource ID
API_ID=$(aws apigateway get-rest-apis --query 'items[?name==`IntelliClaim API`].id' --output text)
ROOT_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query 'items[?path==`/`].id' --output text)

# Create resource for your API
aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part "{proxy+}"

# Get the proxy resource ID
PROXY_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query 'items[?path==`{proxy+}`].id' --output text)

# Create ANY method
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $PROXY_ID \
  --http-method ANY \
  --authorization-type NONE

# Set Lambda integration
aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $PROXY_ID \
  --http-method ANY \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:intelliclaim-backend/invocations

# Deploy the API
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod
```

## 🔧 Configuration Options

### Lambda Function Settings
- **Memory**: 1024 MB (recommended for ML workloads)
- **Timeout**: 900 seconds (15 minutes max)
- **Runtime**: Python 3.11

### Environment Variables
- `GOOGLE_API_KEY`: Your Gemini API key
- `AWS_REGION`: Your AWS region

## 📊 Monitoring and Logs
```bash
# View Lambda logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/intelliclaim-backend"

# View recent logs
aws logs tail /aws/lambda/intelliclaim-backend --follow
```

## 💰 Cost Estimation (Free Tier)
- **Lambda**: Free for first 1M requests/month
- **API Gateway**: Free for first 1M calls/month
- **Data Transfer**: Free for first 15GB/month
- **Total**: ~$0/month within free tier limits

## 🚨 Important Notes
1. **Cold Starts**: Lambda functions may have 1-2 second cold starts
2. **Package Size**: Keep deployment package under 50MB for direct upload
3. **Timeout**: Maximum execution time is 15 minutes
4. **Memory**: More memory = faster execution but higher cost

## 🔍 Troubleshooting
- Check CloudWatch logs for errors
- Verify IAM permissions
- Ensure environment variables are set
- Check API Gateway integration settings

## 📚 Additional Resources
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [AWS Free Tier](https://aws.amazon.com/free/)

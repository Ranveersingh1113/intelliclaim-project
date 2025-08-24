import json
import os
from mangum import Mangum
from app import app

# Create handler for AWS Lambda
handler = Mangum(app, lifespan="off")

# Optional: Direct Lambda handler for simple requests
def lambda_handler(event, context):
    """AWS Lambda handler function"""
    try:
        # Handle API Gateway events
        if 'httpMethod' in event:
            return handler(event, context)
        
        # Handle direct Lambda invocations
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'IntelliClaim Backend is running on AWS Lambda!',
                'event': event
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

// API Configuration for IntelliClaim Frontend
// This file handles different environments and API endpoints

// Determine API base URL based on environment
const getApiBaseUrl = () => {
  // In production, use the ALB endpoint or CloudFront domain
  if (process.env.NODE_ENV === 'production') {
    // If deployed to CloudFront, API calls go through the same domain
    if (window.location.hostname.includes('cloudfront.net') || 
        window.location.hostname.includes('amazonaws.com')) {
      return window.location.origin;
    }
    // Otherwise use environment variable or default AWS ALB endpoint
    return process.env.REACT_APP_API_URL || 'https://your-alb-domain.elb.amazonaws.com';
  }
  
  // Development environment
  return process.env.REACT_APP_API_URL || 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

export const API_ENDPOINTS = {
  QUERY: `${API_BASE_URL}/query`,
  UPLOAD_DOCUMENT: `${API_BASE_URL}/upload-document`,
  UPLOAD_DOCUMENT_URL: `${API_BASE_URL}/upload-document-url`,
  DOCUMENTS: `${API_BASE_URL}/documents`,
  SYSTEM_STATS: `${API_BASE_URL}/system-stats`,
  HEALTH: `${API_BASE_URL}/health`,
};

export const getApiUrl = (endpoint) => {
  return `${API_BASE_URL}${endpoint}`;
};

// AWS-specific configuration
export const AWS_CONFIG = {
  REGION: process.env.REACT_APP_AWS_REGION || 'us-east-1',
  S3_BUCKET: process.env.REACT_APP_S3_BUCKET || '',
  CLOUDFRONT_DOMAIN: process.env.REACT_APP_CLOUDFRONT_DOMAIN || '',
  ENABLE_ANALYTICS: process.env.REACT_APP_ENABLE_ANALYTICS === 'true',
};

export default API_BASE_URL;
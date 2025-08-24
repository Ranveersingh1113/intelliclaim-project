// API Configuration for IntelliClaim Frontend
// This file handles different environments and API endpoints

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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

export default API_BASE_URL;
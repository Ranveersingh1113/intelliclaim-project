import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Badge } from './components/ui/badge';
import { Progress } from './components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from './components/ui/alert';
import { Brain, CheckCircle, XCircle, Clock, Cpu, Eye, MessageSquare, Search, AlertCircle, TrendingUp, Shield, Database, Upload, FileText, CheckCircle2 } from 'lucide-react';
import { API_ENDPOINTS } from './config/api';

const IntelliClaimDemo = () => {
  const [query, setQuery] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [showAgentFlow, setShowAgentFlow] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [systemStats, setSystemStats] = useState(null);
  const [documents, setDocuments] = useState([]);

  const API_ENDPOINT = API_ENDPOINTS.QUERY;
  const UPLOAD_ENDPOINT = API_ENDPOINTS.UPLOAD_DOCUMENT;
  const UPLOAD_URL_ENDPOINT = API_ENDPOINTS.UPLOAD_DOCUMENT_URL;
  const DOCUMENTS_ENDPOINT = API_ENDPOINTS.DOCUMENTS;
  const STATS_ENDPOINT = API_ENDPOINTS.SYSTEM_STATS;

  const sampleQueries = [
    "46-year-old male, knee surgery in Pune, 3-month-old insurance policy",
    "Female, 35 years, heart surgery, Mumbai, 1-year policy",
    "25M, dental treatment, Chennai, new policy",
    "60-year-old woman, cataract surgery, Delhi, 5-year-old policy"
  ];

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    setIsUploading(true);
    setUploadStatus(null);

    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(UPLOAD_ENDPOINT, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || `Upload failed for ${file.name}`);
        }

        const result = await response.json();
        
        setUploadedFiles(prev => [...prev, {
          name: file.name,
          status: 'success',
          documentsAdded: result.documents_added,
          timestamp: new Date().toLocaleTimeString()
        }]);

        setUploadStatus({
          type: 'success',
          message: `Successfully uploaded ${file.name} (${result.documents_added} documents added)`
        });

        // Refresh documents and stats
        fetchDocuments();
        fetchSystemStats();

      } catch (err) {
        console.error(`Upload failed for ${file.name}:`, err);
        setUploadedFiles(prev => [...prev, {
          name: file.name,
          status: 'error',
          error: err.message,
          timestamp: new Date().toLocaleTimeString()
        }]);

        setUploadStatus({
          type: 'error',
          message: `Failed to upload ${file.name}: ${err.message}`
        });
      }
    }

    setIsUploading(false);
    // Clear the file input
    event.target.value = '';
  };

  const processQuery = async () => {
    if (!query.trim()) return;

    setIsProcessing(true);
    setResult(null);
    setError(null);
    setShowAgentFlow(true);

    try {
      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);

    } catch (err) {
      console.error("API call failed:", err);
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const getDecisionCardStyle = () => {
    if (!result) return 'border-gray-200';
    switch (result.decision) {
      case 'APPROVED': return 'border-green-400 bg-green-50';
      case 'REJECTED': return 'border-red-400 bg-red-50';
      default: return 'border-yellow-400 bg-yellow-50';
    }
  };

  const getDecisionIcon = () => {
    if (!result) return null;
    switch (result.decision) {
        case 'APPROVED': return <CheckCircle className="w-6 h-6 text-green-600" />;
        case 'REJECTED': return <XCircle className="w-6 h-6 text-red-600" />;
        default: return <Clock className="w-6 h-6 text-yellow-600" />;
    }
  };

  const fetchSystemStats = async () => {
    try {
      const response = await fetch(STATS_ENDPOINT);
      if (response.ok) {
        const stats = await response.json();
        setSystemStats(stats);
      }
    } catch (err) {
      console.error("Failed to fetch system stats:", err);
    }
  };

  const fetchDocuments = async () => {
    try {
      const response = await fetch(DOCUMENTS_ENDPOINT);
      if (response.ok) {
        const data = await response.json();
        setDocuments(data.document_sources || []);
      }
    } catch (err) {
      console.error("Failed to fetch documents:", err);
    }
  };

  const deleteDocument = async (filename) => {
    try {
      const response = await fetch(`http://localhost:8000/documents/${filename}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        // Refresh documents list
        fetchDocuments();
        fetchSystemStats();
        // Remove from uploaded files list
        setUploadedFiles(prev => prev.filter(file => file.name !== filename));
      }
    } catch (err) {
      console.error("Failed to delete document:", err);
    }
  };

  // Load initial data
  React.useEffect(() => {
    fetchSystemStats();
    fetchDocuments();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        
        <div className="text-center space-y-2">
            <div className="flex items-center justify-center space-x-3">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-3xl sm:text-4xl font-bold text-gray-800">IntelliClaim</h1>
            </div>
            <p className="text-lg text-gray-600">Next-Generation AI Document Processing</p>
        </div>

        {/* System Stats */}
        {systemStats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="shadow-sm">
              <CardContent className="pt-6">
                <div className="flex items-center space-x-2">
                  <Database className="w-5 h-5 text-blue-500" />
                  <div>
                    <p className="text-2xl font-bold">{systemStats.total_documents}</p>
                    <p className="text-xs text-gray-500">Total Documents</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="shadow-sm">
              <CardContent className="pt-6">
                <div className="flex items-center space-x-2">
                  <Shield className="w-5 h-5 text-green-500" />
                  <div>
                    <p className="text-2xl font-bold">{systemStats.system_status}</p>
                    <p className="text-xs text-gray-500">System Status</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="shadow-sm">
              <CardContent className="pt-6">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="w-5 h-5 text-purple-500" />
                  <div>
                    <p className="text-2xl font-bold">{systemStats.api_version}</p>
                    <p className="text-xs text-gray-500">API Version</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="shadow-sm">
              <CardContent className="pt-6">
                <div className="flex items-center space-x-2">
                  <Clock className="w-5 h-5 text-orange-500" />
                  <div>
                    <p className="text-sm font-bold">{new Date(systemStats.last_updated).toLocaleTimeString()}</p>
                    <p className="text-xs text-gray-500">Last Updated</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Document Upload Section */}
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Upload className="w-5 h-5" />
              <span>Upload Policy Documents</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
              <Input
                id="file-upload"
                type="file"
                accept=".pdf,.docx,.eml"
                multiple
                onChange={handleFileUpload}
                disabled={isUploading}
                className="flex-1"
              />
              <Button 
                variant="outline" 
                disabled={isUploading}
                className="px-6"
                onClick={() => document.getElementById('file-upload')?.click()}
              >
                {isUploading ? <Clock className="w-4 h-4 animate-spin" /> : 'Choose Files'}
              </Button>
            </div>
            
            {uploadStatus && (
              <Alert variant={uploadStatus.type === 'success' ? 'default' : 'destructive'}>
                {uploadStatus.type === 'success' ? (
                  <CheckCircle2 className="h-4 w-4" />
                ) : (
                  <AlertCircle className="h-4 w-4" />
                )}
                <AlertDescription>{uploadStatus.message}</AlertDescription>
              </Alert>
            )}

            {/* URL Upload */}
            <UrlUpload
              endpoint={UPLOAD_URL_ENDPOINT}
              onSuccess={() => { fetchDocuments(); fetchSystemStats(); }}
              setUploadStatus={setUploadStatus}
            />

            {/* Document Management */}
            {(documents.length > 0 || uploadedFiles.length > 0) && (
              <div className="space-y-2">
                <h4 className="font-medium text-sm">Document Management:</h4>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {documents.map((doc, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded border">
                      <div className="flex items-center space-x-2">
                        <FileText className="w-4 h-4 text-gray-500" />
                        <span className="text-sm font-medium">{doc}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="secondary" className="text-xs">Indexed</Badge>
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => deleteDocument(doc)}
                          className="text-red-600 hover:text-red-700"
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                  ))}
                  {uploadedFiles.map((file, index) => (
                    <div key={`uploaded-${index}`} className="flex items-center justify-between p-2 bg-gray-50 rounded border">
                      <div className="flex items-center space-x-2">
                        <FileText className="w-4 h-4 text-gray-500" />
                        <span className="text-sm font-medium">{file.name}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        {file.status === 'success' ? (
                          <Badge variant="secondary" className="text-xs">
                            {file.documentsAdded} docs
                          </Badge>
                        ) : (
                          <Badge variant="destructive" className="text-xs">
                            Failed
                          </Badge>
                        )}
                        <span className="text-xs text-gray-500">{file.timestamp}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2"><MessageSquare className="w-5 h-5" /><span>Enter Your Query</span></CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., 46-year-old male, knee surgery in Pune, 3-month policy"
                className="flex-1 text-base"
                disabled={isProcessing}
                onKeyPress={(e) => e.key === 'Enter' && processQuery()}
              />
              <Button onClick={processQuery} disabled={isProcessing || !query.trim()} className="px-6 bg-blue-600 hover:bg-blue-700">
                {isProcessing ? <Clock className="w-4 h-4 animate-spin" /> : 'Process'}
              </Button>
            </div>
            <div className="space-y-2">
              <p className="text-sm text-gray-500">Or try a sample query:</p>
              <div className="flex flex-wrap gap-2">
                {sampleQueries.map((sample, index) => (
                  <Button key={index} variant="outline" size="sm" onClick={() => setQuery(sample)} disabled={isProcessing}>{sample}</Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {isProcessing && (
            <Card>
                <CardContent className="pt-6 text-center">
                    <div className="flex items-center justify-center space-x-3">
                        <Cpu className="w-6 h-6 animate-pulse text-blue-500" />
                        <p className="font-medium text-gray-700">Processing with Multi-Agent Pipeline...</p>
                    </div>
                    <Progress value={66} className="w-full mt-4 h-2" />
                </CardContent>
            </Card>
        )}
        
        {error && (
            <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
            </Alert>
        )}

        {result && !isProcessing && (
          <div className="grid lg:grid-cols-5 gap-6">
            <div className="lg:col-span-3 space-y-6">
                <Card className={`shadow-sm ${getDecisionCardStyle()}`}>
                    <CardHeader>
                        <CardTitle className="flex items-center space-x-2">
                            {getDecisionIcon()}
                            <span>Decision: {result.decision}</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {result.amount && (
                          <div className="bg-white p-3 rounded-lg border">
                            <div className="text-2xl font-bold text-gray-800">₹{result.amount.toLocaleString()}</div>
                            <div className="text-sm text-gray-500">Approved Amount</div>
                          </div>
                        )}
                        <div>
                            <h4 className="font-medium mb-1">Justification:</h4>
                            <p className="text-sm text-gray-700 p-3 rounded border bg-white">{result.justification}</p>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center space-x-2"><Search className="w-5 h-5" /><span>Relevant Clauses</span></CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        {result.clause_mappings && result.clause_mappings.length > 0 ? (
                          result.clause_mappings.map((mapping, index) => (
                            <div key={index} className="text-sm p-3 border rounded bg-gray-50">
                              <p className="font-medium text-gray-800">{mapping.clause_text}</p>
                              <p className="text-xs text-gray-500">Source: {mapping.source}</p>
                            </div>
                          ))
                        ) : (
                          <div className="text-sm p-3 border rounded bg-gray-50 text-gray-500">
                            No relevant clauses found. Upload policy documents to see relevant clauses.
                          </div>
                        )}
                    </CardContent>
                </Card>
            </div>

            <div className="lg:col-span-2 space-y-6">
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center space-x-2"><Eye className="w-5 h-5" /><span>Processing Overview</span></CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                         <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">Confidence Score</span>
                            <Badge variant="secondary">{result.confidence_score}%</Badge>
                         </div>
                         <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">Processing Time</span>
                            <Badge variant="secondary">{result.processing_time}s</Badge>
                         </div>
                         <div>
                            <h4 className="font-medium mb-2 text-sm">Audit Trail:</h4>
                            <ul className="space-y-2">
                                {result.audit_trail && result.audit_trail.map((step, index) => (
                                    <li key={index} className="flex items-start space-x-2 text-sm">
                                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                                        <span>{step}</span>
                                    </li>
                                ))}
                            </ul>
                         </div>
                    </CardContent>
                </Card>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default IntelliClaimDemo;

// Inline component for URL upload to avoid extra files
const UrlUpload = ({ endpoint, onSuccess, setUploadStatus }) => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setUploadStatus(null);
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Upload by URL failed (${res.status})`);
      }
      const data = await res.json();
      setUploadStatus({ type: 'success', message: `URL ingested successfully (${data.documents_added || data.total_documents || 'updated index'})` });
      setUrl('');
      onSuccess && onSuccess();
    } catch (e) {
      setUploadStatus({ type: 'error', message: e.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
      <Input
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Paste PDF/DOCX/EML URL (e.g., blob URL)"
        disabled={loading}
        className="flex-1"
      />
      <Button variant="outline" disabled={loading || !url.trim()} onClick={submit} className="px-6">
        {loading ? 'Uploading...' : 'Upload URL'}
      </Button>
    </div>
  );
};
import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import Button from '../../components/common/Button';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import Alert from '../../components/common/Alert';
import { 
  BookOpen, 
  Play, 
  Copy, 
  Download, 
  Search, 
  Filter,
  ChevronDown,
  ChevronRight,
  Code,
  Globe,
  Shield,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Info,
  Zap,
  Database,
  Users,
  Package,
  ShoppingCart,
  BarChart3,
  Settings
} from 'lucide-react';

const APIDocumentation = () => {
  const { addNotification } = useApp();
  const [apiDocs, setApiDocs] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [expandedEndpoints, setExpandedEndpoints] = useState(new Set());
  const [testResults, setTestResults] = useState({});
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    loadAPIDocumentation();
  }, []);

  const loadAPIDocumentation = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Simulate API documentation data
      const mockDocs = {
        categories: [
          {
            id: 'authentication',
            name: 'Authentication',
            description: 'User authentication and authorization endpoints',
            icon: Shield,
            endpoints: [
              {
                id: 'login',
                method: 'POST',
                path: '/api/auth/login',
                description: 'Authenticate user with credentials',
                parameters: [
                  { name: 'username', type: 'string', required: true, description: 'User username or email' },
                  { name: 'password', type: 'string', required: true, description: 'User password' }
                ],
                responses: [
                  { status: 200, description: 'Login successful', example: { access_token: 'jwt_token', user: {} } },
                  { status: 401, description: 'Invalid credentials', example: { error: 'Invalid credentials' } }
                ]
              },
              {
                id: 'logout',
                method: 'POST',
                path: '/api/auth/logout',
                description: 'Logout user and invalidate token',
                responses: [
                  { status: 200, description: 'Logout successful', example: { message: 'Logged out successfully' } }
                ]
              }
            ]
          },
          {
            id: 'companies',
            name: 'Companies',
            description: 'Company management endpoints',
            icon: Users,
            endpoints: [
              {
                id: 'list-companies',
                method: 'GET',
                path: '/api/companies',
                description: 'Get list of companies',
                parameters: [
                  { name: 'page', type: 'integer', required: false, description: 'Page number' },
                  { name: 'limit', type: 'integer', required: false, description: 'Items per page' },
                  { name: 'search', type: 'string', required: false, description: 'Search term' }
                ],
                responses: [
                  { status: 200, description: 'Companies retrieved successfully', example: { companies: [], total: 0 } }
                ]
              },
              {
                id: 'create-company',
                method: 'POST',
                path: '/api/companies',
                description: 'Create new company',
                parameters: [
                  { name: 'name', type: 'string', required: true, description: 'Company name' },
                  { name: 'email', type: 'string', required: true, description: 'Company email' },
                  { name: 'phone', type: 'string', required: false, description: 'Company phone' }
                ],
                responses: [
                  { status: 201, description: 'Company created successfully', example: { company: {} } },
                  { status: 400, description: 'Validation error', example: { error: 'Validation failed' } }
                ]
              }
            ]
          },
          {
            id: 'inventory',
            name: 'Inventory',
            description: 'Inventory management endpoints',
            icon: Package,
            endpoints: [
              {
                id: 'list-items',
                method: 'GET',
                path: '/api/inventory/items',
                description: 'Get list of inventory items',
                parameters: [
                  { name: 'category', type: 'string', required: false, description: 'Filter by category' },
                  { name: 'status', type: 'string', required: false, description: 'Filter by status' }
                ],
                responses: [
                  { status: 200, description: 'Items retrieved successfully', example: { items: [], total: 0 } }
                ]
              }
            ]
          },
          {
            id: 'pos',
            name: 'Point of Sale',
            description: 'POS system endpoints',
            icon: ShoppingCart,
            endpoints: [
              {
                id: 'process-sale',
                method: 'POST',
                path: '/api/pos/sales',
                description: 'Process a new sale',
                parameters: [
                  { name: 'items', type: 'array', required: true, description: 'Sale items' },
                  { name: 'customer_id', type: 'integer', required: false, description: 'Customer ID' },
                  { name: 'payment_method', type: 'string', required: true, description: 'Payment method' }
                ],
                responses: [
                  { status: 201, description: 'Sale processed successfully', example: { sale: {} } }
                ]
              }
            ]
          },
          {
            id: 'reports',
            name: 'Reports',
            description: 'Reporting and analytics endpoints',
            icon: BarChart3,
            endpoints: [
              {
                id: 'sales-report',
                method: 'GET',
                path: '/api/reports/sales',
                description: 'Generate sales report',
                parameters: [
                  { name: 'start_date', type: 'string', required: true, description: 'Start date (YYYY-MM-DD)' },
                  { name: 'end_date', type: 'string', required: true, description: 'End date (YYYY-MM-DD)' }
                ],
                responses: [
                  { status: 200, description: 'Report generated successfully', example: { report: {} } }
                ]
              }
            ]
          }
        ]
      };
      
      setApiDocs(mockDocs);
    } catch (err) {
      setError(err.message);
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (term) => {
    setSearchTerm(term);
  };

  const handleCategoryFilter = (category) => {
    setSelectedCategory(category);
  };

  const toggleEndpoint = (endpointId) => {
    const newExpanded = new Set(expandedEndpoints);
    if (newExpanded.has(endpointId)) {
      newExpanded.delete(endpointId);
    } else {
      newExpanded.add(endpointId);
    }
    setExpandedEndpoints(newExpanded);
  };

  const handleTestEndpoint = async (endpoint) => {
    setTesting(true);
    try {
      // Simulate API test
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const result = {
        success: Math.random() > 0.2, // 80% success rate
        responseTime: Math.floor(Math.random() * 500) + 100,
        status: Math.random() > 0.2 ? 200 : 400,
        response: { message: 'Test completed successfully' }
      };
      
      setTestResults(prev => ({
        ...prev,
        [endpoint.id]: result
      }));
      
      addNotification({
        type: result.success ? 'success' : 'warning',
        title: result.success ? 'Test Passed' : 'Test Failed',
        message: `Endpoint ${endpoint.path} ${result.success ? 'passed' : 'failed'} in ${result.responseTime}ms`,
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Test Error',
        message: err.message,
      });
    } finally {
      setTesting(false);
    }
  };

  const handleCopyCode = (code) => {
    navigator.clipboard.writeText(code);
    addNotification({
      type: 'success',
      title: 'Copied',
      message: 'Code copied to clipboard',
    });
  };

  const handleDownloadDocs = () => {
    const data = JSON.stringify(apiDocs, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'api-documentation.json';
    a.click();
    URL.revokeObjectURL(url);
    
    addNotification({
      type: 'success',
      title: 'Downloaded',
      message: 'API documentation downloaded successfully',
    });
  };

  const filteredCategories = apiDocs?.categories?.filter(category => {
    if (selectedCategory !== 'all' && category.id !== selectedCategory) {
      return false;
    }
    
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      return category.name.toLowerCase().includes(searchLower) ||
             category.description.toLowerCase().includes(searchLower) ||
             category.endpoints.some(endpoint => 
               endpoint.path.toLowerCase().includes(searchLower) ||
               endpoint.description.toLowerCase().includes(searchLower)
             );
    }
    
    return true;
  }) || [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading API documentation..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center space-x-2">
            <BookOpen className="w-6 h-6 text-primary-600" />
            <span>API Documentation</span>
          </h1>
          <p className="text-gray-600">Interactive API documentation and testing interface</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={handleDownloadDocs}
            className="flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Download</span>
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert type="danger" title="Error">
          {error}
        </Alert>
      )}

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-4 mb-4">
          <div className="flex-1 relative">
            <input
              type="text"
              placeholder="Search endpoints..."
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full px-4 py-2 pl-10 pr-4 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          </div>
          
          <select
            value={selectedCategory}
            onChange={(e) => handleCategoryFilter(e.target.value)}
            className="form-input"
          >
            <option value="all">All Categories</option>
            {apiDocs?.categories?.map(category => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* API Categories */}
      <div className="space-y-6">
        {filteredCategories.map((category) => {
          const CategoryIcon = category.icon;
          
          return (
            <div key={category.id} className="bg-white rounded-lg shadow">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                    <CategoryIcon className="w-5 h-5 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">{category.name}</h3>
                    <p className="text-sm text-gray-500">{category.description}</p>
                  </div>
                </div>
              </div>
              
              <div className="p-6">
                <div className="space-y-4">
                  {category.endpoints.map((endpoint) => {
                    const isExpanded = expandedEndpoints.has(endpoint.id);
                    const testResult = testResults[endpoint.id];
                    
                    return (
                      <div key={endpoint.id} className="border border-gray-200 rounded-lg">
                        <div className="p-4">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <button
                                onClick={() => toggleEndpoint(endpoint.id)}
                                className="text-gray-400 hover:text-gray-600"
                              >
                                {isExpanded ? (
                                  <ChevronDown className="w-5 h-5" />
                                ) : (
                                  <ChevronRight className="w-5 h-5" />
                                )}
                              </button>
                              
                              <div className="flex items-center space-x-2">
                                <span className={`px-2 py-1 text-xs font-medium rounded ${
                                  endpoint.method === 'GET' ? 'bg-success-100 text-success-800' :
                                  endpoint.method === 'POST' ? 'bg-primary-100 text-primary-800' :
                                  endpoint.method === 'PUT' ? 'bg-warning-100 text-warning-800' :
                                  endpoint.method === 'DELETE' ? 'bg-danger-100 text-danger-800' :
                                  'bg-gray-100 text-gray-800'
                                }`}>
                                  {endpoint.method}
                                </span>
                                
                                <code className="text-sm font-mono text-gray-900">
                                  {endpoint.path}
                                </code>
                              </div>
                            </div>
                            
                            <div className="flex items-center space-x-2">
                              {testResult && (
                                <div className={`flex items-center space-x-1 ${
                                  testResult.success ? 'text-success-600' : 'text-danger-600'
                                }`}>
                                  {testResult.success ? (
                                    <CheckCircle className="w-4 h-4" />
                                  ) : (
                                    <XCircle className="w-4 h-4" />
                                  )}
                                  <span className="text-sm">{testResult.responseTime}ms</span>
                                </div>
                              )}
                              
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleTestEndpoint(endpoint)}
                                loading={testing}
                                className="flex items-center space-x-1"
                              >
                                <Play className="w-4 h-4" />
                                <span>Test</span>
                              </Button>
                            </div>
                          </div>
                          
                          <p className="text-sm text-gray-600 mt-2 ml-8">
                            {endpoint.description}
                          </p>
                        </div>
                        
                        {isExpanded && (
                          <div className="border-t border-gray-200 p-4 space-y-4">
                            {/* Parameters */}
                            {endpoint.parameters && endpoint.parameters.length > 0 && (
                              <div>
                                <h4 className="text-sm font-medium text-gray-900 mb-2">Parameters</h4>
                                <div className="space-y-2">
                                  {endpoint.parameters.map((param, index) => (
                                    <div key={index} className="flex items-center space-x-4 text-sm">
                                      <div className="w-24">
                                        <code className="text-gray-900">{param.name}</code>
                                        {param.required && (
                                          <span className="text-danger-500 ml-1">*</span>
                                        )}
                                      </div>
                                      <div className="w-16 text-gray-500">{param.type}</div>
                                      <div className="flex-1 text-gray-600">{param.description}</div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                            
                            {/* Responses */}
                            {endpoint.responses && endpoint.responses.length > 0 && (
                              <div>
                                <h4 className="text-sm font-medium text-gray-900 mb-2">Responses</h4>
                                <div className="space-y-2">
                                  {endpoint.responses.map((response, index) => (
                                    <div key={index} className="border border-gray-200 rounded p-3">
                                      <div className="flex items-center space-x-2 mb-2">
                                        <span className={`px-2 py-1 text-xs font-medium rounded ${
                                          response.status >= 200 && response.status < 300 ? 'bg-success-100 text-success-800' :
                                          response.status >= 400 ? 'bg-danger-100 text-danger-800' :
                                          'bg-warning-100 text-warning-800'
                                        }`}>
                                          {response.status}
                                        </span>
                                        <span className="text-sm text-gray-600">{response.description}</span>
                                      </div>
                                      
                                      {response.example && (
                                        <div className="mt-2">
                                          <button
                                            onClick={() => handleCopyCode(JSON.stringify(response.example, null, 2))}
                                            className="flex items-center space-x-1 text-xs text-gray-500 hover:text-gray-700 mb-1"
                                          >
                                            <Copy className="w-3 h-3" />
                                            <span>Copy</span>
                                          </button>
                                          <pre className="bg-gray-50 rounded p-2 text-xs overflow-x-auto">
                                            <code>{JSON.stringify(response.example, null, 2)}</code>
                                          </pre>
                                        </div>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                            
                            {/* Test Result */}
                            {testResult && (
                              <div>
                                <h4 className="text-sm font-medium text-gray-900 mb-2">Test Result</h4>
                                <div className={`p-3 rounded ${
                                  testResult.success ? 'bg-success-50 border border-success-200' : 'bg-danger-50 border border-danger-200'
                                }`}>
                                  <div className="flex items-center space-x-2 mb-2">
                                    {testResult.success ? (
                                      <CheckCircle className="w-4 h-4 text-success-600" />
                                    ) : (
                                      <XCircle className="w-4 h-4 text-danger-600" />
                                    )}
                                    <span className={`text-sm font-medium ${
                                      testResult.success ? 'text-success-800' : 'text-danger-800'
                                    }`}>
                                      {testResult.success ? 'Test Passed' : 'Test Failed'}
                                    </span>
                                    <span className="text-sm text-gray-500">
                                      ({testResult.responseTime}ms)
                                    </span>
                                  </div>
                                  
                                  {testResult.response && (
                                    <div className="mt-2">
                                      <button
                                        onClick={() => handleCopyCode(JSON.stringify(testResult.response, null, 2))}
                                        className="flex items-center space-x-1 text-xs text-gray-500 hover:text-gray-700 mb-1"
                                      >
                                        <Copy className="w-3 h-3" />
                                        <span>Copy Response</span>
                                      </button>
                                      <pre className="bg-white rounded p-2 text-xs overflow-x-auto">
                                        <code>{JSON.stringify(testResult.response, null, 2)}</code>
                                      </pre>
                                    </div>
                                  )}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default APIDocumentation;
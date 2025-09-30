import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { aiService } from '../../services/aiService';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import Alert from '../common/Alert';
import { 
  Brain, 
  TrendingUp, 
  TrendingDown,
  Target,
  Star,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  Filter,
  SortAsc,
  SortDesc,
  Eye,
  EyeOff,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Info
} from 'lucide-react';

const SmartRecommendations = ({ 
  type = 'all', 
  customerId = null, 
  productId = null,
  onRecommendationClick,
  className = ''
}) => {
  const { addNotification } = useApp();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filteredRecommendations, setFilteredRecommendations] = useState([]);
  const [filters, setFilters] = useState({
    category: 'all',
    confidence: 'all',
    impact: 'all',
    status: 'all'
  });
  const [sortBy, setSortBy] = useState('confidence');
  const [sortOrder, setSortOrder] = useState('desc');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadRecommendations();
  }, [type, customerId, productId]);

  useEffect(() => {
    applyFiltersAndSort();
  }, [recommendations, filters, sortBy, sortOrder]);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await aiService.getSmartRecommendations(type, {
        customer_id: customerId,
        product_id: productId
      });
      
      setRecommendations(data);
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

  const applyFiltersAndSort = () => {
    let filtered = [...recommendations];

    // Apply filters
    if (filters.category !== 'all') {
      filtered = filtered.filter(rec => rec.category === filters.category);
    }
    if (filters.confidence !== 'all') {
      const confidenceThreshold = filters.confidence === 'high' ? 80 : 
                                 filters.confidence === 'medium' ? 60 : 40;
      filtered = filtered.filter(rec => rec.confidence >= confidenceThreshold);
    }
    if (filters.impact !== 'all') {
      filtered = filtered.filter(rec => rec.impact === filters.impact);
    }
    if (filters.status !== 'all') {
      filtered = filtered.filter(rec => rec.status === filters.status);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];
      
      if (sortBy === 'confidence' || sortBy === 'impact_score') {
        aValue = parseFloat(aValue);
        bValue = parseFloat(bValue);
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    setFilteredRecommendations(filtered);
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const handleSortChange = (newSortBy) => {
    if (sortBy === newSortBy) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(newSortBy);
      setSortOrder('desc');
    }
  };

  const handleRecommendationAction = async (recommendationId, action) => {
    try {
      await aiService.updateAIRecommendations(recommendationId, {
        action,
        timestamp: new Date().toISOString()
      });
      
      addNotification({
        type: 'success',
        title: 'Success',
        message: `Recommendation ${action} successfully`,
      });
      
      // Reload recommendations
      loadRecommendations();
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  const handleRecommendationClick = (recommendation) => {
    onRecommendationClick?.(recommendation);
  };

  const getRecommendationIcon = (category) => {
    switch (category) {
      case 'product':
        return Target;
      case 'customer':
        return Star;
      case 'pricing':
        return TrendingUp;
      case 'inventory':
        return AlertTriangle;
      default:
        return Brain;
    }
  };

  const getRecommendationColor = (impact) => {
    switch (impact) {
      case 'high':
        return 'text-success-600 bg-success-100';
      case 'medium':
        return 'text-warning-600 bg-warning-100';
      case 'low':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-primary-600 bg-primary-100';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'text-success-600';
    if (confidence >= 60) return 'text-warning-600';
    return 'text-danger-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading recommendations..." />
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900 flex items-center space-x-2">
            <Brain className="w-5 h-5 text-primary-600" />
            <span>Smart Recommendations</span>
          </h3>
          <p className="text-sm text-gray-500">
            {filteredRecommendations.length} of {recommendations.length} recommendations
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-1"
          >
            <Filter className="w-4 h-4" />
            <span>Filters</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={loadRecommendations}
            className="flex items-center space-x-1"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert type="danger" title="Error">
          {error}
        </Alert>
      )}

      {/* Filters */}
      {showFilters && (
        <div className="bg-gray-50 rounded-lg p-4 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="form-label">Category</label>
              <select
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                className="form-input"
              >
                <option value="all">All Categories</option>
                <option value="product">Product</option>
                <option value="customer">Customer</option>
                <option value="pricing">Pricing</option>
                <option value="inventory">Inventory</option>
                <option value="marketing">Marketing</option>
              </select>
            </div>
            
            <div>
              <label className="form-label">Confidence</label>
              <select
                value={filters.confidence}
                onChange={(e) => handleFilterChange('confidence', e.target.value)}
                className="form-input"
              >
                <option value="all">All Levels</option>
                <option value="high">High (80%+)</option>
                <option value="medium">Medium (60-79%)</option>
                <option value="low">Low (40-59%)</option>
              </select>
            </div>
            
            <div>
              <label className="form-label">Impact</label>
              <select
                value={filters.impact}
                onChange={(e) => handleFilterChange('impact', e.target.value)}
                className="form-input"
              >
                <option value="all">All Impacts</option>
                <option value="high">High Impact</option>
                <option value="medium">Medium Impact</option>
                <option value="low">Low Impact</option>
              </select>
            </div>
            
            <div>
              <label className="form-label">Status</label>
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="form-input"
              >
                <option value="all">All Status</option>
                <option value="new">New</option>
                <option value="applied">Applied</option>
                <option value="dismissed">Dismissed</option>
                <option value="pending">Pending</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Sort Options */}
      <div className="flex items-center space-x-2">
        <span className="text-sm text-gray-500">Sort by:</span>
        <button
          onClick={() => handleSortChange('confidence')}
          className={`flex items-center space-x-1 px-2 py-1 text-sm rounded ${
            sortBy === 'confidence' ? 'bg-primary-100 text-primary-700' : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <span>Confidence</span>
          {sortBy === 'confidence' && (
            sortOrder === 'asc' ? <SortAsc className="w-3 h-3" /> : <SortDesc className="w-3 h-3" />
          )}
        </button>
        <button
          onClick={() => handleSortChange('impact_score')}
          className={`flex items-center space-x-1 px-2 py-1 text-sm rounded ${
            sortBy === 'impact_score' ? 'bg-primary-100 text-primary-700' : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <span>Impact</span>
          {sortBy === 'impact_score' && (
            sortOrder === 'asc' ? <SortAsc className="w-3 h-3" /> : <SortDesc className="w-3 h-3" />
          )}
        </button>
        <button
          onClick={() => handleSortChange('created_at')}
          className={`flex items-center space-x-1 px-2 py-1 text-sm rounded ${
            sortBy === 'created_at' ? 'bg-primary-100 text-primary-700' : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <span>Date</span>
          {sortBy === 'created_at' && (
            sortOrder === 'asc' ? <SortAsc className="w-3 h-3" /> : <SortDesc className="w-3 h-3" />
          )}
        </button>
      </div>

      {/* Recommendations List */}
      {filteredRecommendations.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <Brain className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>No recommendations found</p>
          <p className="text-sm">Try adjusting your filters or refresh the data</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredRecommendations.map((recommendation, index) => {
            const Icon = getRecommendationIcon(recommendation.category);
            
            return (
              <div
                key={index}
                className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => handleRecommendationClick(recommendation)}
              >
                <div className="flex items-start space-x-3">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    getRecommendationColor(recommendation.impact)
                  }`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-medium text-gray-900">{recommendation.title}</h4>
                        <p className="text-sm text-gray-600 mt-1">{recommendation.description}</p>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <span className={`text-sm font-medium ${
                          getConfidenceColor(recommendation.confidence)
                        }`}>
                          {recommendation.confidence}%
                        </span>
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          getRecommendationColor(recommendation.impact)
                        }`}>
                          {recommendation.impact} impact
                        </span>
                      </div>
                    </div>
                    
                    <div className="mt-3 flex items-center justify-between">
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span>Category: {recommendation.category}</span>
                        <span>Status: {recommendation.status}</span>
                        <span>Created: {new Date(recommendation.created_at).toLocaleDateString()}</span>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRecommendationAction(recommendation.id, 'applied');
                          }}
                          className="text-success-600 hover:text-success-900"
                        >
                          <CheckCircle className="w-4 h-4 mr-1" />
                          Apply
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRecommendationAction(recommendation.id, 'dismissed');
                          }}
                          className="text-danger-600 hover:text-danger-900"
                        >
                          <XCircle className="w-4 h-4 mr-1" />
                          Dismiss
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default SmartRecommendations;
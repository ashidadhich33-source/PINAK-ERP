import React, { useState, useEffect, useRef } from 'react';
import { useDebounce } from '../../hooks/usePerformance';
import { searchService } from '../../services/searchService';
import { useApp } from '../../contexts/AppContext';
import Button from '../common/Button';
import Input from '../common/Input';
import Alert from '../common/Alert';
import LoadingSpinner from '../common/LoadingSpinner';
import { 
  Search, 
  Filter, 
  X, 
  Clock, 
  Star, 
  TrendingUp,
  Users,
  Package,
  ShoppingCart,
  Building2,
  FileText,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

const AdvancedSearch = ({ onResultSelect, className = '' }) => {
  const { addNotification } = useApp();
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [searchHistory, setSearchHistory] = useState([]);
  const [savedSearches, setSavedSearches] = useState([]);
  const [showFilters, setShowFilters] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeModule, setActiveModule] = useState('all');
  const [filters, setFilters] = useState({
    dateRange: 'all',
    status: 'all',
    category: 'all',
    sortBy: 'relevance',
    sortOrder: 'desc',
  });

  const debouncedQuery = useDebounce(query, 300);
  const searchRef = useRef(null);

  // Modules for search
  const modules = [
    { id: 'all', name: 'All', icon: Search },
    { id: 'companies', name: 'Companies', icon: Building2 },
    { id: 'customers', name: 'Customers', icon: Users },
    { id: 'inventory', name: 'Inventory', icon: Package },
    { id: 'sales', name: 'Sales', icon: ShoppingCart },
    { id: 'reports', name: 'Reports', icon: FileText },
  ];

  // Fetch suggestions
  useEffect(() => {
    if (debouncedQuery.length >= 2) {
      fetchSuggestions(debouncedQuery);
    } else {
      setSuggestions([]);
    }
  }, [debouncedQuery]);

  // Fetch search history and saved searches
  useEffect(() => {
    fetchSearchHistory();
    fetchSavedSearches();
  }, []);

  const fetchSuggestions = async (searchQuery) => {
    try {
      setLoading(true);
      const results = await searchService.getSuggestions(searchQuery, activeModule);
      setSuggestions(results);
    } catch (err) {
      console.error('Error fetching suggestions:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSearchHistory = async () => {
    try {
      const history = await searchService.getSearchHistory();
      setSearchHistory(history);
    } catch (err) {
      console.error('Error fetching search history:', err);
    }
  };

  const fetchSavedSearches = async () => {
    try {
      const saved = await searchService.getSavedSearches();
      setSavedSearches(saved);
    } catch (err) {
      console.error('Error fetching saved searches:', err);
    }
  };

  const handleSearch = async (searchQuery = query) => {
    if (!searchQuery.trim()) return;

    try {
      setLoading(true);
      setError(null);

      let results;
      if (activeModule === 'all') {
        results = await searchService.globalSearch(searchQuery, filters);
      } else {
        results = await searchService.searchModule(activeModule, searchQuery, filters);
      }

      onResultSelect?.(results);
    } catch (err) {
      setError(err.message);
      addNotification({
        type: 'danger',
        title: 'Search Error',
        message: err.message,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion.text);
    handleSearch(suggestion.text);
  };

  const handleHistoryClick = (historyItem) => {
    setQuery(historyItem.query);
    handleSearch(historyItem.query);
  };

  const handleSavedSearchClick = (savedSearch) => {
    setQuery(savedSearch.query);
    setFilters(savedSearch.filters);
    handleSearch(savedSearch.query);
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleSaveSearch = async () => {
    if (!query.trim()) return;

    try {
      await searchService.saveSearch({
        query,
        filters,
        module: activeModule,
      });
      
      addNotification({
        type: 'success',
        title: 'Search Saved',
        message: 'Search has been saved successfully',
      });
      
      fetchSavedSearches();
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  const handleClearSearch = () => {
    setQuery('');
    setSuggestions([]);
    setError(null);
  };

  return (
    <div className={`relative ${className}`}>
      {/* Search Input */}
      <div className="relative">
        <Input
          ref={searchRef}
          placeholder="Search across all modules..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="pl-10 pr-20"
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        
        <div className="absolute inset-y-0 right-0 flex items-center space-x-1 pr-3">
          {query && (
            <button
              onClick={handleClearSearch}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </button>
          )}
          
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`p-1 rounded ${
              showFilters ? 'bg-primary-100 text-primary-600' : 'text-gray-400 hover:text-gray-600'
            }`}
          >
            <Filter className="h-4 w-4" />
          </button>
          
          <Button
            size="sm"
            onClick={() => handleSearch()}
            loading={loading}
            disabled={!query.trim()}
          >
            Search
          </Button>
        </div>
      </div>

      {/* Module Tabs */}
      <div className="flex space-x-1 mt-2">
        {modules.map((module) => {
          const Icon = module.icon;
          return (
            <button
              key={module.id}
              onClick={() => setActiveModule(module.id)}
              className={`flex items-center space-x-1 px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                activeModule === module.id
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{module.name}</span>
            </button>
          );
        })}
      </div>

      {/* Advanced Filters */}
      {showFilters && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="form-label">Date Range</label>
              <select
                value={filters.dateRange}
                onChange={(e) => handleFilterChange('dateRange', e.target.value)}
                className="form-input"
              >
                <option value="all">All Time</option>
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="year">This Year</option>
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
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="pending">Pending</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            
            <div>
              <label className="form-label">Sort By</label>
              <select
                value={filters.sortBy}
                onChange={(e) => handleFilterChange('sortBy', e.target.value)}
                className="form-input"
              >
                <option value="relevance">Relevance</option>
                <option value="date">Date</option>
                <option value="name">Name</option>
                <option value="amount">Amount</option>
              </select>
            </div>
            
            <div>
              <label className="form-label">Sort Order</label>
              <select
                value={filters.sortOrder}
                onChange={(e) => handleFilterChange('sortOrder', e.target.value)}
                className="form-input"
              >
                <option value="desc">Descending</option>
                <option value="asc">Ascending</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Search Results Dropdown */}
      {(suggestions.length > 0 || searchHistory.length > 0 || savedSearches.length > 0) && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-96 overflow-y-auto">
          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div className="p-2">
              <div className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-500">
                <TrendingUp className="w-4 h-4" />
                <span>Suggestions</span>
              </div>
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded"
                >
                  {suggestion.text}
                </button>
              ))}
            </div>
          )}

          {/* Search History */}
          {searchHistory.length > 0 && (
            <div className="p-2 border-t border-gray-200">
              <div className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-500">
                <Clock className="w-4 h-4" />
                <span>Recent Searches</span>
              </div>
              {searchHistory.slice(0, 5).map((historyItem, index) => (
                <button
                  key={index}
                  onClick={() => handleHistoryClick(historyItem)}
                  className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded"
                >
                  {historyItem.query}
                </button>
              ))}
            </div>
          )}

          {/* Saved Searches */}
          {savedSearches.length > 0 && (
            <div className="p-2 border-t border-gray-200">
              <div className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-500">
                <Star className="w-4 h-4" />
                <span>Saved Searches</span>
              </div>
              {savedSearches.slice(0, 5).map((savedSearch, index) => (
                <button
                  key={index}
                  onClick={() => handleSavedSearchClick(savedSearch)}
                  className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded"
                >
                  {savedSearch.query}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <div className="mt-2">
          <Alert type="danger" title="Search Error">
            {error}
          </Alert>
        </div>
      )}

      {/* Loading Indicator */}
      {loading && (
        <div className="mt-2">
          <LoadingSpinner size="sm" text="Searching..." />
        </div>
      )}
    </div>
  );
};

export default AdvancedSearch;
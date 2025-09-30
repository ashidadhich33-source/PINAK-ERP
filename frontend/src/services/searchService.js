import { apiService } from './apiService';

export const searchService = {
  // Global search across all modules
  globalSearch: async (query, options = {}) => {
    try {
      const results = await apiService.get('/api/search/global', {
        q: query,
        ...options,
      });
      return results;
    } catch (error) {
      throw new Error(error.message || 'Failed to perform global search');
    }
  },

  // Search within specific modules
  searchModule: async (module, query, options = {}) => {
    try {
      const results = await apiService.get(`/api/search/${module}`, {
        q: query,
        ...options,
      });
      return results;
    } catch (error) {
      throw new Error(error.message || `Failed to search ${module}`);
    }
  },

  // Advanced search with filters
  advancedSearch: async (filters, options = {}) => {
    try {
      const results = await apiService.post('/api/search/advanced', {
        filters,
        ...options,
      });
      return results;
    } catch (error) {
      throw new Error(error.message || 'Failed to perform advanced search');
    }
  },

  // Search suggestions
  getSuggestions: async (query, module = null) => {
    try {
      const results = await apiService.get('/api/search/suggestions', {
        q: query,
        module,
      });
      return results;
    } catch (error) {
      throw new Error(error.message || 'Failed to get search suggestions');
    }
  },

  // Search history
  getSearchHistory: async () => {
    try {
      const history = await apiService.get('/api/search/history');
      return history;
    } catch (error) {
      throw new Error(error.message || 'Failed to get search history');
    }
  },

  // Save search
  saveSearch: async (searchData) => {
    try {
      const saved = await apiService.post('/api/search/saved', searchData);
      return saved;
    } catch (error) {
      throw new Error(error.message || 'Failed to save search');
    }
  },

  // Get saved searches
  getSavedSearches: async () => {
    try {
      const searches = await apiService.get('/api/search/saved');
      return searches;
    } catch (error) {
      throw new Error(error.message || 'Failed to get saved searches');
    }
  },

  // Delete saved search
  deleteSavedSearch: async (searchId) => {
    try {
      await apiService.delete(`/api/search/saved/${searchId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete saved search');
    }
  },

  // Search analytics
  getSearchAnalytics: async (options = {}) => {
    try {
      const analytics = await apiService.get('/api/search/analytics', options);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to get search analytics');
    }
  },

  // Search within specific fields
  fieldSearch: async (module, field, query, options = {}) => {
    try {
      const results = await apiService.get(`/api/search/${module}/field`, {
        field,
        q: query,
        ...options,
      });
      return results;
    } catch (error) {
      throw new Error(error.message || `Failed to search ${field} in ${module}`);
    }
  },

  // Fuzzy search
  fuzzySearch: async (query, options = {}) => {
    try {
      const results = await apiService.get('/api/search/fuzzy', {
        q: query,
        ...options,
      });
      return results;
    } catch (error) {
      throw new Error(error.message || 'Failed to perform fuzzy search');
    }
  },

  // Search with filters
  searchWithFilters: async (query, filters, options = {}) => {
    try {
      const results = await apiService.post('/api/search/filters', {
        query,
        filters,
        ...options,
      });
      return results;
    } catch (error) {
      throw new Error(error.message || 'Failed to search with filters');
    }
  },

  // Search within date range
  searchByDateRange: async (query, startDate, endDate, options = {}) => {
    try {
      const results = await apiService.get('/api/search/date-range', {
        q: query,
        start_date: startDate,
        end_date: endDate,
        ...options,
      });
      return results;
    } catch (error) {
      throw new Error(error.message || 'Failed to search by date range');
    }
  },

  // Search with sorting
  searchWithSort: async (query, sortBy, sortOrder = 'asc', options = {}) => {
    try {
      const results = await apiService.get('/api/search/sort', {
        q: query,
        sort_by: sortBy,
        sort_order: sortOrder,
        ...options,
      });
      return results;
    } catch (error) {
      throw new Error(error.message || 'Failed to search with sorting');
    }
  },

  // Search with pagination
  searchWithPagination: async (query, page = 1, limit = 20, options = {}) => {
    try {
      const results = await apiService.get('/api/search/paginated', {
        q: query,
        page,
        limit,
        ...options,
      });
      return results;
    } catch (error) {
      throw new Error(error.message || 'Failed to search with pagination');
    }
  },

  // Search with highlights
  searchWithHighlights: async (query, options = {}) => {
    try {
      const results = await apiService.get('/api/search/highlights', {
        q: query,
        ...options,
      });
      return results;
    } catch (error) {
      throw new Error(error.message || 'Failed to search with highlights');
    }
  },

  // Search with facets
  searchWithFacets: async (query, facets, options = {}) => {
    try {
      const results = await apiService.post('/api/search/facets', {
        query,
        facets,
        ...options,
      });
      return results;
    } catch (error) {
      throw new Error(error.message || 'Failed to search with facets');
    }
  },

  // Search with autocomplete
  autocomplete: async (query, options = {}) => {
    try {
      const results = await apiService.get('/api/search/autocomplete', {
        q: query,
        ...options,
      });
      return results;
    } catch (error) {
      throw new Error(error.message || 'Failed to get autocomplete suggestions');
    }
  },

  // Search with spell check
  spellCheck: async (query) => {
    try {
      const results = await apiService.get('/api/search/spell-check', {
        q: query,
      });
      return results;
    } catch (error) {
      throw new Error(error.message || 'Failed to check spelling');
    }
  },

  // Search with synonyms
  searchWithSynonyms: async (query, options = {}) => {
    try {
      const results = await apiService.get('/api/search/synonyms', {
        q: query,
        ...options,
      });
      return results;
    } catch (error) {
      throw new Error(error.message || 'Failed to search with synonyms');
    }
  },

  // Search with wildcards
  searchWithWildcards: async (query, options = {}) => {
    try {
      const results = await apiService.get('/api/search/wildcards', {
        q: query,
        ...options,
      });
      return results;
    } catch (error) {
      throw new Error(error.message || 'Failed to search with wildcards');
    }
  },

  // Search with regex
  searchWithRegex: async (pattern, options = {}) => {
    try {
      const results = await apiService.get('/api/search/regex', {
        pattern,
        ...options,
      });
      return results;
    } catch (error) {
      throw new Error(error.message || 'Failed to search with regex');
    }
  },

  // Search with proximity
  searchWithProximity: async (query, proximity = 5, options = {}) => {
    try {
      const results = await apiService.get('/api/search/proximity', {
        q: query,
        proximity,
        ...options,
      });
      return results;
    } catch (error) {
      throw new Error(error.message || 'Failed to search with proximity');
    }
  },

  // Search with boosting
  searchWithBoosting: async (query, boostFields, options = {}) => {
    try {
      const results = await apiService.post('/api/search/boosting', {
        query,
        boost_fields: boostFields,
        ...options,
      });
      return results;
    } catch (error) {
      throw new Error(error.message || 'Failed to search with boosting');
    }
  },
};
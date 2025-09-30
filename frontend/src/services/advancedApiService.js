import { apiService } from './apiService';

class AdvancedApiService {
  constructor() {
    this.cache = new Map();
    this.requestQueue = [];
    this.batchQueue = new Map();
    this.retryQueue = [];
    this.rateLimits = new Map();
    this.metrics = {
      requests: 0,
      cacheHits: 0,
      errors: 0,
      avgResponseTime: 0
    };
    
    this.setupInterceptors();
    this.startBatchProcessor();
    this.startRetryProcessor();
  }

  setupInterceptors() {
    // Request interceptor for caching and batching
    apiService.interceptors.request.use(
      (config) => {
        this.metrics.requests++;
        
        // Check cache first
        if (config.method === 'get' && this.cache.has(config.url)) {
          const cached = this.cache.get(config.url);
          if (Date.now() - cached.timestamp < 300000) { // 5 minutes
            this.metrics.cacheHits++;
            return Promise.resolve({ data: cached.data, fromCache: true });
          }
        }

        // Add to batch queue if batchable
        if (this.isBatchable(config)) {
          return this.addToBatch(config);
        }

        // Add rate limiting
        if (this.isRateLimited(config.url)) {
          return this.addToRetryQueue(config);
        }

        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for caching and metrics
    apiService.interceptors.response.use(
      (response) => {
        // Cache GET requests
        if (response.config.method === 'get') {
          this.cache.set(response.config.url, {
            data: response.data,
            timestamp: Date.now()
          });
        }

        // Update metrics
        this.updateMetrics(response);

        return response;
      },
      (error) => {
        this.metrics.errors++;
        
        // Retry on network errors
        if (this.shouldRetry(error)) {
          this.addToRetryQueue(error.config);
        }

        return Promise.reject(error);
      }
    );
  }

  // Cache management
  setCache(key, data, ttl = 300000) {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }

  getCache(key) {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < cached.ttl) {
      this.metrics.cacheHits++;
      return cached.data;
    }
    return null;
  }

  clearCache(pattern = null) {
    if (pattern) {
      for (const [key] of this.cache) {
        if (key.includes(pattern)) {
          this.cache.delete(key);
        }
      }
    } else {
      this.cache.clear();
    }
  }

  // Batch processing
  isBatchable(config) {
    return config.method === 'get' && 
           config.url.includes('/batch') && 
           !config.headers?.['X-No-Batch'];
  }

  addToBatch(config) {
    const batchKey = this.getBatchKey(config);
    
    if (!this.batchQueue.has(batchKey)) {
      this.batchQueue.set(batchKey, []);
    }
    
    this.batchQueue.get(batchKey).push(config);
    
    // Return a promise that will be resolved when batch is processed
    return new Promise((resolve, reject) => {
      config._batchResolve = resolve;
      config._batchReject = reject;
    });
  }

  getBatchKey(config) {
    const baseUrl = config.url.split('?')[0];
    return `${config.method}:${baseUrl}`;
  }

  startBatchProcessor() {
    setInterval(() => {
      this.processBatchQueue();
    }, 100); // Process every 100ms
  }

  async processBatchQueue() {
    for (const [batchKey, requests] of this.batchQueue) {
      if (requests.length > 0) {
        await this.processBatch(batchKey, requests);
        this.batchQueue.set(batchKey, []);
      }
    }
  }

  async processBatch(batchKey, requests) {
    try {
      const batchData = requests.map(req => ({
        url: req.url,
        method: req.method,
        data: req.data
      }));

      const response = await apiService.post('/api/batch', { requests: batchData });
      
      // Resolve individual requests
      requests.forEach((req, index) => {
        if (req._batchResolve) {
          req._batchResolve({ data: response.data[index] });
        }
      });
    } catch (error) {
      // Reject all requests in batch
      requests.forEach(req => {
        if (req._batchReject) {
          req._batchReject(error);
        }
      });
    }
  }

  // Retry mechanism
  shouldRetry(error) {
    return error.code === 'NETWORK_ERROR' || 
           error.response?.status >= 500 ||
           error.response?.status === 429;
  }

  addToRetryQueue(config) {
    this.retryQueue.push({
      config,
      attempts: 0,
      maxAttempts: 3,
      delay: 1000
    });
  }

  startRetryProcessor() {
    setInterval(() => {
      this.processRetryQueue();
    }, 5000); // Process every 5 seconds
  }

  async processRetryQueue() {
    const toRetry = this.retryQueue.splice(0, 10); // Process 10 at a time
    
    for (const item of toRetry) {
      if (item.attempts < item.maxAttempts) {
        try {
          await this.delay(item.delay * Math.pow(2, item.attempts)); // Exponential backoff
          await apiService(item.config);
        } catch (error) {
          item.attempts++;
          if (item.attempts < item.maxAttempts) {
            this.retryQueue.push(item);
          }
        }
      }
    }
  }

  // Rate limiting
  isRateLimited(url) {
    const now = Date.now();
    const key = this.getRateLimitKey(url);
    
    if (!this.rateLimits.has(key)) {
      this.rateLimits.set(key, { count: 0, resetTime: now + 60000 });
    }
    
    const limit = this.rateLimits.get(key);
    
    if (now > limit.resetTime) {
      limit.count = 0;
      limit.resetTime = now + 60000;
    }
    
    if (limit.count >= 100) { // 100 requests per minute
      return true;
    }
    
    limit.count++;
    return false;
  }

  getRateLimitKey(url) {
    const baseUrl = url.split('?')[0];
    return baseUrl;
  }

  // Metrics and monitoring
  updateMetrics(response) {
    const responseTime = Date.now() - response.config.metadata?.startTime;
    this.metrics.avgResponseTime = 
      (this.metrics.avgResponseTime + responseTime) / 2;
  }

  getMetrics() {
    return {
      ...this.metrics,
      cacheSize: this.cache.size,
      queueSize: this.retryQueue.length,
      batchQueueSize: Array.from(this.batchQueue.values())
        .reduce((total, queue) => total + queue.length, 0)
    };
  }

  // Advanced API methods
  async batchRequest(requests) {
    try {
      const response = await apiService.post('/api/batch', { requests });
      return response.data;
    } catch (error) {
      throw new Error(`Batch request failed: ${error.message}`);
    }
  }

  async parallelRequest(urls, options = {}) {
    const { maxConcurrency = 5, timeout = 30000 } = options;
    
    const chunks = this.chunkArray(urls, maxConcurrency);
    const results = [];
    
    for (const chunk of chunks) {
      const promises = chunk.map(url => 
        apiService.get(url).catch(error => ({ error, url }))
      );
      
      const chunkResults = await Promise.allSettled(promises);
      results.push(...chunkResults);
    }
    
    return results;
  }

  async retryRequest(config, options = {}) {
    const { maxAttempts = 3, delay = 1000, backoff = 2 } = options;
    
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        return await apiService(config);
      } catch (error) {
        if (attempt === maxAttempts) {
          throw error;
        }
        
        await this.delay(delay * Math.pow(backoff, attempt - 1));
      }
    }
  }

  async cacheFirst(url, options = {}) {
    const { ttl = 300000, fallback = true } = options;
    
    // Try cache first
    const cached = this.getCache(url);
    if (cached) {
      return cached;
    }
    
    // Fallback to API
    if (fallback) {
      try {
        const response = await apiService.get(url);
        this.setCache(url, response.data, ttl);
        return response.data;
      } catch (error) {
        throw error;
      }
    }
    
    return null;
  }

  async networkFirst(url, options = {}) {
    const { ttl = 300000, fallback = true } = options;
    
    try {
      const response = await apiService.get(url);
      this.setCache(url, response.data, ttl);
      return response.data;
    } catch (error) {
      if (fallback) {
        const cached = this.getCache(url);
        if (cached) {
          return cached;
        }
      }
      throw error;
    }
  }

  // Utility methods
  chunkArray(array, size) {
    const chunks = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Health check
  async healthCheck() {
    try {
      const start = Date.now();
      await apiService.get('/api/health');
      const responseTime = Date.now() - start;
      
      return {
        status: 'healthy',
        responseTime,
        metrics: this.getMetrics()
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        error: error.message,
        metrics: this.getMetrics()
      };
    }
  }

  // Cleanup
  cleanup() {
    this.cache.clear();
    this.requestQueue = [];
    this.batchQueue.clear();
    this.retryQueue = [];
    this.rateLimits.clear();
  }
}

// Create singleton instance
const advancedApiService = new AdvancedApiService();

export default advancedApiService;
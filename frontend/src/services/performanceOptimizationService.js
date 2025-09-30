class PerformanceOptimizationService {
  constructor() {
    this.metrics = {
      pageLoadTime: 0,
      firstContentfulPaint: 0,
      largestContentfulPaint: 0,
      cumulativeLayoutShift: 0,
      firstInputDelay: 0,
      timeToInteractive: 0,
      bundleSize: 0,
      memoryUsage: 0,
      cpuUsage: 0,
      networkLatency: 0
    };
    
    this.optimizations = new Map();
    this.performanceObservers = new Map();
    this.setupPerformanceMonitoring();
    this.initializeOptimizations();
  }

  setupPerformanceMonitoring() {
    // Monitor Core Web Vitals
    this.monitorCoreWebVitals();
    
    // Monitor resource loading
    this.monitorResourceLoading();
    
    // Monitor memory usage
    this.monitorMemoryUsage();
    
    // Monitor network performance
    this.monitorNetworkPerformance();
    
    // Monitor user interactions
    this.monitorUserInteractions();
  }

  monitorCoreWebVitals() {
    // First Contentful Paint (FCP)
    if ('PerformanceObserver' in window) {
      try {
        const fcpObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.name === 'first-contentful-paint') {
              this.metrics.firstContentfulPaint = entry.startTime;
            }
          }
        });
        fcpObserver.observe({ entryTypes: ['paint'] });
        this.performanceObservers.set('fcp', fcpObserver);
      } catch (error) {
        console.warn('FCP monitoring not supported:', error);
      }
    }

    // Largest Contentful Paint (LCP)
    if ('PerformanceObserver' in window) {
      try {
        const lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          this.metrics.largestContentfulPaint = lastEntry.startTime;
        });
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
        this.performanceObservers.set('lcp', lcpObserver);
      } catch (error) {
        console.warn('LCP monitoring not supported:', error);
      }
    }

    // Cumulative Layout Shift (CLS)
    if ('PerformanceObserver' in window) {
      try {
        let clsValue = 0;
        const clsObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (!entry.hadRecentInput) {
              clsValue += entry.value;
            }
          }
          this.metrics.cumulativeLayoutShift = clsValue;
        });
        clsObserver.observe({ entryTypes: ['layout-shift'] });
        this.performanceObservers.set('cls', clsObserver);
      } catch (error) {
        console.warn('CLS monitoring not supported:', error);
      }
    }

    // First Input Delay (FID)
    if ('PerformanceObserver' in window) {
      try {
        const fidObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            this.metrics.firstInputDelay = entry.processingStart - entry.startTime;
          }
        });
        fidObserver.observe({ entryTypes: ['first-input'] });
        this.performanceObservers.set('fid', fidObserver);
      } catch (error) {
        console.warn('FID monitoring not supported:', error);
      }
    }
  }

  monitorResourceLoading() {
    if ('PerformanceObserver' in window) {
      try {
        const resourceObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            this.analyzeResource(entry);
          }
        });
        resourceObserver.observe({ entryTypes: ['resource'] });
        this.performanceObservers.set('resources', resourceObserver);
      } catch (error) {
        console.warn('Resource monitoring not supported:', error);
      }
    }
  }

  analyzeResource(entry) {
    const resource = {
      name: entry.name,
      duration: entry.duration,
      size: entry.transferSize || 0,
      type: this.getResourceType(entry.name),
      priority: this.getResourcePriority(entry)
    };

    // Identify slow resources
    if (resource.duration > 1000) {
      this.optimizations.set(`slow_resource_${Date.now()}`, {
        type: 'slow_resource',
        resource: resource.name,
        duration: resource.duration,
        recommendation: 'Consider optimizing or lazy loading this resource'
      });
    }

    // Identify large resources
    if (resource.size > 100000) { // 100KB
      this.optimizations.set(`large_resource_${Date.now()}`, {
        type: 'large_resource',
        resource: resource.name,
        size: resource.size,
        recommendation: 'Consider compressing or splitting this resource'
      });
    }
  }

  getResourceType(url) {
    if (url.includes('.js')) return 'script';
    if (url.includes('.css')) return 'stylesheet';
    if (url.includes('.png') || url.includes('.jpg') || url.includes('.jpeg') || url.includes('.gif') || url.includes('.webp')) return 'image';
    if (url.includes('.woff') || url.includes('.woff2') || url.includes('.ttf')) return 'font';
    return 'other';
  }

  getResourcePriority(entry) {
    // This would be determined by the browser's priority hints
    return 'normal';
  }

  monitorMemoryUsage() {
    if ('memory' in performance) {
      setInterval(() => {
        const memory = performance.memory;
        this.metrics.memoryUsage = (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100;
        
        // Check for memory leaks
        if (this.metrics.memoryUsage > 80) {
          this.optimizations.set(`memory_usage_${Date.now()}`, {
            type: 'high_memory_usage',
            usage: this.metrics.memoryUsage,
            recommendation: 'Consider optimizing memory usage or clearing unused objects'
          });
        }
      }, 30000); // Check every 30 seconds
    }
  }

  monitorNetworkPerformance() {
    if ('connection' in navigator) {
      const connection = navigator.connection;
      this.metrics.networkLatency = connection.rtt || 0;
      
      // Monitor connection changes
      connection.addEventListener('change', () => {
        this.optimizeForConnection(connection);
      });
    }
  }

  optimizeForConnection(connection) {
    const optimizations = [];
    
    if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
      optimizations.push({
        type: 'slow_connection',
        recommendation: 'Enable aggressive caching and reduce resource loading'
      });
    }
    
    if (connection.saveData) {
      optimizations.push({
        type: 'data_saver',
        recommendation: 'Enable data saver mode and reduce image quality'
      });
    }
    
    optimizations.forEach(opt => {
      this.optimizations.set(`${opt.type}_${Date.now()}`, opt);
    });
  }

  monitorUserInteractions() {
    // Monitor click events for performance
    document.addEventListener('click', (event) => {
      const start = performance.now();
      
      // Measure interaction response time
      requestAnimationFrame(() => {
        const end = performance.now();
        const responseTime = end - start;
        
        if (responseTime > 100) {
          this.optimizations.set(`slow_interaction_${Date.now()}`, {
            type: 'slow_interaction',
            responseTime,
            recommendation: 'Optimize event handling and reduce DOM manipulation'
          });
        }
      });
    });
  }

  initializeOptimizations() {
    // Bundle optimization
    this.optimizations.set('bundle_optimization', {
      type: 'bundle',
      recommendations: [
        'Enable code splitting',
        'Use dynamic imports',
        'Optimize bundle size',
        'Remove unused code'
      ]
    });

    // Image optimization
    this.optimizations.set('image_optimization', {
      type: 'images',
      recommendations: [
        'Use WebP format',
        'Implement lazy loading',
        'Optimize image sizes',
        'Use responsive images'
      ]
    });

    // Caching optimization
    this.optimizations.set('caching_optimization', {
      type: 'caching',
      recommendations: [
        'Implement service worker caching',
        'Use HTTP caching headers',
        'Cache API responses',
        'Implement offline caching'
      ]
    });

    // Network optimization
    this.optimizations.set('network_optimization', {
      type: 'network',
      recommendations: [
        'Enable HTTP/2',
        'Use CDN for static assets',
        'Implement request batching',
        'Optimize API calls'
      ]
    });
  }

  // Performance optimization methods
  optimizeBundleSize() {
    const optimizations = [
      'Enable tree shaking',
      'Use dynamic imports for code splitting',
      'Minify JavaScript and CSS',
      'Remove unused dependencies',
      'Optimize images and assets',
      'Use compression (gzip/brotli)'
    ];

    return {
      type: 'bundle_optimization',
      optimizations,
      estimatedSavings: '30-50% bundle size reduction'
    };
  }

  optimizeImages() {
    const optimizations = [
      'Convert to WebP format',
      'Implement lazy loading',
      'Use responsive images',
      'Optimize image dimensions',
      'Use appropriate compression',
      'Implement progressive loading'
    ];

    return {
      type: 'image_optimization',
      optimizations,
      estimatedSavings: '40-60% image size reduction'
    };
  }

  optimizeCaching() {
    const optimizations = [
      'Implement service worker caching',
      'Use HTTP caching headers',
      'Cache API responses',
      'Implement offline caching',
      'Use browser caching',
      'Optimize cache strategies'
    ];

    return {
      type: 'caching_optimization',
      optimizations,
      estimatedSavings: '50-70% faster repeat visits'
    };
  }

  optimizeNetwork() {
    const optimizations = [
      'Enable HTTP/2',
      'Use CDN for static assets',
      'Implement request batching',
      'Optimize API calls',
      'Use compression',
      'Implement connection pooling'
    ];

    return {
      type: 'network_optimization',
      optimizations,
      estimatedSavings: '20-40% faster loading'
    };
  }

  optimizeRendering() {
    const optimizations = [
      'Use CSS containment',
      'Optimize DOM manipulation',
      'Use virtual scrolling',
      'Implement lazy loading',
      'Optimize animations',
      'Use requestAnimationFrame'
    ];

    return {
      type: 'rendering_optimization',
      optimizations,
      estimatedSavings: '30-50% faster rendering'
    };
  }

  // Performance analysis
  analyzePerformance() {
    const analysis = {
      timestamp: new Date().toISOString(),
      metrics: this.metrics,
      optimizations: Array.from(this.optimizations.values()),
      recommendations: this.generateRecommendations(),
      score: this.calculatePerformanceScore()
    };

    return analysis;
  }

  generateRecommendations() {
    const recommendations = [];
    
    // Core Web Vitals recommendations
    if (this.metrics.firstContentfulPaint > 1800) {
      recommendations.push({
        type: 'critical',
        metric: 'FCP',
        value: this.metrics.firstContentfulPaint,
        recommendation: 'Optimize critical rendering path and reduce server response time'
      });
    }

    if (this.metrics.largestContentfulPaint > 2500) {
      recommendations.push({
        type: 'critical',
        metric: 'LCP',
        value: this.metrics.largestContentfulPaint,
        recommendation: 'Optimize largest contentful paint element and improve server response time'
      });
    }

    if (this.metrics.cumulativeLayoutShift > 0.1) {
      recommendations.push({
        type: 'critical',
        metric: 'CLS',
        value: this.metrics.cumulativeLayoutShift,
        recommendation: 'Fix layout shifts by reserving space for dynamic content'
      });
    }

    if (this.metrics.firstInputDelay > 100) {
      recommendations.push({
        type: 'critical',
        metric: 'FID',
        value: this.metrics.firstInputDelay,
        recommendation: 'Reduce JavaScript execution time and optimize event handlers'
      });
    }

    // Memory usage recommendations
    if (this.metrics.memoryUsage > 80) {
      recommendations.push({
        type: 'warning',
        metric: 'Memory Usage',
        value: this.metrics.memoryUsage,
        recommendation: 'Optimize memory usage and clear unused objects'
      });
    }

    return recommendations;
  }

  calculatePerformanceScore() {
    let score = 100;
    
    // FCP scoring
    if (this.metrics.firstContentfulPaint > 1800) score -= 20;
    else if (this.metrics.firstContentfulPaint > 1000) score -= 10;
    
    // LCP scoring
    if (this.metrics.largestContentfulPaint > 2500) score -= 20;
    else if (this.metrics.largestContentfulPaint > 1500) score -= 10;
    
    // CLS scoring
    if (this.metrics.cumulativeLayoutShift > 0.1) score -= 20;
    else if (this.metrics.cumulativeLayoutShift > 0.05) score -= 10;
    
    // FID scoring
    if (this.metrics.firstInputDelay > 100) score -= 20;
    else if (this.metrics.firstInputDelay > 50) score -= 10;
    
    // Memory usage scoring
    if (this.metrics.memoryUsage > 80) score -= 10;
    else if (this.metrics.memoryUsage > 60) score -= 5;
    
    return Math.max(0, score);
  }

  // Performance monitoring
  startPerformanceMonitoring() {
    // Start monitoring all performance metrics
    this.monitorCoreWebVitals();
    this.monitorResourceLoading();
    this.monitorMemoryUsage();
    this.monitorNetworkPerformance();
    this.monitorUserInteractions();
  }

  stopPerformanceMonitoring() {
    // Stop all performance observers
    for (const [name, observer] of this.performanceObservers) {
      observer.disconnect();
    }
    this.performanceObservers.clear();
  }

  // Performance reporting
  generatePerformanceReport() {
    const report = {
      timestamp: new Date().toISOString(),
      metrics: this.metrics,
      optimizations: Array.from(this.optimizations.values()),
      recommendations: this.generateRecommendations(),
      score: this.calculatePerformanceScore(),
      summary: this.generatePerformanceSummary()
    };

    return report;
  }

  generatePerformanceSummary() {
    const score = this.calculatePerformanceScore();
    let status = 'excellent';
    
    if (score < 50) status = 'poor';
    else if (score < 70) status = 'needs improvement';
    else if (score < 90) status = 'good';
    
    return {
      status,
      score,
      criticalIssues: this.generateRecommendations().filter(r => r.type === 'critical').length,
      warnings: this.generateRecommendations().filter(r => r.type === 'warning').length,
      optimizations: this.optimizations.size
    };
  }

  // Cleanup
  cleanup() {
    this.stopPerformanceMonitoring();
    this.optimizations.clear();
  }
}

// Create singleton instance
const performanceOptimizationService = new PerformanceOptimizationService();

export default performanceOptimizationService;
class ApiSecurityService {
  constructor() {
    this.threats = new Map();
    this.rateLimits = new Map();
    this.blockedIPs = new Set();
    this.suspiciousActivities = new Map();
    this.securityMetrics = {
      totalRequests: 0,
      blockedRequests: 0,
      suspiciousRequests: 0,
      rateLimitHits: 0,
      threatsDetected: 0
    };
    
    this.setupSecurityMonitoring();
  }

  setupSecurityMonitoring() {
    // Monitor for suspicious patterns
    this.monitorSuspiciousActivity();
    
    // Rate limiting
    this.setupRateLimiting();
    
    // Threat detection
    this.setupThreatDetection();
    
    // IP blocking
    this.setupIPBlocking();
  }

  // Rate limiting
  setupRateLimiting() {
    this.rateLimits = new Map();
  }

  isRateLimited(identifier, limit = 100, window = 60000) {
    const now = Date.now();
    const key = `rate_limit_${identifier}`;
    
    if (!this.rateLimits.has(key)) {
      this.rateLimits.set(key, { count: 0, resetTime: now + window });
    }
    
    const rateLimit = this.rateLimits.get(key);
    
    if (now > rateLimit.resetTime) {
      rateLimit.count = 0;
      rateLimit.resetTime = now + window;
    }
    
    if (rateLimit.count >= limit) {
      this.securityMetrics.rateLimitHits++;
      return true;
    }
    
    rateLimit.count++;
    return false;
  }

  // Threat detection
  setupThreatDetection() {
    this.threatPatterns = [
      // SQL injection patterns
      /('|(\\')|(;)|(\\;)|(--)|(\\/\\*)|(\\*\\/))/i,
      /(union|select|insert|update|delete|drop|create|alter)/i,
      
      // XSS patterns
      /<script[^>]*>.*?<\\/script>/gi,
      /javascript:/gi,
      /on\\w+\\s*=/gi,
      
      // Path traversal
      /\\.\\.\\//g,
      /\\.\\.\\\\/g,
      
      // Command injection
      /(;|\\|&|`|\\$)/,
      
      // LDAP injection
      /[()=*!]/,
      
      // NoSQL injection
      /\\$where|\\$ne|\\$gt|\\$lt|\\$regex/i
    ];
  }

  detectThreats(request) {
    const threats = [];
    
    // Check URL for threats
    if (request.url) {
      for (const pattern of this.threatPatterns) {
        if (pattern.test(request.url)) {
          threats.push({
            type: 'url_threat',
            pattern: pattern.toString(),
            severity: 'high',
            description: 'Suspicious pattern detected in URL'
          });
        }
      }
    }
    
    // Check headers for threats
    if (request.headers) {
      for (const [key, value] of Object.entries(request.headers)) {
        for (const pattern of this.threatPatterns) {
          if (pattern.test(value)) {
            threats.push({
              type: 'header_threat',
              pattern: pattern.toString(),
              severity: 'medium',
              description: `Suspicious pattern detected in header: ${key}`
            });
          }
        }
      }
    }
    
    // Check body for threats
    if (request.body) {
      const bodyStr = typeof request.body === 'string' ? request.body : JSON.stringify(request.body);
      for (const pattern of this.threatPatterns) {
        if (pattern.test(bodyStr)) {
          threats.push({
            type: 'body_threat',
            pattern: pattern.toString(),
            severity: 'high',
            description: 'Suspicious pattern detected in request body'
          });
        }
      }
    }
    
    return threats;
  }

  // Suspicious activity monitoring
  monitorSuspiciousActivity() {
    this.suspiciousPatterns = [
      // Rapid requests from same IP
      { type: 'rapid_requests', threshold: 100, window: 60000 },
      
      // Unusual request patterns
      { type: 'unusual_patterns', threshold: 50, window: 300000 },
      
      // Failed authentication attempts
      { type: 'failed_auth', threshold: 10, window: 300000 },
      
      // Unusual user agents
      { type: 'suspicious_ua', threshold: 5, window: 3600000 }
    ];
  }

  detectSuspiciousActivity(request) {
    const activities = [];
    const now = Date.now();
    const ip = this.getClientIP(request);
    
    // Check for rapid requests
    if (this.isRapidRequests(ip, now)) {
      activities.push({
        type: 'rapid_requests',
        severity: 'medium',
        description: 'Rapid requests detected from IP',
        ip,
        timestamp: now
      });
    }
    
    // Check for unusual patterns
    if (this.hasUnusualPatterns(request)) {
      activities.push({
        type: 'unusual_patterns',
        severity: 'low',
        description: 'Unusual request patterns detected',
        ip,
        timestamp: now
      });
    }
    
    // Check for suspicious user agent
    if (this.isSuspiciousUserAgent(request)) {
      activities.push({
        type: 'suspicious_ua',
        severity: 'low',
        description: 'Suspicious user agent detected',
        ip,
        timestamp: now
      });
    }
    
    return activities;
  }

  isRapidRequests(ip, now, threshold = 100, window = 60000) {
    const key = `rapid_${ip}`;
    if (!this.suspiciousActivities.has(key)) {
      this.suspiciousActivities.set(key, []);
    }
    
    const activities = this.suspiciousActivities.get(key);
    const recentActivities = activities.filter(time => now - time < window);
    
    if (recentActivities.length >= threshold) {
      return true;
    }
    
    recentActivities.push(now);
    this.suspiciousActivities.set(key, recentActivities);
    return false;
  }

  hasUnusualPatterns(request) {
    // Check for unusual request methods
    const unusualMethods = ['TRACE', 'OPTIONS', 'HEAD'];
    if (unusualMethods.includes(request.method)) {
      return true;
    }
    
    // Check for unusual paths
    const unusualPaths = ['/admin', '/config', '/.env', '/wp-admin'];
    if (unusualPaths.some(path => request.url.includes(path))) {
      return true;
    }
    
    return false;
  }

  isSuspiciousUserAgent(request) {
    const userAgent = request.headers?.['user-agent'] || '';
    const suspiciousPatterns = [
      /bot/i,
      /crawler/i,
      /spider/i,
      /scraper/i,
      /curl/i,
      /wget/i,
      /python/i,
      /java/i
    ];
    
    return suspiciousPatterns.some(pattern => pattern.test(userAgent));
  }

  // IP blocking
  setupIPBlocking() {
    this.blockedIPs = new Set();
  }

  isIPBlocked(ip) {
    return this.blockedIPs.has(ip);
  }

  blockIP(ip, reason = 'Suspicious activity') {
    this.blockedIPs.add(ip);
    this.logSecurityEvent('ip_blocked', { ip, reason });
  }

  unblockIP(ip) {
    this.blockedIPs.delete(ip);
    this.logSecurityEvent('ip_unblocked', { ip });
  }

  // Security event logging
  logSecurityEvent(eventType, data) {
    const event = {
      type: eventType,
      timestamp: new Date().toISOString(),
      data,
      id: this.generateEventId()
    };
    
    // Store event (in real implementation, this would go to a database)
    console.log('Security Event:', event);
    
    // Update metrics
    this.updateSecurityMetrics(eventType);
  }

  updateSecurityMetrics(eventType) {
    switch (eventType) {
      case 'threat_detected':
        this.securityMetrics.threatsDetected++;
        break;
      case 'rate_limit_hit':
        this.securityMetrics.rateLimitHits++;
        break;
      case 'suspicious_activity':
        this.securityMetrics.suspiciousRequests++;
        break;
      case 'ip_blocked':
        this.securityMetrics.blockedRequests++;
        break;
    }
  }

  generateEventId() {
    return `sec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // Security validation
  validateRequest(request) {
    const validation = {
      isValid: true,
      threats: [],
      suspiciousActivities: [],
      rateLimited: false,
      ipBlocked: false,
      recommendations: []
    };
    
    // Check if IP is blocked
    const ip = this.getClientIP(request);
    if (this.isIPBlocked(ip)) {
      validation.isValid = false;
      validation.ipBlocked = true;
      validation.recommendations.push('IP is blocked due to suspicious activity');
      return validation;
    }
    
    // Check rate limiting
    if (this.isRateLimited(ip)) {
      validation.isValid = false;
      validation.rateLimited = true;
      validation.recommendations.push('Rate limit exceeded');
      return validation;
    }
    
    // Detect threats
    const threats = this.detectThreats(request);
    if (threats.length > 0) {
      validation.threats = threats;
      validation.recommendations.push('Threats detected in request');
    }
    
    // Detect suspicious activities
    const activities = this.detectSuspiciousActivity(request);
    if (activities.length > 0) {
      validation.suspiciousActivities = activities;
      validation.recommendations.push('Suspicious activity detected');
    }
    
    // Update metrics
    this.securityMetrics.totalRequests++;
    
    return validation;
  }

  // Security recommendations
  getSecurityRecommendations() {
    const recommendations = [];
    
    if (this.securityMetrics.threatsDetected > 0) {
      recommendations.push({
        type: 'threats',
        severity: 'high',
        message: `${this.securityMetrics.threatsDetected} threats detected`,
        action: 'Review and block suspicious IPs'
      });
    }
    
    if (this.securityMetrics.rateLimitHits > 0) {
      recommendations.push({
        type: 'rate_limiting',
        severity: 'medium',
        message: `${this.securityMetrics.rateLimitHits} rate limit hits`,
        action: 'Consider adjusting rate limits'
      });
    }
    
    if (this.securityMetrics.suspiciousRequests > 0) {
      recommendations.push({
        type: 'suspicious_activity',
        severity: 'medium',
        message: `${this.securityMetrics.suspiciousRequests} suspicious requests`,
        action: 'Monitor and investigate suspicious activities'
      });
    }
    
    return recommendations;
  }

  // Security dashboard data
  getSecurityDashboard() {
    return {
      metrics: this.securityMetrics,
      blockedIPs: Array.from(this.blockedIPs),
      recommendations: this.getSecurityRecommendations(),
      recentEvents: this.getRecentEvents(),
      threatLevel: this.calculateThreatLevel()
    };
  }

  getRecentEvents() {
    // In real implementation, this would fetch from database
    return [
      {
        type: 'threat_detected',
        timestamp: new Date().toISOString(),
        description: 'SQL injection attempt detected',
        severity: 'high'
      },
      {
        type: 'rate_limit_hit',
        timestamp: new Date().toISOString(),
        description: 'Rate limit exceeded for IP 192.168.1.100',
        severity: 'medium'
      }
    ];
  }

  calculateThreatLevel() {
    const { threatsDetected, suspiciousRequests, rateLimitHits } = this.securityMetrics;
    
    if (threatsDetected > 10 || suspiciousRequests > 50) {
      return 'high';
    } else if (threatsDetected > 5 || suspiciousRequests > 20) {
      return 'medium';
    } else if (threatsDetected > 0 || suspiciousRequests > 0) {
      return 'low';
    }
    
    return 'none';
  }

  // Utility methods
  getClientIP(request) {
    return request.headers?.['x-forwarded-for'] || 
           request.headers?.['x-real-ip'] || 
           request.connection?.remoteAddress || 
           'unknown';
  }

  // Cleanup
  cleanup() {
    this.threats.clear();
    this.rateLimits.clear();
    this.blockedIPs.clear();
    this.suspiciousActivities.clear();
  }
}

// Create singleton instance
const apiSecurityService = new ApiSecurityService();

export default apiSecurityService;
import { apiService } from './apiService';
import advancedApiService from './advancedApiService';
import integrationService from './integrationService';
import apiSecurityService from './apiSecurityService';
import offlineSyncService from './offlineSyncService';
import crossPlatformService from './crossPlatformService';

class SystemIntegrationService {
  constructor() {
    this.modules = new Map();
    this.integrations = new Map();
    this.healthChecks = new Map();
    this.systemMetrics = {
      uptime: Date.now(),
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      averageResponseTime: 0,
      systemLoad: 0,
      memoryUsage: 0,
      errorRate: 0
    };
    
    this.setupSystemMonitoring();
    this.initializeModules();
    this.setupHealthChecks();
  }

  setupSystemMonitoring() {
    // Monitor system performance
    this.monitorSystemPerformance();
    
    // Monitor module health
    this.monitorModuleHealth();
    
    // Monitor integrations
    this.monitorIntegrations();
    
    // Monitor security
    this.monitorSecurity();
  }

  initializeModules() {
    // Core modules
    this.modules.set('authentication', {
      name: 'Authentication',
      status: 'active',
      dependencies: ['api'],
      health: 'healthy',
      lastCheck: Date.now()
    });

    this.modules.set('companies', {
      name: 'Companies',
      status: 'active',
      dependencies: ['authentication', 'api'],
      health: 'healthy',
      lastCheck: Date.now()
    });

    this.modules.set('customers', {
      name: 'Customers',
      status: 'active',
      dependencies: ['authentication', 'api'],
      health: 'healthy',
      lastCheck: Date.now()
    });

    this.modules.set('inventory', {
      name: 'Inventory',
      status: 'active',
      dependencies: ['authentication', 'api'],
      health: 'healthy',
      lastCheck: Date.now()
    });

    this.modules.set('pos', {
      name: 'Point of Sale',
      status: 'active',
      dependencies: ['authentication', 'inventory', 'customers', 'api'],
      health: 'healthy',
      lastCheck: Date.now()
    });

    this.modules.set('sales', {
      name: 'Sales',
      status: 'active',
      dependencies: ['authentication', 'pos', 'api'],
      health: 'healthy',
      lastCheck: Date.now()
    });

    this.modules.set('reports', {
      name: 'Reports',
      status: 'active',
      dependencies: ['authentication', 'sales', 'inventory', 'api'],
      health: 'healthy',
      lastCheck: Date.now()
    });

    this.modules.set('analytics', {
      name: 'Analytics',
      status: 'active',
      dependencies: ['reports', 'api'],
      health: 'healthy',
      lastCheck: Date.now()
    });

    this.modules.set('ai', {
      name: 'AI Features',
      status: 'active',
      dependencies: ['analytics', 'api'],
      health: 'healthy',
      lastCheck: Date.now()
    });

    this.modules.set('mobile', {
      name: 'Mobile Features',
      status: 'active',
      dependencies: ['authentication', 'offline'],
      health: 'healthy',
      lastCheck: Date.now()
    });

    this.modules.set('api', {
      name: 'API Services',
      status: 'active',
      dependencies: [],
      health: 'healthy',
      lastCheck: Date.now()
    });

    this.modules.set('offline', {
      name: 'Offline Sync',
      status: 'active',
      dependencies: ['api'],
      health: 'healthy',
      lastCheck: Date.now()
    });
  }

  setupHealthChecks() {
    // API health check
    this.healthChecks.set('api', async () => {
      try {
        const response = await apiService.get('/api/health');
        return {
          status: 'healthy',
          responseTime: response.responseTime || 0,
          data: response.data
        };
      } catch (error) {
        return {
          status: 'unhealthy',
          error: error.message
        };
      }
    });

    // Advanced API health check
    this.healthChecks.set('advanced_api', async () => {
      try {
        const health = await advancedApiService.healthCheck();
        return {
          status: health.status,
          responseTime: health.responseTime,
          metrics: health.metrics
        };
      } catch (error) {
        return {
          status: 'unhealthy',
          error: error.message
        };
      }
    });

    // Offline sync health check
    this.healthChecks.set('offline_sync', async () => {
      try {
        const health = await offlineSyncService.healthCheck();
        return {
          status: health.status,
          data: health
        };
      } catch (error) {
        return {
          status: 'unhealthy',
          error: error.message
        };
      }
    });

    // Security health check
    this.healthChecks.set('security', async () => {
      try {
        const dashboard = apiSecurityService.getSecurityDashboard();
        return {
          status: dashboard.threatLevel === 'none' ? 'healthy' : 'warning',
          data: dashboard
        };
      } catch (error) {
        return {
          status: 'unhealthy',
          error: error.message
        };
      }
    });

    // Cross-platform health check
    this.healthChecks.set('cross_platform', async () => {
      try {
        const info = crossPlatformService.getPlatformInfo();
        return {
          status: 'healthy',
          data: info
        };
      } catch (error) {
        return {
          status: 'unhealthy',
          error: error.message
        };
      }
    });
  }

  // System monitoring
  monitorSystemPerformance() {
    setInterval(() => {
      this.updateSystemMetrics();
    }, 30000); // Update every 30 seconds
  }

  updateSystemMetrics() {
    // Update system metrics
    this.systemMetrics.systemLoad = this.calculateSystemLoad();
    this.systemMetrics.memoryUsage = this.getMemoryUsage();
    this.systemMetrics.errorRate = this.calculateErrorRate();
    this.systemMetrics.averageResponseTime = this.calculateAverageResponseTime();
  }

  calculateSystemLoad() {
    // Simulate system load calculation
    return Math.random() * 100;
  }

  getMemoryUsage() {
    if ('memory' in performance) {
      const memory = performance.memory;
      return (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100;
    }
    return 0;
  }

  calculateErrorRate() {
    const total = this.systemMetrics.totalRequests;
    const failed = this.systemMetrics.failedRequests;
    return total > 0 ? (failed / total) * 100 : 0;
  }

  calculateAverageResponseTime() {
    // This would be calculated from actual response times
    return Math.random() * 1000;
  }

  // Module health monitoring
  monitorModuleHealth() {
    setInterval(async () => {
      await this.checkAllModules();
    }, 60000); // Check every minute
  }

  async checkAllModules() {
    for (const [moduleId, module] of this.modules) {
      try {
        await this.checkModuleHealth(moduleId);
      } catch (error) {
        console.error(`Health check failed for module ${moduleId}:`, error);
        module.health = 'unhealthy';
        module.lastCheck = Date.now();
      }
    }
  }

  async checkModuleHealth(moduleId) {
    const module = this.modules.get(moduleId);
    if (!module) return;

    // Check dependencies first
    for (const dependency of module.dependencies) {
      const depModule = this.modules.get(dependency);
      if (!depModule || depModule.health !== 'healthy') {
        module.health = 'degraded';
        module.lastCheck = Date.now();
        return;
      }
    }

    // Run specific health checks
    const healthCheck = this.healthChecks.get(moduleId);
    if (healthCheck) {
      const result = await healthCheck();
      module.health = result.status;
      module.lastCheck = Date.now();
    } else {
      // Default health check
      module.health = 'healthy';
      module.lastCheck = Date.now();
    }
  }

  // Integration monitoring
  monitorIntegrations() {
    setInterval(async () => {
      await this.checkAllIntegrations();
    }, 120000); // Check every 2 minutes
  }

  async checkAllIntegrations() {
    const integrations = integrationService.getAvailableIntegrations();
    
    for (const integration of integrations) {
      try {
        await this.checkIntegrationHealth(integration);
      } catch (error) {
        console.error(`Integration health check failed for ${integration.name}:`, error);
      }
    }
  }

  async checkIntegrationHealth(integration) {
    try {
      const result = await integrationService.testIntegration(integration.id);
      this.integrations.set(integration.id, {
        ...integration,
        health: result.success ? 'healthy' : 'unhealthy',
        lastCheck: Date.now(),
        result
      });
    } catch (error) {
      this.integrations.set(integration.id, {
        ...integration,
        health: 'unhealthy',
        lastCheck: Date.now(),
        error: error.message
      });
    }
  }

  // Security monitoring
  monitorSecurity() {
    setInterval(() => {
      this.updateSecurityMetrics();
    }, 30000); // Update every 30 seconds
  }

  updateSecurityMetrics() {
    const securityDashboard = apiSecurityService.getSecurityDashboard();
    this.systemMetrics.security = securityDashboard;
  }

  // System status
  getSystemStatus() {
    const modules = Array.from(this.modules.values());
    const integrations = Array.from(this.integrations.values());
    
    const healthyModules = modules.filter(m => m.health === 'healthy').length;
    const totalModules = modules.length;
    
    const healthyIntegrations = integrations.filter(i => i.health === 'healthy').length;
    const totalIntegrations = integrations.length;
    
    const overallHealth = this.calculateOverallHealth(modules, integrations);
    
    return {
      overall: overallHealth,
      modules: {
        total: totalModules,
        healthy: healthyModules,
        degraded: modules.filter(m => m.health === 'degraded').length,
        unhealthy: modules.filter(m => m.health === 'unhealthy').length
      },
      integrations: {
        total: totalIntegrations,
        healthy: healthyIntegrations,
        unhealthy: integrations.filter(i => i.health === 'unhealthy').length
      },
      metrics: this.systemMetrics,
      uptime: Date.now() - this.systemMetrics.uptime
    };
  }

  calculateOverallHealth(modules, integrations) {
    const moduleHealth = modules.every(m => m.health === 'healthy') ? 'healthy' :
                        modules.some(m => m.health === 'unhealthy') ? 'unhealthy' : 'degraded';
    
    const integrationHealth = integrations.every(i => i.health === 'healthy') ? 'healthy' :
                             integrations.some(i => i.health === 'unhealthy') ? 'degraded' : 'healthy';
    
    if (moduleHealth === 'unhealthy' || integrationHealth === 'unhealthy') {
      return 'unhealthy';
    } else if (moduleHealth === 'degraded' || integrationHealth === 'degraded') {
      return 'degraded';
    } else {
      return 'healthy';
    }
  }

  // System diagnostics
  async runSystemDiagnostics() {
    const diagnostics = {
      timestamp: new Date().toISOString(),
      system: this.getSystemStatus(),
      modules: {},
      integrations: {},
      recommendations: []
    };

    // Check each module
    for (const [moduleId, module] of this.modules) {
      diagnostics.modules[moduleId] = {
        name: module.name,
        status: module.status,
        health: module.health,
        lastCheck: module.lastCheck,
        dependencies: module.dependencies
      };
    }

    // Check each integration
    for (const [integrationId, integration] of this.integrations) {
      diagnostics.integrations[integrationId] = {
        name: integration.name,
        type: integration.type,
        health: integration.health,
        lastCheck: integration.lastCheck
      };
    }

    // Generate recommendations
    diagnostics.recommendations = this.generateRecommendations();

    return diagnostics;
  }

  generateRecommendations() {
    const recommendations = [];
    
    // Check for unhealthy modules
    const unhealthyModules = Array.from(this.modules.values()).filter(m => m.health === 'unhealthy');
    if (unhealthyModules.length > 0) {
      recommendations.push({
        type: 'critical',
        message: `${unhealthyModules.length} modules are unhealthy`,
        action: 'Restart unhealthy modules and check dependencies'
      });
    }

    // Check for degraded modules
    const degradedModules = Array.from(this.modules.values()).filter(m => m.health === 'degraded');
    if (degradedModules.length > 0) {
      recommendations.push({
        type: 'warning',
        message: `${degradedModules.length} modules are degraded`,
        action: 'Check module dependencies and performance'
      });
    }

    // Check for unhealthy integrations
    const unhealthyIntegrations = Array.from(this.integrations.values()).filter(i => i.health === 'unhealthy');
    if (unhealthyIntegrations.length > 0) {
      recommendations.push({
        type: 'warning',
        message: `${unhealthyIntegrations.length} integrations are unhealthy`,
        action: 'Check integration configurations and network connectivity'
      });
    }

    // Check system performance
    if (this.systemMetrics.systemLoad > 80) {
      recommendations.push({
        type: 'warning',
        message: 'High system load detected',
        action: 'Consider scaling resources or optimizing performance'
      });
    }

    if (this.systemMetrics.memoryUsage > 80) {
      recommendations.push({
        type: 'warning',
        message: 'High memory usage detected',
        action: 'Consider clearing cache or optimizing memory usage'
      });
    }

    if (this.systemMetrics.errorRate > 5) {
      recommendations.push({
        type: 'critical',
        message: 'High error rate detected',
        action: 'Investigate and fix errors immediately'
      });
    }

    return recommendations;
  }

  // System maintenance
  async performSystemMaintenance() {
    const maintenance = {
      timestamp: new Date().toISOString(),
      actions: [],
      results: {}
    };

    try {
      // Clear caches
      maintenance.actions.push('Clearing caches...');
      await advancedApiService.clearCache();
      await offlineSyncService.clearCache();
      maintenance.results.cacheCleared = true;

      // Clean up old data
      maintenance.actions.push('Cleaning up old data...');
      await offlineSyncService.cleanupOldData(30);
      maintenance.results.dataCleaned = true;

      // Restart unhealthy modules
      maintenance.actions.push('Restarting unhealthy modules...');
      const unhealthyModules = Array.from(this.modules.values()).filter(m => m.health === 'unhealthy');
      for (const module of unhealthyModules) {
        await this.restartModule(module);
      }
      maintenance.results.modulesRestarted = unhealthyModules.length;

      // Update system metrics
      maintenance.actions.push('Updating system metrics...');
      this.updateSystemMetrics();
      maintenance.results.metricsUpdated = true;

      maintenance.success = true;
    } catch (error) {
      maintenance.success = false;
      maintenance.error = error.message;
    }

    return maintenance;
  }

  async restartModule(module) {
    // Simulate module restart
    module.health = 'healthy';
    module.lastCheck = Date.now();
    return true;
  }

  // System recovery
  async performSystemRecovery() {
    const recovery = {
      timestamp: new Date().toISOString(),
      actions: [],
      results: {}
    };

    try {
      // Restart all modules
      recovery.actions.push('Restarting all modules...');
      for (const [moduleId, module] of this.modules) {
        module.health = 'healthy';
        module.lastCheck = Date.now();
      }
      recovery.results.modulesRestarted = this.modules.size;

      // Clear all caches
      recovery.actions.push('Clearing all caches...');
      await advancedApiService.clearCache();
      await offlineSyncService.clearCache();
      recovery.results.cachesCleared = true;

      // Reset system metrics
      recovery.actions.push('Resetting system metrics...');
      this.systemMetrics = {
        uptime: Date.now(),
        totalRequests: 0,
        successfulRequests: 0,
        failedRequests: 0,
        averageResponseTime: 0,
        systemLoad: 0,
        memoryUsage: 0,
        errorRate: 0
      };
      recovery.results.metricsReset = true;

      recovery.success = true;
    } catch (error) {
      recovery.success = false;
      recovery.error = error.message;
    }

    return recovery;
  }

  // Cleanup
  cleanup() {
    this.modules.clear();
    this.integrations.clear();
    this.healthChecks.clear();
  }
}

// Create singleton instance
const systemIntegrationService = new SystemIntegrationService();

export default systemIntegrationService;
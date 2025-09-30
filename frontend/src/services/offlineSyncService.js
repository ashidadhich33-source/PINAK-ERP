class OfflineSyncService {
  constructor() {
    this.dbName = 'PINAK_ERP_OFFLINE';
    this.dbVersion = 1;
    this.db = null;
    this.syncQueue = [];
    this.isOnline = navigator.onLine;
    this.syncInProgress = false;
    this.listeners = new Map();
    
    this.init();
  }

  async init() {
    try {
      this.db = await this.openDatabase();
      this.setupEventListeners();
      this.startPeriodicSync();
    } catch (error) {
      console.error('Failed to initialize offline sync service:', error);
    }
  }

  async openDatabase() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        
        // Create object stores for different data types
        if (!db.objectStoreNames.contains('companies')) {
          db.createObjectStore('companies', { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains('customers')) {
          db.createObjectStore('customers', { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains('inventory')) {
          db.createObjectStore('inventory', { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains('sales')) {
          db.createObjectStore('sales', { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains('sync_queue')) {
          db.createObjectStore('sync_queue', { keyPath: 'id', autoIncrement: true });
        }
        if (!db.objectStoreNames.contains('offline_data')) {
          db.createObjectStore('offline_data', { keyPath: 'id' });
        }
      };
    });
  }

  setupEventListeners() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.emit('online');
      this.syncAll();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.emit('offline');
    });

    // Listen for visibility change to sync when app becomes visible
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && this.isOnline) {
        this.syncAll();
      }
    });
  }

  startPeriodicSync() {
    // Sync every 30 seconds when online
    setInterval(() => {
      if (this.isOnline && !this.syncInProgress) {
        this.syncAll();
      }
    }, 30000);
  }

  // Data storage methods
  async storeData(storeName, data) {
    try {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      
      if (Array.isArray(data)) {
        for (const item of data) {
          await store.put(item);
        }
      } else {
        await store.put(data);
      }
      
      return true;
    } catch (error) {
      console.error(`Failed to store data in ${storeName}:`, error);
      return false;
    }
  }

  async getData(storeName, id = null) {
    try {
      const transaction = this.db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      
      if (id) {
        return await store.get(id);
      } else {
        return await store.getAll();
      }
    } catch (error) {
      console.error(`Failed to get data from ${storeName}:`, error);
      return null;
    }
  }

  async deleteData(storeName, id) {
    try {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      await store.delete(id);
      return true;
    } catch (error) {
      console.error(`Failed to delete data from ${storeName}:`, error);
      return false;
    }
  }

  // Sync queue management
  async addToSyncQueue(operation) {
    try {
      const syncItem = {
        ...operation,
        timestamp: new Date().toISOString(),
        retryCount: 0,
        status: 'pending'
      };
      
      await this.storeData('sync_queue', syncItem);
      this.syncQueue.push(syncItem);
      
      // Try to sync immediately if online
      if (this.isOnline) {
        this.syncAll();
      }
      
      return true;
    } catch (error) {
      console.error('Failed to add to sync queue:', error);
      return false;
    }
  }

  async getSyncQueue() {
    try {
      return await this.getData('sync_queue');
    } catch (error) {
      console.error('Failed to get sync queue:', error);
      return [];
    }
  }

  async clearSyncQueue() {
    try {
      const transaction = this.db.transaction(['sync_queue'], 'readwrite');
      const store = transaction.objectStore('sync_queue');
      await store.clear();
      this.syncQueue = [];
      return true;
    } catch (error) {
      console.error('Failed to clear sync queue:', error);
      return false;
    }
  }

  // Sync methods
  async syncAll() {
    if (!this.isOnline || this.syncInProgress) {
      return false;
    }

    this.syncInProgress = true;
    this.emit('syncStart');

    try {
      const syncQueue = await this.getSyncQueue();
      const results = [];

      for (const item of syncQueue) {
        try {
          const result = await this.syncItem(item);
          results.push({ ...item, status: 'success', result });
        } catch (error) {
          results.push({ ...item, status: 'error', error: error.message });
        }
      }

      // Remove successful items from sync queue
      const failedItems = results.filter(item => item.status === 'error');
      await this.storeData('sync_queue', failedItems);

      this.emit('syncComplete', results);
      return true;
    } catch (error) {
      console.error('Sync failed:', error);
      this.emit('syncError', error);
      return false;
    } finally {
      this.syncInProgress = false;
    }
  }

  async syncItem(item) {
    // This would typically make API calls to sync data
    // For now, we'll simulate the sync process
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (Math.random() > 0.1) { // 90% success rate
          resolve({ success: true, data: item });
        } else {
          reject(new Error('Sync failed'));
        }
      }, 1000);
    });
  }

  // Offline data management
  async cacheData(key, data) {
    try {
      const cacheItem = {
        id: key,
        data,
        timestamp: new Date().toISOString(),
        version: 1
      };
      
      await this.storeData('offline_data', cacheItem);
      return true;
    } catch (error) {
      console.error('Failed to cache data:', error);
      return false;
    }
  }

  async getCachedData(key) {
    try {
      const cacheItem = await this.getData('offline_data', key);
      return cacheItem ? cacheItem.data : null;
    } catch (error) {
      console.error('Failed to get cached data:', error);
      return null;
    }
  }

  async clearCache() {
    try {
      const transaction = this.db.transaction(['offline_data'], 'readwrite');
      const store = transaction.objectStore('offline_data');
      await store.clear();
      return true;
    } catch (error) {
      console.error('Failed to clear cache:', error);
      return false;
    }
  }

  // Conflict resolution
  async resolveConflict(localData, serverData) {
    // Simple conflict resolution: server data wins
    // In a real implementation, this would be more sophisticated
    return serverData;
  }

  // Event system
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error);
        }
      });
    }
  }

  // Utility methods
  async getStorageSize() {
    try {
      const estimate = await navigator.storage.estimate();
      return {
        used: estimate.usage || 0,
        available: estimate.quota || 0,
        percentage: estimate.usage && estimate.quota ? 
          (estimate.usage / estimate.quota) * 100 : 0
      };
    } catch (error) {
      console.error('Failed to get storage size:', error);
      return null;
    }
  }

  async cleanupOldData(daysToKeep = 30) {
    try {
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);
      
      const stores = ['companies', 'customers', 'inventory', 'sales'];
      
      for (const storeName of stores) {
        const transaction = this.db.transaction([storeName], 'readwrite');
        const store = transaction.objectStore(storeName);
        const data = await store.getAll();
        
        for (const item of data) {
          if (new Date(item.updated_at || item.created_at) < cutoffDate) {
            await store.delete(item.id);
          }
        }
      }
      
      return true;
    } catch (error) {
      console.error('Failed to cleanup old data:', error);
      return false;
    }
  }

  // Health check
  async healthCheck() {
    try {
      const syncQueue = await this.getSyncQueue();
      const storageSize = await this.getStorageSize();
      
      return {
        isOnline: this.isOnline,
        syncInProgress: this.syncInProgress,
        pendingSyncItems: syncQueue.length,
        storageSize,
        dbConnected: !!this.db
      };
    } catch (error) {
      console.error('Health check failed:', error);
      return null;
    }
  }
}

// Create singleton instance
const offlineSyncService = new OfflineSyncService();

export default offlineSyncService;
import { apiService } from './apiService';

export const inventoryService = {
  // Get all items
  getItems: async (params = {}) => {
    try {
      const items = await apiService.get('/api/inventory/items', params);
      return items;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch items');
    }
  },

  // Get item by ID
  getItem: async (itemId) => {
    try {
      const item = await apiService.get(`/api/inventory/items/${itemId}`);
      return item;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch item');
    }
  },

  // Create new item
  createItem: async (itemData) => {
    try {
      const item = await apiService.post('/api/inventory/items', itemData);
      return item;
    } catch (error) {
      throw new Error(error.message || 'Failed to create item');
    }
  },

  // Update item
  updateItem: async (itemId, itemData) => {
    try {
      const item = await apiService.put(`/api/inventory/items/${itemId}`, itemData);
      return item;
    } catch (error) {
      throw new Error(error.message || 'Failed to update item');
    }
  },

  // Delete item
  deleteItem: async (itemId) => {
    try {
      await apiService.delete(`/api/inventory/items/${itemId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete item');
    }
  },

  // Toggle item status
  toggleItemStatus: async (itemId) => {
    try {
      const response = await apiService.put(`/api/inventory/items/${itemId}/toggle-status`);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to toggle item status');
    }
  },

  // Get item statistics
  getItemStats: async (itemId) => {
    try {
      const stats = await apiService.get(`/api/inventory/items/${itemId}/stats`);
      return stats;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch item statistics');
    }
  },

  // Get item stock movements
  getItemStockMovements: async (itemId, params = {}) => {
    try {
      const movements = await apiService.get(`/api/inventory/items/${itemId}/stock-movements`, params);
      return movements;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch stock movements');
    }
  },

  // Search items
  searchItems: async (query, params = {}) => {
    try {
      const items = await apiService.get('/api/inventory/items/search', {
        q: query,
        ...params,
      });
      return items;
    } catch (error) {
      throw new Error(error.message || 'Failed to search items');
    }
  },

  // Export items
  exportItems: async (format = 'csv', filters = {}) => {
    try {
      const response = await apiService.get('/api/inventory/items/export', {
        format,
        ...filters,
      });
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to export items');
    }
  },

  // Import items
  importItems: async (file, onProgress = null) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiService.upload('/api/inventory/items/import', formData, onProgress);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to import items');
    }
  },

  // Get categories
  getCategories: async () => {
    try {
      const categories = await apiService.get('/api/inventory/categories');
      return categories;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch categories');
    }
  },

  // Create category
  createCategory: async (categoryData) => {
    try {
      const category = await apiService.post('/api/inventory/categories', categoryData);
      return category;
    } catch (error) {
      throw new Error(error.message || 'Failed to create category');
    }
  },

  // Update category
  updateCategory: async (categoryId, categoryData) => {
    try {
      const category = await apiService.put(`/api/inventory/categories/${categoryId}`, categoryData);
      return category;
    } catch (error) {
      throw new Error(error.message || 'Failed to update category');
    }
  },

  // Delete category
  deleteCategory: async (categoryId) => {
    try {
      await apiService.delete(`/api/inventory/categories/${categoryId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete category');
    }
  },

  // Get brands
  getBrands: async () => {
    try {
      const brands = await apiService.get('/api/inventory/brands');
      return brands;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch brands');
    }
  },

  // Create brand
  createBrand: async (brandData) => {
    try {
      const brand = await apiService.post('/api/inventory/brands', brandData);
      return brand;
    } catch (error) {
      throw new Error(error.message || 'Failed to create brand');
    }
  },

  // Update brand
  updateBrand: async (brandId, brandData) => {
    try {
      const brand = await apiService.put(`/api/inventory/brands/${brandId}`, brandData);
      return brand;
    } catch (error) {
      throw new Error(error.message || 'Failed to update brand');
    }
  },

  // Delete brand
  deleteBrand: async (brandId) => {
    try {
      await apiService.delete(`/api/inventory/brands/${brandId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete brand');
    }
  },

  // Get units
  getUnits: async () => {
    try {
      const units = await apiService.get('/api/inventory/units');
      return units;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch units');
    }
  },

  // Create unit
  createUnit: async (unitData) => {
    try {
      const unit = await apiService.post('/api/inventory/units', unitData);
      return unit;
    } catch (error) {
      throw new Error(error.message || 'Failed to create unit');
    }
  },

  // Update unit
  updateUnit: async (unitId, unitData) => {
    try {
      const unit = await apiService.put(`/api/inventory/units/${unitId}`, unitData);
      return unit;
    } catch (error) {
      throw new Error(error.message || 'Failed to update unit');
    }
  },

  // Delete unit
  deleteUnit: async (unitId) => {
    try {
      await apiService.delete(`/api/inventory/units/${unitId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete unit');
    }
  },

  // Stock adjustment
  adjustStock: async (itemId, adjustmentData) => {
    try {
      const response = await apiService.post(`/api/inventory/items/${itemId}/adjust-stock`, adjustmentData);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to adjust stock');
    }
  },

  // Get low stock items
  getLowStockItems: async (params = {}) => {
    try {
      const items = await apiService.get('/api/inventory/items/low-stock', params);
      return items;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch low stock items');
    }
  },

  // Get inventory summary
  getInventorySummary: async () => {
    try {
      const summary = await apiService.get('/api/inventory/summary');
      return summary;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch inventory summary');
    }
  },

  // Get item by barcode
  getItemByBarcode: async (barcode) => {
    try {
      const item = await apiService.get(`/api/inventory/items/barcode/${barcode}`);
      return item;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch item by barcode');
    }
  },

  // Get item categories
  getItemCategories: async () => {
    try {
      const categories = await apiService.get('/api/inventory/items/categories');
      return categories;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch item categories');
    }
  },

  // Create item category
  createItemCategory: async (categoryData) => {
    try {
      const category = await apiService.post('/api/inventory/items/categories', categoryData);
      return category;
    } catch (error) {
      throw new Error(error.message || 'Failed to create item category');
    }
  },

  // Update item category
  updateItemCategory: async (categoryId, categoryData) => {
    try {
      const category = await apiService.put(`/api/inventory/items/categories/${categoryId}`, categoryData);
      return category;
    } catch (error) {
      throw new Error(error.message || 'Failed to update item category');
    }
  },

  // Delete item category
  deleteItemCategory: async (categoryId) => {
    try {
      await apiService.delete(`/api/inventory/items/categories/${categoryId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete item category');
    }
  },

  // Update brand
  updateBrand: async (brandId, brandData) => {
    try {
      const brand = await apiService.put(`/api/inventory/items/brands/${brandId}`, brandData);
      return brand;
    } catch (error) {
      throw new Error(error.message || 'Failed to update brand');
    }
  },

  // Delete brand
  deleteBrand: async (brandId) => {
    try {
      await apiService.delete(`/api/inventory/items/brands/${brandId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete brand');
    }
  },

  // Get stock valuation
  getStockValuation: async (params = {}) => {
    try {
      const valuation = await apiService.get('/api/inventory/items/stock-valuation', params);
      return valuation;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch stock valuation');
    }
  },
};
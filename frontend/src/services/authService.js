import { apiService } from './apiService';

export const authService = {
  // Login user
  login: async (credentials) => {
    try {
      const response = await apiService.post('/api/auth/login', credentials);
      
      // Get user profile after successful login
      const user = await authService.getCurrentUser();
      
      return {
        access_token: response.access_token,
        token_type: response.token_type,
        expires_in: response.expires_in,
        user: user,
      };
    } catch (error) {
      throw new Error(error.message || 'Login failed');
    }
  },

  // Get current user
  getCurrentUser: async () => {
    try {
      const user = await apiService.get('/api/auth/me');
      return user;
    } catch (error) {
      throw new Error(error.message || 'Failed to get user profile');
    }
  },

  // Change password
  changePassword: async (passwordData) => {
    try {
      await apiService.post('/api/auth/change-password', passwordData);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to change password');
    }
  },

  // Logout user
  logout: async () => {
    try {
      await apiService.post('/api/auth/logout');
      return true;
    } catch (error) {
      // Even if logout fails on server, clear local token
      console.error('Logout error:', error);
      return true;
    }
  },

  // Get all users (admin only)
  getUsers: async (params = {}) => {
    try {
      const users = await apiService.get('/api/auth/users', params);
      return users;
    } catch (error) {
      throw new Error(error.message || 'Failed to get users');
    }
  },

  // Get user by ID
  getUser: async (userId) => {
    try {
      const user = await apiService.get(`/api/auth/users/${userId}`);
      return user;
    } catch (error) {
      throw new Error(error.message || 'Failed to get user');
    }
  },

  // Create user (admin only)
  createUser: async (userData) => {
    try {
      const user = await apiService.post('/api/auth/users', userData);
      return user;
    } catch (error) {
      throw new Error(error.message || 'Failed to create user');
    }
  },

  // Update user
  updateUser: async (userId, userData) => {
    try {
      const user = await apiService.put(`/api/auth/users/${userId}`, userData);
      return user;
    } catch (error) {
      throw new Error(error.message || 'Failed to update user');
    }
  },

  // Toggle user status
  toggleUserStatus: async (userId) => {
    try {
      const response = await apiService.put(`/api/auth/users/${userId}/toggle-status`);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to toggle user status');
    }
  },

  // Get roles
  getRoles: async () => {
    try {
      const roles = await apiService.get('/api/auth/roles');
      return roles;
    } catch (error) {
      throw new Error(error.message || 'Failed to get roles');
    }
  },

  // Check if user has permission
  hasPermission: (user, permission) => {
    if (!user) return false;
    if (user.is_superuser) return true;
    return user.roles?.some(role => 
      role.permissions?.some(perm => perm.name === permission)
    ) || false;
  },

  // Check if user has role
  hasRole: (user, roleName) => {
    if (!user) return false;
    return user.roles?.some(role => role.name === roleName) || false;
  },
};
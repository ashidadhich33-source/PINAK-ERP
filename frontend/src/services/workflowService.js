import { apiService } from './apiService';

export const workflowService = {
  // Get all workflows
  getWorkflows: async (options = {}) => {
    try {
      const workflows = await apiService.get('/api/workflows', options);
      return workflows;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch workflows');
    }
  },

  // Get workflow by ID
  getWorkflowById: async (workflowId) => {
    try {
      const workflow = await apiService.get(`/api/workflows/${workflowId}`);
      return workflow;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch workflow');
    }
  },

  // Create new workflow
  createWorkflow: async (workflowData) => {
    try {
      const workflow = await apiService.post('/api/workflows', workflowData);
      return workflow;
    } catch (error) {
      throw new Error(error.message || 'Failed to create workflow');
    }
  },

  // Update workflow
  updateWorkflow: async (workflowId, workflowData) => {
    try {
      const workflow = await apiService.put(`/api/workflows/${workflowId}`, workflowData);
      return workflow;
    } catch (error) {
      throw new Error(error.message || 'Failed to update workflow');
    }
  },

  // Delete workflow
  deleteWorkflow: async (workflowId) => {
    try {
      await apiService.delete(`/api/workflows/${workflowId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete workflow');
    }
  },

  // Activate/Deactivate workflow
  toggleWorkflowStatus: async (workflowId, isActive) => {
    try {
      const workflow = await apiService.patch(`/api/workflows/${workflowId}/status`, {
        is_active: isActive
      });
      return workflow;
    } catch (error) {
      throw new Error(error.message || 'Failed to toggle workflow status');
    }
  },

  // Get workflow instances
  getWorkflowInstances: async (workflowId, options = {}) => {
    try {
      const instances = await apiService.get(`/api/workflows/${workflowId}/instances`, options);
      return instances;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch workflow instances');
    }
  },

  // Get workflow instance by ID
  getWorkflowInstance: async (instanceId) => {
    try {
      const instance = await apiService.get(`/api/workflow-instances/${instanceId}`);
      return instance;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch workflow instance');
    }
  },

  // Start workflow instance
  startWorkflowInstance: async (workflowId, data) => {
    try {
      const instance = await apiService.post(`/api/workflows/${workflowId}/start`, data);
      return instance;
    } catch (error) {
      throw new Error(error.message || 'Failed to start workflow instance');
    }
  },

  // Complete workflow step
  completeWorkflowStep: async (instanceId, stepId, data) => {
    try {
      const result = await apiService.post(`/api/workflow-instances/${instanceId}/steps/${stepId}/complete`, data);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to complete workflow step');
    }
  },

  // Reject workflow step
  rejectWorkflowStep: async (instanceId, stepId, reason) => {
    try {
      const result = await apiService.post(`/api/workflow-instances/${instanceId}/steps/${stepId}/reject`, {
        reason
      });
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to reject workflow step');
    }
  },

  // Get pending approvals
  getPendingApprovals: async (options = {}) => {
    try {
      const approvals = await apiService.get('/api/workflows/pending-approvals', options);
      return approvals;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch pending approvals');
    }
  },

  // Get user's workflow tasks
  getUserTasks: async (options = {}) => {
    try {
      const tasks = await apiService.get('/api/workflows/user-tasks', options);
      return tasks;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch user tasks');
    }
  },

  // Complete user task
  completeUserTask: async (taskId, data) => {
    try {
      const result = await apiService.post(`/api/workflows/tasks/${taskId}/complete`, data);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to complete user task');
    }
  },

  // Get workflow templates
  getWorkflowTemplates: async () => {
    try {
      const templates = await apiService.get('/api/workflows/templates');
      return templates;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch workflow templates');
    }
  },

  // Create workflow from template
  createWorkflowFromTemplate: async (templateId, data) => {
    try {
      const workflow = await apiService.post(`/api/workflows/templates/${templateId}/create`, data);
      return workflow;
    } catch (error) {
      throw new Error(error.message || 'Failed to create workflow from template');
    }
  },

  // Get workflow analytics
  getWorkflowAnalytics: async (workflowId, options = {}) => {
    try {
      const analytics = await apiService.get(`/api/workflows/${workflowId}/analytics`, options);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch workflow analytics');
    }
  },

  // Get workflow performance metrics
  getWorkflowMetrics: async (workflowId, options = {}) => {
    try {
      const metrics = await apiService.get(`/api/workflows/${workflowId}/metrics`, options);
      return metrics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch workflow metrics');
    }
  },

  // Export workflow data
  exportWorkflowData: async (workflowId, format = 'csv', options = {}) => {
    try {
      const data = await apiService.get(`/api/workflows/${workflowId}/export`, {
        format,
        ...options
      });
      return data;
    } catch (error) {
      throw new Error(error.message || 'Failed to export workflow data');
    }
  },

  // Get workflow logs
  getWorkflowLogs: async (workflowId, options = {}) => {
    try {
      const logs = await apiService.get(`/api/workflows/${workflowId}/logs`, options);
      return logs;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch workflow logs');
    }
  },

  // Get workflow notifications
  getWorkflowNotifications: async (options = {}) => {
    try {
      const notifications = await apiService.get('/api/workflows/notifications', options);
      return notifications;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch workflow notifications');
    }
  },

  // Mark notification as read
  markNotificationAsRead: async (notificationId) => {
    try {
      await apiService.patch(`/api/workflows/notifications/${notificationId}/read`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to mark notification as read');
    }
  },

  // Get workflow statistics
  getWorkflowStatistics: async (options = {}) => {
    try {
      const statistics = await apiService.get('/api/workflows/statistics', options);
      return statistics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch workflow statistics');
    }
  },

  // Get workflow reports
  getWorkflowReports: async (options = {}) => {
    try {
      const reports = await apiService.get('/api/workflows/reports', options);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch workflow reports');
    }
  },

  // Generate workflow report
  generateWorkflowReport: async (workflowId, reportType, options = {}) => {
    try {
      const report = await apiService.post(`/api/workflows/${workflowId}/reports`, {
        report_type: reportType,
        ...options
      });
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to generate workflow report');
    }
  },

  // Get workflow permissions
  getWorkflowPermissions: async (workflowId) => {
    try {
      const permissions = await apiService.get(`/api/workflows/${workflowId}/permissions`);
      return permissions;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch workflow permissions');
    }
  },

  // Update workflow permissions
  updateWorkflowPermissions: async (workflowId, permissions) => {
    try {
      const result = await apiService.put(`/api/workflows/${workflowId}/permissions`, permissions);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update workflow permissions');
    }
  },

  // Get workflow collaborators
  getWorkflowCollaborators: async (workflowId) => {
    try {
      const collaborators = await apiService.get(`/api/workflows/${workflowId}/collaborators`);
      return collaborators;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch workflow collaborators');
    }
  },

  // Add workflow collaborator
  addWorkflowCollaborator: async (workflowId, userId, role) => {
    try {
      const result = await apiService.post(`/api/workflows/${workflowId}/collaborators`, {
        user_id: userId,
        role: role
      });
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to add workflow collaborator');
    }
  },

  // Remove workflow collaborator
  removeWorkflowCollaborator: async (workflowId, userId) => {
    try {
      await apiService.delete(`/api/workflows/${workflowId}/collaborators/${userId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to remove workflow collaborator');
    }
  },
};
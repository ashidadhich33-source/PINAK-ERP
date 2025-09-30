import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { settingsService } from '../../services/settingsService';
import Button from '../../components/common/Button';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  Bell, 
  Play, 
  Pause, 
  Settings, 
  Plus, 
  Edit, 
  Trash2, 
  RefreshCw, 
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  Clock,
  Activity,
  Zap,
  Workflow,
  Target,
  BarChart3,
  Info
} from 'lucide-react';

const AutomationDashboard = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [workflows, setWorkflows] = useState([]);
  const [rules, setRules] = useState([]);
  const [triggers, setTriggers] = useState([]);
  const [actions, setActions] = useState([]);
  const [logs, setLogs] = useState([]);
  const [activeTab, setActiveTab] = useState('workflows');

  // Fetch automation data
  const fetchAutomationData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [workflowsData, rulesData, triggersData, actionsData, logsData] = await Promise.all([
        settingsService.getAutomationWorkflows(),
        settingsService.getAutomationRules(),
        settingsService.getAutomationTriggers(),
        settingsService.getAutomationActions(),
        settingsService.getAutomationLogs()
      ]);
      
      setWorkflows(workflowsData);
      setRules(rulesData);
      setTriggers(triggersData);
      setActions(actionsData);
      setLogs(logsData);
    } catch (err) {
      setError(err.message);
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAutomationData();
  }, []);

  // Handle execute automation
  const handleExecuteAutomation = async (automationId) => {
    try {
      await settingsService.executeAutomation(automationId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Automation executed successfully',
      });
      fetchAutomationData();
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle approve automation
  const handleApproveAutomation = async (automationId) => {
    try {
      await settingsService.approveAutomation(automationId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Automation approved successfully',
      });
      fetchAutomationData();
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle rollback automation
  const handleRollbackAutomation = async (automationId) => {
    if (!window.confirm('Are you sure you want to rollback this automation?')) {
      return;
    }

    try {
      await settingsService.rollbackAutomation(automationId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Automation rolled back successfully',
      });
      fetchAutomationData();
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Get status icon and color
  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
      case 'running':
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-success-500" />;
      case 'pending':
      case 'waiting':
        return <Clock className="w-5 h-5 text-warning-500" />;
      case 'failed':
      case 'error':
      case 'stopped':
        return <XCircle className="w-5 h-5 text-danger-500" />;
      default:
        return <Info className="w-5 h-5 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading automation data..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Automation Dashboard</h1>
          <p className="text-gray-600">Manage automated workflows and business processes</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={fetchAutomationData}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </Button>
          <Button className="flex items-center space-x-2">
            <Plus className="w-4 h-4" />
            <span>Create Workflow</span>
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert type="danger" title="Error">
          {error}
        </Alert>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'workflows', name: 'Workflows', icon: Workflow },
              { id: 'rules', name: 'Rules', icon: Target },
              { id: 'triggers', name: 'Triggers', icon: Zap },
              { id: 'actions', name: 'Actions', icon: Activity },
              { id: 'logs', name: 'Logs', icon: BarChart3 }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {/* Workflows Tab */}
          {activeTab === 'workflows' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">Automation Workflows</h2>
                  <p className="text-gray-600">Manage your automated business processes</p>
                </div>
                <Button className="flex items-center space-x-2">
                  <Plus className="w-4 h-4" />
                  <span>Create Workflow</span>
                </Button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {workflows.map((workflow) => (
                  <div key={workflow.id} className="bg-white border border-gray-200 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <Workflow className="w-6 h-6 text-primary-600" />
                        <div>
                          <h3 className="text-lg font-medium text-gray-900">{workflow.name}</h3>
                          <p className="text-sm text-gray-500">{workflow.description}</p>
                        </div>
                      </div>
                      {getStatusIcon(workflow.status)}
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-500">Status</span>
                        <span className={`font-medium ${
                          workflow.status === 'active' ? 'text-success-600' :
                          workflow.status === 'pending' ? 'text-warning-600' :
                          'text-danger-600'
                        }`}>
                          {workflow.status}
                        </span>
                      </div>
                      
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-500">Last Run</span>
                        <span className="font-medium">{workflow.last_run || 'Never'}</span>
                      </div>
                      
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-500">Next Run</span>
                        <span className="font-medium">{workflow.next_run || 'Not scheduled'}</span>
                      </div>
                    </div>
                    
                    <div className="mt-4 flex items-center space-x-2">
                      <Button
                        size="sm"
                        onClick={() => handleExecuteAutomation(workflow.id)}
                        className="flex-1"
                      >
                        <Play className="w-4 h-4 mr-1" />
                        Execute
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleApproveAutomation(workflow.id)}
                        className="flex-1"
                      >
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Approve
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleRollbackAutomation(workflow.id)}
                        className="flex-1 text-danger-600 hover:text-danger-700"
                      >
                        <XCircle className="w-4 h-4 mr-1" />
                        Rollback
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Rules Tab */}
          {activeTab === 'rules' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">Automation Rules</h2>
                  <p className="text-gray-600">Define business rules for automation</p>
                </div>
                <Button className="flex items-center space-x-2">
                  <Plus className="w-4 h-4" />
                  <span>Create Rule</span>
                </Button>
              </div>

              <div className="space-y-4">
                {rules.map((rule) => (
                  <div key={rule.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Target className="w-5 h-5 text-primary-600" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">{rule.name}</p>
                        <p className="text-xs text-gray-500">{rule.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(rule.status)}
                      <Button size="sm" variant="outline">
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button size="sm" variant="outline" className="text-danger-600 hover:text-danger-700">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Triggers Tab */}
          {activeTab === 'triggers' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">Automation Triggers</h2>
                  <p className="text-gray-600">Events that trigger automation workflows</p>
                </div>
                <Button className="flex items-center space-x-2">
                  <Plus className="w-4 h-4" />
                  <span>Create Trigger</span>
                </Button>
              </div>

              <div className="space-y-4">
                {triggers.map((trigger) => (
                  <div key={trigger.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Zap className="w-5 h-5 text-primary-600" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">{trigger.name}</p>
                        <p className="text-xs text-gray-500">{trigger.event_type}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(trigger.status)}
                      <Button size="sm" variant="outline">
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button size="sm" variant="outline" className="text-danger-600 hover:text-danger-700">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Actions Tab */}
          {activeTab === 'actions' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">Automation Actions</h2>
                  <p className="text-gray-600">Actions performed by automation workflows</p>
                </div>
                <Button className="flex items-center space-x-2">
                  <Plus className="w-4 h-4" />
                  <span>Create Action</span>
                </Button>
              </div>

              <div className="space-y-4">
                {actions.map((action) => (
                  <div key={action.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Activity className="w-5 h-5 text-primary-600" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">{action.name}</p>
                        <p className="text-xs text-gray-500">{action.action_type}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(action.status)}
                      <Button size="sm" variant="outline">
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button size="sm" variant="outline" className="text-danger-600 hover:text-danger-700">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Logs Tab */}
          {activeTab === 'logs' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">Automation Logs</h2>
                  <p className="text-gray-600">View automation execution history and logs</p>
                </div>
                <Button variant="outline" className="flex items-center space-x-2">
                  <RefreshCw className="w-4 h-4" />
                  <span>Refresh</span>
                </Button>
              </div>

              <div className="space-y-4">
                {logs.map((log) => (
                  <div key={log.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(log.status)}
                      <div>
                        <p className="text-sm font-medium text-gray-900">{log.workflow_name}</p>
                        <p className="text-xs text-gray-500">{log.message}</p>
                        <p className="text-xs text-gray-400">{log.timestamp}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        log.status === 'success' ? 'bg-success-100 text-success-800' :
                        log.status === 'error' ? 'bg-danger-100 text-danger-800' :
                        'bg-warning-100 text-warning-800'
                      }`}>
                        {log.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AutomationDashboard;
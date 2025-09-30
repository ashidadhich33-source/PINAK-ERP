import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { workflowService } from '../../services/workflowService';
import Button from '../common/Button';
import Input from '../common/Input';
import Alert from '../common/Alert';
import LoadingSpinner from '../common/LoadingSpinner';
import { 
  Plus, 
  Trash2, 
  Save, 
  Play, 
  Pause, 
  Settings,
  Users,
  Clock,
  CheckCircle,
  XCircle,
  ArrowRight,
  ArrowDown,
  AlertCircle
} from 'lucide-react';

const WorkflowBuilder = ({ workflowId, onSave, onCancel }) => {
  const { addNotification } = useApp();
  const [workflow, setWorkflow] = useState({
    name: '',
    description: '',
    is_active: true,
    steps: [],
    triggers: [],
    conditions: [],
    actions: []
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [selectedStep, setSelectedStep] = useState(null);
  const [showStepEditor, setShowStepEditor] = useState(false);

  // Step types
  const stepTypes = [
    { id: 'approval', name: 'Approval', icon: CheckCircle, color: 'bg-primary-500' },
    { id: 'notification', name: 'Notification', icon: AlertCircle, color: 'bg-warning-500' },
    { id: 'assignment', name: 'Assignment', icon: Users, color: 'bg-success-500' },
    { id: 'delay', name: 'Delay', icon: Clock, color: 'bg-secondary-500' },
    { id: 'condition', name: 'Condition', icon: Settings, color: 'bg-info-500' },
  ];

  // Load workflow if editing
  useEffect(() => {
    if (workflowId) {
      loadWorkflow();
    }
  }, [workflowId]);

  const loadWorkflow = async () => {
    try {
      setLoading(true);
      const data = await workflowService.getWorkflowById(workflowId);
      setWorkflow(data);
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

  const handleInputChange = (field, value) => {
    setWorkflow(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const addStep = (stepType) => {
    const newStep = {
      id: Date.now().toString(),
      type: stepType,
      name: `New ${stepType} Step`,
      description: '',
      order: workflow.steps.length + 1,
      config: {},
      is_active: true
    };

    setWorkflow(prev => ({
      ...prev,
      steps: [...prev.steps, newStep]
    }));

    setSelectedStep(newStep);
    setShowStepEditor(true);
  };

  const updateStep = (stepId, updates) => {
    setWorkflow(prev => ({
      ...prev,
      steps: prev.steps.map(step => 
        step.id === stepId ? { ...step, ...updates } : step
      )
    }));
  };

  const deleteStep = (stepId) => {
    setWorkflow(prev => ({
      ...prev,
      steps: prev.steps.filter(step => step.id !== stepId)
    }));

    if (selectedStep?.id === stepId) {
      setSelectedStep(null);
      setShowStepEditor(false);
    }
  };

  const moveStep = (stepId, direction) => {
    const steps = [...workflow.steps];
    const index = steps.findIndex(step => step.id === stepId);
    
    if (direction === 'up' && index > 0) {
      [steps[index], steps[index - 1]] = [steps[index - 1], steps[index]];
    } else if (direction === 'down' && index < steps.length - 1) {
      [steps[index], steps[index + 1]] = [steps[index + 1], steps[index]];
    }

    // Update order
    steps.forEach((step, idx) => {
      step.order = idx + 1;
    });

    setWorkflow(prev => ({
      ...prev,
      steps
    }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);

      let savedWorkflow;
      if (workflowId) {
        savedWorkflow = await workflowService.updateWorkflow(workflowId, workflow);
      } else {
        savedWorkflow = await workflowService.createWorkflow(workflow);
      }

      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Workflow saved successfully',
      });

      onSave?.(savedWorkflow);
    } catch (err) {
      setError(err.message);
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    onCancel?.();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading workflow..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            {workflowId ? 'Edit Workflow' : 'Create Workflow'}
          </h2>
          <p className="text-gray-600">Design and configure your workflow</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={handleCancel}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            loading={saving}
            className="flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>Save Workflow</span>
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert type="danger" title="Error">
          {error}
        </Alert>
      )}

      {/* Workflow Details */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Workflow Details</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="form-label">Name</label>
            <Input
              value={workflow.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              placeholder="Enter workflow name"
            />
          </div>
          <div>
            <label className="form-label">Status</label>
            <select
              value={workflow.is_active ? 'active' : 'inactive'}
              onChange={(e) => handleInputChange('is_active', e.target.value === 'active')}
              className="form-input"
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
        </div>
        <div className="mt-4">
          <label className="form-label">Description</label>
          <textarea
            value={workflow.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            placeholder="Enter workflow description"
            className="form-input"
            rows={3}
          />
        </div>
      </div>

      {/* Workflow Steps */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Workflow Steps</h3>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">{workflow.steps.length} steps</span>
          </div>
        </div>

        {/* Add Step Buttons */}
        <div className="flex flex-wrap gap-2 mb-6">
          {stepTypes.map((stepType) => {
            const Icon = stepType.icon;
            return (
              <button
                key={stepType.id}
                onClick={() => addStep(stepType.id)}
                className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
              >
                <Icon className="w-4 h-4" />
                <span>Add {stepType.name}</span>
              </button>
            );
          })}
        </div>

        {/* Steps List */}
        {workflow.steps.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Settings className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No steps added yet</p>
            <p className="text-sm">Click the buttons above to add workflow steps</p>
          </div>
        ) : (
          <div className="space-y-3">
            {workflow.steps.map((step, index) => {
              const stepType = stepTypes.find(t => t.id === step.type);
              const Icon = stepType?.icon || Settings;
              
              return (
                <div
                  key={step.id}
                  className={`flex items-center justify-between p-4 border rounded-lg ${
                    selectedStep?.id === step.id ? 'border-primary-500 bg-primary-50' : 'border-gray-200'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${stepType?.color || 'bg-gray-500'}`}>
                      <Icon className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{step.name}</p>
                      <p className="text-sm text-gray-500">{step.description || 'No description'}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-500">Step {step.order}</span>
                    <button
                      onClick={() => setSelectedStep(step)}
                      className="p-1 text-gray-400 hover:text-gray-600"
                    >
                      <Settings className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => deleteStep(step.id)}
                      className="p-1 text-gray-400 hover:text-danger-600"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Step Editor Modal */}
      {showStepEditor && selectedStep && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-96 overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Edit Step</h3>
                <button
                  onClick={() => setShowStepEditor(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="w-5 h-5" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="form-label">Step Name</label>
                  <Input
                    value={selectedStep.name}
                    onChange={(e) => updateStep(selectedStep.id, { name: e.target.value })}
                    placeholder="Enter step name"
                  />
                </div>
                
                <div>
                  <label className="form-label">Description</label>
                  <textarea
                    value={selectedStep.description}
                    onChange={(e) => updateStep(selectedStep.id, { description: e.target.value })}
                    placeholder="Enter step description"
                    className="form-input"
                    rows={3}
                  />
                </div>
                
                {/* Step-specific configuration */}
                {selectedStep.type === 'approval' && (
                  <div>
                    <label className="form-label">Approval Configuration</label>
                    <div className="space-y-2">
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={selectedStep.config.requires_comment || false}
                          onChange={(e) => updateStep(selectedStep.id, {
                            config: { ...selectedStep.config, requires_comment: e.target.checked }
                          })}
                          className="mr-2"
                        />
                        <span className="text-sm text-gray-700">Require comment</span>
                      </label>
                    </div>
                  </div>
                )}
                
                {selectedStep.type === 'notification' && (
                  <div>
                    <label className="form-label">Notification Configuration</label>
                    <div className="space-y-2">
                      <Input
                        value={selectedStep.config.subject || ''}
                        onChange={(e) => updateStep(selectedStep.id, {
                          config: { ...selectedStep.config, subject: e.target.value }
                        })}
                        placeholder="Notification subject"
                      />
                      <textarea
                        value={selectedStep.config.message || ''}
                        onChange={(e) => updateStep(selectedStep.id, {
                          config: { ...selectedStep.config, message: e.target.value }
                        })}
                        placeholder="Notification message"
                        className="form-input"
                        rows={3}
                      />
                    </div>
                  </div>
                )}
                
                {selectedStep.type === 'delay' && (
                  <div>
                    <label className="form-label">Delay Configuration</label>
                    <div className="grid grid-cols-2 gap-4">
                      <Input
                        type="number"
                        value={selectedStep.config.delay_value || ''}
                        onChange={(e) => updateStep(selectedStep.id, {
                          config: { ...selectedStep.config, delay_value: e.target.value }
                        })}
                        placeholder="Delay value"
                      />
                      <select
                        value={selectedStep.config.delay_unit || 'minutes'}
                        onChange={(e) => updateStep(selectedStep.id, {
                          config: { ...selectedStep.config, delay_unit: e.target.value }
                        })}
                        className="form-input"
                      >
                        <option value="minutes">Minutes</option>
                        <option value="hours">Hours</option>
                        <option value="days">Days</option>
                      </select>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="flex items-center justify-end space-x-3 mt-6">
                <Button
                  variant="outline"
                  onClick={() => setShowStepEditor(false)}
                >
                  Cancel
                </Button>
                <Button
                  onClick={() => setShowStepEditor(false)}
                >
                  Save Step
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkflowBuilder;
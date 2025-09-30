import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { loyaltyService } from '../../services/loyaltyService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  Award, 
  Plus, 
  Edit, 
  Trash2, 
  Search, 
  Filter, 
  Download, 
  RefreshCw, 
  Save, 
  X,
  Eye,
  Star,
  Gift,
  Target,
  Users,
  TrendingUp,
  Calendar,
  Settings,
  CheckCircle,
  AlertTriangle,
  Clock,
  DollarSign,
  Percent,
  Crown,
  Zap
} from 'lucide-react';

const LoyaltyPrograms = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [programs, setPrograms] = useState([]);
  const [filteredPrograms, setFilteredPrograms] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingProgram, setEditingProgram] = useState(null);
  const [viewingProgram, setViewingProgram] = useState(null);
  const [activeTab, setActiveTab] = useState('programs');

  // Form data
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: 'points',
    status: 'active',
    start_date: '',
    end_date: '',
    points_per_rupee: 1,
    minimum_redemption: 100,
    maximum_redemption: 10000,
    expiry_days: 365,
    tiers: [
      { name: 'Bronze', min_points: 0, benefits: [] },
      { name: 'Silver', min_points: 1000, benefits: [] },
      { name: 'Gold', min_points: 5000, benefits: [] }
    ],
    rewards: []
  });

  // Program statuses
  const programStatuses = [
    { value: 'active', label: 'Active', color: 'text-green-600', bgColor: 'bg-green-100' },
    { value: 'inactive', label: 'Inactive', color: 'text-gray-600', bgColor: 'bg-gray-100' },
    { value: 'draft', label: 'Draft', color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
    { value: 'expired', label: 'Expired', color: 'text-red-600', bgColor: 'bg-red-100' }
  ];

  // Program types
  const programTypes = [
    { value: 'points', label: 'Points Based', icon: Star },
    { value: 'tier', label: 'Tier Based', icon: Crown },
    { value: 'cashback', label: 'Cashback', icon: DollarSign },
    { value: 'discount', label: 'Discount', icon: Percent }
  ];

  // Fetch programs
  useEffect(() => {
    const fetchPrograms = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const programsData = await loyaltyService.getLoyaltyPrograms();
        setPrograms(programsData);
        setFilteredPrograms(programsData);
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

    fetchPrograms();
  }, []);

  // Filter programs
  useEffect(() => {
    let filtered = programs;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(program =>
        program.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        program.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(program => program.status === statusFilter);
    }

    setFilteredPrograms(filtered);
  }, [programs, searchTerm, statusFilter]);

  // Handle form field changes
  const handleFieldChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle tier changes
  const handleTierChange = (index, field, value) => {
    const newTiers = [...formData.tiers];
    newTiers[index] = {
      ...newTiers[index],
      [field]: value
    };
    setFormData(prev => ({
      ...prev,
      tiers: newTiers
    }));
  };

  // Add new tier
  const addTier = () => {
    setFormData(prev => ({
      ...prev,
      tiers: [...prev.tiers, { name: '', min_points: 0, benefits: [] }]
    }));
  };

  // Remove tier
  const removeTier = (index) => {
    if (formData.tiers.length > 1) {
      setFormData(prev => ({
        ...prev,
        tiers: prev.tiers.filter((_, i) => i !== index)
      }));
    }
  };

  // Handle add program
  const handleAddProgram = async () => {
    try {
      setSaving(true);
      await loyaltyService.createLoyaltyProgram(formData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Loyalty program created successfully',
      });
      setShowAddForm(false);
      resetForm();
      // Refresh programs
      const programsData = await loyaltyService.getLoyaltyPrograms();
      setPrograms(programsData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setSaving(false);
    }
  };

  // Handle edit program
  const handleEditProgram = async () => {
    try {
      setSaving(true);
      await loyaltyService.updateLoyaltyProgram(editingProgram.id, formData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Loyalty program updated successfully',
      });
      setEditingProgram(null);
      setShowAddForm(false);
      resetForm();
      // Refresh programs
      const programsData = await loyaltyService.getLoyaltyPrograms();
      setPrograms(programsData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setSaving(false);
    }
  };

  // Handle delete program
  const handleDeleteProgram = async (programId) => {
    if (!window.confirm('Are you sure you want to delete this loyalty program?')) {
      return;
    }

    try {
      await loyaltyService.deleteLoyaltyProgram(programId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Loyalty program deleted successfully',
      });
      // Refresh programs
      const programsData = await loyaltyService.getLoyaltyPrograms();
      setPrograms(programsData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      type: 'points',
      status: 'active',
      start_date: '',
      end_date: '',
      points_per_rupee: 1,
      minimum_redemption: 100,
      maximum_redemption: 10000,
      expiry_days: 365,
      tiers: [
        { name: 'Bronze', min_points: 0, benefits: [] },
        { name: 'Silver', min_points: 1000, benefits: [] },
        { name: 'Gold', min_points: 5000, benefits: [] }
      ],
      rewards: []
    });
  };

  // Get status info
  const getStatusInfo = (status) => {
    return programStatuses.find(s => s.value === status) || programStatuses[0];
  };

  // Get program type info
  const getProgramTypeInfo = (type) => {
    return programTypes.find(t => t.value === type) || programTypes[0];
  };

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading loyalty programs..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Loyalty Programs</h1>
          <p className="text-gray-600">Manage customer loyalty programs and rewards</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={() => window.location.reload()}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </Button>
          <Button
            onClick={() => setShowAddForm(true)}
            className="flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Add Program</span>
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
              { id: 'programs', name: 'Loyalty Programs', icon: Award },
              { id: 'tiers', name: 'Tier Management', icon: Crown },
              { id: 'rewards', name: 'Reward Catalog', icon: Gift },
              { id: 'analytics', name: 'Analytics', icon: TrendingUp }
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
          {/* Programs Tab */}
          {activeTab === 'programs' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search programs..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full"
                  />
                </div>
                <div className="w-48">
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="form-input"
                  >
                    <option value="all">All Status</option>
                    {programStatuses.map(status => (
                      <option key={status.value} value={status.value}>
                        {status.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Programs List */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredPrograms.map((program) => {
                  const programTypeInfo = getProgramTypeInfo(program.type);
                  const statusInfo = getStatusInfo(program.status);
                  const Icon = programTypeInfo.icon;
                  
                  return (
                    <div key={program.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                            <Icon className="w-5 h-5 text-primary-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">{program.name}</h3>
                            <p className="text-sm text-gray-500">{program.description}</p>
                          </div>
                        </div>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                          {statusInfo.label}
                        </span>
                      </div>
                      
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Type:</span>
                          <span className="text-sm font-medium text-gray-900">{programTypeInfo.label}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Points per ₹:</span>
                          <span className="text-sm font-medium text-gray-900">{program.points_per_rupee}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Members:</span>
                          <span className="text-sm font-medium text-gray-900">{program.member_count || 0}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Valid:</span>
                          <span className="text-sm font-medium text-gray-900">
                            {program.start_date ? formatDate(program.start_date) : 'N/A'} - {program.end_date ? formatDate(program.end_date) : 'N/A'}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setViewingProgram(program)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingProgram(program);
                            setFormData(program);
                            setShowAddForm(true);
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteProgram(program.id)}
                          className="text-danger-600 hover:text-danger-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Tier Management Tab */}
          {activeTab === 'tiers' && (
            <div className="space-y-6">
              <div className="text-center py-12">
                <Crown className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Tier Management</h3>
                <p className="text-gray-500">Customer tier management will be implemented here</p>
              </div>
            </div>
          )}

          {/* Reward Catalog Tab */}
          {activeTab === 'rewards' && (
            <div className="space-y-6">
              <div className="text-center py-12">
                <Gift className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Reward Catalog</h3>
                <p className="text-gray-500">Reward management system will be implemented here</p>
              </div>
            </div>
          )}

          {/* Analytics Tab */}
          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <div className="text-center py-12">
                <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Loyalty Analytics</h3>
                <p className="text-gray-500">Loyalty program analytics will be implemented here</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Add/Edit Program Modal */}
      {showAddForm && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowAddForm(false)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Award className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {editingProgram ? 'Edit Loyalty Program' : 'Add New Loyalty Program'}
                      </h3>
                      <p className="text-sm text-gray-500">Create or update loyalty program</p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setShowAddForm(false);
                      setEditingProgram(null);
                      resetForm();
                    }}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Program Name *
                      </label>
                      <Input
                        value={formData.name}
                        onChange={(e) => handleFieldChange('name', e.target.value)}
                        placeholder="Enter program name"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Program Type *
                      </label>
                      <select
                        value={formData.type}
                        onChange={(e) => handleFieldChange('type', e.target.value)}
                        className="form-input"
                        required
                      >
                        {programTypes.map(type => (
                          <option key={type.value} value={type.value}>
                            {type.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => handleFieldChange('description', e.target.value)}
                      rows={3}
                      className="form-input"
                      placeholder="Enter program description"
                    />
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Start Date
                      </label>
                      <Input
                        type="date"
                        value={formData.start_date}
                        onChange={(e) => handleFieldChange('start_date', e.target.value)}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        End Date
                      </label>
                      <Input
                        type="date"
                        value={formData.end_date}
                        onChange={(e) => handleFieldChange('end_date', e.target.value)}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Status
                      </label>
                      <select
                        value={formData.status}
                        onChange={(e) => handleFieldChange('status', e.target.value)}
                        className="form-input"
                      >
                        {programStatuses.map(status => (
                          <option key={status.value} value={status.value}>
                            {status.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Points per ₹
                      </label>
                      <Input
                        type="number"
                        value={formData.points_per_rupee}
                        onChange={(e) => handleFieldChange('points_per_rupee', parseFloat(e.target.value) || 0)}
                        min="0"
                        step="0.1"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Min Redemption
                      </label>
                      <Input
                        type="number"
                        value={formData.minimum_redemption}
                        onChange={(e) => handleFieldChange('minimum_redemption', parseFloat(e.target.value) || 0)}
                        min="0"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Max Redemption
                      </label>
                      <Input
                        type="number"
                        value={formData.maximum_redemption}
                        onChange={(e) => handleFieldChange('maximum_redemption', parseFloat(e.target.value) || 0)}
                        min="0"
                      />
                    </div>
                  </div>
                  
                  {/* Tiers Section */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm font-medium text-gray-900">Program Tiers</h4>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={addTier}
                      >
                        <Plus className="w-4 h-4 mr-1" />
                        Add Tier
                      </Button>
                    </div>
                    
                    <div className="space-y-3">
                      {formData.tiers.map((tier, index) => (
                        <div key={index} className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg">
                          <Input
                            value={tier.name}
                            onChange={(e) => handleTierChange(index, 'name', e.target.value)}
                            placeholder="Tier Name"
                            className="flex-1"
                          />
                          <Input
                            type="number"
                            value={tier.min_points}
                            onChange={(e) => handleTierChange(index, 'min_points', parseFloat(e.target.value) || 0)}
                            placeholder="Min Points"
                            min="0"
                            className="w-32"
                          />
                          {formData.tiers.length > 1 && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => removeTier(index)}
                              className="text-danger-600 hover:text-danger-700"
                            >
                              <X className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <Button
                  onClick={editingProgram ? handleEditProgram : handleAddProgram}
                  loading={saving}
                  className="w-full sm:w-auto sm:ml-3"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {editingProgram ? 'Update Program' : 'Create Program'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowAddForm(false);
                    setEditingProgram(null);
                    resetForm();
                  }}
                  className="mt-3 w-full sm:mt-0 sm:w-auto"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* View Program Modal */}
      {viewingProgram && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setViewingProgram(null)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Award className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">Loyalty Program Details</h3>
                      <p className="text-sm text-gray-500">View loyalty program information</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setViewingProgram(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Program Name</p>
                      <p className="text-sm font-medium text-gray-900">{viewingProgram.name}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Type</p>
                      <p className="text-sm font-medium text-gray-900">{getProgramTypeInfo(viewingProgram.type).label}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Status</p>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusInfo(viewingProgram.status).bgColor} ${getStatusInfo(viewingProgram.status).color}`}>
                        {getStatusInfo(viewingProgram.status).label}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Points per ₹</p>
                      <p className="text-sm font-medium text-gray-900">{viewingProgram.points_per_rupee}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Start Date</p>
                      <p className="text-sm font-medium text-gray-900">
                        {viewingProgram.start_date ? formatDate(viewingProgram.start_date) : 'N/A'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">End Date</p>
                      <p className="text-sm font-medium text-gray-900">
                        {viewingProgram.end_date ? formatDate(viewingProgram.end_date) : 'N/A'}
                      </p>
                    </div>
                  </div>
                  
                  {viewingProgram.description && (
                    <div>
                      <p className="text-sm text-gray-500">Description</p>
                      <p className="text-sm text-gray-900">{viewingProgram.description}</p>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <Button
                  onClick={() => setViewingProgram(null)}
                  className="w-full sm:w-auto"
                >
                  Close
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LoyaltyPrograms;
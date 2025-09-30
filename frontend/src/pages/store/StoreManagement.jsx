import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { storeService } from '../../services/storeService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  Store, 
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
  Zap,
  ArrowUp,
  ArrowDown,
  Minus,
  CreditCard,
  ShoppingCart,
  User,
  FileText,
  BarChart3,
  Smartphone,
  Wifi,
  Shield,
  Bell,
  Mail,
  Link,
  Copy,
  Play,
  Pause,
  Stop,
  Send,
  MessageSquare,
  Database,
  Filter as FilterIcon,
  Layers,
  Activity,
  Globe,
  Building2,
  Home,
  Navigation,
  Map,
  Receipt,
  FileCheck,
  TrendingDown,
  PieChart,
  MapPin,
  Phone,
  Mail as MailIcon,
  ExternalLink,
  ChevronRight,
  ChevronDown,
  TreePine,
  Building
} from 'lucide-react';

const StoreManagement = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [stores, setStores] = useState([]);
  const [filteredStores, setFilteredStores] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showAddStore, setShowAddStore] = useState(false);
  const [editingStore, setEditingStore] = useState(null);
  const [viewingStore, setViewingStore] = useState(null);
  const [activeTab, setActiveTab] = useState('stores');
  const [expandedStores, setExpandedStores] = useState(new Set());

  // Store form data
  const [storeFormData, setStoreFormData] = useState({
    name: '',
    code: '',
    type: 'retail',
    parent_store_id: '',
    address: '',
    city: '',
    state: '',
    pincode: '',
    phone: '',
    email: '',
    manager_name: '',
    manager_phone: '',
    manager_email: '',
    opening_hours: '',
    timezone: 'Asia/Kolkata',
    currency: 'INR',
    tax_number: '',
    gst_number: '',
    status: 'active'
  });

  // Store types
  const storeTypes = [
    { value: 'retail', label: 'Retail Store', icon: Store },
    { value: 'warehouse', label: 'Warehouse', icon: Building2 },
    { value: 'outlet', label: 'Outlet', icon: Building },
    { value: 'online', label: 'Online Store', icon: Globe },
    { value: 'popup', label: 'Popup Store', icon: MapPin }
  ];

  // Store statuses
  const storeStatuses = [
    { value: 'active', label: 'Active', color: 'text-green-600', bgColor: 'bg-green-100' },
    { value: 'inactive', label: 'Inactive', color: 'text-gray-600', bgColor: 'bg-gray-100' },
    { value: 'maintenance', label: 'Maintenance', color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
    { value: 'closed', label: 'Closed', color: 'text-red-600', bgColor: 'bg-red-100' }
  ];

  // Timezones
  const timezones = [
    { value: 'Asia/Kolkata', label: 'Asia/Kolkata (IST)' },
    { value: 'Asia/Dubai', label: 'Asia/Dubai (GST)' },
    { value: 'America/New_York', label: 'America/New_York (EST)' },
    { value: 'Europe/London', label: 'Europe/London (GMT)' }
  ];

  // Currencies
  const currencies = [
    { value: 'INR', label: 'Indian Rupee (₹)' },
    { value: 'USD', label: 'US Dollar ($)' },
    { value: 'EUR', label: 'Euro (€)' },
    { value: 'GBP', label: 'British Pound (£)' }
  ];

  // Fetch stores
  useEffect(() => {
    const fetchStores = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const storesData = await storeService.getStores();
        setStores(storesData);
        setFilteredStores(storesData);
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

    fetchStores();
  }, []);

  // Filter stores
  useEffect(() => {
    let filtered = stores;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(store =>
        store.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        store.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
        store.city.toLowerCase().includes(searchTerm.toLowerCase()) ||
        store.manager_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(store => store.status === statusFilter);
    }

    setFilteredStores(filtered);
  }, [stores, searchTerm, statusFilter]);

  // Handle form field changes
  const handleFieldChange = (field, value) => {
    setStoreFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle add store
  const handleAddStore = async () => {
    try {
      setSaving(true);
      await storeService.createStore(storeFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Store created successfully',
      });
      setShowAddStore(false);
      resetForm();
      // Refresh stores
      const storesData = await storeService.getStores();
      setStores(storesData);
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

  // Handle edit store
  const handleEditStore = async () => {
    try {
      setSaving(true);
      await storeService.updateStore(editingStore.id, storeFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Store updated successfully',
      });
      setEditingStore(null);
      setShowAddStore(false);
      resetForm();
      // Refresh stores
      const storesData = await storeService.getStores();
      setStores(storesData);
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

  // Handle delete store
  const handleDeleteStore = async (storeId) => {
    if (!window.confirm('Are you sure you want to delete this store?')) {
      return;
    }

    try {
      await storeService.deleteStore(storeId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Store deleted successfully',
      });
      // Refresh stores
      const storesData = await storeService.getStores();
      setStores(storesData);
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
    setStoreFormData({
      name: '',
      code: '',
      type: 'retail',
      parent_store_id: '',
      address: '',
      city: '',
      state: '',
      pincode: '',
      phone: '',
      email: '',
      manager_name: '',
      manager_phone: '',
      manager_email: '',
      opening_hours: '',
      timezone: 'Asia/Kolkata',
      currency: 'INR',
      tax_number: '',
      gst_number: '',
      status: 'active'
    });
  };

  // Toggle store expansion
  const toggleStoreExpansion = (storeId) => {
    const newExpanded = new Set(expandedStores);
    if (newExpanded.has(storeId)) {
      newExpanded.delete(storeId);
    } else {
      newExpanded.add(storeId);
    }
    setExpandedStores(newExpanded);
  };

  // Get status info
  const getStatusInfo = (status) => {
    return storeStatuses.find(s => s.value === status) || storeStatuses[0];
  };

  // Get store type info
  const getStoreTypeInfo = (type) => {
    return storeTypes.find(t => t.value === type) || storeTypes[0];
  };

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading stores..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Store Management</h1>
          <p className="text-gray-600">Manage multiple stores and their configurations</p>
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
            onClick={() => setShowAddStore(true)}
            className="flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Add Store</span>
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
              { id: 'stores', name: 'Stores', icon: Store },
              { id: 'hierarchy', name: 'Store Hierarchy', icon: TreePine },
              { id: 'settings', name: 'Store Settings', icon: Settings },
              { id: 'analytics', name: 'Store Analytics', icon: BarChart3 }
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
          {/* Stores Tab */}
          {activeTab === 'stores' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search stores..."
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
                    {storeStatuses.map(status => (
                      <option key={status.value} value={status.value}>
                        {status.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Stores List */}
              <div className="space-y-4">
                {filteredStores.map((store) => {
                  const statusInfo = getStatusInfo(store.status);
                  const typeInfo = getStoreTypeInfo(store.type);
                  const TypeIcon = typeInfo.icon;
                  const isExpanded = expandedStores.has(store.id);
                  
                  return (
                    <div key={store.id} className="bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                      <div className="p-6">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                              <TypeIcon className="w-6 h-6 text-blue-600" />
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center space-x-3">
                                <h3 className="text-lg font-medium text-gray-900">{store.name}</h3>
                                <span className="text-sm text-gray-500">({store.code})</span>
                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                                  {statusInfo.label}
                                </span>
                              </div>
                              <div className="flex items-center space-x-4 mt-1">
                                <div className="flex items-center space-x-1">
                                  <MapPin className="w-4 h-4 text-gray-400" />
                                  <span className="text-sm text-gray-500">{store.city}, {store.state}</span>
                                </div>
                                <div className="flex items-center space-x-1">
                                  <User className="w-4 h-4 text-gray-400" />
                                  <span className="text-sm text-gray-500">{store.manager_name}</span>
                                </div>
                                <div className="flex items-center space-x-1">
                                  <Phone className="w-4 h-4 text-gray-400" />
                                  <span className="text-sm text-gray-500">{store.phone}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => toggleStoreExpansion(store.id)}
                            >
                              {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => setViewingStore(store)}
                            >
                              <Eye className="w-4 h-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => {
                                setEditingStore(store);
                                setStoreFormData(store);
                                setShowAddStore(true);
                              }}
                            >
                              <Edit className="w-4 h-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleDeleteStore(store.id)}
                              className="text-danger-600 hover:text-danger-700"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                        
                        {/* Expanded Details */}
                        {isExpanded && (
                          <div className="mt-4 pt-4 border-t border-gray-200">
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                              <div>
                                <h4 className="text-sm font-medium text-gray-900 mb-2">Store Information</h4>
                                <div className="space-y-1">
                                  <div className="flex items-center space-x-2">
                                    <span className="text-sm text-gray-500">Type:</span>
                                    <span className="text-sm font-medium text-gray-900">{typeInfo.label}</span>
                                  </div>
                                  <div className="flex items-center space-x-2">
                                    <span className="text-sm text-gray-500">Currency:</span>
                                    <span className="text-sm font-medium text-gray-900">{store.currency}</span>
                                  </div>
                                  <div className="flex items-center space-x-2">
                                    <span className="text-sm text-gray-500">Timezone:</span>
                                    <span className="text-sm font-medium text-gray-900">{store.timezone}</span>
                                  </div>
                                </div>
                              </div>
                              
                              <div>
                                <h4 className="text-sm font-medium text-gray-900 mb-2">Contact Information</h4>
                                <div className="space-y-1">
                                  <div className="flex items-center space-x-2">
                                    <MailIcon className="w-4 h-4 text-gray-400" />
                                    <span className="text-sm text-gray-900">{store.email}</span>
                                  </div>
                                  <div className="flex items-center space-x-2">
                                    <Phone className="w-4 h-4 text-gray-400" />
                                    <span className="text-sm text-gray-900">{store.phone}</span>
                                  </div>
                                  <div className="flex items-center space-x-2">
                                    <MapPin className="w-4 h-4 text-gray-400" />
                                    <span className="text-sm text-gray-900">{store.address}</span>
                                  </div>
                                </div>
                              </div>
                              
                              <div>
                                <h4 className="text-sm font-medium text-gray-900 mb-2">Manager Information</h4>
                                <div className="space-y-1">
                                  <div className="flex items-center space-x-2">
                                    <span className="text-sm text-gray-500">Name:</span>
                                    <span className="text-sm font-medium text-gray-900">{store.manager_name}</span>
                                  </div>
                                  <div className="flex items-center space-x-2">
                                    <span className="text-sm text-gray-500">Phone:</span>
                                    <span className="text-sm font-medium text-gray-900">{store.manager_phone}</span>
                                  </div>
                                  <div className="flex items-center space-x-2">
                                    <span className="text-sm text-gray-500">Email:</span>
                                    <span className="text-sm font-medium text-gray-900">{store.manager_email}</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Store Hierarchy Tab */}
          {activeTab === 'hierarchy' && (
            <div className="space-y-6">
              <div className="text-center py-12">
                <TreePine className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Store Hierarchy</h3>
                <p className="text-gray-500">Store organization structure will be implemented here</p>
              </div>
            </div>
          )}

          {/* Store Settings Tab */}
          {activeTab === 'settings' && (
            <div className="space-y-6">
              <div className="text-center py-12">
                <Settings className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Store Settings</h3>
                <p className="text-gray-500">Store-specific configurations will be implemented here</p>
              </div>
            </div>
          )}

          {/* Store Analytics Tab */}
          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <div className="text-center py-12">
                <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Store Analytics</h3>
                <p className="text-gray-500">Store performance metrics will be implemented here</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Add/Edit Store Modal */}
      {showAddStore && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowAddStore(false)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Store className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {editingStore ? 'Edit Store' : 'Add New Store'}
                      </h3>
                      <p className="text-sm text-gray-500">Create or update store information</p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setShowAddStore(false);
                      setEditingStore(null);
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
                        Store Name *
                      </label>
                      <Input
                        value={storeFormData.name}
                        onChange={(e) => handleFieldChange('name', e.target.value)}
                        placeholder="Enter store name"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Store Code *
                      </label>
                      <Input
                        value={storeFormData.code}
                        onChange={(e) => handleFieldChange('code', e.target.value)}
                        placeholder="Enter store code"
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Store Type *
                      </label>
                      <select
                        value={storeFormData.type}
                        onChange={(e) => handleFieldChange('type', e.target.value)}
                        className="form-input"
                        required
                      >
                        {storeTypes.map(type => (
                          <option key={type.value} value={type.value}>
                            {type.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Parent Store
                      </label>
                      <select
                        value={storeFormData.parent_store_id}
                        onChange={(e) => handleFieldChange('parent_store_id', e.target.value)}
                        className="form-input"
                      >
                        <option value="">No Parent Store</option>
                        {stores.map(store => (
                          <option key={store.id} value={store.id}>
                            {store.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Address *
                    </label>
                    <textarea
                      value={storeFormData.address}
                      onChange={(e) => handleFieldChange('address', e.target.value)}
                      rows={3}
                      className="form-input"
                      placeholder="Enter store address"
                      required
                    />
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        City *
                      </label>
                      <Input
                        value={storeFormData.city}
                        onChange={(e) => handleFieldChange('city', e.target.value)}
                        placeholder="Enter city"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        State *
                      </label>
                      <Input
                        value={storeFormData.state}
                        onChange={(e) => handleFieldChange('state', e.target.value)}
                        placeholder="Enter state"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Pincode *
                      </label>
                      <Input
                        value={storeFormData.pincode}
                        onChange={(e) => handleFieldChange('pincode', e.target.value)}
                        placeholder="Enter pincode"
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Phone *
                      </label>
                      <Input
                        value={storeFormData.phone}
                        onChange={(e) => handleFieldChange('phone', e.target.value)}
                        placeholder="Enter phone number"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Email *
                      </label>
                      <Input
                        type="email"
                        value={storeFormData.email}
                        onChange={(e) => handleFieldChange('email', e.target.value)}
                        placeholder="Enter email"
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Manager Name *
                      </label>
                      <Input
                        value={storeFormData.manager_name}
                        onChange={(e) => handleFieldChange('manager_name', e.target.value)}
                        placeholder="Enter manager name"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Manager Phone
                      </label>
                      <Input
                        value={storeFormData.manager_phone}
                        onChange={(e) => handleFieldChange('manager_phone', e.target.value)}
                        placeholder="Enter manager phone"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Manager Email
                      </label>
                      <Input
                        type="email"
                        value={storeFormData.manager_email}
                        onChange={(e) => handleFieldChange('manager_email', e.target.value)}
                        placeholder="Enter manager email"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Opening Hours
                      </label>
                      <Input
                        value={storeFormData.opening_hours}
                        onChange={(e) => handleFieldChange('opening_hours', e.target.value)}
                        placeholder="e.g., 9:00 AM - 9:00 PM"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Timezone
                      </label>
                      <select
                        value={storeFormData.timezone}
                        onChange={(e) => handleFieldChange('timezone', e.target.value)}
                        className="form-input"
                      >
                        {timezones.map(timezone => (
                          <option key={timezone.value} value={timezone.value}>
                            {timezone.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Currency
                      </label>
                      <select
                        value={storeFormData.currency}
                        onChange={(e) => handleFieldChange('currency', e.target.value)}
                        className="form-input"
                      >
                        {currencies.map(currency => (
                          <option key={currency.value} value={currency.value}>
                            {currency.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Tax Number
                      </label>
                      <Input
                        value={storeFormData.tax_number}
                        onChange={(e) => handleFieldChange('tax_number', e.target.value)}
                        placeholder="Enter tax number"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        GST Number
                      </label>
                      <Input
                        value={storeFormData.gst_number}
                        onChange={(e) => handleFieldChange('gst_number', e.target.value)}
                        placeholder="Enter GST number"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Status
                    </label>
                    <select
                      value={storeFormData.status}
                      onChange={(e) => handleFieldChange('status', e.target.value)}
                      className="form-input"
                    >
                      {storeStatuses.map(status => (
                        <option key={status.value} value={status.value}>
                          {status.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <Button
                  onClick={editingStore ? handleEditStore : handleAddStore}
                  loading={saving}
                  className="w-full sm:w-auto sm:ml-3"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {editingStore ? 'Update Store' : 'Create Store'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowAddStore(false);
                    setEditingStore(null);
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
    </div>
  );
};

export default StoreManagement;
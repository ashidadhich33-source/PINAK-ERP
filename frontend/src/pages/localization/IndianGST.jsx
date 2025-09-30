import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { localizationService } from '../../services/localizationService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  Calculator, 
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
  PieChart
} from 'lucide-react';

const IndianGST = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [gstRates, setGstRates] = useState([]);
  const [gstReturns, setGstReturns] = useState([]);
  const [gstReports, setGstReports] = useState([]);
  const [filteredRates, setFilteredRates] = useState([]);
  const [filteredReturns, setFilteredReturns] = useState([]);
  const [filteredReports, setFilteredReports] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showAddRate, setShowAddRate] = useState(false);
  const [showAddReturn, setShowAddReturn] = useState(false);
  const [editingRate, setEditingRate] = useState(null);
  const [editingReturn, setEditingReturn] = useState(null);
  const [viewingRate, setViewingRate] = useState(null);
  const [viewingReturn, setViewingReturn] = useState(null);
  const [activeTab, setActiveTab] = useState('rates');

  // GST Rate form data
  const [rateFormData, setRateFormData] = useState({
    category: '',
    subcategory: '',
    cgst_rate: 0,
    sgst_rate: 0,
    igst_rate: 0,
    cess_rate: 0,
    description: '',
    status: 'active'
  });

  // GST Return form data
  const [returnFormData, setReturnFormData] = useState({
    return_type: 'GSTR-1',
    period: '',
    due_date: '',
    status: 'draft',
    description: ''
  });

  // GST categories
  const gstCategories = [
    { value: 'goods', label: 'Goods', icon: ShoppingCart },
    { value: 'services', label: 'Services', icon: Settings },
    { value: 'food', label: 'Food & Beverages', icon: Gift },
    { value: 'healthcare', label: 'Healthcare', icon: Shield },
    { value: 'education', label: 'Education', icon: Users },
    { value: 'transport', label: 'Transport', icon: Navigation }
  ];

  // GST return types
  const gstReturnTypes = [
    { value: 'GSTR-1', label: 'GSTR-1 (Outward Supplies)', icon: ArrowUp },
    { value: 'GSTR-2', label: 'GSTR-2 (Inward Supplies)', icon: ArrowDown },
    { value: 'GSTR-3B', label: 'GSTR-3B (Monthly Return)', icon: Calendar },
    { value: 'GSTR-9', label: 'GSTR-9 (Annual Return)', icon: FileText }
  ];

  // Status options
  const statusOptions = [
    { value: 'active', label: 'Active', color: 'text-green-600', bgColor: 'bg-green-100' },
    { value: 'inactive', label: 'Inactive', color: 'text-gray-600', bgColor: 'bg-gray-100' },
    { value: 'draft', label: 'Draft', color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
    { value: 'submitted', label: 'Submitted', color: 'text-blue-600', bgColor: 'bg-blue-100' },
    { value: 'approved', label: 'Approved', color: 'text-green-600', bgColor: 'bg-green-100' },
    { value: 'rejected', label: 'Rejected', color: 'text-red-600', bgColor: 'bg-red-100' }
  ];

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const [ratesData, returnsData, reportsData] = await Promise.all([
          localizationService.getGSTRates(),
          localizationService.getGSTReturns(),
          localizationService.getGSTReports()
        ]);
        
        setGstRates(ratesData);
        setGstReturns(returnsData);
        setGstReports(reportsData);
        setFilteredRates(ratesData);
        setFilteredReturns(returnsData);
        setFilteredReports(reportsData);
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

    fetchData();
  }, []);

  // Filter data
  useEffect(() => {
    let filtered = [];

    switch (activeTab) {
      case 'rates':
        filtered = gstRates;
        break;
      case 'returns':
        filtered = gstReturns;
        break;
      case 'reports':
        filtered = gstReports;
        break;
      default:
        filtered = [];
    }

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(item =>
        item.category?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.subcategory?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.return_type?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.period?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Category filter
    if (categoryFilter !== 'all') {
      filtered = filtered.filter(item => item.category === categoryFilter);
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(item => item.status === statusFilter);
    }

    switch (activeTab) {
      case 'rates':
        setFilteredRates(filtered);
        break;
      case 'returns':
        setFilteredReturns(filtered);
        break;
      case 'reports':
        setFilteredReports(filtered);
        break;
    }
  }, [gstRates, gstReturns, gstReports, searchTerm, categoryFilter, statusFilter, activeTab]);

  // Handle rate form field changes
  const handleRateFieldChange = (field, value) => {
    setRateFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle return form field changes
  const handleReturnFieldChange = (field, value) => {
    setReturnFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle add rate
  const handleAddRate = async () => {
    try {
      setSaving(true);
      await localizationService.createGSTRate(rateFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'GST rate created successfully',
      });
      setShowAddRate(false);
      resetRateForm();
      // Refresh rates
      const ratesData = await localizationService.getGSTRates();
      setGstRates(ratesData);
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

  // Handle add return
  const handleAddReturn = async () => {
    try {
      setSaving(true);
      await localizationService.createGSTReturn(returnFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'GST return created successfully',
      });
      setShowAddReturn(false);
      resetReturnForm();
      // Refresh returns
      const returnsData = await localizationService.getGSTReturns();
      setGstReturns(returnsData);
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

  // Handle delete rate
  const handleDeleteRate = async (rateId) => {
    if (!window.confirm('Are you sure you want to delete this GST rate?')) {
      return;
    }

    try {
      await localizationService.deleteGSTRate(rateId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'GST rate deleted successfully',
      });
      // Refresh rates
      const ratesData = await localizationService.getGSTRates();
      setGstRates(ratesData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle delete return
  const handleDeleteReturn = async (returnId) => {
    if (!window.confirm('Are you sure you want to delete this GST return?')) {
      return;
    }

    try {
      await localizationService.deleteGSTReturn(returnId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'GST return deleted successfully',
      });
      // Refresh returns
      const returnsData = await localizationService.getGSTReturns();
      setGstReturns(returnsData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Reset forms
  const resetRateForm = () => {
    setRateFormData({
      category: '',
      subcategory: '',
      cgst_rate: 0,
      sgst_rate: 0,
      igst_rate: 0,
      cess_rate: 0,
      description: '',
      status: 'active'
    });
  };

  const resetReturnForm = () => {
    setReturnFormData({
      return_type: 'GSTR-1',
      period: '',
      due_date: '',
      status: 'draft',
      description: ''
    });
  };

  // Get status info
  const getStatusInfo = (status) => {
    return statusOptions.find(s => s.value === status) || statusOptions[0];
  };

  // Get category info
  const getCategoryInfo = (category) => {
    return gstCategories.find(c => c.value === category) || gstCategories[0];
  };

  // Get return type info
  const getReturnTypeInfo = (returnType) => {
    return gstReturnTypes.find(r => r.value === returnType) || gstReturnTypes[0];
  };

  // Format percentage
  const formatPercentage = (value) => {
    return `${value}%`;
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
        <LoadingSpinner size="lg" text="Loading Indian GST..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Indian GST</h1>
          <p className="text-gray-600">Manage GST rates, returns, and compliance</p>
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
              { id: 'rates', name: 'GST Rates', icon: Calculator },
              { id: 'returns', name: 'GST Returns', icon: FileText },
              { id: 'reports', name: 'GST Reports', icon: BarChart3 },
              { id: 'compliance', name: 'Compliance', icon: Shield }
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
          {/* GST Rates Tab */}
          {activeTab === 'rates' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search GST rates..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full"
                  />
                </div>
                <div className="w-48">
                  <select
                    value={categoryFilter}
                    onChange={(e) => setCategoryFilter(e.target.value)}
                    className="form-input"
                  >
                    <option value="all">All Categories</option>
                    {gstCategories.map(category => (
                      <option key={category.value} value={category.value}>
                        {category.label}
                      </option>
                    ))}
                  </select>
                </div>
                <Button
                  onClick={() => setShowAddRate(true)}
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Rate</span>
                </Button>
              </div>

              {/* GST Rates List */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredRates.map((rate) => {
                  const statusInfo = getStatusInfo(rate.status);
                  const categoryInfo = getCategoryInfo(rate.category);
                  const CategoryIcon = categoryInfo.icon;
                  
                  return (
                    <div key={rate.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                            <CategoryIcon className="w-5 h-5 text-blue-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">{rate.category}</h3>
                            <p className="text-sm text-gray-500">{rate.subcategory}</p>
                          </div>
                        </div>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                          {statusInfo.label}
                        </span>
                      </div>
                      
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-500">CGST:</span>
                          <span className="text-sm font-medium text-gray-900">{formatPercentage(rate.cgst_rate)}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-500">SGST:</span>
                          <span className="text-sm font-medium text-gray-900">{formatPercentage(rate.sgst_rate)}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-500">IGST:</span>
                          <span className="text-sm font-medium text-gray-900">{formatPercentage(rate.igst_rate)}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-500">Cess:</span>
                          <span className="text-sm font-medium text-gray-900">{formatPercentage(rate.cess_rate)}</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setViewingRate(rate)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingRate(rate);
                            setRateFormData(rate);
                            setShowAddRate(true);
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteRate(rate.id)}
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

          {/* GST Returns Tab */}
          {activeTab === 'returns' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search GST returns..."
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
                    {statusOptions.map(status => (
                      <option key={status.value} value={status.value}>
                        {status.label}
                      </option>
                    ))}
                  </select>
                </div>
                <Button
                  onClick={() => setShowAddReturn(true)}
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Return</span>
                </Button>
              </div>

              {/* GST Returns List */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredReturns.map((returnItem) => {
                  const statusInfo = getStatusInfo(returnItem.status);
                  const returnTypeInfo = getReturnTypeInfo(returnItem.return_type);
                  const ReturnIcon = returnTypeInfo.icon;
                  
                  return (
                    <div key={returnItem.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                            <ReturnIcon className="w-5 h-5 text-green-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">{returnItem.return_type}</h3>
                            <p className="text-sm text-gray-500">{returnItem.period}</p>
                          </div>
                        </div>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                          {statusInfo.label}
                        </span>
                      </div>
                      
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-500">Period:</span>
                          <span className="text-sm font-medium text-gray-900">{returnItem.period}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-500">Due Date:</span>
                          <span className="text-sm font-medium text-gray-900">{formatDate(returnItem.due_date)}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-500">Amount:</span>
                          <span className="text-sm font-medium text-gray-900">{formatCurrency(returnItem.amount || 0)}</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setViewingReturn(returnItem)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingReturn(returnItem);
                            setReturnFormData(returnItem);
                            setShowAddReturn(true);
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteReturn(returnItem.id)}
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

          {/* GST Reports Tab */}
          {activeTab === 'reports' && (
            <div className="space-y-6">
              <div className="text-center py-12">
                <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">GST Reports</h3>
                <p className="text-gray-500">GST compliance reports will be implemented here</p>
              </div>
            </div>
          )}

          {/* Compliance Tab */}
          {activeTab === 'compliance' && (
            <div className="space-y-6">
              <div className="text-center py-12">
                <Shield className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">GST Compliance</h3>
                <p className="text-gray-500">GST compliance and regulatory reporting will be implemented here</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Add/Edit GST Rate Modal */}
      {showAddRate && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowAddRate(false)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Calculator className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {editingRate ? 'Edit GST Rate' : 'Add New GST Rate'}
                      </h3>
                      <p className="text-sm text-gray-500">Create or update GST rate</p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setShowAddRate(false);
                      setEditingRate(null);
                      resetRateForm();
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
                        Category *
                      </label>
                      <select
                        value={rateFormData.category}
                        onChange={(e) => handleRateFieldChange('category', e.target.value)}
                        className="form-input"
                        required
                      >
                        <option value="">Select Category</option>
                        {gstCategories.map(category => (
                          <option key={category.value} value={category.value}>
                            {category.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Subcategory
                      </label>
                      <Input
                        value={rateFormData.subcategory}
                        onChange={(e) => handleRateFieldChange('subcategory', e.target.value)}
                        placeholder="Enter subcategory"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        CGST Rate (%)
                      </label>
                      <Input
                        type="number"
                        value={rateFormData.cgst_rate}
                        onChange={(e) => handleRateFieldChange('cgst_rate', parseFloat(e.target.value) || 0)}
                        placeholder="Enter CGST rate"
                        min="0"
                        max="100"
                        step="0.01"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        SGST Rate (%)
                      </label>
                      <Input
                        type="number"
                        value={rateFormData.sgst_rate}
                        onChange={(e) => handleRateFieldChange('sgst_rate', parseFloat(e.target.value) || 0)}
                        placeholder="Enter SGST rate"
                        min="0"
                        max="100"
                        step="0.01"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        IGST Rate (%)
                      </label>
                      <Input
                        type="number"
                        value={rateFormData.igst_rate}
                        onChange={(e) => handleRateFieldChange('igst_rate', parseFloat(e.target.value) || 0)}
                        placeholder="Enter IGST rate"
                        min="0"
                        max="100"
                        step="0.01"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Cess Rate (%)
                      </label>
                      <Input
                        type="number"
                        value={rateFormData.cess_rate}
                        onChange={(e) => handleRateFieldChange('cess_rate', parseFloat(e.target.value) || 0)}
                        placeholder="Enter Cess rate"
                        min="0"
                        max="100"
                        step="0.01"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description
                    </label>
                    <textarea
                      value={rateFormData.description}
                      onChange={(e) => handleRateFieldChange('description', e.target.value)}
                      rows={3}
                      className="form-input"
                      placeholder="Enter description"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Status
                    </label>
                    <select
                      value={rateFormData.status}
                      onChange={(e) => handleRateFieldChange('status', e.target.value)}
                      className="form-input"
                    >
                      {statusOptions.map(status => (
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
                  onClick={editingRate ? handleEditRate : handleAddRate}
                  loading={saving}
                  className="w-full sm:w-auto sm:ml-3"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {editingRate ? 'Update Rate' : 'Create Rate'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowAddRate(false);
                    setEditingRate(null);
                    resetRateForm();
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

      {/* Add/Edit GST Return Modal */}
      {showAddReturn && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowAddReturn(false)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {editingReturn ? 'Edit GST Return' : 'Add New GST Return'}
                      </h3>
                      <p className="text-sm text-gray-500">Create or update GST return</p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setShowAddReturn(false);
                      setEditingReturn(null);
                      resetReturnForm();
                    }}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Return Type *
                    </label>
                    <select
                      value={returnFormData.return_type}
                      onChange={(e) => handleReturnFieldChange('return_type', e.target.value)}
                      className="form-input"
                      required
                    >
                      {gstReturnTypes.map(returnType => (
                        <option key={returnType.value} value={returnType.value}>
                          {returnType.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Period *
                      </label>
                      <Input
                        value={returnFormData.period}
                        onChange={(e) => handleReturnFieldChange('period', e.target.value)}
                        placeholder="e.g., 2024-01"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Due Date *
                      </label>
                      <Input
                        type="date"
                        value={returnFormData.due_date}
                        onChange={(e) => handleReturnFieldChange('due_date', e.target.value)}
                        required
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Status
                    </label>
                    <select
                      value={returnFormData.status}
                      onChange={(e) => handleReturnFieldChange('status', e.target.value)}
                      className="form-input"
                    >
                      {statusOptions.map(status => (
                        <option key={status.value} value={status.value}>
                          {status.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description
                    </label>
                    <textarea
                      value={returnFormData.description}
                      onChange={(e) => handleReturnFieldChange('description', e.target.value)}
                      rows={3}
                      className="form-input"
                      placeholder="Enter description"
                    />
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <Button
                  onClick={editingReturn ? handleEditReturn : handleAddReturn}
                  loading={saving}
                  className="w-full sm:w-auto sm:ml-3"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {editingReturn ? 'Update Return' : 'Create Return'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowAddReturn(false);
                    setEditingReturn(null);
                    resetReturnForm();
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

export default IndianGST;
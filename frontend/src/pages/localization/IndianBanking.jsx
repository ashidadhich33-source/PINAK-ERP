import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { localizationService } from '../../services/localizationService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  CreditCard, 
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
  Banknote,
  Wallet,
  Smartphone as SmartphoneIcon,
  QrCode,
  ArrowRightLeft
} from 'lucide-react';

const IndianBanking = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [banks, setBanks] = useState([]);
  const [upiProviders, setUpiProviders] = useState([]);
  const [paymentGateways, setPaymentGateways] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [filteredBanks, setFilteredBanks] = useState([]);
  const [filteredUpiProviders, setFilteredUpiProviders] = useState([]);
  const [filteredPaymentGateways, setFilteredPaymentGateways] = useState([]);
  const [filteredTransactions, setFilteredTransactions] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showAddBank, setShowAddBank] = useState(false);
  const [showAddUpi, setShowAddUpi] = useState(false);
  const [showAddGateway, setShowAddGateway] = useState(false);
  const [editingBank, setEditingBank] = useState(null);
  const [editingUpi, setEditingUpi] = useState(null);
  const [editingGateway, setEditingGateway] = useState(null);
  const [viewingBank, setViewingBank] = useState(null);
  const [viewingUpi, setViewingUpi] = useState(null);
  const [viewingGateway, setViewingGateway] = useState(null);
  const [activeTab, setActiveTab] = useState('banks');

  // Bank form data
  const [bankFormData, setBankFormData] = useState({
    name: '',
    code: '',
    ifsc_code: '',
    micr_code: '',
    branch: '',
    address: '',
    city: '',
    state: '',
    pincode: '',
    phone: '',
    email: '',
    status: 'active'
  });

  // UPI form data
  const [upiFormData, setUpiFormData] = useState({
    provider_name: '',
    provider_code: '',
    api_key: '',
    secret_key: '',
    webhook_url: '',
    status: 'active'
  });

  // Payment Gateway form data
  const [gatewayFormData, setGatewayFormData] = useState({
    gateway_name: '',
    gateway_code: '',
    api_key: '',
    secret_key: '',
    webhook_url: '',
    supported_methods: [],
    status: 'active'
  });

  // Payment methods
  const paymentMethods = [
    { value: 'upi', label: 'UPI', icon: SmartphoneIcon },
    { value: 'neft', label: 'NEFT', icon: ArrowRightLeft },
    { value: 'rtgs', label: 'RTGS', icon: ArrowRightLeft },
    { value: 'card', label: 'Card', icon: CreditCard },
    { value: 'wallet', label: 'Wallet', icon: Wallet },
    { value: 'netbanking', label: 'Net Banking', icon: Globe }
  ];

  // Status options
  const statusOptions = [
    { value: 'active', label: 'Active', color: 'text-green-600', bgColor: 'bg-green-100' },
    { value: 'inactive', label: 'Inactive', color: 'text-gray-600', bgColor: 'bg-gray-100' },
    { value: 'maintenance', label: 'Maintenance', color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
    { value: 'suspended', label: 'Suspended', color: 'text-red-600', bgColor: 'bg-red-100' }
  ];

  // Transaction status options
  const transactionStatusOptions = [
    { value: 'pending', label: 'Pending', color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
    { value: 'success', label: 'Success', color: 'text-green-600', bgColor: 'bg-green-100' },
    { value: 'failed', label: 'Failed', color: 'text-red-600', bgColor: 'bg-red-100' },
    { value: 'cancelled', label: 'Cancelled', color: 'text-gray-600', bgColor: 'bg-gray-100' }
  ];

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const [banksData, upiData, gatewaysData, transactionsData] = await Promise.all([
          localizationService.getIndianBanks(),
          localizationService.getUPIProviders(),
          localizationService.getPaymentGateways(),
          localizationService.getBankingTransactions()
        ]);
        
        setBanks(banksData);
        setUpiProviders(upiData);
        setPaymentGateways(gatewaysData);
        setTransactions(transactionsData);
        setFilteredBanks(banksData);
        setFilteredUpiProviders(upiData);
        setFilteredPaymentGateways(gatewaysData);
        setFilteredTransactions(transactionsData);
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
      case 'banks':
        filtered = banks;
        break;
      case 'upi':
        filtered = upiProviders;
        break;
      case 'gateways':
        filtered = paymentGateways;
        break;
      case 'transactions':
        filtered = transactions;
        break;
      default:
        filtered = [];
    }

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(item =>
        item.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.provider_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.gateway_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.transaction_id?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter(item => item.type === typeFilter);
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(item => item.status === statusFilter);
    }

    switch (activeTab) {
      case 'banks':
        setFilteredBanks(filtered);
        break;
      case 'upi':
        setFilteredUpiProviders(filtered);
        break;
      case 'gateways':
        setFilteredPaymentGateways(filtered);
        break;
      case 'transactions':
        setFilteredTransactions(filtered);
        break;
    }
  }, [banks, upiProviders, paymentGateways, transactions, searchTerm, typeFilter, statusFilter, activeTab]);

  // Handle bank form field changes
  const handleBankFieldChange = (field, value) => {
    setBankFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle UPI form field changes
  const handleUpiFieldChange = (field, value) => {
    setUpiFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle gateway form field changes
  const handleGatewayFieldChange = (field, value) => {
    setGatewayFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle add bank
  const handleAddBank = async () => {
    try {
      setSaving(true);
      await localizationService.createIndianBank(bankFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Indian bank created successfully',
      });
      setShowAddBank(false);
      resetBankForm();
      // Refresh banks
      const banksData = await localizationService.getIndianBanks();
      setBanks(banksData);
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

  // Handle add UPI
  const handleAddUpi = async () => {
    try {
      setSaving(true);
      await localizationService.createUPIProvider(upiFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'UPI provider created successfully',
      });
      setShowAddUpi(false);
      resetUpiForm();
      // Refresh UPI providers
      const upiData = await localizationService.getUPIProviders();
      setUpiProviders(upiData);
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

  // Handle add gateway
  const handleAddGateway = async () => {
    try {
      setSaving(true);
      await localizationService.createPaymentGateway(gatewayFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Payment gateway created successfully',
      });
      setShowAddGateway(false);
      resetGatewayForm();
      // Refresh payment gateways
      const gatewaysData = await localizationService.getPaymentGateways();
      setPaymentGateways(gatewaysData);
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

  // Handle delete bank
  const handleDeleteBank = async (bankId) => {
    if (!window.confirm('Are you sure you want to delete this Indian bank?')) {
      return;
    }

    try {
      await localizationService.deleteIndianBank(bankId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Indian bank deleted successfully',
      });
      // Refresh banks
      const banksData = await localizationService.getIndianBanks();
      setBanks(banksData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle delete UPI
  const handleDeleteUpi = async (upiId) => {
    if (!window.confirm('Are you sure you want to delete this UPI provider?')) {
      return;
    }

    try {
      await localizationService.deleteUPIProvider(upiId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'UPI provider deleted successfully',
      });
      // Refresh UPI providers
      const upiData = await localizationService.getUPIProviders();
      setUpiProviders(upiData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle delete gateway
  const handleDeleteGateway = async (gatewayId) => {
    if (!window.confirm('Are you sure you want to delete this payment gateway?')) {
      return;
    }

    try {
      await localizationService.deletePaymentGateway(gatewayId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Payment gateway deleted successfully',
      });
      // Refresh payment gateways
      const gatewaysData = await localizationService.getPaymentGateways();
      setPaymentGateways(gatewaysData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Reset forms
  const resetBankForm = () => {
    setBankFormData({
      name: '',
      code: '',
      ifsc_code: '',
      micr_code: '',
      branch: '',
      address: '',
      city: '',
      state: '',
      pincode: '',
      phone: '',
      email: '',
      status: 'active'
    });
  };

  const resetUpiForm = () => {
    setUpiFormData({
      provider_name: '',
      provider_code: '',
      api_key: '',
      secret_key: '',
      webhook_url: '',
      status: 'active'
    });
  };

  const resetGatewayForm = () => {
    setGatewayFormData({
      gateway_name: '',
      gateway_code: '',
      api_key: '',
      secret_key: '',
      webhook_url: '',
      supported_methods: [],
      status: 'active'
    });
  };

  // Get status info
  const getStatusInfo = (status) => {
    return statusOptions.find(s => s.value === status) || statusOptions[0];
  };

  // Get transaction status info
  const getTransactionStatusInfo = (status) => {
    return transactionStatusOptions.find(s => s.value === status) || transactionStatusOptions[0];
  };

  // Get payment method info
  const getPaymentMethodInfo = (method) => {
    return paymentMethods.find(m => m.value === method) || paymentMethods[0];
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
        <LoadingSpinner size="lg" text="Loading Indian banking..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Indian Banking</h1>
          <p className="text-gray-600">Manage Indian banks, UPI, and payment gateways</p>
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
              { id: 'banks', name: 'Indian Banks', icon: Building2 },
              { id: 'upi', name: 'UPI Integration', icon: SmartphoneIcon },
              { id: 'gateways', name: 'Payment Gateways', icon: CreditCard },
              { id: 'transactions', name: 'Transactions', icon: ArrowRightLeft }
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
          {/* Banks Tab */}
          {activeTab === 'banks' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search banks..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full"
                  />
                </div>
                <Button
                  onClick={() => setShowAddBank(true)}
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Bank</span>
                </Button>
              </div>

              {/* Banks List */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredBanks.map((bank) => {
                  const statusInfo = getStatusInfo(bank.status);
                  
                  return (
                    <div key={bank.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                            <Building2 className="w-5 h-5 text-blue-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">{bank.name}</h3>
                            <p className="text-sm text-gray-500">{bank.code} • {bank.branch}</p>
                          </div>
                        </div>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                          {statusInfo.label}
                        </span>
                      </div>
                      
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">IFSC:</span>
                          <span className="text-sm font-medium text-gray-900">{bank.ifsc_code}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">MICR:</span>
                          <span className="text-sm font-medium text-gray-900">{bank.micr_code}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">City:</span>
                          <span className="text-sm font-medium text-gray-900">{bank.city}</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setViewingBank(bank)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingBank(bank);
                            setBankFormData(bank);
                            setShowAddBank(true);
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteBank(bank.id)}
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

          {/* UPI Tab */}
          {activeTab === 'upi' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search UPI providers..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full"
                  />
                </div>
                <Button
                  onClick={() => setShowAddUpi(true)}
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add UPI Provider</span>
                </Button>
              </div>

              {/* UPI Providers List */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredUpiProviders.map((upi) => {
                  const statusInfo = getStatusInfo(upi.status);
                  
                  return (
                    <div key={upi.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                            <SmartphoneIcon className="w-5 h-5 text-green-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">{upi.provider_name}</h3>
                            <p className="text-sm text-gray-500">{upi.provider_code}</p>
                          </div>
                        </div>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                          {statusInfo.label}
                        </span>
                      </div>
                      
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">API Key:</span>
                          <span className="text-sm font-medium text-gray-900">{upi.api_key ? 'Configured' : 'Not Set'}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Webhook:</span>
                          <span className="text-sm font-medium text-gray-900">{upi.webhook_url ? 'Configured' : 'Not Set'}</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setViewingUpi(upi)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingUpi(upi);
                            setUpiFormData(upi);
                            setShowAddUpi(true);
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteUpi(upi.id)}
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

          {/* Payment Gateways Tab */}
          {activeTab === 'gateways' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search payment gateways..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full"
                  />
                </div>
                <Button
                  onClick={() => setShowAddGateway(true)}
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Gateway</span>
                </Button>
              </div>

              {/* Payment Gateways List */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredPaymentGateways.map((gateway) => {
                  const statusInfo = getStatusInfo(gateway.status);
                  
                  return (
                    <div key={gateway.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                            <CreditCard className="w-5 h-5 text-purple-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">{gateway.gateway_name}</h3>
                            <p className="text-sm text-gray-500">{gateway.gateway_code}</p>
                          </div>
                        </div>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                          {statusInfo.label}
                        </span>
                      </div>
                      
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Methods:</span>
                          <span className="text-sm font-medium text-gray-900">{gateway.supported_methods?.length || 0}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">API Key:</span>
                          <span className="text-sm font-medium text-gray-900">{gateway.api_key ? 'Configured' : 'Not Set'}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Webhook:</span>
                          <span className="text-sm font-medium text-gray-900">{gateway.webhook_url ? 'Configured' : 'Not Set'}</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setViewingGateway(gateway)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingGateway(gateway);
                            setGatewayFormData(gateway);
                            setShowAddGateway(true);
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteGateway(gateway.id)}
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

          {/* Transactions Tab */}
          {activeTab === 'transactions' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search transactions..."
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
                    {transactionStatusOptions.map(status => (
                      <option key={status.value} value={status.value}>
                        {status.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Transactions List */}
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Transaction ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Method
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Amount
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredTransactions.map((transaction) => {
                      const statusInfo = getTransactionStatusInfo(transaction.status);
                      const methodInfo = getPaymentMethodInfo(transaction.method);
                      const MethodIcon = methodInfo.icon;
                      
                      return (
                        <tr key={transaction.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {transaction.transaction_id}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center space-x-2">
                              <MethodIcon className="w-4 h-4 text-gray-600" />
                              <span className="text-sm text-gray-900">{methodInfo.label}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatCurrency(transaction.amount)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                              {statusInfo.label}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatDate(transaction.created_at)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <div className="flex items-center space-x-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => setViewingTransaction(transaction)}
                              >
                                <Eye className="w-4 h-4" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default IndianBanking;
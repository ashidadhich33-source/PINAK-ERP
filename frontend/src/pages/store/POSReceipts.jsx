import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { storeService } from '../../services/storeService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  Receipt, 
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
  Building,
  Lock,
  Unlock,
  Power,
  Zap as ZapIcon,
  Timer,
  LogIn,
  LogOut,
  Printer,
  Smartphone as SmartphoneIcon,
  Monitor,
  QrCode,
  Image,
  Type,
  AlignLeft,
  AlignCenter,
  AlignRight,
  Bold,
  Italic,
  Underline
} from 'lucide-react';

const POSReceipts = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [receipts, setReceipts] = useState([]);
  const [filteredTemplates, setFilteredTemplates] = useState([]);
  const [filteredReceipts, setFilteredReceipts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showAddTemplate, setShowAddTemplate] = useState(false);
  const [showAddReceipt, setShowAddReceipt] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [editingReceipt, setEditingReceipt] = useState(null);
  const [viewingTemplate, setViewingTemplate] = useState(null);
  const [viewingReceipt, setViewingReceipt] = useState(null);
  const [activeTab, setActiveTab] = useState('templates');

  // Template form data
  const [templateFormData, setTemplateFormData] = useState({
    name: '',
    type: 'thermal',
    width: 80,
    height: 0,
    header_text: '',
    footer_text: '',
    logo_url: '',
    show_logo: true,
    show_qr_code: true,
    show_tax_breakdown: true,
    show_payment_method: true,
    status: 'active'
  });

  // Receipt form data
  const [receiptFormData, setReceiptFormData] = useState({
    template_id: '',
    transaction_id: '',
    customer_name: '',
    customer_email: '',
    customer_phone: '',
    items: [],
    subtotal: 0,
    tax_amount: 0,
    discount_amount: 0,
    total_amount: 0,
    payment_method: 'cash',
    status: 'pending'
  });

  // Receipt types
  const receiptTypes = [
    { value: 'thermal', label: 'Thermal Receipt', icon: Printer },
    { value: 'standard', label: 'Standard Receipt', icon: Receipt },
    { value: 'digital', label: 'Digital Receipt', icon: SmartphoneIcon },
    { value: 'email', label: 'Email Receipt', icon: Mail }
  ];

  // Payment methods
  const paymentMethods = [
    { value: 'cash', label: 'Cash', icon: DollarSign },
    { value: 'card', label: 'Card', icon: CreditCard },
    { value: 'upi', label: 'UPI', icon: SmartphoneIcon },
    { value: 'wallet', label: 'Wallet', icon: Wallet },
    { value: 'netbanking', label: 'Net Banking', icon: Globe }
  ];

  // Status options
  const statusOptions = [
    { value: 'active', label: 'Active', color: 'text-green-600', bgColor: 'bg-green-100' },
    { value: 'inactive', label: 'Inactive', color: 'text-gray-600', bgColor: 'bg-gray-100' },
    { value: 'draft', label: 'Draft', color: 'text-yellow-600', bgColor: 'bg-yellow-100' }
  ];

  // Receipt status options
  const receiptStatusOptions = [
    { value: 'pending', label: 'Pending', color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
    { value: 'sent', label: 'Sent', color: 'text-green-600', bgColor: 'bg-green-100' },
    { value: 'failed', label: 'Failed', color: 'text-red-600', bgColor: 'bg-red-100' }
  ];

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const [templatesData, receiptsData] = await Promise.all([
          storeService.getReceiptTemplates(),
          storeService.getReceipts()
        ]);
        
        setTemplates(templatesData);
        setReceipts(receiptsData);
        setFilteredTemplates(templatesData);
        setFilteredReceipts(receiptsData);
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
      case 'templates':
        filtered = templates;
        break;
      case 'receipts':
        filtered = receipts;
        break;
      default:
        filtered = [];
    }

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(item =>
        item.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.template_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.transaction_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.customer_name?.toLowerCase().includes(searchTerm.toLowerCase())
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
      case 'templates':
        setFilteredTemplates(filtered);
        break;
      case 'receipts':
        setFilteredReceipts(filtered);
        break;
    }
  }, [templates, receipts, searchTerm, typeFilter, statusFilter, activeTab]);

  // Handle template form field changes
  const handleTemplateFieldChange = (field, value) => {
    setTemplateFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle receipt form field changes
  const handleReceiptFieldChange = (field, value) => {
    setReceiptFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle add template
  const handleAddTemplate = async () => {
    try {
      setSaving(true);
      await storeService.createReceiptTemplate(templateFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Receipt template created successfully',
      });
      setShowAddTemplate(false);
      resetTemplateForm();
      // Refresh templates
      const templatesData = await storeService.getReceiptTemplates();
      setTemplates(templatesData);
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

  // Handle add receipt
  const handleAddReceipt = async () => {
    try {
      setSaving(true);
      await storeService.createReceipt(receiptFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Receipt created successfully',
      });
      setShowAddReceipt(false);
      resetReceiptForm();
      // Refresh receipts
      const receiptsData = await storeService.getReceipts();
      setReceipts(receiptsData);
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

  // Handle delete template
  const handleDeleteTemplate = async (templateId) => {
    if (!window.confirm('Are you sure you want to delete this receipt template?')) {
      return;
    }

    try {
      await storeService.deleteReceiptTemplate(templateId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Receipt template deleted successfully',
      });
      // Refresh templates
      const templatesData = await storeService.getReceiptTemplates();
      setTemplates(templatesData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle delete receipt
  const handleDeleteReceipt = async (receiptId) => {
    if (!window.confirm('Are you sure you want to delete this receipt?')) {
      return;
    }

    try {
      await storeService.deleteReceipt(receiptId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Receipt deleted successfully',
      });
      // Refresh receipts
      const receiptsData = await storeService.getReceipts();
      setReceipts(receiptsData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle print receipt
  const handlePrintReceipt = async (receiptId) => {
    try {
      await storeService.printReceipt(receiptId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Receipt sent to printer',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle send receipt
  const handleSendReceipt = async (receiptId) => {
    try {
      await storeService.sendReceipt(receiptId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Receipt sent successfully',
      });
      // Refresh receipts
      const receiptsData = await storeService.getReceipts();
      setReceipts(receiptsData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Reset forms
  const resetTemplateForm = () => {
    setTemplateFormData({
      name: '',
      type: 'thermal',
      width: 80,
      height: 0,
      header_text: '',
      footer_text: '',
      logo_url: '',
      show_logo: true,
      show_qr_code: true,
      show_tax_breakdown: true,
      show_payment_method: true,
      status: 'active'
    });
  };

  const resetReceiptForm = () => {
    setReceiptFormData({
      template_id: '',
      transaction_id: '',
      customer_name: '',
      customer_email: '',
      customer_phone: '',
      items: [],
      subtotal: 0,
      tax_amount: 0,
      discount_amount: 0,
      total_amount: 0,
      payment_method: 'cash',
      status: 'pending'
    });
  };

  // Get status info
  const getStatusInfo = (status) => {
    return statusOptions.find(s => s.value === status) || statusOptions[0];
  };

  // Get receipt status info
  const getReceiptStatusInfo = (status) => {
    return receiptStatusOptions.find(s => s.value === status) || receiptStatusOptions[0];
  };

  // Get type info
  const getTypeInfo = (type) => {
    return receiptTypes.find(t => t.value === type) || receiptTypes[0];
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
        <LoadingSpinner size="lg" text="Loading POS receipts..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">POS Receipts</h1>
          <p className="text-gray-600">Manage receipt templates and digital receipts</p>
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
              { id: 'templates', name: 'Receipt Templates', icon: Type },
              { id: 'receipts', name: 'Digital Receipts', icon: Receipt },
              { id: 'printing', name: 'Receipt Printing', icon: Printer },
              { id: 'analytics', name: 'Receipt Analytics', icon: BarChart3 }
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
          {/* Templates Tab */}
          {activeTab === 'templates' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search templates..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full"
                  />
                </div>
                <div className="w-48">
                  <select
                    value={typeFilter}
                    onChange={(e) => setTypeFilter(e.target.value)}
                    className="form-input"
                  >
                    <option value="all">All Types</option>
                    {receiptTypes.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>
                <Button
                  onClick={() => setShowAddTemplate(true)}
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Template</span>
                </Button>
              </div>

              {/* Templates List */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredTemplates.map((template) => {
                  const statusInfo = getStatusInfo(template.status);
                  const typeInfo = getTypeInfo(template.type);
                  const TypeIcon = typeInfo.icon;
                  
                  return (
                    <div key={template.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                            <TypeIcon className="w-5 h-5 text-blue-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">{template.name}</h3>
                            <p className="text-sm text-gray-500">{typeInfo.label}</p>
                          </div>
                        </div>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                          {statusInfo.label}
                        </span>
                      </div>
                      
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Width:</span>
                          <span className="text-sm font-medium text-gray-900">{template.width}mm</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Logo:</span>
                          <span className="text-sm font-medium text-gray-900">{template.show_logo ? 'Yes' : 'No'}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">QR Code:</span>
                          <span className="text-sm font-medium text-gray-900">{template.show_qr_code ? 'Yes' : 'No'}</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setViewingTemplate(template)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingTemplate(template);
                            setTemplateFormData(template);
                            setShowAddTemplate(true);
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteTemplate(template.id)}
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

          {/* Receipts Tab */}
          {activeTab === 'receipts' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search receipts..."
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
                    {receiptStatusOptions.map(status => (
                      <option key={status.value} value={status.value}>
                        {status.label}
                      </option>
                    ))}
                  </select>
                </div>
                <Button
                  onClick={() => setShowAddReceipt(true)}
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Receipt</span>
                </Button>
              </div>

              {/* Receipts List */}
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Receipt ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Customer
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Amount
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Payment Method
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
                    {filteredReceipts.map((receipt) => {
                      const statusInfo = getReceiptStatusInfo(receipt.status);
                      const paymentMethodInfo = getPaymentMethodInfo(receipt.payment_method);
                      const PaymentIcon = paymentMethodInfo.icon;
                      
                      return (
                        <tr key={receipt.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {receipt.receipt_id}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                                <User className="w-4 h-4 text-gray-600" />
                              </div>
                              <div className="ml-3">
                                <div className="text-sm font-medium text-gray-900">{receipt.customer_name}</div>
                                <div className="text-sm text-gray-500">{receipt.customer_email}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatCurrency(receipt.total_amount)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center space-x-2">
                              <PaymentIcon className="w-4 h-4 text-gray-600" />
                              <span className="text-sm text-gray-900">{paymentMethodInfo.label}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                              {statusInfo.label}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatDate(receipt.created_at)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <div className="flex items-center space-x-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => setViewingReceipt(receipt)}
                              >
                                <Eye className="w-4 h-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handlePrintReceipt(receipt.id)}
                              >
                                <Printer className="w-4 h-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleSendReceipt(receipt.id)}
                              >
                                <Send className="w-4 h-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleDeleteReceipt(receipt.id)}
                                className="text-danger-600 hover:text-danger-700"
                              >
                                <Trash2 className="w-4 h-4" />
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

          {/* Receipt Printing Tab */}
          {activeTab === 'printing' && (
            <div className="space-y-6">
              <div className="text-center py-12">
                <Printer className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Receipt Printing</h3>
                <p className="text-gray-500">Thermal printer integration will be implemented here</p>
              </div>
            </div>
          )}

          {/* Receipt Analytics Tab */}
          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <div className="text-center py-12">
                <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Receipt Analytics</h3>
                <p className="text-gray-500">Receipt usage analytics will be implemented here</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Add/Edit Template Modal */}
      {showAddTemplate && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowAddTemplate(false)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Type className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {editingTemplate ? 'Edit Receipt Template' : 'Add New Receipt Template'}
                      </h3>
                      <p className="text-sm text-gray-500">Create or update receipt template</p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setShowAddTemplate(false);
                      setEditingTemplate(null);
                      resetTemplateForm();
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
                        Template Name *
                      </label>
                      <Input
                        value={templateFormData.name}
                        onChange={(e) => handleTemplateFieldChange('name', e.target.value)}
                        placeholder="Enter template name"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Template Type *
                      </label>
                      <select
                        value={templateFormData.type}
                        onChange={(e) => handleTemplateFieldChange('type', e.target.value)}
                        className="form-input"
                        required
                      >
                        {receiptTypes.map(type => (
                          <option key={type.value} value={type.value}>
                            {type.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Width (mm)
                      </label>
                      <Input
                        type="number"
                        value={templateFormData.width}
                        onChange={(e) => handleTemplateFieldChange('width', parseFloat(e.target.value) || 0)}
                        placeholder="Enter width"
                        min="0"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Height (mm)
                      </label>
                      <Input
                        type="number"
                        value={templateFormData.height}
                        onChange={(e) => handleTemplateFieldChange('height', parseFloat(e.target.value) || 0)}
                        placeholder="Enter height"
                        min="0"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Header Text
                    </label>
                    <textarea
                      value={templateFormData.header_text}
                      onChange={(e) => handleTemplateFieldChange('header_text', e.target.value)}
                      rows={3}
                      className="form-input"
                      placeholder="Enter header text"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Footer Text
                    </label>
                    <textarea
                      value={templateFormData.footer_text}
                      onChange={(e) => handleTemplateFieldChange('footer_text', e.target.value)}
                      rows={3}
                      className="form-input"
                      placeholder="Enter footer text"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Logo URL
                    </label>
                    <Input
                      value={templateFormData.logo_url}
                      onChange={(e) => handleTemplateFieldChange('logo_url', e.target.value)}
                      placeholder="Enter logo URL"
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        checked={templateFormData.show_logo}
                        onChange={(e) => handleTemplateFieldChange('show_logo', e.target.checked)}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <label className="ml-2 block text-sm text-gray-900">
                        Show Logo
                      </label>
                    </div>
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        checked={templateFormData.show_qr_code}
                        onChange={(e) => handleTemplateFieldChange('show_qr_code', e.target.checked)}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <label className="ml-2 block text-sm text-gray-900">
                        Show QR Code
                      </label>
                    </div>
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        checked={templateFormData.show_tax_breakdown}
                        onChange={(e) => handleTemplateFieldChange('show_tax_breakdown', e.target.checked)}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <label className="ml-2 block text-sm text-gray-900">
                        Show Tax Breakdown
                      </label>
                    </div>
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        checked={templateFormData.show_payment_method}
                        onChange={(e) => handleTemplateFieldChange('show_payment_method', e.target.checked)}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <label className="ml-2 block text-sm text-gray-900">
                        Show Payment Method
                      </label>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Status
                    </label>
                    <select
                      value={templateFormData.status}
                      onChange={(e) => handleTemplateFieldChange('status', e.target.value)}
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
                  onClick={editingTemplate ? handleEditTemplate : handleAddTemplate}
                  loading={saving}
                  className="w-full sm:w-auto sm:ml-3"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {editingTemplate ? 'Update Template' : 'Create Template'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowAddTemplate(false);
                    setEditingTemplate(null);
                    resetTemplateForm();
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

export default POSReceipts;
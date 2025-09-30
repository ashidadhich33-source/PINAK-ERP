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
  Zap,
  ArrowUp,
  ArrowDown,
  Minus,
  CreditCard,
  ShoppingCart,
  User,
  FileText,
  BarChart3
} from 'lucide-react';

const LoyaltyTransactions = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [filteredTransactions, setFilteredTransactions] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState('all');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState(null);
  const [viewingTransaction, setViewingTransaction] = useState(null);
  const [activeTab, setActiveTab] = useState('transactions');

  // Form data
  const [formData, setFormData] = useState({
    customer_id: '',
    program_id: '',
    type: 'earn',
    points: 0,
    amount: 0,
    description: '',
    reference: '',
    status: 'completed'
  });

  // Transaction types
  const transactionTypes = [
    { value: 'earn', label: 'Earn Points', icon: ArrowUp, color: 'text-green-600', bgColor: 'bg-green-100' },
    { value: 'redeem', label: 'Redeem Points', icon: ArrowDown, color: 'text-red-600', bgColor: 'bg-red-100' },
    { value: 'expire', label: 'Points Expired', icon: Clock, color: 'text-orange-600', bgColor: 'bg-orange-100' },
    { value: 'adjust', label: 'Points Adjustment', icon: Settings, color: 'text-blue-600', bgColor: 'bg-blue-100' }
  ];

  // Transaction statuses
  const transactionStatuses = [
    { value: 'completed', label: 'Completed', color: 'text-green-600', bgColor: 'bg-green-100' },
    { value: 'pending', label: 'Pending', color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
    { value: 'failed', label: 'Failed', color: 'text-red-600', bgColor: 'bg-red-100' },
    { value: 'cancelled', label: 'Cancelled', color: 'text-gray-600', bgColor: 'bg-gray-100' }
  ];

  // Date filter options
  const dateFilterOptions = [
    { value: 'all', label: 'All Time' },
    { value: 'today', label: 'Today' },
    { value: 'week', label: 'This Week' },
    { value: 'month', label: 'This Month' },
    { value: 'quarter', label: 'This Quarter' },
    { value: 'year', label: 'This Year' }
  ];

  // Fetch transactions
  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const transactionsData = await loyaltyService.getLoyaltyTransactions();
        setTransactions(transactionsData);
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

    fetchTransactions();
  }, []);

  // Filter transactions
  useEffect(() => {
    let filtered = transactions;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(transaction =>
        transaction.customer_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        transaction.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        transaction.reference?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter(transaction => transaction.type === typeFilter);
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(transaction => transaction.status === statusFilter);
    }

    // Date filter
    if (dateFilter !== 'all') {
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      
      filtered = filtered.filter(transaction => {
        const transactionDate = new Date(transaction.created_at);
        
        switch (dateFilter) {
          case 'today':
            return transactionDate >= today;
          case 'week':
            const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
            return transactionDate >= weekAgo;
          case 'month':
            const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
            return transactionDate >= monthAgo;
          case 'quarter':
            const quarterAgo = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000);
            return transactionDate >= quarterAgo;
          case 'year':
            const yearAgo = new Date(today.getTime() - 365 * 24 * 60 * 60 * 1000);
            return transactionDate >= yearAgo;
          default:
            return true;
        }
      });
    }

    setFilteredTransactions(filtered);
  }, [transactions, searchTerm, typeFilter, statusFilter, dateFilter]);

  // Handle form field changes
  const handleFieldChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle add transaction
  const handleAddTransaction = async () => {
    try {
      setSaving(true);
      await loyaltyService.createLoyaltyTransaction(formData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Loyalty transaction created successfully',
      });
      setShowAddForm(false);
      resetForm();
      // Refresh transactions
      const transactionsData = await loyaltyService.getLoyaltyTransactions();
      setTransactions(transactionsData);
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

  // Handle edit transaction
  const handleEditTransaction = async () => {
    try {
      setSaving(true);
      await loyaltyService.updateLoyaltyTransaction(editingTransaction.id, formData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Loyalty transaction updated successfully',
      });
      setEditingTransaction(null);
      setShowAddForm(false);
      resetForm();
      // Refresh transactions
      const transactionsData = await loyaltyService.getLoyaltyTransactions();
      setTransactions(transactionsData);
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

  // Handle delete transaction
  const handleDeleteTransaction = async (transactionId) => {
    if (!window.confirm('Are you sure you want to delete this loyalty transaction?')) {
      return;
    }

    try {
      await loyaltyService.deleteLoyaltyTransaction(transactionId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Loyalty transaction deleted successfully',
      });
      // Refresh transactions
      const transactionsData = await loyaltyService.getLoyaltyTransactions();
      setTransactions(transactionsData);
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
      customer_id: '',
      program_id: '',
      type: 'earn',
      points: 0,
      amount: 0,
      description: '',
      reference: '',
      status: 'completed'
    });
  };

  // Get transaction type info
  const getTransactionTypeInfo = (type) => {
    return transactionTypes.find(t => t.value === type) || transactionTypes[0];
  };

  // Get transaction status info
  const getTransactionStatusInfo = (status) => {
    return transactionStatuses.find(s => s.value === status) || transactionStatuses[0];
  };

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading loyalty transactions..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Loyalty Transactions</h1>
          <p className="text-gray-600">Track and manage loyalty points transactions</p>
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
            <span>Add Transaction</span>
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
              { id: 'transactions', name: 'Transactions', icon: FileText },
              { id: 'points', name: 'Points Tracking', icon: Star },
              { id: 'redemption', name: 'Redemption', icon: Gift },
              { id: 'analytics', name: 'Analytics', icon: BarChart3 }
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
          {/* Transactions Tab */}
          {activeTab === 'transactions' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <div className="md:col-span-2">
                  <Input
                    placeholder="Search transactions..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full"
                  />
                </div>
                <div>
                  <select
                    value={typeFilter}
                    onChange={(e) => setTypeFilter(e.target.value)}
                    className="form-input"
                  >
                    <option value="all">All Types</option>
                    {transactionTypes.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="form-input"
                  >
                    <option value="all">All Status</option>
                    {transactionStatuses.map(status => (
                      <option key={status.value} value={status.value}>
                        {status.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <select
                    value={dateFilter}
                    onChange={(e) => setDateFilter(e.target.value)}
                    className="form-input"
                  >
                    {dateFilterOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
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
                        Customer
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Points
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
                      const typeInfo = getTransactionTypeInfo(transaction.type);
                      const statusInfo = getTransactionStatusInfo(transaction.status);
                      const TypeIcon = typeInfo.icon;
                      
                      return (
                        <tr key={transaction.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                                <User className="w-4 h-4 text-gray-600" />
                              </div>
                              <div className="ml-3">
                                <div className="text-sm font-medium text-gray-900">
                                  {transaction.customer_name || 'Unknown Customer'}
                                </div>
                                <div className="text-sm text-gray-500">
                                  {transaction.customer_email || 'No email'}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center space-x-2">
                              <TypeIcon className={`w-4 h-4 ${typeInfo.color}`} />
                              <span className={`text-sm font-medium ${typeInfo.color}`}>
                                {typeInfo.label}
                              </span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            <span className={`font-medium ${transaction.type === 'earn' ? 'text-green-600' : 'text-red-600'}`}>
                              {transaction.type === 'earn' ? '+' : '-'}{transaction.points}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {transaction.amount ? formatCurrency(transaction.amount) : '-'}
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
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => {
                                  setEditingTransaction(transaction);
                                  setFormData(transaction);
                                  setShowAddForm(true);
                                }}
                              >
                                <Edit className="w-4 h-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleDeleteTransaction(transaction.id)}
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

          {/* Points Tracking Tab */}
          {activeTab === 'points' && (
            <div className="space-y-6">
              <div className="text-center py-12">
                <Star className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Points Tracking</h3>
                <p className="text-gray-500">Customer points history will be implemented here</p>
              </div>
            </div>
          )}

          {/* Redemption Tab */}
          {activeTab === 'redemption' && (
            <div className="space-y-6">
              <div className="text-center py-12">
                <Gift className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Redemption Processing</h3>
                <p className="text-gray-500">Points redemption workflow will be implemented here</p>
              </div>
            </div>
          )}

          {/* Analytics Tab */}
          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <div className="text-center py-12">
                <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Loyalty Analytics</h3>
                <p className="text-gray-500">Loyalty program analytics will be implemented here</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Add/Edit Transaction Modal */}
      {showAddForm && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowAddForm(false)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {editingTransaction ? 'Edit Loyalty Transaction' : 'Add New Loyalty Transaction'}
                      </h3>
                      <p className="text-sm text-gray-500">Create or update loyalty transaction</p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setShowAddForm(false);
                      setEditingTransaction(null);
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
                        Customer *
                      </label>
                      <Input
                        value={formData.customer_id}
                        onChange={(e) => handleFieldChange('customer_id', e.target.value)}
                        placeholder="Select customer"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Program *
                      </label>
                      <Input
                        value={formData.program_id}
                        onChange={(e) => handleFieldChange('program_id', e.target.value)}
                        placeholder="Select program"
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Transaction Type *
                      </label>
                      <select
                        value={formData.type}
                        onChange={(e) => handleFieldChange('type', e.target.value)}
                        className="form-input"
                        required
                      >
                        {transactionTypes.map(type => (
                          <option key={type.value} value={type.value}>
                            {type.label}
                          </option>
                        ))}
                      </select>
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
                        {transactionStatuses.map(status => (
                          <option key={status.value} value={status.value}>
                            {status.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Points *
                      </label>
                      <Input
                        type="number"
                        value={formData.points}
                        onChange={(e) => handleFieldChange('points', parseFloat(e.target.value) || 0)}
                        placeholder="Enter points"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Amount
                      </label>
                      <Input
                        type="number"
                        value={formData.amount}
                        onChange={(e) => handleFieldChange('amount', parseFloat(e.target.value) || 0)}
                        placeholder="Enter amount"
                        step="0.01"
                      />
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
                      placeholder="Enter transaction description"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Reference
                    </label>
                    <Input
                      value={formData.reference}
                      onChange={(e) => handleFieldChange('reference', e.target.value)}
                      placeholder="Enter reference number"
                    />
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <Button
                  onClick={editingTransaction ? handleEditTransaction : handleAddTransaction}
                  loading={saving}
                  className="w-full sm:w-auto sm:ml-3"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {editingTransaction ? 'Update Transaction' : 'Create Transaction'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowAddForm(false);
                    setEditingTransaction(null);
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

      {/* View Transaction Modal */}
      {viewingTransaction && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setViewingTransaction(null)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">Transaction Details</h3>
                      <p className="text-sm text-gray-500">View transaction information</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setViewingTransaction(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Customer</p>
                      <p className="text-sm font-medium text-gray-900">{viewingTransaction.customer_name || 'Unknown'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Type</p>
                      <p className="text-sm font-medium text-gray-900">{getTransactionTypeInfo(viewingTransaction.type).label}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Points</p>
                      <p className="text-sm font-medium text-gray-900">{viewingTransaction.points}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Status</p>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getTransactionStatusInfo(viewingTransaction.status).bgColor} ${getTransactionStatusInfo(viewingTransaction.status).color}`}>
                        {getTransactionStatusInfo(viewingTransaction.status).label}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Amount</p>
                      <p className="text-sm font-medium text-gray-900">
                        {viewingTransaction.amount ? formatCurrency(viewingTransaction.amount) : 'N/A'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Date</p>
                      <p className="text-sm font-medium text-gray-900">{formatDate(viewingTransaction.created_at)}</p>
                    </div>
                  </div>
                  
                  {viewingTransaction.description && (
                    <div>
                      <p className="text-sm text-gray-500">Description</p>
                      <p className="text-sm text-gray-900">{viewingTransaction.description}</p>
                    </div>
                  )}
                  
                  {viewingTransaction.reference && (
                    <div>
                      <p className="text-sm text-gray-500">Reference</p>
                      <p className="text-sm text-gray-900">{viewingTransaction.reference}</p>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <Button
                  onClick={() => setViewingTransaction(null)}
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

export default LoyaltyTransactions;
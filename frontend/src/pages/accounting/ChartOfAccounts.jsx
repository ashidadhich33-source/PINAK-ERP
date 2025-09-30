import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { accountingService } from '../../services/accountingService';
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
  Upload, 
  RefreshCw, 
  Save, 
  X,
  ChevronRight,
  ChevronDown,
  Building2,
  CreditCard,
  DollarSign,
  TrendingUp,
  TrendingDown,
  Wallet,
  PiggyBank,
  BarChart3,
  CheckCircle,
  AlertTriangle,
  Info
} from 'lucide-react';

const ChartOfAccounts = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [filteredAccounts, setFilteredAccounts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingAccount, setEditingAccount] = useState(null);
  const [expandedAccounts, setExpandedAccounts] = useState(new Set());

  // Form data
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    category: '',
    parent_id: null,
    account_type: '',
    description: '',
    is_active: true,
    opening_balance: 0,
    balance_type: 'debit'
  });

  // Account categories
  const accountCategories = [
    {
      id: 'assets',
      name: 'Assets',
      icon: Building2,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      description: 'Resources owned by the company'
    },
    {
      id: 'liabilities',
      name: 'Liabilities',
      icon: CreditCard,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
      description: 'Debts and obligations'
    },
    {
      id: 'equity',
      name: 'Equity',
      icon: DollarSign,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      description: 'Owner\'s equity and capital'
    },
    {
      id: 'income',
      name: 'Income',
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
      description: 'Revenue and income sources'
    },
    {
      id: 'expenses',
      name: 'Expenses',
      icon: TrendingDown,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
      description: 'Business expenses and costs'
    }
  ];

  // Account types
  const accountTypes = [
    { value: 'current_asset', label: 'Current Asset' },
    { value: 'fixed_asset', label: 'Fixed Asset' },
    { value: 'intangible_asset', label: 'Intangible Asset' },
    { value: 'current_liability', label: 'Current Liability' },
    { value: 'long_term_liability', label: 'Long-term Liability' },
    { value: 'owner_equity', label: 'Owner\'s Equity' },
    { value: 'retained_earnings', label: 'Retained Earnings' },
    { value: 'revenue', label: 'Revenue' },
    { value: 'other_income', label: 'Other Income' },
    { value: 'operating_expense', label: 'Operating Expense' },
    { value: 'administrative_expense', label: 'Administrative Expense' },
    { value: 'financial_expense', label: 'Financial Expense' }
  ];

  // Fetch accounts
  useEffect(() => {
    const fetchAccounts = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const accountsData = await accountingService.getChartOfAccounts();
        setAccounts(accountsData);
        setFilteredAccounts(accountsData);
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

    fetchAccounts();
  }, []);

  // Filter accounts
  useEffect(() => {
    let filtered = accounts;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(account =>
        account.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        account.code.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(account => account.category === selectedCategory);
    }

    setFilteredAccounts(filtered);
  }, [accounts, searchTerm, selectedCategory]);

  // Handle form field changes
  const handleFieldChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle add account
  const handleAddAccount = async () => {
    try {
      setSaving(true);
      await accountingService.createAccount(formData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Account created successfully',
      });
      setShowAddForm(false);
      setFormData({
        code: '',
        name: '',
        category: '',
        parent_id: null,
        account_type: '',
        description: '',
        is_active: true,
        opening_balance: 0,
        balance_type: 'debit'
      });
      // Refresh accounts
      const accountsData = await accountingService.getChartOfAccounts();
      setAccounts(accountsData);
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

  // Handle edit account
  const handleEditAccount = async () => {
    try {
      setSaving(true);
      await accountingService.updateAccount(editingAccount.id, formData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Account updated successfully',
      });
      setEditingAccount(null);
      setFormData({
        code: '',
        name: '',
        category: '',
        parent_id: null,
        account_type: '',
        description: '',
        is_active: true,
        opening_balance: 0,
        balance_type: 'debit'
      });
      // Refresh accounts
      const accountsData = await accountingService.getChartOfAccounts();
      setAccounts(accountsData);
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

  // Handle delete account
  const handleDeleteAccount = async (accountId) => {
    if (!window.confirm('Are you sure you want to delete this account?')) {
      return;
    }

    try {
      await accountingService.deleteAccount(accountId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Account deleted successfully',
      });
      // Refresh accounts
      const accountsData = await accountingService.getChartOfAccounts();
      setAccounts(accountsData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle toggle account expansion
  const toggleAccountExpansion = (accountId) => {
    const newExpanded = new Set(expandedAccounts);
    if (newExpanded.has(accountId)) {
      newExpanded.delete(accountId);
    } else {
      newExpanded.add(accountId);
    }
    setExpandedAccounts(newExpanded);
  };

  // Get account icon
  const getAccountIcon = (category) => {
    const categoryData = accountCategories.find(cat => cat.id === category);
    return categoryData ? categoryData.icon : Calculator;
  };

  // Get account color
  const getAccountColor = (category) => {
    const categoryData = accountCategories.find(cat => cat.id === category);
    return categoryData ? categoryData.color : 'text-gray-600';
  };

  // Get account background color
  const getAccountBgColor = (category) => {
    const categoryData = accountCategories.find(cat => cat.id === category);
    return categoryData ? categoryData.bgColor : 'bg-gray-100';
  };

  // Render account tree
  const renderAccountTree = (accounts, parentId = null, level = 0) => {
    const childAccounts = accounts.filter(account => account.parent_id === parentId);
    
    return childAccounts.map(account => {
      const hasChildren = accounts.some(child => child.parent_id === account.id);
      const isExpanded = expandedAccounts.has(account.id);
      const Icon = getAccountIcon(account.category);
      
      return (
        <div key={account.id} className="space-y-1">
          <div 
            className={`flex items-center space-x-3 p-3 rounded-lg border ${
              account.is_active ? 'bg-white border-gray-200' : 'bg-gray-50 border-gray-100'
            }`}
            style={{ marginLeft: `${level * 20}px` }}
          >
            {hasChildren ? (
              <button
                onClick={() => toggleAccountExpansion(account.id)}
                className="p-1 hover:bg-gray-100 rounded"
              >
                {isExpanded ? (
                  <ChevronDown className="w-4 h-4 text-gray-500" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-gray-500" />
                )}
              </button>
            ) : (
              <div className="w-6"></div>
            )}
            
            <div className={`w-8 h-8 rounded-full ${getAccountBgColor(account.category)} flex items-center justify-center`}>
              <Icon className={`w-4 h-4 ${getAccountColor(account.category)}`} />
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2">
                <p className="text-sm font-medium text-gray-900">{account.name}</p>
                <span className="text-xs text-gray-500">({account.code})</span>
                {!account.is_active && (
                  <span className="text-xs text-gray-400">(Inactive)</span>
                )}
              </div>
              <p className="text-xs text-gray-500">{account.description}</p>
            </div>
            
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-gray-900">
                ₹{account.current_balance?.toLocaleString() || '0.00'}
              </span>
              <div className="flex items-center space-x-1">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setEditingAccount(account);
                    setFormData(account);
                    setShowAddForm(true);
                  }}
                >
                  <Edit className="w-4 h-4" />
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleDeleteAccount(account.id)}
                  className="text-danger-600 hover:text-danger-700"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
          
          {hasChildren && isExpanded && (
            <div className="ml-4">
              {renderAccountTree(accounts, account.id, level + 1)}
            </div>
          )}
        </div>
      );
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading chart of accounts..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Chart of Accounts</h1>
          <p className="text-gray-600">Manage your accounting accounts and categories</p>
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
            <span>Add Account</span>
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert type="danger" title="Error">
          {error}
        </Alert>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <Input
              placeholder="Search accounts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full"
            />
          </div>
          <div className="w-48">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="form-input"
            >
              <option value="all">All Categories</option>
              {accountCategories.map(category => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Account Categories Summary */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {accountCategories.map(category => {
          const Icon = category.icon;
          const categoryAccounts = accounts.filter(account => account.category === category.id);
          const totalBalance = categoryAccounts.reduce((sum, account) => sum + (account.current_balance || 0), 0);
          
          return (
            <div key={category.id} className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center space-x-3 mb-3">
                <div className={`w-10 h-10 rounded-full ${category.bgColor} flex items-center justify-center`}>
                  <Icon className={`w-5 h-5 ${category.color}`} />
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-900">{category.name}</h3>
                  <p className="text-xs text-gray-500">{categoryAccounts.length} accounts</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-lg font-bold text-gray-900">₹{totalBalance.toLocaleString()}</p>
                <p className="text-xs text-gray-500">Total Balance</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Accounts List */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Accounts List</h2>
          <p className="text-sm text-gray-500">Manage your chart of accounts</p>
        </div>
        
        <div className="p-6">
          {filteredAccounts.length === 0 ? (
            <div className="text-center py-8">
              <Calculator className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No accounts found</p>
              <p className="text-sm text-gray-400">Create your first account to get started</p>
            </div>
          ) : (
            <div className="space-y-2">
              {renderAccountTree(filteredAccounts)}
            </div>
          )}
        </div>
      </div>

      {/* Add/Edit Account Modal */}
      {showAddForm && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowAddForm(false)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Calculator className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {editingAccount ? 'Edit Account' : 'Add New Account'}
                      </h3>
                      <p className="text-sm text-gray-500">Create or update account information</p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setShowAddForm(false);
                      setEditingAccount(null);
                      setFormData({
                        code: '',
                        name: '',
                        category: '',
                        parent_id: null,
                        account_type: '',
                        description: '',
                        is_active: true,
                        opening_balance: 0,
                        balance_type: 'debit'
                      });
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
                        Account Code *
                      </label>
                      <Input
                        value={formData.code}
                        onChange={(e) => handleFieldChange('code', e.target.value)}
                        placeholder="e.g., 1001"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Account Name *
                      </label>
                      <Input
                        value={formData.name}
                        onChange={(e) => handleFieldChange('name', e.target.value)}
                        placeholder="e.g., Cash in Hand"
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Category *
                      </label>
                      <select
                        value={formData.category}
                        onChange={(e) => handleFieldChange('category', e.target.value)}
                        className="form-input"
                        required
                      >
                        <option value="">Select Category</option>
                        {accountCategories.map(category => (
                          <option key={category.id} value={category.id}>
                            {category.name}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Account Type *
                      </label>
                      <select
                        value={formData.account_type}
                        onChange={(e) => handleFieldChange('account_type', e.target.value)}
                        className="form-input"
                        required
                      >
                        <option value="">Select Type</option>
                        {accountTypes.map(type => (
                          <option key={type.value} value={type.value}>
                            {type.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Parent Account
                    </label>
                    <select
                      value={formData.parent_id || ''}
                      onChange={(e) => handleFieldChange('parent_id', e.target.value || null)}
                      className="form-input"
                    >
                      <option value="">No Parent Account</option>
                      {accounts.map(account => (
                        <option key={account.id} value={account.id}>
                          {account.code} - {account.name}
                        </option>
                      ))}
                    </select>
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
                      placeholder="Account description..."
                    />
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Opening Balance
                      </label>
                      <Input
                        type="number"
                        value={formData.opening_balance}
                        onChange={(e) => handleFieldChange('opening_balance', parseFloat(e.target.value) || 0)}
                        placeholder="0.00"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Balance Type
                      </label>
                      <select
                        value={formData.balance_type}
                        onChange={(e) => handleFieldChange('balance_type', e.target.value)}
                        className="form-input"
                      >
                        <option value="debit">Debit</option>
                        <option value="credit">Credit</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="is_active"
                      checked={formData.is_active}
                      onChange={(e) => handleFieldChange('is_active', e.target.checked)}
                      className="form-checkbox"
                    />
                    <label htmlFor="is_active" className="text-sm text-gray-700">
                      Account is active
                    </label>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <Button
                  onClick={editingAccount ? handleEditAccount : handleAddAccount}
                  loading={saving}
                  className="w-full sm:w-auto sm:ml-3"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {editingAccount ? 'Update Account' : 'Create Account'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowAddForm(false);
                    setEditingAccount(null);
                    setFormData({
                      code: '',
                      name: '',
                      category: '',
                      parent_id: null,
                      account_type: '',
                      description: '',
                      is_active: true,
                      opening_balance: 0,
                      balance_type: 'debit'
                    });
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

export default ChartOfAccounts;
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import { accountingService } from '../../services/accountingService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import DataTable from '../../components/common/DataTable';
import { 
  Plus, 
  Search, 
  Download, 
  Upload,
  BookOpen,
  Eye,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  DollarSign,
  Filter,
  TreePine,
  Calculator
} from 'lucide-react';

const ChartOfAccounts = () => {
  const { addNotification } = useApp();
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    accountType: 'all',
    isActive: 'all',
    sortBy: 'account_code',
    sortOrder: 'asc',
  });

  // Fetch chart of accounts
  const fetchAccounts = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        search: searchTerm,
        account_type: filters.accountType !== 'all' ? filters.accountType : undefined,
        is_active: filters.isActive !== 'all' ? filters.isActive === 'active' : undefined,
        sort_by: filters.sortBy,
        sort_order: filters.sortOrder,
      };
      
      const data = await accountingService.getChartOfAccounts(params);
      setAccounts(data);
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
    fetchAccounts();
  }, [searchTerm, filters]);

  // Handle search
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  // Handle filter change
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Handle delete account
  const handleDelete = async (accountId) => {
    if (!window.confirm('Are you sure you want to delete this account?')) {
      return;
    }

    try {
      await accountingService.deleteChartOfAccount(accountId);
      setAccounts(prev => prev.filter(account => account.id !== accountId));
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Account deleted successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle toggle active status
  const handleToggleActive = async (accountId, currentStatus) => {
    try {
      const account = await accountingService.getChartOfAccount(accountId);
      await accountingService.updateChartOfAccount(accountId, {
        ...account,
        is_active: !currentStatus
      });
      setAccounts(prev => prev.map(account => 
        account.id === accountId 
          ? { ...account, is_active: !currentStatus }
          : account
      ));
      addNotification({
        type: 'success',
        title: 'Success',
        message: `Account ${!currentStatus ? 'activated' : 'deactivated'} successfully`,
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle export
  const handleExport = async () => {
    try {
      await accountingService.exportAccountingData('csv', 'chart_of_accounts', filters);
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: 'Chart of accounts export will be downloaded shortly',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Get account type color
  const getAccountTypeColor = (type) => {
    switch (type) {
      case 'asset':
        return 'text-blue-600 bg-blue-100';
      case 'liability':
        return 'text-red-600 bg-red-100';
      case 'equity':
        return 'text-green-600 bg-green-100';
      case 'income':
        return 'text-purple-600 bg-purple-100';
      case 'expense':
        return 'text-orange-600 bg-orange-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  // Table columns
  const columns = [
    {
      key: 'account_code',
      label: 'Account Code',
      render: (account) => (
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <BookOpen className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <p className="font-medium text-gray-900">{account.account_code}</p>
            <p className="text-sm text-gray-500">{account.account_name}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'account_type',
      label: 'Type',
      render: (account) => (
        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getAccountTypeColor(account.account_type)}`}>
          {account.account_type}
        </span>
      ),
    },
    {
      key: 'parent_account',
      label: 'Parent Account',
      render: (account) => (
        <div>
          <p className="text-sm text-gray-900">{account.parent_account?.account_name || '-'}</p>
          <p className="text-xs text-gray-500">{account.parent_account?.account_code || ''}</p>
        </div>
      ),
    },
    {
      key: 'balance',
      label: 'Balance',
      render: (account) => (
        <div className="text-right">
          <p className="font-medium text-gray-900">₹{account.current_balance || 0}</p>
          <p className="text-xs text-gray-500">
            {account.account_type === 'asset' || account.account_type === 'expense' ? 'Debit' : 'Credit'}
          </p>
        </div>
      ),
    },
    {
      key: 'is_active',
      label: 'Status',
      render: (account) => (
        <div className="flex items-center space-x-2">
          {account.is_active ? (
            <CheckCircle className="w-4 h-4 text-success-500" />
          ) : (
            <XCircle className="w-4 h-4 text-danger-500" />
          )}
          <span className="text-sm text-gray-900">
            {account.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>
      ),
    },
    {
      key: 'description',
      label: 'Description',
      render: (account) => (
        <div className="max-w-xs">
          <p className="text-sm text-gray-900 truncate">{account.description || '-'}</p>
        </div>
      ),
    },
    {
      key: 'created_at',
      label: 'Created',
      render: (account) => new Date(account.created_at).toLocaleDateString(),
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (account) => (
        <div className="flex items-center space-x-2">
          <Link
            to={`/accounting/chart-of-accounts/${account.id}`}
            className="text-primary-600 hover:text-primary-900"
          >
            <Eye className="w-4 h-4" />
          </Link>
          <Link
            to={`/accounting/chart-of-accounts/${account.id}/edit`}
            className="text-secondary-600 hover:text-secondary-900"
          >
            <Edit className="w-4 h-4" />
          </Link>
          <button
            onClick={() => handleToggleActive(account.id, account.is_active)}
            className={account.is_active ? "text-warning-600 hover:text-warning-900" : "text-success-600 hover:text-success-900"}
            title={account.is_active ? "Deactivate" : "Activate"}
          >
            {account.is_active ? <XCircle className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />}
          </button>
          <button
            onClick={() => handleDelete(account.id)}
            className="text-danger-600 hover:text-danger-900"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      ),
    },
  ];

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
          <p className="text-gray-600">Manage your accounting chart of accounts</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={handleExport}
            className="flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Export</span>
          </Button>
          <Button
            variant="outline"
            className="flex items-center space-x-2"
          >
            <Upload className="w-4 h-4" />
            <span>Import</span>
          </Button>
          <Link to="/accounting/chart-of-accounts/new">
            <Button className="flex items-center space-x-2">
              <Plus className="w-4 h-4" />
              <span>New Account</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="md:col-span-2">
            <div className="relative">
              <Input
                placeholder="Search accounts..."
                value={searchTerm}
                onChange={handleSearch}
                className="pl-10"
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
            </div>
          </div>
          
          <div>
            <select
              value={filters.accountType}
              onChange={(e) => handleFilterChange('accountType', e.target.value)}
              className="form-input"
            >
              <option value="all">All Types</option>
              <option value="asset">Asset</option>
              <option value="liability">Liability</option>
              <option value="equity">Equity</option>
              <option value="income">Income</option>
              <option value="expense">Expense</option>
            </select>
          </div>
          
          <div>
            <select
              value={filters.isActive}
              onChange={(e) => handleFilterChange('isActive', e.target.value)}
              className="form-input"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
          
          <div>
            <select
              value={filters.sortBy}
              onChange={(e) => handleFilterChange('sortBy', e.target.value)}
              className="form-input"
            >
              <option value="account_code">Sort by Code</option>
              <option value="account_name">Sort by Name</option>
              <option value="account_type">Sort by Type</option>
              <option value="current_balance">Sort by Balance</option>
            </select>
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert type="danger" title="Error">
          {error}
        </Alert>
      )}

      {/* Data Table */}
      <div className="bg-white rounded-lg shadow">
        <DataTable
          data={accounts}
          columns={columns}
          loading={loading}
          emptyMessage="No accounts found"
        />
      </div>
    </div>
  );
};

export default ChartOfAccounts;
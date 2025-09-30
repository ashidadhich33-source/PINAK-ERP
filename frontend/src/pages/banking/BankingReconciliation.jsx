import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import { bankingService } from '../../services/bankingService';
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
  Building2,
  Eye,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  Clock,
  DollarSign,
  Filter,
  Calendar,
  CreditCard,
  FileText,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Settings,
  Target
} from 'lucide-react';

const BankingReconciliation = () => {
  const { addNotification } = useApp();
  const [activeTab, setActiveTab] = useState('bank-accounts');
  const [bankAccounts, setBankAccounts] = useState([]);
  const [bankStatements, setBankStatements] = useState([]);
  const [reconciliations, setReconciliations] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    status: 'all',
    dateRange: 'all',
    sortBy: 'created_at',
    sortOrder: 'desc',
  });

  // Fetch data based on active tab
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        search: searchTerm,
        status: filters.status !== 'all' ? filters.status : undefined,
        date_range: filters.dateRange !== 'all' ? filters.dateRange : undefined,
        sort_by: filters.sortBy,
        sort_order: filters.sortOrder,
      };
      
      let data;
      switch (activeTab) {
        case 'bank-accounts':
          data = await bankingService.getBankAccounts(params);
          setBankAccounts(data);
          break;
        case 'bank-statements':
          data = await bankingService.getBankStatements(params);
          setBankStatements(data);
          break;
        case 'reconciliations':
          data = await bankingService.getReconciliations(params);
          setReconciliations(data);
          break;
        case 'payment-methods':
          data = await bankingService.getPaymentMethods(params);
          setPaymentMethods(data);
          break;
        default:
          break;
      }
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
    fetchData();
  }, [activeTab, searchTerm, filters]);

  // Handle search
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  // Handle filter change
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Handle delete
  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this item?')) {
      return;
    }

    try {
      switch (activeTab) {
        case 'bank-accounts':
          await bankingService.deleteBankAccount(id);
          setBankAccounts(prev => prev.filter(item => item.id !== id));
          break;
        case 'bank-statements':
          await bankingService.deleteBankStatement(id);
          setBankStatements(prev => prev.filter(item => item.id !== id));
          break;
        case 'reconciliations':
          await bankingService.deleteReconciliation(id);
          setReconciliations(prev => prev.filter(item => item.id !== id));
          break;
        case 'payment-methods':
          await bankingService.deletePaymentMethod(id);
          setPaymentMethods(prev => prev.filter(item => item.id !== id));
          break;
        default:
          break;
      }
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Item deleted successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle auto reconcile
  const handleAutoReconcile = async (reconciliationId) => {
    try {
      await bankingService.autoReconcile(reconciliationId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Auto reconciliation completed',
      });
      fetchData();
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
      await bankingService.exportBankingData('csv', activeTab, filters);
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: 'Data export will be downloaded shortly',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Get current data based on active tab
  const getCurrentData = () => {
    switch (activeTab) {
      case 'bank-accounts':
        return bankAccounts;
      case 'bank-statements':
        return bankStatements;
      case 'reconciliations':
        return reconciliations;
      case 'payment-methods':
        return paymentMethods;
      default:
        return [];
    }
  };

  // Get columns based on active tab
  const getColumns = () => {
    switch (activeTab) {
      case 'bank-accounts':
        return [
          {
            key: 'account_name',
            label: 'Account Name',
            render: (account) => (
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <Building2 className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{account.account_name}</p>
                  <p className="text-sm text-gray-500">{account.bank_name}</p>
                </div>
              </div>
            ),
          },
          {
            key: 'account_number',
            label: 'Account Number',
            render: (account) => (
              <div>
                <p className="font-medium text-gray-900">{account.account_number}</p>
                <p className="text-sm text-gray-500">{account.ifsc_code}</p>
              </div>
            ),
          },
          {
            key: 'account_type',
            label: 'Type',
            render: (account) => (
              <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                {account.account_type}
              </span>
            ),
          },
          {
            key: 'balance',
            label: 'Balance',
            render: (account) => (
              <div className="text-right">
                <p className="font-medium text-gray-900">₹{account.current_balance || 0}</p>
                <p className="text-sm text-gray-500">{account.currency}</p>
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
            key: 'actions',
            label: 'Actions',
            render: (account) => (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/banking/accounts/${account.id}`}
                  className="text-primary-600 hover:text-primary-900"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                <Link
                  to={`/banking/accounts/${account.id}/edit`}
                  className="text-secondary-600 hover:text-secondary-900"
                >
                  <Edit className="w-4 h-4" />
                </Link>
                <Link
                  to={`/banking/accounts/${account.id}/statements`}
                  className="text-blue-600 hover:text-blue-900"
                  title="View Statements"
                >
                  <FileText className="w-4 h-4" />
                </Link>
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
      case 'bank-statements':
        return [
          {
            key: 'statement_info',
            label: 'Statement',
            render: (statement) => (
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <FileText className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{statement.statement_name}</p>
                  <p className="text-sm text-gray-500">{statement.bank_account?.account_name}</p>
                </div>
              </div>
            ),
          },
          {
            key: 'statement_date',
            label: 'Statement Date',
            render: (statement) => (
              <div>
                <p className="font-medium text-gray-900">
                  {new Date(statement.statement_date).toLocaleDateString()}
                </p>
                <p className="text-sm text-gray-500">
                  {new Date(statement.created_at).toLocaleDateString()}
                </p>
              </div>
            ),
          },
          {
            key: 'balance',
            label: 'Balance',
            render: (statement) => (
              <div className="text-right">
                <p className="font-medium text-gray-900">₹{statement.opening_balance || 0}</p>
                <p className="text-sm text-gray-500">to ₹{statement.closing_balance || 0}</p>
              </div>
            ),
          },
          {
            key: 'transactions',
            label: 'Transactions',
            render: (statement) => (
              <div className="text-center">
                <p className="font-medium text-gray-900">{statement.transaction_count || 0}</p>
                <p className="text-sm text-gray-500">transactions</p>
              </div>
            ),
          },
          {
            key: 'status',
            label: 'Status',
            render: (statement) => {
              const statusInfo = {
                imported: { icon: CheckCircle, color: 'text-success-600', bgColor: 'bg-success-100' },
                processing: { icon: Clock, color: 'text-warning-600', bgColor: 'bg-warning-100' },
                error: { icon: XCircle, color: 'text-danger-600', bgColor: 'bg-danger-100' },
              }[statement.status] || { icon: Clock, color: 'text-gray-600', bgColor: 'bg-gray-100' };
              
              const Icon = statusInfo.icon;
              return (
                <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                  <Icon className="w-3 h-3 mr-1" />
                  {statement.status}
                </span>
              );
            },
          },
          {
            key: 'actions',
            label: 'Actions',
            render: (statement) => (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/banking/statements/${statement.id}`}
                  className="text-primary-600 hover:text-primary-900"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                <Link
                  to={`/banking/statements/${statement.id}/edit`}
                  className="text-secondary-600 hover:text-secondary-900"
                >
                  <Edit className="w-4 h-4" />
                </Link>
                <button
                  onClick={() => handleDelete(statement.id)}
                  className="text-danger-600 hover:text-danger-900"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ),
          },
        ];
      case 'reconciliations':
        return [
          {
            key: 'reconciliation_info',
            label: 'Reconciliation',
            render: (reconciliation) => (
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <Target className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{reconciliation.reconciliation_name}</p>
                  <p className="text-sm text-gray-500">{reconciliation.bank_account?.account_name}</p>
                </div>
              </div>
            ),
          },
          {
            key: 'reconciliation_date',
            label: 'Date',
            render: (reconciliation) => (
              <div>
                <p className="font-medium text-gray-900">
                  {new Date(reconciliation.reconciliation_date).toLocaleDateString()}
                </p>
                <p className="text-sm text-gray-500">
                  {new Date(reconciliation.created_at).toLocaleDateString()}
                </p>
              </div>
            ),
          },
          {
            key: 'balance',
            label: 'Balance',
            render: (reconciliation) => (
              <div className="text-right">
                <p className="font-medium text-gray-900">₹{reconciliation.statement_balance || 0}</p>
                <p className="text-sm text-gray-500">vs ₹{reconciliation.book_balance || 0}</p>
              </div>
            ),
          },
          {
            key: 'difference',
            label: 'Difference',
            render: (reconciliation) => {
              const difference = (reconciliation.statement_balance || 0) - (reconciliation.book_balance || 0);
              return (
                <div className="text-right">
                  <p className={`font-medium ${difference === 0 ? 'text-success-600' : 'text-danger-600'}`}>
                    ₹{Math.abs(difference)}
                  </p>
                  <p className="text-sm text-gray-500">
                    {difference === 0 ? 'Balanced' : difference > 0 ? 'Over' : 'Under'}
                  </p>
                </div>
              );
            },
          },
          {
            key: 'status',
            label: 'Status',
            render: (reconciliation) => {
              const statusInfo = {
                balanced: { icon: CheckCircle, color: 'text-success-600', bgColor: 'bg-success-100' },
                unbalanced: { icon: XCircle, color: 'text-danger-600', bgColor: 'bg-danger-100' },
                in_progress: { icon: Clock, color: 'text-warning-600', bgColor: 'bg-warning-100' },
              }[reconciliation.status] || { icon: Clock, color: 'text-gray-600', bgColor: 'bg-gray-100' };
              
              const Icon = statusInfo.icon;
              return (
                <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                  <Icon className="w-3 h-3 mr-1" />
                  {reconciliation.status}
                </span>
              );
            },
          },
          {
            key: 'actions',
            label: 'Actions',
            render: (reconciliation) => (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/banking/reconciliations/${reconciliation.id}`}
                  className="text-primary-600 hover:text-primary-900"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                <Link
                  to={`/banking/reconciliations/${reconciliation.id}/edit`}
                  className="text-secondary-600 hover:text-secondary-900"
                >
                  <Edit className="w-4 h-4" />
                </Link>
                {reconciliation.status === 'unbalanced' && (
                  <button
                    onClick={() => handleAutoReconcile(reconciliation.id)}
                    className="text-blue-600 hover:text-blue-900"
                    title="Auto Reconcile"
                  >
                    <RefreshCw className="w-4 h-4" />
                  </button>
                )}
                <button
                  onClick={() => handleDelete(reconciliation.id)}
                  className="text-danger-600 hover:text-danger-900"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ),
          },
        ];
      case 'payment-methods':
        return [
          {
            key: 'method_name',
            label: 'Payment Method',
            render: (method) => (
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <CreditCard className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{method.method_name}</p>
                  <p className="text-sm text-gray-500">{method.method_code}</p>
                </div>
              </div>
            ),
          },
          {
            key: 'method_type',
            label: 'Type',
            render: (method) => (
              <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                {method.method_type}
              </span>
            ),
          },
          {
            key: 'bank_account',
            label: 'Bank Account',
            render: (method) => (
              <div>
                <p className="font-medium text-gray-900">{method.bank_account?.account_name || '-'}</p>
                <p className="text-sm text-gray-500">{method.bank_account?.account_number || ''}</p>
              </div>
            ),
          },
          {
            key: 'is_active',
            label: 'Status',
            render: (method) => (
              <div className="flex items-center space-x-2">
                {method.is_active ? (
                  <CheckCircle className="w-4 h-4 text-success-500" />
                ) : (
                  <XCircle className="w-4 h-4 text-danger-500" />
                )}
                <span className="text-sm text-gray-900">
                  {method.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            ),
          },
          {
            key: 'actions',
            label: 'Actions',
            render: (method) => (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/banking/payment-methods/${method.id}`}
                  className="text-primary-600 hover:text-primary-900"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                <Link
                  to={`/banking/payment-methods/${method.id}/edit`}
                  className="text-secondary-600 hover:text-secondary-900"
                >
                  <Edit className="w-4 h-4" />
                </Link>
                <button
                  onClick={() => handleDelete(method.id)}
                  className="text-danger-600 hover:text-danger-900"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ),
          },
        ];
      default:
        return [];
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading banking data..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Banking & Reconciliation</h1>
          <p className="text-gray-600">Manage bank accounts, statements, and reconciliation</p>
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
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {[
              { id: 'bank-accounts', name: 'Bank Accounts', icon: Building2 },
              { id: 'bank-statements', name: 'Bank Statements', icon: FileText },
              { id: 'reconciliations', name: 'Reconciliations', icon: Target },
              { id: 'payment-methods', name: 'Payment Methods', icon: CreditCard },
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {/* Filters and Search */}
          <div className="mb-6">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div className="md:col-span-2">
                <div className="relative">
                  <Input
                    placeholder="Search..."
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
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  className="form-input"
                >
                  <option value="all">All Status</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="balanced">Balanced</option>
                  <option value="unbalanced">Unbalanced</option>
                </select>
              </div>
              
              <div>
                <select
                  value={filters.dateRange}
                  onChange={(e) => handleFilterChange('dateRange', e.target.value)}
                  className="form-input"
                >
                  <option value="all">All Dates</option>
                  <option value="today">Today</option>
                  <option value="week">This Week</option>
                  <option value="month">This Month</option>
                </select>
              </div>
              
              <div>
                <select
                  value={filters.sortBy}
                  onChange={(e) => handleFilterChange('sortBy', e.target.value)}
                  className="form-input"
                >
                  <option value="created_at">Sort by Date</option>
                  <option value="name">Sort by Name</option>
                  <option value="status">Sort by Status</option>
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
          <DataTable
            data={getCurrentData()}
            columns={getColumns()}
            loading={loading}
            emptyMessage="No data found"
          />
        </div>
      </div>
    </div>
  );
};

export default BankingReconciliation;
import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { accountingService } from '../../services/accountingService';
import Button from '../../components/common/Button';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import DataTable from '../../components/common/DataTable';
import { 
  Download, 
  RefreshCw,
  Calculator,
  CheckCircle,
  XCircle,
  DollarSign,
  Calendar,
  FileText,
  TrendingUp,
  TrendingDown
} from 'lucide-react';

const TrialBalance = () => {
  const { addNotification } = useApp();
  const [trialBalance, setTrialBalance] = useState(null);
  const [trialBalanceItems, setTrialBalanceItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    balanceDate: new Date().toISOString().split('T')[0],
    financialYearId: null,
  });

  // Fetch trial balance
  const fetchTrialBalance = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        balance_date: filters.balanceDate,
        financial_year_id: filters.financialYearId,
      };
      
      const data = await accountingService.getTrialBalance(params);
      setTrialBalance(data);
      setTrialBalanceItems(data.balance_items || []);
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

  // Generate trial balance
  const generateTrialBalance = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = {
        balance_date: filters.balanceDate,
        financial_year_id: filters.financialYearId,
      };
      
      const result = await accountingService.generateTrialBalance(data);
      setTrialBalance(result);
      setTrialBalanceItems(result.balance_items || []);
      
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Trial balance generated successfully',
      });
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
    fetchTrialBalance();
  }, [filters.balanceDate, filters.financialYearId]);

  // Handle filter change
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Handle export
  const handleExport = async () => {
    try {
      await accountingService.exportAccountingData('pdf', 'trial_balance', {
        balance_date: filters.balanceDate,
        financial_year_id: filters.financialYearId,
      });
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: 'Trial balance export will be downloaded shortly',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Table columns
  const columns = [
    {
      key: 'account_code',
      label: 'Account Code',
      render: (item) => (
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
            <Calculator className="w-4 h-4 text-primary-600" />
          </div>
          <div>
            <p className="font-medium text-gray-900">{item.account.account_code}</p>
            <p className="text-sm text-gray-500">{item.account.account_name}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'account_type',
      label: 'Type',
      render: (item) => (
        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
          item.account.account_type === 'asset' ? 'text-blue-600 bg-blue-100' :
          item.account.account_type === 'liability' ? 'text-red-600 bg-red-100' :
          item.account.account_type === 'equity' ? 'text-green-600 bg-green-100' :
          item.account.account_type === 'income' ? 'text-purple-600 bg-purple-100' :
          'text-orange-600 bg-orange-100'
        }`}>
          {item.account.account_type}
        </span>
      ),
    },
    {
      key: 'debit_balance',
      label: 'Debit Balance',
      render: (item) => (
        <div className="text-right">
          <p className="font-medium text-gray-900">₹{item.debit_balance || 0}</p>
        </div>
      ),
    },
    {
      key: 'credit_balance',
      label: 'Credit Balance',
      render: (item) => (
        <div className="text-right">
          <p className="font-medium text-gray-900">₹{item.credit_balance || 0}</p>
        </div>
      ),
    },
    {
      key: 'net_balance',
      label: 'Net Balance',
      render: (item) => {
        const netBalance = (item.debit_balance || 0) - (item.credit_balance || 0);
        return (
          <div className="text-right">
            <p className={`font-medium ${netBalance > 0 ? 'text-blue-600' : netBalance < 0 ? 'text-red-600' : 'text-gray-600'}`}>
              ₹{Math.abs(netBalance)}
            </p>
            <p className="text-xs text-gray-500">
              {netBalance > 0 ? 'Debit' : netBalance < 0 ? 'Credit' : 'Zero'}
            </p>
          </div>
        );
      },
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading trial balance..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Trial Balance</h1>
          <p className="text-gray-600">View and generate trial balance report</p>
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
            onClick={generateTrialBalance}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Generate</span>
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Balance Date
            </label>
            <input
              type="date"
              value={filters.balanceDate}
              onChange={(e) => handleFilterChange('balanceDate', e.target.value)}
              className="form-input"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Financial Year
            </label>
            <select
              value={filters.financialYearId || ''}
              onChange={(e) => handleFilterChange('financialYearId', e.target.value || null)}
              className="form-input"
            >
              <option value="">Select Financial Year</option>
              {/* Add financial year options here */}
            </select>
          </div>
          
          <div className="flex items-end">
            <Button
              onClick={fetchTrialBalance}
              variant="outline"
              className="w-full flex items-center justify-center space-x-2"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Trial Balance Summary */}
      {trialBalance && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-100 rounded-md flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Debit</p>
                <p className="text-2xl font-semibold text-gray-900">₹{trialBalance.total_debit || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-red-100 rounded-md flex items-center justify-center">
                  <TrendingDown className="w-5 h-5 text-red-600" />
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Credit</p>
                <p className="text-2xl font-semibold text-gray-900">₹{trialBalance.total_credit || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className={`w-8 h-8 rounded-md flex items-center justify-center ${
                  trialBalance.is_balanced ? 'bg-green-100' : 'bg-red-100'
                }`}>
                  {trialBalance.is_balanced ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-600" />
                  )}
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Status</p>
                <p className={`text-lg font-semibold ${
                  trialBalance.is_balanced ? 'text-green-600' : 'text-red-600'
                }`}>
                  {trialBalance.is_balanced ? 'Balanced' : 'Not Balanced'}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <Alert type="danger" title="Error">
          {error}
        </Alert>
      )}

      {/* Trial Balance Items */}
      {trialBalanceItems.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Trial Balance Items</h3>
          </div>
          <DataTable
            data={trialBalanceItems}
            columns={columns}
            loading={loading}
            emptyMessage="No trial balance items found"
          />
        </div>
      )}

      {/* Empty State */}
      {!trialBalance && !loading && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Calculator className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Trial Balance</h3>
          <p className="text-gray-500 mb-6">
            Generate a trial balance to view your account balances.
          </p>
          <Button onClick={generateTrialBalance} className="flex items-center space-x-2 mx-auto">
            <RefreshCw className="w-4 h-4" />
            <span>Generate Trial Balance</span>
          </Button>
        </div>
      )}
    </div>
  );
};

export default TrialBalance;
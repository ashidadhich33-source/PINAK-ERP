import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { accountingService } from '../../services/accountingService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  BookOpen, 
  Search, 
  Filter, 
  Download, 
  RefreshCw, 
  Calendar,
  Calculator,
  TrendingUp,
  TrendingDown,
  DollarSign,
  FileText,
  Eye,
  BarChart3,
  PieChart,
  Activity
} from 'lucide-react';

const GeneralLedger = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [ledgerData, setLedgerData] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('table'); // table, chart

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const [ledger, accountsData] = await Promise.all([
          accountingService.getGeneralLedger({
            account_id: selectedAccount,
            date_from: dateFrom,
            date_to: dateTo
          }),
          accountingService.getChartOfAccounts()
        ]);
        
        setLedgerData(ledger);
        setAccounts(accountsData);
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
  }, [selectedAccount, dateFrom, dateTo]);

  // Handle search
  const handleSearch = async () => {
    try {
      setLoading(true);
      const ledger = await accountingService.getGeneralLedger({
        account_id: selectedAccount,
        date_from: dateFrom,
        date_to: dateTo,
        search: searchTerm
      });
      setLedgerData(ledger);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setLoading(false);
    }
  };

  // Handle export
  const handleExport = async () => {
    try {
      await accountingService.exportGeneralLedger({
        account_id: selectedAccount,
        date_from: dateFrom,
        date_to: dateTo
      });
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: 'General ledger export will be downloaded shortly',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
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

  // Calculate running balance
  const calculateRunningBalance = (entries) => {
    let runningBalance = 0;
    return entries.map(entry => {
      if (entry.account_type === 'debit') {
        runningBalance += entry.amount;
      } else {
        runningBalance -= entry.amount;
      }
      return {
        ...entry,
        running_balance: runningBalance
      };
    });
  };

  // Get account summary
  const getAccountSummary = () => {
    if (!ledgerData.length) return null;
    
    const totalDebit = ledgerData.reduce((sum, entry) => sum + (entry.debit || 0), 0);
    const totalCredit = ledgerData.reduce((sum, entry) => sum + (entry.credit || 0), 0);
    const openingBalance = ledgerData[0]?.opening_balance || 0;
    const closingBalance = ledgerData[ledgerData.length - 1]?.running_balance || 0;
    
    return {
      openingBalance,
      totalDebit,
      totalCredit,
      closingBalance
    };
  };

  const summary = getAccountSummary();
  const entriesWithBalance = calculateRunningBalance(ledgerData);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading general ledger..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">General Ledger</h1>
          <p className="text-gray-600">View detailed account transactions and balances</p>
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
            variant="outline"
            onClick={handleExport}
            className="flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Export</span>
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
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Account
            </label>
            <select
              value={selectedAccount}
              onChange={(e) => setSelectedAccount(e.target.value)}
              className="form-input"
            >
              <option value="">All Accounts</option>
              {accounts.map(account => (
                <option key={account.id} value={account.id}>
                  {account.code} - {account.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Date From
            </label>
            <Input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Date To
            </label>
            <Input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
            />
          </div>
          <div className="flex items-end">
            <Button
              onClick={handleSearch}
              className="w-full flex items-center justify-center space-x-2"
            >
              <Search className="w-4 h-4" />
              <span>Search</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Account Summary */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <DollarSign className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Opening Balance</p>
                <p className="text-lg font-semibold text-gray-900">{formatCurrency(summary.openingBalance)}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Debit</p>
                <p className="text-lg font-semibold text-gray-900">{formatCurrency(summary.totalDebit)}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <TrendingDown className="w-5 h-5 text-red-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Credit</p>
                <p className="text-lg font-semibold text-gray-900">{formatCurrency(summary.totalCredit)}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                <Calculator className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Closing Balance</p>
                <p className="text-lg font-semibold text-gray-900">{formatCurrency(summary.closingBalance)}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* View Mode Toggle */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-700">View Mode:</span>
            <div className="flex items-center space-x-1">
              <Button
                size="sm"
                variant={viewMode === 'table' ? 'primary' : 'outline'}
                onClick={() => setViewMode('table')}
                className="flex items-center space-x-1"
              >
                <FileText className="w-4 h-4" />
                <span>Table</span>
              </Button>
              <Button
                size="sm"
                variant={viewMode === 'chart' ? 'primary' : 'outline'}
                onClick={() => setViewMode('chart')}
                className="flex items-center space-x-1"
              >
                <BarChart3 className="w-4 h-4" />
                <span>Chart</span>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Ledger Data */}
      {viewMode === 'table' ? (
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">General Ledger</h2>
            <p className="text-sm text-gray-500">Detailed transaction history</p>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Reference
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Debit
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Credit
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Balance
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {entriesWithBalance.map((entry, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(entry.date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {entry.reference}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {entry.description}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {entry.debit ? formatCurrency(entry.debit) : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {entry.credit ? formatCurrency(entry.credit) : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {formatCurrency(entry.running_balance)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-medium text-gray-900">Ledger Chart</h2>
            <div className="flex items-center space-x-2">
              <Button
                size="sm"
                variant="outline"
                className="flex items-center space-x-1"
              >
                <BarChart3 className="w-4 h-4" />
                <span>Bar Chart</span>
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="flex items-center space-x-1"
              >
                <PieChart className="w-4 h-4" />
                <span>Pie Chart</span>
              </Button>
            </div>
          </div>
          
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="text-center">
              <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Chart visualization will be implemented here</p>
              <p className="text-sm text-gray-400">This will show transaction trends and patterns</p>
            </div>
          </div>
        </div>
      )}

      {/* No Data State */}
      {ledgerData.length === 0 && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Transactions Found</h3>
          <p className="text-gray-500">No transactions found for the selected criteria.</p>
          <p className="text-sm text-gray-400 mt-2">Try adjusting your search filters.</p>
        </div>
      )}
    </div>
  );
};

export default GeneralLedger;
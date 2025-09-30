import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { accountingService } from '../../services/accountingService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  BarChart3, 
  Download, 
  RefreshCw, 
  Calendar,
  TrendingUp,
  TrendingDown,
  DollarSign,
  FileText,
  PieChart,
  Activity,
  Calculator,
  Eye,
  Print,
  Share2
} from 'lucide-react';

const FinancialReports = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedReport, setSelectedReport] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [reportData, setReportData] = useState(null);
  const [showReport, setShowReport] = useState(false);

  // Report types
  const reportTypes = [
    {
      id: 'trial_balance',
      name: 'Trial Balance',
      icon: Calculator,
      description: 'Summary of all account balances',
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      id: 'profit_loss',
      name: 'Profit & Loss Statement',
      icon: TrendingUp,
      description: 'Revenue and expense summary',
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      id: 'balance_sheet',
      name: 'Balance Sheet',
      icon: BarChart3,
      description: 'Assets, liabilities, and equity',
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      id: 'cash_flow',
      name: 'Cash Flow Statement',
      icon: Activity,
      description: 'Cash inflows and outflows',
      color: 'text-orange-600',
      bgColor: 'bg-orange-100'
    }
  ];

  // Set default dates
  useEffect(() => {
    const today = new Date();
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
    const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);
    
    setDateFrom(firstDay.toISOString().split('T')[0]);
    setDateTo(lastDay.toISOString().split('T')[0]);
  }, []);

  // Handle report generation
  const handleGenerateReport = async () => {
    if (!selectedReport) {
      addNotification({
        type: 'warning',
        title: 'Warning',
        message: 'Please select a report type',
      });
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      let data;
      const params = {
        date_from: dateFrom,
        date_to: dateTo
      };

      switch (selectedReport) {
        case 'trial_balance':
          data = await accountingService.getTrialBalance(params);
          break;
        case 'profit_loss':
          data = await accountingService.getProfitAndLoss(params);
          break;
        case 'balance_sheet':
          data = await accountingService.getBalanceSheet(params);
          break;
        case 'cash_flow':
          data = await accountingService.getCashFlow(params);
          break;
        default:
          throw new Error('Invalid report type');
      }
      
      setReportData(data);
      setShowReport(true);
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

  // Handle export report
  const handleExportReport = async () => {
    if (!selectedReport) return;

    try {
      await accountingService.exportTrialBalance({
        date_from: dateFrom,
        date_to: dateTo
      });
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: 'Report export will be downloaded shortly',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
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

  // Render trial balance
  const renderTrialBalance = (data) => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Trial Balance</h2>
            <p className="text-sm text-gray-500">
              {formatDate(dateFrom)} to {formatDate(dateTo)}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              onClick={handleExportReport}
              className="flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Export</span>
            </Button>
            <Button
              variant="outline"
              className="flex items-center space-x-2"
            >
              <Print className="w-4 h-4" />
              <span>Print</span>
            </Button>
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Account
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Debit
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Credit
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.accounts?.map((account, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {account.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {account.debit ? formatCurrency(account.debit) : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {account.credit ? formatCurrency(account.credit) : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot className="bg-gray-50">
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Total
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {formatCurrency(data.total_debit)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {formatCurrency(data.total_credit)}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  );

  // Render profit and loss
  const renderProfitLoss = (data) => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Profit & Loss Statement</h2>
            <p className="text-sm text-gray-500">
              {formatDate(dateFrom)} to {formatDate(dateTo)}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              onClick={handleExportReport}
              className="flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Export</span>
            </Button>
            <Button
              variant="outline"
              className="flex items-center space-x-2"
            >
              <Print className="w-4 h-4" />
              <span>Print</span>
            </Button>
          </div>
        </div>
        
        <div className="space-y-4">
          {/* Revenue Section */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Revenue</h3>
            <div className="space-y-2">
              {data.revenue?.map((item, index) => (
                <div key={index} className="flex items-center justify-between py-2">
                  <span className="text-sm text-gray-900">{item.name}</span>
                  <span className="text-sm font-medium text-gray-900">{formatCurrency(item.amount)}</span>
                </div>
              ))}
            </div>
            <div className="border-t border-gray-200 pt-2 mt-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-900">Total Revenue</span>
                <span className="text-sm font-bold text-gray-900">{formatCurrency(data.total_revenue)}</span>
              </div>
            </div>
          </div>

          {/* Expenses Section */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Expenses</h3>
            <div className="space-y-2">
              {data.expenses?.map((item, index) => (
                <div key={index} className="flex items-center justify-between py-2">
                  <span className="text-sm text-gray-900">{item.name}</span>
                  <span className="text-sm font-medium text-gray-900">{formatCurrency(item.amount)}</span>
                </div>
              ))}
            </div>
            <div className="border-t border-gray-200 pt-2 mt-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-900">Total Expenses</span>
                <span className="text-sm font-bold text-gray-900">{formatCurrency(data.total_expenses)}</span>
              </div>
            </div>
          </div>

          {/* Net Profit/Loss */}
          <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <div className="flex items-center justify-between">
              <span className="text-lg font-medium text-gray-900">Net Profit/Loss</span>
              <span className={`text-lg font-bold ${data.net_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(data.net_profit)}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Render balance sheet
  const renderBalanceSheet = (data) => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Balance Sheet</h2>
            <p className="text-sm text-gray-500">
              As of {formatDate(dateTo)}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              onClick={handleExportReport}
              className="flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Export</span>
            </Button>
            <Button
              variant="outline"
              className="flex items-center space-x-2"
            >
              <Print className="w-4 h-4" />
              <span>Print</span>
            </Button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Assets */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Assets</h3>
            <div className="space-y-2">
              {data.assets?.map((item, index) => (
                <div key={index} className="flex items-center justify-between py-2">
                  <span className="text-sm text-gray-900">{item.name}</span>
                  <span className="text-sm font-medium text-gray-900">{formatCurrency(item.amount)}</span>
                </div>
              ))}
            </div>
            <div className="border-t border-gray-200 pt-2 mt-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-900">Total Assets</span>
                <span className="text-sm font-bold text-gray-900">{formatCurrency(data.total_assets)}</span>
              </div>
            </div>
          </div>

          {/* Liabilities & Equity */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Liabilities & Equity</h3>
            <div className="space-y-2">
              {data.liabilities?.map((item, index) => (
                <div key={index} className="flex items-center justify-between py-2">
                  <span className="text-sm text-gray-900">{item.name}</span>
                  <span className="text-sm font-medium text-gray-900">{formatCurrency(item.amount)}</span>
                </div>
              ))}
              {data.equity?.map((item, index) => (
                <div key={index} className="flex items-center justify-between py-2">
                  <span className="text-sm text-gray-900">{item.name}</span>
                  <span className="text-sm font-medium text-gray-900">{formatCurrency(item.amount)}</span>
                </div>
              ))}
            </div>
            <div className="border-t border-gray-200 pt-2 mt-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-900">Total Liabilities & Equity</span>
                <span className="text-sm font-bold text-gray-900">{formatCurrency(data.total_liabilities_equity)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Render cash flow
  const renderCashFlow = (data) => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Cash Flow Statement</h2>
            <p className="text-sm text-gray-500">
              {formatDate(dateFrom)} to {formatDate(dateTo)}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              onClick={handleExportReport}
              className="flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Export</span>
            </Button>
            <Button
              variant="outline"
              className="flex items-center space-x-2"
            >
              <Print className="w-4 h-4" />
              <span>Print</span>
            </Button>
          </div>
        </div>
        
        <div className="space-y-4">
          {/* Operating Activities */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Operating Activities</h3>
            <div className="space-y-2">
              {data.operating?.map((item, index) => (
                <div key={index} className="flex items-center justify-between py-2">
                  <span className="text-sm text-gray-900">{item.name}</span>
                  <span className="text-sm font-medium text-gray-900">{formatCurrency(item.amount)}</span>
                </div>
              ))}
            </div>
            <div className="border-t border-gray-200 pt-2 mt-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-900">Net Operating Cash Flow</span>
                <span className="text-sm font-bold text-gray-900">{formatCurrency(data.net_operating)}</span>
              </div>
            </div>
          </div>

          {/* Investing Activities */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Investing Activities</h3>
            <div className="space-y-2">
              {data.investing?.map((item, index) => (
                <div key={index} className="flex items-center justify-between py-2">
                  <span className="text-sm text-gray-900">{item.name}</span>
                  <span className="text-sm font-medium text-gray-900">{formatCurrency(item.amount)}</span>
                </div>
              ))}
            </div>
            <div className="border-t border-gray-200 pt-2 mt-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-900">Net Investing Cash Flow</span>
                <span className="text-sm font-bold text-gray-900">{formatCurrency(data.net_investing)}</span>
              </div>
            </div>
          </div>

          {/* Financing Activities */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Financing Activities</h3>
            <div className="space-y-2">
              {data.financing?.map((item, index) => (
                <div key={index} className="flex items-center justify-between py-2">
                  <span className="text-sm text-gray-900">{item.name}</span>
                  <span className="text-sm font-medium text-gray-900">{formatCurrency(item.amount)}</span>
                </div>
              ))}
            </div>
            <div className="border-t border-gray-200 pt-2 mt-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-900">Net Financing Cash Flow</span>
                <span className="text-sm font-bold text-gray-900">{formatCurrency(data.net_financing)}</span>
              </div>
            </div>
          </div>

          {/* Net Cash Flow */}
          <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <div className="flex items-center justify-between">
              <span className="text-lg font-medium text-gray-900">Net Cash Flow</span>
              <span className={`text-lg font-bold ${data.net_cash_flow >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(data.net_cash_flow)}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Financial Reports</h1>
          <p className="text-gray-600">Generate and view financial reports</p>
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

      {/* Report Selection */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Select Report Type</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {reportTypes.map((report) => {
            const Icon = report.icon;
            return (
              <button
                key={report.id}
                onClick={() => setSelectedReport(report.id)}
                className={`p-4 border-2 rounded-lg text-left transition-colors ${
                  selectedReport === report.id
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-3 mb-2">
                  <div className={`w-8 h-8 rounded-full ${report.bgColor} flex items-center justify-center`}>
                    <Icon className={`w-4 h-4 ${report.color}`} />
                  </div>
                  <h3 className="text-sm font-medium text-gray-900">{report.name}</h3>
                </div>
                <p className="text-xs text-gray-500">{report.description}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Date Range */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Date Range</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              From Date
            </label>
            <Input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              To Date
            </label>
            <Input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
            />
          </div>
          <div className="flex items-end">
            <Button
              onClick={handleGenerateReport}
              loading={loading}
              className="w-full flex items-center justify-center space-x-2"
            >
              <BarChart3 className="w-4 h-4" />
              <span>Generate Report</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Report Display */}
      {showReport && reportData && (
        <div className="space-y-6">
          {selectedReport === 'trial_balance' && renderTrialBalance(reportData)}
          {selectedReport === 'profit_loss' && renderProfitLoss(reportData)}
          {selectedReport === 'balance_sheet' && renderBalanceSheet(reportData)}
          {selectedReport === 'cash_flow' && renderCashFlow(reportData)}
        </div>
      )}

      {/* No Report Selected */}
      {!showReport && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Report Generated</h3>
          <p className="text-gray-500">Select a report type and date range to generate a financial report.</p>
        </div>
      )}
    </div>
  );
};

export default FinancialReports;
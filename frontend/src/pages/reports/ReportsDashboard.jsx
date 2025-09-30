import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { reportsService } from '../../services/reportsService';
import Button from '../../components/common/Button';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown,
  DollarSign,
  Users,
  Package,
  ShoppingCart,
  Download,
  Calendar,
  Filter,
  RefreshCw
} from 'lucide-react';

const ReportsDashboard = () => {
  const { addNotification } = useApp();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dateRange, setDateRange] = useState('7d');
  const [refreshing, setRefreshing] = useState(false);

  // Fetch analytics data
  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await reportsService.getDashboardAnalytics({
        date_range: dateRange,
      });
      
      setAnalytics(data);
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
    fetchAnalytics();
  }, [dateRange]);

  // Handle refresh
  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchAnalytics();
    setRefreshing(false);
  };

  // Handle export
  const handleExport = async (reportType) => {
    try {
      await reportsService.exportReports(reportType, 'csv', { date_range: dateRange });
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: `${reportType} report will be downloaded shortly`,
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading reports..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <Alert type="danger" title="Error">
          {error}
        </Alert>
        <Button onClick={fetchAnalytics}>
          Retry
        </Button>
      </div>
    );
  }

  const reportCards = [
    {
      title: 'Sales Report',
      description: 'Revenue, transactions, and sales trends',
      icon: ShoppingCart,
      color: 'bg-primary-500',
      onClick: () => handleExport('sales'),
    },
    {
      title: 'Inventory Report',
      description: 'Stock levels, movements, and alerts',
      icon: Package,
      color: 'bg-success-500',
      onClick: () => handleExport('inventory'),
    },
    {
      title: 'Customer Report',
      description: 'Customer analytics and behavior',
      icon: Users,
      color: 'bg-warning-500',
      onClick: () => handleExport('customers'),
    },
    {
      title: 'Financial Report',
      description: 'Revenue, profit, and financial metrics',
      icon: DollarSign,
      color: 'bg-secondary-500',
      onClick: () => handleExport('financial'),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reports & Analytics</h1>
          <p className="text-gray-600">Comprehensive business insights and reports</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="form-input"
          >
            <option value="1d">Today</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          <Button
            variant="outline"
            onClick={handleRefresh}
            loading={refreshing}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-primary-100 rounded-md flex items-center justify-center">
                  <DollarSign className="w-5 h-5 text-primary-600" />
                </div>
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-500">Total Revenue</p>
                <p className="text-2xl font-semibold text-gray-900">₹{analytics.total_revenue || 0}</p>
                <p className="text-sm text-success-600">
                  <TrendingUp className="w-4 h-4 inline mr-1" />
                  +{analytics.revenue_growth || 0}%
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-success-100 rounded-md flex items-center justify-center">
                  <ShoppingCart className="w-5 h-5 text-success-600" />
                </div>
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-500">Total Sales</p>
                <p className="text-2xl font-semibold text-gray-900">{analytics.total_sales || 0}</p>
                <p className="text-sm text-success-600">
                  <TrendingUp className="w-4 h-4 inline mr-1" />
                  +{analytics.sales_growth || 0}%
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-warning-100 rounded-md flex items-center justify-center">
                  <Users className="w-5 h-5 text-warning-600" />
                </div>
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-500">Active Customers</p>
                <p className="text-2xl font-semibold text-gray-900">{analytics.active_customers || 0}</p>
                <p className="text-sm text-success-600">
                  <TrendingUp className="w-4 h-4 inline mr-1" />
                  +{analytics.customer_growth || 0}%
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-secondary-100 rounded-md flex items-center justify-center">
                  <Package className="w-5 h-5 text-secondary-600" />
                </div>
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-500">Inventory Items</p>
                <p className="text-2xl font-semibold text-gray-900">{analytics.inventory_items || 0}</p>
                <p className="text-sm text-warning-600">
                  <TrendingDown className="w-4 h-4 inline mr-1" />
                  {analytics.low_stock_items || 0} low stock
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Report Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {reportCards.map((card) => {
          const Icon = card.icon;
          return (
            <button
              key={card.title}
              onClick={card.onClick}
              className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow text-left"
            >
              <div className="flex items-center space-x-4">
                <div className={`w-12 h-12 ${card.color} rounded-lg flex items-center justify-center`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-gray-900">{card.title}</h3>
                  <p className="text-sm text-gray-500">{card.description}</p>
                </div>
                <Download className="w-5 h-5 text-gray-400" />
              </div>
            </button>
          );
        })}
      </div>

      {/* Charts Section */}
      {analytics && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Sales Trend Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Sales Trend</h3>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleExport('sales')}
              >
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
            </div>
            <div className="h-64 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <BarChart3 className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                <p>Sales trend chart will be displayed here</p>
              </div>
            </div>
          </div>

          {/* Top Products Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Top Products</h3>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleExport('products')}
              >
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
            </div>
            <div className="h-64 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <Package className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                <p>Top products chart will be displayed here</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Button
            variant="outline"
            onClick={() => handleExport('sales')}
            className="flex items-center justify-center space-x-2"
          >
            <ShoppingCart className="w-4 h-4" />
            <span>Export Sales Report</span>
          </Button>
          
          <Button
            variant="outline"
            onClick={() => handleExport('inventory')}
            className="flex items-center justify-center space-x-2"
          >
            <Package className="w-4 h-4" />
            <span>Export Inventory Report</span>
          </Button>
          
          <Button
            variant="outline"
            onClick={() => handleExport('financial')}
            className="flex items-center justify-center space-x-2"
          >
            <DollarSign className="w-4 h-4" />
            <span>Export Financial Report</span>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ReportsDashboard;
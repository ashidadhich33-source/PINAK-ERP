import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { reportsService } from '../../services/reportsService';
import ChartContainer from '../../components/charts/ChartContainer';
import Button from '../../components/common/Button';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown,
  DollarSign,
  Users,
  Package,
  ShoppingCart,
  Calendar,
  Download,
  RefreshCw,
  Filter
} from 'lucide-react';

const AnalyticsDashboard = () => {
  const { addNotification } = useApp();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState('30d');
  const [refreshing, setRefreshing] = useState(false);

  // Fetch analytics data
  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await reportsService.getDashboardAnalytics({
        date_range: dateRange,
        include_charts: true,
      });
      
      setAnalytics(data);
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
        <LoadingSpinner size="lg" text="Loading analytics..." />
      </div>
    );
  }

  // Sales trend chart data
  const salesTrendData = {
    labels: analytics?.sales_trend?.labels || [],
    datasets: [
      {
        label: 'Sales',
        data: analytics?.sales_trend?.data || [],
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  // Revenue by category chart data
  const revenueByCategoryData = {
    labels: analytics?.revenue_by_category?.labels || [],
    datasets: [
      {
        data: analytics?.revenue_by_category?.data || [],
        backgroundColor: [
          '#3b82f6',
          '#10b981',
          '#f59e0b',
          '#ef4444',
          '#8b5cf6',
          '#06b6d4',
        ],
      },
    ],
  };

  // Top products chart data
  const topProductsData = {
    labels: analytics?.top_products?.labels || [],
    datasets: [
      {
        label: 'Sales',
        data: analytics?.top_products?.data || [],
        backgroundColor: '#10b981',
        borderColor: '#10b981',
        borderWidth: 1,
      },
    ],
  };

  // Customer acquisition chart data
  const customerAcquisitionData = {
    labels: analytics?.customer_acquisition?.labels || [],
    datasets: [
      {
        label: 'New Customers',
        data: analytics?.customer_acquisition?.data || [],
        borderColor: '#8b5cf6',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600">Advanced business intelligence and insights</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="form-input"
          >
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
              <p className="text-2xl font-semibold text-gray-900">₹{analytics?.total_revenue || 0}</p>
              <p className="text-sm text-success-600">
                <TrendingUp className="w-4 h-4 inline mr-1" />
                +{analytics?.revenue_growth || 0}%
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
              <p className="text-2xl font-semibold text-gray-900">{analytics?.total_sales || 0}</p>
              <p className="text-sm text-success-600">
                <TrendingUp className="w-4 h-4 inline mr-1" />
                +{analytics?.sales_growth || 0}%
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
              <p className="text-2xl font-semibold text-gray-900">{analytics?.active_customers || 0}</p>
              <p className="text-sm text-success-600">
                <TrendingUp className="w-4 h-4 inline mr-1" />
                +{analytics?.customer_growth || 0}%
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
              <p className="text-2xl font-semibold text-gray-900">{analytics?.inventory_items || 0}</p>
              <p className="text-sm text-warning-600">
                <TrendingDown className="w-4 h-4 inline mr-1" />
                {analytics?.low_stock_items || 0} low stock
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sales Trend Chart */}
        <ChartContainer
          type="line"
          data={salesTrendData}
          title="Sales Trend"
          subtitle="Revenue over time"
          className="lg:col-span-2"
        />

        {/* Revenue by Category */}
        <ChartContainer
          type="pie"
          data={revenueByCategoryData}
          title="Revenue by Category"
          subtitle="Sales distribution by product category"
        />

        {/* Top Products */}
        <ChartContainer
          type="bar"
          data={topProductsData}
          title="Top Selling Products"
          subtitle="Best performing products"
        />

        {/* Customer Acquisition */}
        <ChartContainer
          type="line"
          data={customerAcquisitionData}
          title="Customer Acquisition"
          subtitle="New customer registrations over time"
          className="lg:col-span-2"
        />
      </div>

      {/* Advanced Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Performance Metrics */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Metrics</h3>
          <div className="space-y-4">
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Average Order Value</span>
              <span className="text-sm font-medium text-gray-900">₹{analytics?.avg_order_value || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Customer Lifetime Value</span>
              <span className="text-sm font-medium text-gray-900">₹{analytics?.customer_lifetime_value || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Conversion Rate</span>
              <span className="text-sm font-medium text-gray-900">{analytics?.conversion_rate || 0}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Return Rate</span>
              <span className="text-sm font-medium text-gray-900">{analytics?.return_rate || 0}%</span>
            </div>
          </div>
        </div>

        {/* Top Customers */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top Customers</h3>
          <div className="space-y-3">
            {analytics?.top_customers?.map((customer, index) => (
              <div key={customer.id} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <span className="text-xs font-medium text-primary-600">#{index + 1}</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{customer.name}</p>
                    <p className="text-xs text-gray-500">{customer.email}</p>
                  </div>
                </div>
                <span className="text-sm font-medium text-gray-900">₹{customer.total_spent}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <Button
              variant="outline"
              onClick={() => handleExport('sales')}
              className="w-full flex items-center justify-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Export Sales Report</span>
            </Button>
            
            <Button
              variant="outline"
              onClick={() => handleExport('customers')}
              className="w-full flex items-center justify-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Export Customer Report</span>
            </Button>
            
            <Button
              variant="outline"
              onClick={() => handleExport('inventory')}
              className="w-full flex items-center justify-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Export Inventory Report</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
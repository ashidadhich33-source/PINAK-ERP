import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { purchaseService } from '../../services/purchaseService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Calendar, 
  Download, 
  RefreshCw, 
  Building2, 
  ShoppingBag, 
  FileText, 
  PieChart, 
  Activity,
  Target,
  Award,
  Clock,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';

const PurchaseAnalytics = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analyticsData, setAnalyticsData] = useState({});
  const [reportsData, setReportsData] = useState({});
  const [vendorAnalysis, setVendorAnalysis] = useState([]);
  const [costAnalysis, setCostAnalysis] = useState({});
  const [trendAnalysis, setTrendAnalysis] = useState({});
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  // Set default dates
  useEffect(() => {
    const today = new Date();
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
    const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);
    
    setDateFrom(firstDay.toISOString().split('T')[0]);
    setDateTo(lastDay.toISOString().split('T')[0]);
  }, []);

  // Fetch analytics data
  useEffect(() => {
    const fetchAnalyticsData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const [analytics, reports, vendors, cost, trend] = await Promise.all([
          purchaseService.getPurchaseAnalytics({ date_from: dateFrom, date_to: dateTo }),
          purchaseService.getPurchaseReports({ date_from: dateFrom, date_to: dateTo }),
          purchaseService.getVendorAnalysis({ date_from: dateFrom, date_to: dateTo }),
          purchaseService.getCostAnalysis({ date_from: dateFrom, date_to: dateTo }),
          purchaseService.getTrendAnalysis({ date_from: dateFrom, date_to: dateTo })
        ]);
        
        setAnalyticsData(analytics);
        setReportsData(reports);
        setVendorAnalysis(vendors);
        setCostAnalysis(cost);
        setTrendAnalysis(trend);
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

    if (dateFrom && dateTo) {
      fetchAnalyticsData();
    }
  }, [dateFrom, dateTo]);

  // Handle export
  const handleExport = async () => {
    try {
      await purchaseService.exportPurchaseReports({
        date_from: dateFrom,
        date_to: dateTo
      });
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: 'Purchase analytics export will be downloaded shortly',
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

  // Format percentage
  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading purchase analytics..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Purchase Analytics</h1>
          <p className="text-gray-600">Analyze purchase trends and vendor performance</p>
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
              onClick={() => window.location.reload()}
              className="w-full flex items-center justify-center space-x-2"
            >
              <BarChart3 className="w-4 h-4" />
              <span>Update Analytics</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'overview', name: 'Overview', icon: BarChart3 },
              { id: 'vendors', name: 'Vendor Analysis', icon: Building2 },
              { id: 'costs', name: 'Cost Analysis', icon: DollarSign },
              { id: 'trends', name: 'Trend Analysis', icon: TrendingUp }
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
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                      <ShoppingBag className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Total Orders</p>
                      <p className="text-2xl font-bold text-gray-900">{analyticsData.total_orders || 0}</p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                      <DollarSign className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Total Value</p>
                      <p className="text-2xl font-bold text-gray-900">{formatCurrency(analyticsData.total_value || 0)}</p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                      <Building2 className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Active Vendors</p>
                      <p className="text-2xl font-bold text-gray-900">{analyticsData.active_vendors || 0}</p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
                      <TrendingUp className="w-5 h-5 text-orange-600" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Growth Rate</p>
                      <p className="text-2xl font-bold text-gray-900">{formatPercentage(analyticsData.growth_rate || 0)}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Purchase Status Overview */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Purchase Status Overview</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Clock className="w-5 h-5 text-yellow-600" />
                      <span className="text-sm font-medium text-gray-900">Pending</span>
                    </div>
                    <span className="text-lg font-bold text-gray-900">{analyticsData.pending_orders || 0}</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <span className="text-sm font-medium text-gray-900">Completed</span>
                    </div>
                    <span className="text-lg font-bold text-gray-900">{analyticsData.completed_orders || 0}</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <AlertTriangle className="w-5 h-5 text-red-600" />
                      <span className="text-sm font-medium text-gray-900">Overdue</span>
                    </div>
                    <span className="text-lg font-bold text-gray-900">{analyticsData.overdue_orders || 0}</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Activity className="w-5 h-5 text-blue-600" />
                      <span className="text-sm font-medium text-gray-900">In Progress</span>
                    </div>
                    <span className="text-lg font-bold text-gray-900">{analyticsData.in_progress_orders || 0}</span>
                  </div>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Purchase Activity</h3>
                <div className="space-y-3">
                  {analyticsData.recent_activity?.map((activity, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                        <span className="text-sm text-gray-900">{activity.description}</span>
                      </div>
                      <span className="text-xs text-gray-500">{formatDate(activity.date)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Vendor Analysis Tab */}
          {activeTab === 'vendors' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Top Vendors */}
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Top Vendors by Value</h3>
                  <div className="space-y-3">
                    {vendorAnalysis.slice(0, 5).map((vendor, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                            <span className="text-sm font-medium text-primary-600">{index + 1}</span>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-900">{vendor.name}</p>
                            <p className="text-xs text-gray-500">{vendor.orders_count} orders</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium text-gray-900">{formatCurrency(vendor.total_value)}</p>
                          <p className="text-xs text-gray-500">{formatPercentage(vendor.market_share)}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Vendor Performance */}
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Vendor Performance</h3>
                  <div className="space-y-3">
                    {vendorAnalysis.slice(0, 5).map((vendor, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-900">{vendor.name}</p>
                          <p className="text-xs text-gray-500">Rating: {vendor.rating}/5</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="w-20 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-primary-600 h-2 rounded-full" 
                              style={{ width: `${(vendor.rating / 5) * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-xs text-gray-500">{vendor.rating}/5</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Cost Analysis Tab */}
          {activeTab === 'costs' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Cost Breakdown</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Materials</span>
                      <span className="text-sm font-medium text-gray-900">{formatCurrency(costAnalysis.materials || 0)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Services</span>
                      <span className="text-sm font-medium text-gray-900">{formatCurrency(costAnalysis.services || 0)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Equipment</span>
                      <span className="text-sm font-medium text-gray-900">{formatCurrency(costAnalysis.equipment || 0)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Other</span>
                      <span className="text-sm font-medium text-gray-900">{formatCurrency(costAnalysis.other || 0)}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Cost Trends</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">This Month</span>
                      <span className="text-sm font-medium text-gray-900">{formatCurrency(costAnalysis.this_month || 0)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Last Month</span>
                      <span className="text-sm font-medium text-gray-900">{formatCurrency(costAnalysis.last_month || 0)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Change</span>
                      <span className={`text-sm font-medium ${(costAnalysis.change || 0) >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {formatPercentage(Math.abs(costAnalysis.change || 0))}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Average Costs</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Per Order</span>
                      <span className="text-sm font-medium text-gray-900">{formatCurrency(costAnalysis.avg_per_order || 0)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Per Vendor</span>
                      <span className="text-sm font-medium text-gray-900">{formatCurrency(costAnalysis.avg_per_vendor || 0)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Per Item</span>
                      <span className="text-sm font-medium text-gray-900">{formatCurrency(costAnalysis.avg_per_item || 0)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Trend Analysis Tab */}
          {activeTab === 'trends' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Purchase Trends</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Monthly Growth</span>
                      <span className="text-sm font-medium text-gray-900">{formatPercentage(trendAnalysis.monthly_growth || 0)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Quarterly Growth</span>
                      <span className="text-sm font-medium text-gray-900">{formatPercentage(trendAnalysis.quarterly_growth || 0)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Yearly Growth</span>
                      <span className="text-sm font-medium text-gray-900">{formatPercentage(trendAnalysis.yearly_growth || 0)}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Seasonal Patterns</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Peak Month</span>
                      <span className="text-sm font-medium text-gray-900">{trendAnalysis.peak_month || 'N/A'}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Low Month</span>
                      <span className="text-sm font-medium text-gray-900">{trendAnalysis.low_month || 'N/A'}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Seasonal Factor</span>
                      <span className="text-sm font-medium text-gray-900">{formatPercentage(trendAnalysis.seasonal_factor || 0)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Trend Chart Placeholder */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Purchase Trend Chart</h3>
                <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">Trend chart visualization will be implemented here</p>
                    <p className="text-sm text-gray-400">This will show purchase trends over time</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PurchaseAnalytics;
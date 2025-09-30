import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { reportService } from '../../services/reportService';
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
  FileText, 
  PieChart, 
  Activity,
  Calculator,
  Eye,
  Print,
  Share2,
  Clock,
  Target,
  Award,
  CheckCircle,
  AlertTriangle,
  Users,
  ShoppingCart,
  Package,
  Building2,
  CreditCard,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  ArrowUp,
  ArrowDown,
  Minus
} from 'lucide-react';

const DashboardReports = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedDashboard, setSelectedDashboard] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [dashboardData, setDashboardData] = useState(null);
  const [showDashboard, setShowDashboard] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  // Dashboard types
  const dashboardTypes = [
    {
      id: 'executive',
      name: 'Executive Dashboard',
      icon: Award,
      description: 'High-level business metrics',
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      id: 'operational',
      name: 'Operational Dashboard',
      icon: Activity,
      description: 'Day-to-day operations',
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      id: 'financial',
      name: 'Financial Dashboard',
      icon: DollarSign,
      description: 'Financial performance',
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      id: 'sales',
      name: 'Sales Dashboard',
      icon: TrendingUp,
      description: 'Sales performance metrics',
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

  // Handle dashboard generation
  const handleGenerateDashboard = async () => {
    if (!selectedDashboard) {
      addNotification({
        type: 'warning',
        title: 'Warning',
        message: 'Please select a dashboard type',
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

      switch (selectedDashboard) {
        case 'executive':
          data = await reportService.getExecutiveDashboard(params);
          break;
        case 'operational':
          data = await reportService.getOperationalDashboard(params);
          break;
        case 'financial':
          data = await reportService.getFinancialDashboard(params);
          break;
        case 'sales':
          data = await reportService.getSalesDashboard(params);
          break;
        default:
          throw new Error('Invalid dashboard type');
      }
      
      setDashboardData(data);
      setShowDashboard(true);
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

  // Handle export dashboard
  const handleExportDashboard = async () => {
    if (!selectedDashboard) return;

    try {
      await reportService.exportDashboard(selectedDashboard, {
        date_from: dateFrom,
        date_to: dateTo
      });
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: 'Dashboard export will be downloaded shortly',
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

  // Render executive dashboard
  const renderExecutiveDashboard = (data) => (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Revenue</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(data.total_revenue)}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Growth Rate</p>
              <p className="text-2xl font-bold text-gray-900">{formatPercentage(data.growth_rate)}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
              <Users className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Active Customers</p>
              <p className="text-2xl font-bold text-gray-900">{data.active_customers}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
              <Target className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Goal Achievement</p>
              <p className="text-2xl font-bold text-gray-900">{formatPercentage(data.goal_achievement)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Revenue Trend</h3>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="text-center">
              <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Revenue trend chart will be implemented here</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Customer Growth</h3>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="text-center">
              <PieChart className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Customer growth chart will be implemented here</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Render operational dashboard
  const renderOperationalDashboard = (data) => (
    <div className="space-y-6">
      {/* Operational Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <ShoppingCart className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Orders Today</p>
              <p className="text-2xl font-bold text-gray-900">{data.orders_today}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <Package className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Items in Stock</p>
              <p className="text-2xl font-bold text-gray-900">{data.items_in_stock}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
              <Clock className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Pending Tasks</p>
              <p className="text-2xl font-bold text-gray-900">{data.pending_tasks}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          {data.recent_activity?.map((activity, index) => (
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
  );

  // Render financial dashboard
  const renderFinancialDashboard = (data) => (
    <div className="space-y-6">
      {/* Financial Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Revenue</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(data.total_revenue)}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
              <TrendingDown className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Expenses</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(data.total_expenses)}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Net Profit</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(data.net_profit)}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
              <Calculator className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Profit Margin</p>
              <p className="text-2xl font-bold text-gray-900">{formatPercentage(data.profit_margin)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Financial Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Revenue vs Expenses</h3>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="text-center">
              <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Revenue vs expenses chart will be implemented here</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Profit Trend</h3>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="text-center">
              <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Profit trend chart will be implemented here</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Render sales dashboard
  const renderSalesDashboard = (data) => (
    <div className="space-y-6">
      {/* Sales Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <ShoppingCart className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Sales</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(data.total_sales)}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <Users className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">New Customers</p>
              <p className="text-2xl font-bold text-gray-900">{data.new_customers}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
              <Target className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Conversion Rate</p>
              <p className="text-2xl font-bold text-gray-900">{formatPercentage(data.conversion_rate)}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
              <Award className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Top Product</p>
              <p className="text-2xl font-bold text-gray-900">{data.top_product}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Sales Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Sales Trend</h3>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="text-center">
              <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Sales trend chart will be implemented here</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Product Performance</h3>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="text-center">
              <PieChart className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Product performance chart will be implemented here</p>
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
          <h1 className="text-2xl font-bold text-gray-900">Dashboard Reports</h1>
          <p className="text-gray-600">Generate and view comprehensive dashboard reports</p>
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

      {/* Dashboard Selection */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Select Dashboard Type</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {dashboardTypes.map((dashboard) => {
            const Icon = dashboard.icon;
            return (
              <button
                key={dashboard.id}
                onClick={() => setSelectedDashboard(dashboard.id)}
                className={`p-4 border-2 rounded-lg text-left transition-colors ${
                  selectedDashboard === dashboard.id
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-3 mb-2">
                  <div className={`w-8 h-8 rounded-full ${dashboard.bgColor} flex items-center justify-center`}>
                    <Icon className={`w-4 h-4 ${dashboard.color}`} />
                  </div>
                  <h3 className="text-sm font-medium text-gray-900">{dashboard.name}</h3>
                </div>
                <p className="text-xs text-gray-500">{dashboard.description}</p>
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
              onClick={handleGenerateDashboard}
              loading={loading}
              className="w-full flex items-center justify-center space-x-2"
            >
              <BarChart3 className="w-4 h-4" />
              <span>Generate Dashboard</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Dashboard Display */}
      {showDashboard && dashboardData && (
        <div className="space-y-6">
          {selectedDashboard === 'executive' && renderExecutiveDashboard(dashboardData)}
          {selectedDashboard === 'operational' && renderOperationalDashboard(dashboardData)}
          {selectedDashboard === 'financial' && renderFinancialDashboard(dashboardData)}
          {selectedDashboard === 'sales' && renderSalesDashboard(dashboardData)}
        </div>
      )}

      {/* No Dashboard Selected */}
      {!showDashboard && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Dashboard Generated</h3>
          <p className="text-gray-500">Select a dashboard type and date range to generate a dashboard report.</p>
        </div>
      )}
    </div>
  );
};

export default DashboardReports;
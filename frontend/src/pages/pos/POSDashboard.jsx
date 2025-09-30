import React, { useState, useEffect } from 'react';
import { usePos } from '../../contexts/PosContext';
import { useApp } from '../../contexts/AppContext';
import { posService } from '../../services/posService';
import Button from '../../components/common/Button';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  ShoppingCart, 
  Users, 
  Package, 
  DollarSign,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertTriangle,
  Plus,
  Search,
  Filter
} from 'lucide-react';

const POSDashboard = () => {
  const { addNotification } = useApp();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recentTransactions, setRecentTransactions] = useState([]);

  // Fetch dashboard data
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [dashboard, transactions] = await Promise.all([
        posService.getPosDashboard(),
        posService.getPosTransactions({ limit: 10 }),
      ]);
      
      setDashboardData(dashboard);
      setRecentTransactions(transactions);
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
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading POS dashboard..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <Alert type="danger" title="Error">
          {error}
        </Alert>
        <Button onClick={fetchDashboardData}>
          Retry
        </Button>
      </div>
    );
  }

  const stats = [
    {
      name: 'Today\'s Sales',
      value: `₹${dashboardData?.today_sales || 0}`,
      change: `+${dashboardData?.sales_growth || 0}%`,
      changeType: 'positive',
      icon: DollarSign,
    },
    {
      name: 'Total Transactions',
      value: dashboardData?.total_transactions || 0,
      change: `+${dashboardData?.transaction_growth || 0}%`,
      changeType: 'positive',
      icon: ShoppingCart,
    },
    {
      name: 'Active Customers',
      value: dashboardData?.active_customers || 0,
      change: `+${dashboardData?.customer_growth || 0}%`,
      changeType: 'positive',
      icon: Users,
    },
    {
      name: 'Inventory Items',
      value: dashboardData?.inventory_items || 0,
      change: `+${dashboardData?.inventory_growth || 0}%`,
      changeType: 'positive',
      icon: Package,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">POS Dashboard</h1>
          <p className="text-gray-600">Point of Sale Management System</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            className="flex items-center space-x-2"
          >
            <Filter className="w-4 h-4" />
            <span>Filters</span>
          </Button>
          <Button className="flex items-center space-x-2">
            <Plus className="w-4 h-4" />
            <span>New Sale</span>
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-primary-100 rounded-md flex items-center justify-center">
                    <Icon className="w-5 h-5 text-primary-600" />
                  </div>
                </div>
                <div className="ml-4 flex-1">
                  <p className="text-sm font-medium text-gray-500">{stat.name}</p>
                  <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
                  <p className={`text-sm ${
                    stat.changeType === 'positive' ? 'text-success-600' : 'text-danger-600'
                  }`}>
                    {stat.change} from yesterday
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Transactions */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Recent Transactions</h3>
          </div>
          <div className="px-6 py-4">
            <div className="space-y-4">
              {recentTransactions.length === 0 ? (
                <p className="text-gray-500 text-center py-4">No recent transactions</p>
              ) : (
                recentTransactions.map((transaction) => (
                  <div key={transaction.id} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                        <ShoppingCart className="w-4 h-4 text-primary-600" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          #{transaction.transaction_number}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(transaction.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">
                        ₹{transaction.total_amount}
                      </p>
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                        transaction.status === 'completed' 
                          ? 'bg-success-100 text-success-800'
                          : transaction.status === 'pending'
                            ? 'bg-warning-100 text-warning-800'
                            : 'bg-danger-100 text-danger-800'
                      }`}>
                        {transaction.status}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
          </div>
          <div className="px-6 py-4">
            <div className="grid grid-cols-2 gap-4">
              <button className="flex flex-col items-center p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors">
                <ShoppingCart className="w-8 h-8 text-primary-600 mb-2" />
                <span className="text-sm font-medium text-gray-900">New Sale</span>
              </button>
              
              <button className="flex flex-col items-center p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors">
                <Users className="w-8 h-8 text-primary-600 mb-2" />
                <span className="text-sm font-medium text-gray-900">Add Customer</span>
              </button>
              
              <button className="flex flex-col items-center p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors">
                <Package className="w-8 h-8 text-primary-600 mb-2" />
                <span className="text-sm font-medium text-gray-900">Add Product</span>
              </button>
              
              <button className="flex flex-col items-center p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors">
                <TrendingUp className="w-8 h-8 text-primary-600 mb-2" />
                <span className="text-sm font-medium text-gray-900">View Reports</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Alerts */}
      {dashboardData?.alerts && dashboardData.alerts.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">System Alerts</h3>
          </div>
          <div className="px-6 py-4">
            <div className="space-y-3">
              {dashboardData.alerts.map((alert, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <AlertTriangle className="w-5 h-5 text-warning-500 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-900">{alert.message}</p>
                    <p className="text-xs text-gray-500">{alert.timestamp}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default POSDashboard;
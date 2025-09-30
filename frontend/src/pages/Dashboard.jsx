import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Users, 
  Package, 
  ShoppingCart, 
  TrendingUp,
  DollarSign,
  Activity,
  AlertTriangle
} from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();

  const stats = [
    {
      name: 'Total Customers',
      value: '1,234',
      change: '+12%',
      changeType: 'positive',
      icon: Users,
    },
    {
      name: 'Total Products',
      value: '567',
      change: '+8%',
      changeType: 'positive',
      icon: Package,
    },
    {
      name: 'Today\'s Sales',
      value: '₹45,678',
      change: '+15%',
      changeType: 'positive',
      icon: ShoppingCart,
    },
    {
      name: 'Revenue Growth',
      value: '23.5%',
      change: '+2.1%',
      changeType: 'positive',
      icon: TrendingUp,
    },
  ];

  const recentActivities = [
    {
      id: 1,
      type: 'sale',
      message: 'New sale created: #SO-001',
      time: '2 minutes ago',
      amount: '₹5,000',
    },
    {
      id: 2,
      type: 'customer',
      message: 'New customer registered: John Doe',
      time: '1 hour ago',
    },
    {
      id: 3,
      type: 'inventory',
      message: 'Low stock alert: 5 items need restocking',
      time: '3 hours ago',
    },
    {
      id: 4,
      type: 'payment',
      message: 'Payment received: ₹10,000 from ABC Corp',
      time: '5 hours ago',
    },
  ];

  const quickActions = [
    {
      name: 'New Sale',
      href: '/pos',
      icon: ShoppingCart,
      color: 'bg-primary-500',
    },
    {
      name: 'Add Customer',
      href: '/customers/new',
      icon: Users,
      color: 'bg-success-500',
    },
    {
      name: 'Add Product',
      href: '/inventory/items/new',
      icon: Package,
      color: 'bg-warning-500',
    },
    {
      name: 'View Reports',
      href: '/reports',
      icon: TrendingUp,
      color: 'bg-secondary-500',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.full_name || user?.username}!
        </h1>
        <p className="text-gray-600 mt-1">
          Here's what's happening with your business today.
        </p>
      </div>

      {/* Stats grid */}
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
                    {stat.change} from last month
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activities */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Recent Activities</h3>
          </div>
          <div className="px-6 py-4">
            <div className="space-y-4">
              {recentActivities.map((activity) => (
                <div key={activity.id} className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <div className="w-2 h-2 bg-primary-500 rounded-full mt-2"></div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900">{activity.message}</p>
                    <p className="text-xs text-gray-500">{activity.time}</p>
                    {activity.amount && (
                      <p className="text-xs text-success-600 font-medium">{activity.amount}</p>
                    )}
                  </div>
                </div>
              ))}
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
              {quickActions.map((action) => {
                const Icon = action.icon;
                return (
                  <a
                    key={action.name}
                    href={action.href}
                    className="flex flex-col items-center p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors"
                  >
                    <div className={`w-12 h-12 ${action.color} rounded-lg flex items-center justify-center mb-3`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <span className="text-sm font-medium text-gray-900 text-center">
                      {action.name}
                    </span>
                  </a>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Alerts */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">System Alerts</h3>
        </div>
        <div className="px-6 py-4">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-5 h-5 text-warning-500 mt-0.5" />
            <div>
              <p className="text-sm text-gray-900">
                Low stock alert: 5 items need restocking
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Consider placing purchase orders for these items.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
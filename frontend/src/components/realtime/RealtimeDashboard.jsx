import React, { useState, useEffect } from 'react';
import { useRealtime } from '../../contexts/RealtimeContext';
import { 
  Wifi, 
  WifiOff, 
  Bell, 
  ShoppingCart, 
  Package, 
  Users, 
  CreditCard,
  TrendingUp,
  Activity,
  RefreshCw
} from 'lucide-react';
import Button from '../common/Button';
import Alert from '../common/Alert';

const RealtimeDashboard = () => {
  const { 
    isConnected, 
    realtimeData, 
    getNotifications, 
    getSales, 
    getInventory, 
    getCustomers, 
    getPos,
    clearNotifications,
    reconnect
  } = useRealtime();

  const [activeTab, setActiveTab] = useState('notifications');

  const tabs = [
    { id: 'notifications', label: 'Notifications', icon: Bell, count: getNotifications().length },
    { id: 'sales', label: 'Sales', icon: ShoppingCart, count: getSales().length },
    { id: 'inventory', label: 'Inventory', icon: Package, count: getInventory().length },
    { id: 'customers', label: 'Customers', icon: Users, count: getCustomers().length },
    { id: 'pos', label: 'POS', icon: CreditCard, count: getPos().length },
  ];

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'text-success-600';
      case 'warning':
        return 'text-warning-600';
      case 'error':
        return 'text-danger-600';
      default:
        return 'text-gray-600';
    }
  };

  const renderNotifications = () => {
    const notifications = getNotifications();
    
    if (notifications.length === 0) {
      return (
        <div className="text-center py-8 text-gray-500">
          <Bell className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>No notifications</p>
        </div>
      );
    }

    return (
      <div className="space-y-3">
        {notifications.map((notification, index) => (
          <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
            <div className={`w-2 h-2 rounded-full mt-2 ${
              notification.type === 'success' ? 'bg-success-500' :
              notification.type === 'warning' ? 'bg-warning-500' :
              notification.type === 'error' ? 'bg-danger-500' :
              'bg-primary-500'
            }`} />
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">{notification.title}</p>
              <p className="text-sm text-gray-600">{notification.message}</p>
              <p className="text-xs text-gray-500 mt-1">{formatTimestamp(notification.timestamp)}</p>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderSales = () => {
    const sales = getSales();
    
    if (sales.length === 0) {
      return (
        <div className="text-center py-8 text-gray-500">
          <ShoppingCart className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>No recent sales</p>
        </div>
      );
    }

    return (
      <div className="space-y-3">
        {sales.map((sale, index) => (
          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <ShoppingCart className="w-5 h-5 text-primary-600" />
              <div>
                <p className="text-sm font-medium text-gray-900">#{sale.sale_number}</p>
                <p className="text-xs text-gray-500">{sale.customer?.name || 'Walk-in'}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">₹{sale.total_amount}</p>
              <p className="text-xs text-gray-500">{formatTimestamp(sale.timestamp)}</p>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderInventory = () => {
    const inventory = getInventory();
    
    if (inventory.length === 0) {
      return (
        <div className="text-center py-8 text-gray-500">
          <Package className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>No inventory updates</p>
        </div>
      );
    }

    return (
      <div className="space-y-3">
        {inventory.map((item, index) => (
          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <Package className="w-5 h-5 text-primary-600" />
              <div>
                <p className="text-sm font-medium text-gray-900">{item.name}</p>
                <p className="text-xs text-gray-500">SKU: {item.sku}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">Stock: {item.stock_quantity}</p>
              <p className="text-xs text-gray-500">{formatTimestamp(item.timestamp)}</p>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderCustomers = () => {
    const customers = getCustomers();
    
    if (customers.length === 0) {
      return (
        <div className="text-center py-8 text-gray-500">
          <Users className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>No customer updates</p>
        </div>
      );
    }

    return (
      <div className="space-y-3">
        {customers.map((customer, index) => (
          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <Users className="w-5 h-5 text-primary-600" />
              <div>
                <p className="text-sm font-medium text-gray-900">{customer.name}</p>
                <p className="text-xs text-gray-500">{customer.email}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">{customer.status}</p>
              <p className="text-xs text-gray-500">{formatTimestamp(customer.timestamp)}</p>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderPos = () => {
    const pos = getPos();
    
    if (pos.length === 0) {
      return (
        <div className="text-center py-8 text-gray-500">
          <CreditCard className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>No POS transactions</p>
        </div>
      );
    }

    return (
      <div className="space-y-3">
        {pos.map((transaction, index) => (
          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <CreditCard className="w-5 h-5 text-primary-600" />
              <div>
                <p className="text-sm font-medium text-gray-900">#{transaction.transaction_number}</p>
                <p className="text-xs text-gray-500">{transaction.payment_method}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">₹{transaction.total_amount}</p>
              <p className="text-xs text-gray-500">{formatTimestamp(transaction.timestamp)}</p>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'notifications':
        return renderNotifications();
      case 'sales':
        return renderSales();
      case 'inventory':
        return renderInventory();
      case 'customers':
        return renderCustomers();
      case 'pos':
        return renderPos();
      default:
        return null;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${
              isConnected ? 'bg-success-500' : 'bg-danger-500'
            }`} />
            <h3 className="text-lg font-medium text-gray-900">Real-time Updates</h3>
            {isConnected ? (
              <Wifi className="w-4 h-4 text-success-500" />
            ) : (
              <WifiOff className="w-4 h-4 text-danger-500" />
            )}
          </div>
          <div className="flex items-center space-x-2">
            {!isConnected && (
              <Button
                size="sm"
                variant="outline"
                onClick={reconnect}
                className="flex items-center space-x-1"
              >
                <RefreshCw className="w-3 h-3" />
                <span>Reconnect</span>
              </Button>
            )}
            {activeTab === 'notifications' && (
              <Button
                size="sm"
                variant="outline"
                onClick={clearNotifications}
                className="text-danger-600 hover:text-danger-900"
              >
                Clear
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Connection Status */}
      {!isConnected && (
        <div className="px-6 py-3">
          <Alert type="warning" title="Connection Lost">
            Real-time updates are not available. Check your internet connection.
          </Alert>
        </div>
      )}

      {/* Tabs */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex space-x-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  activeTab === tab.id
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
                {tab.count > 0 && (
                  <span className="bg-primary-500 text-white text-xs rounded-full px-2 py-1">
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="px-6 py-4 max-h-96 overflow-y-auto">
        {renderContent()}
      </div>
    </div>
  );
};

export default RealtimeDashboard;
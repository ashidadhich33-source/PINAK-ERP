import React, { useState, useEffect, useRef } from 'react';
import { useApp } from '../../contexts/AppContext';
import { useAuth } from '../../contexts/AuthContext';
import Button from '../common/Button';
import { 
  Home, 
  Users, 
  Package, 
  ShoppingCart, 
  BarChart3, 
  Settings,
  Bell,
  Search,
  Plus,
  ChevronLeft,
  ChevronRight,
  Menu,
  X,
  User,
  LogOut,
  Wifi,
  WifiOff,
  Battery,
  Signal
} from 'lucide-react';

const MobileNavigation = () => {
  const { sidebarOpen, setSidebarOpen } = useApp();
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [swipeDirection, setSwipeDirection] = useState(null);
  const [touchStart, setTouchStart] = useState(null);
  const [touchEnd, setTouchEnd] = useState(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [batteryLevel, setBatteryLevel] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [showQuickActions, setShowQuickActions] = useState(false);
  
  const navigationRef = useRef(null);
  const sidebarRef = useRef(null);

  // Navigation items
  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home, path: '/dashboard' },
    { id: 'companies', label: 'Companies', icon: Users, path: '/companies' },
    { id: 'customers', label: 'Customers', icon: Users, path: '/customers' },
    { id: 'inventory', label: 'Inventory', icon: Package, path: '/inventory' },
    { id: 'pos', label: 'POS', icon: ShoppingCart, path: '/pos' },
    { id: 'sales', label: 'Sales', icon: BarChart3, path: '/sales' },
    { id: 'reports', label: 'Reports', icon: BarChart3, path: '/reports' },
    { id: 'settings', label: 'Settings', icon: Settings, path: '/settings' },
  ];

  // Quick actions
  const quickActions = [
    { id: 'new-customer', label: 'New Customer', icon: Users, action: () => {} },
    { id: 'new-sale', label: 'New Sale', icon: ShoppingCart, action: () => {} },
    { id: 'new-item', label: 'New Item', icon: Package, action: () => {} },
    { id: 'search', label: 'Search', icon: Search, action: () => {} },
  ];

  // Monitor online status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Monitor battery level
  useEffect(() => {
    if ('getBattery' in navigator) {
      navigator.getBattery().then((battery) => {
        setBatteryLevel(battery.level);
        
        const updateBatteryLevel = () => setBatteryLevel(battery.level);
        battery.addEventListener('levelchange', updateBatteryLevel);
        
        return () => battery.removeEventListener('levelchange', updateBatteryLevel);
      });
    }
  }, []);

  // Touch event handlers
  const handleTouchStart = (e) => {
    setTouchStart(e.targetTouches[0].clientX);
  };

  const handleTouchMove = (e) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  const handleTouchEnd = () => {
    if (!touchStart || !touchEnd) return;
    
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > 50;
    const isRightSwipe = distance < -50;

    if (isLeftSwipe) {
      setSwipeDirection('left');
      setSidebarOpen(false);
    } else if (isRightSwipe) {
      setSwipeDirection('right');
      setSidebarOpen(true);
    }
  };

  // Handle navigation item click
  const handleNavigationClick = (item) => {
    setActiveTab(item.id);
    setSidebarOpen(false);
    // Navigate to the item's path
    window.location.href = item.path;
  };

  // Handle quick action click
  const handleQuickAction = (action) => {
    action.action();
    setShowQuickActions(false);
  };

  // Handle logout
  const handleLogout = () => {
    logout();
    setSidebarOpen(false);
  };

  // Get battery icon
  const getBatteryIcon = () => {
    if (batteryLevel === null) return Battery;
    if (batteryLevel < 0.2) return Battery;
    return Battery;
  };

  const getBatteryColor = () => {
    if (batteryLevel === null) return 'text-gray-500';
    if (batteryLevel < 0.2) return 'text-danger-500';
    if (batteryLevel < 0.5) return 'text-warning-500';
    return 'text-success-500';
  };

  const BatteryIcon = getBatteryIcon();

  return (
    <>
      {/* Mobile Header */}
      <header className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
        <div className="flex items-center justify-between px-4 py-3">
          {/* Left Section */}
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
            >
              {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-semibold text-gray-900">PINAK-ERP</h1>
              {!isOnline && (
                <div className="w-2 h-2 bg-danger-500 rounded-full" />
              )}
            </div>
          </div>

          {/* Right Section */}
          <div className="flex items-center space-x-2">
            {/* Status Indicators */}
            <div className="flex items-center space-x-1 text-xs text-gray-500">
              {isOnline ? (
                <Wifi className="w-4 h-4 text-success-500" />
              ) : (
                <WifiOff className="w-4 h-4 text-danger-500" />
              )}
              
              {batteryLevel !== null && (
                <div className="flex items-center space-x-1">
                  <BatteryIcon className={`w-4 h-4 ${getBatteryColor()}`} />
                  <span>{Math.round(batteryLevel * 100)}%</span>
                </div>
              )}
            </div>

            {/* Notifications */}
            <button className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md">
              <Bell className="w-5 h-5" />
              {notifications.length > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-danger-500 text-white text-xs rounded-full flex items-center justify-center">
                  {notifications.length}
                </span>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Sidebar */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50" 
          onClick={() => setSidebarOpen(false)}
        >
          <div 
            ref={sidebarRef}
            className="fixed left-0 top-0 h-full w-80 bg-white shadow-xl"
            onTouchStart={handleTouchStart}
            onTouchMove={handleTouchMove}
            onTouchEnd={handleTouchEnd}
          >
            <div className="flex flex-col h-full">
              {/* Sidebar Header */}
              <div className="flex items-center justify-between p-4 border-b border-gray-200">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-primary-600">
                      {user?.full_name?.charAt(0) || 'U'}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{user?.full_name || 'User'}</p>
                    <p className="text-xs text-gray-500">{user?.email || 'user@example.com'}</p>
                  </div>
                </div>
                <button
                  onClick={() => setSidebarOpen(false)}
                  className="p-2 text-gray-400 hover:text-gray-600"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Navigation */}
              <nav className="flex-1 px-4 py-4 space-y-2">
                {navigationItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = activeTab === item.id;
                  
                  return (
                    <button
                      key={item.id}
                      onClick={() => handleNavigationClick(item)}
                      className={`w-full flex items-center space-x-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                        isActive 
                          ? 'bg-primary-100 text-primary-700' 
                          : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span>{item.label}</span>
                    </button>
                  );
                })}
              </nav>

              {/* Sidebar Footer */}
              <div className="p-4 border-t border-gray-200">
                <Button
                  variant="outline"
                  onClick={handleLogout}
                  className="w-full flex items-center justify-center space-x-2"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Logout</span>
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Mobile Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-gray-200 shadow-lg">
        <div className="flex items-center justify-around py-2">
          {navigationItems.slice(0, 5).map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => handleNavigationClick(item)}
                className={`flex flex-col items-center space-y-1 px-3 py-2 text-xs font-medium transition-colors ${
                  isActive 
                    ? 'text-primary-600' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </nav>

      {/* Floating Action Button */}
      <button 
        onClick={() => setShowQuickActions(!showQuickActions)}
        className="fixed bottom-20 right-4 z-30 w-14 h-14 bg-primary-600 text-white rounded-full shadow-lg hover:bg-primary-700 transition-colors flex items-center justify-center"
      >
        <Plus className="w-6 h-6" />
      </button>

      {/* Quick Actions Menu */}
      {showQuickActions && (
        <div className="fixed bottom-20 right-4 z-30 bg-white rounded-lg shadow-lg border border-gray-200 p-2">
          <div className="space-y-2">
            {quickActions.map((action) => {
              const Icon = action.icon;
              return (
                <button
                  key={action.id}
                  onClick={() => handleQuickAction(action)}
                  className="flex items-center space-x-3 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md w-full text-left"
                >
                  <Icon className="w-4 h-4" />
                  <span>{action.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Swipe Indicator */}
      {swipeDirection && (
        <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 bg-black bg-opacity-75 text-white px-4 py-2 rounded-lg text-sm">
          Swiped {swipeDirection}
        </div>
      )}

      {/* Offline Indicator */}
      {!isOnline && (
        <div className="fixed top-16 left-0 right-0 z-30 bg-warning-500 text-white px-4 py-2 text-center text-sm">
          <div className="flex items-center justify-center space-x-2">
            <WifiOff className="w-4 h-4" />
            <span>You're offline. Some features may not be available.</span>
          </div>
        </div>
      )}
    </>
  );
};

export default MobileNavigation;
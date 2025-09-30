import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useApp } from '../../contexts/AppContext';
import { 
  LayoutDashboard,
  Users,
  Package,
  ShoppingCart,
  ShoppingBag,
  BarChart3,
  Settings,
  CreditCard,
  Gift,
  MessageSquare,
  FileText,
  Building2,
  Menu,
  X,
  Shield,
  Database,
  HardDrive,
  Bell,
  Monitor,
  FileText as FileTextIcon,
  Calculator,
  BookOpen,
  TrendingUp,
  PieChart,
  ShoppingBag,
  FileText,
  Building2,
  BarChart3
} from 'lucide-react';

const Sidebar = () => {
  const { user, hasPermission } = useAuth();
  const { sidebarCollapsed, toggleSidebar } = useApp();

  const navigation = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: LayoutDashboard,
      permission: null,
    },
    {
      name: 'Companies',
      href: '/companies',
      icon: Building2,
      permission: 'companies.view',
    },
    {
      name: 'Customers',
      href: '/customers',
      icon: Users,
      permission: 'customers.view',
    },
    {
      name: 'Inventory',
      href: '/inventory',
      icon: Package,
      permission: 'items.view',
    },
    {
      name: 'POS',
      href: '/pos',
      icon: ShoppingCart,
      permission: 'pos.view',
    },
    {
      name: 'Sales',
      href: '/sales',
      icon: ShoppingBag,
      permission: 'sales.view',
    },
    {
      name: 'Purchases',
      href: '/purchases',
      icon: ShoppingBag,
      permission: 'purchases.view',
    },
    {
      name: 'Reports',
      href: '/reports',
      icon: BarChart3,
      permission: 'reports.sales',
    },
    {
      name: 'Accounting',
      href: '/accounting',
      icon: FileText,
      permission: 'accounting.view',
    },
    {
      name: 'Loyalty',
      href: '/loyalty',
      icon: Gift,
      permission: 'loyalty.view',
    },
    {
      name: 'WhatsApp',
      href: '/whatsapp',
      icon: MessageSquare,
      permission: 'whatsapp.view',
    },
    {
      name: 'Payments',
      href: '/payments',
      icon: CreditCard,
      permission: 'payments.view',
    },
    {
      name: 'Settings',
      href: '/settings',
      icon: Settings,
      permission: 'settings.view',
    },
  ];

  const adminNavigation = [
    {
      name: 'System Settings',
      href: '/admin/settings',
      icon: Settings,
      permission: 'admin.settings',
    },
    {
      name: 'Company Settings',
      href: '/admin/company',
      icon: Building2,
      permission: 'admin.company',
    },
    {
      name: 'Print Templates',
      href: '/admin/templates',
      icon: FileTextIcon,
      permission: 'admin.templates',
    },
    {
      name: 'System Info',
      href: '/admin/system',
      icon: Monitor,
      permission: 'admin.system',
    },
    {
      name: 'Database',
      href: '/admin/database',
      icon: Database,
      permission: 'admin.database',
    },
    {
      name: 'Backup & Recovery',
      href: '/admin/backup',
      icon: HardDrive,
      permission: 'admin.backup',
    },
    {
      name: 'Automation',
      href: '/admin/automation',
      icon: Bell,
      permission: 'admin.automation',
    },
  ];

  const accountingNavigation = [
    {
      name: 'Chart of Accounts',
      href: '/accounting/chart-of-accounts',
      icon: Calculator,
      permission: 'accounting.accounts',
    },
    {
      name: 'Journal Entries',
      href: '/accounting/journal-entries',
      icon: BookOpen,
      permission: 'accounting.journal',
    },
    {
      name: 'General Ledger',
      href: '/accounting/general-ledger',
      icon: FileText,
      permission: 'accounting.ledger',
    },
    {
      name: 'Financial Reports',
      href: '/accounting/financial-reports',
      icon: TrendingUp,
      permission: 'accounting.reports',
    },
  ];

  const purchaseNavigation = [
    {
      name: 'Purchase Orders',
      href: '/purchases/orders',
      icon: ShoppingBag,
      permission: 'purchases.orders',
    },
    {
      name: 'Purchase Invoices',
      href: '/purchases/invoices',
      icon: FileText,
      permission: 'purchases.invoices',
    },
    {
      name: 'Vendor Management',
      href: '/purchases/vendors',
      icon: Building2,
      permission: 'purchases.vendors',
    },
    {
      name: 'Purchase Analytics',
      href: '/purchases/analytics',
      icon: BarChart3,
      permission: 'purchases.analytics',
    },
  ];

  const filteredNavigation = navigation.filter(item => 
    !item.permission || hasPermission(item.permission)
  );

  const filteredAdminNavigation = adminNavigation.filter(item => 
    !item.permission || hasPermission(item.permission)
  );

  const filteredAccountingNavigation = accountingNavigation.filter(item => 
    !item.permission || hasPermission(item.permission)
  );

  const filteredPurchaseNavigation = purchaseNavigation.filter(item => 
    !item.permission || hasPermission(item.permission)
  );

  return (
    <>
      {/* Mobile sidebar overlay */}
      {!sidebarCollapsed && (
        <div 
          className="fixed inset-0 z-40 lg:hidden"
          onClick={toggleSidebar}
        >
          <div className="absolute inset-0 bg-gray-600 opacity-75"></div>
        </div>
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0
        ${sidebarCollapsed ? '-translate-x-full lg:translate-x-0 lg:w-16' : 'translate-x-0'}
      `}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
            {!sidebarCollapsed && (
              <h1 className="text-xl font-bold text-gray-900">PINAK-ERP</h1>
            )}
            <button
              onClick={toggleSidebar}
              className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            {filteredNavigation.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) =>
                    `group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                      isActive
                        ? 'bg-primary-100 text-primary-700'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`
                  }
                >
                  <Icon className="flex-shrink-0 h-5 w-5" />
                  {!sidebarCollapsed && (
                    <span className="ml-3">{item.name}</span>
                  )}
                </NavLink>
              );
            })}
            
            {/* Admin Section */}
            {filteredAdminNavigation.length > 0 && (
              <>
                <div className="pt-6">
                  <div className="flex items-center px-3 py-2">
                    <Shield className="flex-shrink-0 h-5 w-5 text-gray-400" />
                    {!sidebarCollapsed && (
                      <span className="ml-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        Administration
                      </span>
                    )}
                  </div>
                </div>
                
                {filteredAdminNavigation.map((item) => {
                  const Icon = item.icon;
                  return (
                    <NavLink
                      key={item.name}
                      to={item.href}
                      className={({ isActive }) =>
                        `group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                          isActive
                            ? 'bg-primary-100 text-primary-700'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                        }`
                      }
                    >
                      <Icon className="flex-shrink-0 h-5 w-5" />
                      {!sidebarCollapsed && (
                        <span className="ml-3">{item.name}</span>
                      )}
                    </NavLink>
                  );
                })}
              </>
            )}

            {/* Accounting Section */}
            {filteredAccountingNavigation.length > 0 && (
              <>
                <div className="pt-6">
                  <div className="flex items-center px-3 py-2">
                    <Calculator className="flex-shrink-0 h-5 w-5 text-gray-400" />
                    {!sidebarCollapsed && (
                      <span className="ml-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        Accounting
                      </span>
                    )}
                  </div>
                </div>
                
                {filteredAccountingNavigation.map((item) => {
                  const Icon = item.icon;
                  return (
                    <NavLink
                      key={item.name}
                      to={item.href}
                      className={({ isActive }) =>
                        `group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                          isActive
                            ? 'bg-primary-100 text-primary-700'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                        }`
                      }
                    >
                      <Icon className="flex-shrink-0 h-5 w-5" />
                      {!sidebarCollapsed && (
                        <span className="ml-3">{item.name}</span>
                      )}
                    </NavLink>
                  );
                })}
              </>
            )}

            {/* Purchase Section */}
            {filteredPurchaseNavigation.length > 0 && (
              <>
                <div className="pt-6">
                  <div className="flex items-center px-3 py-2">
                    <ShoppingBag className="flex-shrink-0 h-5 w-5 text-gray-400" />
                    {!sidebarCollapsed && (
                      <span className="ml-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        Purchases
                      </span>
                    )}
                  </div>
                </div>
                
                {filteredPurchaseNavigation.map((item) => {
                  const Icon = item.icon;
                  return (
                    <NavLink
                      key={item.name}
                      to={item.href}
                      className={({ isActive }) =>
                        `group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                          isActive
                            ? 'bg-primary-100 text-primary-700'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                        }`
                      }
                    >
                      <Icon className="flex-shrink-0 h-5 w-5" />
                      {!sidebarCollapsed && (
                        <span className="ml-3">{item.name}</span>
                      )}
                    </NavLink>
                  );
                })}
              </>
            )}
          </nav>

          {/* User info */}
          {!sidebarCollapsed && (
            <div className="px-4 py-4 border-t border-gray-200">
              <div className="flex items-center space-x-3">
                <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center">
                  <span className="text-sm font-medium text-primary-600">
                    {user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {user?.full_name || user?.username}
                  </p>
                  <p className="text-xs text-gray-500 truncate">
                    {user?.email}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default Sidebar;
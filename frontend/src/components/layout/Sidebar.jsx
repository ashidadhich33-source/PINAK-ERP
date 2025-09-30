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
  BarChart3,
  Package,
  Settings,
  Award,
  Star,
  MessageSquare,
  Target,
  Zap,
  Globe,
  Map,
  Calculator,
  CreditCard,
  Store,
  Monitor,
  Receipt,
  Wallet,
  DollarSign,
  Database,
  Zap
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
      name: 'Enhanced Sales',
      href: '/sales/enhanced',
      icon: FileText,
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
      icon: Calculator,
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

  const reportingNavigation = [
    {
      name: 'Financial Reports',
      href: '/reports/financial',
      icon: TrendingUp,
      permission: 'reports.financial',
    },
    {
      name: 'Stock Reports',
      href: '/reports/stock',
      icon: Package,
      permission: 'reports.stock',
    },
    {
      name: 'Dashboard Reports',
      href: '/reports/dashboards',
      icon: BarChart3,
      permission: 'reports.dashboards',
    },
    {
      name: 'Advanced Reporting',
      href: '/reports/advanced',
      icon: Settings,
      permission: 'reports.advanced',
    },
  ];

  const loyaltyNavigation = [
    {
      name: 'Loyalty Programs',
      href: '/loyalty/programs',
      icon: Award,
      permission: 'loyalty.programs',
    },
    {
      name: 'Loyalty Transactions',
      href: '/loyalty/transactions',
      icon: Star,
      permission: 'loyalty.transactions',
    },
  ];

  const marketingNavigation = [
    {
      name: 'WhatsApp Integration',
      href: '/marketing/whatsapp',
      icon: MessageSquare,
      permission: 'marketing.whatsapp',
    },
    {
      name: 'Marketing Automation',
      href: '/marketing/automation',
      icon: Target,
      permission: 'marketing.automation',
    },
  ];

  const localizationNavigation = [
    {
      name: 'Indian Geography',
      href: '/localization/geography',
      icon: Map,
      permission: 'localization.geography',
    },
    {
      name: 'Indian GST',
      href: '/localization/gst',
      icon: Calculator,
      permission: 'localization.gst',
    },
    {
      name: 'Indian Banking',
      href: '/localization/banking',
      icon: CreditCard,
      permission: 'localization.banking',
    },
  ];

  const storeNavigation = [
    {
      name: 'Store Management',
      href: '/store/management',
      icon: Store,
      permission: 'store.management',
    },
    {
      name: 'POS Sessions',
      href: '/store/sessions',
      icon: Monitor,
      permission: 'store.sessions',
    },
    {
      name: 'POS Receipts',
      href: '/store/receipts',
      icon: Receipt,
      permission: 'store.receipts',
    },
  ];

  const paymentNavigation = [
    {
      name: 'Payment Management',
      href: '/payment/management',
      icon: CreditCard,
      permission: 'payment.management',
    },
    {
      name: 'Payment Modes',
      href: '/payment/modes',
      icon: Wallet,
      permission: 'payment.modes',
    },
    {
      name: 'Financial Transactions',
      href: '/payment/transactions',
      icon: Database,
      permission: 'payment.transactions',
    },
    {
      name: 'Financial Integration',
      href: '/payment/integration',
      icon: Zap,
      permission: 'payment.integration',
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

  const filteredReportingNavigation = reportingNavigation.filter(item => 
    !item.permission || hasPermission(item.permission)
  );

  const filteredLoyaltyNavigation = loyaltyNavigation.filter(item => 
    !item.permission || hasPermission(item.permission)
  );

  const filteredMarketingNavigation = marketingNavigation.filter(item => 
    !item.permission || hasPermission(item.permission)
  );

  const filteredLocalizationNavigation = localizationNavigation.filter(item => 
    !item.permission || hasPermission(item.permission)
  );

  const filteredStoreNavigation = storeNavigation.filter(item => 
    !item.permission || hasPermission(item.permission)
  );

  const filteredPaymentNavigation = paymentNavigation.filter(item => 
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

            {/* Reporting Section */}
            {filteredReportingNavigation.length > 0 && (
              <>
                <div className="pt-6">
                  <div className="flex items-center px-3 py-2">
                    <BarChart3 className="flex-shrink-0 h-5 w-5 text-gray-400" />
                    {!sidebarCollapsed && (
                      <span className="ml-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        Reporting
                      </span>
                    )}
                  </div>
                </div>
                
                {filteredReportingNavigation.map((item) => {
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

            {/* Loyalty Section */}
            {filteredLoyaltyNavigation.length > 0 && (
              <>
                <div className="pt-6">
                  <div className="flex items-center px-3 py-2">
                    <Award className="flex-shrink-0 h-5 w-5 text-gray-400" />
                    {!sidebarCollapsed && (
                      <span className="ml-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        Loyalty
                      </span>
                    )}
                  </div>
                </div>
                
                {filteredLoyaltyNavigation.map((item) => {
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

            {/* Marketing Section */}
            {filteredMarketingNavigation.length > 0 && (
              <>
                <div className="pt-6">
                  <div className="flex items-center px-3 py-2">
                    <Target className="flex-shrink-0 h-5 w-5 text-gray-400" />
                    {!sidebarCollapsed && (
                      <span className="ml-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        Marketing
                      </span>
                    )}
                  </div>
                </div>
                
                {filteredMarketingNavigation.map((item) => {
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

            {/* Localization Section */}
            {filteredLocalizationNavigation.length > 0 && (
              <>
                <div className="pt-6">
                  <div className="flex items-center px-3 py-2">
                    <Globe className="flex-shrink-0 h-5 w-5 text-gray-400" />
                    {!sidebarCollapsed && (
                      <span className="ml-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        Localization
                      </span>
                    )}
                  </div>
                </div>
                
                {filteredLocalizationNavigation.map((item) => {
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

            {/* Store Section */}
            {filteredStoreNavigation.length > 0 && (
              <>
                <div className="pt-6">
                  <div className="flex items-center px-3 py-2">
                    <Store className="flex-shrink-0 h-5 w-5 text-gray-400" />
                    {!sidebarCollapsed && (
                      <span className="ml-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        Store & POS
                      </span>
                    )}
                  </div>
                </div>
                
                {filteredStoreNavigation.map((item) => {
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

            {/* Payment Section */}
            {filteredPaymentNavigation.length > 0 && (
              <>
                <div className="pt-6">
                  <div className="flex items-center px-3 py-2">
                    <DollarSign className="flex-shrink-0 h-5 w-5 text-gray-400" />
                    {!sidebarCollapsed && (
                      <span className="ml-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        Payment & Finance
                      </span>
                    )}
                  </div>
                </div>
                
                {filteredPaymentNavigation.map((item) => {
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
import React, { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './contexts/AppContext';
import { AuthProvider } from './contexts/AuthContext';
import { PosProvider } from './contexts/PosContext';
import Layout from './components/layout/Layout';
import ProtectedRoute from './components/auth/ProtectedRoute';
import LoadingSpinner from './components/common/LoadingSpinner';
import LazyComponent from './components/common/LazyComponent';

// Lazy load components for better performance
const Login = lazy(() => import('./pages/auth/Login'));
const Dashboard = lazy(() => import('./pages/Dashboard'));

// Companies routes
const CompaniesList = lazy(() => import('./pages/companies/CompaniesList'));
const CompanyDetails = lazy(() => import('./pages/companies/CompanyDetails'));
const CompanyFormPage = lazy(() => import('./pages/companies/CompanyFormPage'));

// Customers routes
const CustomersList = lazy(() => import('./pages/customers/CustomersList'));
const CustomerDetails = lazy(() => import('./pages/customers/CustomerDetails'));
const CustomerFormPage = lazy(() => import('./pages/customers/CustomerFormPage'));

// Inventory routes
const InventoryList = lazy(() => import('./pages/inventory/InventoryList'));
const ItemDetails = lazy(() => import('./pages/inventory/ItemDetails'));
const ItemFormPage = lazy(() => import('./pages/inventory/ItemFormPage'));

// POS routes
const POSDashboard = lazy(() => import('./pages/pos/POSDashboard'));
const POSTerminal = lazy(() => import('./pages/pos/POSTerminal'));

// Sales routes
const SalesList = lazy(() => import('./pages/sales/SalesList'));

// Reports routes
const ReportsDashboard = lazy(() => import('./pages/reports/ReportsDashboard'));

// Admin routes
const SettingsDashboard = lazy(() => import('./pages/admin/SettingsDashboard'));
const CompanySettings = lazy(() => import('./pages/admin/CompanySettings'));
const PrintTemplates = lazy(() => import('./pages/admin/PrintTemplates'));
const SystemInfo = lazy(() => import('./pages/admin/SystemInfo'));
const DatabaseManagement = lazy(() => import('./pages/admin/DatabaseManagement'));
const BackupRecovery = lazy(() => import('./pages/admin/BackupRecovery'));
const AutomationDashboard = lazy(() => import('./pages/admin/AutomationDashboard'));

// Accounting routes
const ChartOfAccounts = lazy(() => import('./pages/accounting/ChartOfAccounts'));
const JournalEntries = lazy(() => import('./pages/accounting/JournalEntries'));
const GeneralLedger = lazy(() => import('./pages/accounting/GeneralLedger'));
const AccountingReports = lazy(() => import('./pages/accounting/FinancialReports'));

// Purchase routes
const PurchaseOrders = lazy(() => import('./pages/purchases/PurchaseOrders'));
const PurchaseInvoices = lazy(() => import('./pages/purchases/PurchaseInvoices'));
const VendorManagement = lazy(() => import('./pages/purchases/VendorManagement'));
const PurchaseAnalytics = lazy(() => import('./pages/purchases/PurchaseAnalytics'));

// Reporting routes
const FinancialReports = lazy(() => import('./pages/reports/FinancialReports'));
const StockReports = lazy(() => import('./pages/reports/StockReports'));
const DashboardReports = lazy(() => import('./pages/reports/DashboardReports'));
const AdvancedReporting = lazy(() => import('./pages/reports/AdvancedReporting'));

// Loyalty routes
const LoyaltyPrograms = lazy(() => import('./pages/loyalty/LoyaltyPrograms'));
const LoyaltyTransactions = lazy(() => import('./pages/loyalty/LoyaltyTransactions'));

// Marketing routes
const WhatsAppIntegration = lazy(() => import('./pages/marketing/WhatsAppIntegration'));
const MarketingAutomation = lazy(() => import('./pages/marketing/MarketingAutomation'));

// Localization routes
const IndianGeography = lazy(() => import('./pages/localization/IndianGeography'));
const IndianGST = lazy(() => import('./pages/localization/IndianGST'));
const IndianBanking = lazy(() => import('./pages/localization/IndianBanking'));

// Store routes
const StoreManagement = lazy(() => import('./pages/store/StoreManagement'));
const POSSessions = lazy(() => import('./pages/store/POSSessions'));
const POSReceipts = lazy(() => import('./pages/store/POSReceipts'));

// Payment routes
const PaymentManagement = lazy(() => import('./pages/payment/PaymentManagement'));
const PaymentModes = lazy(() => import('./pages/payment/PaymentModes'));
const FinancialTransactions = lazy(() => import('./pages/payment/FinancialTransactions'));
const FinancialIntegration = lazy(() => import('./pages/payment/FinancialIntegration'));

function App() {
  return (
    <AppProvider>
      <AuthProvider>
        <PosProvider>
          <div className="App">
            <Routes>
              {/* Public Routes */}
              <Route path="/login" element={
                <LazyComponent>
                  <Login />
                </LazyComponent>
              } />
              
              {/* Protected Routes */}
              <Route
                path="/*"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Routes>
                      <Route path="/" element={<Navigate to="/dashboard" replace />} />
                      <Route path="/dashboard" element={
                        <LazyComponent>
                          <Dashboard />
                        </LazyComponent>
                      } />
                      
                      {/* Companies routes */}
                      <Route path="/companies" element={
                        <LazyComponent>
                          <CompaniesList />
                        </LazyComponent>
                      } />
                      <Route path="/companies/new" element={
                        <LazyComponent>
                          <CompanyFormPage />
                        </LazyComponent>
                      } />
                      <Route path="/companies/:id" element={
                        <LazyComponent>
                          <CompanyDetails />
                        </LazyComponent>
                      } />
                      <Route path="/companies/:id/edit" element={
                        <LazyComponent>
                          <CompanyFormPage />
                        </LazyComponent>
                      } />
                      
                      {/* Customers routes */}
                      <Route path="/customers" element={
                        <LazyComponent>
                          <CustomersList />
                        </LazyComponent>
                      } />
                      <Route path="/customers/new" element={
                        <LazyComponent>
                          <CustomerFormPage />
                        </LazyComponent>
                      } />
                      <Route path="/customers/:id" element={
                        <LazyComponent>
                          <CustomerDetails />
                        </LazyComponent>
                      } />
                      <Route path="/customers/:id/edit" element={
                        <LazyComponent>
                          <CustomerFormPage />
                        </LazyComponent>
                      } />
                      
                      {/* Inventory routes */}
                      <Route path="/inventory" element={
                        <LazyComponent>
                          <InventoryList />
                        </LazyComponent>
                      } />
                      <Route path="/inventory/items/new" element={
                        <LazyComponent>
                          <ItemFormPage />
                        </LazyComponent>
                      } />
                      <Route path="/inventory/items/:id" element={
                        <LazyComponent>
                          <ItemDetails />
                        </LazyComponent>
                      } />
                      <Route path="/inventory/items/:id/edit" element={
                        <LazyComponent>
                          <ItemFormPage />
                        </LazyComponent>
                      } />
                      
                      {/* POS routes */}
                      <Route path="/pos" element={
                        <LazyComponent>
                          <POSDashboard />
                        </LazyComponent>
                      } />
                      <Route path="/pos/terminal" element={
                        <LazyComponent>
                          <POSTerminal />
                        </LazyComponent>
                      } />
                      
                      {/* Sales routes */}
                      <Route path="/sales" element={
                        <LazyComponent>
                          <SalesList />
                        </LazyComponent>
                      } />
                      
                      {/* Reports routes */}
                      <Route path="/reports" element={
                        <LazyComponent>
                          <ReportsDashboard />
                        </LazyComponent>
                      } />
                      
                      {/* Admin routes */}
                      <Route path="/admin/settings" element={
                        <LazyComponent>
                          <SettingsDashboard />
                        </LazyComponent>
                      } />
                      <Route path="/admin/company" element={
                        <LazyComponent>
                          <CompanySettings />
                        </LazyComponent>
                      } />
                      <Route path="/admin/templates" element={
                        <LazyComponent>
                          <PrintTemplates />
                        </LazyComponent>
                      } />
                      <Route path="/admin/system" element={
                        <LazyComponent>
                          <SystemInfo />
                        </LazyComponent>
                      } />
                      <Route path="/admin/database" element={
                        <LazyComponent>
                          <DatabaseManagement />
                        </LazyComponent>
                      } />
                      <Route path="/admin/backup" element={
                        <LazyComponent>
                          <BackupRecovery />
                        </LazyComponent>
                      } />
                      <Route path="/admin/automation" element={
                        <LazyComponent>
                          <AutomationDashboard />
                        </LazyComponent>
                      } />
                      
                      {/* Accounting routes */}
                      <Route path="/accounting/chart-of-accounts" element={
                        <LazyComponent>
                          <ChartOfAccounts />
                        </LazyComponent>
                      } />
                      <Route path="/accounting/journal-entries" element={
                        <LazyComponent>
                          <JournalEntries />
                        </LazyComponent>
                      } />
                      <Route path="/accounting/general-ledger" element={
                        <LazyComponent>
                          <GeneralLedger />
                        </LazyComponent>
                      } />
                      <Route path="/accounting/financial-reports" element={
                        <LazyComponent>
                          <AccountingReports />
                        </LazyComponent>
                      } />
                      
                      {/* Purchase routes */}
                      <Route path="/purchases/orders" element={
                        <LazyComponent>
                          <PurchaseOrders />
                        </LazyComponent>
                      } />
                      <Route path="/purchases/invoices" element={
                        <LazyComponent>
                          <PurchaseInvoices />
                        </LazyComponent>
                      } />
                      <Route path="/purchases/vendors" element={
                        <LazyComponent>
                          <VendorManagement />
                        </LazyComponent>
                      } />
                      <Route path="/purchases/analytics" element={
                        <LazyComponent>
                          <PurchaseAnalytics />
                        </LazyComponent>
                      } />
                      
                      {/* Reporting routes */}
                      <Route path="/reports/financial" element={
                        <LazyComponent>
                          <FinancialReports />
                        </LazyComponent>
                      } />
                      <Route path="/reports/stock" element={
                        <LazyComponent>
                          <StockReports />
                        </LazyComponent>
                      } />
                      <Route path="/reports/dashboards" element={
                        <LazyComponent>
                          <DashboardReports />
                        </LazyComponent>
                      } />
                      <Route path="/reports/advanced" element={
                        <LazyComponent>
                          <AdvancedReporting />
                        </LazyComponent>
                      } />
                      
                      {/* Loyalty routes */}
                      <Route path="/loyalty/programs" element={
                        <LazyComponent>
                          <LoyaltyPrograms />
                        </LazyComponent>
                      } />
                      <Route path="/loyalty/transactions" element={
                        <LazyComponent>
                          <LoyaltyTransactions />
                        </LazyComponent>
                      } />
                      
                      {/* Marketing routes */}
                      <Route path="/marketing/whatsapp" element={
                        <LazyComponent>
                          <WhatsAppIntegration />
                        </LazyComponent>
                      } />
                      <Route path="/marketing/automation" element={
                        <LazyComponent>
                          <MarketingAutomation />
                        </LazyComponent>
                      } />
                      
                      {/* Localization routes */}
                      <Route path="/localization/geography" element={
                        <LazyComponent>
                          <IndianGeography />
                        </LazyComponent>
                      } />
                      <Route path="/localization/gst" element={
                        <LazyComponent>
                          <IndianGST />
                        </LazyComponent>
                      } />
                      <Route path="/localization/banking" element={
                        <LazyComponent>
                          <IndianBanking />
                        </LazyComponent>
                      } />
                      
                      {/* Store routes */}
                      <Route path="/store/management" element={
                        <LazyComponent>
                          <StoreManagement />
                        </LazyComponent>
                      } />
                      <Route path="/store/sessions" element={
                        <LazyComponent>
                          <POSSessions />
                        </LazyComponent>
                      } />
                      <Route path="/store/receipts" element={
                        <LazyComponent>
                          <POSReceipts />
                        </LazyComponent>
                      } />
                      
                      {/* Payment routes */}
                      <Route path="/payment/management" element={
                        <LazyComponent>
                          <PaymentManagement />
                        </LazyComponent>
                      } />
                      <Route path="/payment/modes" element={
                        <LazyComponent>
                          <PaymentModes />
                        </LazyComponent>
                      } />
                      <Route path="/payment/transactions" element={
                        <LazyComponent>
                          <FinancialTransactions />
                        </LazyComponent>
                      } />
                      <Route path="/payment/integration" element={
                        <LazyComponent>
                          <FinancialIntegration />
                        </LazyComponent>
                      } />
                      
                      {/* Add more routes here as we build them */}
                      </Routes>
                    </Layout>
                  </ProtectedRoute>
                }
              />
            </Routes>
          </div>
        </PosProvider>
      </AuthProvider>
    </AppProvider>
  );
}

export default App;
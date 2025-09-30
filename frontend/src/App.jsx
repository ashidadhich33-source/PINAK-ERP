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
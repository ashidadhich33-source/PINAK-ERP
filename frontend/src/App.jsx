import { Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './contexts/AppContext';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/layout/Layout';
import Login from './pages/auth/Login';
import Dashboard from './pages/Dashboard';
import ProtectedRoute from './components/auth/ProtectedRoute';
import LoadingSpinner from './components/common/LoadingSpinner';

// Companies routes
import CompaniesList from './pages/companies/CompaniesList';
import CompanyDetails from './pages/companies/CompanyDetails';
import CompanyFormPage from './pages/companies/CompanyFormPage';

// Customers routes
import CustomersList from './pages/customers/CustomersList';
import CustomerDetails from './pages/customers/CustomerDetails';
import CustomerFormPage from './pages/customers/CustomerFormPage';

// Inventory routes
import InventoryList from './pages/inventory/InventoryList';
import ItemDetails from './pages/inventory/ItemDetails';
import ItemFormPage from './pages/inventory/ItemFormPage';

function App() {
  return (
    <AppProvider>
      <AuthProvider>
        <div className="App">
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            
            {/* Protected Routes */}
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Routes>
                      <Route path="/" element={<Navigate to="/dashboard" replace />} />
                      <Route path="/dashboard" element={<Dashboard />} />
                      
                      {/* Companies routes */}
                      <Route path="/companies" element={<CompaniesList />} />
                      <Route path="/companies/new" element={<CompanyFormPage />} />
                      <Route path="/companies/:id" element={<CompanyDetails />} />
                      <Route path="/companies/:id/edit" element={<CompanyFormPage />} />
                      
                      {/* Customers routes */}
                      <Route path="/customers" element={<CustomersList />} />
                      <Route path="/customers/new" element={<CustomerFormPage />} />
                      <Route path="/customers/:id" element={<CustomerDetails />} />
                      <Route path="/customers/:id/edit" element={<CustomerFormPage />} />
                      
                      {/* Inventory routes */}
                      <Route path="/inventory" element={<InventoryList />} />
                      <Route path="/inventory/items/new" element={<ItemFormPage />} />
                      <Route path="/inventory/items/:id" element={<ItemDetails />} />
                      <Route path="/inventory/items/:id/edit" element={<ItemFormPage />} />
                      
                      {/* Add more routes here as we build them */}
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </div>
      </AuthProvider>
    </AppProvider>
  );
}

export default App;
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import { customersService } from '../../services/customersService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import DataTable from '../../components/common/DataTable';
import { 
  Plus, 
  Search, 
  Download, 
  Upload,
  Users,
  Eye,
  Edit,
  Trash2,
  Phone,
  Mail,
  MapPin
} from 'lucide-react';

const CustomersList = () => {
  const { addNotification } = useApp();
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    status: 'all',
    group: 'all',
    sortBy: 'name',
    sortOrder: 'asc',
  });

  // Fetch customers
  const fetchCustomers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        search: searchTerm,
        status: filters.status !== 'all' ? filters.status : undefined,
        group: filters.group !== 'all' ? filters.group : undefined,
        sort_by: filters.sortBy,
        sort_order: filters.sortOrder,
      };
      
      const data = await customersService.getCustomers(params);
      setCustomers(data);
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
    fetchCustomers();
  }, [searchTerm, filters]);

  // Handle search
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  // Handle filter change
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Handle delete customer
  const handleDelete = async (customerId) => {
    if (!window.confirm('Are you sure you want to delete this customer?')) {
      return;
    }

    try {
      await customersService.deleteCustomer(customerId);
      setCustomers(prev => prev.filter(customer => customer.id !== customerId));
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Customer deleted successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle toggle status
  const handleToggleStatus = async (customerId) => {
    try {
      await customersService.toggleCustomerStatus(customerId);
      setCustomers(prev => prev.map(customer => 
        customer.id === customerId 
          ? { ...customer, is_active: !customer.is_active }
          : customer
      ));
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Customer status updated successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle export
  const handleExport = async () => {
    try {
      await customersService.exportCustomers('csv', filters);
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: 'Customers export will be downloaded shortly',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Table columns
  const columns = [
    {
      key: 'name',
      label: 'Customer Name',
      render: (customer) => (
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <Users className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <p className="font-medium text-gray-900">{customer.name}</p>
            <p className="text-sm text-gray-500">{customer.email}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'phone',
      label: 'Phone',
      render: (customer) => (
        <div className="flex items-center space-x-1">
          <Phone className="w-4 h-4 text-gray-400" />
          <span>{customer.phone || '-'}</span>
        </div>
      ),
    },
    {
      key: 'address',
      label: 'Address',
      render: (customer) => (
        <div className="max-w-xs">
          <div className="flex items-center space-x-1">
            <MapPin className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-900 truncate">
              {customer.address || '-'}
            </span>
          </div>
          {customer.city && (
            <p className="text-xs text-gray-500">{customer.city}</p>
          )}
        </div>
      ),
    },
    {
      key: 'group',
      label: 'Group',
      render: (customer) => (
        <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-secondary-100 text-secondary-800">
          {customer.group?.name || 'No Group'}
        </span>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (customer) => (
        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
          customer.is_active 
            ? 'bg-success-100 text-success-800' 
            : 'bg-danger-100 text-danger-800'
        }`}>
          {customer.is_active ? 'Active' : 'Inactive'}
        </span>
      ),
    },
    {
      key: 'created_at',
      label: 'Created',
      render: (customer) => new Date(customer.created_at).toLocaleDateString(),
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (customer) => (
        <div className="flex items-center space-x-2">
          <Link
            to={`/customers/${customer.id}`}
            className="text-primary-600 hover:text-primary-900"
          >
            <Eye className="w-4 h-4" />
          </Link>
          <Link
            to={`/customers/${customer.id}/edit`}
            className="text-secondary-600 hover:text-secondary-900"
          >
            <Edit className="w-4 h-4" />
          </Link>
          <button
            onClick={() => handleToggleStatus(customer.id)}
            className={`${
              customer.is_active 
                ? 'text-danger-600 hover:text-danger-900' 
                : 'text-success-600 hover:text-success-900'
            }`}
          >
            {customer.is_active ? 'Deactivate' : 'Activate'}
          </button>
          <button
            onClick={() => handleDelete(customer.id)}
            className="text-danger-600 hover:text-danger-900"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      ),
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading customers..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Customers</h1>
          <p className="text-gray-600">Manage your customer information</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={handleExport}
            className="flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Export</span>
          </Button>
          <Button
            variant="outline"
            className="flex items-center space-x-2"
          >
            <Upload className="w-4 h-4" />
            <span>Import</span>
          </Button>
          <Link to="/customers/new">
            <Button className="flex items-center space-x-2">
              <Plus className="w-4 h-4" />
              <span>Add Customer</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <Input
              placeholder="Search customers..."
              value={searchTerm}
              onChange={handleSearch}
              className="pl-10"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
          </div>
          
          <div>
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="form-input"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
          
          <div>
            <select
              value={filters.sortBy}
              onChange={(e) => handleFilterChange('sortBy', e.target.value)}
              className="form-input"
            >
              <option value="name">Sort by Name</option>
              <option value="created_at">Sort by Date</option>
              <option value="email">Sort by Email</option>
            </select>
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert type="danger" title="Error">
          {error}
        </Alert>
      )}

      {/* Data Table */}
      <div className="bg-white rounded-lg shadow">
        <DataTable
          data={customers}
          columns={columns}
          loading={loading}
          emptyMessage="No customers found"
        />
      </div>
    </div>
  );
};

export default CustomersList;
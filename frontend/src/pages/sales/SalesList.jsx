import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import { salesService } from '../../services/salesService';
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
  ShoppingBag,
  Eye,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  Clock,
  DollarSign
} from 'lucide-react';

const SalesList = () => {
  const { addNotification } = useApp();
  const [sales, setSales] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    status: 'all',
    dateRange: 'all',
    sortBy: 'created_at',
    sortOrder: 'desc',
  });

  // Fetch sales
  const fetchSales = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        search: searchTerm,
        status: filters.status !== 'all' ? filters.status : undefined,
        date_range: filters.dateRange !== 'all' ? filters.dateRange : undefined,
        sort_by: filters.sortBy,
        sort_order: filters.sortOrder,
      };
      
      const data = await salesService.getSales(params);
      setSales(data);
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
    fetchSales();
  }, [searchTerm, filters]);

  // Handle search
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  // Handle filter change
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Handle delete sale
  const handleDelete = async (saleId) => {
    if (!window.confirm('Are you sure you want to delete this sale?')) {
      return;
    }

    try {
      await salesService.deleteSale(saleId);
      setSales(prev => prev.filter(sale => sale.id !== saleId));
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Sale deleted successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle cancel sale
  const handleCancel = async (saleId) => {
    if (!window.confirm('Are you sure you want to cancel this sale?')) {
      return;
    }

    try {
      await salesService.cancelSale(saleId);
      setSales(prev => prev.map(sale => 
        sale.id === saleId 
          ? { ...sale, status: 'cancelled' }
          : sale
      ));
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Sale cancelled successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle complete sale
  const handleComplete = async (saleId) => {
    try {
      await salesService.completeSale(saleId);
      setSales(prev => prev.map(sale => 
        sale.id === saleId 
          ? { ...sale, status: 'completed' }
          : sale
      ));
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Sale completed successfully',
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
      await salesService.exportSales('csv', filters);
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: 'Sales export will be downloaded shortly',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Get status icon and color
  const getStatusInfo = (status) => {
    switch (status) {
      case 'completed':
        return {
          icon: CheckCircle,
          color: 'text-success-600',
          bgColor: 'bg-success-100',
        };
      case 'pending':
        return {
          icon: Clock,
          color: 'text-warning-600',
          bgColor: 'bg-warning-100',
        };
      case 'cancelled':
        return {
          icon: XCircle,
          color: 'text-danger-600',
          bgColor: 'bg-danger-100',
        };
      default:
        return {
          icon: Clock,
          color: 'text-gray-600',
          bgColor: 'bg-gray-100',
        };
    }
  };

  // Table columns
  const columns = [
    {
      key: 'sale_number',
      label: 'Sale Number',
      render: (sale) => (
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <ShoppingBag className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <p className="font-medium text-gray-900">#{sale.sale_number}</p>
            <p className="text-sm text-gray-500">{new Date(sale.created_at).toLocaleDateString()}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'customer',
      label: 'Customer',
      render: (sale) => (
        <div>
          <p className="font-medium text-gray-900">{sale.customer?.name || 'Walk-in Customer'}</p>
          <p className="text-sm text-gray-500">{sale.customer?.email || '-'}</p>
        </div>
      ),
    },
    {
      key: 'items',
      label: 'Items',
      render: (sale) => (
        <div>
          <p className="font-medium text-gray-900">{sale.items_count || 0} items</p>
          <p className="text-sm text-gray-500">Total: ₹{sale.total_amount}</p>
        </div>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (sale) => {
        const statusInfo = getStatusInfo(sale.status);
        const Icon = statusInfo.icon;
        return (
          <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
            <Icon className="w-3 h-3 mr-1" />
            {sale.status}
          </span>
        );
      },
    },
    {
      key: 'payment_status',
      label: 'Payment',
      render: (sale) => (
        <div className="flex items-center space-x-2">
          <DollarSign className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-900">
            {sale.payment_status === 'paid' ? 'Paid' : 'Pending'}
          </span>
        </div>
      ),
    },
    {
      key: 'created_at',
      label: 'Date',
      render: (sale) => new Date(sale.created_at).toLocaleDateString(),
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (sale) => (
        <div className="flex items-center space-x-2">
          <Link
            to={`/sales/${sale.id}`}
            className="text-primary-600 hover:text-primary-900"
          >
            <Eye className="w-4 h-4" />
          </Link>
          {sale.status === 'pending' && (
            <>
              <Link
                to={`/sales/${sale.id}/edit`}
                className="text-secondary-600 hover:text-secondary-900"
              >
                <Edit className="w-4 h-4" />
              </Link>
              <button
                onClick={() => handleComplete(sale.id)}
                className="text-success-600 hover:text-success-900"
              >
                <CheckCircle className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleCancel(sale.id)}
                className="text-danger-600 hover:text-danger-900"
              >
                <XCircle className="w-4 h-4" />
              </button>
            </>
          )}
          <button
            onClick={() => handleDelete(sale.id)}
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
        <LoadingSpinner size="lg" text="Loading sales..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Sales</h1>
          <p className="text-gray-600">Manage your sales and orders</p>
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
          <Link to="/sales/new">
            <Button className="flex items-center space-x-2">
              <Plus className="w-4 h-4" />
              <span>New Sale</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <Input
              placeholder="Search sales..."
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
              <option value="pending">Pending</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          
          <div>
            <select
              value={filters.sortBy}
              onChange={(e) => handleFilterChange('sortBy', e.target.value)}
              className="form-input"
            >
              <option value="created_at">Sort by Date</option>
              <option value="total_amount">Sort by Amount</option>
              <option value="sale_number">Sort by Number</option>
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
          data={sales}
          columns={columns}
          loading={loading}
          emptyMessage="No sales found"
        />
      </div>
    </div>
  );
};

export default SalesList;
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import { inventoryService } from '../../services/inventoryService';
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
  Package,
  Eye,
  Edit,
  Trash2,
  AlertTriangle,
  TrendingUp,
  TrendingDown
} from 'lucide-react';

const InventoryList = () => {
  const { addNotification } = useApp();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    status: 'all',
    category: 'all',
    brand: 'all',
    sortBy: 'name',
    sortOrder: 'asc',
  });

  // Fetch items
  const fetchItems = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        search: searchTerm,
        status: filters.status !== 'all' ? filters.status : undefined,
        category: filters.category !== 'all' ? filters.category : undefined,
        brand: filters.brand !== 'all' ? filters.brand : undefined,
        sort_by: filters.sortBy,
        sort_order: filters.sortOrder,
      };
      
      const data = await inventoryService.getItems(params);
      setItems(data);
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
    fetchItems();
  }, [searchTerm, filters]);

  // Handle search
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  // Handle filter change
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Handle delete item
  const handleDelete = async (itemId) => {
    if (!window.confirm('Are you sure you want to delete this item?')) {
      return;
    }

    try {
      await inventoryService.deleteItem(itemId);
      setItems(prev => prev.filter(item => item.id !== itemId));
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Item deleted successfully',
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
  const handleToggleStatus = async (itemId) => {
    try {
      await inventoryService.toggleItemStatus(itemId);
      setItems(prev => prev.map(item => 
        item.id === itemId 
          ? { ...item, is_active: !item.is_active }
          : item
      ));
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Item status updated successfully',
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
      await inventoryService.exportItems('csv', filters);
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: 'Inventory export will be downloaded shortly',
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
      label: 'Item Name',
      render: (item) => (
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <Package className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <p className="font-medium text-gray-900">{item.name}</p>
            <p className="text-sm text-gray-500">{item.sku}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'category',
      label: 'Category',
      render: (item) => (
        <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-secondary-100 text-secondary-800">
          {item.category?.name || 'No Category'}
        </span>
      ),
    },
    {
      key: 'brand',
      label: 'Brand',
      render: (item) => item.brand?.name || '-',
    },
    {
      key: 'stock',
      label: 'Stock',
      render: (item) => (
        <div className="flex items-center space-x-2">
          <span className={`font-medium ${
            item.stock_quantity <= item.min_stock_level 
              ? 'text-danger-600' 
              : item.stock_quantity <= item.min_stock_level * 1.5 
                ? 'text-warning-600' 
                : 'text-success-600'
          }`}>
            {item.stock_quantity}
          </span>
          <span className="text-sm text-gray-500">/ {item.min_stock_level}</span>
          {item.stock_quantity <= item.min_stock_level && (
            <AlertTriangle className="w-4 h-4 text-danger-500" />
          )}
        </div>
      ),
    },
    {
      key: 'price',
      label: 'Price',
      render: (item) => (
        <div>
          <p className="font-medium text-gray-900">₹{item.selling_price}</p>
          <p className="text-sm text-gray-500">Cost: ₹{item.cost_price}</p>
        </div>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (item) => (
        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
          item.is_active 
            ? 'bg-success-100 text-success-800' 
            : 'bg-danger-100 text-danger-800'
        }`}>
          {item.is_active ? 'Active' : 'Inactive'}
        </span>
      ),
    },
    {
      key: 'created_at',
      label: 'Created',
      render: (item) => new Date(item.created_at).toLocaleDateString(),
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (item) => (
        <div className="flex items-center space-x-2">
          <Link
            to={`/inventory/items/${item.id}`}
            className="text-primary-600 hover:text-primary-900"
          >
            <Eye className="w-4 h-4" />
          </Link>
          <Link
            to={`/inventory/items/${item.id}/edit`}
            className="text-secondary-600 hover:text-secondary-900"
          >
            <Edit className="w-4 h-4" />
          </Link>
          <button
            onClick={() => handleToggleStatus(item.id)}
            className={`${
              item.is_active 
                ? 'text-danger-600 hover:text-danger-900' 
                : 'text-success-600 hover:text-success-900'
            }`}
          >
            {item.is_active ? 'Deactivate' : 'Activate'}
          </button>
          <button
            onClick={() => handleDelete(item.id)}
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
        <LoadingSpinner size="lg" text="Loading inventory..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Inventory</h1>
          <p className="text-gray-600">Manage your inventory items</p>
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
          <Link to="/inventory/items/new">
            <Button className="flex items-center space-x-2">
              <Plus className="w-4 h-4" />
              <span>Add Item</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <Input
              placeholder="Search items..."
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
              <option value="stock_quantity">Sort by Stock</option>
              <option value="selling_price">Sort by Price</option>
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
          data={items}
          columns={columns}
          loading={loading}
          emptyMessage="No items found"
        />
      </div>
    </div>
  );
};

export default InventoryList;
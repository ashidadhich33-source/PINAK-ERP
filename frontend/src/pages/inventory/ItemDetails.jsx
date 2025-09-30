import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import { inventoryService } from '../../services/inventoryService';
import Button from '../../components/common/Button';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  Package, 
  Edit, 
  Trash2, 
  ArrowLeft,
  Tag,
  DollarSign,
  BarChart3,
  Calendar,
  AlertTriangle,
  TrendingUp,
  TrendingDown
} from 'lucide-react';

const ItemDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addNotification } = useApp();
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [stockMovements, setStockMovements] = useState([]);

  // Fetch item details
  const fetchItem = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [itemData, statsData, movementsData] = await Promise.all([
        inventoryService.getItem(id),
        inventoryService.getItemStats(id).catch(() => null),
        inventoryService.getItemStockMovements(id).catch(() => []),
      ]);
      
      setItem(itemData);
      setStats(statsData);
      setStockMovements(movementsData);
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
    fetchItem();
  }, [id]);

  // Handle delete
  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
      return;
    }

    try {
      await inventoryService.deleteItem(id);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Item deleted successfully',
      });
      navigate('/inventory');
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle toggle status
  const handleToggleStatus = async () => {
    try {
      await inventoryService.toggleItemStatus(id);
      setItem(prev => ({ ...prev, is_active: !prev.is_active }));
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading item details..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <Alert type="danger" title="Error">
          {error}
        </Alert>
        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            onClick={() => navigate('/inventory')}
            className="flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Inventory</span>
          </Button>
        </div>
      </div>
    );
  }

  if (!item) {
    return (
      <div className="text-center py-12">
        <Package className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Item not found</h3>
        <p className="text-gray-600 mb-4">The item you're looking for doesn't exist.</p>
        <Button
          variant="outline"
          onClick={() => navigate('/inventory')}
          className="flex items-center space-x-2"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Inventory</span>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            onClick={() => navigate('/inventory')}
            className="flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back</span>
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{item.name}</h1>
            <p className="text-gray-600">Item Details</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button
            variant={item.is_active ? 'danger' : 'success'}
            onClick={handleToggleStatus}
          >
            {item.is_active ? 'Deactivate' : 'Activate'}
          </Button>
          <Link to={`/inventory/items/${item.id}/edit`}>
            <Button variant="outline" className="flex items-center space-x-2">
              <Edit className="w-4 h-4" />
              <span>Edit</span>
            </Button>
          </Link>
          <Button
            variant="danger"
            onClick={handleDelete}
            className="flex items-center space-x-2"
          >
            <Trash2 className="w-4 h-4" />
            <span>Delete</span>
          </Button>
        </div>
      </div>

      {/* Item Information */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Basic Information */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Package className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">Basic Information</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">Item Name</label>
                <p className="text-sm text-gray-900">{item.name}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">SKU</label>
                <p className="text-sm text-gray-900">{item.sku}</p>
              </div>
              
              <div className="md:col-span-2">
                <label className="text-sm font-medium text-gray-500">Description</label>
                <p className="text-sm text-gray-900">{item.description || '-'}</p>
              </div>
            </div>
          </div>

          {/* Classification */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Tag className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">Classification</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">Category</label>
                <p className="text-sm text-gray-900">{item.category?.name || 'No Category'}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Brand</label>
                <p className="text-sm text-gray-900">{item.brand?.name || 'No Brand'}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Unit</label>
                <p className="text-sm text-gray-900">{item.unit?.name || 'No Unit'}</p>
              </div>
            </div>
          </div>

          {/* Pricing */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-2 mb-4">
              <DollarSign className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">Pricing</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">Cost Price</label>
                <p className="text-sm text-gray-900">₹{item.cost_price}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Selling Price</label>
                <p className="text-sm text-gray-900">₹{item.selling_price}</p>
              </div>
            </div>
          </div>

          {/* Stock Management */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-2 mb-4">
              <BarChart3 className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">Stock Management</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">Current Stock</label>
                <p className={`text-sm font-medium ${
                  item.stock_quantity <= item.min_stock_level 
                    ? 'text-danger-600' 
                    : item.stock_quantity <= item.min_stock_level * 1.5 
                      ? 'text-warning-600' 
                      : 'text-success-600'
                }`}>
                  {item.stock_quantity}
                </p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Minimum Stock Level</label>
                <p className="text-sm text-gray-900">{item.min_stock_level}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Maximum Stock Level</label>
                <p className="text-sm text-gray-900">{item.max_stock_level || '-'}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Status Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Status</h3>
            <div className="flex items-center space-x-3">
              <span className={`inline-flex px-3 py-1 text-sm font-medium rounded-full ${
                item.is_active 
                  ? 'bg-success-100 text-success-800' 
                  : 'bg-danger-100 text-danger-800'
              }`}>
                {item.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>

          {/* Stock Alert */}
          {item.stock_quantity <= item.min_stock_level && (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center space-x-2 mb-2">
                <AlertTriangle className="w-5 h-5 text-danger-500" />
                <h3 className="text-lg font-medium text-gray-900">Stock Alert</h3>
              </div>
              <p className="text-sm text-danger-600">
                This item is running low on stock. Consider restocking.
              </p>
            </div>
          )}

          {/* Statistics */}
          {stats && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Statistics</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Total Sold</span>
                  <span className="text-sm font-medium text-gray-900">{stats.total_sold || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Total Revenue</span>
                  <span className="text-sm font-medium text-gray-900">₹{stats.total_revenue || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Average Price</span>
                  <span className="text-sm font-medium text-gray-900">₹{stats.average_price || 0}</span>
                </div>
              </div>
            </div>
          )}

          {/* Recent Stock Movements */}
          {stockMovements.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Stock Movements</h3>
              <div className="space-y-3">
                {stockMovements.slice(0, 5).map((movement) => (
                  <div key={movement.id} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {movement.type === 'in' ? (
                        <TrendingUp className="w-4 h-4 text-success-500" />
                      ) : (
                        <TrendingDown className="w-4 h-4 text-danger-500" />
                      )}
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {movement.type === 'in' ? 'Stock In' : 'Stock Out'}
                        </p>
                        <p className="text-xs text-gray-500">{movement.reason}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">
                        {movement.type === 'in' ? '+' : '-'}{movement.quantity}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(movement.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Meta Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Meta Information</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Calendar className="w-4 h-4 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Created</p>
                  <p className="text-xs text-gray-500">
                    {new Date(item.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              
              {item.updated_at && (
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Last Updated</p>
                    <p className="text-xs text-gray-500">
                      {new Date(item.updated_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ItemDetails;
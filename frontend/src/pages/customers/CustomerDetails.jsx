import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import { customersService } from '../../services/customersService';
import Button from '../../components/common/Button';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  Users, 
  Edit, 
  Trash2, 
  ArrowLeft,
  MapPin,
  Phone,
  Mail,
  Building2,
  Calendar,
  DollarSign,
  ShoppingBag,
  CreditCard
} from 'lucide-react';

const CustomerDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addNotification } = useApp();
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [orders, setOrders] = useState([]);
  const [payments, setPayments] = useState([]);

  // Fetch customer details
  const fetchCustomer = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [customerData, statsData, ordersData, paymentsData] = await Promise.all([
        customersService.getCustomer(id),
        customersService.getCustomerStats(id).catch(() => null),
        customersService.getCustomerOrders(id).catch(() => []),
        customersService.getCustomerPayments(id).catch(() => []),
      ]);
      
      setCustomer(customerData);
      setStats(statsData);
      setOrders(ordersData);
      setPayments(paymentsData);
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
    fetchCustomer();
  }, [id]);

  // Handle delete
  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this customer? This action cannot be undone.')) {
      return;
    }

    try {
      await customersService.deleteCustomer(id);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Customer deleted successfully',
      });
      navigate('/customers');
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
      await customersService.toggleCustomerStatus(id);
      setCustomer(prev => ({ ...prev, is_active: !prev.is_active }));
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading customer details..." />
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
            onClick={() => navigate('/customers')}
            className="flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Customers</span>
          </Button>
        </div>
      </div>
    );
  }

  if (!customer) {
    return (
      <div className="text-center py-12">
        <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Customer not found</h3>
        <p className="text-gray-600 mb-4">The customer you're looking for doesn't exist.</p>
        <Button
          variant="outline"
          onClick={() => navigate('/customers')}
          className="flex items-center space-x-2"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Customers</span>
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
            onClick={() => navigate('/customers')}
            className="flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back</span>
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{customer.name}</h1>
            <p className="text-gray-600">Customer Details</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button
            variant={customer.is_active ? 'danger' : 'success'}
            onClick={handleToggleStatus}
          >
            {customer.is_active ? 'Deactivate' : 'Activate'}
          </Button>
          <Link to={`/customers/${customer.id}/edit`}>
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

      {/* Customer Information */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Basic Information */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Users className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">Basic Information</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">Customer Name</label>
                <p className="text-sm text-gray-900">{customer.name}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Email</label>
                <p className="text-sm text-gray-900">{customer.email || '-'}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Phone</label>
                <p className="text-sm text-gray-900">{customer.phone || '-'}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Group</label>
                <p className="text-sm text-gray-900">{customer.group?.name || 'No Group'}</p>
              </div>
            </div>
          </div>

          {/* Address Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-2 mb-4">
              <MapPin className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">Address Information</h3>
            </div>
            
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-gray-500">Address</label>
                <p className="text-sm text-gray-900">{customer.address || '-'}</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">City</label>
                  <p className="text-sm text-gray-900">{customer.city || '-'}</p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-500">State</label>
                  <p className="text-sm text-gray-900">{customer.state || '-'}</p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-500">Country</label>
                  <p className="text-sm text-gray-900">{customer.country || '-'}</p>
                </div>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Postal Code</label>
                <p className="text-sm text-gray-900">{customer.postal_code || '-'}</p>
              </div>
            </div>
          </div>

          {/* Tax Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Building2 className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">Tax Information</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">GST Number</label>
                <p className="text-sm text-gray-900">{customer.gst_number || '-'}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">PAN Number</label>
                <p className="text-sm text-gray-900">{customer.pan_number || '-'}</p>
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
                customer.is_active 
                  ? 'bg-success-100 text-success-800' 
                  : 'bg-danger-100 text-danger-800'
              }`}>
                {customer.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>

          {/* Statistics */}
          {stats && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Statistics</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Total Orders</span>
                  <span className="text-sm font-medium text-gray-900">{stats.total_orders || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Total Spent</span>
                  <span className="text-sm font-medium text-gray-900">₹{stats.total_spent || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Last Order</span>
                  <span className="text-sm font-medium text-gray-900">
                    {stats.last_order_date ? new Date(stats.last_order_date).toLocaleDateString() : 'Never'}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Recent Orders */}
          {orders.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Orders</h3>
              <div className="space-y-3">
                {orders.slice(0, 5).map((order) => (
                  <div key={order.id} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900">#{order.order_number}</p>
                      <p className="text-xs text-gray-500">{new Date(order.created_at).toLocaleDateString()}</p>
                    </div>
                    <span className="text-sm font-medium text-gray-900">₹{order.total_amount}</span>
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
                    {new Date(customer.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              
              {customer.updated_at && (
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Last Updated</p>
                    <p className="text-xs text-gray-500">
                      {new Date(customer.updated_at).toLocaleDateString()}
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

export default CustomerDetails;
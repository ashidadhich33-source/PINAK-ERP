import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { purchaseService } from '../../services/purchaseService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  ShoppingBag, 
  Plus, 
  Edit, 
  Trash2, 
  Search, 
  Filter, 
  Download, 
  RefreshCw, 
  Save, 
  X,
  Eye,
  CheckCircle,
  AlertTriangle,
  Clock,
  Truck,
  Package,
  DollarSign,
  Calendar,
  User,
  Building2,
  FileText,
  Send,
  Ban
} from 'lucide-react';

const PurchaseOrders = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [orders, setOrders] = useState([]);
  const [filteredOrders, setFilteredOrders] = useState([]);
  const [vendors, setVendors] = useState([]);
  const [items, setItems] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingOrder, setEditingOrder] = useState(null);
  const [viewingOrder, setViewingOrder] = useState(null);

  // Form data
  const [formData, setFormData] = useState({
    po_number: '',
    vendor_id: '',
    order_date: new Date().toISOString().split('T')[0],
    expected_delivery_date: '',
    status: 'draft',
    notes: '',
    items: [
      { item_id: '', quantity: 1, unit_price: 0, total: 0 }
    ],
    subtotal: 0,
    tax_amount: 0,
    total_amount: 0
  });

  // Order statuses
  const orderStatuses = [
    { value: 'draft', label: 'Draft', color: 'text-gray-600', bgColor: 'bg-gray-100' },
    { value: 'pending', label: 'Pending', color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
    { value: 'approved', label: 'Approved', color: 'text-blue-600', bgColor: 'bg-blue-100' },
    { value: 'sent', label: 'Sent', color: 'text-purple-600', bgColor: 'bg-purple-100' },
    { value: 'received', label: 'Received', color: 'text-green-600', bgColor: 'bg-green-100' },
    { value: 'cancelled', label: 'Cancelled', color: 'text-red-600', bgColor: 'bg-red-100' }
  ];

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const [ordersData, vendorsData, itemsData] = await Promise.all([
          purchaseService.getPurchaseOrders(),
          purchaseService.getVendors(),
          purchaseService.getItems()
        ]);
        
        setOrders(ordersData);
        setFilteredOrders(ordersData);
        setVendors(vendorsData);
        setItems(itemsData);
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

    fetchData();
  }, []);

  // Filter orders
  useEffect(() => {
    let filtered = orders;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(order =>
        order.po_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        order.vendor_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(order => order.status === statusFilter);
    }

    setFilteredOrders(filtered);
  }, [orders, searchTerm, statusFilter]);

  // Handle form field changes
  const handleFieldChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle item line changes
  const handleItemLineChange = (index, field, value) => {
    const newItems = [...formData.items];
    newItems[index] = {
      ...newItems[index],
      [field]: value
    };
    
    // Calculate line total
    if (field === 'quantity' || field === 'unit_price') {
      newItems[index].total = (newItems[index].quantity || 0) * (newItems[index].unit_price || 0);
    }
    
    // Calculate totals
    const subtotal = newItems.reduce((sum, item) => sum + (item.total || 0), 0);
    const taxAmount = subtotal * 0.18; // 18% GST
    const totalAmount = subtotal + taxAmount;
    
    setFormData(prev => ({
      ...prev,
      items: newItems,
      subtotal,
      tax_amount: taxAmount,
      total_amount: totalAmount
    }));
  };

  // Add new item line
  const addItemLine = () => {
    setFormData(prev => ({
      ...prev,
      items: [...prev.items, { item_id: '', quantity: 1, unit_price: 0, total: 0 }]
    }));
  };

  // Remove item line
  const removeItemLine = (index) => {
    if (formData.items.length > 1) {
      const newItems = formData.items.filter((_, i) => i !== index);
      const subtotal = newItems.reduce((sum, item) => sum + (item.total || 0), 0);
      const taxAmount = subtotal * 0.18;
      const totalAmount = subtotal + taxAmount;
      
      setFormData(prev => ({
        ...prev,
        items: newItems,
        subtotal,
        tax_amount: taxAmount,
        total_amount: totalAmount
      }));
    }
  };

  // Handle add order
  const handleAddOrder = async () => {
    try {
      setSaving(true);
      await purchaseService.createPurchaseOrder(formData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Purchase order created successfully',
      });
      setShowAddForm(false);
      resetForm();
      // Refresh orders
      const ordersData = await purchaseService.getPurchaseOrders();
      setOrders(ordersData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setSaving(false);
    }
  };

  // Handle edit order
  const handleEditOrder = async () => {
    try {
      setSaving(true);
      await purchaseService.updatePurchaseOrder(editingOrder.id, formData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Purchase order updated successfully',
      });
      setEditingOrder(null);
      setShowAddForm(false);
      resetForm();
      // Refresh orders
      const ordersData = await purchaseService.getPurchaseOrders();
      setOrders(ordersData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setSaving(false);
    }
  };

  // Handle delete order
  const handleDeleteOrder = async (orderId) => {
    if (!window.confirm('Are you sure you want to delete this purchase order?')) {
      return;
    }

    try {
      await purchaseService.deletePurchaseOrder(orderId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Purchase order deleted successfully',
      });
      // Refresh orders
      const ordersData = await purchaseService.getPurchaseOrders();
      setOrders(ordersData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle approve order
  const handleApproveOrder = async (orderId) => {
    try {
      await purchaseService.approvePurchaseOrder(orderId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Purchase order approved successfully',
      });
      // Refresh orders
      const ordersData = await purchaseService.getPurchaseOrders();
      setOrders(ordersData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle send order
  const handleSendOrder = async (orderId) => {
    try {
      await purchaseService.sendPurchaseOrder(orderId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Purchase order sent successfully',
      });
      // Refresh orders
      const ordersData = await purchaseService.getPurchaseOrders();
      setOrders(ordersData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle cancel order
  const handleCancelOrder = async (orderId) => {
    if (!window.confirm('Are you sure you want to cancel this purchase order?')) {
      return;
    }

    try {
      await purchaseService.cancelPurchaseOrder(orderId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Purchase order cancelled successfully',
      });
      // Refresh orders
      const ordersData = await purchaseService.getPurchaseOrders();
      setOrders(ordersData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      po_number: '',
      vendor_id: '',
      order_date: new Date().toISOString().split('T')[0],
      expected_delivery_date: '',
      status: 'draft',
      notes: '',
      items: [
        { item_id: '', quantity: 1, unit_price: 0, total: 0 }
      ],
      subtotal: 0,
      tax_amount: 0,
      total_amount: 0
    });
  };

  // Get status info
  const getStatusInfo = (status) => {
    return orderStatuses.find(s => s.value === status) || orderStatuses[0];
  };

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading purchase orders..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Purchase Orders</h1>
          <p className="text-gray-600">Manage purchase orders and vendor transactions</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={() => window.location.reload()}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </Button>
          <Button
            onClick={() => setShowAddForm(true)}
            className="flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Add Order</span>
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert type="danger" title="Error">
          {error}
        </Alert>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <Input
              placeholder="Search orders..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full"
            />
          </div>
          <div className="w-48">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="form-input"
            >
              <option value="all">All Status</option>
              {orderStatuses.map(status => (
                <option key={status.value} value={status.value}>
                  {status.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Orders List */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Purchase Orders</h2>
          <p className="text-sm text-gray-500">Manage your purchase orders</p>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  PO Number
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Vendor
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Order Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Expected Delivery
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredOrders.map((order) => {
                const statusInfo = getStatusInfo(order.status);
                return (
                  <tr key={order.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {order.po_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {order.vendor_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(order.order_date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {order.expected_delivery_date ? formatDate(order.expected_delivery_date) : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(order.total_amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                        {statusInfo.label}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setViewingOrder(order)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingOrder(order);
                            setFormData(order);
                            setShowAddForm(true);
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        {order.status === 'draft' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleApproveOrder(order.id)}
                            className="text-green-600 hover:text-green-700"
                          >
                            <CheckCircle className="w-4 h-4" />
                          </Button>
                        )}
                        {order.status === 'approved' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleSendOrder(order.id)}
                            className="text-blue-600 hover:text-blue-700"
                          >
                            <Send className="w-4 h-4" />
                          </Button>
                        )}
                        {order.status !== 'cancelled' && order.status !== 'received' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleCancelOrder(order.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Ban className="w-4 h-4" />
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteOrder(order.id)}
                          className="text-danger-600 hover:text-danger-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add/Edit Order Modal */}
      {showAddForm && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowAddForm(false)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <ShoppingBag className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {editingOrder ? 'Edit Purchase Order' : 'Add New Purchase Order'}
                      </h3>
                      <p className="text-sm text-gray-500">Create or update purchase order</p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setShowAddForm(false);
                      setEditingOrder(null);
                      resetForm();
                    }}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        PO Number *
                      </label>
                      <Input
                        value={formData.po_number}
                        onChange={(e) => handleFieldChange('po_number', e.target.value)}
                        placeholder="PO-001"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Vendor *
                      </label>
                      <select
                        value={formData.vendor_id}
                        onChange={(e) => handleFieldChange('vendor_id', e.target.value)}
                        className="form-input"
                        required
                      >
                        <option value="">Select Vendor</option>
                        {vendors.map(vendor => (
                          <option key={vendor.id} value={vendor.id}>
                            {vendor.name}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Order Date *
                      </label>
                      <Input
                        type="date"
                        value={formData.order_date}
                        onChange={(e) => handleFieldChange('order_date', e.target.value)}
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Expected Delivery Date
                      </label>
                      <Input
                        type="date"
                        value={formData.expected_delivery_date}
                        onChange={(e) => handleFieldChange('expected_delivery_date', e.target.value)}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Status
                      </label>
                      <select
                        value={formData.status}
                        onChange={(e) => handleFieldChange('status', e.target.value)}
                        className="form-input"
                      >
                        {orderStatuses.map(status => (
                          <option key={status.value} value={status.value}>
                            {status.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Notes
                    </label>
                    <textarea
                      value={formData.notes}
                      onChange={(e) => handleFieldChange('notes', e.target.value)}
                      rows={3}
                      className="form-input"
                      placeholder="Additional notes..."
                    />
                  </div>
                  
                  {/* Items Section */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm font-medium text-gray-900">Order Items</h4>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={addItemLine}
                      >
                        <Plus className="w-4 h-4 mr-1" />
                        Add Item
                      </Button>
                    </div>
                    
                    <div className="space-y-3">
                      {formData.items.map((item, index) => (
                        <div key={index} className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg">
                          <div className="flex-1">
                            <select
                              value={item.item_id}
                              onChange={(e) => handleItemLineChange(index, 'item_id', e.target.value)}
                              className="form-input"
                              required
                            >
                              <option value="">Select Item</option>
                              {items.map(itemOption => (
                                <option key={itemOption.id} value={itemOption.id}>
                                  {itemOption.name}
                                </option>
                              ))}
                            </select>
                          </div>
                          <div className="w-24">
                            <Input
                              type="number"
                              value={item.quantity}
                              onChange={(e) => handleItemLineChange(index, 'quantity', parseFloat(e.target.value) || 0)}
                              placeholder="Qty"
                              min="1"
                            />
                          </div>
                          <div className="w-32">
                            <Input
                              type="number"
                              value={item.unit_price}
                              onChange={(e) => handleItemLineChange(index, 'unit_price', parseFloat(e.target.value) || 0)}
                              placeholder="Unit Price"
                              min="0"
                              step="0.01"
                            />
                          </div>
                          <div className="w-32">
                            <Input
                              type="number"
                              value={item.total}
                              onChange={(e) => handleItemLineChange(index, 'total', parseFloat(e.target.value) || 0)}
                              placeholder="Total"
                              min="0"
                              step="0.01"
                              readOnly
                            />
                          </div>
                          {formData.items.length > 1 && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => removeItemLine(index)}
                              className="text-danger-600 hover:text-danger-700"
                            >
                              <X className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Totals */}
                  <div className="flex items-center justify-end space-x-6 p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm">
                      <span className="font-medium text-gray-900">Subtotal: </span>
                      <span className="text-gray-900">{formatCurrency(formData.subtotal)}</span>
                    </div>
                    <div className="text-sm">
                      <span className="font-medium text-gray-900">Tax (18%): </span>
                      <span className="text-gray-900">{formatCurrency(formData.tax_amount)}</span>
                    </div>
                    <div className="text-sm">
                      <span className="font-medium text-gray-900">Total: </span>
                      <span className="text-gray-900 font-bold">{formatCurrency(formData.total_amount)}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <Button
                  onClick={editingOrder ? handleEditOrder : handleAddOrder}
                  loading={saving}
                  className="w-full sm:w-auto sm:ml-3"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {editingOrder ? 'Update Order' : 'Create Order'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowAddForm(false);
                    setEditingOrder(null);
                    resetForm();
                  }}
                  className="mt-3 w-full sm:mt-0 sm:w-auto"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* View Order Modal */}
      {viewingOrder && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setViewingOrder(null)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <ShoppingBag className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">Purchase Order Details</h3>
                      <p className="text-sm text-gray-500">View purchase order information</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setViewingOrder(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">PO Number</p>
                      <p className="text-sm font-medium text-gray-900">{viewingOrder.po_number}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Vendor</p>
                      <p className="text-sm font-medium text-gray-900">{viewingOrder.vendor_name}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Order Date</p>
                      <p className="text-sm font-medium text-gray-900">{formatDate(viewingOrder.order_date)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Expected Delivery</p>
                      <p className="text-sm font-medium text-gray-900">
                        {viewingOrder.expected_delivery_date ? formatDate(viewingOrder.expected_delivery_date) : '-'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Status</p>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusInfo(viewingOrder.status).bgColor} ${getStatusInfo(viewingOrder.status).color}`}>
                        {getStatusInfo(viewingOrder.status).label}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Total Amount</p>
                      <p className="text-sm font-medium text-gray-900">{formatCurrency(viewingOrder.total_amount)}</p>
                    </div>
                  </div>
                  
                  {viewingOrder.notes && (
                    <div>
                      <p className="text-sm text-gray-500">Notes</p>
                      <p className="text-sm text-gray-900">{viewingOrder.notes}</p>
                    </div>
                  )}
                  
                  <div>
                    <p className="text-sm text-gray-500 mb-2">Order Items</p>
                    <div className="space-y-2">
                      {viewingOrder.items?.map((item, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex-1">
                            <p className="text-sm font-medium text-gray-900">{item.item_name}</p>
                            <p className="text-xs text-gray-500">Qty: {item.quantity} × {formatCurrency(item.unit_price)}</p>
                          </div>
                          <div className="text-sm font-medium text-gray-900">
                            {formatCurrency(item.total)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <Button
                  onClick={() => setViewingOrder(null)}
                  className="w-full sm:w-auto"
                >
                  Close
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PurchaseOrders;
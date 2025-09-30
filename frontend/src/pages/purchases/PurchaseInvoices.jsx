import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { purchaseService } from '../../services/purchaseService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  FileText, 
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
  DollarSign,
  Calendar,
  User,
  Building2,
  CreditCard,
  Receipt,
  Link,
  Send
} from 'lucide-react';

const PurchaseInvoices = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [invoices, setInvoices] = useState([]);
  const [filteredInvoices, setFilteredInvoices] = useState([]);
  const [vendors, setVendors] = useState([]);
  const [purchaseOrders, setPurchaseOrders] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingInvoice, setEditingInvoice] = useState(null);
  const [viewingInvoice, setViewingInvoice] = useState(null);

  // Form data
  const [formData, setFormData] = useState({
    invoice_number: '',
    vendor_id: '',
    purchase_order_id: '',
    invoice_date: new Date().toISOString().split('T')[0],
    due_date: '',
    status: 'draft',
    notes: '',
    items: [
      { item_id: '', description: '', quantity: 1, unit_price: 0, total: 0 }
    ],
    subtotal: 0,
    tax_amount: 0,
    total_amount: 0,
    paid_amount: 0,
    balance_amount: 0
  });

  // Invoice statuses
  const invoiceStatuses = [
    { value: 'draft', label: 'Draft', color: 'text-gray-600', bgColor: 'bg-gray-100' },
    { value: 'pending', label: 'Pending', color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
    { value: 'approved', label: 'Approved', color: 'text-blue-600', bgColor: 'bg-blue-100' },
    { value: 'matched', label: 'Matched', color: 'text-purple-600', bgColor: 'bg-purple-100' },
    { value: 'paid', label: 'Paid', color: 'text-green-600', bgColor: 'bg-green-100' },
    { value: 'overdue', label: 'Overdue', color: 'text-red-600', bgColor: 'bg-red-100' }
  ];

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const [invoicesData, vendorsData, ordersData] = await Promise.all([
          purchaseService.getPurchaseInvoices(),
          purchaseService.getVendors(),
          purchaseService.getPurchaseOrders()
        ]);
        
        setInvoices(invoicesData);
        setFilteredInvoices(invoicesData);
        setVendors(vendorsData);
        setPurchaseOrders(ordersData);
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

  // Filter invoices
  useEffect(() => {
    let filtered = invoices;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(invoice =>
        invoice.invoice_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        invoice.vendor_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(invoice => invoice.status === statusFilter);
    }

    setFilteredInvoices(filtered);
  }, [invoices, searchTerm, statusFilter]);

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
    const balanceAmount = totalAmount - formData.paid_amount;
    
    setFormData(prev => ({
      ...prev,
      items: newItems,
      subtotal,
      tax_amount: taxAmount,
      total_amount: totalAmount,
      balance_amount: balanceAmount
    }));
  };

  // Handle paid amount change
  const handlePaidAmountChange = (value) => {
    const paidAmount = parseFloat(value) || 0;
    const balanceAmount = formData.total_amount - paidAmount;
    
    setFormData(prev => ({
      ...prev,
      paid_amount: paidAmount,
      balance_amount: balanceAmount
    }));
  };

  // Add new item line
  const addItemLine = () => {
    setFormData(prev => ({
      ...prev,
      items: [...prev.items, { item_id: '', description: '', quantity: 1, unit_price: 0, total: 0 }]
    }));
  };

  // Remove item line
  const removeItemLine = (index) => {
    if (formData.items.length > 1) {
      const newItems = formData.items.filter((_, i) => i !== index);
      const subtotal = newItems.reduce((sum, item) => sum + (item.total || 0), 0);
      const taxAmount = subtotal * 0.18;
      const totalAmount = subtotal + taxAmount;
      const balanceAmount = totalAmount - formData.paid_amount;
      
      setFormData(prev => ({
        ...prev,
        items: newItems,
        subtotal,
        tax_amount: taxAmount,
        total_amount: totalAmount,
        balance_amount: balanceAmount
      }));
    }
  };

  // Handle add invoice
  const handleAddInvoice = async () => {
    try {
      setSaving(true);
      await purchaseService.createPurchaseInvoice(formData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Purchase invoice created successfully',
      });
      setShowAddForm(false);
      resetForm();
      // Refresh invoices
      const invoicesData = await purchaseService.getPurchaseInvoices();
      setInvoices(invoicesData);
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

  // Handle edit invoice
  const handleEditInvoice = async () => {
    try {
      setSaving(true);
      await purchaseService.updatePurchaseInvoice(editingInvoice.id, formData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Purchase invoice updated successfully',
      });
      setEditingInvoice(null);
      setShowAddForm(false);
      resetForm();
      // Refresh invoices
      const invoicesData = await purchaseService.getPurchaseInvoices();
      setInvoices(invoicesData);
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

  // Handle delete invoice
  const handleDeleteInvoice = async (invoiceId) => {
    if (!window.confirm('Are you sure you want to delete this purchase invoice?')) {
      return;
    }

    try {
      await purchaseService.deletePurchaseInvoice(invoiceId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Purchase invoice deleted successfully',
      });
      // Refresh invoices
      const invoicesData = await purchaseService.getPurchaseInvoices();
      setInvoices(invoicesData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle approve invoice
  const handleApproveInvoice = async (invoiceId) => {
    try {
      await purchaseService.approvePurchaseInvoice(invoiceId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Purchase invoice approved successfully',
      });
      // Refresh invoices
      const invoicesData = await purchaseService.getPurchaseInvoices();
      setInvoices(invoicesData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle match invoice
  const handleMatchInvoice = async (invoiceId) => {
    try {
      await purchaseService.matchPurchaseInvoice(invoiceId, {});
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Purchase invoice matched successfully',
      });
      // Refresh invoices
      const invoicesData = await purchaseService.getPurchaseInvoices();
      setInvoices(invoicesData);
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
      invoice_number: '',
      vendor_id: '',
      purchase_order_id: '',
      invoice_date: new Date().toISOString().split('T')[0],
      due_date: '',
      status: 'draft',
      notes: '',
      items: [
        { item_id: '', description: '', quantity: 1, unit_price: 0, total: 0 }
      ],
      subtotal: 0,
      tax_amount: 0,
      total_amount: 0,
      paid_amount: 0,
      balance_amount: 0
    });
  };

  // Get status info
  const getStatusInfo = (status) => {
    return invoiceStatuses.find(s => s.value === status) || invoiceStatuses[0];
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
        <LoadingSpinner size="lg" text="Loading purchase invoices..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Purchase Invoices</h1>
          <p className="text-gray-600">Manage purchase invoices and vendor payments</p>
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
            <span>Add Invoice</span>
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
              placeholder="Search invoices..."
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
              {invoiceStatuses.map(status => (
                <option key={status.value} value={status.value}>
                  {status.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Invoices List */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Purchase Invoices</h2>
          <p className="text-sm text-gray-500">Manage your purchase invoices</p>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Invoice Number
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Vendor
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Invoice Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Due Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Paid Amount
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
              {filteredInvoices.map((invoice) => {
                const statusInfo = getStatusInfo(invoice.status);
                return (
                  <tr key={invoice.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {invoice.invoice_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {invoice.vendor_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(invoice.invoice_date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {invoice.due_date ? formatDate(invoice.due_date) : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(invoice.total_amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(invoice.paid_amount)}
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
                          onClick={() => setViewingInvoice(invoice)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingInvoice(invoice);
                            setFormData(invoice);
                            setShowAddForm(true);
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        {invoice.status === 'draft' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleApproveInvoice(invoice.id)}
                            className="text-green-600 hover:text-green-700"
                          >
                            <CheckCircle className="w-4 h-4" />
                          </Button>
                        )}
                        {invoice.status === 'approved' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleMatchInvoice(invoice.id)}
                            className="text-purple-600 hover:text-purple-700"
                          >
                            <Link className="w-4 h-4" />
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteInvoice(invoice.id)}
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

      {/* Add/Edit Invoice Modal */}
      {showAddForm && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowAddForm(false)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {editingInvoice ? 'Edit Purchase Invoice' : 'Add New Purchase Invoice'}
                      </h3>
                      <p className="text-sm text-gray-500">Create or update purchase invoice</p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setShowAddForm(false);
                      setEditingInvoice(null);
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
                        Invoice Number *
                      </label>
                      <Input
                        value={formData.invoice_number}
                        onChange={(e) => handleFieldChange('invoice_number', e.target.value)}
                        placeholder="INV-001"
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
                        Purchase Order
                      </label>
                      <select
                        value={formData.purchase_order_id}
                        onChange={(e) => handleFieldChange('purchase_order_id', e.target.value)}
                        className="form-input"
                      >
                        <option value="">Select Purchase Order</option>
                        {purchaseOrders.map(order => (
                          <option key={order.id} value={order.id}>
                            {order.po_number}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Invoice Date *
                      </label>
                      <Input
                        type="date"
                        value={formData.invoice_date}
                        onChange={(e) => handleFieldChange('invoice_date', e.target.value)}
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Due Date
                      </label>
                      <Input
                        type="date"
                        value={formData.due_date}
                        onChange={(e) => handleFieldChange('due_date', e.target.value)}
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
                        {invoiceStatuses.map(status => (
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
                      <h4 className="text-sm font-medium text-gray-900">Invoice Items</h4>
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
                            <Input
                              value={item.description}
                              onChange={(e) => handleItemLineChange(index, 'description', e.target.value)}
                              placeholder="Item description"
                            />
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
                  
                  {/* Payment Section */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Paid Amount
                      </label>
                      <Input
                        type="number"
                        value={formData.paid_amount}
                        onChange={(e) => handlePaidAmountChange(e.target.value)}
                        placeholder="0.00"
                        min="0"
                        step="0.01"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Balance Amount
                      </label>
                      <Input
                        type="number"
                        value={formData.balance_amount}
                        placeholder="0.00"
                        readOnly
                        className="bg-gray-50"
                      />
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
                  onClick={editingInvoice ? handleEditInvoice : handleAddInvoice}
                  loading={saving}
                  className="w-full sm:w-auto sm:ml-3"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {editingInvoice ? 'Update Invoice' : 'Create Invoice'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowAddForm(false);
                    setEditingInvoice(null);
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

      {/* View Invoice Modal */}
      {viewingInvoice && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setViewingInvoice(null)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">Purchase Invoice Details</h3>
                      <p className="text-sm text-gray-500">View purchase invoice information</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setViewingInvoice(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Invoice Number</p>
                      <p className="text-sm font-medium text-gray-900">{viewingInvoice.invoice_number}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Vendor</p>
                      <p className="text-sm font-medium text-gray-900">{viewingInvoice.vendor_name}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Invoice Date</p>
                      <p className="text-sm font-medium text-gray-900">{formatDate(viewingInvoice.invoice_date)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Due Date</p>
                      <p className="text-sm font-medium text-gray-900">
                        {viewingInvoice.due_date ? formatDate(viewingInvoice.due_date) : '-'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Status</p>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusInfo(viewingInvoice.status).bgColor} ${getStatusInfo(viewingInvoice.status).color}`}>
                        {getStatusInfo(viewingInvoice.status).label}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Total Amount</p>
                      <p className="text-sm font-medium text-gray-900">{formatCurrency(viewingInvoice.total_amount)}</p>
                    </div>
                  </div>
                  
                  {viewingInvoice.notes && (
                    <div>
                      <p className="text-sm text-gray-500">Notes</p>
                      <p className="text-sm text-gray-900">{viewingInvoice.notes}</p>
                    </div>
                  )}
                  
                  <div>
                    <p className="text-sm text-gray-500 mb-2">Invoice Items</p>
                    <div className="space-y-2">
                      {viewingInvoice.items?.map((item, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex-1">
                            <p className="text-sm font-medium text-gray-900">{item.description}</p>
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
                  onClick={() => setViewingInvoice(null)}
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

export default PurchaseInvoices;
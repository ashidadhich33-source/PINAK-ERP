import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import { enhancedSalesService } from '../../services/enhancedSalesService';
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
  Truck,
  FileText,
  Filter,
  Calendar,
  DollarSign,
  Users,
  Settings
} from 'lucide-react';

const EnhancedSales = () => {
  const { addNotification } = useApp();
  const [activeTab, setActiveTab] = useState('challans');
  const [challans, setChallans] = useState([]);
  const [billSeries, setBillSeries] = useState([]);
  const [paymentModes, setPaymentModes] = useState([]);
  const [staff, setStaff] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    status: 'all',
    dateRange: 'all',
    sortBy: 'created_at',
    sortOrder: 'desc',
  });

  // Fetch data based on active tab
  const fetchData = async () => {
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
      
      let data;
      switch (activeTab) {
        case 'challans':
          data = await enhancedSalesService.getSaleChallans(params);
          setChallans(data);
          break;
        case 'bill-series':
          data = await enhancedSalesService.getBillSeries(params);
          setBillSeries(data);
          break;
        case 'payment-modes':
          data = await enhancedSalesService.getPaymentModes(params);
          setPaymentModes(data);
          break;
        case 'staff':
          data = await enhancedSalesService.getStaff(params);
          setStaff(data);
          break;
        default:
          break;
      }
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
    fetchData();
  }, [activeTab, searchTerm, filters]);

  // Handle search
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  // Handle filter change
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Handle delete
  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this item?')) {
      return;
    }

    try {
      switch (activeTab) {
        case 'challans':
          await enhancedSalesService.deleteSaleChallan(id);
          setChallans(prev => prev.filter(item => item.id !== id));
          break;
        case 'bill-series':
          await enhancedSalesService.deleteBillSeries(id);
          setBillSeries(prev => prev.filter(item => item.id !== id));
          break;
        case 'payment-modes':
          await enhancedSalesService.deletePaymentMode(id);
          setPaymentModes(prev => prev.filter(item => item.id !== id));
          break;
        case 'staff':
          await enhancedSalesService.deleteStaff(id);
          setStaff(prev => prev.filter(item => item.id !== id));
          break;
        default:
          break;
      }
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

  // Handle confirm challan
  const handleConfirmChallan = async (challanId) => {
    try {
      await enhancedSalesService.confirmSaleChallan(challanId);
      setChallans(prev => prev.map(challan => 
        challan.id === challanId 
          ? { ...challan, status: 'confirmed' }
          : challan
      ));
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Challan confirmed successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle deliver challan
  const handleDeliverChallan = async (challanId) => {
    try {
      await enhancedSalesService.deliverSaleChallan(challanId);
      setChallans(prev => prev.map(challan => 
        challan.id === challanId 
          ? { ...challan, status: 'delivered' }
          : challan
      ));
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Challan delivered successfully',
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
      await enhancedSalesService.exportSalesData('csv', activeTab, filters);
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: 'Data export will be downloaded shortly',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Get current data based on active tab
  const getCurrentData = () => {
    switch (activeTab) {
      case 'challans':
        return challans;
      case 'bill-series':
        return billSeries;
      case 'payment-modes':
        return paymentModes;
      case 'staff':
        return staff;
      default:
        return [];
    }
  };

  // Get columns based on active tab
  const getColumns = () => {
    switch (activeTab) {
      case 'challans':
        return [
          {
            key: 'challan_number',
            label: 'Challan Number',
            render: (challan) => (
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <FileText className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">#{challan.challan_number}</p>
                  <p className="text-sm text-gray-500">{new Date(challan.challan_date).toLocaleDateString()}</p>
                </div>
              </div>
            ),
          },
          {
            key: 'customer',
            label: 'Customer',
            render: (challan) => (
              <div>
                <p className="font-medium text-gray-900">{challan.customer?.name || 'Walk-in Customer'}</p>
                <p className="text-sm text-gray-500">{challan.customer?.email || '-'}</p>
              </div>
            ),
          },
          {
            key: 'challan_type',
            label: 'Type',
            render: (challan) => (
              <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                {challan.challan_type}
              </span>
            ),
          },
          {
            key: 'amounts',
            label: 'Amounts',
            render: (challan) => (
              <div>
                <p className="font-medium text-gray-900">Qty: {challan.total_quantity}</p>
                <p className="text-sm text-gray-500">₹{challan.total_amount}</p>
              </div>
            ),
          },
          {
            key: 'status',
            label: 'Status',
            render: (challan) => {
              const statusInfo = {
                draft: { icon: Clock, color: 'text-warning-600', bgColor: 'bg-warning-100' },
                confirmed: { icon: CheckCircle, color: 'text-blue-600', bgColor: 'bg-blue-100' },
                delivered: { icon: Truck, color: 'text-success-600', bgColor: 'bg-success-100' },
                cancelled: { icon: XCircle, color: 'text-danger-600', bgColor: 'bg-danger-100' },
              }[challan.status] || { icon: Clock, color: 'text-gray-600', bgColor: 'bg-gray-100' };
              
              const Icon = statusInfo.icon;
              return (
                <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                  <Icon className="w-3 h-3 mr-1" />
                  {challan.status}
                </span>
              );
            },
          },
          {
            key: 'actions',
            label: 'Actions',
            render: (challan) => (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/sales/challans/${challan.id}`}
                  className="text-primary-600 hover:text-primary-900"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                <Link
                  to={`/sales/challans/${challan.id}/edit`}
                  className="text-secondary-600 hover:text-secondary-900"
                >
                  <Edit className="w-4 h-4" />
                </Link>
                {challan.status === 'draft' && (
                  <button
                    onClick={() => handleConfirmChallan(challan.id)}
                    className="text-blue-600 hover:text-blue-900"
                    title="Confirm Challan"
                  >
                    <CheckCircle className="w-4 h-4" />
                  </button>
                )}
                {challan.status === 'confirmed' && (
                  <button
                    onClick={() => handleDeliverChallan(challan.id)}
                    className="text-green-600 hover:text-green-900"
                    title="Mark as Delivered"
                  >
                    <Truck className="w-4 h-4" />
                  </button>
                )}
                <button
                  onClick={() => handleDelete(challan.id)}
                  className="text-danger-600 hover:text-danger-900"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ),
          },
        ];
      case 'bill-series':
        return [
          {
            key: 'series_name',
            label: 'Series Name',
            render: (series) => (
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <FileText className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{series.series_name}</p>
                  <p className="text-sm text-gray-500">{series.series_code}</p>
                </div>
              </div>
            ),
          },
          {
            key: 'document_type',
            label: 'Document Type',
            render: (series) => (
              <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                {series.document_type}
              </span>
            ),
          },
          {
            key: 'number_format',
            label: 'Number Format',
            render: (series) => (
              <div>
                <p className="font-medium text-gray-900">{series.prefix}{series.suffix || ''}</p>
                <p className="text-sm text-gray-500">Length: {series.number_length}</p>
              </div>
            ),
          },
          {
            key: 'current_number',
            label: 'Current Number',
            render: (series) => (
              <div>
                <p className="font-medium text-gray-900">{series.current_number}</p>
                <p className="text-sm text-gray-500">Next: {series.current_number + 1}</p>
              </div>
            ),
          },
          {
            key: 'is_active',
            label: 'Status',
            render: (series) => (
              <div className="flex items-center space-x-2">
                {series.is_active ? (
                  <CheckCircle className="w-4 h-4 text-success-500" />
                ) : (
                  <XCircle className="w-4 h-4 text-danger-500" />
                )}
                <span className="text-sm text-gray-900">
                  {series.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            ),
          },
          {
            key: 'actions',
            label: 'Actions',
            render: (series) => (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/sales/bill-series/${series.id}`}
                  className="text-primary-600 hover:text-primary-900"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                <Link
                  to={`/sales/bill-series/${series.id}/edit`}
                  className="text-secondary-600 hover:text-secondary-900"
                >
                  <Edit className="w-4 h-4" />
                </Link>
                <button
                  onClick={() => handleDelete(series.id)}
                  className="text-danger-600 hover:text-danger-900"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ),
          },
        ];
      case 'payment-modes':
        return [
          {
            key: 'mode_name',
            label: 'Payment Mode',
            render: (mode) => (
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <DollarSign className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{mode.mode_name}</p>
                  <p className="text-sm text-gray-500">{mode.mode_code}</p>
                </div>
              </div>
            ),
          },
          {
            key: 'mode_type',
            label: 'Type',
            render: (mode) => (
              <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                {mode.mode_type}
              </span>
            ),
          },
          {
            key: 'requirements',
            label: 'Requirements',
            render: (mode) => (
              <div className="space-y-1">
                {mode.requires_reference && (
                  <span className="inline-block px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded">
                    Reference Required
                  </span>
                )}
                {mode.requires_approval && (
                  <span className="inline-block px-2 py-1 text-xs bg-orange-100 text-orange-800 rounded">
                    Approval Required
                  </span>
                )}
              </div>
            ),
          },
          {
            key: 'limits',
            label: 'Amount Limits',
            render: (mode) => (
              <div>
                <p className="text-sm text-gray-900">
                  Min: ₹{mode.minimum_amount || 0}
                </p>
                <p className="text-sm text-gray-500">
                  Max: ₹{mode.maximum_amount || 'No limit'}
                </p>
              </div>
            ),
          },
          {
            key: 'is_active',
            label: 'Status',
            render: (mode) => (
              <div className="flex items-center space-x-2">
                {mode.is_active ? (
                  <CheckCircle className="w-4 h-4 text-success-500" />
                ) : (
                  <XCircle className="w-4 h-4 text-danger-500" />
                )}
                <span className="text-sm text-gray-900">
                  {mode.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            ),
          },
          {
            key: 'actions',
            label: 'Actions',
            render: (mode) => (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/sales/payment-modes/${mode.id}`}
                  className="text-primary-600 hover:text-primary-900"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                <Link
                  to={`/sales/payment-modes/${mode.id}/edit`}
                  className="text-secondary-600 hover:text-secondary-900"
                >
                  <Edit className="w-4 h-4" />
                </Link>
                <button
                  onClick={() => handleDelete(mode.id)}
                  className="text-danger-600 hover:text-danger-900"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ),
          },
        ];
      case 'staff':
        return [
          {
            key: 'employee_info',
            label: 'Employee',
            render: (member) => (
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <Users className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{member.first_name} {member.last_name}</p>
                  <p className="text-sm text-gray-500">{member.employee_id}</p>
                </div>
              </div>
            ),
          },
          {
            key: 'contact',
            label: 'Contact',
            render: (member) => (
              <div>
                <p className="text-sm text-gray-900">{member.email || '-'}</p>
                <p className="text-sm text-gray-500">{member.phone || '-'}</p>
              </div>
            ),
          },
          {
            key: 'position',
            label: 'Position',
            render: (member) => (
              <div>
                <p className="font-medium text-gray-900">{member.designation || '-'}</p>
                <p className="text-sm text-gray-500">{member.department || '-'}</p>
              </div>
            ),
          },
          {
            key: 'salary',
            label: 'Salary',
            render: (member) => (
              <div>
                <p className="font-medium text-gray-900">₹{member.salary || 0}</p>
                <p className="text-sm text-gray-500">Commission: {member.commission_percentage || 0}%</p>
              </div>
            ),
          },
          {
            key: 'is_active',
            label: 'Status',
            render: (member) => (
              <div className="flex items-center space-x-2">
                {member.is_active ? (
                  <CheckCircle className="w-4 h-4 text-success-500" />
                ) : (
                  <XCircle className="w-4 h-4 text-danger-500" />
                )}
                <span className="text-sm text-gray-900">
                  {member.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            ),
          },
          {
            key: 'actions',
            label: 'Actions',
            render: (member) => (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/sales/staff/${member.id}`}
                  className="text-primary-600 hover:text-primary-900"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                <Link
                  to={`/sales/staff/${member.id}/edit`}
                  className="text-secondary-600 hover:text-secondary-900"
                >
                  <Edit className="w-4 h-4" />
                </Link>
                <button
                  onClick={() => handleDelete(member.id)}
                  className="text-danger-600 hover:text-danger-900"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ),
          },
        ];
      default:
        return [];
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading enhanced sales data..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Enhanced Sales Management</h1>
          <p className="text-gray-600">Manage sale challans, bill series, payment modes, and staff</p>
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
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {[
              { id: 'challans', name: 'Sale Challans', icon: FileText },
              { id: 'bill-series', name: 'Bill Series', icon: Settings },
              { id: 'payment-modes', name: 'Payment Modes', icon: DollarSign },
              { id: 'staff', name: 'Staff', icon: Users },
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {/* Filters and Search */}
          <div className="mb-6">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div className="md:col-span-2">
                <div className="relative">
                  <Input
                    placeholder="Search..."
                    value={searchTerm}
                    onChange={handleSearch}
                    className="pl-10"
                  />
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-gray-400" />
                  </div>
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
                  <option value="draft">Draft</option>
                  <option value="confirmed">Confirmed</option>
                  <option value="delivered">Delivered</option>
                </select>
              </div>
              
              <div>
                <select
                  value={filters.dateRange}
                  onChange={(e) => handleFilterChange('dateRange', e.target.value)}
                  className="form-input"
                >
                  <option value="all">All Dates</option>
                  <option value="today">Today</option>
                  <option value="week">This Week</option>
                  <option value="month">This Month</option>
                </select>
              </div>
              
              <div>
                <select
                  value={filters.sortBy}
                  onChange={(e) => handleFilterChange('sortBy', e.target.value)}
                  className="form-input"
                >
                  <option value="created_at">Sort by Date</option>
                  <option value="name">Sort by Name</option>
                  <option value="status">Sort by Status</option>
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
          <DataTable
            data={getCurrentData()}
            columns={getColumns()}
            loading={loading}
            emptyMessage="No data found"
          />
        </div>
      </div>
    </div>
  );
};

export default EnhancedSales;
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import { localizationService } from '../../services/localizationService';
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
  Receipt,
  Eye,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  Calculator,
  Filter,
  Percent,
  MapPin,
  Building
} from 'lucide-react';

const IndianGST = () => {
  const { addNotification } = useApp();
  const [activeTab, setActiveTab] = useState('gst-slabs');
  const [gstSlabs, setGstSlabs] = useState([]);
  const [hsnCodes, setHsnCodes] = useState([]);
  const [sacCodes, setSacCodes] = useState([]);
  const [stateCodes, setStateCodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    status: 'all',
    sortBy: 'name',
    sortOrder: 'asc',
  });

  // GST Calculation state
  const [gstCalculation, setGstCalculation] = useState({
    taxableAmount: '',
    supplierStateCode: '',
    recipientStateCode: '',
    gstRate: '',
    hsnCode: '',
    sacCode: '',
  });
  const [calculationResult, setCalculationResult] = useState(null);

  // Fetch data based on active tab
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        search: searchTerm,
        sort_by: filters.sortBy,
        sort_order: filters.sortOrder,
      };
      
      let data;
      switch (activeTab) {
        case 'gst-slabs':
          data = await localizationService.getGSTSlabs(params);
          setGstSlabs(data);
          break;
        case 'hsn-codes':
          data = await localizationService.getHSNCodes(params);
          setHsnCodes(data);
          break;
        case 'sac-codes':
          data = await localizationService.getSACCodes(params);
          setSacCodes(data);
          break;
        case 'state-codes':
          data = await localizationService.getStateCodes(params);
          setStateCodes(data);
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

  // Handle GST calculation
  const handleGSTCalculation = async () => {
    try {
      const result = await localizationService.calculateGST(gstCalculation);
      setCalculationResult(result);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle delete
  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this item?')) {
      return;
    }

    try {
      switch (activeTab) {
        case 'gst-slabs':
          await localizationService.deleteGSTSlab(id);
          setGstSlabs(prev => prev.filter(item => item.id !== id));
          break;
        case 'hsn-codes':
          await localizationService.deleteHSNCode(id);
          setHsnCodes(prev => prev.filter(item => item.id !== id));
          break;
        case 'sac-codes':
          await localizationService.deleteSACCode(id);
          setSacCodes(prev => prev.filter(item => item.id !== id));
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

  // Handle export
  const handleExport = async () => {
    try {
      await localizationService.exportLocalizationData('csv', activeTab, filters);
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
      case 'gst-slabs':
        return gstSlabs;
      case 'hsn-codes':
        return hsnCodes;
      case 'sac-codes':
        return sacCodes;
      case 'state-codes':
        return stateCodes;
      default:
        return [];
    }
  };

  // Get columns based on active tab
  const getColumns = () => {
    switch (activeTab) {
      case 'gst-slabs':
        return [
          {
            key: 'name',
            label: 'Slab Name',
            render: (item) => (
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <Percent className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{item.name}</p>
                  <p className="text-sm text-gray-500">{item.tax_type}</p>
                </div>
              </div>
            ),
          },
          {
            key: 'rate',
            label: 'Rate',
            render: (item) => (
              <span className="font-medium text-gray-900">{item.rate}%</span>
            ),
          },
          {
            key: 'cgst_rate',
            label: 'CGST',
            render: (item) => (
              <span className="text-gray-900">{item.cgst_rate || '-'}%</span>
            ),
          },
          {
            key: 'sgst_rate',
            label: 'SGST',
            render: (item) => (
              <span className="text-gray-900">{item.sgst_rate || '-'}%</span>
            ),
          },
          {
            key: 'igst_rate',
            label: 'IGST',
            render: (item) => (
              <span className="text-gray-900">{item.igst_rate || '-'}%</span>
            ),
          },
          {
            key: 'actions',
            label: 'Actions',
            render: (item) => (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/localization/gst/slabs/${item.id}`}
                  className="text-primary-600 hover:text-primary-900"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                <Link
                  to={`/localization/gst/slabs/${item.id}/edit`}
                  className="text-secondary-600 hover:text-secondary-900"
                >
                  <Edit className="w-4 h-4" />
                </Link>
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
      case 'hsn-codes':
        return [
          {
            key: 'code',
            label: 'HSN Code',
            render: (item) => (
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <Receipt className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{item.code}</p>
                  <p className="text-sm text-gray-500">{item.description}</p>
                </div>
              </div>
            ),
          },
          {
            key: 'gst_rate',
            label: 'GST Rate',
            render: (item) => (
              <span className="font-medium text-gray-900">{item.gst_rate || '-'}%</span>
            ),
          },
          {
            key: 'cess_rate',
            label: 'Cess Rate',
            render: (item) => (
              <span className="text-gray-900">{item.cess_rate || '-'}%</span>
            ),
          },
          {
            key: 'actions',
            label: 'Actions',
            render: (item) => (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/localization/gst/hsn-codes/${item.id}`}
                  className="text-primary-600 hover:text-primary-900"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                <Link
                  to={`/localization/gst/hsn-codes/${item.id}/edit`}
                  className="text-secondary-600 hover:text-secondary-900"
                >
                  <Edit className="w-4 h-4" />
                </Link>
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
      case 'sac-codes':
        return [
          {
            key: 'code',
            label: 'SAC Code',
            render: (item) => (
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <Building className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{item.code}</p>
                  <p className="text-sm text-gray-500">{item.description}</p>
                </div>
              </div>
            ),
          },
          {
            key: 'category',
            label: 'Category',
            render: (item) => (
              <span className="text-gray-900">{item.category || '-'}</span>
            ),
          },
          {
            key: 'gst_rate',
            label: 'GST Rate',
            render: (item) => (
              <span className="font-medium text-gray-900">{item.gst_rate || '-'}%</span>
            ),
          },
          {
            key: 'actions',
            label: 'Actions',
            render: (item) => (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/localization/gst/sac-codes/${item.id}`}
                  className="text-primary-600 hover:text-primary-900"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                <Link
                  to={`/localization/gst/sac-codes/${item.id}/edit`}
                  className="text-secondary-600 hover:text-secondary-900"
                >
                  <Edit className="w-4 h-4" />
                </Link>
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
      case 'state-codes':
        return [
          {
            key: 'code',
            label: 'State Code',
            render: (item) => (
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <MapPin className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{item.code}</p>
                  <p className="text-sm text-gray-500">{item.name}</p>
                </div>
              </div>
            ),
          },
          {
            key: 'state_type',
            label: 'Type',
            render: (item) => (
              <span className="text-gray-900">{item.state_type}</span>
            ),
          },
          {
            key: 'actions',
            label: 'Actions',
            render: (item) => (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/localization/gst/state-codes/${item.id}`}
                  className="text-primary-600 hover:text-primary-900"
                >
                  <Eye className="w-4 h-4" />
                </Link>
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
        <LoadingSpinner size="lg" text="Loading GST data..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Indian GST Management</h1>
          <p className="text-gray-600">Manage GST slabs, HSN codes, SAC codes, and state codes</p>
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
              { id: 'gst-slabs', name: 'GST Slabs', icon: Percent },
              { id: 'hsn-codes', name: 'HSN Codes', icon: Receipt },
              { id: 'sac-codes', name: 'SAC Codes', icon: Building },
              { id: 'state-codes', name: 'State Codes', icon: MapPin },
              { id: 'gst-calculator', name: 'GST Calculator', icon: Calculator },
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
          {/* GST Calculator Tab */}
          {activeTab === 'gst-calculator' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-gray-900">GST Calculation</h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Taxable Amount
                    </label>
                    <Input
                      type="number"
                      value={gstCalculation.taxableAmount}
                      onChange={(e) => setGstCalculation(prev => ({ ...prev, taxableAmount: e.target.value }))}
                      placeholder="Enter taxable amount"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Supplier State Code
                    </label>
                    <Input
                      value={gstCalculation.supplierStateCode}
                      onChange={(e) => setGstCalculation(prev => ({ ...prev, supplierStateCode: e.target.value }))}
                      placeholder="Enter supplier state code"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Recipient State Code
                    </label>
                    <Input
                      value={gstCalculation.recipientStateCode}
                      onChange={(e) => setGstCalculation(prev => ({ ...prev, recipientStateCode: e.target.value }))}
                      placeholder="Enter recipient state code"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      GST Rate (%)
                    </label>
                    <Input
                      type="number"
                      value={gstCalculation.gstRate}
                      onChange={(e) => setGstCalculation(prev => ({ ...prev, gstRate: e.target.value }))}
                      placeholder="Enter GST rate"
                    />
                  </div>

                  <Button onClick={handleGSTCalculation} className="w-full">
                    Calculate GST
                  </Button>
                </div>

                {calculationResult && (
                  <div className="bg-gray-50 rounded-lg p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Calculation Result</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Place of Supply:</span>
                        <span className="font-medium">{calculationResult.place_of_supply}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">CGST ({calculationResult.cgst_rate}%):</span>
                        <span className="font-medium">₹{calculationResult.cgst_amount}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">SGST ({calculationResult.sgst_rate}%):</span>
                        <span className="font-medium">₹{calculationResult.sgst_amount}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">IGST ({calculationResult.igst_rate}%):</span>
                        <span className="font-medium">₹{calculationResult.igst_amount}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Cess ({calculationResult.cess_rate}%):</span>
                        <span className="font-medium">₹{calculationResult.cess_amount}</span>
                      </div>
                      <hr />
                      <div className="flex justify-between">
                        <span className="text-gray-600">Total GST:</span>
                        <span className="font-medium">₹{calculationResult.total_gst_amount}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Total Amount:</span>
                        <span className="font-medium">₹{calculationResult.total_amount}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Other tabs */}
          {activeTab !== 'gst-calculator' && (
            <>
              {/* Filters and Search */}
              <div className="mb-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
                      value={filters.sortBy}
                      onChange={(e) => handleFilterChange('sortBy', e.target.value)}
                      className="form-input"
                    >
                      <option value="name">Sort by Name</option>
                      <option value="code">Sort by Code</option>
                      <option value="rate">Sort by Rate</option>
                    </select>
                  </div>
                  
                  <div>
                    <select
                      value={filters.sortOrder}
                      onChange={(e) => handleFilterChange('sortOrder', e.target.value)}
                      className="form-input"
                    >
                      <option value="asc">Ascending</option>
                      <option value="desc">Descending</option>
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
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default IndianGST;
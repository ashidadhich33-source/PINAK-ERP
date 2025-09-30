import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { localizationService } from '../../services/localizationService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  MapPin, 
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
  Star,
  Gift,
  Target,
  Users,
  TrendingUp,
  Calendar,
  Settings,
  CheckCircle,
  AlertTriangle,
  Clock,
  DollarSign,
  Percent,
  Crown,
  Zap,
  ArrowUp,
  ArrowDown,
  Minus,
  CreditCard,
  ShoppingCart,
  User,
  FileText,
  BarChart3,
  Smartphone,
  Wifi,
  Shield,
  Bell,
  Mail,
  Link,
  Copy,
  Play,
  Pause,
  Stop,
  Send,
  MessageSquare,
  Database,
  Filter as FilterIcon,
  Layers,
  Activity,
  Globe,
  Building2,
  Home,
  Navigation,
  Map
} from 'lucide-react';

const IndianGeography = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [states, setStates] = useState([]);
  const [cities, setCities] = useState([]);
  const [pincodes, setPincodes] = useState([]);
  const [filteredStates, setFilteredStates] = useState([]);
  const [filteredCities, setFilteredCities] = useState([]);
  const [filteredPincodes, setFilteredPincodes] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [stateFilter, setStateFilter] = useState('all');
  const [showAddState, setShowAddState] = useState(false);
  const [showAddCity, setShowAddCity] = useState(false);
  const [showAddPincode, setShowAddPincode] = useState(false);
  const [editingState, setEditingState] = useState(null);
  const [editingCity, setEditingCity] = useState(null);
  const [editingPincode, setEditingPincode] = useState(null);
  const [viewingState, setViewingState] = useState(null);
  const [viewingCity, setViewingCity] = useState(null);
  const [viewingPincode, setViewingPincode] = useState(null);
  const [activeTab, setActiveTab] = useState('states');

  // State form data
  const [stateFormData, setStateFormData] = useState({
    name: '',
    code: '',
    capital: '',
    region: '',
    population: '',
    area: '',
    status: 'active'
  });

  // City form data
  const [cityFormData, setCityFormData] = useState({
    name: '',
    state_id: '',
    district: '',
    population: '',
    area: '',
    status: 'active'
  });

  // Pincode form data
  const [pincodeFormData, setPincodeFormData] = useState({
    pincode: '',
    city_id: '',
    area: '',
    delivery_status: 'active',
    status: 'active'
  });

  // Indian regions
  const indianRegions = [
    { value: 'north', label: 'North India' },
    { value: 'south', label: 'South India' },
    { value: 'east', label: 'East India' },
    { value: 'west', label: 'West India' },
    { value: 'central', label: 'Central India' },
    { value: 'northeast', label: 'Northeast India' }
  ];

  // Status options
  const statusOptions = [
    { value: 'active', label: 'Active', color: 'text-green-600', bgColor: 'bg-green-100' },
    { value: 'inactive', label: 'Inactive', color: 'text-gray-600', bgColor: 'bg-gray-100' }
  ];

  // Delivery status options
  const deliveryStatusOptions = [
    { value: 'active', label: 'Active', color: 'text-green-600', bgColor: 'bg-green-100' },
    { value: 'limited', label: 'Limited', color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
    { value: 'inactive', label: 'Inactive', color: 'text-red-600', bgColor: 'bg-red-100' }
  ];

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const [statesData, citiesData, pincodesData] = await Promise.all([
          localizationService.getIndianStates(),
          localizationService.getIndianCities(),
          localizationService.getIndianPincodes()
        ]);
        
        setStates(statesData);
        setCities(citiesData);
        setPincodes(pincodesData);
        setFilteredStates(statesData);
        setFilteredCities(citiesData);
        setFilteredPincodes(pincodesData);
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

  // Filter data
  useEffect(() => {
    let filtered = [];

    switch (activeTab) {
      case 'states':
        filtered = states;
        break;
      case 'cities':
        filtered = cities;
        break;
      case 'pincodes':
        filtered = pincodes;
        break;
      default:
        filtered = [];
    }

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(item =>
        item.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.capital?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.district?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.pincode?.includes(searchTerm)
      );
    }

    // State filter for cities and pincodes
    if (stateFilter !== 'all' && (activeTab === 'cities' || activeTab === 'pincodes')) {
      filtered = filtered.filter(item => item.state_id === stateFilter);
    }

    switch (activeTab) {
      case 'states':
        setFilteredStates(filtered);
        break;
      case 'cities':
        setFilteredCities(filtered);
        break;
      case 'pincodes':
        setFilteredPincodes(filtered);
        break;
    }
  }, [states, cities, pincodes, searchTerm, stateFilter, activeTab]);

  // Handle state form field changes
  const handleStateFieldChange = (field, value) => {
    setStateFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle city form field changes
  const handleCityFieldChange = (field, value) => {
    setCityFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle pincode form field changes
  const handlePincodeFieldChange = (field, value) => {
    setPincodeFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle add state
  const handleAddState = async () => {
    try {
      setSaving(true);
      await localizationService.createIndianState(stateFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Indian state created successfully',
      });
      setShowAddState(false);
      resetStateForm();
      // Refresh states
      const statesData = await localizationService.getIndianStates();
      setStates(statesData);
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

  // Handle add city
  const handleAddCity = async () => {
    try {
      setSaving(true);
      await localizationService.createIndianCity(cityFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Indian city created successfully',
      });
      setShowAddCity(false);
      resetCityForm();
      // Refresh cities
      const citiesData = await localizationService.getIndianCities();
      setCities(citiesData);
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

  // Handle add pincode
  const handleAddPincode = async () => {
    try {
      setSaving(true);
      await localizationService.createIndianPincode(pincodeFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Indian pincode created successfully',
      });
      setShowAddPincode(false);
      resetPincodeForm();
      // Refresh pincodes
      const pincodesData = await localizationService.getIndianPincodes();
      setPincodes(pincodesData);
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

  // Handle delete state
  const handleDeleteState = async (stateId) => {
    if (!window.confirm('Are you sure you want to delete this Indian state?')) {
      return;
    }

    try {
      await localizationService.deleteIndianState(stateId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Indian state deleted successfully',
      });
      // Refresh states
      const statesData = await localizationService.getIndianStates();
      setStates(statesData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle delete city
  const handleDeleteCity = async (cityId) => {
    if (!window.confirm('Are you sure you want to delete this Indian city?')) {
      return;
    }

    try {
      await localizationService.deleteIndianCity(cityId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Indian city deleted successfully',
      });
      // Refresh cities
      const citiesData = await localizationService.getIndianCities();
      setCities(citiesData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle delete pincode
  const handleDeletePincode = async (pincodeId) => {
    if (!window.confirm('Are you sure you want to delete this Indian pincode?')) {
      return;
    }

    try {
      await localizationService.deleteIndianPincode(pincodeId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Indian pincode deleted successfully',
      });
      // Refresh pincodes
      const pincodesData = await localizationService.getIndianPincodes();
      setPincodes(pincodesData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Reset forms
  const resetStateForm = () => {
    setStateFormData({
      name: '',
      code: '',
      capital: '',
      region: '',
      population: '',
      area: '',
      status: 'active'
    });
  };

  const resetCityForm = () => {
    setCityFormData({
      name: '',
      state_id: '',
      district: '',
      population: '',
      area: '',
      status: 'active'
    });
  };

  const resetPincodeForm = () => {
    setPincodeFormData({
      pincode: '',
      city_id: '',
      area: '',
      delivery_status: 'active',
      status: 'active'
    });
  };

  // Get status info
  const getStatusInfo = (status) => {
    return statusOptions.find(s => s.value === status) || statusOptions[0];
  };

  // Get delivery status info
  const getDeliveryStatusInfo = (status) => {
    return deliveryStatusOptions.find(s => s.value === status) || deliveryStatusOptions[0];
  };

  // Format number
  const formatNumber = (number) => {
    return new Intl.NumberFormat('en-IN').format(number);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading Indian geography..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Indian Geography</h1>
          <p className="text-gray-600">Manage Indian states, cities, and pincodes</p>
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
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert type="danger" title="Error">
          {error}
        </Alert>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'states', name: 'States & Territories', icon: Map },
              { id: 'cities', name: 'Cities & Districts', icon: Building2 },
              { id: 'pincodes', name: 'Pincodes', icon: MapPin },
              { id: 'validation', name: 'Address Validation', icon: CheckCircle }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {/* States Tab */}
          {activeTab === 'states' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search states..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full"
                  />
                </div>
                <Button
                  onClick={() => setShowAddState(true)}
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add State</span>
                </Button>
              </div>

              {/* States List */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredStates.map((state) => {
                  const statusInfo = getStatusInfo(state.status);
                  
                  return (
                    <div key={state.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                            <Map className="w-5 h-5 text-blue-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">{state.name}</h3>
                            <p className="text-sm text-gray-500">{state.code} • {state.capital}</p>
                          </div>
                        </div>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                          {statusInfo.label}
                        </span>
                      </div>
                      
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Region:</span>
                          <span className="text-sm font-medium text-gray-900">{state.region}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Population:</span>
                          <span className="text-sm font-medium text-gray-900">{formatNumber(state.population)}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Area:</span>
                          <span className="text-sm font-medium text-gray-900">{formatNumber(state.area)} km²</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setViewingState(state)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingState(state);
                            setStateFormData(state);
                            setShowAddState(true);
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteState(state.id)}
                          className="text-danger-600 hover:text-danger-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Cities Tab */}
          {activeTab === 'cities' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search cities..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full"
                  />
                </div>
                <div className="w-48">
                  <select
                    value={stateFilter}
                    onChange={(e) => setStateFilter(e.target.value)}
                    className="form-input"
                  >
                    <option value="all">All States</option>
                    {states.map(state => (
                      <option key={state.id} value={state.id}>
                        {state.name}
                      </option>
                    ))}
                  </select>
                </div>
                <Button
                  onClick={() => setShowAddCity(true)}
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add City</span>
                </Button>
              </div>

              {/* Cities List */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredCities.map((city) => {
                  const statusInfo = getStatusInfo(city.status);
                  const state = states.find(s => s.id === city.state_id);
                  
                  return (
                    <div key={city.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                            <Building2 className="w-5 h-5 text-green-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">{city.name}</h3>
                            <p className="text-sm text-gray-500">{state?.name} • {city.district}</p>
                          </div>
                        </div>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                          {statusInfo.label}
                        </span>
                      </div>
                      
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Population:</span>
                          <span className="text-sm font-medium text-gray-900">{formatNumber(city.population)}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Area:</span>
                          <span className="text-sm font-medium text-gray-900">{formatNumber(city.area)} km²</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setViewingCity(city)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingCity(city);
                            setCityFormData(city);
                            setShowAddCity(true);
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteCity(city.id)}
                          className="text-danger-600 hover:text-danger-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Pincodes Tab */}
          {activeTab === 'pincodes' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search pincodes..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full"
                  />
                </div>
                <div className="w-48">
                  <select
                    value={stateFilter}
                    onChange={(e) => setStateFilter(e.target.value)}
                    className="form-input"
                  >
                    <option value="all">All States</option>
                    {states.map(state => (
                      <option key={state.id} value={state.id}>
                        {state.name}
                      </option>
                    ))}
                  </select>
                </div>
                <Button
                  onClick={() => setShowAddPincode(true)}
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Pincode</span>
                </Button>
              </div>

              {/* Pincodes List */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredPincodes.map((pincode) => {
                  const statusInfo = getStatusInfo(pincode.status);
                  const deliveryStatusInfo = getDeliveryStatusInfo(pincode.delivery_status);
                  const city = cities.find(c => c.id === pincode.city_id);
                  
                  return (
                    <div key={pincode.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                            <MapPin className="w-5 h-5 text-purple-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">{pincode.pincode}</h3>
                            <p className="text-sm text-gray-500">{city?.name} • {pincode.area}</p>
                          </div>
                        </div>
                        <div className="flex flex-col space-y-1">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                            {statusInfo.label}
                          </span>
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${deliveryStatusInfo.bgColor} ${deliveryStatusInfo.color}`}>
                            {deliveryStatusInfo.label}
                          </span>
                        </div>
                      </div>
                      
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Area:</span>
                          <span className="text-sm font-medium text-gray-900">{pincode.area}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">City:</span>
                          <span className="text-sm font-medium text-gray-900">{city?.name || 'N/A'}</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setViewingPincode(pincode)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingPincode(pincode);
                            setPincodeFormData(pincode);
                            setShowAddPincode(true);
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeletePincode(pincode.id)}
                          className="text-danger-600 hover:text-danger-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Address Validation Tab */}
          {activeTab === 'validation' && (
            <div className="space-y-6">
              <div className="text-center py-12">
                <CheckCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Address Validation</h3>
                <p className="text-gray-500">Indian address format validation will be implemented here</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Add/Edit State Modal */}
      {showAddState && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowAddState(false)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Map className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {editingState ? 'Edit Indian State' : 'Add New Indian State'}
                      </h3>
                      <p className="text-sm text-gray-500">Create or update Indian state</p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setShowAddState(false);
                      setEditingState(null);
                      resetStateForm();
                    }}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        State Name *
                      </label>
                      <Input
                        value={stateFormData.name}
                        onChange={(e) => handleStateFieldChange('name', e.target.value)}
                        placeholder="Enter state name"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        State Code *
                      </label>
                      <Input
                        value={stateFormData.code}
                        onChange={(e) => handleStateFieldChange('code', e.target.value)}
                        placeholder="Enter state code"
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Capital
                      </label>
                      <Input
                        value={stateFormData.capital}
                        onChange={(e) => handleStateFieldChange('capital', e.target.value)}
                        placeholder="Enter capital city"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Region
                      </label>
                      <select
                        value={stateFormData.region}
                        onChange={(e) => handleStateFieldChange('region', e.target.value)}
                        className="form-input"
                      >
                        <option value="">Select Region</option>
                        {indianRegions.map(region => (
                          <option key={region.value} value={region.value}>
                            {region.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Population
                      </label>
                      <Input
                        type="number"
                        value={stateFormData.population}
                        onChange={(e) => handleStateFieldChange('population', e.target.value)}
                        placeholder="Enter population"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Area (km²)
                      </label>
                      <Input
                        type="number"
                        value={stateFormData.area}
                        onChange={(e) => handleStateFieldChange('area', e.target.value)}
                        placeholder="Enter area"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Status
                    </label>
                    <select
                      value={stateFormData.status}
                      onChange={(e) => handleStateFieldChange('status', e.target.value)}
                      className="form-input"
                    >
                      {statusOptions.map(status => (
                        <option key={status.value} value={status.value}>
                          {status.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <Button
                  onClick={editingState ? handleEditState : handleAddState}
                  loading={saving}
                  className="w-full sm:w-auto sm:ml-3"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {editingState ? 'Update State' : 'Create State'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowAddState(false);
                    setEditingState(null);
                    resetStateForm();
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
    </div>
  );
};

export default IndianGeography;
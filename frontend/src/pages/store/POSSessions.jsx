import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { storeService } from '../../services/storeService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  Monitor, 
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
  Map,
  Receipt,
  FileCheck,
  TrendingDown,
  PieChart,
  MapPin,
  Phone,
  Mail as MailIcon,
  ExternalLink,
  ChevronRight,
  ChevronDown,
  TreePine,
  Building,
  Lock,
  Unlock,
  Power,
  Zap as ZapIcon,
  Timer,
  LogIn,
  LogOut
} from 'lucide-react';

const POSSessions = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [filteredSessions, setFilteredSessions] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [storeFilter, setStoreFilter] = useState('all');
  const [showAddSession, setShowAddSession] = useState(false);
  const [editingSession, setEditingSession] = useState(null);
  const [viewingSession, setViewingSession] = useState(null);
  const [activeTab, setActiveTab] = useState('sessions');
  const [stores, setStores] = useState([]);

  // Session form data
  const [sessionFormData, setSessionFormData] = useState({
    store_id: '',
    cashier_name: '',
    cashier_id: '',
    opening_cash: 0,
    expected_cash: 0,
    notes: '',
    status: 'active'
  });

  // Session statuses
  const sessionStatuses = [
    { value: 'active', label: 'Active', color: 'text-green-600', bgColor: 'bg-green-100' },
    { value: 'closed', label: 'Closed', color: 'text-gray-600', bgColor: 'bg-gray-100' },
    { value: 'suspended', label: 'Suspended', color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
    { value: 'locked', label: 'Locked', color: 'text-red-600', bgColor: 'bg-red-100' }
  ];

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const [sessionsData, storesData] = await Promise.all([
          storeService.getPOSSessions(),
          storeService.getStores()
        ]);
        
        setSessions(sessionsData);
        setStores(storesData);
        setFilteredSessions(sessionsData);
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

  // Filter sessions
  useEffect(() => {
    let filtered = sessions;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(session =>
        session.cashier_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        session.cashier_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        session.session_id.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(session => session.status === statusFilter);
    }

    // Store filter
    if (storeFilter !== 'all') {
      filtered = filtered.filter(session => session.store_id === storeFilter);
    }

    setFilteredSessions(filtered);
  }, [sessions, searchTerm, statusFilter, storeFilter]);

  // Handle form field changes
  const handleFieldChange = (field, value) => {
    setSessionFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle add session
  const handleAddSession = async () => {
    try {
      setSaving(true);
      await storeService.createPOSSession(sessionFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'POS session created successfully',
      });
      setShowAddSession(false);
      resetForm();
      // Refresh sessions
      const sessionsData = await storeService.getPOSSessions();
      setSessions(sessionsData);
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

  // Handle edit session
  const handleEditSession = async () => {
    try {
      setSaving(true);
      await storeService.updatePOSSession(editingSession.id, sessionFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'POS session updated successfully',
      });
      setEditingSession(null);
      setShowAddSession(false);
      resetForm();
      // Refresh sessions
      const sessionsData = await storeService.getPOSSessions();
      setSessions(sessionsData);
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

  // Handle delete session
  const handleDeleteSession = async (sessionId) => {
    if (!window.confirm('Are you sure you want to delete this POS session?')) {
      return;
    }

    try {
      await storeService.deletePOSSession(sessionId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'POS session deleted successfully',
      });
      // Refresh sessions
      const sessionsData = await storeService.getPOSSessions();
      setSessions(sessionsData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle close session
  const handleCloseSession = async (sessionId) => {
    if (!window.confirm('Are you sure you want to close this POS session?')) {
      return;
    }

    try {
      await storeService.closePOSSession(sessionId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'POS session closed successfully',
      });
      // Refresh sessions
      const sessionsData = await storeService.getPOSSessions();
      setSessions(sessionsData);
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
    setSessionFormData({
      store_id: '',
      cashier_name: '',
      cashier_id: '',
      opening_cash: 0,
      expected_cash: 0,
      notes: '',
      status: 'active'
    });
  };

  // Get status info
  const getStatusInfo = (status) => {
    return sessionStatuses.find(s => s.value === status) || sessionStatuses[0];
  };

  // Get store name
  const getStoreName = (storeId) => {
    const store = stores.find(s => s.id === storeId);
    return store ? store.name : 'Unknown Store';
  };

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  // Format time
  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString();
  };

  // Calculate session duration
  const calculateDuration = (startTime, endTime) => {
    if (!startTime || !endTime) return 'N/A';
    const start = new Date(startTime);
    const end = new Date(endTime);
    const diff = end - start;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading POS sessions..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">POS Sessions</h1>
          <p className="text-gray-600">Manage POS sessions and cashier operations</p>
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
            onClick={() => setShowAddSession(true)}
            className="flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Start Session</span>
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
              { id: 'sessions', name: 'Sessions', icon: Monitor },
              { id: 'reports', name: 'Session Reports', icon: FileText },
              { id: 'analytics', name: 'Session Analytics', icon: BarChart3 },
              { id: 'security', name: 'Session Security', icon: Shield }
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
          {/* Sessions Tab */}
          {activeTab === 'sessions' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search sessions..."
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
                    {sessionStatuses.map(status => (
                      <option key={status.value} value={status.value}>
                        {status.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="w-48">
                  <select
                    value={storeFilter}
                    onChange={(e) => setStoreFilter(e.target.value)}
                    className="form-input"
                  >
                    <option value="all">All Stores</option>
                    {stores.map(store => (
                      <option key={store.id} value={store.id}>
                        {store.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Sessions List */}
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Session ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Store
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Cashier
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Opening Cash
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Duration
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredSessions.map((session) => {
                      const statusInfo = getStatusInfo(session.status);
                      
                      return (
                        <tr key={session.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {session.session_id}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {getStoreName(session.store_id)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                                <User className="w-4 h-4 text-gray-600" />
                              </div>
                              <div className="ml-3">
                                <div className="text-sm font-medium text-gray-900">{session.cashier_name}</div>
                                <div className="text-sm text-gray-500">{session.cashier_id}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatCurrency(session.opening_cash)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                              {statusInfo.label}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {calculateDuration(session.start_time, session.end_time)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <div className="flex items-center space-x-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => setViewingSession(session)}
                              >
                                <Eye className="w-4 h-4" />
                              </Button>
                              {session.status === 'active' && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handleCloseSession(session.id)}
                                  className="text-green-600 hover:text-green-700"
                                >
                                  <Stop className="w-4 h-4" />
                                </Button>
                              )}
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => {
                                  setEditingSession(session);
                                  setSessionFormData(session);
                                  setShowAddSession(true);
                                }}
                              >
                                <Edit className="w-4 h-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleDeleteSession(session.id)}
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
          )}

          {/* Session Reports Tab */}
          {activeTab === 'reports' && (
            <div className="space-y-6">
              <div className="text-center py-12">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Session Reports</h3>
                <p className="text-gray-500">Session-based reporting will be implemented here</p>
              </div>
            </div>
          )}

          {/* Session Analytics Tab */}
          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <div className="text-center py-12">
                <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Session Analytics</h3>
                <p className="text-gray-500">Session performance analysis will be implemented here</p>
              </div>
            </div>
          )}

          {/* Session Security Tab */}
          {activeTab === 'security' && (
            <div className="space-y-6">
              <div className="text-center py-12">
                <Shield className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Session Security</h3>
                <p className="text-gray-500">Session access control will be implemented here</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Add/Edit Session Modal */}
      {showAddSession && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowAddSession(false)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Monitor className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {editingSession ? 'Edit POS Session' : 'Start New POS Session'}
                      </h3>
                      <p className="text-sm text-gray-500">Create or update POS session</p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setShowAddSession(false);
                      setEditingSession(null);
                      resetForm();
                    }}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Store *
                    </label>
                    <select
                      value={sessionFormData.store_id}
                      onChange={(e) => handleFieldChange('store_id', e.target.value)}
                      className="form-input"
                      required
                    >
                      <option value="">Select Store</option>
                      {stores.map(store => (
                        <option key={store.id} value={store.id}>
                          {store.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Cashier Name *
                      </label>
                      <Input
                        value={sessionFormData.cashier_name}
                        onChange={(e) => handleFieldChange('cashier_name', e.target.value)}
                        placeholder="Enter cashier name"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Cashier ID *
                      </label>
                      <Input
                        value={sessionFormData.cashier_id}
                        onChange={(e) => handleFieldChange('cashier_id', e.target.value)}
                        placeholder="Enter cashier ID"
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Opening Cash *
                      </label>
                      <Input
                        type="number"
                        value={sessionFormData.opening_cash}
                        onChange={(e) => handleFieldChange('opening_cash', parseFloat(e.target.value) || 0)}
                        placeholder="Enter opening cash amount"
                        required
                        min="0"
                        step="0.01"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Expected Cash
                      </label>
                      <Input
                        type="number"
                        value={sessionFormData.expected_cash}
                        onChange={(e) => handleFieldChange('expected_cash', parseFloat(e.target.value) || 0)}
                        placeholder="Enter expected cash amount"
                        min="0"
                        step="0.01"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Notes
                    </label>
                    <textarea
                      value={sessionFormData.notes}
                      onChange={(e) => handleFieldChange('notes', e.target.value)}
                      rows={3}
                      className="form-input"
                      placeholder="Enter session notes"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Status
                    </label>
                    <select
                      value={sessionFormData.status}
                      onChange={(e) => handleFieldChange('status', e.target.value)}
                      className="form-input"
                    >
                      {sessionStatuses.map(status => (
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
                  onClick={editingSession ? handleEditSession : handleAddSession}
                  loading={saving}
                  className="w-full sm:w-auto sm:ml-3"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {editingSession ? 'Update Session' : 'Start Session'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowAddSession(false);
                    setEditingSession(null);
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
    </div>
  );
};

export default POSSessions;
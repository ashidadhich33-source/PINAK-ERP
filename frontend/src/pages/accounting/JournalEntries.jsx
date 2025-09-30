import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { accountingService } from '../../services/accountingService';
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
  Upload, 
  RefreshCw, 
  Save, 
  X,
  CheckCircle,
  AlertTriangle,
  Clock,
  Eye,
  RotateCcw,
  Calculator,
  Calendar,
  User,
  DollarSign
} from 'lucide-react';

const JournalEntries = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [entries, setEntries] = useState([]);
  const [filteredEntries, setFilteredEntries] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingEntry, setEditingEntry] = useState(null);
  const [viewingEntry, setViewingEntry] = useState(null);

  // Form data
  const [formData, setFormData] = useState({
    entry_date: new Date().toISOString().split('T')[0],
    reference: '',
    description: '',
    total_debit: 0,
    total_credit: 0,
    status: 'draft',
    entries: [
      { account_id: '', description: '', debit: 0, credit: 0 },
      { account_id: '', description: '', debit: 0, credit: 0 }
    ]
  });

  // Entry statuses
  const entryStatuses = [
    { value: 'draft', label: 'Draft', color: 'text-gray-600', bgColor: 'bg-gray-100' },
    { value: 'pending', label: 'Pending', color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
    { value: 'approved', label: 'Approved', color: 'text-green-600', bgColor: 'bg-green-100' },
    { value: 'rejected', label: 'Rejected', color: 'text-red-600', bgColor: 'bg-red-100' },
    { value: 'reversed', label: 'Reversed', color: 'text-purple-600', bgColor: 'bg-purple-100' }
  ];

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const [entriesData, accountsData] = await Promise.all([
          accountingService.getJournalEntries(),
          accountingService.getChartOfAccounts()
        ]);
        
        setEntries(entriesData);
        setFilteredEntries(entriesData);
        setAccounts(accountsData);
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

  // Filter entries
  useEffect(() => {
    let filtered = entries;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(entry =>
        entry.reference.toLowerCase().includes(searchTerm.toLowerCase()) ||
        entry.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(entry => entry.status === statusFilter);
    }

    setFilteredEntries(filtered);
  }, [entries, searchTerm, statusFilter]);

  // Handle form field changes
  const handleFieldChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle entry line changes
  const handleEntryLineChange = (index, field, value) => {
    const newEntries = [...formData.entries];
    newEntries[index] = {
      ...newEntries[index],
      [field]: value
    };
    
    // Calculate totals
    const totalDebit = newEntries.reduce((sum, entry) => sum + (parseFloat(entry.debit) || 0), 0);
    const totalCredit = newEntries.reduce((sum, entry) => sum + (parseFloat(entry.credit) || 0), 0);
    
    setFormData(prev => ({
      ...prev,
      entries: newEntries,
      total_debit: totalDebit,
      total_credit: totalCredit
    }));
  };

  // Add new entry line
  const addEntryLine = () => {
    setFormData(prev => ({
      ...prev,
      entries: [...prev.entries, { account_id: '', description: '', debit: 0, credit: 0 }]
    }));
  };

  // Remove entry line
  const removeEntryLine = (index) => {
    if (formData.entries.length > 2) {
      const newEntries = formData.entries.filter((_, i) => i !== index);
      const totalDebit = newEntries.reduce((sum, entry) => sum + (parseFloat(entry.debit) || 0), 0);
      const totalCredit = newEntries.reduce((sum, entry) => sum + (parseFloat(entry.credit) || 0), 0);
      
      setFormData(prev => ({
        ...prev,
        entries: newEntries,
        total_debit: totalDebit,
        total_credit: totalCredit
      }));
    }
  };

  // Handle add entry
  const handleAddEntry = async () => {
    try {
      setSaving(true);
      await accountingService.createJournalEntry(formData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Journal entry created successfully',
      });
      setShowAddForm(false);
      resetForm();
      // Refresh entries
      const entriesData = await accountingService.getJournalEntries();
      setEntries(entriesData);
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

  // Handle edit entry
  const handleEditEntry = async () => {
    try {
      setSaving(true);
      await accountingService.updateJournalEntry(editingEntry.id, formData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Journal entry updated successfully',
      });
      setEditingEntry(null);
      setShowAddForm(false);
      resetForm();
      // Refresh entries
      const entriesData = await accountingService.getJournalEntries();
      setEntries(entriesData);
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

  // Handle delete entry
  const handleDeleteEntry = async (entryId) => {
    if (!window.confirm('Are you sure you want to delete this journal entry?')) {
      return;
    }

    try {
      await accountingService.deleteJournalEntry(entryId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Journal entry deleted successfully',
      });
      // Refresh entries
      const entriesData = await accountingService.getJournalEntries();
      setEntries(entriesData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle approve entry
  const handleApproveEntry = async (entryId) => {
    try {
      await accountingService.approveJournalEntry(entryId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Journal entry approved successfully',
      });
      // Refresh entries
      const entriesData = await accountingService.getJournalEntries();
      setEntries(entriesData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle reverse entry
  const handleReverseEntry = async (entryId) => {
    if (!window.confirm('Are you sure you want to reverse this journal entry?')) {
      return;
    }

    try {
      await accountingService.reverseJournalEntry(entryId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Journal entry reversed successfully',
      });
      // Refresh entries
      const entriesData = await accountingService.getJournalEntries();
      setEntries(entriesData);
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
      entry_date: new Date().toISOString().split('T')[0],
      reference: '',
      description: '',
      total_debit: 0,
      total_credit: 0,
      status: 'draft',
      entries: [
        { account_id: '', description: '', debit: 0, credit: 0 },
        { account_id: '', description: '', debit: 0, credit: 0 }
      ]
    });
  };

  // Get status info
  const getStatusInfo = (status) => {
    return entryStatuses.find(s => s.value === status) || entryStatuses[0];
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
        <LoadingSpinner size="lg" text="Loading journal entries..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Journal Entries</h1>
          <p className="text-gray-600">Manage manual journal entries and transactions</p>
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
            <span>Add Entry</span>
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
              placeholder="Search entries..."
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
              {entryStatuses.map(status => (
                <option key={status.value} value={status.value}>
                  {status.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Entries List */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Journal Entries</h2>
          <p className="text-sm text-gray-500">Manage your journal entries</p>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Reference
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Debit
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Credit
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
              {filteredEntries.map((entry) => {
                const statusInfo = getStatusInfo(entry.status);
                return (
                  <tr key={entry.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(entry.entry_date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {entry.reference}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {entry.description}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(entry.total_debit)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(entry.total_credit)}
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
                          onClick={() => setViewingEntry(entry)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingEntry(entry);
                            setFormData(entry);
                            setShowAddForm(true);
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        {entry.status === 'draft' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleApproveEntry(entry.id)}
                            className="text-green-600 hover:text-green-700"
                          >
                            <CheckCircle className="w-4 h-4" />
                          </Button>
                        )}
                        {entry.status === 'approved' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleReverseEntry(entry.id)}
                            className="text-purple-600 hover:text-purple-700"
                          >
                            <RotateCcw className="w-4 h-4" />
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteEntry(entry.id)}
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

      {/* Add/Edit Entry Modal */}
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
                        {editingEntry ? 'Edit Journal Entry' : 'Add New Journal Entry'}
                      </h3>
                      <p className="text-sm text-gray-500">Create or update journal entry</p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setShowAddForm(false);
                      setEditingEntry(null);
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
                        Entry Date *
                      </label>
                      <Input
                        type="date"
                        value={formData.entry_date}
                        onChange={(e) => handleFieldChange('entry_date', e.target.value)}
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Reference *
                      </label>
                      <Input
                        value={formData.reference}
                        onChange={(e) => handleFieldChange('reference', e.target.value)}
                        placeholder="JE-001"
                        required
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
                        {entryStatuses.map(status => (
                          <option key={status.value} value={status.value}>
                            {status.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => handleFieldChange('description', e.target.value)}
                      rows={3}
                      className="form-input"
                      placeholder="Journal entry description..."
                    />
                  </div>
                  
                  {/* Entry Lines */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm font-medium text-gray-900">Entry Lines</h4>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={addEntryLine}
                      >
                        <Plus className="w-4 h-4 mr-1" />
                        Add Line
                      </Button>
                    </div>
                    
                    <div className="space-y-3">
                      {formData.entries.map((entry, index) => (
                        <div key={index} className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg">
                          <div className="flex-1">
                            <select
                              value={entry.account_id}
                              onChange={(e) => handleEntryLineChange(index, 'account_id', e.target.value)}
                              className="form-input"
                              required
                            >
                              <option value="">Select Account</option>
                              {accounts.map(account => (
                                <option key={account.id} value={account.id}>
                                  {account.code} - {account.name}
                                </option>
                              ))}
                            </select>
                          </div>
                          <div className="flex-1">
                            <Input
                              value={entry.description}
                              onChange={(e) => handleEntryLineChange(index, 'description', e.target.value)}
                              placeholder="Line description"
                            />
                          </div>
                          <div className="w-32">
                            <Input
                              type="number"
                              value={entry.debit}
                              onChange={(e) => handleEntryLineChange(index, 'debit', parseFloat(e.target.value) || 0)}
                              placeholder="0.00"
                            />
                          </div>
                          <div className="w-32">
                            <Input
                              type="number"
                              value={entry.credit}
                              onChange={(e) => handleEntryLineChange(index, 'credit', parseFloat(e.target.value) || 0)}
                              placeholder="0.00"
                            />
                          </div>
                          {formData.entries.length > 2 && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => removeEntryLine(index)}
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
                      <span className="font-medium text-gray-900">Total Debit: </span>
                      <span className="text-gray-900">{formatCurrency(formData.total_debit)}</span>
                    </div>
                    <div className="text-sm">
                      <span className="font-medium text-gray-900">Total Credit: </span>
                      <span className="text-gray-900">{formatCurrency(formData.total_credit)}</span>
                    </div>
                    <div className="text-sm">
                      <span className="font-medium text-gray-900">Difference: </span>
                      <span className={`${Math.abs(formData.total_debit - formData.total_credit) === 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatCurrency(Math.abs(formData.total_debit - formData.total_credit))}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <Button
                  onClick={editingEntry ? handleEditEntry : handleAddEntry}
                  loading={saving}
                  disabled={Math.abs(formData.total_debit - formData.total_credit) !== 0}
                  className="w-full sm:w-auto sm:ml-3"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {editingEntry ? 'Update Entry' : 'Create Entry'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowAddForm(false);
                    setEditingEntry(null);
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

      {/* View Entry Modal */}
      {viewingEntry && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setViewingEntry(null)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">Journal Entry Details</h3>
                      <p className="text-sm text-gray-500">View journal entry information</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setViewingEntry(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Date</p>
                      <p className="text-sm font-medium text-gray-900">{formatDate(viewingEntry.entry_date)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Reference</p>
                      <p className="text-sm font-medium text-gray-900">{viewingEntry.reference}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Status</p>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusInfo(viewingEntry.status).bgColor} ${getStatusInfo(viewingEntry.status).color}`}>
                        {getStatusInfo(viewingEntry.status).label}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Total Amount</p>
                      <p className="text-sm font-medium text-gray-900">{formatCurrency(viewingEntry.total_debit)}</p>
                    </div>
                  </div>
                  
                  {viewingEntry.description && (
                    <div>
                      <p className="text-sm text-gray-500">Description</p>
                      <p className="text-sm text-gray-900">{viewingEntry.description}</p>
                    </div>
                  )}
                  
                  <div>
                    <p className="text-sm text-gray-500 mb-2">Entry Lines</p>
                    <div className="space-y-2">
                      {viewingEntry.entries?.map((entry, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex-1">
                            <p className="text-sm font-medium text-gray-900">{entry.account_name}</p>
                            <p className="text-xs text-gray-500">{entry.description}</p>
                          </div>
                          <div className="flex items-center space-x-4">
                            <div className="text-sm text-gray-900">
                              Debit: {formatCurrency(entry.debit)}
                            </div>
                            <div className="text-sm text-gray-900">
                              Credit: {formatCurrency(entry.credit)}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <Button
                  onClick={() => setViewingEntry(null)}
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

export default JournalEntries;
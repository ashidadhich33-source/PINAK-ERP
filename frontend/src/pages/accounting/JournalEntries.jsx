import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import { accountingService } from '../../services/accountingService';
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
  FileText,
  Eye,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  Clock,
  DollarSign,
  Filter,
  Calendar
} from 'lucide-react';

const JournalEntries = () => {
  const { addNotification } = useApp();
  const [journalEntries, setJournalEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    status: 'all',
    dateRange: 'all',
    sortBy: 'entry_date',
    sortOrder: 'desc',
  });

  // Fetch journal entries
  const fetchJournalEntries = async () => {
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
      
      const data = await accountingService.getJournalEntries(params);
      setJournalEntries(data);
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
    fetchJournalEntries();
  }, [searchTerm, filters]);

  // Handle search
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  // Handle filter change
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Handle delete journal entry
  const handleDelete = async (entryId) => {
    if (!window.confirm('Are you sure you want to delete this journal entry?')) {
      return;
    }

    try {
      await accountingService.deleteJournalEntry(entryId);
      setJournalEntries(prev => prev.filter(entry => entry.id !== entryId));
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Journal entry deleted successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle post journal entry
  const handlePost = async (entryId) => {
    try {
      await accountingService.postJournalEntry(entryId);
      setJournalEntries(prev => prev.map(entry => 
        entry.id === entryId 
          ? { ...entry, status: 'posted' }
          : entry
      ));
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Journal entry posted successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle reverse journal entry
  const handleReverse = async (entryId) => {
    if (!window.confirm('Are you sure you want to reverse this journal entry?')) {
      return;
    }

    try {
      await accountingService.reverseJournalEntry(entryId);
      setJournalEntries(prev => prev.map(entry => 
        entry.id === entryId 
          ? { ...entry, is_reversed: true }
          : entry
      ));
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Journal entry reversed successfully',
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
      await accountingService.exportAccountingData('csv', 'journal_entries', filters);
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: 'Journal entries export will be downloaded shortly',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Get status icon and color
  const getStatusInfo = (status) => {
    switch (status) {
      case 'posted':
        return {
          icon: CheckCircle,
          color: 'text-success-600',
          bgColor: 'bg-success-100',
        };
      case 'draft':
        return {
          icon: Clock,
          color: 'text-warning-600',
          bgColor: 'bg-warning-100',
        };
      case 'cancelled':
        return {
          icon: XCircle,
          color: 'text-danger-600',
          bgColor: 'bg-danger-100',
        };
      default:
        return {
          icon: Clock,
          color: 'text-gray-600',
          bgColor: 'bg-gray-100',
        };
    }
  };

  // Table columns
  const columns = [
    {
      key: 'entry_number',
      label: 'Entry Number',
      render: (entry) => (
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <FileText className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <p className="font-medium text-gray-900">#{entry.entry_number}</p>
            <p className="text-sm text-gray-500">{new Date(entry.entry_date).toLocaleDateString()}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'reference',
      label: 'Reference',
      render: (entry) => (
        <div>
          <p className="font-medium text-gray-900">{entry.reference_number || '-'}</p>
          <p className="text-sm text-gray-500">{entry.reference_type || '-'}</p>
        </div>
      ),
    },
    {
      key: 'narration',
      label: 'Narration',
      render: (entry) => (
        <div className="max-w-xs">
          <p className="text-sm text-gray-900 truncate">{entry.narration || '-'}</p>
        </div>
      ),
    },
    {
      key: 'amounts',
      label: 'Amounts',
      render: (entry) => (
        <div>
          <p className="font-medium text-gray-900">Debit: ₹{entry.total_debit}</p>
          <p className="text-sm text-gray-500">Credit: ₹{entry.total_credit}</p>
        </div>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (entry) => {
        const statusInfo = getStatusInfo(entry.status);
        const Icon = statusInfo.icon;
        return (
          <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
            <Icon className="w-3 h-3 mr-1" />
            {entry.status}
          </span>
        );
      },
    },
    {
      key: 'reversed',
      label: 'Reversed',
      render: (entry) => (
        <div className="flex items-center space-x-2">
          {entry.is_reversed ? (
            <XCircle className="w-4 h-4 text-danger-500" />
          ) : (
            <CheckCircle className="w-4 h-4 text-success-500" />
          )}
          <span className="text-sm text-gray-900">
            {entry.is_reversed ? 'Yes' : 'No'}
          </span>
        </div>
      ),
    },
    {
      key: 'created_at',
      label: 'Created',
      render: (entry) => new Date(entry.created_at).toLocaleDateString(),
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (entry) => (
        <div className="flex items-center space-x-2">
          <Link
            to={`/accounting/journal-entries/${entry.id}`}
            className="text-primary-600 hover:text-primary-900"
          >
            <Eye className="w-4 h-4" />
          </Link>
          {entry.status === 'draft' && (
            <>
              <Link
                to={`/accounting/journal-entries/${entry.id}/edit`}
                className="text-secondary-600 hover:text-secondary-900"
              >
                <Edit className="w-4 h-4" />
              </Link>
              <button
                onClick={() => handlePost(entry.id)}
                className="text-success-600 hover:text-success-900"
                title="Post Entry"
              >
                <CheckCircle className="w-4 h-4" />
              </button>
            </>
          )}
          {entry.status === 'posted' && !entry.is_reversed && (
            <button
              onClick={() => handleReverse(entry.id)}
              className="text-warning-600 hover:text-warning-900"
              title="Reverse Entry"
            >
              <XCircle className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={() => handleDelete(entry.id)}
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
          <p className="text-gray-600">Manage your accounting journal entries</p>
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
          <Link to="/accounting/journal-entries/new">
            <Button className="flex items-center space-x-2">
              <Plus className="w-4 h-4" />
              <span>New Entry</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="md:col-span-2">
            <div className="relative">
              <Input
                placeholder="Search journal entries..."
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
              <option value="draft">Draft</option>
              <option value="posted">Posted</option>
              <option value="cancelled">Cancelled</option>
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
              <option value="quarter">This Quarter</option>
              <option value="year">This Year</option>
            </select>
          </div>
          
          <div>
            <select
              value={filters.sortBy}
              onChange={(e) => handleFilterChange('sortBy', e.target.value)}
              className="form-input"
            >
              <option value="entry_date">Sort by Date</option>
              <option value="entry_number">Sort by Number</option>
              <option value="total_debit">Sort by Amount</option>
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
      <div className="bg-white rounded-lg shadow">
        <DataTable
          data={journalEntries}
          columns={columns}
          loading={loading}
          emptyMessage="No journal entries found"
        />
      </div>
    </div>
  );
};

export default JournalEntries;
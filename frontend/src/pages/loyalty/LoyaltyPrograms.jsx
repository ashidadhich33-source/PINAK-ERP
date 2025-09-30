import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import { loyaltyProgramService } from '../../services/loyaltyProgramService';
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
  Gift,
  Eye,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  Star,
  Users,
  TrendingUp,
  Calendar,
  Settings,
  Target
} from 'lucide-react';

const LoyaltyPrograms = () => {
  const { addNotification } = useApp();
  const [loyaltyPrograms, setLoyaltyPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    status: 'all',
    programType: 'all',
    sortBy: 'program_name',
    sortOrder: 'asc',
  });

  // Fetch loyalty programs
  const fetchLoyaltyPrograms = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        search: searchTerm,
        status: filters.status !== 'all' ? filters.status : undefined,
        program_type: filters.programType !== 'all' ? filters.programType : undefined,
        sort_by: filters.sortBy,
        sort_order: filters.sortOrder,
      };
      
      const data = await loyaltyProgramService.getLoyaltyPrograms(params);
      setLoyaltyPrograms(data);
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
    fetchLoyaltyPrograms();
  }, [searchTerm, filters]);

  // Handle search
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  // Handle filter change
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Handle delete program
  const handleDelete = async (programId) => {
    if (!window.confirm('Are you sure you want to delete this loyalty program?')) {
      return;
    }

    try {
      await loyaltyProgramService.deleteLoyaltyProgram(programId);
      setLoyaltyPrograms(prev => prev.filter(program => program.id !== programId));
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Loyalty program deleted successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle activate/deactivate program
  const handleToggleStatus = async (programId, currentStatus) => {
    try {
      if (currentStatus) {
        await loyaltyProgramService.deactivateLoyaltyProgram(programId);
      } else {
        await loyaltyProgramService.activateLoyaltyProgram(programId);
      }
      setLoyaltyPrograms(prev => prev.map(program => 
        program.id === programId 
          ? { ...program, is_active: !currentStatus }
          : program
      ));
      addNotification({
        type: 'success',
        title: 'Success',
        message: `Loyalty program ${!currentStatus ? 'activated' : 'deactivated'} successfully`,
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
      await loyaltyProgramService.exportLoyaltyData('csv', 'programs', filters);
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: 'Loyalty programs export will be downloaded shortly',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Get program type color
  const getProgramTypeColor = (type) => {
    switch (type) {
      case 'points':
        return 'text-blue-600 bg-blue-100';
      case 'tier':
        return 'text-purple-600 bg-purple-100';
      case 'cashback':
        return 'text-green-600 bg-green-100';
      case 'stamp':
        return 'text-orange-600 bg-orange-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  // Table columns
  const columns = [
    {
      key: 'program_name',
      label: 'Program Name',
      render: (program) => (
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <Gift className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <p className="font-medium text-gray-900">{program.program_name}</p>
            <p className="text-sm text-gray-500">{program.program_code}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'program_type',
      label: 'Type',
      render: (program) => (
        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getProgramTypeColor(program.program_type)}`}>
          {program.program_type}
        </span>
      ),
    },
    {
      key: 'description',
      label: 'Description',
      render: (program) => (
        <div className="max-w-xs">
          <p className="text-sm text-gray-900 truncate">{program.description || '-'}</p>
        </div>
      ),
    },
    {
      key: 'date_range',
      label: 'Date Range',
      render: (program) => (
        <div>
          <p className="text-sm text-gray-900">
            {new Date(program.start_date).toLocaleDateString()}
          </p>
          <p className="text-xs text-gray-500">
            to {program.end_date ? new Date(program.end_date).toLocaleDateString() : 'Ongoing'}
          </p>
        </div>
      ),
    },
    {
      key: 'auto_enrollment',
      label: 'Auto Enrollment',
      render: (program) => (
        <div className="flex items-center space-x-2">
          {program.auto_enrollment ? (
            <CheckCircle className="w-4 h-4 text-success-500" />
          ) : (
            <XCircle className="w-4 h-4 text-gray-400" />
          )}
          <span className="text-sm text-gray-900">
            {program.auto_enrollment ? 'Yes' : 'No'}
          </span>
        </div>
      ),
    },
    {
      key: 'is_active',
      label: 'Status',
      render: (program) => (
        <div className="flex items-center space-x-2">
          {program.is_active ? (
            <CheckCircle className="w-4 h-4 text-success-500" />
          ) : (
            <XCircle className="w-4 h-4 text-danger-500" />
          )}
          <span className="text-sm text-gray-900">
            {program.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>
      ),
    },
    {
      key: 'created_at',
      label: 'Created',
      render: (program) => new Date(program.created_at).toLocaleDateString(),
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (program) => (
        <div className="flex items-center space-x-2">
          <Link
            to={`/loyalty/programs/${program.id}`}
            className="text-primary-600 hover:text-primary-900"
          >
            <Eye className="w-4 h-4" />
          </Link>
          <Link
            to={`/loyalty/programs/${program.id}/edit`}
            className="text-secondary-600 hover:text-secondary-900"
          >
            <Edit className="w-4 h-4" />
          </Link>
          <Link
            to={`/loyalty/programs/${program.id}/tiers`}
            className="text-purple-600 hover:text-purple-900"
            title="Manage Tiers"
          >
            <Star className="w-4 h-4" />
          </Link>
          <Link
            to={`/loyalty/programs/${program.id}/points`}
            className="text-blue-600 hover:text-blue-900"
            title="Manage Points"
          >
            <Target className="w-4 h-4" />
          </Link>
          <button
            onClick={() => handleToggleStatus(program.id, program.is_active)}
            className={program.is_active ? "text-warning-600 hover:text-warning-900" : "text-success-600 hover:text-success-900"}
            title={program.is_active ? "Deactivate" : "Activate"}
          >
            {program.is_active ? <XCircle className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />}
          </button>
          <button
            onClick={() => handleDelete(program.id)}
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
        <LoadingSpinner size="lg" text="Loading loyalty programs..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Loyalty Programs</h1>
          <p className="text-gray-600">Manage customer loyalty programs and rewards</p>
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
          <Link to="/loyalty/programs/new">
            <Button className="flex items-center space-x-2">
              <Plus className="w-4 h-4" />
              <span>New Program</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-primary-100 rounded-md flex items-center justify-center">
                <Gift className="w-5 h-5 text-primary-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Programs</p>
              <p className="text-2xl font-semibold text-gray-900">{loyaltyPrograms.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-green-100 rounded-md flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-green-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Active Programs</p>
              <p className="text-2xl font-semibold text-gray-900">
                {loyaltyPrograms.filter(p => p.is_active).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-100 rounded-md flex items-center justify-center">
                <Users className="w-5 h-5 text-blue-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Members</p>
              <p className="text-2xl font-semibold text-gray-900">-</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-purple-100 rounded-md flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-purple-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Points Issued</p>
              <p className="text-2xl font-semibold text-gray-900">-</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="md:col-span-2">
            <div className="relative">
              <Input
                placeholder="Search loyalty programs..."
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
            </select>
          </div>
          
          <div>
            <select
              value={filters.programType}
              onChange={(e) => handleFilterChange('programType', e.target.value)}
              className="form-input"
            >
              <option value="all">All Types</option>
              <option value="points">Points</option>
              <option value="tier">Tier</option>
              <option value="cashback">Cashback</option>
              <option value="stamp">Stamp</option>
            </select>
          </div>
          
          <div>
            <select
              value={filters.sortBy}
              onChange={(e) => handleFilterChange('sortBy', e.target.value)}
              className="form-input"
            >
              <option value="program_name">Sort by Name</option>
              <option value="program_code">Sort by Code</option>
              <option value="start_date">Sort by Date</option>
              <option value="program_type">Sort by Type</option>
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
          data={loyaltyPrograms}
          columns={columns}
          loading={loading}
          emptyMessage="No loyalty programs found"
        />
      </div>
    </div>
  );
};

export default LoyaltyPrograms;
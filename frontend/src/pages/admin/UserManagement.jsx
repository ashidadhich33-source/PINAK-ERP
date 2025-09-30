import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import { authService } from '../../services/authService';
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
  Users,
  Eye,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  Clock,
  Filter,
  Calendar,
  Shield,
  Key,
  Mail,
  Phone,
  MapPin,
  Settings,
  UserCheck,
  UserX,
  Lock,
  Unlock
} from 'lucide-react';

const UserManagement = () => {
  const { addNotification } = useApp();
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [permissions, setPermissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    status: 'all',
    role: 'all',
    sortBy: 'created_at',
    sortOrder: 'desc',
  });

  // Fetch users
  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        search: searchTerm,
        status: filters.status !== 'all' ? filters.status : undefined,
        role: filters.role !== 'all' ? filters.role : undefined,
        sort_by: filters.sortBy,
        sort_order: filters.sortOrder,
      };
      
      const data = await authService.getUsers(params);
      setUsers(data);
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

  // Fetch roles
  const fetchRoles = async () => {
    try {
      const data = await authService.getRoles();
      setRoles(data);
    } catch (err) {
      console.error('Failed to fetch roles:', err);
    }
  };

  // Fetch permissions
  const fetchPermissions = async () => {
    try {
      const data = await authService.getPermissions();
      setPermissions(data);
    } catch (err) {
      console.error('Failed to fetch permissions:', err);
    }
  };

  useEffect(() => {
    fetchUsers();
    fetchRoles();
    fetchPermissions();
  }, [searchTerm, filters]);

  // Handle search
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  // Handle filter change
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Handle delete user
  const handleDelete = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) {
      return;
    }

    try {
      await authService.deleteUser(userId);
      setUsers(prev => prev.filter(user => user.id !== userId));
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'User deleted successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle toggle user status
  const handleToggleStatus = async (userId, currentStatus) => {
    try {
      const user = await authService.getUser(userId);
      await authService.updateUser(userId, {
        ...user,
        is_active: !currentStatus
      });
      setUsers(prev => prev.map(user => 
        user.id === userId 
          ? { ...user, is_active: !currentStatus }
          : user
      ));
      addNotification({
        type: 'success',
        title: 'Success',
        message: `User ${!currentStatus ? 'activated' : 'deactivated'} successfully`,
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle lock/unlock user
  const handleToggleLock = async (userId, currentLockStatus) => {
    try {
      const user = await authService.getUser(userId);
      await authService.updateUser(userId, {
        ...user,
        is_locked: !currentLockStatus
      });
      setUsers(prev => prev.map(user => 
        user.id === userId 
          ? { ...user, is_locked: !currentLockStatus }
          : user
      ));
      addNotification({
        type: 'success',
        title: 'Success',
        message: `User ${!currentLockStatus ? 'locked' : 'unlocked'} successfully`,
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
      await authService.exportUsers(filters);
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: 'Users export will be downloaded shortly',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Get user status info
  const getUserStatusInfo = (user) => {
    if (user.is_locked) {
      return {
        icon: Lock,
        color: 'text-danger-600',
        bgColor: 'bg-danger-100',
        text: 'Locked'
      };
    }
    if (user.is_active) {
      return {
        icon: CheckCircle,
        color: 'text-success-600',
        bgColor: 'bg-success-100',
        text: 'Active'
      };
    }
    return {
      icon: XCircle,
      color: 'text-gray-600',
      bgColor: 'bg-gray-100',
      text: 'Inactive'
    };
  };

  // Table columns
  const columns = [
    {
      key: 'user_info',
      label: 'User',
      render: (user) => (
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <Users className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <p className="font-medium text-gray-900">{user.first_name} {user.last_name}</p>
            <p className="text-sm text-gray-500">{user.email}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'contact',
      label: 'Contact',
      render: (user) => (
        <div>
          <p className="text-sm text-gray-900">{user.phone || '-'}</p>
          <p className="text-sm text-gray-500">{user.address || '-'}</p>
        </div>
      ),
    },
    {
      key: 'role',
      label: 'Role',
      render: (user) => (
        <div>
          <p className="font-medium text-gray-900">{user.role?.role_name || 'No Role'}</p>
          <p className="text-sm text-gray-500">{user.role?.description || ''}</p>
        </div>
      ),
    },
    {
      key: 'permissions',
      label: 'Permissions',
      render: (user) => (
        <div className="flex flex-wrap gap-1">
          {user.permissions?.slice(0, 3).map((permission, index) => (
            <span key={index} className="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
              {permission.permission_name}
            </span>
          ))}
          {user.permissions?.length > 3 && (
            <span className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded">
              +{user.permissions.length - 3} more
            </span>
          )}
        </div>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (user) => {
        const statusInfo = getUserStatusInfo(user);
        const Icon = statusInfo.icon;
        return (
          <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
            <Icon className="w-3 h-3 mr-1" />
            {statusInfo.text}
          </span>
        );
      },
    },
    {
      key: 'last_login',
      label: 'Last Login',
      render: (user) => (
        <div>
          <p className="font-medium text-gray-900">
            {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
          </p>
          <p className="text-sm text-gray-500">
            {user.last_login ? new Date(user.last_login).toLocaleTimeString() : ''}
          </p>
        </div>
      ),
    },
    {
      key: 'created_at',
      label: 'Created',
      render: (user) => new Date(user.created_at).toLocaleDateString(),
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (user) => (
        <div className="flex items-center space-x-2">
          <Link
            to={`/admin/users/${user.id}`}
            className="text-primary-600 hover:text-primary-900"
          >
            <Eye className="w-4 h-4" />
          </Link>
          <Link
            to={`/admin/users/${user.id}/edit`}
            className="text-secondary-600 hover:text-secondary-900"
          >
            <Edit className="w-4 h-4" />
          </Link>
          <button
            onClick={() => handleToggleStatus(user.id, user.is_active)}
            className={user.is_active ? "text-warning-600 hover:text-warning-900" : "text-success-600 hover:text-success-900"}
            title={user.is_active ? "Deactivate" : "Activate"}
          >
            {user.is_active ? <UserX className="w-4 h-4" /> : <UserCheck className="w-4 h-4" />}
          </button>
          <button
            onClick={() => handleToggleLock(user.id, user.is_locked)}
            className={user.is_locked ? "text-success-600 hover:text-success-900" : "text-warning-600 hover:text-warning-900"}
            title={user.is_locked ? "Unlock" : "Lock"}
          >
            {user.is_locked ? <Unlock className="w-4 h-4" /> : <Lock className="w-4 h-4" />}
          </button>
          <button
            onClick={() => handleDelete(user.id)}
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
        <LoadingSpinner size="lg" text="Loading users..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-600">Manage users, roles, and permissions</p>
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
          <Link to="/admin/users/new">
            <Button className="flex items-center space-x-2">
              <Plus className="w-4 h-4" />
              <span>New User</span>
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
                <Users className="w-5 h-5 text-primary-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Users</p>
              <p className="text-2xl font-semibold text-gray-900">{users.length}</p>
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
              <p className="text-sm font-medium text-gray-500">Active Users</p>
              <p className="text-2xl font-semibold text-gray-900">
                {users.filter(u => u.is_active).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-100 rounded-md flex items-center justify-center">
                <Shield className="w-5 h-5 text-blue-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Roles</p>
              <p className="text-2xl font-semibold text-gray-900">{roles.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-purple-100 rounded-md flex items-center justify-center">
                <Key className="w-5 h-5 text-purple-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Permissions</p>
              <p className="text-2xl font-semibold text-gray-900">{permissions.length}</p>
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
                placeholder="Search users..."
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
              <option value="locked">Locked</option>
            </select>
          </div>
          
          <div>
            <select
              value={filters.role}
              onChange={(e) => handleFilterChange('role', e.target.value)}
              className="form-input"
            >
              <option value="all">All Roles</option>
              {roles.map(role => (
                <option key={role.id} value={role.id}>{role.role_name}</option>
              ))}
            </select>
          </div>
          
          <div>
            <select
              value={filters.sortBy}
              onChange={(e) => handleFilterChange('sortBy', e.target.value)}
              className="form-input"
            >
              <option value="created_at">Sort by Date</option>
              <option value="first_name">Sort by Name</option>
              <option value="email">Sort by Email</option>
              <option value="last_login">Sort by Last Login</option>
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
          data={users}
          columns={columns}
          loading={loading}
          emptyMessage="No users found"
        />
      </div>
    </div>
  );
};

export default UserManagement;
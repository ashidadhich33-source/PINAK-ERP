import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import { companiesService } from '../../services/companiesService';
import Button from '../../components/common/Button';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  Building2, 
  Edit, 
  Trash2, 
  ArrowLeft,
  MapPin,
  Phone,
  Mail,
  Globe,
  FileText,
  Calendar,
  User
} from 'lucide-react';

const CompanyDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addNotification } = useApp();
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);

  // Fetch company details
  const fetchCompany = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [companyData, statsData] = await Promise.all([
        companiesService.getCompany(id),
        companiesService.getCompanyStats(id).catch(() => null),
      ]);
      
      setCompany(companyData);
      setStats(statsData);
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
    fetchCompany();
  }, [id]);

  // Handle delete
  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this company? This action cannot be undone.')) {
      return;
    }

    try {
      await companiesService.deleteCompany(id);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Company deleted successfully',
      });
      navigate('/companies');
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle toggle status
  const handleToggleStatus = async () => {
    try {
      await companiesService.toggleCompanyStatus(id);
      setCompany(prev => ({ ...prev, is_active: !prev.is_active }));
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Company status updated successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading company details..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <Alert type="danger" title="Error">
          {error}
        </Alert>
        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            onClick={() => navigate('/companies')}
            className="flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Companies</span>
          </Button>
        </div>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="text-center py-12">
        <Building2 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Company not found</h3>
        <p className="text-gray-600 mb-4">The company you're looking for doesn't exist.</p>
        <Button
          variant="outline"
          onClick={() => navigate('/companies')}
          className="flex items-center space-x-2"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Companies</span>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            onClick={() => navigate('/companies')}
            className="flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back</span>
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{company.name}</h1>
            <p className="text-gray-600">Company Details</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button
            variant={company.is_active ? 'danger' : 'success'}
            onClick={handleToggleStatus}
          >
            {company.is_active ? 'Deactivate' : 'Activate'}
          </Button>
          <Link to={`/companies/${company.id}/edit`}>
            <Button variant="outline" className="flex items-center space-x-2">
              <Edit className="w-4 h-4" />
              <span>Edit</span>
            </Button>
          </Link>
          <Button
            variant="danger"
            onClick={handleDelete}
            className="flex items-center space-x-2"
          >
            <Trash2 className="w-4 h-4" />
            <span>Delete</span>
          </Button>
        </div>
      </div>

      {/* Company Information */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Basic Information */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Building2 className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">Basic Information</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">Company Name</label>
                <p className="text-sm text-gray-900">{company.name}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Email</label>
                <p className="text-sm text-gray-900">{company.email || '-'}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Phone</label>
                <p className="text-sm text-gray-900">{company.phone || '-'}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Website</label>
                <p className="text-sm text-gray-900">
                  {company.website ? (
                    <a 
                      href={company.website} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-primary-600 hover:text-primary-900"
                    >
                      {company.website}
                    </a>
                  ) : '-'}
                </p>
              </div>
            </div>
          </div>

          {/* Address Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-2 mb-4">
              <MapPin className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">Address Information</h3>
            </div>
            
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-gray-500">Address</label>
                <p className="text-sm text-gray-900">{company.address || '-'}</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">City</label>
                  <p className="text-sm text-gray-900">{company.city || '-'}</p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-500">State</label>
                  <p className="text-sm text-gray-900">{company.state || '-'}</p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-500">Country</label>
                  <p className="text-sm text-gray-900">{company.country || '-'}</p>
                </div>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Postal Code</label>
                <p className="text-sm text-gray-900">{company.postal_code || '-'}</p>
              </div>
            </div>
          </div>

          {/* Tax Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-2 mb-4">
              <FileText className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">Tax Information</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">GST Number</label>
                <p className="text-sm text-gray-900">{company.gst_number || '-'}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">PAN Number</label>
                <p className="text-sm text-gray-900">{company.pan_number || '-'}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Status Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Status</h3>
            <div className="flex items-center space-x-3">
              <span className={`inline-flex px-3 py-1 text-sm font-medium rounded-full ${
                company.is_active 
                  ? 'bg-success-100 text-success-800' 
                  : 'bg-danger-100 text-danger-800'
              }`}>
                {company.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>

          {/* Statistics */}
          {stats && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Statistics</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Total Customers</span>
                  <span className="text-sm font-medium text-gray-900">{stats.total_customers || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Total Sales</span>
                  <span className="text-sm font-medium text-gray-900">₹{stats.total_sales || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Total Orders</span>
                  <span className="text-sm font-medium text-gray-900">{stats.total_orders || 0}</span>
                </div>
              </div>
            </div>
          )}

          {/* Meta Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Meta Information</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Calendar className="w-4 h-4 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Created</p>
                  <p className="text-xs text-gray-500">
                    {new Date(company.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              
              {company.updated_at && (
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Last Updated</p>
                    <p className="text-xs text-gray-500">
                      {new Date(company.updated_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompanyDetails;
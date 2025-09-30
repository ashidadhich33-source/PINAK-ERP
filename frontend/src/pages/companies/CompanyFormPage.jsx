import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import { companiesService } from '../../services/companiesService';
import CompanyForm from '../../components/companies/CompanyForm';
import Button from '../../components/common/Button';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { ArrowLeft, Building2 } from 'lucide-react';

const CompanyFormPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addNotification } = useApp();
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(!!id);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const isEdit = !!id;

  // Fetch company for editing
  useEffect(() => {
    if (isEdit) {
      const fetchCompany = async () => {
        try {
          setLoading(true);
          setError(null);
          const companyData = await companiesService.getCompany(id);
          setCompany(companyData);
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

      fetchCompany();
    }
  }, [id, isEdit, addNotification]);

  // Handle form submission
  const handleSubmit = async (data) => {
    try {
      setSubmitting(true);
      setError(null);

      if (isEdit) {
        await companiesService.updateCompany(id, data);
        addNotification({
          type: 'success',
          title: 'Success',
          message: 'Company updated successfully',
        });
      } else {
        await companiesService.createCompany(data);
        addNotification({
          type: 'success',
          title: 'Success',
          message: 'Company created successfully',
        });
      }

      navigate('/companies');
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading company..." />
      </div>
    );
  }

  if (error && isEdit) {
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
            <h1 className="text-2xl font-bold text-gray-900">
              {isEdit ? 'Edit Company' : 'Create New Company'}
            </h1>
            <p className="text-gray-600">
              {isEdit ? 'Update company information' : 'Add a new company to your system'}
            </p>
          </div>
        </div>
      </div>

      {/* Form */}
      <CompanyForm
        company={company}
        onSubmit={handleSubmit}
        loading={submitting}
        error={error}
      />
    </div>
  );
};

export default CompanyFormPage;
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import { customersService } from '../../services/customersService';
import CustomerForm from '../../components/customers/CustomerForm';
import Button from '../../components/common/Button';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { ArrowLeft, Users } from 'lucide-react';

const CustomerFormPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addNotification } = useApp();
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(!!id);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const isEdit = !!id;

  // Fetch customer for editing
  useEffect(() => {
    if (isEdit) {
      const fetchCustomer = async () => {
        try {
          setLoading(true);
          setError(null);
          const customerData = await customersService.getCustomer(id);
          setCustomer(customerData);
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

      fetchCustomer();
    }
  }, [id, isEdit, addNotification]);

  // Handle form submission
  const handleSubmit = async (data) => {
    try {
      setSubmitting(true);
      setError(null);

      if (isEdit) {
        await customersService.updateCustomer(id, data);
        addNotification({
          type: 'success',
          title: 'Success',
          message: 'Customer updated successfully',
        });
      } else {
        await customersService.createCustomer(data);
        addNotification({
          type: 'success',
          title: 'Success',
          message: 'Customer created successfully',
        });
      }

      navigate('/customers');
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
        <LoadingSpinner size="lg" text="Loading customer..." />
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
            onClick={() => navigate('/customers')}
            className="flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Customers</span>
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
            onClick={() => navigate('/customers')}
            className="flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back</span>
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {isEdit ? 'Edit Customer' : 'Create New Customer'}
            </h1>
            <p className="text-gray-600">
              {isEdit ? 'Update customer information' : 'Add a new customer to your system'}
            </p>
          </div>
        </div>
      </div>

      {/* Form */}
      <CustomerForm
        customer={customer}
        onSubmit={handleSubmit}
        loading={submitting}
        error={error}
      />
    </div>
  );
};

export default CustomerFormPage;
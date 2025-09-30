import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useApp } from '../../contexts/AppContext';
import { customersService } from '../../services/customersService';
import Button from '../common/Button';
import Input from '../common/Input';
import Alert from '../common/Alert';
import { Users, MapPin, Phone, Mail, User, Building2 } from 'lucide-react';

const CustomerForm = ({ 
  customer = null, 
  onSubmit, 
  loading = false, 
  error = null 
}) => {
  const { addNotification } = useApp();
  const [customerGroups, setCustomerGroups] = useState([]);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm({
    defaultValues: customer || {
      name: '',
      email: '',
      phone: '',
      address: '',
      city: '',
      state: '',
      country: '',
      postal_code: '',
      gst_number: '',
      pan_number: '',
      group_id: null,
      is_active: true,
    },
  });

  // Fetch customer groups
  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const groups = await customersService.getCustomerGroups();
        setCustomerGroups(groups);
      } catch (err) {
        console.error('Failed to fetch customer groups:', err);
      }
    };

    fetchGroups();
  }, []);

  const handleFormSubmit = async (data) => {
    try {
      await onSubmit(data);
      addNotification({
        type: 'success',
        title: 'Success',
        message: customer ? 'Customer updated successfully' : 'Customer created successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message || 'Failed to save customer',
      });
    }
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      {error && (
        <Alert type="danger" title="Error">
          {error}
        </Alert>
      )}

      {/* Basic Information */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Users className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-medium text-gray-900">Basic Information</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Customer Name"
            required
            error={errors.name?.message}
            {...register('name', {
              required: 'Customer name is required',
              minLength: {
                value: 2,
                message: 'Customer name must be at least 2 characters',
              },
            })}
          />
          
          <Input
            label="Email"
            type="email"
            error={errors.email?.message}
            {...register('email', {
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: 'Invalid email address',
              },
            })}
          />
          
          <Input
            label="Phone"
            type="tel"
            error={errors.phone?.message}
            {...register('phone')}
          />
          
          <div>
            <label className="form-label">Customer Group</label>
            <select
              {...register('group_id')}
              className="form-input"
            >
              <option value="">Select a group</option>
              {customerGroups.map((group) => (
                <option key={group.id} value={group.id}>
                  {group.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Address Information */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 mb-4">
          <MapPin className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-medium text-gray-900">Address Information</h3>
        </div>
        
        <div className="space-y-4">
          <Input
            label="Address"
            error={errors.address?.message}
            {...register('address')}
          />
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              label="City"
              error={errors.city?.message}
              {...register('city')}
            />
            
            <Input
              label="State"
              error={errors.state?.message}
              {...register('state')}
            />
            
            <Input
              label="Country"
              error={errors.country?.message}
              {...register('country')}
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Postal Code"
              error={errors.postal_code?.message}
              {...register('postal_code')}
            />
          </div>
        </div>
      </div>

      {/* Tax Information */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Building2 className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-medium text-gray-900">Tax Information</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="GST Number"
            error={errors.gst_number?.message}
            {...register('gst_number')}
          />
          
          <Input
            label="PAN Number"
            error={errors.pan_number?.message}
            {...register('pan_number')}
          />
        </div>
      </div>

      {/* Additional Information */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 mb-4">
          <User className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-medium text-gray-900">Additional Information</h3>
        </div>
        
        <div className="space-y-4">
          <div className="flex items-center">
            <input
              type="checkbox"
              {...register('is_active')}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label className="ml-2 text-sm text-gray-700">
              Customer is active
            </label>
          </div>
        </div>
      </div>

      {/* Form Actions */}
      <div className="flex items-center justify-end space-x-4">
        <Button
          type="button"
          variant="outline"
          onClick={() => reset()}
        >
          Reset
        </Button>
        <Button
          type="submit"
          loading={loading}
        >
          {customer ? 'Update Customer' : 'Create Customer'}
        </Button>
      </div>
    </form>
  );
};

export default CustomerForm;
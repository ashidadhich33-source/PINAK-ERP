import React from 'react';
import { useForm } from 'react-hook-form';
import { useApp } from '../../contexts/AppContext';
import Button from '../common/Button';
import Input from '../common/Input';
import Alert from '../common/Alert';
import { Building2, MapPin, Phone, Mail, Globe, FileText } from 'lucide-react';

const CompanyForm = ({ 
  company = null, 
  onSubmit, 
  loading = false, 
  error = null 
}) => {
  const { addNotification } = useApp();
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm({
    defaultValues: company || {
      name: '',
      email: '',
      phone: '',
      website: '',
      address: '',
      city: '',
      state: '',
      country: '',
      postal_code: '',
      gst_number: '',
      pan_number: '',
      description: '',
      is_active: true,
    },
  });

  const handleFormSubmit = async (data) => {
    try {
      await onSubmit(data);
      addNotification({
        type: 'success',
        title: 'Success',
        message: company ? 'Company updated successfully' : 'Company created successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message || 'Failed to save company',
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
          <Building2 className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-medium text-gray-900">Basic Information</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Company Name"
            required
            error={errors.name?.message}
            {...register('name', {
              required: 'Company name is required',
              minLength: {
                value: 2,
                message: 'Company name must be at least 2 characters',
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
          
          <Input
            label="Website"
            type="url"
            error={errors.website?.message}
            {...register('website')}
          />
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
          <FileText className="w-5 h-5 text-primary-600" />
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
          <FileText className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-medium text-gray-900">Additional Information</h3>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="form-label">Description</label>
            <textarea
              {...register('description')}
              rows={4}
              className="form-input"
              placeholder="Enter company description..."
            />
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              {...register('is_active')}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label className="ml-2 text-sm text-gray-700">
              Company is active
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
          {company ? 'Update Company' : 'Create Company'}
        </Button>
      </div>
    </form>
  );
};

export default CompanyForm;
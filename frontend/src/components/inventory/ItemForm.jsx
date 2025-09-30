import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useApp } from '../../contexts/AppContext';
import { inventoryService } from '../../services/inventoryService';
import Button from '../common/Button';
import Input from '../common/Input';
import Alert from '../common/Alert';
import { Package, Tag, DollarSign, BarChart3, AlertTriangle } from 'lucide-react';

const ItemForm = ({ 
  item = null, 
  onSubmit, 
  loading = false, 
  error = null 
}) => {
  const { addNotification } = useApp();
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);
  const [units, setUnits] = useState([]);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm({
    defaultValues: item || {
      name: '',
      sku: '',
      description: '',
      category_id: null,
      brand_id: null,
      unit_id: null,
      cost_price: 0,
      selling_price: 0,
      stock_quantity: 0,
      min_stock_level: 0,
      max_stock_level: 0,
      is_active: true,
    },
  });

  // Fetch dropdown data
  useEffect(() => {
    const fetchDropdownData = async () => {
      try {
        const [categoriesData, brandsData, unitsData] = await Promise.all([
          inventoryService.getCategories(),
          inventoryService.getBrands(),
          inventoryService.getUnits(),
        ]);
        
        setCategories(categoriesData);
        setBrands(brandsData);
        setUnits(unitsData);
      } catch (err) {
        console.error('Failed to fetch dropdown data:', err);
      }
    };

    fetchDropdownData();
  }, []);

  const handleFormSubmit = async (data) => {
    try {
      await onSubmit(data);
      addNotification({
        type: 'success',
        title: 'Success',
        message: item ? 'Item updated successfully' : 'Item created successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message || 'Failed to save item',
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
          <Package className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-medium text-gray-900">Basic Information</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Item Name"
            required
            error={errors.name?.message}
            {...register('name', {
              required: 'Item name is required',
              minLength: {
                value: 2,
                message: 'Item name must be at least 2 characters',
              },
            })}
          />
          
          <Input
            label="SKU"
            required
            error={errors.sku?.message}
            {...register('sku', {
              required: 'SKU is required',
              minLength: {
                value: 3,
                message: 'SKU must be at least 3 characters',
              },
            })}
          />
          
          <div className="md:col-span-2">
            <label className="form-label">Description</label>
            <textarea
              {...register('description')}
              rows={3}
              className="form-input"
              placeholder="Enter item description..."
            />
          </div>
        </div>
      </div>

      {/* Category and Brand */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Tag className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-medium text-gray-900">Classification</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="form-label">Category</label>
            <select
              {...register('category_id')}
              className="form-input"
            >
              <option value="">Select a category</option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="form-label">Brand</label>
            <select
              {...register('brand_id')}
              className="form-input"
            >
              <option value="">Select a brand</option>
              {brands.map((brand) => (
                <option key={brand.id} value={brand.id}>
                  {brand.name}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="form-label">Unit</label>
            <select
              {...register('unit_id')}
              className="form-input"
            >
              <option value="">Select a unit</option>
              {units.map((unit) => (
                <option key={unit.id} value={unit.id}>
                  {unit.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Pricing */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 mb-4">
          <DollarSign className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-medium text-gray-900">Pricing</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Cost Price"
            type="number"
            step="0.01"
            min="0"
            required
            error={errors.cost_price?.message}
            {...register('cost_price', {
              required: 'Cost price is required',
              min: {
                value: 0,
                message: 'Cost price must be greater than or equal to 0',
              },
            })}
          />
          
          <Input
            label="Selling Price"
            type="number"
            step="0.01"
            min="0"
            required
            error={errors.selling_price?.message}
            {...register('selling_price', {
              required: 'Selling price is required',
              min: {
                value: 0,
                message: 'Selling price must be greater than or equal to 0',
              },
            })}
          />
        </div>
      </div>

      {/* Stock Management */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 mb-4">
          <BarChart3 className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-medium text-gray-900">Stock Management</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            label="Current Stock"
            type="number"
            min="0"
            required
            error={errors.stock_quantity?.message}
            {...register('stock_quantity', {
              required: 'Stock quantity is required',
              min: {
                value: 0,
                message: 'Stock quantity must be greater than or equal to 0',
              },
            })}
          />
          
          <Input
            label="Minimum Stock Level"
            type="number"
            min="0"
            required
            error={errors.min_stock_level?.message}
            {...register('min_stock_level', {
              required: 'Minimum stock level is required',
              min: {
                value: 0,
                message: 'Minimum stock level must be greater than or equal to 0',
              },
            })}
          />
          
          <Input
            label="Maximum Stock Level"
            type="number"
            min="0"
            error={errors.max_stock_level?.message}
            {...register('max_stock_level', {
              min: {
                value: 0,
                message: 'Maximum stock level must be greater than or equal to 0',
              },
            })}
          />
        </div>
      </div>

      {/* Additional Information */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 mb-4">
          <AlertTriangle className="w-5 h-5 text-primary-600" />
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
              Item is active
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
          {item ? 'Update Item' : 'Create Item'}
        </Button>
      </div>
    </form>
  );
};

export default ItemForm;
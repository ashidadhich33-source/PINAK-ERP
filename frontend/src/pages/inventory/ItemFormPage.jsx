import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import { inventoryService } from '../../services/inventoryService';
import ItemForm from '../../components/inventory/ItemForm';
import Button from '../../components/common/Button';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { ArrowLeft, Package } from 'lucide-react';

const ItemFormPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addNotification } = useApp();
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(!!id);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const isEdit = !!id;

  // Fetch item for editing
  useEffect(() => {
    if (isEdit) {
      const fetchItem = async () => {
        try {
          setLoading(true);
          setError(null);
          const itemData = await inventoryService.getItem(id);
          setItem(itemData);
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

      fetchItem();
    }
  }, [id, isEdit, addNotification]);

  // Handle form submission
  const handleSubmit = async (data) => {
    try {
      setSubmitting(true);
      setError(null);

      if (isEdit) {
        await inventoryService.updateItem(id, data);
        addNotification({
          type: 'success',
          title: 'Success',
          message: 'Item updated successfully',
        });
      } else {
        await inventoryService.createItem(data);
        addNotification({
          type: 'success',
          title: 'Success',
          message: 'Item created successfully',
        });
      }

      navigate('/inventory');
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
        <LoadingSpinner size="lg" text="Loading item..." />
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
            onClick={() => navigate('/inventory')}
            className="flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Inventory</span>
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
            onClick={() => navigate('/inventory')}
            className="flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back</span>
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {isEdit ? 'Edit Item' : 'Create New Item'}
            </h1>
            <p className="text-gray-600">
              {isEdit ? 'Update item information' : 'Add a new item to your inventory'}
            </p>
          </div>
        </div>
      </div>

      {/* Form */}
      <ItemForm
        item={item}
        onSubmit={handleSubmit}
        loading={submitting}
        error={error}
      />
    </div>
  );
};

export default ItemFormPage;
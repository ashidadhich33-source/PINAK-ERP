import React, { useState, useEffect } from 'react';
import { usePos } from '../../contexts/PosContext';
import { useApp } from '../../contexts/AppContext';
import { posService } from '../../services/posService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  ShoppingCart, 
  Users, 
  Package, 
  DollarSign,
  Plus,
  Minus,
  Trash2,
  Search,
  CreditCard,
  CheckCircle,
  X
} from 'lucide-react';

const POSTerminal = () => {
  const { 
    cart, 
    customer, 
    paymentMethod, 
    discount, 
    tax, 
    total, 
    loading, 
    error,
    addToCart,
    removeFromCart,
    updateCartItem,
    clearCart,
    setCustomer,
    setPaymentMethod,
    setDiscount,
    setTax,
    setLoading,
    setError,
    clearError
  } = usePos();
  
  const { addNotification } = useApp();
  const [inventory, setInventory] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCustomerModal, setShowCustomerModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [processingPayment, setProcessingPayment] = useState(false);

  // Fetch initial data
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setLoading(true);
        const [inventoryData, customersData, paymentMethodsData] = await Promise.all([
          posService.getPosInventory(),
          posService.getPosCustomers(),
          posService.getPaymentMethods(),
        ]);
        
        setInventory(inventoryData);
        setCustomers(customersData);
        setPaymentMethods(paymentMethodsData);
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

    fetchInitialData();
  }, []);

  // Handle search
  const handleSearch = async (query) => {
    if (query.length < 2) return;
    
    try {
      const results = await posService.searchPosInventory(query);
      setInventory(results);
    } catch (err) {
      console.error('Search error:', err);
    }
  };

  // Handle add to cart
  const handleAddToCart = (item) => {
    addToCart({
      id: item.id,
      name: item.name,
      price: item.selling_price,
      sku: item.sku,
      quantity: 1,
    });
  };

  // Handle update quantity
  const handleUpdateQuantity = (itemId, quantity) => {
    if (quantity <= 0) {
      removeFromCart(itemId);
    } else {
      updateCartItem(itemId, { quantity });
    }
  };

  // Handle remove from cart
  const handleRemoveFromCart = (itemId) => {
    removeFromCart(itemId);
  };

  // Handle process payment
  const handleProcessPayment = async () => {
    if (cart.length === 0) {
      addNotification({
        type: 'warning',
        title: 'Empty Cart',
        message: 'Please add items to cart before processing payment',
      });
      return;
    }

    if (!paymentMethod) {
      addNotification({
        type: 'warning',
        title: 'Payment Method Required',
        message: 'Please select a payment method',
      });
      return;
    }

    try {
      setProcessingPayment(true);
      
      const transactionData = {
        items: cart,
        customer_id: customer?.id,
        payment_method: paymentMethod,
        discount_percentage: discount,
        tax_percentage: tax,
        total_amount: total,
      };

      const transaction = await posService.createPosTransaction(transactionData);
      
      addNotification({
        type: 'success',
        title: 'Payment Processed',
        message: 'Transaction completed successfully',
      });

      // Clear cart and reset
      clearCart();
      setCustomer(null);
      setPaymentMethod(null);
      setDiscount(0);
      setTax(0);
      
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Payment Failed',
        message: err.message,
      });
    } finally {
      setProcessingPayment(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading POS terminal..." />
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-screen">
      {/* Left Panel - Inventory */}
      <div className="lg:col-span-2 space-y-4">
        {/* Search */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="relative">
            <Input
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                handleSearch(e.target.value);
              }}
              className="pl-10"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
          </div>
        </div>

        {/* Inventory Grid */}
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Products</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 max-h-96 overflow-y-auto">
            {inventory.map((item) => (
              <button
                key={item.id}
                onClick={() => handleAddToCart(item)}
                className="flex flex-col items-center p-3 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors"
              >
                <Package className="w-8 h-8 text-primary-600 mb-2" />
                <span className="text-sm font-medium text-gray-900 text-center truncate w-full">
                  {item.name}
                </span>
                <span className="text-xs text-gray-500">₹{item.selling_price}</span>
                <span className="text-xs text-gray-500">Stock: {item.stock_quantity}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Right Panel - Cart & Checkout */}
      <div className="space-y-4">
        {/* Cart */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Cart</h3>
            <Button
              variant="outline"
              size="sm"
              onClick={clearCart}
              className="text-danger-600 hover:text-danger-900"
            >
              Clear
            </Button>
          </div>
          
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {cart.length === 0 ? (
              <p className="text-gray-500 text-center py-4">Cart is empty</p>
            ) : (
              cart.map((item) => (
                <div key={item.id} className="flex items-center justify-between p-2 border border-gray-200 rounded">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{item.name}</p>
                    <p className="text-xs text-gray-500">₹{item.price}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleUpdateQuantity(item.id, item.quantity - 1)}
                    >
                      <Minus className="w-3 h-3" />
                    </Button>
                    <span className="text-sm font-medium">{item.quantity}</span>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                    >
                      <Plus className="w-3 h-3" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleRemoveFromCart(item.id)}
                      className="text-danger-600 hover:text-danger-900"
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Customer Selection */}
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Customer</h3>
          {customer ? (
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">{customer.name}</p>
                <p className="text-xs text-gray-500">{customer.email}</p>
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={() => setCustomer(null)}
              >
                <X className="w-3 h-3" />
              </Button>
            </div>
          ) : (
            <Button
              variant="outline"
              onClick={() => setShowCustomerModal(true)}
              className="w-full"
            >
              <Users className="w-4 h-4 mr-2" />
              Select Customer
            </Button>
          )}
        </div>

        {/* Payment Summary */}
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Payment Summary</h3>
          
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Subtotal</span>
              <span className="text-sm font-medium">₹{cart.reduce((sum, item) => sum + (item.price * item.quantity), 0)}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Discount ({discount}%)</span>
              <span className="text-sm font-medium">-₹{((cart.reduce((sum, item) => sum + (item.price * item.quantity), 0) * discount) / 100)}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-sm text-gray-500">Tax ({tax}%)</span>
              <span className="text-sm font-medium">₹{((cart.reduce((sum, item) => sum + (item.price * item.quantity), 0) * (1 - discount / 100)) * tax / 100)}</span>
            </div>
            
            <div className="border-t border-gray-200 pt-2">
              <div className="flex justify-between">
                <span className="text-lg font-medium text-gray-900">Total</span>
                <span className="text-lg font-bold text-gray-900">₹{total}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Payment Method */}
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Payment Method</h3>
          {paymentMethod ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <CreditCard className="w-4 h-4 text-gray-400" />
                <span className="text-sm font-medium text-gray-900">{paymentMethod.name}</span>
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={() => setPaymentMethod(null)}
              >
                <X className="w-3 h-3" />
              </Button>
            </div>
          ) : (
            <Button
              variant="outline"
              onClick={() => setShowPaymentModal(true)}
              className="w-full"
            >
              <CreditCard className="w-4 h-4 mr-2" />
              Select Payment Method
            </Button>
          )}
        </div>

        {/* Process Payment */}
        <Button
          onClick={handleProcessPayment}
          loading={processingPayment}
          disabled={cart.length === 0 || !paymentMethod}
          className="w-full"
        >
          <CheckCircle className="w-4 h-4 mr-2" />
          Process Payment (₹{total})
        </Button>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert type="danger" title="Error">
          {error}
        </Alert>
      )}
    </div>
  );
};

export default POSTerminal;
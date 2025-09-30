import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { paymentService } from '../../services/paymentService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { CreditCard, DollarSign, Smartphone, Building2, Wallet, RefreshCw, Plus, BarChart3, Settings } from 'lucide-react';

const PaymentModes = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('cash');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      // Fetch payment modes data
    } catch (err) {
      addNotification({ type: 'danger', title: 'Error', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="flex items-center justify-center h-64"><LoadingSpinner size="lg" text="Loading payment modes..." /></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Payment Modes</h1>
          <p className="text-gray-600">Manage different payment methods and modes</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="outline" onClick={fetchData}><RefreshCw className="w-4 h-4 mr-2" />Refresh</Button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'cash', name: 'Cash Management', icon: DollarSign },
              { id: 'card', name: 'Card Payments', icon: CreditCard },
              { id: 'digital', name: 'Digital Payments', icon: Smartphone },
              { id: 'bank', name: 'Bank Transfers', icon: Building2 }
            ].map((tab) => (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`flex items-center space-x-2 py-4 border-b-2 ${activeTab === tab.id ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500'}`}>
                <tab.icon className="w-5 h-5" /><span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'cash' && (
            <div className="text-center py-12">
              <DollarSign className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Cash Management</h3>
              <p className="text-gray-500">Cash transaction handling will be implemented here</p>
            </div>
          )}

          {activeTab === 'card' && (
            <div className="text-center py-12">
              <CreditCard className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Card Payments</h3>
              <p className="text-gray-500">Credit/debit card processing will be implemented here</p>
            </div>
          )}

          {activeTab === 'digital' && (
            <div className="text-center py-12">
              <Smartphone className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Digital Payments</h3>
              <p className="text-gray-500">UPI, wallets, and online payments will be implemented here</p>
            </div>
          )}

          {activeTab === 'bank' && (
            <div className="text-center py-12">
              <Building2 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Bank Transfers</h3>
              <p className="text-gray-500">NEFT, RTGS, IMPS integration will be implemented here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PaymentModes;
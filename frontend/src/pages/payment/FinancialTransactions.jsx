import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { paymentService } from '../../services/paymentService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { Database, Plus, RefreshCw, FileText, BarChart3, Link2, Eye, Edit } from 'lucide-react';

const FinancialTransactions = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [transactions, setTransactions] = useState([]);
  const [activeTab, setActiveTab] = useState('transactions');

  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const data = await paymentService.getTransactions();
      setTransactions(data);
    } catch (err) {
      addNotification({ type: 'danger', title: 'Error', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="flex items-center justify-center h-64"><LoadingSpinner size="lg" text="Loading transactions..." /></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Financial Transactions</h1>
          <p className="text-gray-600">Manage financial transactions and matching</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="outline" onClick={fetchTransactions}><RefreshCw className="w-4 h-4 mr-2" />Refresh</Button>
          <Button><Plus className="w-4 h-4 mr-2" />Add Transaction</Button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'transactions', name: 'Transaction Recording', icon: Database },
              { id: 'matching', name: 'Transaction Matching', icon: Link2 },
              { id: 'reports', name: 'Transaction Reports', icon: FileText },
              { id: 'analytics', name: 'Transaction Analytics', icon: BarChart3 }
            ].map((tab) => (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`flex items-center space-x-2 py-4 border-b-2 ${activeTab === tab.id ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500'}`}>
                <tab.icon className="w-5 h-5" /><span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'transactions' && (
            <div className="text-center py-12">
              <Database className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Transaction Recording</h3>
              <p className="text-gray-500">Financial transaction logging will be implemented here</p>
            </div>
          )}

          {activeTab === 'matching' && (
            <div className="text-center py-12">
              <Link2 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Transaction Matching</h3>
              <p className="text-gray-500">Payment-invoice matching will be implemented here</p>
            </div>
          )}

          {activeTab === 'reports' && (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Transaction Reports</h3>
              <p className="text-gray-500">Financial transaction reports will be implemented here</p>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="text-center py-12">
              <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Transaction Analytics</h3>
              <p className="text-gray-500">Financial performance analysis will be implemented here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FinancialTransactions;
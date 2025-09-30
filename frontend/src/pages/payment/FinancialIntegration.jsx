import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { paymentService } from '../../services/paymentService';
import Button from '../../components/common/Button';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { Zap, Building2, CreditCard, FileText, Shield, RefreshCw, Settings, CheckCircle } from 'lucide-react';

const FinancialIntegration = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('banking');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      // Fetch integration data
    } catch (err) {
      addNotification({ type: 'danger', title: 'Error', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="flex items-center justify-center h-64"><LoadingSpinner size="lg" text="Loading integrations..." /></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Financial Integration</h1>
          <p className="text-gray-600">Manage banking APIs, payment gateways, and compliance</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="outline" onClick={fetchData}><RefreshCw className="w-4 h-4 mr-2" />Refresh</Button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'banking', name: 'Banking APIs', icon: Building2 },
              { id: 'gateways', name: 'Payment Gateways', icon: CreditCard },
              { id: 'reporting', name: 'Financial Reporting', icon: FileText },
              { id: 'compliance', name: 'Compliance Reporting', icon: Shield }
            ].map((tab) => (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`flex items-center space-x-2 py-4 border-b-2 ${activeTab === tab.id ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500'}`}>
                <tab.icon className="w-5 h-5" /><span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'banking' && (
            <div className="text-center py-12">
              <Building2 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Banking APIs</h3>
              <p className="text-gray-500">Bank API integration will be implemented here</p>
            </div>
          )}

          {activeTab === 'gateways' && (
            <div className="text-center py-12">
              <CreditCard className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Payment Gateways</h3>
              <p className="text-gray-500">Multiple gateway support will be implemented here</p>
            </div>
          )}

          {activeTab === 'reporting' && (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Financial Reporting</h3>
              <p className="text-gray-500">Comprehensive financial reports will be implemented here</p>
            </div>
          )}

          {activeTab === 'compliance' && (
            <div className="text-center py-12">
              <Shield className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Compliance Reporting</h3>
              <p className="text-gray-500">Regulatory compliance reports will be implemented here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FinancialIntegration;
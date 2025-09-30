import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { paymentService } from '../../services/paymentService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { CreditCard, Plus, Edit, Trash2, RefreshCw, Save, X, Eye, DollarSign, BarChart3, FileText, CheckCircle, Clock, AlertTriangle, Search, Filter, Download, Send } from 'lucide-react';

const PaymentManagement = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [payments, setPayments] = useState([]);
  const [filteredPayments, setFilteredPayments] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [activeTab, setActiveTab] = useState('payments');
  const [showAddPayment, setShowAddPayment] = useState(false);

  const paymentStatuses = [
    { value: 'pending', label: 'Pending', color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
    { value: 'completed', label: 'Completed', color: 'text-green-600', bgColor: 'bg-green-100' },
    { value: 'failed', label: 'Failed', color: 'text-red-600', bgColor: 'bg-red-100' },
    { value: 'refunded', label: 'Refunded', color: 'text-gray-600', bgColor: 'bg-gray-100' }
  ];

  useEffect(() => {
    fetchPayments();
  }, []);

  useEffect(() => {
    let filtered = payments;
    if (searchTerm) {
      filtered = filtered.filter(p => p.transaction_id?.toLowerCase().includes(searchTerm.toLowerCase()) || p.customer_name?.toLowerCase().includes(searchTerm.toLowerCase()));
    }
    if (statusFilter !== 'all') {
      filtered = filtered.filter(p => p.status === statusFilter);
    }
    setFilteredPayments(filtered);
  }, [payments, searchTerm, statusFilter]);

  const fetchPayments = async () => {
    try {
      setLoading(true);
      const data = await paymentService.getPayments();
      setPayments(data);
      setFilteredPayments(data);
    } catch (err) {
      addNotification({ type: 'danger', title: 'Error', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(amount);
  const formatDate = (dateString) => new Date(dateString).toLocaleDateString();
  const getStatusInfo = (status) => paymentStatuses.find(s => s.value === status) || paymentStatuses[0];

  if (loading) return <div className="flex items-center justify-center h-64"><LoadingSpinner size="lg" text="Loading payments..." /></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Payment Management</h1>
          <p className="text-gray-600">Manage payments and financial transactions</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="outline" onClick={fetchPayments}><RefreshCw className="w-4 h-4 mr-2" />Refresh</Button>
          <Button onClick={() => setShowAddPayment(true)}><Plus className="w-4 h-4 mr-2" />Add Payment</Button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'payments', name: 'Payment Processing', icon: CreditCard },
              { id: 'reconciliation', name: 'Reconciliation', icon: CheckCircle },
              { id: 'reports', name: 'Reports', icon: FileText },
              { id: 'analytics', name: 'Analytics', icon: BarChart3 }
            ].map((tab) => (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`flex items-center space-x-2 py-4 border-b-2 ${activeTab === tab.id ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500'}`}>
                <tab.icon className="w-5 h-5" /><span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'payments' && (
            <div className="space-y-6">
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Input placeholder="Search payments..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-full" />
                </div>
                <div className="w-48">
                  <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="form-input">
                    <option value="all">All Status</option>
                    {paymentStatuses.map(status => <option key={status.value} value={status.value}>{status.label}</option>)}
                  </select>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Transaction ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Method</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredPayments.map((payment) => {
                      const statusInfo = getStatusInfo(payment.status);
                      return (
                        <tr key={payment.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{payment.transaction_id}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{payment.customer_name}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatCurrency(payment.amount)}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{payment.payment_method}</td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>{statusInfo.label}</span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatDate(payment.created_at)}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <div className="flex items-center space-x-2">
                              <Button size="sm" variant="outline"><Eye className="w-4 h-4" /></Button>
                              <Button size="sm" variant="outline"><Edit className="w-4 h-4" /></Button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'reconciliation' && (
            <div className="text-center py-12">
              <CheckCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Payment Reconciliation</h3>
              <p className="text-gray-500">Payment matching and reconciliation will be implemented here</p>
            </div>
          )}

          {activeTab === 'reports' && (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Payment Reports</h3>
              <p className="text-gray-500">Payment transaction reports will be implemented here</p>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="text-center py-12">
              <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Payment Analytics</h3>
              <p className="text-gray-500">Payment performance analysis will be implemented here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PaymentManagement;
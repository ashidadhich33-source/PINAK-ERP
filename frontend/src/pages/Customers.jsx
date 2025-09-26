import { useState, useEffect } from 'react'
import api from '../services/api'

const Customers = () => {
  const [customers, setCustomers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)
  const [newCustomer, setNewCustomer] = useState({
    name: '',
    phone: '',
    email: '',
    address: ''
  })

  useEffect(() => {
    fetchCustomers()
  }, [])

  const fetchCustomers = async () => {
    try {
      setLoading(true)
      // Mock data for now - replace with actual API call
      const mockCustomers = [
        {
          id: 1,
          name: 'John Doe',
          phone: '+91 9876543210',
          email: 'john@example.com',
          address: '123 Main St, Mumbai',
          totalPurchases: 5,
          totalSpent: 2500,
          lastPurchase: '2024-01-15'
        },
        {
          id: 2,
          name: 'Jane Smith',
          phone: '+91 9876543211',
          email: 'jane@example.com',
          address: '456 Oak Ave, Delhi',
          totalPurchases: 3,
          totalSpent: 1800,
          lastPurchase: '2024-01-10'
        },
        {
          id: 3,
          name: 'Bob Johnson',
          phone: '+91 9876543212',
          email: 'bob@example.com',
          address: '789 Pine Rd, Bangalore',
          totalPurchases: 8,
          totalSpent: 4200,
          lastPurchase: '2024-01-20'
        },
        {
          id: 4,
          name: 'Alice Brown',
          phone: '+91 9876543213',
          email: 'alice@example.com',
          address: '321 Elm St, Chennai',
          totalPurchases: 2,
          totalSpent: 900,
          lastPurchase: '2024-01-05'
        },
      ]
      setCustomers(mockCustomers)
    } catch (err) {
      setError('Failed to fetch customers')
      console.error('Customers error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddCustomer = async () => {
    if (!newCustomer.name || !newCustomer.phone) return

    try {
      const customerToAdd = {
        ...newCustomer,
        id: Date.now(),
        totalPurchases: 0,
        totalSpent: 0,
        lastPurchase: null
      }

      setCustomers([...customers, customerToAdd])
      setNewCustomer({ name: '', phone: '', email: '', address: '' })
      setShowAddModal(false)
    } catch (err) {
      setError('Failed to add customer')
      console.error('Add customer error:', err)
    }
  }

  const handleDeleteCustomer = async (id) => {
    if (window.confirm('Are you sure you want to delete this customer?')) {
      try {
        setCustomers(customers.filter(customer => customer.id !== id))
      } catch (err) {
        setError('Failed to delete customer')
        console.error('Delete customer error:', err)
      }
    }
  }

  const filteredCustomers = customers.filter(customer =>
    customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.phone.includes(searchTerm) ||
    customer.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount)
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Never'
    return new Date(dateString).toLocaleDateString('en-IN')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Customers</h1>
          <p className="text-gray-600">Manage your customer database</p>
        </div>
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
          onClick={() => setShowAddModal(true)}
        >
          Add New Customer
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Search */}
      <div className="bg-white shadow rounded-lg p-6">
        <input
          type="text"
          placeholder="Search customers by name, phone, or email..."
          className="w-full px-4 py-3 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Customers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCustomers.map((customer) => (
          <div key={customer.id} className="bg-white shadow rounded-lg p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium text-lg">
                {customer.name.charAt(0).toUpperCase()}
              </div>
              <button
                className="text-red-500 hover:text-red-700 text-sm"
                onClick={() => handleDeleteCustomer(customer.id)}
              >
                Delete
              </button>
            </div>

            <h3 className="text-lg font-medium text-gray-900 mb-2">{customer.name}</h3>

            <div className="space-y-2 text-sm text-gray-600 mb-4">
              <div className="flex items-center">
                <span className="font-medium mr-2">📞</span>
                <span>{customer.phone}</span>
              </div>
              <div className="flex items-center">
                <span className="font-medium mr-2">✉️</span>
                <span>{customer.email}</span>
              </div>
              <div className="flex items-center">
                <span className="font-medium mr-2">🏠</span>
                <span>{customer.address}</span>
              </div>
            </div>

            <div className="border-t pt-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Total Purchases:</span>
                  <div className="font-medium">{customer.totalPurchases}</div>
                </div>
                <div>
                  <span className="text-gray-500">Total Spent:</span>
                  <div className="font-medium">{formatCurrency(customer.totalSpent)}</div>
                </div>
              </div>
              <div className="mt-2 text-sm">
                <span className="text-gray-500">Last Purchase:</span>
                <div className="font-medium">{formatDate(customer.lastPurchase)}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredCustomers.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No customers found</p>
        </div>
      )}

      {/* Add Customer Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Customer</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Name *</label>
                <input
                  type="text"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  value={newCustomer.name}
                  onChange={(e) => setNewCustomer({ ...newCustomer, name: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Phone *</label>
                <input
                  type="tel"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  value={newCustomer.phone}
                  onChange={(e) => setNewCustomer({ ...newCustomer, phone: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  value={newCustomer.email}
                  onChange={(e) => setNewCustomer({ ...newCustomer, email: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Address</label>
                <textarea
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  rows="3"
                  value={newCustomer.address}
                  onChange={(e) => setNewCustomer({ ...newCustomer, address: e.target.value })}
                />
              </div>
            </div>
            <div className="mt-6 flex justify-end space-x-3">
              <button
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                onClick={() => setShowAddModal(false)}
              >
                Cancel
              </button>
              <button
                className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700"
                onClick={handleAddCustomer}
              >
                Add Customer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Customers
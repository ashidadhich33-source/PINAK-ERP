import { useState, useEffect } from 'react'
import api from '../services/api'

const Reports = () => {
  const [reports, setReports] = useState({
    salesByDate: [],
    topProducts: [],
    salesByCategory: [],
    monthlyRevenue: []
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [dateRange, setDateRange] = useState({
    from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    to: new Date().toISOString().split('T')[0]
  })

  useEffect(() => {
    fetchReports()
  }, [dateRange])

  const fetchReports = async () => {
    try {
      setLoading(true)
      // Mock data for now - replace with actual API calls
      const mockReports = {
        salesByDate: [
          { date: '2024-01-15', sales: 2500, transactions: 12 },
          { date: '2024-01-16', sales: 3200, transactions: 15 },
          { date: '2024-01-17', sales: 1800, transactions: 8 },
          { date: '2024-01-18', sales: 4100, transactions: 20 },
          { date: '2024-01-19', sales: 2900, transactions: 14 },
        ],
        topProducts: [
          { name: 'Product A', sold: 45, revenue: 4500 },
          { name: 'Product B', sold: 32, revenue: 4800 },
          { name: 'Product C', sold: 28, revenue: 5600 },
          { name: 'Product D', sold: 25, revenue: 1875 },
          { name: 'Product E', sold: 18, revenue: 5400 },
        ],
        salesByCategory: [
          { category: 'Electronics', sales: 12500, percentage: 35 },
          { category: 'Clothing', sales: 8900, percentage: 25 },
          { category: 'Home', sales: 6700, percentage: 19 },
          { category: 'Food', sales: 5600, percentage: 16 },
          { category: 'Other', sales: 1800, percentage: 5 },
        ],
        monthlyRevenue: [
          { month: 'Aug', revenue: 25000 },
          { month: 'Sep', revenue: 28000 },
          { month: 'Oct', revenue: 32000 },
          { month: 'Nov', revenue: 35000 },
          { month: 'Dec', revenue: 42000 },
          { month: 'Jan', revenue: 38000 },
        ]
      }
      setReports(mockReports)
    } catch (err) {
      setError('Failed to fetch reports')
      console.error('Reports error:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount)
  }

  const formatDate = (dateString) => {
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
          <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
          <p className="text-gray-600">View sales analytics and business insights</p>
        </div>
        <div className="flex space-x-4">
          <input
            type="date"
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={dateRange.from}
            onChange={(e) => setDateRange({ ...dateRange, from: e.target.value })}
          />
          <input
            type="date"
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={dateRange.to}
            onChange={(e) => setDateRange({ ...dateRange, to: e.target.value })}
          />
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center">
              <span className="text-white text-xl">💰</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Revenue</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(reports.salesByDate.reduce((sum, day) => sum + day.sales, 0))}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center">
              <span className="text-white text-xl">🛒</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Transactions</p>
              <p className="text-2xl font-bold text-gray-900">
                {reports.salesByDate.reduce((sum, day) => sum + day.transactions, 0)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center">
              <span className="text-white text-xl">📦</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Items Sold</p>
              <p className="text-2xl font-bold text-gray-900">
                {reports.topProducts.reduce((sum, product) => sum + product.sold, 0)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-yellow-500 rounded-lg flex items-center justify-center">
              <span className="text-white text-xl">📊</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg per Transaction</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(
                  reports.salesByDate.reduce((sum, day) => sum + day.sales, 0) /
                  Math.max(reports.salesByDate.reduce((sum, day) => sum + day.transactions, 0), 1)
                )}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sales by Date */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Daily Sales</h3>
          <div className="space-y-3">
            {reports.salesByDate.map((day, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-20 text-sm text-gray-600">{formatDate(day.date)}</div>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{
                        width: `${(day.sales / Math.max(...reports.salesByDate.map(d => d.sales))) * 100}%`
                      }}
                    ></div>
                  </div>
                </div>
                <div className="text-sm font-medium text-gray-900">
                  {formatCurrency(day.sales)}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Products */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top Products</h3>
          <div className="space-y-3">
            {reports.topProducts.map((product, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-xs font-medium text-blue-600">
                    {index + 1}
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-900">{product.name}</div>
                    <div className="text-xs text-gray-500">{product.sold} sold</div>
                  </div>
                </div>
                <div className="text-sm font-medium text-gray-900">
                  {formatCurrency(product.revenue)}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Sales by Category */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Sales by Category</h3>
          <div className="space-y-3">
            {reports.salesByCategory.map((category, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <div>
                    <div className="text-sm font-medium text-gray-900">{category.category}</div>
                    <div className="text-xs text-gray-500">{category.percentage}% of total</div>
                  </div>
                </div>
                <div className="text-sm font-medium text-gray-900">
                  {formatCurrency(category.sales)}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Monthly Revenue */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Monthly Revenue Trend</h3>
          <div className="space-y-3">
            {reports.monthlyRevenue.map((month, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-16 text-sm font-medium text-gray-900">{month.month}</div>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{
                        width: `${(month.revenue / Math.max(...reports.monthlyRevenue.map(m => m.revenue))) * 100}%`
                      }}
                    ></div>
                  </div>
                </div>
                <div className="text-sm font-medium text-gray-900">
                  {formatCurrency(month.revenue)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Reports
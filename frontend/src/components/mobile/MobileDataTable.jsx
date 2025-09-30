import React, { useState, useEffect } from 'react';
import { 
  ChevronLeft, 
  ChevronRight, 
  Search, 
  Filter, 
  SortAsc, 
  SortDesc,
  MoreVertical,
  Eye,
  Edit,
  Trash2,
  Download,
  Share
} from 'lucide-react';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';

const MobileDataTable = ({
  data = [],
  columns = [],
  loading = false,
  onRowClick,
  onEdit,
  onDelete,
  onExport,
  onShare,
  searchable = true,
  sortable = true,
  filterable = true,
  pagination = true,
  pageSize = 10,
  className = ''
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortColumn, setSortColumn] = useState('');
  const [sortDirection, setSortDirection] = useState('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedRows, setSelectedRows] = useState([]);
  const [showActions, setShowActions] = useState(null);

  // Filter and sort data
  const filteredData = data.filter(item => {
    if (!searchTerm) return true;
    return columns.some(column => {
      const value = item[column.key];
      return value && value.toString().toLowerCase().includes(searchTerm.toLowerCase());
    });
  });

  const sortedData = [...filteredData].sort((a, b) => {
    if (!sortColumn) return 0;
    
    const aValue = a[sortColumn];
    const bValue = b[sortColumn];
    
    if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

  // Pagination
  const totalPages = Math.ceil(sortedData.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const paginatedData = sortedData.slice(startIndex, endIndex);

  const handleSort = (columnKey) => {
    if (sortColumn === columnKey) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(columnKey);
      setSortDirection('asc');
    }
  };

  const handleRowClick = (item) => {
    onRowClick?.(item);
  };

  const handleRowLongPress = (item) => {
    setShowActions(item.id);
  };

  const handleSelectRow = (itemId) => {
    setSelectedRows(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const handleSelectAll = () => {
    if (selectedRows.length === paginatedData.length) {
      setSelectedRows([]);
    } else {
      setSelectedRows(paginatedData.map(item => item.id));
    }
  };

  const handleAction = (action, item) => {
    setShowActions(null);
    
    switch (action) {
      case 'edit':
        onEdit?.(item);
        break;
      case 'delete':
        onDelete?.(item);
        break;
      case 'export':
        onExport?.(item);
        break;
      case 'share':
        onShare?.(item);
        break;
      default:
        break;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading data..." />
      </div>
    );
  }

  return (
    <div className={`mobile-data-table ${className}`}>
      {/* Mobile Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            {data.length} items
          </h3>
          <div className="flex items-center space-x-2">
            {filterable && (
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
              >
                <Filter className="w-5 h-5" />
              </button>
            )}
            {onExport && (
              <button
                onClick={() => onExport(selectedRows)}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
              >
                <Download className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>

        {/* Search */}
        {searchable && (
          <div className="relative">
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 pl-10 pr-4 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          </div>
        )}

        {/* Filters */}
        {showFilters && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <div className="grid grid-cols-2 gap-4">
              {columns.filter(col => col.filterable).map((column) => (
                <div key={column.key}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {column.label}
                  </label>
                  <select className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500">
                    <option value="">All</option>
                    {/* Add filter options here */}
                  </select>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Mobile Data Cards */}
      <div className="space-y-2 p-4">
        {paginatedData.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No data found</p>
            {searchTerm && (
              <p className="text-sm">Try adjusting your search</p>
            )}
          </div>
        ) : (
          paginatedData.map((item, index) => (
            <div
              key={item.id || index}
              className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {/* Primary Information */}
                  <div className="flex items-center space-x-3 mb-2">
                    <input
                      type="checkbox"
                      checked={selectedRows.includes(item.id)}
                      onChange={() => handleSelectRow(item.id)}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">
                        {item[columns[0]?.key] || 'No title'}
                      </h4>
                      {columns[1] && (
                        <p className="text-sm text-gray-600">
                          {item[columns[1].key] || ''}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Additional Information */}
                  <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                    {columns.slice(2, 4).map((column) => (
                      <div key={column.key}>
                        <span className="font-medium">{column.label}:</span>
                        <span className="ml-1">{item[column.key] || '-'}</span>
                      </div>
                    ))}
                  </div>

                  {/* Status or Tags */}
                  {item.status && (
                    <div className="mt-2">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        item.status === 'active' ? 'bg-success-100 text-success-800' :
                        item.status === 'inactive' ? 'bg-gray-100 text-gray-800' :
                        item.status === 'pending' ? 'bg-warning-100 text-warning-800' :
                        'bg-danger-100 text-danger-800'
                      }`}>
                        {item.status}
                      </span>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleRowClick(item)}
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  
                  <button
                    onClick={() => setShowActions(item.id)}
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md"
                  >
                    <MoreVertical className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Action Menu */}
              {showActions === item.id && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <div className="flex items-center space-x-2">
                    {onEdit && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleAction('edit', item)}
                        className="flex items-center space-x-1"
                      >
                        <Edit className="w-4 h-4" />
                        <span>Edit</span>
                      </Button>
                    )}
                    
                    {onDelete && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleAction('delete', item)}
                        className="flex items-center space-x-1 text-danger-600 hover:text-danger-900"
                      >
                        <Trash2 className="w-4 h-4" />
                        <span>Delete</span>
                      </Button>
                    )}
                    
                    {onShare && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleAction('share', item)}
                        className="flex items-center space-x-1"
                      >
                        <Share className="w-4 h-4" />
                        <span>Share</span>
                      </Button>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Mobile Pagination */}
      {pagination && totalPages > 1 && (
        <div className="bg-white border-t border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              Showing {startIndex + 1} to {Math.min(endIndex, sortedData.length)} of {sortedData.length} results
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="p-2 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              
              <span className="text-sm text-gray-600">
                {currentPage} of {totalPages}
              </span>
              
              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="p-2 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Selected Items Actions */}
      {selectedRows.length > 0 && (
        <div className="fixed bottom-20 left-0 right-0 z-30 bg-white border-t border-gray-200 p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">
              {selectedRows.length} item{selectedRows.length > 1 ? 's' : ''} selected
            </span>
            <div className="flex items-center space-x-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => setSelectedRows([])}
              >
                Clear
              </Button>
              {onExport && (
                <Button
                  size="sm"
                  onClick={() => onExport(selectedRows)}
                  className="flex items-center space-x-1"
                >
                  <Download className="w-4 h-4" />
                  <span>Export</span>
                </Button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MobileDataTable;
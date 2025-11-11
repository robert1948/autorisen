/**
 * Invoice History Dashboard Component
 * Comprehensive invoice management with filtering, pagination, and export capabilities
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useInvoices } from '../../context/PaymentStateContext';
import { PaymentErrorBoundary } from './PaymentErrorBoundary';
import type { 
  Invoice, 
  InvoiceFilters, 
  InvoiceHistoryProps 
} from '../../types/payments';

interface InvoiceHistoryState {
  selectedInvoices: Set<string>;
  sortField: keyof Invoice;
  sortDirection: 'asc' | 'desc';
  viewMode: 'table' | 'cards';
  exportLoading: boolean;
}

const INITIAL_STATE: InvoiceHistoryState = {
  selectedInvoices: new Set(),
  sortField: 'createdAt',
  sortDirection: 'desc',
  viewMode: 'table',
  exportLoading: false,
};

const INVOICE_STATUSES = [
  { value: 'pending', label: 'Pending', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'paid', label: 'Paid', color: 'bg-green-100 text-green-800' },
  { value: 'failed', label: 'Failed', color: 'bg-red-100 text-red-800' },
  { value: 'cancelled', label: 'Cancelled', color: 'bg-gray-100 text-gray-800' },
] as const;

const DATE_RANGES = [
  { value: 'all', label: 'All Time' },
  { value: '7d', label: 'Last 7 Days' },
  { value: '30d', label: 'Last 30 Days' },
  { value: '90d', label: 'Last 3 Months' },
  { value: 'custom', label: 'Custom Range' },
] as const;

export default function InvoiceHistory({ className }: { className?: string }) {
  const {
    invoices,
    loading: invoicesLoading,
    error: invoicesError,
    pagination: invoicesPagination,
    filters: invoiceFilters,
    loadInvoices,
    loadMoreInvoices,
    updateInvoiceFilters,
  } = useInvoices();

  const [state, setState] = useState<InvoiceHistoryState>(INITIAL_STATE);
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  // Load initial data
  useEffect(() => {
    loadInvoices();
  }, [loadInvoices]);

  // Filtered and sorted invoices
  const processedInvoices = useMemo(() => {
    let filtered = invoices;

    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(invoice => 
        invoice.id.toLowerCase().includes(term) ||
        invoice.itemName?.toLowerCase().includes(term) ||
        invoice.customerEmail?.toLowerCase().includes(term) ||
        invoice.amount.toString().includes(term)
      );
    }

    // Sort invoices
    const sorted = [...filtered].sort((a, b) => {
      const aValue = a[state.sortField];
      const bValue = b[state.sortField];
      
      let comparison = 0;
      if (aValue != null && bValue != null) {
        if (aValue < bValue) comparison = -1;
        if (aValue > bValue) comparison = 1;
      }
      
      return state.sortDirection === 'desc' ? -comparison : comparison;
    });

    return sorted;
  }, [invoices, searchTerm, state.sortField, state.sortDirection]);

  // Handle sort change
  const handleSort = useCallback((field: keyof Invoice) => {
    setState(prev => ({
      ...prev,
      sortField: field,
      sortDirection: prev.sortField === field && prev.sortDirection === 'asc' ? 'desc' : 'asc',
    }));
  }, []);

  // Handle filter updates
  const handleFilterChange = useCallback((newFilters: Partial<InvoiceFilters>) => {
    updateInvoiceFilters(newFilters);
  }, [updateInvoiceFilters]);

  // Handle invoice selection
  const handleInvoiceSelection = useCallback((invoiceId: string, selected: boolean) => {
    setState(prev => {
      const newSelected = new Set(prev.selectedInvoices);
      if (selected) {
        newSelected.add(invoiceId);
      } else {
        newSelected.delete(invoiceId);
      }
      return { ...prev, selectedInvoices: newSelected };
    });
  }, []);

  // Handle bulk selection
  const handleBulkSelection = useCallback((selected: boolean) => {
    setState(prev => ({
      ...prev,
      selectedInvoices: selected ? new Set(processedInvoices.map(i => i.id)) : new Set(),
    }));
  }, [processedInvoices]);

  // Handle export
  const handleExport = useCallback(async (format: 'csv' | 'pdf') => {
    setState(prev => ({ ...prev, exportLoading: true }));
    
    try {
      const selectedIds = Array.from(state.selectedInvoices);
      const invoicesToExport = selectedIds.length > 0 
        ? processedInvoices.filter(inv => selectedIds.includes(inv.id))
        : processedInvoices;
      
      // Mock export functionality
      const filename = `invoices-${new Date().toISOString().split('T')[0]}.${format}`;
      
      if (format === 'csv') {
        const headers = ['ID', 'Date', 'Amount', 'Status', 'Customer', 'Item'];
        const rows = invoicesToExport.map(inv => [
          inv.id,
          new Date(inv.createdAt).toLocaleDateString(),
          `R${inv.amount.toFixed(2)}`,
          inv.status,
          inv.customerEmail || '',
          inv.itemName || '',
        ]);
        
        const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
      
      console.log(`Exported ${invoicesToExport.length} invoices as ${format}`);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setState(prev => ({ ...prev, exportLoading: false }));
    }
  }, [state.selectedInvoices, processedInvoices]);

  // Format currency
  const formatCurrency = (amount: number) => `R${amount.toFixed(2)}`;

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-ZA', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Get status badge
  const getStatusBadge = (status: Invoice['status']) => {
    const statusConfig = INVOICE_STATUSES.find(s => s.value === status);
    if (!statusConfig) return null;
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusConfig.color}`}>
        {statusConfig.label}
      </span>
    );
  };

  if (invoicesError) {
    return (
      <div className={`invoice-history ${className || ''}`}>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <h3 className="text-lg font-medium text-red-900 mb-2">Unable to Load Invoices</h3>
          <p className="text-red-700 mb-4">{invoicesError}</p>
          <button
            onClick={() => loadInvoices()}
            className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <PaymentErrorBoundary>
      <div className={`invoice-history ${className || ''}`}>
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Invoice History</h2>
              <p className="text-gray-600 mt-1">
                {invoicesPagination.total} invoices • {state.selectedInvoices.size} selected
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              {/* View Mode Toggle */}
              <div className="flex items-center bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setState(prev => ({ ...prev, viewMode: 'table' }))}
                  className={`px-3 py-1 text-sm rounded ${
                    state.viewMode === 'table' 
                      ? 'bg-white text-gray-900 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Table
                </button>
                <button
                  onClick={() => setState(prev => ({ ...prev, viewMode: 'cards' }))}
                  className={`px-3 py-1 text-sm rounded ${
                    state.viewMode === 'cards' 
                      ? 'bg-white text-gray-900 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Cards
                </button>
              </div>

              {/* Export Dropdown */}
              <div className="relative">
                <button
                  disabled={state.exportLoading}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
                >
                  {state.exportLoading ? (
                    <>
                      <svg className="w-4 h-4 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Exporting...
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      Export
                    </>
                  )}
                </button>
              </div>

              <button
                onClick={() => loadInvoices()}
                className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 flex items-center"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Refresh
              </button>
            </div>
          </div>

          {/* Search and Filters */}
          <div className="flex items-center space-x-4">
            <div className="flex-1 max-w-md">
              <div className="relative">
                <svg className="w-4 h-4 absolute left-3 top-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input
                  type="text"
                  placeholder="Search invoices..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`px-4 py-2 rounded-lg border transition-colors ${
                showFilters || Object.keys(invoiceFilters).length > 0
                  ? 'border-blue-300 bg-blue-50 text-blue-700'
                  : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <svg className="w-4 h-4 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.414A1 1 0 013 6.707V4z" />
              </svg>
              Filters
            </button>
          </div>

          {/* Filter Panel */}
          {showFilters && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg border">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Status Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                  <select
                    value={invoiceFilters.status?.[0] || ''}
                    onChange={(e) => handleFilterChange({ 
                      status: e.target.value ? [e.target.value as Invoice['status']] : undefined 
                    })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value="">All Statuses</option>
                    {INVOICE_STATUSES.map(status => (
                      <option key={status.value} value={status.value}>
                        {status.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Date Range */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
                  <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                    {DATE_RANGES.map(range => (
                      <option key={range.value} value={range.value}>
                        {range.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Amount Range */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Amount Range</label>
                  <div className="flex space-x-2">
                    <input
                      type="number"
                      placeholder="Min"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    />
                    <input
                      type="number"
                      placeholder="Max"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end mt-4 space-x-2">
                <button
                  onClick={() => {
                    handleFilterChange({});
                    setSearchTerm('');
                  }}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800"
                >
                  Clear All
                </button>
                <button
                  onClick={() => setShowFilters(false)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                  Apply Filters
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Loading State */}
        {invoicesLoading && processedInvoices.length === 0 && (
          <div className="text-center py-12">
            <svg className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <p className="text-gray-600">Loading invoices...</p>
          </div>
        )}

        {/* Empty State */}
        {!invoicesLoading && processedInvoices.length === 0 && (
          <div className="text-center py-12">
            <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No invoices found</h3>
            <p className="text-gray-600 mb-6">
              {searchTerm || Object.keys(invoiceFilters).length > 0
                ? 'Try adjusting your search or filters.'
                : 'Your invoices will appear here as you make payments.'}
            </p>
          </div>
        )}

        {/* Table View */}
        {state.viewMode === 'table' && processedInvoices.length > 0 && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left">
                      <input
                        type="checkbox"
                        checked={processedInvoices.length > 0 && state.selectedInvoices.size === processedInvoices.length}
                        onChange={(e) => handleBulkSelection(e.target.checked)}
                        className="rounded border-gray-300"
                      />
                    </th>
                    {[
                      { key: 'id', label: 'Invoice ID' },
                      { key: 'createdAt', label: 'Date' },
                      { key: 'amount', label: 'Amount' },
                      { key: 'status', label: 'Status' },
                      { key: 'customerEmail', label: 'Customer' },
                      { key: 'itemName', label: 'Item' },
                    ].map(({ key, label }) => (
                      <th key={key} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        <button
                          onClick={() => handleSort(key as keyof Invoice)}
                          className="flex items-center hover:text-gray-700"
                        >
                          {label}
                          {state.sortField === key && (
                            <svg 
                              className={`ml-1 w-4 h-4 ${state.sortDirection === 'desc' ? 'rotate-180' : ''}`} 
                              fill="none" stroke="currentColor" viewBox="0 0 24 24"
                            >
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                            </svg>
                          )}
                        </button>
                      </th>
                    ))}
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {processedInvoices.map((invoice) => (
                    <tr key={invoice.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <input
                          type="checkbox"
                          checked={state.selectedInvoices.has(invoice.id)}
                          onChange={(e) => handleInvoiceSelection(invoice.id, e.target.checked)}
                          className="rounded border-gray-300"
                        />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {invoice.id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(invoice.createdAt)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {formatCurrency(invoice.amount)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(invoice.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {invoice.customerEmail || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {invoice.itemName || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button className="text-blue-600 hover:text-blue-900 mr-3">
                          View
                        </button>
                        <button className="text-gray-600 hover:text-gray-900">
                          Download
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Cards View */}
        {state.viewMode === 'cards' && processedInvoices.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {processedInvoices.map((invoice) => (
              <div key={invoice.id} className="bg-white rounded-lg shadow border hover:shadow-md transition-shadow">
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{invoice.id}</h3>
                      <p className="text-sm text-gray-500">{formatDate(invoice.createdAt)}</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={state.selectedInvoices.has(invoice.id)}
                      onChange={(e) => handleInvoiceSelection(invoice.id, e.target.checked)}
                      className="rounded border-gray-300"
                    />
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Amount:</span>
                      <span className="text-sm font-medium">{formatCurrency(invoice.amount)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Status:</span>
                      {getStatusBadge(invoice.status)}
                    </div>
                    {invoice.customerEmail && (
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Customer:</span>
                        <span className="text-sm text-gray-900 truncate ml-2">{invoice.customerEmail}</span>
                      </div>
                    )}
                    {invoice.itemName && (
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Item:</span>
                        <span className="text-sm text-gray-900 truncate ml-2">{invoice.itemName}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex space-x-2">
                    <button className="flex-1 bg-blue-600 text-white py-2 px-3 rounded text-sm hover:bg-blue-700">
                      View Details
                    </button>
                    <button className="bg-gray-100 text-gray-700 py-2 px-3 rounded text-sm hover:bg-gray-200">
                      Download
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {processedInvoices.length > 0 && (
          <div className="mt-6 flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing {Math.min(Math.floor(invoicesPagination.offset / invoicesPagination.limit) + 1, Math.ceil(invoicesPagination.total / invoicesPagination.limit))} of{' '}
              {Math.ceil(invoicesPagination.total / invoicesPagination.limit)} pages ({invoicesPagination.total} total invoices)
            </div>
            
            {invoicesPagination.hasNext && (
              <button
                onClick={loadMoreInvoices}
                disabled={invoicesLoading}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {invoicesLoading ? 'Loading...' : 'Load More'}
              </button>
            )}
          </div>
        )}

        {/* Export Action Sheet */}
        {state.selectedInvoices.size > 0 && (
          <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-white rounded-lg shadow-lg border p-4">
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                {state.selectedInvoices.size} invoice{state.selectedInvoices.size !== 1 ? 's' : ''} selected
              </span>
              <button
                onClick={() => handleExport('csv')}
                disabled={state.exportLoading}
                className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
              >
                Export CSV
              </button>
              <button
                onClick={() => handleExport('pdf')}
                disabled={state.exportLoading}
                className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 disabled:opacity-50"
              >
                Export PDF
              </button>
              <button
                onClick={() => setState(prev => ({ ...prev, selectedInvoices: new Set() }))}
                className="text-gray-600 hover:text-gray-800 text-sm"
              >
                Clear
              </button>
            </div>
          </div>
        )}
      </div>
    </PaymentErrorBoundary>
  );
}
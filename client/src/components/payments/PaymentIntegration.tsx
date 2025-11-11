/**
 * Payment Integration Utilities
 * Helper functions and components for integrating payments into the main dashboard
 */

import React from 'react';
import { Link } from 'react-router-dom';
import type { Invoice, PaymentMethod, Transaction } from '../../types/payments';

// Dashboard payment summary widget
export interface PaymentDashboardSummaryProps {
  className?: string;
}

export function PaymentDashboardSummary({ className }: PaymentDashboardSummaryProps) {
  // Mock data - will be replaced with real data from hooks
  const summaryData = {
    totalSpent: 450.00,
    activeSubscriptions: 2,
    pendingPayments: 1,
    lastPayment: '2 days ago',
  };

  return (
    <div className={`payment-dashboard-summary ${className || ''}`}>
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Payment Summary</h3>
          <Link 
            to="/billing" 
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            View All
          </Link>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-3 bg-gray-50 rounded">
            <div className="text-2xl font-bold text-gray-900">
              R{summaryData.totalSpent.toFixed(2)}
            </div>
            <div className="text-sm text-gray-500">Total Spent</div>
          </div>
          
          <div className="text-center p-3 bg-gray-50 rounded">
            <div className="text-2xl font-bold text-green-600">
              {summaryData.activeSubscriptions}
            </div>
            <div className="text-sm text-gray-500">Active Plans</div>
          </div>
          
          <div className="text-center p-3 bg-gray-50 rounded">
            <div className="text-2xl font-bold text-yellow-600">
              {summaryData.pendingPayments}
            </div>
            <div className="text-sm text-gray-500">Pending</div>
          </div>
          
          <div className="text-center p-3 bg-gray-50 rounded">
            <div className="text-sm font-medium text-gray-900">
              {summaryData.lastPayment}
            </div>
            <div className="text-sm text-gray-500">Last Payment</div>
          </div>
        </div>
        
        <div className="mt-4 pt-4 border-t border-gray-200">
          <Link
            to="/checkout"
            className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
          >
            Make Payment
          </Link>
        </div>
      </div>
    </div>
  );
}

// Quick payment action button
export interface QuickPaymentButtonProps {
  amount?: number;
  itemName?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'primary' | 'secondary' | 'outline';
  onClick?: () => void;
}

export function QuickPaymentButton({
  amount,
  itemName = 'CapeControl Service',
  className,
  size = 'md',
  variant = 'primary',
  onClick
}: QuickPaymentButtonProps) {
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  };
  
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 border-blue-600',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700 border-gray-600',
    outline: 'bg-white text-blue-600 hover:bg-blue-50 border-blue-600',
  };

  return (
    <button
      type="button"
      onClick={onClick}
      className={`
        inline-flex items-center border font-medium rounded-md transition-colors
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${className || ''}
      `}
    >
      <svg 
        className="w-4 h-4 mr-2" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          strokeWidth={2} 
          d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" 
        />
      </svg>
      {amount ? `Pay R${amount.toFixed(2)}` : 'Make Payment'}
    </button>
  );
}

// Payment status indicator
export interface PaymentStatusIndicatorProps {
  status: Invoice['status'];
  className?: string;
  showText?: boolean;
}

export function PaymentStatusIndicator({ 
  status, 
  className, 
  showText = true 
}: PaymentStatusIndicatorProps) {
  const statusConfig = {
    pending: {
      color: 'yellow',
      icon: 'clock',
      text: 'Pending',
    },
    paid: {
      color: 'green',
      icon: 'check',
      text: 'Paid',
    },
    failed: {
      color: 'red',
      icon: 'x',
      text: 'Failed',
    },
    cancelled: {
      color: 'gray',
      icon: 'ban',
      text: 'Cancelled',
    },
    refunded: {
      color: 'blue',
      icon: 'refresh',
      text: 'Refunded',
    },
  };
  
  const config = statusConfig[status];
  const colorClasses: Record<string, string> = {
    yellow: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    green: 'bg-green-100 text-green-800 border-green-200',
    red: 'bg-red-100 text-red-800 border-red-200',
    gray: 'bg-gray-100 text-gray-800 border-gray-200',
    blue: 'bg-blue-100 text-blue-800 border-blue-200',
  };

  return (
    <span
      className={`
        inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border
        ${colorClasses[config.color]}
        ${className || ''}
      `}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5" />
      {showText && config.text}
    </span>
  );
}

// Recent payments list widget
export interface RecentPaymentsWidgetProps {
  invoices?: Invoice[];
  limit?: number;
  className?: string;
}

export function RecentPaymentsWidget({ 
  invoices = [], 
  limit = 5, 
  className 
}: RecentPaymentsWidgetProps) {
  const recentInvoices = invoices.slice(0, limit);

  if (recentInvoices.length === 0) {
    return (
      <div className={`recent-payments-widget ${className || ''}`}>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Payments</h3>
          <div className="text-center py-8">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
            <p className="mt-2 text-sm text-gray-500">No payments yet</p>
            <Link 
              to="/checkout"
              className="mt-2 inline-flex items-center text-sm text-blue-600 hover:text-blue-700"
            >
              Make your first payment
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`recent-payments-widget ${className || ''}`}>
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Recent Payments</h3>
          <Link 
            to="/billing" 
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            View All
          </Link>
        </div>
        
        <div className="space-y-3">
          {recentInvoices.map((invoice) => (
            <div key={invoice.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50">
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{invoice.itemName}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(invoice.createdAt).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-gray-900">
                      R{invoice.amount.toFixed(2)}
                    </p>
                    <PaymentStatusIndicator status={invoice.status} />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {invoices.length > limit && (
          <div className="mt-4 pt-4 border-t border-gray-200 text-center">
            <Link
              to="/billing"
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              View {invoices.length - limit} more payments
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}

// Payment method selector
export interface PaymentMethodSelectorProps {
  methods: PaymentMethod[];
  selectedMethodId?: string;
  onSelect: (methodId: string) => void;
  onAddNew?: () => void;
  className?: string;
}

export function PaymentMethodSelector({
  methods,
  selectedMethodId,
  onSelect,
  onAddNew,
  className
}: PaymentMethodSelectorProps) {
  return (
    <div className={`payment-method-selector ${className || ''}`}>
      <div className="space-y-2">
        {methods.map((method) => (
          <label key={method.id} className="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
            <input
              type="radio"
              name="paymentMethod"
              value={method.id}
              checked={selectedMethodId === method.id}
              onChange={() => onSelect(method.id)}
              className="mr-3"
            />
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900 capitalize">
                    {method.methodType.replace('_', ' ')}
                  </p>
                  {method.lastFour && (
                    <p className="text-xs text-gray-500">•••• {method.lastFour}</p>
                  )}
                </div>
                {method.isDefault && (
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    Default
                  </span>
                )}
              </div>
            </div>
          </label>
        ))}
        
        {onAddNew && (
          <button
            type="button"
            onClick={onAddNew}
            className="w-full flex items-center justify-center p-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:text-gray-700 hover:border-gray-400"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Add New Payment Method
          </button>
        )}
      </div>
    </div>
  );
}

// Payment routing helper
export const paymentRoutes = {
  billing: '/billing',
  checkout: '/checkout',
  paymentMethods: '/billing/methods',
  invoices: '/billing/invoices',
  subscriptions: '/billing/subscriptions',
};

// Payment utility functions
export const paymentUtils = {
  formatCurrency: (amount: number, currency = 'ZAR'): string => {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
    }).format(amount);
  },
  
  formatDate: (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-ZA', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  },
  
  getStatusColor: (status: Invoice['status']): string => {
    const colors = {
      pending: 'yellow',
      paid: 'green',
      failed: 'red',
      cancelled: 'gray',
      refunded: 'blue',
    };
    return colors[status] || 'gray';
  },
  
  isOverdue: (invoice: Invoice): boolean => {
    if (invoice.status !== 'pending') return false;
    const createdDate = new Date(invoice.createdAt);
    const daysDiff = (Date.now() - createdDate.getTime()) / (1000 * 60 * 60 * 24);
    return daysDiff > 7; // Consider overdue after 7 days
  },
  
  calculateTotal: (invoices: Invoice[]): number => {
    return invoices.reduce((total, invoice) => {
      return invoice.status === 'paid' ? total + invoice.amount : total;
    }, 0);
  },
  
  filterInvoicesByStatus: (invoices: Invoice[], status: Invoice['status'][]): Invoice[] => {
    return invoices.filter(invoice => status.includes(invoice.status));
  },
  
  sortInvoicesByDate: (invoices: Invoice[], order: 'asc' | 'desc' = 'desc'): Invoice[] => {
    return [...invoices].sort((a, b) => {
      const dateA = new Date(a.createdAt).getTime();
      const dateB = new Date(b.createdAt).getTime();
      return order === 'desc' ? dateB - dateA : dateA - dateB;
    });
  },
};

// Integration hooks for dashboard
export function usePaymentIntegration() {
  // This would integrate with the payment state management
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  
  const navigateToCheckout = React.useCallback((params?: {
    amount?: number;
    itemName?: string;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.amount) searchParams.set('amount', params.amount.toString());
    if (params?.itemName) searchParams.set('item', params.itemName);
    
    const url = `/checkout${searchParams.toString() ? `?${searchParams.toString()}` : ''}`;
    window.location.href = url;
  }, []);
  
  const navigateToBilling = React.useCallback(() => {
    window.location.href = '/billing';
  }, []);
  
  return {
    isLoading,
    error,
    navigateToCheckout,
    navigateToBilling,
    paymentRoutes,
    paymentUtils,
  };
}
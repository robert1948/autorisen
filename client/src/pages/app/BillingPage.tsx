/**
 * Billing Page - Comprehensive Payment Management Dashboard
 * Integrates all payment components into a unified billing interface
 */

import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { PaymentStateProvider, usePaymentMethods, useInvoices, usePaymentUI } from '../../context/PaymentStateContext';
import { PaymentErrorBoundary } from '../../components/payments/PaymentErrorBoundary';
import { PaymentSecurityProvider, PaymentSecurityGuard } from '../../components/payments/PaymentSecurityProvider';
import { 
  PaymentDashboardSummary, 
  RecentPaymentsWidget, 
  PaymentStatusIndicator, 
  QuickPaymentButton,
  paymentUtils 
} from '../../components/payments/PaymentIntegration';
import PaymentMethodManager from '../../components/payments/PaymentMethodManager';
import InvoiceHistory from '../../components/payments/InvoiceHistory';
import type { PaymentMethod } from '../../types/payments';

// Tab navigation for billing sections
type BillingTab = 'overview' | 'methods' | 'invoices' | 'subscriptions';

function BillingPageCore() {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Determine active tab from URL
  const getActiveTab = (): BillingTab => {
    const path = location.pathname;
    if (path.includes('/methods')) return 'methods';
    if (path.includes('/invoices')) return 'invoices';
    if (path.includes('/subscriptions')) return 'subscriptions';
    return 'overview';
  };
  
  const [activeTab, setActiveTab] = useState<BillingTab>(getActiveTab());
  
  // Update tab when URL changes
  useEffect(() => {
    setActiveTab(getActiveTab());
  }, [location.pathname]);
  
  const handleTabChange = (tab: BillingTab) => {
    const routes = {
      overview: '/billing',
      methods: '/billing/methods',
      invoices: '/billing/invoices',
      subscriptions: '/billing/subscriptions',
    };
    navigate(routes[tab]);
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link 
                to="/app/dashboard" 
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">Billing & Payments</h1>
            </div>
            <QuickPaymentButton 
              onClick={() => navigate('/checkout')}
              variant="primary"
              size="md"
            />
          </div>
          
          {/* Tab Navigation */}
          <nav className="mt-6">
            <div className="border-b border-gray-200">
              <div className="flex space-x-8">
                {[
                  { key: 'overview', label: 'Overview', icon: '📊' },
                  { key: 'methods', label: 'Payment Methods', icon: '💳' },
                  { key: 'invoices', label: 'Invoices', icon: '📄' },
                  { key: 'subscriptions', label: 'Subscriptions', icon: '🔄' },
                ].map((tab) => (
                  <button
                    key={tab.key}
                    onClick={() => handleTabChange(tab.key as BillingTab)}
                    className={`
                      py-2 px-1 border-b-2 font-medium text-sm transition-colors
                      ${activeTab === tab.key
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }
                    `}
                  >
                    <span className="mr-2">{tab.icon}</span>
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>
          </nav>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="p-6">
        {activeTab === 'overview' && <BillingOverview />}
        {activeTab === 'methods' && <PaymentMethodsSection />}
        {activeTab === 'invoices' && <InvoicesSection />}
        {activeTab === 'subscriptions' && <SubscriptionsSection />}
      </main>
    </div>
  );
}

// Overview Tab Content
function BillingOverview() {
  return (
    <div className="space-y-8">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <PaymentDashboardSummary />
        
        {/* Quick Stats */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">This Month</h3>
          <div className="space-y-4">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Payments Made</span>
              <span className="text-sm font-medium text-gray-900">3</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Total Spent</span>
              <span className="text-sm font-medium text-gray-900">R 245.00</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Average Payment</span>
              <span className="text-sm font-medium text-gray-900">R 81.67</span>
            </div>
          </div>
        </div>
        
        {/* Account Status */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Status</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Payment Status</span>
              <PaymentStatusIndicator status="paid" />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Next Payment</span>
              <span className="text-sm text-gray-900">Dec 15, 2025</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Plan</span>
              <span className="text-sm font-medium text-blue-600">Professional</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentPaymentsWidget limit={5} />
        
        {/* Upcoming Payments */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Payments</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-gray-900">Monthly Subscription</p>
                <p className="text-xs text-gray-500">Due in 4 days</p>
              </div>
              <span className="text-sm font-semibold text-gray-900">R 99.00</span>
            </div>
            <div className="text-center py-4 text-gray-500 text-sm">
              No other upcoming payments
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Payment Methods Tab (Placeholder for Codex)
function PaymentMethodsSection() {
  const { paymentMethods, loading, error, loadPaymentMethods, updatePaymentMethod, removePaymentMethod } = usePaymentMethods();
  const { openPaymentMethodModal } = usePaymentUI();
  
  useEffect(() => {
    loadPaymentMethods();
  }, [loadPaymentMethods]);
  
  const handleAdd = () => {
    openPaymentMethodModal();
  };
  
  const handleEdit = (_method: PaymentMethod) => {
    openPaymentMethodModal();
  };
  
  const handleDelete = (methodId: string) => {
    removePaymentMethod(methodId);
  };
  
  const handleSetDefault = (methodId: string) => {
    const target = paymentMethods.find((method) => method.id === methodId);
    if (!target) return;
    
    // Remove default flag from any existing default method
    paymentMethods
      .filter((method) => method.isDefault && method.id !== methodId)
      .forEach((method) => updatePaymentMethod({ ...method, isDefault: false }));
    
    updatePaymentMethod({ ...target, isDefault: true });
  };
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error loading payment methods: {error}</p>
      </div>
    );
  }
  
  return (
    <PaymentMethodManager
      methods={paymentMethods}
      onAdd={handleAdd}
      onEdit={handleEdit}
      onDelete={handleDelete}
      onSetDefault={handleSetDefault}
    />
  );
}

// Invoices Tab - Comprehensive Invoice Management
function InvoicesSection() {
  return (
    <div className="space-y-6">
      <InvoiceHistory />
    </div>
  );
}

// Subscriptions Tab
function SubscriptionsSection() {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Subscriptions</h2>
        
        <div className="border border-gray-200 rounded-lg">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-gray-900">CapeControl Professional</h3>
                <p className="text-sm text-gray-500 mt-1">
                  Advanced automation and agent management
                </p>
              </div>
              <div className="text-right">
                <div className="text-lg font-semibold text-gray-900">R 99.00/month</div>
                <PaymentStatusIndicator status="paid" />
              </div>
            </div>
            
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Next payment:</span>
                <div className="font-medium">December 15, 2025</div>
              </div>
              <div>
                <span className="text-gray-500">Payment method:</span>
                <div className="font-medium">•••• 4242</div>
              </div>
              <div>
                <span className="text-gray-500">Started:</span>
                <div className="font-medium">January 15, 2025</div>
              </div>
            </div>
            
            <div className="mt-6 flex space-x-3">
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm">
                Update Payment Method
              </button>
              <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 text-sm">
                Cancel Subscription
              </button>
            </div>
          </div>
        </div>
        
        {/* Available Plans */}
        <div className="mt-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Available Plans</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { name: 'Starter', price: 29, features: ['5 Agents', 'Basic Support', '10GB Storage'] },
              { name: 'Professional', price: 99, features: ['Unlimited Agents', 'Priority Support', '100GB Storage'], current: true },
              { name: 'Enterprise', price: 299, features: ['Everything', 'Custom Integration', 'Dedicated Support'] },
            ].map((plan) => (
              <div
                key={plan.name}
                className={`border rounded-lg p-4 ${
                  plan.current ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                }`}
              >
                <h4 className="font-medium text-gray-900">{plan.name}</h4>
                <div className="mt-2">
                  <span className="text-2xl font-bold">R {plan.price}</span>
                  <span className="text-gray-500">/month</span>
                </div>
                <ul className="mt-3 space-y-1 text-sm text-gray-600">
                  {plan.features.map((feature, index) => (
                    <li key={index}>• {feature}</li>
                  ))}
                </ul>
                {plan.current ? (
                  <div className="mt-4 text-sm text-blue-600 font-medium">Current Plan</div>
                ) : (
                  <button className="mt-4 w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 text-sm">
                    Upgrade
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// Main exported component with full security wrapper
export default function BillingPage() {
  return (
    <PaymentSecurityProvider>
      <PaymentStateProvider>
        <PaymentSecurityGuard>
          <PaymentErrorBoundary>
            <BillingPageCore />
          </PaymentErrorBoundary>
        </PaymentSecurityGuard>
      </PaymentStateProvider>
    </PaymentSecurityProvider>
  );
}

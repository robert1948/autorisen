/**
 * Billing Page - Payment Management Dashboard
 * Wired to real subscription, plan, and invoice data via useBilling hook.
 */

import React, { useEffect, useRef, useState } from 'react';
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom';
import { PaymentStateProvider, usePaymentMethods, usePaymentUI } from '../../context/PaymentStateContext';
import { PaymentErrorBoundary } from '../../components/payments/PaymentErrorBoundary';
import { PaymentSecurityProvider, PaymentSecurityGuard } from '../../components/payments/PaymentSecurityProvider';
import PaymentMethodManager from '../../components/payments/PaymentMethodManager';
import InvoiceHistory from '../../components/payments/InvoiceHistory';
import { useBilling } from '../../hooks/useBilling';
import type { PaymentMethod, Plan } from '../../types/payments';

// Tab navigation for billing sections
type BillingTab = 'overview' | 'methods' | 'invoices' | 'subscriptions';

function BillingPageCore() {
  const location = useLocation();
  const billing = useBilling();
  
  // Determine active tab from URL
  const getActiveTab = (): BillingTab => {
    const path = location.pathname;
    if (path.includes('/methods')) return 'methods';
    if (path.includes('/invoices')) return 'invoices';
    if (path.includes('/subscriptions')) return 'subscriptions';
    return 'overview';
  };
  
  const activeTab = getActiveTab();
  
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-950">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 dark:bg-slate-900 dark:border-slate-700">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link 
                to="/app/dashboard" 
                className="text-gray-500 hover:text-gray-700 dark:text-slate-400 dark:hover:text-slate-200"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </Link>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Billing & Payments</h1>
            </div>
            <Link
              to="/app/pricing"
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm font-medium"
            >
              Upgrade Plan
            </Link>
          </div>
          
          {/* Tab Navigation */}
          <nav className="mt-6">
            <div className="border-b border-gray-200 dark:border-slate-700">
              <div className="flex space-x-8">
                {[
                  { key: 'overview', label: 'Overview', icon: '📊', to: '/app/billing' },
                  { key: 'methods', label: 'Payment Methods', icon: '💳', to: '/app/billing/methods' },
                  { key: 'invoices', label: 'Invoices', icon: '📄', to: '/app/billing/invoices' },
                  { key: 'subscriptions', label: 'Subscriptions', icon: '🔄', to: '/app/billing/subscriptions' },
                ].map((tab) => (
                  <NavLink
                    key={tab.key}
                    to={tab.to}
                    end={tab.key === 'overview'}
                    className={({ isActive }) => `
                      py-2 px-1 border-b-2 font-medium text-sm transition-colors
                      ${isActive
                        ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-slate-400 dark:hover:text-slate-200'
                      }
                    `}
                  >
                    <span className="mr-2">{tab.icon}</span>
                    {tab.label}
                  </NavLink>
                ))}
              </div>
            </div>
          </nav>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="p-6">
        {billing.loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : billing.error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 dark:bg-red-900/20 dark:border-red-800">
            <p className="text-red-800 dark:text-red-300">{billing.error}</p>
            <button onClick={billing.refresh} className="mt-2 text-sm text-red-600 underline dark:text-red-400">
              Try again
            </button>
          </div>
        ) : (
          <>
            {activeTab === 'overview' && <BillingOverview billing={billing} />}
            {activeTab === 'methods' && <PaymentMethodsSection />}
            {activeTab === 'invoices' && <InvoicesSection />}
            {activeTab === 'subscriptions' && <SubscriptionsSection billing={billing} />}
          </>
        )}
      </main>
    </div>
  );
}

// Overview Tab Content — wired to real data
function BillingOverview({ billing }: { billing: ReturnType<typeof useBilling> }) {
  const { subscription, plans, invoiceStats, latestInvoice } = billing;
  const currentPlan = plans.find((p) => p.id === subscription?.plan_id) ?? plans.find((p) => p.is_default);
  const statusLabel = subscription?.status ?? 'free';
  const periodEnd = subscription?.current_period_end
    ? new Date(subscription.current_period_end).toLocaleDateString('en-ZA', { day: 'numeric', month: 'long', year: 'numeric' })
    : '—';

  return (
    <div className="space-y-8">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Current Plan */}
        <div className="bg-white rounded-lg shadow p-6 dark:bg-slate-900">
          <h3 className="text-sm font-medium text-gray-500 dark:text-slate-400">Current Plan</h3>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-gray-900 dark:text-white">{currentPlan?.name ?? 'Free'}</span>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
              statusLabel === 'active' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
                : statusLabel === 'cancelled' ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
                : 'bg-gray-100 text-gray-600 dark:bg-slate-700 dark:text-slate-300'
            }`}>
              {statusLabel}
            </span>
          </div>
          {currentPlan && parseFloat(currentPlan.price_monthly_zar) > 0 && (
            <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">
              R{parseFloat(currentPlan.price_monthly_zar).toLocaleString('en-ZA')}/month
            </p>
          )}
          {subscription?.cancel_at_period_end && (
            <p className="mt-2 text-xs text-amber-600 dark:text-amber-400">
              Cancels at end of period ({periodEnd})
            </p>
          )}
        </div>

        {/* Invoice Stats */}
        <div className="bg-white rounded-lg shadow p-6 dark:bg-slate-900">
          <h3 className="text-sm font-medium text-gray-500 dark:text-slate-400">Payments</h3>
          <div className="mt-2 space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600 dark:text-slate-400">Total Invoices</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">{invoiceStats.total_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600 dark:text-slate-400">Paid</span>
              <span className="text-sm font-medium text-emerald-600 dark:text-emerald-400">{invoiceStats.paid_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600 dark:text-slate-400">Total Spent</span>
              <span className="text-sm font-bold text-gray-900 dark:text-white">
                R{invoiceStats.total_amount.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
              </span>
            </div>
          </div>
        </div>

        {/* Next Payment / Period */}
        <div className="bg-white rounded-lg shadow p-6 dark:bg-slate-900">
          <h3 className="text-sm font-medium text-gray-500 dark:text-slate-400">Billing Period</h3>
          <div className="mt-2 space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600 dark:text-slate-400">Period Ends</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">{periodEnd}</span>
            </div>
            {latestInvoice && (
              <div className="flex justify-between">
                <span className="text-sm text-gray-600 dark:text-slate-400">Last Invoice</span>
                <span className="text-sm font-mono text-gray-700 dark:text-slate-300">
                  {latestInvoice.invoice_number ?? latestInvoice.id.slice(0, 8)}
                </span>
              </div>
            )}
            {latestInvoice && (
              <div className="flex justify-between">
                <span className="text-sm text-gray-600 dark:text-slate-400">Last Amount</span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {latestInvoice.currency} {parseFloat(latestInvoice.amount).toFixed(2)}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6 dark:bg-slate-900">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h3>
        <div className="flex flex-wrap gap-3">
          <Link
            to="/app/pricing"
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm font-medium"
          >
            {subscription?.plan_id === 'free' || !subscription ? 'Upgrade Plan' : 'Change Plan'}
          </Link>
          <Link
            to="/app/billing/invoices"
            className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 text-sm font-medium dark:bg-slate-800 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-700"
          >
            View Invoices
          </Link>
        </div>
      </div>
    </div>
  );
}

// Payment Methods Tab (Placeholder for Codex)
function PaymentMethodsSection() {
  const { paymentMethods, loading, error, loadPaymentMethods, addPaymentMethod, updatePaymentMethod, removePaymentMethod } = usePaymentMethods();
  const { isPaymentMethodModalOpen, openPaymentMethodModal, closePaymentMethodModal } = usePaymentUI();
  const hasLoadedRef = useRef(false);
  const [editingMethod, setEditingMethod] = useState<PaymentMethod | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [methodType, setMethodType] = useState<PaymentMethod['methodType']>('card');
  const [isActive, setIsActive] = useState(true);
  const [lastFour, setLastFour] = useState('');
  const [cardBrand, setCardBrand] = useState('');
  const [expiryMonth, setExpiryMonth] = useState('');
  const [expiryYear, setExpiryYear] = useState('');
  const [modalError, setModalError] = useState<string | null>(null);
  
  useEffect(() => {
    if (hasLoadedRef.current) return;
    hasLoadedRef.current = true;
    loadPaymentMethods();
  }, [loadPaymentMethods]);

  const resetForm = () => {
    setEditingMethod(null);
    setMethodType('card');
    setIsActive(true);
    setLastFour('');
    setCardBrand('');
    setExpiryMonth('');
    setExpiryYear('');
  };

  const handleCloseModal = () => {
    setModalError(null);
    resetForm();
    closePaymentMethodModal();
  };
  
  const handleAdd = () => {
    setModalError(null);
    resetForm();
    openPaymentMethodModal();
  };
  
  const handleEdit = (method: PaymentMethod) => {
    setModalError(null);
    setEditingMethod(method);
    setMethodType(method.methodType);
    setIsActive(method.isActive);
    setLastFour(method.lastFour ?? '');
    setCardBrand(method.cardBrand ?? '');
    setExpiryMonth(method.expiryMonth ? String(method.expiryMonth) : '');
    setExpiryYear(method.expiryYear ? String(method.expiryYear) : '');
    openPaymentMethodModal();
  };
  
  const handleDelete = async (methodId: string) => {
    setModalError(null);
    try {
      await removePaymentMethod(methodId);
    } catch (e: unknown) {
      setModalError(e instanceof Error ? e.message : 'Failed to remove payment method');
    }
  };
  
  const handleSetDefault = async (methodId: string) => {
    setModalError(null);
    try {
      await updatePaymentMethod(methodId, { isDefault: true });
    } catch (e: unknown) {
      setModalError(e instanceof Error ? e.message : 'Failed to set default payment method');
    }
  };

  const handleSubmitMethod = async () => {
    setModalError(null);
    if (isSaving) return;

    if (methodType === 'card' && !/^\d{4}$/.test(lastFour.trim())) {
      setModalError('Last four digits must be exactly 4 numbers for card methods.');
      return;
    }

    try {
      setIsSaving(true);
      const monthNum = expiryMonth ? Number(expiryMonth) : undefined;
      const yearNum = expiryYear ? Number(expiryYear) : undefined;

      const payload = {
        methodType,
        isActive,
        lastFour: methodType === 'card' ? lastFour.trim() : undefined,
        cardBrand: methodType === 'card' ? cardBrand.trim() || undefined : undefined,
        expiryMonth: methodType === 'card' ? monthNum : undefined,
        expiryYear: methodType === 'card' ? yearNum : undefined,
      };

      if (editingMethod) {
        await updatePaymentMethod(editingMethod.id, payload);
      } else {
        await addPaymentMethod({
          ...payload,
          isDefault: paymentMethods.length === 0,
        });
      }

      handleCloseModal();
    } catch (e: unknown) {
      setModalError(e instanceof Error ? e.message : editingMethod ? 'Failed to update payment method' : 'Failed to add payment method');
    } finally {
      setIsSaving(false);
    }
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
    <>
      {modalError && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3">
          <p className="text-sm text-red-700">{modalError}</p>
        </div>
      )}
      <PaymentMethodManager
        methods={paymentMethods}
        onAdd={handleAdd}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onSetDefault={handleSetDefault}
      />
      {isPaymentMethodModalOpen && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center px-4 z-50">
          <div className="bg-white rounded-xl shadow-xl p-6 max-w-md w-full space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">{editingMethod ? 'Edit payment method' : 'Add payment method'}</h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Method type</label>
              <select
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                value={methodType}
                onChange={(e) => setMethodType(e.target.value as PaymentMethod['methodType'])}
              >
                <option value="card">Card</option>
                <option value="eft">EFT</option>
                <option value="instant_eft">Instant EFT</option>
                <option value="bank_transfer">Bank transfer</option>
              </select>
            </div>
            {editingMethod && (
              <label className="inline-flex items-center gap-2 text-sm text-gray-700">
                <input
                  type="checkbox"
                  checked={isActive}
                  onChange={(e) => setIsActive(e.target.checked)}
                />
                Active method
              </label>
            )}
            {methodType === 'card' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Last four digits</label>
                  <input className="w-full border border-gray-300 rounded-md px-3 py-2" value={lastFour} maxLength={4} onChange={(e) => setLastFour(e.target.value.replace(/\D/g, ''))} />
                </div>
                <div className="grid grid-cols-3 gap-3">
                  <div className="col-span-1">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Exp MM</label>
                    <input className="w-full border border-gray-300 rounded-md px-3 py-2" value={expiryMonth} onChange={(e) => setExpiryMonth(e.target.value.replace(/\D/g, ''))} />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Exp YYYY</label>
                    <input className="w-full border border-gray-300 rounded-md px-3 py-2" value={expiryYear} onChange={(e) => setExpiryYear(e.target.value.replace(/\D/g, ''))} />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Card brand (optional)</label>
                  <input className="w-full border border-gray-300 rounded-md px-3 py-2" value={cardBrand} onChange={(e) => setCardBrand(e.target.value)} />
                </div>
              </>
            )}
            <div className="flex justify-end gap-3 pt-2">
              <button type="button" className="px-4 py-2 rounded-md border border-gray-300 text-gray-700" onClick={handleCloseModal}>Cancel</button>
              <button type="button" className="px-4 py-2 rounded-md bg-blue-600 text-white disabled:opacity-60" onClick={handleSubmitMethod} disabled={isSaving}>{isSaving ? 'Saving...' : editingMethod ? 'Save changes' : 'Save'}</button>
            </div>
          </div>
        </div>
      )}
    </>
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

// Subscriptions Tab — wired to real data
function SubscriptionsSection({ billing }: { billing: ReturnType<typeof useBilling> }) {
  const navigate = useNavigate();
  const { subscription, plans } = billing;
  const [cancelling, setCancelling] = useState(false);
  const [cancelError, setCancelError] = useState<string | null>(null);

  const currentPlan = plans.find((p) => p.id === subscription?.plan_id) ?? plans.find((p) => p.is_default);
  const isActive = subscription?.status === 'active';
  const isPaid = currentPlan && parseFloat(currentPlan.price_monthly_zar) > 0;
  const periodEnd = subscription?.current_period_end
    ? new Date(subscription.current_period_end).toLocaleDateString('en-ZA', { day: 'numeric', month: 'long', year: 'numeric' })
    : null;
  const periodStart = subscription?.current_period_start
    ? new Date(subscription.current_period_start).toLocaleDateString('en-ZA', { day: 'numeric', month: 'long', year: 'numeric' })
    : null;

  const handleCancel = async () => {
    if (!confirm('Are you sure you want to cancel your subscription? You will retain access until the end of your billing period.')) return;
    setCancelling(true);
    setCancelError(null);
    try {
      // Fetch CSRF token
      const csrfRes = await fetch('/api/auth/csrf');
      const csrfData = await csrfRes.json();
      const csrfToken = csrfData.csrf_token;

      const res = await fetch('/api/payments/subscription/cancel', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('autorisen-auth') ? JSON.parse(localStorage.getItem('autorisen-auth')!).accessToken : ''}`,
          'X-CSRF-Token': csrfToken,
        },
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Failed to cancel subscription');
      }
      billing.refresh();
    } catch (e: unknown) {
      setCancelError(e instanceof Error ? e.message : 'Failed to cancel');
    } finally {
      setCancelling(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Current Subscription Card */}
      <div className="bg-white rounded-lg shadow dark:bg-slate-900">
        <div className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Current Subscription</h2>
          
          <div className="border border-gray-200 rounded-lg p-6 dark:border-slate-700">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  CapeControl {currentPlan?.name ?? 'Free'}
                </h3>
                <p className="text-sm text-gray-500 dark:text-slate-400 mt-1">
                  {currentPlan?.description ?? 'Get started with CapeControl basics'}
                </p>
              </div>
              <div className="text-right">
                <div className="text-lg font-semibold text-gray-900 dark:text-white">
                  {isPaid ? `R${parseFloat(currentPlan!.price_monthly_zar).toLocaleString('en-ZA')}/month` : 'Free'}
                </div>
                <span className={`inline-block text-xs px-2 py-0.5 rounded-full font-medium mt-1 ${
                  isActive ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
                    : subscription?.status === 'cancelled' ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
                    : subscription?.status === 'pending' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                    : 'bg-gray-100 text-gray-600 dark:bg-slate-700 dark:text-slate-300'
                }`}>
                  {subscription?.status ?? 'free'}
                </span>
              </div>
            </div>

            {/* Period details */}
            {(periodStart || periodEnd) && (
              <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                {periodStart && (
                  <div>
                    <span className="text-gray-500 dark:text-slate-400">Started:</span>
                    <div className="font-medium text-gray-900 dark:text-white">{periodStart}</div>
                  </div>
                )}
                {periodEnd && (
                  <div>
                    <span className="text-gray-500 dark:text-slate-400">
                      {subscription?.cancel_at_period_end ? 'Access until:' : 'Renews:'}
                    </span>
                    <div className="font-medium text-gray-900 dark:text-white">{periodEnd}</div>
                  </div>
                )}
                <div>
                  <span className="text-gray-500 dark:text-slate-400">Plan ID:</span>
                  <div className="font-mono text-xs text-gray-700 dark:text-slate-300">{subscription?.plan_id ?? 'free'}</div>
                </div>
              </div>
            )}

            {/* Cancellation notice */}
            {subscription?.cancel_at_period_end && (
              <div className="mt-4 bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-700 dark:bg-amber-900/20 dark:border-amber-800 dark:text-amber-400">
                Your subscription will be cancelled at the end of the current billing period ({periodEnd}).
                You'll retain access to {currentPlan?.name} features until then.
              </div>
            )}

            {/* Actions */}
            <div className="mt-6 flex flex-wrap gap-3">
              <button
                onClick={() => navigate('/app/pricing')}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm font-medium"
              >
                {isPaid ? 'Change Plan' : 'Upgrade'}
              </button>
              {isPaid && isActive && !subscription?.cancel_at_period_end && (
                <button
                  onClick={handleCancel}
                  disabled={cancelling}
                  className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 text-sm font-medium disabled:opacity-50 dark:bg-slate-800 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-700"
                >
                  {cancelling ? 'Cancelling…' : 'Cancel Subscription'}
                </button>
              )}
            </div>

            {cancelError && (
              <p className="mt-3 text-sm text-red-600 dark:text-red-400">{cancelError}</p>
            )}
          </div>
        </div>
      </div>

      {/* Available Plans */}
      <div className="bg-white rounded-lg shadow p-6 dark:bg-slate-900">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Available Plans</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {plans.map((plan: Plan) => {
            const isCurrent = plan.id === subscription?.plan_id;
            const price = parseFloat(plan.price_monthly_zar);
            return (
              <div
                key={plan.id}
                className={`border rounded-lg p-4 ${
                  isCurrent
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-600'
                    : 'border-gray-200 dark:border-slate-700'
                }`}
              >
                <h4 className="font-medium text-gray-900 dark:text-white">{plan.name}</h4>
                <p className="text-xs text-gray-500 dark:text-slate-400 mt-0.5">{plan.description}</p>
                <div className="mt-2">
                  <span className="text-2xl font-bold text-gray-900 dark:text-white">
                    {price > 0 ? `R${price.toLocaleString('en-ZA')}` : 'R0'}
                  </span>
                  <span className="text-gray-500 dark:text-slate-400">
                    {price > 0 ? '/month' : ' forever'}
                  </span>
                </div>
                <ul className="mt-3 space-y-1 text-sm text-gray-600 dark:text-slate-400">
                  {plan.features.map((feature: string, index: number) => (
                    <li key={index}>✓ {feature}</li>
                  ))}
                </ul>
                {isCurrent ? (
                  <div className="mt-4 text-sm text-blue-600 font-medium dark:text-blue-400">Current Plan</div>
                ) : plan.is_enterprise ? (
                  <a
                    href="mailto:sales@cape-control.com"
                    className="mt-4 block w-full bg-gray-900 text-white py-2 rounded-lg hover:bg-gray-800 text-sm text-center dark:bg-slate-700 dark:hover:bg-slate-600"
                  >
                    Contact Sales
                  </a>
                ) : (
                  <button
                    onClick={() => navigate('/app/pricing')}
                    className="mt-4 w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 text-sm"
                  >
                    {price > 0 ? 'Upgrade' : 'Downgrade'}
                  </button>
                )}
              </div>
            );
          })}
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

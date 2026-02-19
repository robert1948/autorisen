/**
 * Checkout Page - Secure Payment Processing Interface
 * Integrates the CheckoutFlow component with URL parameters and navigation
 */

import React, { useMemo } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../features/auth/AuthContext';
import CheckoutFlow from '../../components/payments/CheckoutFlow';
import { PaymentErrorBoundary } from '../../components/payments/PaymentErrorBoundary';
import type { PaymentFormData, PayFastCheckoutResponse } from '../../types/payments';

export default function CheckoutPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { state: authState, loading: authLoading } = useAuth();
  const token = authState.accessToken;
  
  // Extract initial data from URL parameters
  const initialData = useMemo((): Partial<PaymentFormData> => {
    const data: Partial<PaymentFormData> = {};
    
    const amount = searchParams.get('amount');
    if (amount) {
      data.amount = amount;
    }
    
    const itemName = searchParams.get('item');
    if (itemName) {
      data.itemName = decodeURIComponent(itemName);
    }
    
    const description = searchParams.get('description');
    if (description) {
      data.itemDescription = decodeURIComponent(description);
    }
    
    return data;
  }, [searchParams]);

  const handleCheckoutComplete = (result: PayFastCheckoutResponse) => {
    // Create PayFast form and auto-submit
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = result.process_url;
    form.style.display = 'none';
    
    // Add all form fields
    Object.entries(result.fields).forEach(([key, value]) => {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = key;
      input.value = value;
      form.appendChild(input);
    });
    
    // Append to body and submit
    document.body.appendChild(form);
    form.submit();
  };
  
  const handleCheckoutCancel = () => {
    navigate('/app/billing');
  };

  // If product code is provided (from PricingPage), auto-checkout
  const productCode = searchParams.get('product');

  React.useEffect(() => {
    if (!productCode || authLoading) return;

    const doProductCheckout = async () => {
      try {
        const csrfRes = await fetch('/api/auth/csrf', { credentials: 'include' });
        const csrfData = await csrfRes.json().catch(() => ({}));
        const csrfToken = csrfData.csrf_token || '';

        const headers: Record<string, string> = {
          'Content-Type': 'application/json',
          'X-CSRF-Token': csrfToken,
        };
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }

        const res = await fetch('/api/payments/payfast/checkout', {
          method: 'POST',
          headers,
          credentials: 'include',
          body: JSON.stringify({ product_code: productCode }),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || 'Checkout failed');
        }
        const result = await res.json();
        handleCheckoutComplete(result);
      } catch (err) {
        console.error('Product checkout error:', err);
        // Fall through to normal checkout flow
      }
    };

    doProductCheckout();
  }, [productCode, token, authLoading]);

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-slate-700/50 bg-slate-800/60 backdrop-blur">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link 
                to="/app/billing" 
                className="text-slate-400 hover:text-white transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </Link>
              <h1 className="text-2xl font-bold text-white">Secure Checkout</h1>
            </div>
            <div className="text-sm text-slate-400">
              🔒 Secure payment processing
            </div>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="container mx-auto px-6 py-8 max-w-4xl">
        {/* Security Notice */}
        <div className="bg-blue-900/30 border border-blue-500/30 rounded-lg p-4 mb-8">
          <div className="flex items-start">
            <svg className="w-5 h-5 text-blue-400 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 className="text-sm font-medium text-blue-300">Secure Payment Processing</h3>
              <p className="mt-1 text-sm text-blue-400/80">
                Your payment information is encrypted and processed securely through PayFast.
                We never store your payment details on our servers.
              </p>
            </div>
          </div>
        </div>
        
        {/* Checkout Flow */}
        <div className="bg-slate-800/60 rounded-lg shadow-lg border border-slate-700/50">
          <PaymentErrorBoundary 
            fallback={
              <div className="p-8 text-center">
                <h3 className="text-lg font-medium text-white mb-4">Payment System Unavailable</h3>
                <p className="text-slate-400 mb-6">
                  We're experiencing technical difficulties with our payment system. 
                  Please try again in a few minutes.
                </p>
                <div className="space-x-4">
                  <button
                    onClick={() => window.location.reload()}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                  >
                    Try Again
                  </button>
                  <Link
                    to="/app/billing"
                    className="bg-slate-700 text-slate-200 px-4 py-2 rounded-lg hover:bg-slate-600"
                  >
                    Return to Billing
                  </Link>
                </div>
              </div>
            }
          >
            <CheckoutFlow
              initialData={initialData}
              onComplete={handleCheckoutComplete}
              onCancel={handleCheckoutCancel}
              className="p-8"
            />
          </PaymentErrorBoundary>
        </div>
        
        {/* Payment Info */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-slate-800/60 rounded-lg shadow border border-slate-700/50 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Payment Methods Accepted</h3>
            <div className="space-y-3">
              <div className="flex items-center">
                <div className="w-8 h-5 bg-blue-600 rounded mr-3"></div>
                <span className="text-sm text-slate-300">Credit & Debit Cards</span>
              </div>
              <div className="flex items-center">
                <div className="w-8 h-5 bg-green-600 rounded mr-3"></div>
                <span className="text-sm text-slate-300">Instant EFT</span>
              </div>
              <div className="flex items-center">
                <div className="w-8 h-5 bg-purple-600 rounded mr-3"></div>
                <span className="text-sm text-slate-300">Bank Transfer</span>
              </div>
            </div>
          </div>
          
          <div className="bg-slate-800/60 rounded-lg shadow border border-slate-700/50 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Security & Protection</h3>
            <div className="space-y-3 text-sm text-slate-400">
              <div className="flex items-start">
                <svg className="w-4 h-4 text-green-400 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>256-bit SSL encryption</span>
              </div>
              <div className="flex items-start">
                <svg className="w-4 h-4 text-green-400 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>PCI DSS compliant</span>
              </div>
              <div className="flex items-start">
                <svg className="w-4 h-4 text-green-400 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Fraud protection</span>
              </div>
              <div className="flex items-start">
                <svg className="w-4 h-4 text-green-400 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Secure data handling</span>
              </div>
            </div>
          </div>
        </div>
        
        {/* Support Info */}
        <div className="mt-8 text-center text-sm text-slate-500">
          <p>
            Need help? <Link to="/support" className="text-blue-400 hover:text-blue-300">Contact support</Link>
            {' '}or call +27 11 123 4567
          </p>
          <p className="mt-1">
            By proceeding, you agree to our{' '}
            <Link to="/terms" className="text-blue-400 hover:text-blue-300">Terms of Service</Link>
            {' '}and{' '}
            <Link to="/privacy" className="text-blue-400 hover:text-blue-300">Privacy Policy</Link>
          </p>
        </div>
      </main>
    </div>
  );
}
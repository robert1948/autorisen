/**
 * Pricing Page - Plan comparison and subscription selection
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../features/auth/AuthContext';
import type { Plan, PlansResponse, Subscription } from '../../types/payments';

export default function PricingPage() {
  const navigate = useNavigate();
  const { isAuthenticated, token } = useAuth();
  const [plans, setPlans] = useState<Plan[]>([]);
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const [loading, setLoading] = useState(true);
  const [subscribing, setSubscribing] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch plans (public endpoint)
        const plansRes = await fetch('/api/payments/plans');
        if (plansRes.ok) {
          const data: PlansResponse = await plansRes.json();
          setPlans(data.plans);
        }

        // Fetch current subscription if authenticated
        if (isAuthenticated && token) {
          const subRes = await fetch('/api/payments/subscription', {
            headers: { Authorization: `Bearer ${token}` },
          });
          if (subRes.ok) {
            setSubscription(await subRes.json());
          }
        }
      } catch {
        setError('Failed to load pricing information');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [isAuthenticated, token]);

  const handleSelectPlan = async (plan: Plan) => {
    if (!isAuthenticated) {
      navigate('/auth/login?redirect=/app/pricing');
      return;
    }
    if (plan.id === subscription?.plan_id && subscription?.status === 'active') {
      return; // Already on this plan
    }

    setSubscribing(plan.id);
    setError(null);

    try {
      // Create/update subscription
      const res = await fetch('/api/payments/subscription', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          plan_id: plan.id,
          billing_cycle: billingCycle,
        }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Failed to update subscription');
      }

      const updatedSub: Subscription = await res.json();
      setSubscription(updatedSub);

      // For paid plans, redirect to checkout
      if (plan.id !== 'free') {
        const productCode = billingCycle === 'yearly'
          ? plan.product_code_yearly
          : plan.product_code_monthly;
        navigate(`/app/checkout?product=${productCode}`);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setSubscribing(null);
    }
  };

  const getPrice = (plan: Plan): string => {
    const price = billingCycle === 'yearly' ? plan.price_yearly_zar : plan.price_monthly_zar;
    const num = parseFloat(price);
    if (num === 0) return 'Free';
    if (billingCycle === 'yearly') {
      const monthly = num / 12;
      return `R${monthly.toFixed(0)}/mo`;
    }
    return `R${num.toFixed(0)}/mo`;
  };

  const getAnnualPrice = (plan: Plan): string | null => {
    if (billingCycle !== 'yearly') return null;
    const num = parseFloat(plan.price_yearly_zar);
    if (num === 0) return null;
    return `R${num.toLocaleString()}/year`;
  };

  const isCurrentPlan = (plan: Plan): boolean => {
    return subscription?.plan_id === plan.id && subscription?.status === 'active';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary,#0f172a)] flex items-center justify-center">
        <div className="text-[var(--text-secondary,#94a3b8)]">Loading plans...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--bg-primary,#0f172a)] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-3">
            Choose Your Plan
          </h1>
          <p className="text-[var(--text-secondary,#94a3b8)] text-lg max-w-2xl mx-auto">
            Scale your AI automation with the right plan for your team
          </p>
        </div>

        {/* Billing Toggle */}
        <div className="flex items-center justify-center gap-3 mb-10">
          <span className={`text-sm font-medium ${billingCycle === 'monthly' ? 'text-white' : 'text-[var(--text-secondary,#94a3b8)]'}`}>
            Monthly
          </span>
          <button
            onClick={() => setBillingCycle(b => b === 'monthly' ? 'yearly' : 'monthly')}
            className={`relative inline-flex h-7 w-14 items-center rounded-full transition-colors ${
              billingCycle === 'yearly' ? 'bg-blue-600' : 'bg-gray-600'
            }`}
            aria-label="Toggle billing cycle"
          >
            <span
              className={`inline-block h-5 w-5 transform rounded-full bg-white transition-transform ${
                billingCycle === 'yearly' ? 'translate-x-8' : 'translate-x-1'
              }`}
            />
          </button>
          <span className={`text-sm font-medium ${billingCycle === 'yearly' ? 'text-white' : 'text-[var(--text-secondary,#94a3b8)]'}`}>
            Yearly
          </span>
          {billingCycle === 'yearly' && (
            <span className="ml-2 inline-block bg-green-500/20 text-green-400 text-xs font-semibold px-2 py-0.5 rounded-full">
              Save 20%
            </span>
          )}
        </div>

        {error && (
          <div className="mb-6 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-center text-sm">
            {error}
          </div>
        )}

        {/* Plan Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans.map((plan) => {
            const current = isCurrentPlan(plan);
            const isPro = plan.id === 'pro';

            return (
              <div
                key={plan.id}
                className={`relative rounded-2xl border p-6 flex flex-col ${
                  isPro
                    ? 'border-blue-500 bg-[var(--bg-secondary,#1e293b)] ring-2 ring-blue-500/30'
                    : 'border-[var(--border-color,#334155)] bg-[var(--bg-secondary,#1e293b)]'
                }`}
              >
                {isPro && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full">
                    Most Popular
                  </div>
                )}

                <div className="mb-4">
                  <h3 className="text-xl font-bold text-white">{plan.name}</h3>
                  <p className="text-[var(--text-secondary,#94a3b8)] text-sm mt-1">
                    {plan.description}
                  </p>
                </div>

                <div className="mb-6">
                  <div className="flex items-baseline gap-1">
                    <span className="text-3xl font-bold text-white">
                      {getPrice(plan)}
                    </span>
                  </div>
                  {getAnnualPrice(plan) && (
                    <p className="text-xs text-[var(--text-secondary,#94a3b8)] mt-1">
                      Billed {getAnnualPrice(plan)}
                    </p>
                  )}
                </div>

                <ul className="space-y-3 mb-8 flex-1">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <svg className="w-4 h-4 text-green-400 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-[var(--text-secondary,#94a3b8)]">{feature}</span>
                    </li>
                  ))}
                </ul>

                {plan.is_enterprise ? (
                  <a
                    href="mailto:sales@cape-control.com?subject=Enterprise%20Inquiry"
                    className="w-full block text-center py-2.5 px-4 rounded-lg border border-blue-500 text-blue-400 font-medium hover:bg-blue-500/10 transition-colors"
                  >
                    Contact Sales
                  </a>
                ) : current ? (
                  <button
                    disabled
                    className="w-full py-2.5 px-4 rounded-lg bg-green-600/20 text-green-400 font-medium cursor-default"
                  >
                    Current Plan
                  </button>
                ) : (
                  <button
                    onClick={() => handleSelectPlan(plan)}
                    disabled={subscribing === plan.id}
                    className={`w-full py-2.5 px-4 rounded-lg font-medium transition-colors ${
                      isPro
                        ? 'bg-blue-600 text-white hover:bg-blue-700'
                        : 'bg-[var(--bg-primary,#0f172a)] text-white hover:bg-[var(--bg-primary,#0f172a)]/80 border border-[var(--border-color,#334155)]'
                    } disabled:opacity-50`}
                  >
                    {subscribing === plan.id ? 'Processing...' : plan.id === 'free' ? 'Get Started' : 'Subscribe'}
                  </button>
                )}
              </div>
            );
          })}
        </div>

        {/* FAQ / trust signals */}
        <div className="mt-16 text-center">
          <p className="text-[var(--text-secondary,#94a3b8)] text-sm">
            All prices in ZAR. Cancel anytime. Secure payments via PayFast.
          </p>
        </div>
      </div>
    </div>
  );
}

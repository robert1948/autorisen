import React, { useState, useEffect } from 'react';
import useAuth from '../hooks/useAuth';

const Subscribe = () => {
  const { user } = useAuth();
  const [selectedTier, setSelectedTier] = useState('Basic');
  const [pricing, setPricing] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [currentSubscription, setCurrentSubscription] = useState(null);

  const tiers = {
    Basic: {
      name: 'Basic',
      description: 'Perfect for individuals getting started',
      highlight: false
    },
    Pro: {
      name: 'Pro',
      description: 'Best for growing teams and businesses',
      highlight: true
    },
    Enterprise: {
      name: 'Enterprise',
      description: 'For large organizations with advanced needs',
      highlight: false
    }
  };

  useEffect(() => {
    fetchPricing();
    fetchCurrentSubscription();
  }, []);

  const fetchPricing = async () => {
    try {
      const response = await fetch('/api/payment/pricing');
      const data = await response.json();
      setPricing(data);
    } catch (err) {
      console.error('Failed to fetch pricing:', err);
    }
  };

  const fetchCurrentSubscription = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/payment/subscription/status', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setCurrentSubscription(data);
      }
    } catch (err) {
      console.error('Failed to fetch subscription:', err);
    }
  };

  const handleSubscribe = async (tier) => {
    if (!user) {
      setError('Please log in to subscribe');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // For demo purposes, we'll simulate a payment method
      // In production, you'd integrate with Stripe Elements
      const paymentMethodId = 'pm_card_visa'; // Test payment method

      const token = localStorage.getItem('token');
      const response = await fetch('/api/payment/subscription/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          tier,
          payment_method_id: paymentMethodId
        })
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(`Successfully subscribed to ${tier} plan!`);
        fetchCurrentSubscription();
      } else {
        setError(data.detail || 'Subscription failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    if (!confirm('Are you sure you want to cancel your subscription?')) {
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/payment/subscription/cancel', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setSuccess('Subscription cancelled successfully');
        fetchCurrentSubscription();
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to cancel subscription');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!pricing) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Choose Your Plan
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Unlock the full potential of Cape Control with our flexible subscription tiers
          </p>
        </div>

        {/* Current Subscription Status */}
        {currentSubscription && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h3 className="text-lg font-semibold mb-4">Current Subscription</h3>
            <div className="flex items-center justify-between">
              <div>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                  {currentSubscription.tier} Plan
                </span>
                <p className="text-gray-600 mt-1">
                  Status: {currentSubscription.status} | 
                  API Calls: {currentSubscription.api_calls_limit} per month
                </p>
              </div>
              {currentSubscription.tier !== 'Basic' && (
                <button
                  onClick={handleCancelSubscription}
                  disabled={loading}
                  className="px-4 py-2 text-red-600 border border-red-300 rounded-md hover:bg-red-50 disabled:opacity-50"
                >
                  Cancel Subscription
                </button>
              )}
            </div>
          </div>
        )}

        {/* Alert Messages */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">{error}</div>
              </div>
            </div>
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-green-800">Success</h3>
                <div className="mt-2 text-sm text-green-700">{success}</div>
              </div>
            </div>
          </div>
        )}

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8">
          {Object.entries(pricing.subscription_tiers).map(([tierName, tierData]) => {
            const tierInfo = tiers[tierName];
            const isCurrentTier = currentSubscription?.tier === tierName;
            
            return (
              <div
                key={tierName}
                className={`bg-white rounded-lg shadow-lg overflow-hidden ${
                  tierInfo.highlight ? 'ring-2 ring-purple-600 transform scale-105' : ''
                }`}
              >
                {tierInfo.highlight && (
                  <div className="bg-purple-600 text-white text-center py-2 text-sm font-medium">
                    Most Popular
                  </div>
                )}
                
                <div className="p-6">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">
                    {tierInfo.name}
                  </h3>
                  <p className="text-gray-600 mb-4">{tierInfo.description}</p>
                  
                  <div className="mb-6">
                    <span className="text-4xl font-bold text-gray-900">
                      ${tierData.price_usd}
                    </span>
                    <span className="text-gray-600">/month</span>
                  </div>

                  <ul className="space-y-3 mb-6">
                    <li className="flex items-center">
                      <svg className="h-5 w-5 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-gray-700">
                        {tierData.api_calls.toLocaleString()} API calls/month
                      </span>
                    </li>
                    {tierData.features.map((feature, index) => (
                      <li key={index} className="flex items-center">
                        <svg className="h-5 w-5 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                    <li className="flex items-center">
                      <svg className="h-5 w-5 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-gray-700">{tierData.support} Support</span>
                    </li>
                  </ul>

                  <button
                    onClick={() => handleSubscribe(tierName)}
                    disabled={loading || isCurrentTier}
                    className={`w-full py-3 px-4 rounded-lg font-semibold transition-colors ${
                      isCurrentTier
                        ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                        : tierInfo.highlight
                        ? 'bg-purple-600 text-white hover:bg-purple-700'
                        : 'bg-gray-900 text-white hover:bg-gray-800'
                    } disabled:opacity-50`}
                  >
                    {loading ? 'Processing...' : isCurrentTier ? 'Current Plan' : `Subscribe to ${tierName}`}
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Credit Packs Section */}
        <div className="mt-16">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Need Extra Credits?
            </h2>
            <p className="text-lg text-gray-600">
              Purchase additional credits for one-time usage or overflow capacity
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {Object.entries(pricing.credit_packs).map(([packName, packData]) => (
              <div key={packName} className="bg-white rounded-lg shadow-lg p-6">
                <div className="text-center">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2 capitalize">
                    {packName} Pack
                  </h3>
                  <div className="mb-4">
                    <span className="text-3xl font-bold text-gray-900">
                      ${packData.price_usd}
                    </span>
                  </div>
                  <div className="mb-4">
                    <span className="text-lg text-gray-600">
                      {packData.total_credits} credits
                    </span>
                    {packData.bonus > 0 && (
                      <span className="block text-sm text-green-600 font-medium">
                        +{packData.bonus} bonus credits!
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500 mb-6">
                    {packData.value}
                  </p>
                  <button
                    onClick={() => {/* TODO: Implement credit purchase */}}
                    disabled={loading || !user}
                    className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                  >
                    Purchase Credits
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Enterprise Contact */}
        <div className="mt-16 bg-gray-900 rounded-lg p-8 text-center">
          <h3 className="text-2xl font-bold text-white mb-4">
            Need a Custom Solution?
          </h3>
          <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
            Our team can build custom AI agents and integrations tailored to your specific needs.
            Contact us for enterprise pricing and dedicated support.
          </p>
          <button
            onClick={() => {/* TODO: Implement custom agent request */}}
            className="bg-purple-600 text-white px-8 py-3 rounded-lg hover:bg-purple-700 transition-colors"
          >
            Request Custom Development
          </button>
        </div>
      </div>
    </div>
  );
};

export default Subscribe;

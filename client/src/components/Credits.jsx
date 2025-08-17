import React, { useState, useEffect } from 'react';
import useAuth from '../hooks/useAuth';

const Credits = () => {
  const { user } = useAuth();
  const [creditBalance, setCreditBalance] = useState(null);
  const [pricing, setPricing] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (user) {
      fetchCreditBalance();
      fetchPricing();
    }
  }, [user]);

  const fetchCreditBalance = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/payment/credits/balance', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCreditBalance(data);
      }
    } catch (err) {
      console.error('Failed to fetch credit balance:', err);
    }
  };

  const fetchPricing = async () => {
    try {
      const response = await fetch('/api/payment/pricing');
      const data = await response.json();
      setPricing(data);
    } catch (err) {
      console.error('Failed to fetch pricing:', err);
    }
  };

  const handlePurchaseCredits = async (packSize) => {
    if (!user) {
      setError('Please log in to purchase credits');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // Build PayFast checkout request
      const pack = pricing?.credit_packs?.[packSize];
      if (!pack) {
        setError('Invalid credit pack selected');
        setLoading(false);
        return;
      }

      // PayFast uses ZAR; for sandbox, we reuse displayed USD numeric value as amount
      const amountDecimal = Number(pack.price_usd).toFixed(2);
      const mPaymentId = `credits:${user.id}:${packSize}:${Date.now()}`;

      const payload = {
        m_payment_id: mPaymentId,
        amount: amountDecimal,
        item_name: `CapeControl Credits - ${packSize}`,
        item_description: `Purchase of ${pack.total_credits} credits (${pack.credits}+${pack.bonus} bonus).`,
        email_address: user.email || ''
      };

      const resp = await fetch('/api/payfast/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!resp.ok) {
        const data = await resp.json().catch(() => ({}));
        throw new Error(data.detail || 'Failed to create PayFast checkout');
      }

      const data = await resp.json();
      // Redirect user to PayFast payment page
      window.location.assign(data.redirect_url);
    } catch (err) {
      setError(err.message || 'Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Please Log In
          </h2>
          <p className="text-gray-600">
            You need to be logged in to view your credits
          </p>
        </div>
      </div>
    );
  }

  if (!creditBalance || !pricing) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const packSizes = ['small', 'medium', 'large'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Your Credits
          </h1>
          <p className="text-xl text-gray-600">
            Manage your credit balance and purchase additional credits
          </p>
        </div>

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

        {/* Current Balance */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <div className="text-center">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Current Balance
            </h2>
            <div className="text-6xl font-bold text-blue-600 mb-4">
              {creditBalance.balance.toLocaleString()}
            </div>
            <p className="text-gray-600">
              Credits available for AI agent usage
            </p>
          </div>
        </div>

        {/* Purchase Credits */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Purchase Additional Credits
          </h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            {packSizes.map((packSize) => {
              const packData = pricing.credit_packs[packSize];
              const isPopular = packSize === 'medium';
              
              return (
                <div
                  key={packSize}
                  className={`bg-white rounded-lg shadow-lg overflow-hidden ${
                    isPopular ? 'ring-2 ring-blue-600 transform scale-105' : ''
                  }`}
                >
                  {isPopular && (
                    <div className="bg-blue-600 text-white text-center py-2 text-sm font-medium">
                      Best Value
                    </div>
                  )}
                  
                  <div className="p-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-2 capitalize">
                      {packSize} Pack
                    </h3>
                    
                    <div className="mb-4">
                      <span className="text-3xl font-bold text-gray-900">
                        ${packData.price_usd}
                      </span>
                    </div>

                    <div className="mb-6">
                      <div className="text-lg text-gray-700 mb-2">
                        {packData.credits.toLocaleString()} credits
                      </div>
                      {packData.bonus > 0 && (
                        <div className="text-green-600 font-medium">
                          + {packData.bonus.toLocaleString()} bonus credits!
                        </div>
                      )}
                      <div className="text-lg font-semibold text-gray-900 mt-2">
                        Total: {packData.total_credits.toLocaleString()} credits
                      </div>
                      <div className="text-sm text-gray-500 mt-1">
                        {packData.value}
                      </div>
                    </div>

                    <button
                      onClick={() => handlePurchaseCredits(packSize)}
                      disabled={loading}
                      className={`w-full py-3 px-4 rounded-lg font-semibold transition-colors ${
                        isPopular
                          ? 'bg-blue-600 text-white hover:bg-blue-700'
                          : 'bg-gray-900 text-white hover:bg-gray-800'
                      } disabled:opacity-50`}
                    >
                      {loading ? 'Processing...' : `Purchase ${packSize.charAt(0).toUpperCase() + packSize.slice(1)} Pack`}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            Recent Transactions
          </h3>
          
          {creditBalance.recent_transactions.length === 0 ? (
            <p className="text-gray-600 text-center py-8">
              No transactions yet
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Description
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {creditBalance.recent_transactions.map((transaction) => (
                    <tr key={transaction.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(transaction.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          transaction.type === 'purchase' 
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {transaction.type}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {transaction.type === 'purchase' ? '+' : '-'}{transaction.amount}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {transaction.description}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Credit Usage Guide */}
        <div className="mt-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-8 text-white">
          <h3 className="text-2xl font-bold mb-4">How Credits Work</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold mb-2">Credit Usage:</h4>
              <ul className="space-y-1 text-blue-100">
                <li>• 1 credit = 1 basic AI query</li>
                <li>• 2-5 credits = Complex AI analysis</li>
                <li>• 10+ credits = Custom AI agent creation</li>
                <li>• Credits never expire</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Bonus Credits:</h4>
              <ul className="space-y-1 text-blue-100">
                <li>• Larger packs include bonus credits</li>
                <li>• Subscription members get monthly credits</li>
                <li>• Referral bonuses available</li>
                <li>• Special promotions throughout the year</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Credits;

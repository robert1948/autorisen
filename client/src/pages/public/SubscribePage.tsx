import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Footer from '../../components/Footer';

interface PricingTier {
  name: string;
  price: string;
  period: string;
  description: string;
  features: string[];
  cta: string;
  popular?: boolean;
}

const SubscribePage: React.FC = () => {
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');
  const handleOpenSupport = () => {
    console.log("Open support chat");
  };

  const pricingTiers: PricingTier[] = [
    {
      name: 'Free',
      price: '$0',
      period: 'forever',
      description: 'Perfect for getting started with AI automation',
      features: [
        '5 AI agents',
        '100 monthly executions',
        'Basic integrations',
        'Community support',
        'Standard templates'
      ],
      cta: 'Get Started Free'
    },
    {
      name: 'Pro',
      price: billingPeriod === 'monthly' ? '$29' : '$24',
      period: billingPeriod === 'monthly' ? 'per month' : 'per month, billed yearly',
      description: 'Ideal for individuals and small teams',
      features: [
        '50 AI agents',
        '2,500 monthly executions',
        'All integrations',
        'Priority support',
        'Advanced templates',
        'Custom workflows',
        'Analytics dashboard'
      ],
      cta: 'Start Pro Trial',
      popular: true
    },
    {
      name: 'Enterprise',
      price: billingPeriod === 'monthly' ? '$99' : '$79',
      period: billingPeriod === 'monthly' ? 'per month' : 'per month, billed yearly',
      description: 'For teams that need advanced features and support',
      features: [
        'Unlimited AI agents',
        'Unlimited executions',
        'Custom integrations',
        'Dedicated support',
        'White-label options',
        'Advanced security',
        'SLA guarantees',
        'On-premise deployment'
      ],
      cta: 'Contact Sales'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <div className="flex-1">
      {/* Header */}
      <div className="bg-white">
        <div className="max-w-7xl mx-auto py-16 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl">
              Choose Your Plan
            </h1>
            <p className="mt-4 text-xl text-gray-600">
              Scale your AI automation with flexible pricing that grows with you
            </p>
          </div>

          {/* Billing Period Toggle */}
          <div className="mt-8 flex justify-center">
            <div className="relative bg-gray-100 p-1 rounded-lg">
              <button
                onClick={() => setBillingPeriod('monthly')}
                className={`relative px-4 py-2 text-sm font-medium rounded-md transition-all ${
                  billingPeriod === 'monthly'
                    ? 'bg-white text-gray-900 shadow'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingPeriod('yearly')}
                className={`relative px-4 py-2 text-sm font-medium rounded-md transition-all ${
                  billingPeriod === 'yearly'
                    ? 'bg-white text-gray-900 shadow'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Yearly
                <span className="ml-1 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Save 20%
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          {pricingTiers.map((tier) => (
            <div
              key={tier.name}
              className={`relative bg-white rounded-lg shadow-lg overflow-hidden ${
                tier.popular ? 'ring-2 ring-blue-500' : ''
              }`}
            >
              {tier.popular && (
                <div className="absolute top-0 right-0 bg-blue-500 text-white px-4 py-1 text-sm font-medium">
                  Most Popular
                </div>
              )}
              
              <div className="p-8">
                <h3 className="text-2xl font-semibold text-gray-900">{tier.name}</h3>
                <p className="mt-2 text-gray-600">{tier.description}</p>
                
                <div className="mt-6">
                  <div className="flex items-baseline">
                    <span className="text-5xl font-extrabold text-gray-900">{tier.price}</span>
                    <span className="ml-1 text-xl font-semibold text-gray-500">/{tier.period.split(' ')[0]}</span>
                  </div>
                  {tier.period.includes('billed yearly') && (
                    <p className="mt-1 text-sm text-gray-500">{tier.period}</p>
                  )}
                </div>

                <ul className="mt-8 space-y-4">
                  {tier.features.map((feature, index) => (
                    <li key={index} className="flex items-start">
                      <svg className="h-5 w-5 text-green-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="ml-3 text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>

                <div className="mt-8">
                  {tier.name === 'Free' ? (
                    <Link
                      to="/auth/register"
                      className={`block w-full text-center px-6 py-3 border border-transparent rounded-md font-medium ${
                        tier.popular
                          ? 'text-white bg-blue-600 hover:bg-blue-700'
                          : 'text-blue-600 bg-blue-50 hover:bg-blue-100'
                      }`}
                    >
                      {tier.cta}
                    </Link>
                  ) : tier.name === 'Enterprise' ? (
                    <button className="block w-full text-center px-6 py-3 border border-gray-300 rounded-md font-medium text-gray-700 bg-white hover:bg-gray-50">
                      {tier.cta}
                    </button>
                  ) : (
                    <Link
                      to="/auth/register?plan=pro"
                      className="block w-full text-center px-6 py-3 border border-transparent rounded-md font-medium text-white bg-blue-600 hover:bg-blue-700"
                    >
                      {tier.cta}
                    </Link>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* FAQ Section */}
        <div className="mt-16">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-8">
            Frequently Asked Questions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Can I change my plan later?
              </h3>
              <p className="text-gray-600">
                Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                What happens to my data if I cancel?
              </h3>
              <p className="text-gray-600">
                Your data is yours. We provide export tools and give you 30 days to download your data.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Do you offer custom enterprise solutions?
              </h3>
              <p className="text-gray-600">
                Yes, we work with enterprises to create custom solutions that fit their specific needs.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Is there a free trial for Pro plans?
              </h3>
              <p className="text-gray-600">
                Yes, we offer a 14-day free trial for all Pro features. No credit card required.
              </p>
            </div>
          </div>
        </div>

        {/* Support CTA */}
        <div className="mt-16 bg-blue-50 rounded-lg p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Need help choosing the right plan?
          </h2>
          <p className="text-gray-600 mb-6">
            Our team is here to help you find the perfect solution for your needs.
          </p>
          <div className="space-x-4">
            <Link
              to="/contact"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              Contact Sales
            </Link>
            <Link
              to="/support"
              className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              Get Support
            </Link>
          </div>
        </div>
      </div>
      </div>
      <Footer onOpenSupport={handleOpenSupport} />
    </div>
  );
};

export default SubscribePage;
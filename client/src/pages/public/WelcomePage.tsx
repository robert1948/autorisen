import React from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import Footer from '../../components/Footer';

const Welcome: React.FC = () => {
  const [searchParams] = useSearchParams();
  const emailVerified = searchParams.get('email_verified');
  const userType = searchParams.get('type') || 'user';
  const handleOpenSupport = () => {
    console.log("Open support chat");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col">
      <div className="flex-1 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
          <div className="text-center">
          {/* Success Icon */}
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
            <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Welcome to CapeControl!
          </h1>
          
          {emailVerified === '1' && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
              <p className="text-sm text-green-800">
                ✅ Your email has been successfully verified!
              </p>
            </div>
          )}
          
          <p className="text-gray-600 mb-6">
            Your account is ready. Let&apos;s begin guided onboarding so you can configure
            workflows with clear controls from day one.
          </p>

          {/* Next Steps */}
          <div className="space-y-4">
            {userType === 'developer' ? (
              <>
                <Link
                  to="/onboarding/developer"
                  className="block w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                >
                  Start Guided Onboarding
                </Link>
                <Link
                  to="/how-it-works"
                  className="block w-full border border-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-50 transition-colors"
                >
                  See How It Works
                </Link>
              </>
            ) : (
              <>
                <Link
                  to="/onboarding/customer"
                  className="block w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                >
                  Start Guided Onboarding
                </Link>
                <Link
                  to="/how-it-works"
                  className="block w-full border border-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-50 transition-colors"
                >
                  See How It Works
                </Link>
              </>
            )}
          </div>

          {/* Additional Resources */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Links</h3>
            <div className="space-y-2 text-sm">
              <Link to="/docs" className="block text-blue-600 hover:text-blue-800">
                📚 Documentation
              </Link>
              <Link to="/support" className="block text-blue-600 hover:text-blue-800">
                💬 Support
              </Link>
              <Link to="/about" className="block text-blue-600 hover:text-blue-800">
                ℹ️ About CapeControl
              </Link>
            </div>
          </div>
          </div>
        </div>
      </div>
      <Footer onOpenSupport={handleOpenSupport} />
    </div>
  );
};

export default Welcome;
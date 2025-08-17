import { useEffect, useState } from "react";
import axios from "axios";
import OnboardingChecklist from "../components/onboarding/OnboardingChecklist";
import useOnboarding from "../hooks/useOnboarding";

function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { isComplete, progress } = useOnboarding();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError("");

      try {
        const response = await axios.get("/api/me");
        setData(response.data);
      } catch (err) {
        setError("Failed to load user data.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="container-mobile mt-16 lg:mt-20">
      <div className="mb-8">
        <h2 className="text-2xl sm:text-3xl font-bold mb-4 text-center lg:text-left">Welcome to Your Dashboard</h2>
        
        {!isComplete && (
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-400 rounded-xl p-6 mb-6 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-bold text-blue-800">Getting Started</h3>
              <span className="bg-blue-100 text-blue-800 text-sm font-bold px-3 py-1 rounded-full">
                {progress.percentage}% Complete
              </span>
            </div>
            <p className="text-blue-700 text-sm leading-relaxed">
              Complete your onboarding to unlock the full potential of CapeControl
            </p>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white border border-gray-200 rounded-2xl shadow-lg p-6 lg:p-8">
            <div className="flex items-center mb-6">
              <div className="bg-blue-600 rounded-full p-2 mr-3">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900">User Information</h3>
            </div>

            {loading && (
              <div className="flex items-center justify-center py-8">
                <svg className="animate-spin h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span className="ml-3 text-blue-600 font-medium">Loading your information...</span>
              </div>
            )}
            {error && (
              <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-lg">
                <p className="text-red-700 font-medium">{error}</p>
              </div>
            )}

            {data && (
              <div className="space-y-4">
                <div className="flex justify-between items-center py-3 border-b border-gray-100">
                  <span className="font-semibold text-gray-600">Name:</span>
                  <span className="text-gray-900 font-medium">{data.name}</span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-gray-100">
                  <span className="font-semibold text-gray-600">Email:</span>
                  <span className="text-gray-900 font-medium">{data.email}</span>
                </div>
                <div className="flex justify-between items-center py-3">
                  <span className="font-semibold text-gray-600">Status:</span>
                  <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold">
                    ✓ Active
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="bg-white border border-gray-200 rounded-2xl shadow-lg p-6 lg:p-8 mt-6">
            <div className="flex items-center mb-6">
              <div className="bg-purple-600 rounded-full p-2 mr-3">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900">Quick Actions</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button className="btn-mobile bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all duration-200 p-4 text-left shadow-md hover:shadow-lg">
                <div className="flex items-center">
                  <span className="text-2xl mr-3">🚀</span>
                  <div>
                    <div className="font-bold">Launch New Agent</div>
                    <div className="text-blue-100 text-sm">Start automating</div>
                  </div>
                </div>
              </button>
              <button className="btn-mobile bg-gradient-to-r from-green-600 to-green-700 text-white rounded-xl hover:from-green-700 hover:to-green-800 transition-all duration-200 p-4 text-left shadow-md hover:shadow-lg">
                <div className="flex items-center">
                  <span className="text-2xl mr-3">📊</span>
                  <div>
                    <div className="font-bold">View Analytics</div>
                    <div className="text-green-100 text-sm">Track performance</div>
                  </div>
                </div>
              </button>
              <button className="btn-mobile bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-xl hover:from-purple-700 hover:to-purple-800 transition-all duration-200 p-4 text-left shadow-md hover:shadow-lg">
                <div className="flex items-center">
                  <span className="text-2xl mr-3">⚙️</span>
                  <div>
                    <div className="font-bold">Manage Settings</div>
                    <div className="text-purple-100 text-sm">Customize experience</div>
                  </div>
                </div>
              </button>
              <button className="btn-mobile bg-gradient-to-r from-orange-600 to-orange-700 text-white rounded-xl hover:from-orange-700 hover:to-orange-800 transition-all duration-200 p-4 text-left shadow-md hover:shadow-lg">
                <div className="flex items-center">
                  <span className="text-2xl mr-3">💬</span>
                  <div>
                    <div className="font-bold">Get Support</div>
                    <div className="text-orange-100 text-sm">We're here to help</div>
                  </div>
                </div>
              </button>
            </div>
          </div>
        </div>

        <div className="lg:col-span-1">
          {/* Onboarding Checklist */}
          {!isComplete && <OnboardingChecklist />}
          
          {/* Recent Activity */}
          <div className="bg-white border rounded-xl shadow p-6 mt-6">
            <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-2 text-gray-600">
                <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                Account created successfully
              </div>
              <div className="flex items-center gap-2 text-gray-600">
                <span className="w-2 h-2 bg-blue-400 rounded-full"></span>
                Dashboard accessed
              </div>
              <div className="flex items-center gap-2 text-gray-600">
                <span className="w-2 h-2 bg-purple-400 rounded-full"></span>
                CapeAI assistant activated
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

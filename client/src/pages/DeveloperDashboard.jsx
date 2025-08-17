import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function DeveloperDashboard() {
  const [user, setUser] = useState(null);
  const [earningsData, setEarningsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [earningsLoading, setEarningsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          navigate("/login");
          return;
        }

        const response = await fetch("/api/user/profile", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
          
          // Fetch earnings data for developers
          if (userData.role === 'developer' || userData.role === 'DEVELOPER') {
            await fetchEarningsData(token);
          }
        } else {
          navigate("/login");
        }
      } catch (error) {
        console.error("Error fetching user data:", error);
        navigate("/login");
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [navigate]);

  const fetchEarningsData = async (token) => {
    try {
      setEarningsLoading(true);
      const response = await fetch("/api/developer/earnings/summary", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const result = await response.json();
        setEarningsData(result.data);
      } else {
        console.warn("Could not fetch earnings data - using fallback");
        // Set fallback data if API is not available
        setEarningsData({
          total_earnings: { total_earned: { formatted: "$0.00" }, pending_payout: { formatted: "$0.00" } },
          month_earnings: { formatted: "$0.00" },
          week_earnings: { formatted: "$0.00" },
          performance_overview: { total_customers: 0, avg_transaction: { formatted: "$0.00" }, satisfaction: 0 }
        });
      }
    } catch (error) {
      console.error("Error fetching earnings data:", error);
      // Set fallback data on error
      setEarningsData({
        total_earnings: { total_earned: { formatted: "$0.00" }, pending_payout: { formatted: "$0.00" } },
        month_earnings: { formatted: "$0.00" },
        week_earnings: { formatted: "$0.00" },
        performance_overview: { total_customers: 0, avg_transaction: { formatted: "$0.00" }, satisfaction: 0 }
      });
    } finally {
      setEarningsLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading developer dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Developer Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Welcome back, {user?.name || user?.email || "Developer"}! 
            Manage your AI agents and track your earnings.
          </p>
        </div>

        {/* Earnings Overview */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Earnings</p>
                <p className="text-2xl font-bold text-green-600">
                  {earningsLoading ? (
                    <div className="animate-pulse bg-gray-200 h-6 w-20 rounded"></div>
                  ) : (
                    earningsData?.total_earnings?.total_earned?.formatted || "$0.00"
                  )}
                </p>
              </div>
              <div className="text-green-600 text-2xl">💰</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">This Month</p>
                <p className="text-2xl font-bold text-blue-600">
                  {earningsLoading ? (
                    <div className="animate-pulse bg-gray-200 h-6 w-16 rounded"></div>
                  ) : (
                    earningsData?.month_earnings?.formatted || "$0.00"
                  )}
                </p>
              </div>
              <div className="text-blue-600 text-2xl">📈</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Pending Payout</p>
                <p className="text-2xl font-bold text-orange-600">
                  {earningsLoading ? (
                    <div className="animate-pulse bg-gray-200 h-6 w-16 rounded"></div>
                  ) : (
                    earningsData?.total_earnings?.pending_payout?.formatted || "$0.00"
                  )}
                </p>
              </div>
              <div className="text-orange-600 text-2xl">⏳</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Customers</p>
                <p className="text-2xl font-bold text-purple-600">
                  {earningsLoading ? (
                    <div className="animate-pulse bg-gray-200 h-6 w-12 rounded"></div>
                  ) : (
                    earningsData?.performance_overview?.total_customers || 0
                  )}
                </p>
              </div>
              <div className="text-purple-600 text-2xl">👥</div>
            </div>
          </div>
        </div>

        {/* Revenue Information */}
        <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-xl p-6 mb-8">
          <div className="flex items-center mb-4">
            <div className="bg-green-500 rounded-full p-2 mr-3">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-green-800">Revenue Details</h3>
          </div>
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-green-700 font-medium">Revenue Share</p>
              <p className="text-green-600">You earn 80% of every sale</p>
            </div>
            <div>
              <p className="text-blue-700 font-medium">Payout Schedule</p>
              <p className="text-blue-600">Weekly automatic payouts</p>
            </div>
            <div>
              <p className="text-purple-700 font-medium">Next Payout</p>
              <p className="text-purple-600">
                {earningsData?.next_payout ? new Date(earningsData.next_payout).toLocaleDateString() : "TBD"}
              </p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer">
            <div className="text-blue-600 text-3xl mb-4">🛠️</div>
            <h3 className="text-xl font-semibold mb-2">Create New Agent</h3>
            <p className="text-gray-600 text-sm">
              Build a new AI agent using our developer tools and templates.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer">
            <div className="text-green-600 text-3xl mb-4">📚</div>
            <h3 className="text-xl font-semibold mb-2">Documentation</h3>
            <p className="text-gray-600 text-sm">
              Access comprehensive guides and API documentation.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer">
            <div className="text-purple-600 text-3xl mb-4">🏪</div>
            <h3 className="text-xl font-semibold mb-2">Marketplace</h3>
            <p className="text-gray-600 text-sm">
              Publish and manage your agents in the marketplace.
            </p>
          </div>
        </div>

        {/* Getting Started */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold mb-4">Getting Started</h2>
          <div className="space-y-4">
            <div className="flex items-center space-x-4 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
              <div className="text-blue-600 text-2xl">📋</div>
              <div>
                <div className="font-semibold">Complete Your Developer Profile</div>
                <div className="text-sm text-gray-600">
                  Add your portfolio, skills, and payment information to start earning.
                </div>
              </div>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 ml-auto">
                Complete Profile
              </button>
            </div>

            <div className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
              <div className="text-gray-400 text-2xl">🚀</div>
              <div>
                <div className="font-semibold text-gray-500">Create Your First Agent</div>
                <div className="text-sm text-gray-400">
                  Use our SDK and templates to build your first AI agent.
                </div>
              </div>
              <button className="bg-gray-300 text-gray-500 px-4 py-2 rounded-lg cursor-not-allowed ml-auto">
                Coming Soon
              </button>
            </div>

            <div className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
              <div className="text-gray-400 text-2xl">💳</div>
              <div>
                <div className="font-semibold text-gray-500">Setup Payment Method</div>
                <div className="text-sm text-gray-400">
                  Configure how you'll receive payments from agent sales.
                </div>
              </div>
              <button className="bg-gray-300 text-gray-500 px-4 py-2 rounded-lg cursor-not-allowed ml-auto">
                Coming Soon
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

import { Link } from "react-router-dom";

export default function Platform() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 pt-20">
      <div className="max-w-6xl mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            CapeControl Platform
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Enterprise-grade AI platform built for scale, security, and seamless integration
          </p>
        </div>

        {/* Platform Overview */}
        <section className="mb-16">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">How We Bring This Vision to Life</h2>
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-semibold text-blue-600 mb-3">Client-Centric Platform Design</h3>
                <p className="text-gray-700">
                  Upon registration, clients are greeted by an intuitive interface where they can outline their objectives, challenges, or desired outcomes. Our secure, role-based registration system instantly creates personalized accounts with JWT authentication, ensuring immediate access to AI-agent capabilities.
                </p>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-blue-600 mb-3">Showcasing AI in Action</h3>
                <p className="text-gray-700">
                  Every interaction on the platform—from onboarding to solution delivery—demonstrates the capabilities of our AI-agents. Whether it's natural language processing, predictive analytics, or adaptive problem-solving, clients experience the power of AI in real time.
                </p>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-blue-600 mb-3">Continuous Evolution</h3>
                <p className="text-gray-700">
                  CapeControl is built on a foundation of iterative improvement. Our AI-agents learn from every user interaction, industry trend, and technological advancement, ensuring that the platform remains at the forefront of innovation.
                </p>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-blue-600 mb-3">Scalable and Inclusive Solutions</h3>
                <p className="text-gray-700">
                  Our platform is designed to serve a wide range of users, from individuals with minimal technical knowledge to large organizations with complex needs. Flexible pricing models ensure accessibility for all.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Technical Architecture */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Technical Foundation</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
              <div className="text-3xl mb-4">🔒</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Enterprise-Grade Security</h3>
              <ul className="text-gray-700 space-y-2">
                <li>• JWT authentication with refresh tokens</li>
                <li>• Role-based access controls</li>
                <li>• Comprehensive audit logging</li>
                <li>• Secure password management</li>
                <li>• Production-grade encryption</li>
              </ul>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
              <div className="text-3xl mb-4">🏗️</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Scalable Architecture</h3>
              <ul className="text-gray-700 space-y-2">
                <li>• PostgreSQL with v2 database schemas</li>
                <li>• RESTful API design</li>
                <li>• Microservices architecture</li>
                <li>• Auto-scaling infrastructure</li>
                <li>• Load balancing and redundancy</li>
              </ul>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-purple-500">
              <div className="text-3xl mb-4">🚀</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Production-Ready</h3>
              <ul className="text-gray-700 space-y-2">
                <li>• 24/7 availability monitoring</li>
                <li>• Continuous integration/deployment</li>
                <li>• Zero-downtime deployments</li>
                <li>• Automated testing pipeline</li>
                <li>• Performance optimization</li>
              </ul>
            </div>
          </div>
        </section>

        {/* API Features */}
        <section className="mb-16">
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-8 rounded-lg">
            <h2 className="text-3xl font-bold mb-6">API-First Design</h2>
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-semibold mb-4">Enhanced Authentication API</h3>
                <div className="bg-black/20 p-4 rounded-lg font-mono text-sm">
                  <div className="text-green-300">POST /api/enhanced/register</div>
                  <div className="text-green-300">POST /api/enhanced/login</div>
                  <div className="text-green-300">GET /api/enhanced/me</div>
                  <div className="text-green-300">POST /api/enhanced/refresh</div>
                  <div className="text-yellow-300">// JWT + Role-based access</div>
                </div>
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-4">Developer Revenue Tracking</h3>
                <div className="bg-black/20 p-4 rounded-lg font-mono text-sm">
                  <div className="text-green-300">GET /api/enhanced/developer/earnings</div>
                  <div className="text-green-300">POST /api/enhanced/developer/agents</div>
                  <div className="text-green-300">GET /api/enhanced/analytics</div>
                  <div className="text-yellow-300">// Automated payouts & metrics</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* User Roles */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Built for Every User Type</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center bg-white p-6 rounded-lg shadow-md">
              <div className="text-4xl mb-4">👤</div>
              <h3 className="text-xl font-semibold text-blue-600 mb-3">Customers</h3>
              <p className="text-gray-700 mb-4">
                Access AI-agents, track usage, manage subscriptions, and integrate with business workflows.
              </p>
              <Link to="/register" className="inline-block bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors">
                Start Free Trial
              </Link>
            </div>

            <div className="text-center bg-white p-6 rounded-lg shadow-md">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-xl font-semibold text-purple-600 mb-3">Developers</h3>
              <p className="text-gray-700 mb-4">
                Create AI-agents, track earnings, manage revenue sharing, and access developer analytics.
              </p>
              <Link to="/developers" className="inline-block bg-purple-600 text-white py-2 px-4 rounded hover:bg-purple-700 transition-colors">
                Join Developer Program
              </Link>
            </div>

            <div className="text-center bg-white p-6 rounded-lg shadow-md">
              <div className="text-4xl mb-4">⚙️</div>
              <h3 className="text-xl font-semibold text-green-600 mb-3">Administrators</h3>
              <p className="text-gray-700 mb-4">
                Manage users, monitor system health, configure settings, and access comprehensive analytics.
              </p>
              <div className="inline-block bg-green-600 text-white py-2 px-4 rounded opacity-75">
                Enterprise Only
              </div>
            </div>
          </div>
        </section>

        {/* Status Dashboard */}
        <section className="mb-16">
          <div className="bg-green-50 border border-green-200 p-6 rounded-lg">
            <h2 className="text-2xl font-bold text-green-800 mb-4">✅ System Status: Operational</h2>
            <div className="grid md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">99.9%</div>
                <div className="text-sm text-green-700">Uptime</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">&lt;100ms</div>
                <div className="text-sm text-green-700">API Response</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">5</div>
                <div className="text-sm text-green-700">Active Users</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">Live</div>
                <div className="text-sm text-green-700">Enhanced Auth</div>
              </div>
            </div>
          </div>
        </section>

        {/* Call to Action */}
        <section className="text-center">
          <div className="bg-gray-900 text-white p-12 rounded-lg">
            <h2 className="text-3xl font-bold mb-4">Ready to Build with CapeControl?</h2>
            <p className="text-xl mb-8 opacity-90">
              Experience the power of our enterprise-grade AI platform today.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register"
                className="bg-blue-600 hover:bg-blue-700 text-white py-3 px-8 rounded-lg font-semibold transition-colors"
              >
                Get Started Free
              </Link>
              <Link
                to="/docs"
                className="border-2 border-white text-white hover:bg-white hover:text-gray-900 py-3 px-8 rounded-lg font-semibold transition-colors"
              >
                View Documentation
              </Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

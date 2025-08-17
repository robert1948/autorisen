import { Link } from "react-router-dom";

export default function About() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-12 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
            About Cape Control
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Revolutionizing local business management with powerful AI agents, seamless automation, and real-time insights.
          </p>
        </div>

        {/* Mission Section */}
        <section className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-lg mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Our Mission
          </h2>
          <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
            Cape Control empowers local and regional businesses with advanced AI solutions—delivering the speed, intelligence,
            and automation traditionally reserved for large enterprises. Our platform enables smarter workflows,
            data-driven decisions, and remarkable customer service—all with simplicity and elegance.
          </p>
        </section>

        {/* Why Cape Control */}
        <section className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-lg mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Why Cape Control?
          </h2>
          <ul className="list-disc list-inside text-gray-600 dark:text-gray-300 space-y-2">
            <li>✅ Purpose-built for SMEs in emerging markets</li>
            <li>✅ AI agents that learn and adapt to your business needs</li>
            <li>✅ Streamlined setup—no tech skills required</li>
            <li>✅ Live usage analytics, performance dashboards, and reporting</li>
            <li>✅ Secure and privacy-respecting architecture</li>
          </ul>
        </section>

        {/* Features Section */}
        <section className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-lg mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
            What We Offer
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <FeatureItem title="AI Agents" description="Intelligent, context-aware assistants for customer service, appointments, and task automation." />
              <FeatureItem title="Performance Analytics" description="Real-time insights to help you make faster, smarter business decisions." />
            </div>
            <div className="space-y-4">
              <FeatureItem title="Custom Integrations" description="Connect to your existing CRM, POS, or cloud tools without breaking your workflow." />
              <FeatureItem title="24/7 Support" description="Dedicated team ready to assist—via chat, email, or phone." />
            </div>
          </div>
        </section>

        {/* Technology Section */}
        <section className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-lg mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Built with Modern Technology
          </h2>
          <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-4">
            Cape Control leverages a modern, modular stack built for performance and security. 
            With React for dynamic user experiences, FastAPI for scalable APIs, and PostgreSQL for reliable storage, 
            our infrastructure is robust and production-ready.
          </p>
          <div className="flex flex-wrap gap-2">
            {["React", "Vite", "Tailwind CSS", "FastAPI", "PostgreSQL", "Redis", "OpenAI", "Cloudflare", "Docker", "Heroku"].map((tech) => (
              <span
                key={tech}
                className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-sm rounded-full"
              >
                {tech}
              </span>
            ))}
          </div>
        </section>

        {/* Trust Section */}
        <section className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-lg mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Security & Trust
          </h2>
          <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
            Your data is encrypted, your users are protected, and your workflows are safe. 
            Cape Control follows industry best practices for API security, authentication, and data protection—giving you peace of mind as your business grows.
          </p>
        </section>

        {/* CTA Section */}
        <section className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-8 text-center text-white">
          <h2 className="text-2xl font-bold mb-4">Ready to Transform Your Business?</h2>
          <p className="mb-6 opacity-90">
            Start your journey today with Cape Control and experience the power of adaptive automation.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
            >
              Get Started
            </Link>
            <Link
              to="/vision"
              className="border border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:bg-opacity-10 transition-colors"
            >
              Learn More
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}

// Subcomponent for reusability
function FeatureItem({ title, description }) {
  return (
    <div className="flex items-start space-x-3">
      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
      <div>
        <h3 className="font-semibold text-gray-900 dark:text-white">{title}</h3>
        <p className="text-gray-600 dark:text-gray-300 text-sm">{description}</p>
      </div>
    </div>
  );
}

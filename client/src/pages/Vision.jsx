import { Link } from "react-router-dom";

export default function Vision() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white pt-20">
      <div className="max-w-4xl mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            CapeControl Vision
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Empowering the world through accessible artificial intelligence
          </p>
        </div>

        {/* Our Purpose */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Purpose</h2>
          <p className="text-lg text-gray-700 leading-relaxed">
            At CapeControl, we envision a world where the power of artificial intelligence is accessible to everyone, regardless of technical expertise or resources. Our platform serves as a bridge between human ambition and technological possibility, offering a seamless, intuitive experience that transforms ideas into reality. By harnessing the capabilities of advanced AI-agents, we aim to redefine how businesses and individuals solve problems, optimize workflows, and innovate in an ever-changing global landscape.
          </p>
        </section>

        {/* Core Pillars */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Core Pillars of Our Vision</h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-semibold text-blue-600 mb-3">Empowerment Through Accessibility</h3>
              <p className="text-gray-700">
                We are committed to democratizing AI, enabling users from startups to enterprises, and from solo entrepreneurs to creative individuals, to leverage cutting-edge technology. Our platform allows clients to register, articulate their unique requirements, and receive personalized, actionable guidance—making AI an enabler of success rather than a barrier.
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-semibold text-blue-600 mb-3">Intelligence That Evolves</h3>
              <p className="text-gray-700">
                Our AI-agents are designed to go beyond automation. They understand context, anticipate needs, and continuously learn from user interactions and evolving data. This intelligence ensures that every solution is tailored, relevant, and aligned with the client's goals, whether it's streamlining operations, enhancing decision-making, or sparking innovation.
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-semibold text-blue-600 mb-3">Adaptability for a Changing World</h3>
              <p className="text-gray-700">
                In a digital landscape defined by rapid change, CapeControl's platform is built to evolve. Our AI-agents dynamically adapt to shifting user needs, market trends, and technological advancements, ensuring that clients remain agile and competitive. This adaptability positions our users as leaders in their industries, ready to seize new opportunities.
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-semibold text-blue-600 mb-3">Simplicity in Complexity</h3>
              <p className="text-gray-700">
                We believe that advanced technology should be intuitive and approachable. CapeControl's platform is designed with user-friendly interfaces and streamlined processes, allowing clients to engage with AI effortlessly. From registration to solution delivery, every interaction is clear, concise, and focused on delivering value without unnecessary complexity.
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-semibold text-blue-600 mb-3">Productivity and Innovation Unleashed</h3>
              <p className="text-gray-700">
                Our AI-agents are catalysts for efficiency and creativity. By automating repetitive tasks, providing deep insights, and offering innovative approaches to challenges, we enable clients to focus on what matters most—strategic growth and bold ideas. CapeControl empowers users to achieve measurable productivity gains while exploring new possibilities for their businesses or personal projects.
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-semibold text-blue-600 mb-3">A Living Demonstration of AI Excellence</h3>
              <p className="text-gray-700">
                The CapeControl platform is more than a service—it's a showcase of what AI can achieve. From the moment clients register, they experience the power of our AI-agents firsthand. The platform's functionality, responsiveness, and intelligence serve as a testament to the transformative potential of our solutions, inspiring confidence and trust in our ability to deliver.
              </p>
            </div>
          </div>
        </section>

        {/* Technical Foundation */}
        <section className="mb-16 bg-gradient-to-r from-blue-50 to-indigo-50 p-8 rounded-lg">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Technical Foundation: Built for Excellence</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-blue-600 mb-2">🔒 Enterprise-Grade Security</h3>
              <p className="text-gray-700 text-sm">
                Every user interaction is protected by advanced JWT authentication, role-based access controls, and comprehensive audit logging.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-blue-600 mb-2">🏗️ Scalable Architecture</h3>
              <p className="text-gray-700 text-sm">
                Built on PostgreSQL with enhanced v2 database schemas, supporting seamless user management for customers, developers, and administrators.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-blue-600 mb-2">💰 Developer Revenue Platform</h3>
              <p className="text-gray-700 text-sm">
                Built-in earnings system that tracks AI-agent performance, revenue sharing, and automated payouts.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-blue-600 mb-2">🚀 Production-Ready Infrastructure</h3>
              <p className="text-gray-700 text-sm">
                Deployed on enterprise cloud infrastructure with continuous integration, automated testing, and zero-downtime deployments.
              </p>
            </div>
          </div>
        </section>

        {/* Call to Action */}
        <section className="text-center bg-blue-600 text-white p-12 rounded-lg">
          <h2 className="text-3xl font-bold mb-4">Ready to Experience the Future?</h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of users who are already transforming their businesses with CapeControl AI-agents.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="bg-white text-blue-600 hover:bg-gray-100 py-3 px-8 rounded-lg font-semibold transition-colors"
            >
              Get Started Free
            </Link>
            <Link
              to="/platform"
              className="border-2 border-white text-white hover:bg-white hover:text-blue-600 py-3 px-8 rounded-lg font-semibold transition-colors"
            >
              Explore Platform
            </Link>
          </div>
        </section>

        {/* Quote */}
        <section className="text-center mt-16">
          <blockquote className="text-2xl font-medium text-gray-800 italic">
            "CapeControl AI-Agents: Where intelligence meets impact, and possibilities become realities."
          </blockquote>
        </section>
      </div>
    </div>
  );
}

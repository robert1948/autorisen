import React from 'react';
import { Link } from 'react-router-dom';
import TopNav from './nav/TopNav';
import Footer from './Footer';

const HomePage: React.FC = () => {
  const handleOpenSupport = () => {
    console.log("Open support chat");
    // In a full implementation, this would toggle the chat modal
  };

  return (
    <div className="min-h-screen flex flex-col font-sans text-gray-800">
      <TopNav onOpenSupport={handleOpenSupport} />

      {/* Hero Section */}
      <section id="home" className="bg-[#0B1120] text-white text-left md:text-center py-12 md:py-24 px-10 md:px-5">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
            Governed AI Workflows for Compliance-Heavy Operations
          </h1>
          <p className="text-xl md:text-2xl mb-8 opacity-90">
            CapeControl helps businesses execute multi-step operational work with advanced AI agents, approved-source retrieval, evidence-backed outputs, and human-guided controls designed for trust-sensitive workflows.
          </p>
          <div className="flex flex-col md:flex-row justify-center gap-4">
            <Link 
              to="/how-it-works" 
              className="block bg-[#ff6b6b] hover:bg-[#ff5252] text-white px-8 py-4 rounded-lg font-bold text-lg transition-colors shadow-lg"
            >
              Book a Governance Walkthrough
            </Link>
            <button
              type="button"
              onClick={handleOpenSupport}
              className="block bg-white/10 hover:bg-white/20 text-white px-8 py-4 rounded-lg font-bold text-lg transition-colors shadow-lg backdrop-blur-sm"
            >
              Start Guided Onboarding
            </button>
          </div>
        </div>
      </section>

      {/* The Alchemy of AI */}
      <section id="features" className="bg-[#0B1120] lg:bg-white py-12 md:py-20 px-10 md:px-5 max-w-7xl mx-auto">
        <div className="text-left lg:text-center mb-12 md:mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-white lg:text-gray-800 mb-4">Trust by Design, Not by Assumption.</h2>
          <p className="text-2xl text-gray-300 lg:text-gray-600 max-w-3xl mx-auto">
            Agents that move work forward. Evidence you can stand behind. Governance built in for teams that need speed with control.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12 md:gap-10">
          <div className="flex flex-col items-center text-left lg:text-center gap-6">
            <img 
              src="/images/feature-ai-anxiety.webp" 
              alt="AI Anxiety Reframed" 
              fetchPriority="high"
              width={400}
              height={225}
              className="rounded-xl shadow-md w-full h-auto aspect-video object-cover shrink-0" 
            />
            <div>
              <h3 className="text-3xl font-bold text-[#667eea] mb-4">Agents That Act</h3>
              <p className="text-gray-300 lg:text-gray-600 text-2xl leading-relaxed">Agents understand workflow goals and context, then guide users through multi-step operational tasks.</p>
            </div>
          </div>
          <div className="flex flex-col items-center text-left lg:text-center gap-6">
            <img 
              src="/images/feature-magic-queries.webp" 
              alt="Magical Queries" 
              loading="lazy"
              width={400}
              height={225}
              className="rounded-xl shadow-md w-full h-auto aspect-video object-cover shrink-0" 
            />
            <div>
              <h3 className="text-3xl font-bold text-[#764ba2] mb-4">Evidence You Can Verify</h3>
              <p className="text-gray-300 lg:text-gray-600 text-2xl leading-relaxed">Retrieval is restricted to approved business knowledge, giving teams clear source boundaries and review-ready records.</p>
            </div>
          </div>
          <div className="flex flex-col items-center text-left lg:text-center gap-6">
            <img 
              src="/images/feature-compliant-agents.webp" 
              alt="Compliant Agents" 
              loading="lazy"
              width={400}
              height={225}
              className="rounded-xl shadow-md w-full h-auto aspect-video object-cover shrink-0" 
            />
            <div>
              <h3 className="text-3xl font-bold text-[#ff6b6b] mb-4">Control Where It Matters</h3>
              <p className="text-gray-300 lg:text-gray-600 text-2xl leading-relaxed">Agents recommend next actions and pause at approval points for escalation and accountable decision-making.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Reverse Benchmark */}
      <section id="experiences" className="bg-gray-50 py-12 md:py-20 px-5">
        <div className="max-w-7xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4">Built to Strengthen Core Business Functions</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-12 md:mb-16">
            Operational execution, compliance, and reporting in one governed workflow layer.
          </p>

          <div className="grid md:grid-cols-3 gap-8 md:gap-8 text-left">
            <div className="bg-white p-8 md:p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
              <h3 className="text-2xl md:text-3xl font-bold text-[#667eea] mb-4">Operations Support</h3>
              <p className="text-gray-600 text-lg md:text-xl leading-relaxed">Keep routine work moving with guided task handoffs, role-aware context, and recommended next actions.</p>
            </div>
            <div className="bg-white p-8 md:p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
              <h3 className="text-2xl md:text-3xl font-bold text-[#764ba2] mb-4">Compliance Workflows</h3>
              <p className="text-gray-600 text-lg md:text-xl leading-relaxed">Apply approvals, escalation, and evidence requirements where risk and accountability matter most.</p>
            </div>
            <div className="bg-white p-8 md:p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
              <h3 className="text-2xl md:text-3xl font-bold text-[#ff6b6b] mb-4">Reporting and Documentation</h3>
              <p className="text-gray-600 text-lg md:text-xl leading-relaxed">Produce source-grounded records and summaries that are easier to review, share, and audit.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Explore the Magic */}
      <section className="py-20 px-5 max-w-5xl mx-auto text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4">Why Teams Trust CapeControl</h2>
        <p className="text-xl text-gray-600 mb-12">
          High-trust AI starts with clear boundaries: approved-source retrieval, human approval points, and traceable activity.
        </p>

        <div className="flex flex-col md:flex-row justify-center items-center gap-8 mb-12">
          <div className="w-64 h-64 rounded-full bg-[#667eea] flex flex-col items-center justify-center text-white text-2xl font-bold shadow-xl">
            <span>1</span>
            <span>Approved</span>
            <span>Sources</span>
          </div>
          <div className="w-64 h-64 rounded-full bg-[#ff6b6b] flex flex-col items-center justify-center text-white text-2xl font-bold shadow-xl">
            <span>2</span>
            <span>Human</span>
            <span>Checkpoints</span>
          </div>
        </div>

        <p className="text-lg text-gray-700">
          Guided onboarding helps teams understand agent behavior, approval logic, and escalation paths with confidence.
        </p>
      </section>

      {/* The Human Spark */}
      <section className="bg-gradient-to-br from-[#ff6b6b]/20 to-[#ff6b6b]/5 py-20 px-5 text-center">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-800 mb-6">Advanced Agents. Clear Boundaries.</h2>
          <p className="text-xl text-gray-800 mb-8">
            CapeControl is designed so agents can be useful without becoming opaque. Permissions, approvals, escalation ownership, and review points keep critical work accountable.
          </p>
          <div className="inline-block bg-white p-2 rounded-xl shadow-md">
            <button onClick={handleOpenSupport} className="block text-[#667eea] px-8 py-3 font-bold text-lg hover:bg-gray-50 rounded-lg transition-colors">
              Talk to a Workflow Specialist
            </button>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 px-5 text-center bg-white">
        <h2 className="text-3xl md:text-4xl font-bold text-gray-800 mb-6">Ready to Deploy Governed Workflows With Confidence?</h2>
        <p className="text-xl text-gray-600 mb-10">Start with one critical workflow and show measurable trust gains through evidence, approvals, and traceable execution.</p>
        
        <Link 
          to="/how-it-works" 
          className="inline-block bg-[#667eea] hover:bg-[#5a6fd6] text-white px-10 py-4 rounded-lg font-bold text-lg shadow-lg transition-all transform hover:-translate-y-1"
        >
          Book a Trust-First Demo
        </Link>
        
        <p className="mt-10 text-sm text-gray-400">
          Built for compliance-heavy teams | © 2025 CapeControl
        </p>
      </section>

      {/* Quote Section */}
      <div className="bg-[#333] text-white text-center py-6 px-4">
        <p className="text-lg italic opacity-80">"Useful autonomy. Accountable execution." – CapeControl trust-by-design principle</p>
      </div>

      <Footer onOpenSupport={handleOpenSupport} />
    </div>
  );
};

export default HomePage;

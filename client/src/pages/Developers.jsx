import { Link } from "react-router-dom";

export default function Developers() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 pt-20">
      <div className="max-w-6xl mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            CapeControl Developer Platform
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Independent contractor program for AI module development with revenue-based compensation
          </p>
        </div>

        {/* Important Notice */}
        <section className="mb-16">
          <div className="bg-amber-50 border border-amber-200 p-8 rounded-lg">
            <h2 className="text-2xl font-bold text-amber-800 mb-4">⚠️ Important: Revenue-Only Payment Model</h2>
            <p className="text-amber-800 mb-4">
              <strong>Developer payments are strictly tied to actual customer revenue.</strong> You earn 30% of confirmed 
              customer payments attributable to your AI modules only after CapeControl receives payment from customers.
            </p>
            <div className="bg-white p-4 rounded border border-amber-300">
              <ul className="text-sm text-gray-700 space-y-2">
                <li>• <strong>No guaranteed payments:</strong> Payment depends entirely on customer revenue generation</li>
                <li>• <strong>Freemium = No payment:</strong> Free usage generates zero compensation until monetized</li>
                <li>• <strong>Work-for-hire:</strong> All code and IP belongs to CapeControl upon creation</li>
                <li>• <strong>Independent contractor:</strong> You are responsible for your own taxes and insurance</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Revenue Model Explanation */}
        <section className="mb-16">
          <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white p-12 rounded-lg">
            <h2 className="text-3xl font-bold mb-6 text-center">Revenue-Based Compensation Model</h2>
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-semibold mb-4">How Payment Works</h3>
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-white text-green-600 rounded-full flex items-center justify-center font-bold">1</div>
                    <p className="text-sm">You develop AI module as independent contractor</p>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-white text-green-600 rounded-full flex items-center justify-center font-bold">2</div>
                    <p className="text-sm">CapeControl deploys your module to paying customers</p>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-white text-green-600 rounded-full flex items-center justify-center font-bold">3</div>
                    <p className="text-sm">Customer pays CapeControl for using your module</p>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-white text-green-600 rounded-full flex items-center justify-center font-bold">4</div>
                    <p className="text-sm">You invoice for 30% of confirmed customer revenue</p>
                  </div>
                </div>
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-4">Payment Conditions</h3>
                <div className="bg-white/10 p-6 rounded-lg">
                  <ul className="text-sm space-y-3">
                    <li>• Payment only after customer revenue received</li>
                    <li>• 30% of net customer revenue attributable to your module</li>
                    <li>• Monthly payment schedule within 30 days of invoice approval</li>
                    <li>• Minimum payout threshold: $50 USD</li>
                    <li>• No work delivery guarantee = No payment guarantee</li>
                    <li>• Subject to customer refunds and chargebacks</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Developer Requirements & Obligations */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Developer Requirements</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md border">
              <div className="text-3xl mb-4">👨‍💼</div>
              <h3 className="text-xl font-semibold text-red-600 mb-3">Independent Contractor Status</h3>
              <p className="text-gray-700 mb-4">
                You work as an independent contractor, not an employee. You are responsible for your own taxes, 
                insurance, and legal compliance.
              </p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Handle your own tax obligations</li>
                <li>• Provide your own equipment and software</li>
                <li>• Maintain professional standards</li>
              </ul>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border">
              <div className="text-3xl mb-4">�</div>
              <h3 className="text-xl font-semibold text-red-600 mb-3">Confidentiality & Security</h3>
              <p className="text-gray-700 mb-4">
                Strict confidentiality requirements for client data, project details, and proprietary information 
                with 5-year post-termination obligations.
              </p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Protect all confidential information</li>
                <li>• Follow security guidelines</li>
                <li>• GDPR/CCPA compliance required</li>
              </ul>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border">
              <div className="text-3xl mb-4">⚖️</div>
              <h3 className="text-xl font-semibold text-red-600 mb-3">IP Ownership (Work-for-Hire)</h3>
              <p className="text-gray-700 mb-4">
                All code, designs, and deliverables you create belong to CapeControl or its clients immediately 
                upon creation. No ownership retained.
              </p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• All IP rights transferred to CapeControl</li>
                <li>• Portfolio use requires written approval</li>
                <li>• Pre-existing materials must be disclosed</li>
              </ul>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border">
              <div className="text-3xl mb-4">�</div>
              <h3 className="text-xl font-semibold text-purple-600 mb-3">Quality Standards</h3>
              <p className="text-gray-700 mb-4">
                All deliverables must meet specifications and pass quality review. Free revisions required 
                if work doesn't meet project brief requirements.
              </p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Industry-standard development practices</li>
                <li>• Code quality and security compliance</li>
                <li>• Client approval required for final acceptance</li>
              </ul>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border">
              <div className="text-3xl mb-4">🎯</div>
              <h3 className="text-xl font-semibold text-purple-600 mb-3">Project-Based Assignments</h3>
              <p className="text-gray-700 mb-4">
                Work is assigned based on skills, availability, and agency needs. Each project has separate 
                requirements, deliverables, and timelines.
              </p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• No guaranteed continuous work</li>
                <li>• Communicate availability clearly</li>
                <li>• Meet agreed-upon deadlines</li>
              </ul>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border">
              <div className="text-3xl mb-4">⚠️</div>
              <h3 className="text-xl font-semibold text-purple-600 mb-3">Liability & Warranties</h3>
              <p className="text-gray-700 mb-4">
                You warrant work quality and indemnify CapeControl against claims. Agency liability is limited 
                to actual customer revenue received.
              </p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Warranty on work quality and IP rights</li>
                <li>• Indemnification for breaches</li>
                <li>• No guaranteed minimum revenue</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Detailed Payment Terms */}
        <section className="mb-16">
          <div className="bg-red-50 border border-red-200 p-8 rounded-lg">
            <h2 className="text-3xl font-bold text-red-800 mb-6">Payment Terms & Conditions</h2>
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-semibold text-red-700 mb-4">When You Get Paid</h3>
                <div className="bg-white p-6 rounded-lg shadow-sm">
                  <ul className="text-sm text-gray-700 space-y-3">
                    <li className="flex items-start space-x-2">
                      <span className="text-red-600 font-bold">✓</span>
                      <span><strong>Only after customer payment:</strong> CapeControl must receive payment from customers first</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="text-red-600 font-bold">✓</span>
                      <span><strong>Monthly processing:</strong> Payments within 30 days of invoice approval</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="text-red-600 font-bold">✓</span>
                      <span><strong>Revenue attribution:</strong> Payment only for revenue directly tied to your module</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="text-amber-600 font-bold">⚠</span>
                      <span><strong>$50 minimum:</strong> Must reach threshold before payout</span>
                    </li>
                  </ul>
                </div>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-red-700 mb-4">When You Don't Get Paid</h3>
                <div className="bg-white p-6 rounded-lg shadow-sm">
                  <ul className="text-sm text-gray-700 space-y-3">
                    <li className="flex items-start space-x-2">
                      <span className="text-red-600 font-bold">✗</span>
                      <span><strong>Freemium usage:</strong> Free tier generates zero payment</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="text-red-600 font-bold">✗</span>
                      <span><strong>Customer refunds:</strong> Payments subject to chargebacks</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="text-red-600 font-bold">✗</span>
                      <span><strong>Module not adopted:</strong> No customer usage = no payment</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="text-red-600 font-bold">✗</span>
                      <span><strong>Work delivery alone:</strong> Completing work doesn't guarantee payment</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Revenue Share Breakdown */}
            <div className="mt-8 bg-gray-900 text-white p-6 rounded-lg">
              <h3 className="text-xl font-semibold mb-4">Revenue Share Breakdown</h3>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <div className="text-3xl font-bold text-green-400 mb-2">30%</div>
                  <p className="text-green-300 mb-2">Developer Share</p>
                  <p className="text-sm text-gray-300">Your portion of net customer revenue attributed to your AI module</p>
                </div>
                <div>
                  <div className="text-3xl font-bold text-blue-400 mb-2">70%</div>
                  <p className="text-blue-300 mb-2">Platform Share</p>
                  <p className="text-sm text-gray-300">Covers infrastructure, support, marketing, and platform maintenance</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Legal & Termination */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Legal Framework & Termination</h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md border">
              <h3 className="text-xl font-semibold text-red-600 mb-4">Termination Conditions</h3>
              <ul className="text-sm text-gray-700 space-y-3">
                <li className="flex items-start space-x-2">
                  <span className="text-red-600 font-bold">•</span>
                  <span><strong>Either party:</strong> 14 days' written notice (no active projects)</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-red-600 font-bold">•</span>
                  <span><strong>For cause:</strong> Immediate termination for material breaches</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-red-600 font-bold">•</span>
                  <span><strong>Project termination:</strong> Agency can cancel specific projects</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-red-600 font-bold">•</span>
                  <span><strong>Post-termination:</strong> Return all confidential information</span>
                </li>
              </ul>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md border">
              <h3 className="text-xl font-semibold text-red-600 mb-4">Dispute Resolution</h3>
              <ul className="text-sm text-gray-700 space-y-3">
                <li className="flex items-start space-x-2">
                  <span className="text-red-600 font-bold">•</span>
                  <span><strong>Payment disputes:</strong> Must be raised within 14 days</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-red-600 font-bold">•</span>
                  <span><strong>Resolution process:</strong> Good-faith negotiation, then mediation/arbitration</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-red-600 font-bold">•</span>
                  <span><strong>Legal costs:</strong> Prevailing party entitled to attorney fees</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-red-600 font-bold">•</span>
                  <span><strong>Governing law:</strong> CapeControl's jurisdiction applies</span>
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* Developer Tools & API */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Development Environment</h2>
          <div className="bg-gray-900 text-white p-8 rounded-lg">
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-semibold text-blue-400 mb-4">Revenue Tracking API</h3>
                <div className="bg-black/50 p-4 rounded font-mono text-sm">
                  <div className="text-green-300">GET /api/developer/revenue</div>
                  <div className="text-gray-400 mt-2">// Customer revenue attribution</div>
                  <div className="text-gray-400">// Payment-eligible earnings</div>
                  <div className="text-gray-400">// Invoice generation status</div>
                </div>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-blue-400 mb-4">Module Management</h3>
                <div className="bg-black/50 p-4 rounded font-mono text-sm">
                  <div className="text-green-300">POST /api/developer/modules</div>
                  <div className="text-green-300">GET /api/developer/analytics</div>
                  <div className="text-gray-400 mt-2">// Deploy AI modules</div>
                  <div className="text-gray-400">// Customer usage metrics</div>
                </div>
              </div>
            </div>
            <div className="mt-6 bg-amber-900/50 p-4 rounded border border-amber-700">
              <p className="text-amber-200 text-sm">
                <strong>Note:</strong> API access requires signed developer agreement and approved contractor status.
                All development must follow security guidelines and code quality standards.
              </p>
            </div>
          </div>
        </section>

        {/* Getting Started - Legal Acknowledgment */}
        <section className="text-center">
          <div className="bg-gradient-to-r from-red-600 to-purple-600 text-white p-12 rounded-lg">
            <h2 className="text-3xl font-bold mb-4">Ready to Join as Independent Contractor?</h2>
            <div className="bg-red-900/30 p-6 rounded-lg mb-8">
              <h3 className="text-xl font-semibold mb-4">⚠️ Legal Requirements Before Proceeding</h3>
              <ul className="text-sm text-left space-y-2 max-w-2xl mx-auto">
                <li>• You acknowledge payment is contingent on customer revenue generation</li>
                <li>• You agree to work-for-hire terms (no IP ownership retained)</li>
                <li>• You understand independent contractor tax and legal obligations</li>
                <li>• You accept 5-year confidentiality and security requirements</li>
                <li>• You agree to quality standards and revision obligations</li>
              </ul>
            </div>
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6">
              <Link
                to="/developer-terms"
                className="bg-white text-red-600 hover:bg-gray-100 py-3 px-8 rounded-lg font-semibold transition-colors"
              >
                📋 Read Full Legal Terms First
              </Link>
              <Link
                to="/register"
                className="border-2 border-white text-white hover:bg-white hover:text-red-600 py-3 px-8 rounded-lg font-semibold transition-colors"
              >
                Apply as Developer
              </Link>
            </div>
            <div className="text-sm space-y-2 opacity-75">
              <p><strong>No setup fees • Revenue-based only • Work-for-hire terms</strong></p>
              <p>Independent contractor status • $50 minimum payout • 30% revenue share</p>
            </div>
            <div className="text-xs mt-4 opacity-60 max-w-2xl mx-auto">
              <p>
                By applying, you acknowledge that you have read and agree to our{' '}
                <Link to="/developer-terms" className="underline hover:text-red-200">
                  Developer Terms & Conditions
                </Link>, which constitute a legally binding independent contractor agreement.
                Payment is contingent on customer revenue generation and not guaranteed by work delivery alone.
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

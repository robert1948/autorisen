export default function DeveloperTerms() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow-lg rounded-lg overflow-hidden">
          <div className="px-6 py-8 sm:p-10">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                CapeControl Developer Terms & Conditions
              </h1>
              <p className="text-lg text-gray-600">
                Terms governing the CapeControl Developer Platform and Revenue Sharing Program
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Last updated: August 5, 2025
              </p>
            </div>

            <div className="prose prose-lg max-w-none">
              
              {/* Company Information */}
              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">Company Information</h2>
                <div className="bg-purple-50 rounded-lg p-6">
                  <div className="space-y-2 text-gray-700">
                    <p><strong>Legal Entity:</strong> Cape Craft Projects CC</p>
                    <p><strong>VAT Number:</strong> 4270105119</p>
                    <p><strong>Trading Name:</strong> Cape Control</p>
                    <p><strong>Platform:</strong> CapeControl (formerly LocalStorm)</p>
                  </div>
                </div>
              </section>

              {/* Introduction */}
              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Introduction</h2>
                <p className="text-gray-700 mb-4">
                  This Terms and Conditions Agreement ("Agreement") governs the relationship between Cape Craft Projects CC 
                  (VAT: 4270105119) trading as Cape Control ("Agency") and you, the Developer ("Developer" or "You"), 
                  an independent contractor providing development services for the Agency. By accepting this Agreement, 
                  You agree to be bound by its terms.
                </p>
                <p className="text-gray-700">
                  By registering as a developer or using our developer tools, you agree to these Developer Terms in 
                  addition to our general <a href="/terms" className="text-purple-600 hover:underline">Terms of Service</a> 
                  and <a href="/privacy" className="text-purple-600 hover:underline">Privacy Policy</a>.
                </p>
              </section>

              {/* Scope of Services */}
              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Scope of Services</h2>
                
                <h3 className="text-xl font-semibold text-gray-800 mb-3">2.1 Engagement</h3>
                <p className="text-gray-700 mb-4">
                  The Agency may engage You to provide development services, including but not limited to designing, coding, 
                  testing, and deploying agent-based solutions (e.g., AI agents, chatbots, automation tools) for the Agency's 
                  clients ("Projects").
                </p>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">2.2 Project Assignments</h3>
                <p className="text-gray-700 mb-4">
                  Projects will be assigned based on Your skills, availability, and the Agency's needs. Each Project will have 
                  a separate Project Brief outlining specific requirements, deliverables, timelines, and compensation.
                </p>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">2.3 Independent Contractor Status</h3>
                <p className="text-gray-700 mb-4">
                  You are an independent contractor, not an employee, partner, or agent of the Agency. You are responsible 
                  for Your own taxes, insurance, and compliance with applicable laws.
                </p>
              </section>

              {/* Developer Obligations */}
              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. Developer Obligations</h2>
                
                <h3 className="text-xl font-semibold text-gray-800 mb-3">3.1 Performance</h3>
                <p className="text-gray-700 mb-4">
                  You agree to perform all services professionally, diligently, and in accordance with industry standards, 
                  the Project Brief, and the Agency's guidelines.
                </p>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">3.2 Availability</h3>
                <p className="text-gray-700 mb-4">
                  You will communicate Your availability for Projects and meet agreed-upon deadlines. Any delays must be 
                  reported promptly to the Agency.
                </p>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">3.3 Tools and Resources</h3>
                <p className="text-gray-700 mb-4">
                  You are responsible for providing Your own equipment, software, and resources unless otherwise specified 
                  in the Project Brief.
                </p>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">3.4 Compliance</h3>
                <p className="text-gray-700 mb-4">
                  You will comply with all applicable laws, including data protection regulations (e.g., GDPR, CCPA), 
                  and adhere to the Agency's policies on code quality, security, and ethics.
                </p>
              </section>

              {/* Compensation - Revenue-Based Payment Model */}
              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Compensation</h2>
                
                <h3 className="text-xl font-semibold text-gray-800 mb-3">4.1 Revenue-Based Payment Model</h3>
                <div className="bg-amber-50 border border-amber-200 p-4 rounded-lg mb-4">
                  <p className="text-gray-700 font-semibold mb-2">
                    Important: Payments to Developers are strictly tied to actual revenue generated by the Agency 
                    from customer usage of the AI module developed by the Developer.
                  </p>
                </div>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">4.2 Payment Conditions</h3>
                <ul className="list-disc pl-6 text-gray-700 mb-4">
                  <li>Payments will be made <strong>only after the Agency receives revenue</strong> from paying customers directly attributable to the Developer's Work Product</li>
                  <li>If a module is made available under a freemium or promotional model, no payment shall be due until revenue is generated from its use</li>
                  <li>The Developer understands that delivery of work does not guarantee payment unless and until the Work Product is monetized</li>
                </ul>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">4.3 Revenue Share</h3>
                <div className="bg-green-50 border border-green-200 p-4 rounded-lg mb-4">
                  <p className="text-gray-700">
                    <strong>Standard Revenue Share:</strong> 30% of net customer revenue attributable to your AI module<br/>
                    <strong>Platform Share:</strong> 70% (covers infrastructure, support, marketing, and platform maintenance)
                  </p>
                </div>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">4.4 Invoicing and Tracking</h3>
                <ul className="list-disc pl-6 text-gray-700 mb-4">
                  <li>Invoices may only be submitted once the Agency confirms that customer revenue tied to the Developer's module has been received</li>
                  <li>The Agency will provide reasonable access to usage and revenue metrics to confirm module adoption and earnings</li>
                  <li>Minimum payout threshold: $50 USD</li>
                </ul>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">4.5 Payment Schedule</h3>
                <ul className="list-disc pl-6 text-gray-700 mb-4">
                  <li>Once revenue is received and the Developer's share is determined, payments will be made within 30 days of invoice approval</li>
                  <li>Payments are processed monthly for the previous month's confirmed earnings</li>
                  <li>All payments will be made via bank transfer or PayPal, unless otherwise stated in the Project Brief</li>
                </ul>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">4.6 Disputes and Adjustments</h3>
                <ul className="list-disc pl-6 text-gray-700 mb-4">
                  <li>Any disputes over payments must be raised within 14 days of payment or report delivery</li>
                  <li>The Agency reserves the right to adjust revenue share calculations due to refunds, chargebacks, or service cancellations by customers</li>
                </ul>
              </section>

              {/* Confidentiality */}
              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. Confidentiality</h2>
                
                <h3 className="text-xl font-semibold text-gray-800 mb-3">5.1 Confidential Information</h3>
                <p className="text-gray-700 mb-4">
                  You may have access to confidential information, including client data, project details, and Agency processes. 
                  You agree to keep all such information confidential and not disclose it to third parties without prior written 
                  consent from the Agency.
                </p>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">5.2 Data Security</h3>
                <p className="text-gray-700 mb-4">
                  You will implement reasonable measures to protect confidential information, including secure storage and 
                  transmission of data. All development work must follow our security guidelines.
                </p>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">5.3 Duration</h3>
                <p className="text-gray-700 mb-4">
                  Confidentiality obligations survive the termination of this Agreement for five (5) years.
                </p>
              </section>

              {/* Intellectual Property */}
              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Intellectual Property</h2>
                
                <h3 className="text-xl font-semibold text-gray-800 mb-3">6.1 Ownership</h3>
                <p className="text-gray-700 mb-4">
                  All code, designs, and deliverables created by You for a Project ("Work Product") are considered 
                  "work-for-hire" and belong to the Agency or its client, as specified in the Project Brief. You assign 
                  all rights, title, and interest in the Work Product to the Agency upon creation.
                </p>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">6.2 Pre-Existing Materials</h3>
                <p className="text-gray-700 mb-4">
                  If You incorporate pre-existing materials (e.g., open-source code, proprietary tools) into the Work Product, 
                  You must disclose this in advance and ensure proper licensing. You grant the Agency a perpetual, 
                  non-exclusive license to use such materials for the Project.
                </p>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">6.3 Portfolio Use</h3>
                <p className="text-gray-700 mb-4">
                  You may showcase the Work Product in Your portfolio only with the Agency's prior written approval, 
                  ensuring no confidential client information is disclosed.
                </p>
              </section>

              {/* Quality and Acceptance */}
              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Quality and Acceptance</h2>
                
                <h3 className="text-xl font-semibold text-gray-800 mb-3">7.1 Standards</h3>
                <p className="text-gray-700 mb-4">
                  All deliverables must meet the specifications in the Project Brief and pass the Agency's quality review process.
                </p>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">7.2 Revisions</h3>
                <p className="text-gray-700 mb-4">
                  You agree to make reasonable revisions to deliverables if they do not meet the Project Brief requirements, 
                  at no additional cost, within seven (7) days of feedback.
                </p>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">7.3 Client Approval</h3>
                <p className="text-gray-700 mb-4">
                  Final acceptance of deliverables is subject to client approval, as communicated by the Agency.
                </p>
              </section>

              {/* Termination */}
              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. Termination</h2>
                
                <h3 className="text-xl font-semibold text-gray-800 mb-3">8.1 Termination by Either Party</h3>
                <p className="text-gray-700 mb-4">
                  Either party may terminate this Agreement with 14 days' written notice, provided no active Projects are pending.
                </p>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">8.2 Termination for Cause</h3>
                <p className="text-gray-700 mb-4">
                  The Agency may terminate this Agreement immediately if You breach any material term (e.g., failure to deliver, 
                  breach of confidentiality).
                </p>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">8.3 Project Termination</h3>
                <p className="text-gray-700 mb-4">
                  The Agency may terminate a specific Project with notice if the client cancels or You fail to meet obligations. 
                  You will be compensated for revenue received from completed work up to the termination date, subject to client 
                  usage and approval.
                </p>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">8.4 Post-Termination</h3>
                <p className="text-gray-700 mb-4">
                  Upon termination, You must return or destroy all confidential information and cease using Agency resources.
                </p>
              </section>

              {/* Warranties and Indemnification */}
              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. Warranties and Indemnification</h2>
                
                <h3 className="text-xl font-semibold text-gray-800 mb-3">9.1 Warranties</h3>
                <p className="text-gray-700 mb-4">
                  You warrant that Your services will be performed competently, that the Work Product will not infringe 
                  third-party rights, and that You have the authority to enter this Agreement.
                </p>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">9.2 Indemnification</h3>
                <p className="text-gray-700 mb-4">
                  You agree to indemnify the Agency against claims arising from Your breach of this Agreement, including 
                  intellectual property violations or failure to comply with laws.
                </p>
              </section>

              {/* Limitation of Liability */}
              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">10. Limitation of Liability</h2>
                
                <h3 className="text-xl font-semibold text-gray-800 mb-3">10.1 Liability Cap</h3>
                <p className="text-gray-700 mb-4">
                  The Agency's liability to You is limited to the actual amount of customer revenue received for the relevant Work Product.
                </p>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">10.2 No Guarantees</h3>
                <p className="text-gray-700 mb-4">
                  The Agency does not guarantee a minimum number of Projects, continuous work, or guaranteed revenue.
                </p>
              </section>

              {/* Governing Law and Dispute Resolution */}
              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">11. Governing Law and Dispute Resolution</h2>
                
                <h3 className="text-xl font-semibold text-gray-800 mb-3">11.1 Governing Law</h3>
                <p className="text-gray-700 mb-4">
                  This Agreement is governed by the laws applicable to CapeControl's jurisdiction.
                </p>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">11.2 Dispute Resolution</h3>
                <p className="text-gray-700 mb-4">
                  Any disputes will be resolved through good-faith negotiation, followed by mediation or arbitration if necessary. 
                  The prevailing party in any legal action is entitled to reasonable attorney fees.
                </p>
              </section>

              {/* Miscellaneous */}
              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">12. Miscellaneous</h2>
                
                <h3 className="text-xl font-semibold text-gray-800 mb-3">12.1 Entire Agreement</h3>
                <p className="text-gray-700 mb-4">
                  This Agreement constitutes the entire understanding between the Agency and You, superseding all prior agreements.
                </p>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">12.2 Amendments</h3>
                <p className="text-gray-700 mb-4">
                  The Agency may update this Agreement with 30 days' notice. Continued engagement after updates constitutes acceptance.
                </p>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">12.3 Assignment</h3>
                <p className="text-gray-700 mb-4">
                  You may not assign this Agreement without the Agency's written consent.
                </p>

                <h3 className="text-xl font-semibold text-gray-800 mb-3">12.4 Severability</h3>
                <p className="text-gray-700 mb-4">
                  If any provision is found invalid, the remaining provisions remain in effect.
                </p>
              </section>

              {/* Acceptance */}
              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">13. Acceptance</h2>
                <p className="text-gray-700 mb-4">
                  By registering as a developer, clicking "Accept" in the Agency's onboarding portal, or using our developer tools, 
                  You acknowledge that You have read, understood, and agree to be bound by this Agreement.
                </p>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">
                    <strong>Important Notice:</strong> This is a legally binding agreement. Please review all terms carefully 
                    before accepting. If you have questions about any provision, contact us before proceeding.
                  </p>
                </div>
              </section>

              {/* Contact Information */}
              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">14. Contact Information</h2>
                <p className="text-gray-700 mb-4">
                  For questions about these Developer Terms or the developer program, please contact us:
                </p>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-gray-700">
                    <strong>Company:</strong> Cape Craft Projects CC (VAT: 4270105119) trading as Cape Control<br/>
                    <strong>Email:</strong> <a href="mailto:contact@cape-control.com" className="text-purple-600 hover:underline">contact@cape-control.com</a><br/>
                    <strong>Subject:</strong> Developer Terms Inquiry<br/>
                    <strong>Website:</strong> <a href="https://cape-control.com" className="text-purple-600 hover:underline">https://cape-control.com</a>
                  </p>
                </div>
              </section>

            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

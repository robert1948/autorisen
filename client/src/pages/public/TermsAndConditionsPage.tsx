import React, { useState } from "react";
import { Link } from "react-router-dom";
import TopNav from "../../components/nav/TopNav";
import logoUrl from "../../assets/capecontrol-logo.png";
import BuildBadge from "../../components/version/BuildBadge";

type SectionKey =
  | "definitions"
  | "scope"
  | "payment"
  | "timeline"
  | "ip"
  | "data"
  | "confidentiality"
  | "termination"
  | "warranties"
  | "indemnification"
  | "forcemajeure"
  | "nonsolicitation"
  | "governing"
  | "amendments"
  | "miscellaneous"
  | "acceptance";

const TermsAndConditionsPage: React.FC = () => {
  const [openSections, setOpenSections] = useState<Set<SectionKey>>(
    new Set<SectionKey>(["definitions"])
  );

  const allKeys: SectionKey[] = [
    "definitions",
    "scope",
    "payment",
    "timeline",
    "ip",
    "data",
    "confidentiality",
    "termination",
    "warranties",
    "indemnification",
    "forcemajeure",
    "nonsolicitation",
    "governing",
    "amendments",
    "miscellaneous",
    "acceptance",
  ];

  const toggle = (key: SectionKey) => {
    setOpenSections((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const expandAll = () => setOpenSections(new Set<SectionKey>(allKeys));
  const collapseAll = () => setOpenSections(new Set<SectionKey>());
  const isOpen = (key: SectionKey) => openSections.has(key);
  const chevron = (key: SectionKey) => (isOpen(key) ? "▾" : "▸");

  const sectionStyle: React.CSSProperties = {
    background: "rgba(255,255,255,0.04)",
    border: "1px solid rgba(255,255,255,0.08)",
    borderRadius: 12,
    marginBottom: "1rem",
    overflow: "hidden",
  };

  const headerStyle: React.CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    padding: "1.25rem 1.5rem",
    cursor: "pointer",
    userSelect: "none",
    width: "100%",
    background: "none",
    border: "none",
    color: "inherit",
    font: "inherit",
    textAlign: "left",
  };

  const bodyStyle: React.CSSProperties = {
    padding: "0 1.5rem 1.5rem",
    lineHeight: 1.8,
  };

  const subStyle: React.CSSProperties = {
    marginLeft: "1rem",
    paddingLeft: "1rem",
    borderLeft: "2px solid rgba(255,255,255,0.08)",
    marginTop: "0.5rem",
    marginBottom: "0.5rem",
  };

  return (
    <div className="landing">
      <TopNav onOpenSupport={() => {}} />
      <main className="landing__main">
        <section className="section" style={{ paddingTop: "6rem" }}>
          <div style={{ maxWidth: 860, margin: "0 auto" }}>
            <span className="badge badge--accent">Customer Legal</span>
            <h1 style={{ fontSize: "2.4rem", lineHeight: 1.2, marginBottom: "0.5rem" }}>
              Terms and Conditions for Customers
            </h1>
            <p style={{ opacity: 0.7, marginBottom: "0.25rem" }}>
              <strong>Cape Craft Projects CC</strong>, trading as <strong>CapeControl</strong>
            </p>
            <p style={{ opacity: 0.6, marginBottom: "1.5rem", fontSize: "0.9rem" }}>
              Effective Date: February 14, 2026 &nbsp;|&nbsp; Last Updated: February 14, 2026
            </p>

            <p style={{ marginBottom: "1.5rem" }}>
              Welcome to CapeControl (&ldquo;Agency,&rdquo; &ldquo;we,&rdquo; &ldquo;us,&rdquo; or
              &ldquo;our&rdquo;). These Terms and Conditions (&ldquo;T&amp;Cs&rdquo;) govern the
              provision of services by the Agency to you, the customer (&ldquo;Customer,&rdquo;
              &ldquo;you,&rdquo; or &ldquo;your&rdquo;). By engaging our services, signing a
              Proposal, or making any payment, you agree to be bound by these T&amp;Cs. Please
              read them carefully before proceeding.
            </p>

            {/* Toggle controls */}
            <div style={{ display: "flex", gap: "0.75rem", marginBottom: "2rem", flexWrap: "wrap" }}>
              <button type="button" className="btn btn--ghost" style={{ fontSize: "0.85rem", padding: "0.5rem 1rem" }} onClick={expandAll}>
                Expand All Sections
              </button>
              <button type="button" className="btn btn--ghost" style={{ fontSize: "0.85rem", padding: "0.5rem 1rem" }} onClick={collapseAll}>
                Collapse All
              </button>
            </div>

            {/* ---- §1 Definitions ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("definitions")} aria-expanded={isOpen("definitions")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("definitions")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>1. Definitions</h2>
              </button>
              {isOpen("definitions") && (
                <div style={bodyStyle}>
                  <ul style={{ paddingLeft: "1.5rem" }}>
                    <li><strong>Services:</strong> The development, customisation, deployment, maintenance, or support of agent-based solutions (e.g., AI agents, chatbots, automation tools) as outlined in the applicable Proposal.</li>
                    <li><strong>Proposal:</strong> The document provided by the Agency detailing the scope, deliverables, timeline, pricing, and acceptance criteria for the Services.</li>
                    <li><strong>Deliverables:</strong> The specific outputs (e.g., software, code, documentation, reports) provided to the Customer as part of the Services.</li>
                    <li><strong>Intellectual Property (IP):</strong> Any software, code, algorithms, designs, documentation, or materials created during the performance of the Services.</li>
                    <li><strong>Confidential Information:</strong> Any proprietary, sensitive, or non-public information disclosed by either party to the other in connection with the Services, whether in written, oral, electronic, or other form.</li>
                    <li><strong>Pre-Existing IP:</strong> Any intellectual property owned by the Agency or its licensors prior to or independent of the Services, including frameworks, libraries, tools, and methodologies.</li>
                    <li><strong>Change Order:</strong> A written document agreed upon by both parties that modifies the scope, timeline, or pricing of the Services.</li>
                  </ul>
                </div>
              )}
            </div>

            {/* ---- §2 Scope of Services ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("scope")} aria-expanded={isOpen("scope")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("scope")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>2. Scope of Services</h2>
              </button>
              {isOpen("scope") && (
                <div style={bodyStyle}>
                  <p><strong>2.1.</strong> The Agency will provide Services as outlined in the Proposal, which forms an integral part of these T&amp;Cs. In the event of a conflict between the Proposal and these T&amp;Cs, the Proposal shall prevail unless expressly stated otherwise.</p>
                  <p><strong>2.2.</strong> Any changes to the scope, timeline, or deliverables must be documented in a written Change Order signed by authorised representatives of both parties. Additional fees may apply for scope changes.</p>
                  <p><strong>2.3.</strong> The Customer agrees to provide, in a timely manner, all necessary information, materials, access credentials (e.g., APIs, systems, platforms), and cooperation reasonably required for the Agency to deliver the Services. Delays attributable to the Customer&rsquo;s failure to fulfil these obligations may result in corresponding extensions to project timelines.</p>
                  <p><strong>2.4.</strong> The Agency reserves the right to subcontract portions of the Services to qualified third-party developers or contractors, provided that the Agency remains responsible for the quality and compliance of the subcontracted work under these T&amp;Cs.</p>
                  <p><strong>2.5.</strong> The Agency may use third-party tools, platforms, or services (e.g., cloud hosting, AI model APIs) in delivering the Services. The Customer acknowledges that such third-party services are subject to their own terms and conditions, which the Agency will disclose upon request.</p>
                </div>
              )}
            </div>

            {/* ---- §3 Payment Terms ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("payment")} aria-expanded={isOpen("payment")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("payment")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>3. Payment Terms</h2>
              </button>
              {isOpen("payment") && (
                <div style={bodyStyle}>
                  <p><strong>3.1. Fees:</strong> The Customer agrees to pay the fees outlined in the Proposal. All fees are quoted in South African Rand (ZAR) and are exclusive of applicable taxes (including VAT) unless expressly stated otherwise. The Customer is responsible for all applicable taxes.</p>
                  <p><strong>3.2. Payment Schedule:</strong> Payments shall be made according to the milestones or schedule set out in the Proposal (e.g., 50% upon signing, 50% upon completion). No work will commence until the initial payment is received unless otherwise agreed in writing.</p>
                  <p><strong>3.3. Invoicing:</strong> Invoices will be issued electronically to the email address provided by the Customer and are due within 14 days of the invoice date unless otherwise specified in the Proposal.</p>
                  <p><strong>3.4. Late Payments:</strong> Overdue payments shall incur interest at a rate of 1.5% per month (or the maximum rate permitted by applicable South African law, whichever is lower) on the outstanding balance, calculated from the due date until the date of payment. The Agency reserves the right to suspend or delay all Services without liability for any consequences arising from such suspension until the Customer&rsquo;s account is fully settled. The Customer shall also be responsible for any reasonable collection costs, including legal fees, incurred by the Agency.</p>
                  <p><strong>3.5. Refunds:</strong> Fees are non-refundable for work already completed. Refund entitlements arising from termination are governed by Section 8. Any refunds will be processed within 30 days of the determination of the refundable amount.</p>
                  <p><strong>3.6. Expense Reimbursement:</strong> Any out-of-pocket expenses (e.g., third-party software licences, hosting fees) required for the Services will be pre-approved by the Customer in writing and invoiced separately.</p>
                </div>
              )}
            </div>

            {/* ---- §4 Project Timeline and Delivery ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("timeline")} aria-expanded={isOpen("timeline")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("timeline")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>4. Project Timeline and Delivery</h2>
              </button>
              {isOpen("timeline") && (
                <div style={bodyStyle}>
                  <p><strong>4.1.</strong> The Agency will use commercially reasonable efforts to meet the timelines outlined in the Proposal. All timelines are estimates unless expressly designated as fixed deadlines in the Proposal. Delays caused by the Customer (e.g., failure to provide materials, delayed feedback, scope changes) shall automatically extend deadlines by a corresponding period.</p>
                  <p><strong>4.2.</strong> Deliverables will be provided in the format and delivery method specified in the Proposal (e.g., software deployment, code repository access, file transfer).</p>
                  <p><strong>4.3. Acceptance Process:</strong> The Customer must review each Deliverable within 7 business days of receipt and provide written acceptance or a detailed list of specific deficiencies referencing the agreed specifications in the Proposal. Failure to respond within this period shall constitute deemed acceptance of the Deliverable.</p>
                  <p><strong>4.4.</strong> If the Customer identifies deficiencies that constitute a genuine failure to meet the agreed specifications, the Agency shall use commercially reasonable efforts to remedy such deficiencies within 14 business days at no additional cost. Issues arising from changes in requirements, Customer-provided materials, or matters outside the agreed specifications shall be addressed via a Change Order.</p>
                  <p><strong>4.5.</strong> The Agency shall provide the Customer with reasonable progress updates at intervals agreed upon in the Proposal or as reasonably requested.</p>
                </div>
              )}
            </div>

            {/* ---- §5 Intellectual Property ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("ip")} aria-expanded={isOpen("ip")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("ip")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>5. Intellectual Property</h2>
              </button>
              {isOpen("ip") && (
                <div style={bodyStyle}>
                  <p><strong>5.1. Pre-Existing IP:</strong> The Agency retains all rights, title, and interest in any Pre-Existing IP, including proprietary frameworks, libraries, tools, code templates, and methodologies used in or incorporated into the Deliverables. To the extent Pre-Existing IP is incorporated into the Deliverables, the Agency grants the Customer a non-exclusive, perpetual, irrevocable, worldwide, royalty-free licence to use such Pre-Existing IP solely as part of and to the extent necessary for the use of the Deliverables for their intended purpose.</p>
                  <p><strong>5.2. Custom Deliverables Ownership:</strong> Upon full and final payment of all fees due under the applicable Proposal:</p>
                  <div style={subStyle}>
                    <p><strong>Option A (Licence):</strong> The Agency grants the Customer a non-exclusive, perpetual, irrevocable, worldwide licence to use, modify, and deploy the custom portions of the Deliverables for the Customer&rsquo;s internal business purposes. The Agency retains ownership of the custom Deliverables.</p>
                    <p><strong>Option B (Assignment):</strong> The Agency assigns to the Customer all rights, title, and interest in the custom portions of the Deliverables specifically created for the Customer. The Agency retains a non-exclusive, royalty-free licence to use general techniques, knowledge, experience, and non-Customer-specific components developed during the Services for future projects.</p>
                  </div>
                  <p><em>The applicable option will be specified in the Proposal.</em></p>
                  <p><strong>5.3. Customer Materials:</strong> The Customer grants the Agency a non-exclusive, royalty-free, limited licence to use any materials provided by the Customer (e.g., logos, branding assets, data, content) solely for the purpose of performing the Services. All rights in Customer materials remain with the Customer.</p>
                  <p><strong>5.4. Third-Party IP:</strong> The Customer represents and warrants that all materials provided to the Agency do not infringe upon any third-party intellectual property rights, proprietary rights, or other legal rights. The Customer shall indemnify and hold harmless the Agency from any claims, damages, or expenses arising from any such infringement.</p>
                  <p><strong>5.5. Open-Source Components:</strong> Where open-source software is incorporated into the Deliverables, the Agency will disclose the applicable open-source licences. The Customer acknowledges that such components are subject to their respective licence terms.</p>
                </div>
              )}
            </div>

            {/* ---- §6 Data Protection and Privacy ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("data")} aria-expanded={isOpen("data")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("data")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>6. Data Protection and Privacy</h2>
              </button>
              {isOpen("data") && (
                <div style={bodyStyle}>
                  <p><strong>6.1. Data Handling:</strong> Where the Agency processes personal data on behalf of the Customer in the course of providing the Services, both parties agree to comply with all applicable data protection laws and regulations, including the Protection of Personal Information Act, 2013 (POPIA), and where applicable, the EU GDPR, UK GDPR, CCPA, or equivalent legislation.</p>
                  <p><strong>6.2. Data Processing Agreement:</strong> If the Services involve the processing of personal data (as defined in POPIA), the parties shall enter into a separate Data Processing Agreement (DPA) that complies with applicable legal requirements, including POPIA&rsquo;s requirements for operators. The DPA shall form part of these T&amp;Cs.</p>
                  <p><strong>6.3. Customer Obligations:</strong> The Customer warrants that any personal data provided to the Agency has been collected lawfully, that all necessary consents have been obtained in accordance with POPIA (or the applicable data protection legislation in the Customer&rsquo;s jurisdiction), and that the Customer has a valid legal basis for sharing such data with the Agency.</p>
                  <p><strong>6.4. Data Security:</strong> The Agency will implement reasonable technical and organisational measures to protect any data provided by the Customer against unauthorised access, loss, or destruction, in compliance with POPIA and applicable industry standards.</p>
                </div>
              )}
            </div>

            {/* ---- §7 Confidentiality ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("confidentiality")} aria-expanded={isOpen("confidentiality")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("confidentiality")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>7. Confidentiality</h2>
              </button>
              {isOpen("confidentiality") && (
                <div style={bodyStyle}>
                  <p><strong>7.1.</strong> Both parties agree to maintain the confidentiality of all Confidential Information received from the other party during and after the term of the Services. Neither party shall disclose, use, or permit disclosure of Confidential Information except as necessary to perform or receive the Services or as required by applicable law or regulation.</p>
                  <p><strong>7.2.</strong> Confidentiality obligations under this section do not apply to information that:</p>
                  <div style={subStyle}>
                    <p>(a) is or becomes publicly available through no fault of the receiving party;</p>
                    <p>(b) was already known to the receiving party before disclosure;</p>
                    <p>(c) is independently developed by the receiving party without reference to the disclosing party&rsquo;s Confidential Information; or</p>
                    <p>(d) is rightfully received from a third party without restriction on disclosure.</p>
                  </div>
                  <p><strong>7.3.</strong> The Agency may use the Customer&rsquo;s name, logo, and a general description of the project in the Agency&rsquo;s portfolio and marketing materials, unless the Customer opts out by providing written notice to the Agency. Any detailed case studies or testimonials require the Customer&rsquo;s prior written approval.</p>
                  <p><strong>7.4.</strong> Confidentiality obligations under this section shall survive termination or expiration of these T&amp;Cs for a period of 3 years.</p>
                </div>
              )}
            </div>

            {/* ---- §8 Termination ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("termination")} aria-expanded={isOpen("termination")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("termination")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>8. Termination</h2>
              </button>
              {isOpen("termination") && (
                <div style={bodyStyle}>
                  <p><strong>8.1. Termination for Breach:</strong> Either party may terminate the Services by providing written notice if the other party materially breaches these T&amp;Cs and fails to cure such breach within 14 days of receiving written notice specifying the nature of the breach.</p>
                  <p><strong>8.2. Termination for Convenience by the Customer:</strong> The Customer may terminate the Services at any time by providing 30 days&rsquo; written notice to the Agency. In such case:</p>
                  <div style={subStyle}>
                    <p>If terminated before Services commence, a cancellation fee of 20% of the total project fee shall apply.</p>
                    <p>If terminated after Services have commenced, the Customer shall pay for all work satisfactorily completed up to the effective date of termination, plus any non-cancellable third-party costs incurred by the Agency.</p>
                  </div>
                  <p><strong>8.3. Termination by the Agency:</strong> The Agency may terminate the Services immediately upon written notice if:</p>
                  <div style={subStyle}>
                    <p>The Customer fails to make any payment when due and such failure continues for 14 days after written notice;</p>
                    <p>The Customer fails to provide necessary materials, access, or cooperation, materially impeding the Agency&rsquo;s ability to perform; or</p>
                    <p>The Customer becomes insolvent, enters business rescue, liquidation, or undergoes analogous proceedings.</p>
                  </div>
                  <p><strong>8.4. Post-Termination Obligations:</strong></p>
                  <div style={subStyle}>
                    <p>The Agency will deliver to the Customer all completed Deliverables and work-in-progress for which the Customer has paid.</p>
                    <p>The Customer will pay all outstanding fees for Services rendered and expenses incurred up to the termination date within 14 days of receiving a final invoice.</p>
                    <p>Each party will promptly return or destroy the other party&rsquo;s Confidential Information upon written request, except as required to be retained by law.</p>
                    <p>Sections 5 (Intellectual Property), 6 (Data Protection), 7 (Confidentiality), 8.4 (Post-Termination Obligations), 9 (Warranties and Liability), and 13 (Governing Law) shall survive termination.</p>
                  </div>
                </div>
              )}
            </div>

            {/* ---- §9 Warranties and Liability ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("warranties")} aria-expanded={isOpen("warranties")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("warranties")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>9. Warranties and Liability</h2>
              </button>
              {isOpen("warranties") && (
                <div style={bodyStyle}>
                  <p><strong>9.1. Agency Warranty:</strong> The Agency warrants that:</p>
                  <div style={subStyle}>
                    <p>Services will be performed with reasonable professional care, skill, and diligence consistent with generally accepted industry standards;</p>
                    <p>Deliverables will substantially conform to the specifications set out in the Proposal for a period of 30 days following acceptance (&ldquo;Warranty Period&rdquo;);</p>
                    <p>During the Warranty Period, the Agency will remedy any material defects in the Deliverables at no additional cost, provided the defect is attributable to the Agency&rsquo;s work and not to modifications made by the Customer, Customer-provided materials, or third-party systems.</p>
                  </div>
                  <p><strong>9.2. Customer Warranty:</strong> The Customer warrants that:</p>
                  <div style={subStyle}>
                    <p>All information and materials provided to the Agency are accurate, complete, and lawfully obtained;</p>
                    <p>The Customer has full authority to enter into these T&amp;Cs and to authorise the Agency to perform the Services;</p>
                    <p>Customer-provided materials do not infringe upon any third-party rights.</p>
                  </div>
                  <p><strong>9.3. Disclaimer:</strong> Except as expressly stated in these T&amp;Cs, the Agency makes no other warranties, whether express, implied, statutory, or otherwise, including any implied warranties of merchantability, fitness for a particular purpose, or non-infringement. The Agency does not warrant that the Deliverables will be error-free or that their operation will be uninterrupted.</p>
                  <p><strong>9.4. Limitation of Liability:</strong></p>
                  <div style={subStyle}>
                    <p>The Agency&rsquo;s total aggregate liability arising out of or in connection with these T&amp;Cs, whether in contract, delict (including negligence), breach of statutory duty, or otherwise, shall not exceed the total fees actually paid by the Customer under the applicable Proposal in the 12 months preceding the claim.</p>
                    <p>In no event shall the Agency be liable for any indirect, incidental, special, consequential, or punitive damages, including but not limited to loss of profits, loss of revenue, loss of data, loss of business opportunity, or loss of goodwill, even if advised of the possibility of such damages.</p>
                    <p>Nothing in these T&amp;Cs shall exclude or limit liability for: (a) death or personal injury caused by negligence; (b) fraud or fraudulent misrepresentation; or (c) any other liability that cannot be excluded or limited by applicable South African law.</p>
                  </div>
                  <p><strong>9.5. No Guarantee of Results:</strong> The Agency does not guarantee any specific business outcomes, revenue increases, performance metrics, or results from the use of the Deliverables beyond their substantial conformance with the agreed specifications. The Customer acknowledges that the success of AI-based solutions may depend on factors beyond the Agency&rsquo;s control, including data quality, user adoption, and market conditions.</p>
                </div>
              )}
            </div>

            {/* ---- §10 Indemnification ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("indemnification")} aria-expanded={isOpen("indemnification")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("indemnification")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>10. Indemnification</h2>
              </button>
              {isOpen("indemnification") && (
                <div style={bodyStyle}>
                  <p><strong>10.1. Customer Indemnification:</strong> The Customer shall indemnify, defend, and hold harmless the Agency and its officers, directors, employees, and contractors from and against any claims, damages, losses, liabilities, costs, and expenses (including reasonable attorney fees) arising out of or related to: (a) the Customer&rsquo;s breach of these T&amp;Cs; (b) the Customer&rsquo;s use of the Deliverables in a manner not contemplated by the Proposal; (c) any infringement of third-party rights by Customer-provided materials; or (d) the Customer&rsquo;s violation of applicable laws.</p>
                  <p><strong>10.2. Agency Indemnification:</strong> The Agency shall indemnify, defend, and hold harmless the Customer from and against any third-party claims alleging that the Deliverables (excluding Customer-provided materials and third-party components) infringe a third party&rsquo;s intellectual property rights, provided that the Customer promptly notifies the Agency in writing and gives the Agency reasonable control over the defence and settlement of such claim.</p>
                </div>
              )}
            </div>

            {/* ---- §11 Force Majeure ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("forcemajeure")} aria-expanded={isOpen("forcemajeure")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("forcemajeure")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>11. Force Majeure</h2>
              </button>
              {isOpen("forcemajeure") && (
                <div style={bodyStyle}>
                  <p><strong>11.1.</strong> Neither party shall be liable for any delay or failure to perform its obligations under these T&amp;Cs to the extent that such delay or failure results from circumstances beyond that party&rsquo;s reasonable control (&ldquo;Force Majeure Event&rdquo;), including but not limited to natural disasters, pandemics, acts of war or terrorism, government actions, load shedding or prolonged power outages, internet failures, cyberattacks, or third-party service provider outages.</p>
                  <p><strong>11.2.</strong> The affected party must notify the other party in writing within 5 business days of becoming aware of the Force Majeure Event, detailing the nature, expected duration, and steps being taken to mitigate the impact.</p>
                  <p><strong>11.3.</strong> If a Force Majeure Event continues for more than 60 days, either party may terminate the affected Services upon written notice without further liability, except for payment of Services satisfactorily rendered prior to the Force Majeure Event.</p>
                </div>
              )}
            </div>

            {/* ---- §12 Non-Solicitation ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("nonsolicitation")} aria-expanded={isOpen("nonsolicitation")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("nonsolicitation")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>12. Non-Solicitation</h2>
              </button>
              {isOpen("nonsolicitation") && (
                <div style={bodyStyle}>
                  <p><strong>12.1.</strong> During the term of the Services and for a period of 12 months following termination, neither party shall directly solicit or hire any employee or contractor of the other party who was materially involved in the Services without the other party&rsquo;s prior written consent. This restriction does not apply to individuals who respond to general public job advertisements.</p>
                </div>
              )}
            </div>

            {/* ---- §13 Governing Law and Dispute Resolution ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("governing")} aria-expanded={isOpen("governing")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("governing")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>13. Governing Law and Dispute Resolution</h2>
              </button>
              {isOpen("governing") && (
                <div style={bodyStyle}>
                  <p><strong>13.1.</strong> These T&amp;Cs shall be governed by and construed in accordance with the laws of the Republic of South Africa, without regard to its conflict of law principles.</p>
                  <p><strong>13.2.</strong> The parties hereby submit to the exclusive jurisdiction of the High Court of South Africa, Western Cape Division, Cape Town, or such other competent court in Cape Town, South Africa, for the resolution of any disputes arising out of or in connection with these T&amp;Cs. Each party irrevocably waives any objection to the laying of venue in such courts and any claim that any action or proceeding brought in such courts has been brought in an inconvenient forum.</p>
                  <p><strong>13.3.</strong> The parties agree to attempt to resolve any dispute arising out of or in connection with these T&amp;Cs through good-faith negotiation for a period of at least 30 calendar days following written notice of the dispute.</p>
                  <p><strong>13.4.</strong> If the dispute is not resolved through negotiation, the parties agree to submit the dispute to mediation administered by the Arbitration Foundation of Southern Africa (AFSA) or another mutually agreed mediation body, with mediation proceedings to be held in Cape Town, South Africa, before pursuing arbitration or litigation.</p>
                  <p><strong>13.5.</strong> If mediation is unsuccessful within 30 calendar days of its commencement (or such longer period as the parties may agree), the dispute shall be referred to and finally resolved by binding arbitration conducted in Cape Town, South Africa, under the rules of the Arbitration Foundation of Southern Africa (AFSA). The arbitration shall be conducted by a single arbitrator, unless the parties agree otherwise. The language of the arbitration shall be English. The arbitrator&rsquo;s award shall be final and binding and may be entered as a judgment in any court of competent jurisdiction, including the High Court of South Africa, Western Cape Division, Cape Town.</p>
                  <p><strong>13.6.</strong> Nothing in this section shall prevent either party from seeking urgent interim relief, including an interdict or other equitable relief, in the High Court of South Africa, Western Cape Division, Cape Town, or any other court of competent jurisdiction, to protect its intellectual property or Confidential Information, without the requirement to first pursue negotiation, mediation, or arbitration.</p>
                  <p><strong>13.7.</strong> Nothing in this section shall be construed to limit any rights the Customer may have under the Consumer Protection Act, 2008 (Act No. 68 of 2008), to the extent applicable.</p>
                </div>
              )}
            </div>

            {/* ---- §14 Amendments ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("amendments")} aria-expanded={isOpen("amendments")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("amendments")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>14. Amendments</h2>
              </button>
              {isOpen("amendments") && (
                <div style={bodyStyle}>
                  <p><strong>14.1.</strong> The Agency may update these T&amp;Cs by providing the Customer with at least 30 days&rsquo; written notice. Updated T&amp;Cs will apply to Services commenced or renewed after the effective date of the update. Continued engagement of new Services after such notice constitutes acceptance. Material changes to terms governing ongoing projects require the Customer&rsquo;s written consent.</p>
                  <p><strong>14.2.</strong> Any amendments to the Proposal, scope of Services, or project-specific terms must be documented in a written Change Order signed by authorised representatives of both parties.</p>
                </div>
              )}
            </div>

            {/* ---- §15 Miscellaneous ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("miscellaneous")} aria-expanded={isOpen("miscellaneous")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("miscellaneous")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>15. Miscellaneous</h2>
              </button>
              {isOpen("miscellaneous") && (
                <div style={bodyStyle}>
                  <p><strong>15.1. Entire Agreement:</strong> These T&amp;Cs, together with the applicable Proposal, any Change Orders, and any Data Processing Agreement, constitute the entire agreement between the parties with respect to the subject matter hereof and supersede all prior negotiations, representations, warranties, understandings, or agreements, whether written or oral.</p>
                  <p><strong>15.2. Assignment:</strong> The Customer may not assign, transfer, or delegate any of its rights or obligations under these T&amp;Cs without the Agency&rsquo;s prior written consent. The Agency may assign these T&amp;Cs to a successor entity in connection with a merger, acquisition, or sale of substantially all of its assets, provided the successor assumes the Agency&rsquo;s obligations hereunder.</p>
                  <p><strong>15.3. Severability:</strong> If any provision of these T&amp;Cs is held to be invalid, illegal, or unenforceable by a court of competent jurisdiction, such provision shall be modified to the minimum extent necessary to make it enforceable, and the remaining provisions shall continue in full force and effect.</p>
                  <p><strong>15.4. Waiver:</strong> No failure or delay by either party in exercising any right or remedy under these T&amp;Cs shall constitute a waiver of that right or remedy. Any waiver must be in writing and signed by the waiving party.</p>
                  <p><strong>15.5. Notices:</strong> All notices, requests, and communications under these T&amp;Cs must be in writing and sent to the contact details specified in the Proposal (or as updated by written notice). Notices shall be deemed received: (a) upon delivery if delivered by hand; (b) upon confirmed transmission if sent by email; or (c) 3 business days after posting if sent by registered mail.</p>
                  <p><strong>15.6. Independent Contractors:</strong> The relationship between the Agency and the Customer is that of independent contractors. Nothing in these T&amp;Cs creates a partnership, joint venture, employment, or agency relationship between the parties.</p>
                  <p><strong>15.7. Third-Party Rights:</strong> These T&amp;Cs do not confer any rights on any third party unless expressly stated.</p>
                  <p><strong>15.8. Electronic Signatures:</strong> Electronic signatures shall be deemed valid and binding to the extent permitted by the Electronic Communications and Transactions Act, 2002 (Act No. 25 of 2002).</p>
                </div>
              )}
            </div>

            {/* ---- §16 Acceptance ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("acceptance")} aria-expanded={isOpen("acceptance")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("acceptance")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>16. Acceptance</h2>
              </button>
              {isOpen("acceptance") && (
                <div style={bodyStyle}>
                  <p>By signing the Proposal, making a payment, or instructing the Agency to commence Services, the Customer acknowledges and confirms that they have read, understood, and agree to be bound by these T&amp;Cs in their entirety. The Customer confirms that the person accepting these T&amp;Cs is authorised to do so on behalf of the Customer.</p>
                </div>
              )}
            </div>

            {/* ---- CTAs ---- */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                gap: "1rem",
                marginTop: "2.5rem",
                marginBottom: "2rem",
              }}
            >
              <Link
                to="/auth/register"
                className="btn btn--primary"
                style={{ textAlign: "center" }}
              >
                Register as Customer
              </Link>
              <Link
                to="/customer-terms"
                className="btn btn--ghost"
                style={{ textAlign: "center" }}
              >
                Proposal Terms Summary
              </Link>
              <a
                href="mailto:support@cape-control.com"
                className="btn btn--ghost"
                style={{ textAlign: "center" }}
              >
                Contact Support
              </a>
            </div>

            {/* ---- Contact ---- */}
            <h2 style={{ marginTop: "3rem" }}>Contact Information</h2>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                gap: "1rem",
                marginTop: "1rem",
              }}
            >
              {[
                { label: "Company", value: "Cape Craft Projects CC", href: undefined },
                { label: "Trading As", value: "CapeControl", href: undefined },
                { label: "Location", value: "Cape Town, South Africa", href: undefined },
                { label: "Email", value: "support@cape-control.com", href: "mailto:support@cape-control.com" },
                { label: "Website", value: "cape-control.com", href: "https://cape-control.com" },
              ].map((item) => (
                <div
                  key={item.label}
                  style={{
                    background: "rgba(255,255,255,0.04)",
                    border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: 10,
                    padding: "1.25rem",
                  }}
                >
                  <p style={{ opacity: 0.6, fontSize: "0.85rem", margin: "0 0 0.25rem" }}>
                    {item.label}
                  </p>
                  {item.href ? (
                    <a href={item.href} style={{ color: "#93c5fd", fontWeight: 500 }}>
                      {item.value}
                    </a>
                  ) : (
                    <p style={{ margin: 0, fontWeight: 500 }}>{item.value}</p>
                  )}
                </div>
              ))}
            </div>

            {/* ---- Disclaimer ---- */}
            <div
              style={{
                marginTop: "3rem",
                marginBottom: "4rem",
                padding: "1.25rem 1.5rem",
                background: "rgba(255,255,255,0.04)",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: 10,
                fontSize: "0.85rem",
                opacity: 0.7,
                lineHeight: 1.7,
              }}
            >
              <strong>Legal Disclaimer:</strong> This document is provided for informational purposes
              only and does not constitute legal advice. These Terms and Conditions are governed by the
              laws of the Republic of South Africa. All disputes shall be resolved in Cape Town, South
              Africa, as specified in Section 13. Customers are encouraged to seek independent legal
              advice before engaging services. This document should be reviewed periodically as the
              Agency may update it with 30 days&rsquo; notice in accordance with Section 14.
            </div>
          </div>
        </section>
      </main>

      {/* FOOTER */}
      <footer className="footer">
        <div className="footer__content">
          <div className="footer__main">
            <div className="footer__brand">
              <img
                className="footer__logo"
                src={logoUrl}
                alt="CapeControl logo"
                width={44}
                height={44}
                loading="lazy"
              />
              <div>
                <h3>CapeControl</h3>
                <p className="footer__brand-meta">Operated by Cape Craft Projects CC</p>
                <p className="footer__brand-meta">Trading as CapeControl</p>
              </div>
            </div>
            <div className="footer__column">
              <h4>Platform</h4>
              <ul className="footer__links-list">
                <li><Link to="/">Home</Link></li>
                <li><Link to="/subscribe">Pricing</Link></li>
              </ul>
            </div>
            <div className="footer__column">
              <h4>Information</h4>
              <ul className="footer__links-list">
                <li><Link to="/customer-terms">Proposal Terms</Link></li>
                <li><Link to="/terms-and-conditions">Customer T&amp;Cs</Link></li>
                <li><Link to="/developer-terms">Developer T&amp;Cs</Link></li>
              </ul>
            </div>
            <div className="footer__column">
              <h4>Company</h4>
              <ul className="footer__links-list">
                <li><a href="/#about">About</a></li>
                <li><a href="/#privacy">Privacy Policy</a></li>
              </ul>
            </div>
          </div>
          <div className="footer__bottom">
            <p>&copy; {new Date().getFullYear()} Cape Control. All rights reserved.</p>
            <div className="footer__bottom-meta">
              <BuildBadge />
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default TermsAndConditionsPage;

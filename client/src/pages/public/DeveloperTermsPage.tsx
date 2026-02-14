import React, { useState } from "react";
import { Link } from "react-router-dom";
import TopNav from "../../components/nav/TopNav";
import logoUrl from "../../assets/capecontrol-logo.png";
import BuildBadge from "../../components/version/BuildBadge";

type SectionKey =
  | "definitions"
  | "scope"
  | "obligations"
  | "compensation"
  | "confidentiality"
  | "ip"
  | "qa"
  | "warranties"
  | "indemnification"
  | "liability"
  | "governing"
  | "termination"
  | "nonsolicitation"
  | "general"
  | "acceptance";

const DeveloperTermsPage: React.FC = () => {
  const [openSections, setOpenSections] = useState<Set<SectionKey>>(
    new Set<SectionKey>(["definitions"])
  );

  const allKeys: SectionKey[] = [
    "definitions",
    "scope",
    "obligations",
    "compensation",
    "confidentiality",
    "ip",
    "qa",
    "warranties",
    "indemnification",
    "liability",
    "governing",
    "termination",
    "nonsolicitation",
    "general",
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
            <span className="badge badge--accent">Developer Legal</span>
            <h1 style={{ fontSize: "2.4rem", lineHeight: 1.2, marginBottom: "0.5rem" }}>
              Terms and Conditions for Developers
            </h1>
            <p style={{ opacity: 0.7, marginBottom: "0.25rem" }}>
              <strong>Cape Craft Projects CC</strong>, trading as <strong>CapeControl</strong>
            </p>
            <p style={{ opacity: 0.6, marginBottom: "1.5rem", fontSize: "0.9rem" }}>
              Effective Date: February 14, 2026 &nbsp;|&nbsp; Version 1.0
            </p>

            <p style={{ marginBottom: "1.5rem" }}>
              This Terms and Conditions Agreement (&ldquo;Agreement&rdquo;) governs the relationship between
              Cape Craft Projects CC, trading as CapeControl (&ldquo;Agency&rdquo;), a Close Corporation
              registered in the Republic of South Africa, and the undersigned developer (&ldquo;Developer&rdquo;
              or &ldquo;You&rdquo;), an independent contractor providing development services to the Agency. By
              signing this Agreement or clicking &ldquo;Accept&rdquo; in the Agency&rsquo;s onboarding portal, You
              confirm that You have read, understood, and agree to be bound by its terms.
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
                    <li><strong>1.1 &ldquo;Agreement&rdquo;</strong> means this Terms and Conditions document, including any amendments made in accordance with Section 12.2.</li>
                    <li><strong>1.2 &ldquo;Client&rdquo;</strong> means any third party for whom the Agency provides services and to whom a Project relates.</li>
                    <li><strong>1.3 &ldquo;Confidential Information&rdquo;</strong> means all non-public information disclosed by the Agency or its Clients to the Developer, whether orally, in writing, or electronically, including but not limited to client data, business strategies, technical specifications, project details, pricing, and proprietary processes.</li>
                    <li><strong>1.4 &ldquo;Deliverables&rdquo;</strong> means all tangible and intangible outputs produced by the Developer under a Project Brief, including code, documentation, designs, models, and reports.</li>
                    <li><strong>1.5 &ldquo;Project&rdquo;</strong> means a specific engagement assigned to the Developer under this Agreement, governed by its own Project Brief.</li>
                    <li><strong>1.6 &ldquo;Project Brief&rdquo;</strong> means the written document issued by the Agency for each Project, specifying requirements, deliverables, timelines, acceptance criteria, and compensation.</li>
                    <li><strong>1.7 &ldquo;Work Product&rdquo;</strong> means all Deliverables, including all code, designs, algorithms, documentation, and other materials created by the Developer in the course of performing a Project.</li>
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
                  <p><strong>2.1 Engagement.</strong> The Agency may engage You to provide development services, including but not limited to designing, coding, testing, debugging, and deploying agent-based solutions (e.g., AI agents, chatbots, automation tools, workflow integrations) for the Agency&rsquo;s Clients.</p>
                  <p><strong>2.2 Project Assignments.</strong> Projects will be assigned based on Your skills, availability, and the Agency&rsquo;s needs. Each Project will be governed by a separate Project Brief. In the event of a conflict between this Agreement and a Project Brief, the Project Brief shall prevail with respect to that specific Project, except where the Project Brief attempts to override Sections 4, 5, 8, or 9 of this Agreement.</p>
                  <p><strong>2.3 Independent Contractor Status.</strong> You are an independent contractor, not an employee, partner, joint venturer, or agent of the Agency. Nothing in this Agreement creates an employment relationship, partnership, or agency. You are solely responsible for:</p>
                  <div style={subStyle}>
                    <p>(a) Your own taxes, including income tax, Value-Added Tax (VAT) where applicable, and any contributions required by the South African Revenue Service (SARS) or the equivalent tax authority in Your jurisdiction;</p>
                    <p>(b) Your own health insurance, liability insurance, and other benefits;</p>
                    <p>(c) Compliance with all applicable laws and regulations in Your jurisdiction;</p>
                    <p>(d) Obtaining any permits, licences, or registrations required for Your services.</p>
                  </div>
                  <p><strong>2.4 No Exclusivity.</strong> Unless otherwise stated in a Project Brief, this Agreement is non-exclusive. You are free to provide services to other parties, provided such work does not conflict with Your obligations under this Agreement, including confidentiality and non-competition provisions applicable to active Projects.</p>
                </div>
              )}
            </div>

            {/* ---- §3 Developer Obligations ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("obligations")} aria-expanded={isOpen("obligations")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("obligations")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>3. Developer Obligations</h2>
              </button>
              {isOpen("obligations") && (
                <div style={bodyStyle}>
                  <p><strong>3.1 Standard of Performance.</strong> You agree to perform all services professionally, diligently, and in accordance with generally accepted industry standards, the applicable Project Brief, and the Agency&rsquo;s published guidelines and coding standards.</p>
                  <p><strong>3.2 Communication and Availability.</strong> You will:</p>
                  <div style={subStyle}>
                    <p>(a) Communicate Your availability for Projects promptly and accurately;</p>
                    <p>(b) Meet all agreed-upon deadlines as specified in the Project Brief;</p>
                    <p>(c) Report any anticipated delays to the Agency within 24 hours of becoming aware of such delays, along with a proposed revised timeline;</p>
                    <p>(d) Respond to Agency communications within one (1) business day unless otherwise agreed.</p>
                  </div>
                  <p><strong>3.3 Tools and Resources.</strong> You are responsible for providing Your own equipment, software licences, internet connectivity, and development resources unless otherwise specified in the Project Brief. The Agency may provide access to specific tools, platforms, or environments as needed for a Project, subject to the Agency&rsquo;s usage policies.</p>
                  <p><strong>3.4 Legal and Regulatory Compliance.</strong> You will comply with all applicable laws and regulations, including but not limited to:</p>
                  <div style={subStyle}>
                    <p>(a) Data protection and privacy regulations, including the Protection of Personal Information Act, 2013 (POPIA), and where applicable, GDPR, CCPA, or other international data protection laws;</p>
                    <p>(b) Export control and sanctions laws;</p>
                    <p>(c) Anti-bribery and anti-corruption laws, including the Prevention and Combating of Corrupt Activities Act, 2004;</p>
                    <p>(d) The Agency&rsquo;s published policies on code quality, security standards, and professional ethics.</p>
                  </div>
                  <p><strong>3.5 Background Checks.</strong> The Agency reserves the right to conduct background checks or request professional references prior to assigning Projects, subject to applicable law, including POPIA.</p>
                </div>
              )}
            </div>

            {/* ---- §4 Compensation ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("compensation")} aria-expanded={isOpen("compensation")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("compensation")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>4. Compensation</h2>
              </button>
              {isOpen("compensation") && (
                <div style={bodyStyle}>
                  <p><strong>4.1 Payment Terms.</strong> Compensation for each Project will be specified in the applicable Project Brief. Payment structures may include:</p>
                  <div style={subStyle}>
                    <p>(a) <strong>Hourly Rate:</strong> Based on hours worked and tracked in an Agency-approved time-tracking tool;</p>
                    <p>(b) <strong>Fixed Rate:</strong> A flat fee for completion of specified Deliverables;</p>
                    <p>(c) <strong>Milestone-Based:</strong> Payments tied to the completion and acceptance of defined milestones.</p>
                  </div>
                  <p><strong>4.2 Invoicing.</strong> You must submit invoices for completed work in accordance with the schedule and format specified in the Project Brief. Each invoice must include, at minimum:</p>
                  <div style={subStyle}>
                    <p>(a) Your legal name and contact information;</p>
                    <p>(b) Invoice number and date;</p>
                    <p>(c) Description of work performed and the applicable Project;</p>
                    <p>(d) Hours worked (for hourly engagements) or milestones completed;</p>
                    <p>(e) Pre-approved expenses, if any, with supporting receipts;</p>
                    <p>(f) Total amount due;</p>
                    <p>(g) VAT registration number and VAT amount, if applicable.</p>
                  </div>
                  <p><strong>4.3 Payment Schedule.</strong> The Agency will process payments within 30 calendar days of receiving a valid and undisputed invoice. Payments are subject to:</p>
                  <div style={subStyle}>
                    <p>(a) Satisfactory completion and Agency review of the applicable Deliverables;</p>
                    <p>(b) Client approval, where required by the Project Brief;</p>
                    <p>(c) Your compliance with the terms of this Agreement.</p>
                  </div>
                  <p>Payments will be made via EFT bank transfer or an agreed electronic payment method in South African Rand (ZAR) unless otherwise agreed in the Project Brief. If payments are made in a foreign currency, the applicable exchange rate and any conversion fees will be specified in the Project Brief.</p>
                  <p><strong>4.4 Expenses.</strong> The Agency will reimburse only those expenses that have been pre-approved in writing and are documented with receipts. Unapproved expenses will not be reimbursed.</p>
                  <p><strong>4.5 Taxes.</strong> You are solely responsible for all taxes, levies, and contributions arising from payments received under this Agreement. You will provide the Agency with any required tax documentation prior to Your first payment, including Your tax registration number and, if applicable, VAT registration number.</p>
                  <p><strong>4.6 Payment Disputes.</strong> Any payment disputes must be raised in writing within fourteen (14) calendar days of invoice submission. The Agency reserves the right to withhold payment for Deliverables that are materially non-compliant with the Project Brief or incomplete, until the dispute is resolved through good-faith discussion. If the dispute cannot be resolved within thirty (30) days, either party may pursue the remedies described in Section 11.</p>
                  <p><strong>4.7 Late Payments.</strong> If the Agency fails to pay an undisputed invoice within the period specified in Section 4.3, the Developer is entitled to charge interest at a rate of 1.5% per month (or the maximum rate permitted by applicable South African law, whichever is lower) on the overdue amount, calculated from the date payment was due.</p>
                </div>
              )}
            </div>

            {/* ---- §5 Confidentiality ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("confidentiality")} aria-expanded={isOpen("confidentiality")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("confidentiality")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>5. Confidentiality</h2>
              </button>
              {isOpen("confidentiality") && (
                <div style={bodyStyle}>
                  <p><strong>5.1 Obligations.</strong> You agree to:</p>
                  <div style={subStyle}>
                    <p>(a) Keep all Confidential Information strictly confidential;</p>
                    <p>(b) Not disclose Confidential Information to any third party without the Agency&rsquo;s prior written consent;</p>
                    <p>(c) Use Confidential Information solely for the purpose of performing Your obligations under this Agreement;</p>
                    <p>(d) Restrict access to Confidential Information to those who have a need to know and who are bound by confidentiality obligations no less restrictive than those contained herein.</p>
                  </div>
                  <p><strong>5.2 Exceptions.</strong> Confidential Information does not include information that:</p>
                  <div style={subStyle}>
                    <p>(a) Is or becomes publicly available through no fault of the Developer;</p>
                    <p>(b) Was known to the Developer prior to disclosure, as demonstrated by written records;</p>
                    <p>(c) Is independently developed by the Developer without use of or reference to the Confidential Information;</p>
                    <p>(d) Is disclosed to the Developer by a third party who is not bound by a confidentiality obligation to the Agency;</p>
                    <p>(e) Is required to be disclosed by law, regulation, or court order, provided You give the Agency prompt written notice (where legally permitted) and cooperate with the Agency&rsquo;s efforts to seek protective measures.</p>
                  </div>
                  <p><strong>5.3 Non-Disclosure Agreement (NDA).</strong> If required by the Agency or a Client, You will sign a separate NDA for specific Projects. Any such NDA supplements, and does not replace, the confidentiality obligations in this Section.</p>
                  <p><strong>5.4 Data Security.</strong> You will implement reasonable and appropriate technical and organizational measures to protect Confidential Information, including but not limited to:</p>
                  <div style={subStyle}>
                    <p>(a) Encrypted storage and secure transmission of data;</p>
                    <p>(b) Use of strong, unique passwords and multi-factor authentication;</p>
                    <p>(c) Regular software and security updates;</p>
                    <p>(d) Secure disposal of data when no longer needed.</p>
                  </div>
                  <p><strong>5.5 Breach Notification.</strong> You must notify the Agency within 24 hours of becoming aware of any actual or suspected breach of confidentiality or unauthorized access to Confidential Information. Where a breach involves personal information as defined by POPIA, the Agency shall be responsible for notifying the Information Regulator to the extent required by law, and You will cooperate fully with such notification process.</p>
                  <p><strong>5.6 Duration.</strong> Confidentiality obligations under this Section survive the termination or expiration of this Agreement for a period of 5 years, or indefinitely with respect to trade secrets to the extent permitted by applicable law.</p>
                </div>
              )}
            </div>

            {/* ---- §6 Intellectual Property ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("ip")} aria-expanded={isOpen("ip")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("ip")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>6. Intellectual Property</h2>
              </button>
              {isOpen("ip") && (
                <div style={bodyStyle}>
                  <p><strong>6.1 Ownership of Work Product.</strong> All Work Product created by You in the course of performing a Project is considered &ldquo;work made for hire&rdquo; to the maximum extent permitted by South African law, including the Copyright Act, 1978 (Act No. 98 of 1978). To the extent any Work Product does not automatically vest in the Agency under applicable law, You hereby irrevocably assign to the Agency all right, title, and interest in and to such Work Product worldwide, including all copyrights, patents, trade secrets, and other intellectual property rights. You agree to execute any documents and take any actions reasonably requested by the Agency to effectuate or confirm such assignment.</p>
                  <p><strong>6.2 Moral Rights.</strong> To the extent permitted by applicable law, You waive any and all moral rights in the Work Product, including rights of attribution and integrity.</p>
                  <p><strong>6.3 Pre-Existing Materials.</strong> If You propose to incorporate any pre-existing materials into the Work Product (including but not limited to open-source code, third-party libraries, or Your own proprietary tools), You must:</p>
                  <div style={subStyle}>
                    <p>(a) Disclose all such materials to the Agency in writing before incorporation;</p>
                    <p>(b) Identify the applicable licence terms for each item;</p>
                    <p>(c) Obtain the Agency&rsquo;s written approval before incorporation;</p>
                    <p>(d) Ensure that the use of such materials does not impose any obligations on the Agency or its Clients that conflict with this Agreement (e.g., copyleft obligations).</p>
                  </div>
                  <p>Upon approval, You grant the Agency and its Clients a perpetual, irrevocable, worldwide, royalty-free, non-exclusive licence to use, modify, sublicence, and distribute such pre-existing materials as part of the Work Product.</p>
                  <p><strong>6.4 Agency and Third-Party Materials.</strong> Any materials, tools, platforms, or intellectual property provided by the Agency or its Clients remain the exclusive property of the Agency or the applicable Client. You may use such materials solely for the purpose of performing the applicable Project and must return or delete them upon Project completion or termination.</p>
                  <p><strong>6.5 Portfolio Use.</strong> You may reference or showcase the Work Product in Your professional portfolio only with the Agency&rsquo;s prior written approval. Any permitted portfolio use must:</p>
                  <div style={subStyle}>
                    <p>(a) Not disclose Confidential Information or identify a Client without that Client&rsquo;s consent;</p>
                    <p>(b) Comply with any restrictions specified by the Agency;</p>
                    <p>(c) Include appropriate attribution to the Agency, if requested.</p>
                  </div>
                </div>
              )}
            </div>

            {/* ---- §7 Quality Assurance and Acceptance ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("qa")} aria-expanded={isOpen("qa")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("qa")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>7. Quality Assurance and Acceptance</h2>
              </button>
              {isOpen("qa") && (
                <div style={bodyStyle}>
                  <p><strong>7.1 Standards.</strong> All Deliverables must meet the specifications, acceptance criteria, and quality standards defined in the applicable Project Brief. In the absence of specific standards, Deliverables must conform to generally accepted industry practices.</p>
                  <p><strong>7.2 Review Process.</strong> The Agency will review submitted Deliverables and provide written feedback within 10 business days of submission. Feedback may include approval, conditional approval with minor corrections, or rejection with detailed reasons.</p>
                  <p><strong>7.3 Revisions.</strong> You agree to make reasonable revisions to Deliverables that do not meet the requirements specified in the Project Brief, at no additional cost, within 7 business days of receiving feedback. &ldquo;Reasonable revisions&rdquo; means corrections to bring Deliverables into compliance with the original Project Brief specifications, and does not include changes to scope or requirements not originally agreed upon.</p>
                  <p><strong>7.4 Scope Changes.</strong> Any changes to the scope, requirements, or specifications beyond the original Project Brief require a written amendment to the Project Brief, agreed upon by both parties, which may include adjustments to timelines and compensation.</p>
                  <p><strong>7.5 Client Approval.</strong> Final acceptance of Deliverables may be subject to Client approval, as specified in the Project Brief. The Agency will communicate Client feedback to You in a timely manner. If Client approval is unreasonably delayed (beyond 30 calendar days of final submission without feedback), the Deliverables shall be deemed accepted for purposes of payment.</p>
                </div>
              )}
            </div>

            {/* ---- §8 Warranties and Representations ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("warranties")} aria-expanded={isOpen("warranties")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("warranties")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>8. Warranties and Representations</h2>
              </button>
              {isOpen("warranties") && (
                <div style={bodyStyle}>
                  <p><strong>8.1 Developer Warranties.</strong> You represent and warrant that:</p>
                  <div style={subStyle}>
                    <p>(a) You have the legal capacity and authority to enter into this Agreement and perform the services;</p>
                    <p>(b) Your services will be performed competently, in a professional and workmanlike manner, and in accordance with the applicable Project Brief;</p>
                    <p>(c) The Work Product will be original to You (except for disclosed pre-existing materials) and will not infringe, misappropriate, or violate any third party&rsquo;s intellectual property rights, privacy rights, or other legal rights;</p>
                    <p>(d) You will not introduce any malicious code, viruses, backdoors, or unauthorized data collection mechanisms into the Work Product;</p>
                    <p>(e) Any pre-existing materials incorporated into the Work Product are properly licenced and disclosed in accordance with Section 6.3;</p>
                    <p>(f) You are not subject to any agreement, obligation, or restriction that would prevent You from fulfilling Your obligations under this Agreement.</p>
                  </div>
                  <p><strong>8.2 Agency Warranties.</strong> The Agency represents and warrants that:</p>
                  <div style={subStyle}>
                    <p>(a) It has the authority to enter into this Agreement;</p>
                    <p>(b) It will provide reasonably clear Project Briefs and timely feedback on Deliverables;</p>
                    <p>(c) It will process payments in accordance with Section 4 of this Agreement.</p>
                  </div>
                  <p><strong>8.3 Disclaimer.</strong> Except as expressly stated in this Agreement, the Agency makes no warranties, express or implied, including but not limited to implied warranties of merchantability or fitness for a particular purpose, regarding the volume, continuity, or nature of Projects available.</p>
                </div>
              )}
            </div>

            {/* ---- §9 Indemnification ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("indemnification")} aria-expanded={isOpen("indemnification")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("indemnification")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>9. Indemnification</h2>
              </button>
              {isOpen("indemnification") && (
                <div style={bodyStyle}>
                  <p><strong>9.1 Developer Indemnification.</strong> You agree to indemnify, defend, and hold harmless the Agency, its officers, directors, employees, agents, and Clients from and against any and all claims, damages, losses, liabilities, costs, and expenses (including reasonable attorney fees) arising from or related to:</p>
                  <div style={subStyle}>
                    <p>(a) Your breach of any term of this Agreement;</p>
                    <p>(b) Your negligent or wilful misconduct;</p>
                    <p>(c) Any claim that the Work Product infringes or misappropriates a third party&rsquo;s intellectual property or other rights;</p>
                    <p>(d) Your failure to comply with applicable laws or regulations;</p>
                    <p>(e) Any tax liability or penalty arising from Your misclassification or failure to pay required taxes.</p>
                  </div>
                  <p><strong>9.2 Agency Indemnification.</strong> The Agency agrees to indemnify, defend, and hold harmless the Developer from and against any and all claims, damages, losses, liabilities, costs, and expenses (including reasonable attorney fees) arising from or related to:</p>
                  <div style={subStyle}>
                    <p>(a) The Agency&rsquo;s breach of any term of this Agreement;</p>
                    <p>(b) Claims arising from the Agency&rsquo;s use of the Work Product in a manner not contemplated by the applicable Project Brief;</p>
                    <p>(c) The Agency&rsquo;s negligent or wilful misconduct.</p>
                  </div>
                  <p><strong>9.3 Indemnification Procedure.</strong> The indemnified party must: (a) provide prompt written notice of any claim; (b) grant the indemnifying party sole control of the defence and settlement; and (c) provide reasonable cooperation at the indemnifying party&rsquo;s expense. The indemnifying party may not settle any claim that imposes obligations on the indemnified party without the indemnified party&rsquo;s prior written consent.</p>
                </div>
              )}
            </div>

            {/* ---- §10 Limitation of Liability ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("liability")} aria-expanded={isOpen("liability")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("liability")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>10. Limitation of Liability</h2>
              </button>
              {isOpen("liability") && (
                <div style={bodyStyle}>
                  <p><strong>10.1 Liability Cap.</strong> To the maximum extent permitted by applicable law, each party&rsquo;s total aggregate liability to the other under this Agreement shall not exceed the total amount paid or payable to the Developer for the specific Project giving rise to the claim in the twelve (12) months preceding the event that gave rise to the liability.</p>
                  <p><strong>10.2 Exclusion of Damages.</strong> Neither party shall be liable for any indirect, incidental, consequential, special, punitive, or exemplary damages, including but not limited to loss of profits, revenue, data, or business opportunities, regardless of the cause of action or the theory of liability, even if such party has been advised of the possibility of such damages.</p>
                  <p><strong>10.3 Exceptions.</strong> The limitations in Sections 10.1 and 10.2 shall not apply to:</p>
                  <div style={subStyle}>
                    <p>(a) Breaches of confidentiality obligations under Section 5;</p>
                    <p>(b) Intellectual property infringement claims;</p>
                    <p>(c) Indemnification obligations under Section 9;</p>
                    <p>(d) Fraud or wilful misconduct;</p>
                    <p>(e) The Developer&rsquo;s obligations under Section 4.5 (Taxes).</p>
                  </div>
                  <p><strong>10.4 No Guarantees of Work.</strong> The Agency does not guarantee a minimum number of Projects, minimum compensation, or continuous engagement. The Agency&rsquo;s decision to assign or not assign Projects is at its sole discretion.</p>
                </div>
              )}
            </div>

            {/* ---- §11 Governing Law and Dispute Resolution ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("governing")} aria-expanded={isOpen("governing")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("governing")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>11. Governing Law and Dispute Resolution</h2>
              </button>
              {isOpen("governing") && (
                <div style={bodyStyle}>
                  <p><strong>11.1 Governing Law.</strong> This Agreement shall be governed by and construed in accordance with the laws of the Republic of South Africa, without regard to its conflict of laws principles.</p>
                  <p><strong>11.2 Jurisdiction.</strong> The parties hereby submit to the exclusive jurisdiction of the High Court of South Africa, Western Cape Division, Cape Town, or such other competent court in Cape Town, South Africa, for the resolution of any disputes arising out of or in connection with this Agreement. Each party irrevocably waives any objection to the laying of venue in such courts and any claim that any action or proceeding brought in such courts has been brought in an inconvenient forum.</p>
                  <p><strong>11.3 Informal Resolution.</strong> Before initiating any formal dispute resolution process, the parties agree to attempt to resolve any dispute through good-faith negotiation for a period of at least thirty (30) calendar days following written notice of the dispute.</p>
                  <p><strong>11.4 Mediation.</strong> If the dispute cannot be resolved through negotiation, the parties agree to submit the dispute to mediation administered by the Arbitration Foundation of Southern Africa (AFSA) or another mutually agreed mediation body, with mediation proceedings to be held in Cape Town, South Africa, before pursuing arbitration or litigation.</p>
                  <p><strong>11.5 Arbitration.</strong> If mediation is unsuccessful within thirty (30) calendar days of its commencement (or such longer period as the parties may agree), the dispute shall be referred to and finally resolved by binding arbitration conducted in Cape Town, South Africa, under the rules of the Arbitration Foundation of Southern Africa (AFSA). The arbitration shall be conducted by a single arbitrator, unless the parties agree otherwise. The language of the arbitration shall be English. The arbitrator&rsquo;s award shall be final and binding and may be entered as a judgment in any court of competent jurisdiction, including the High Court of South Africa, Western Cape Division, Cape Town.</p>
                  <p><strong>11.6 Attorney Fees.</strong> The prevailing party in any legal action, arbitration, or proceeding arising out of this Agreement shall be entitled to recover its reasonable attorney fees, costs, and other collection expenses from the non-prevailing party, to the extent permitted by South African law.</p>
                  <p><strong>11.7 Injunctive Relief.</strong> Notwithstanding any other provision in this Section, either party may seek urgent interim relief, including an interdict or other equitable relief, in the High Court of South Africa, Western Cape Division, Cape Town, or any other court of competent jurisdiction, to prevent the actual or threatened breach of Sections 5 or 6 of this Agreement, without the requirement to first pursue negotiation, mediation, or arbitration, and without being required to prove actual damages.</p>
                  <p><strong>11.8 Consumer Protection.</strong> Nothing in this Section shall be construed to limit any rights the Developer may have under the Consumer Protection Act, 2008 (Act No. 68 of 2008), to the extent applicable.</p>
                </div>
              )}
            </div>

            {/* ---- §12 Termination ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("termination")} aria-expanded={isOpen("termination")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("termination")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>12. Termination</h2>
              </button>
              {isOpen("termination") && (
                <div style={bodyStyle}>
                  <p><strong>12.1 Termination for Convenience.</strong> Either party may terminate this Agreement with 14 calendar days&rsquo; written notice, provided that all obligations related to active Projects are fulfilled or a mutually agreed transition plan is in place.</p>
                  <p><strong>12.2 Termination for Cause.</strong> Either party may terminate this Agreement immediately upon written notice if the other party:</p>
                  <div style={subStyle}>
                    <p>(a) Commits a material breach of any term of this Agreement and fails to cure such breach within 14 calendar days of receiving written notice specifying the breach; or</p>
                    <p>(b) Commits a breach that is incapable of cure (e.g., breach of confidentiality, intellectual property infringement, fraud).</p>
                  </div>
                  <p><strong>12.3 Project Termination.</strong> The Agency may terminate a specific Project with written notice if:</p>
                  <div style={subStyle}>
                    <p>(a) The Client cancels the Project;</p>
                    <p>(b) The Developer fails to meet material obligations under the Project Brief;</p>
                    <p>(c) Circumstances beyond the Agency&rsquo;s control make the Project unfeasible.</p>
                  </div>
                  <p>Upon Project termination, You will be compensated for Deliverables satisfactorily completed and accepted up to the effective date of termination, in accordance with Section 4.</p>
                  <p><strong>12.4 Post-Termination Obligations.</strong> Upon termination or expiration of this Agreement:</p>
                  <div style={subStyle}>
                    <p>(a) You must immediately return or, at the Agency&rsquo;s direction, securely destroy all Confidential Information, Agency materials, and Client materials in Your possession;</p>
                    <p>(b) You must provide written certification of such return or destruction within 7 calendar days;</p>
                    <p>(c) You must cease all use of Agency resources, systems, and accounts;</p>
                    <p>(d) Sections 1, 4 (for amounts owed), 5, 6, 8, 9, 10, 11, and this Section 12.4 shall survive termination or expiration of this Agreement.</p>
                  </div>
                </div>
              )}
            </div>

            {/* ---- §13 Non-Solicitation ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("nonsolicitation")} aria-expanded={isOpen("nonsolicitation")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("nonsolicitation")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>13. Non-Solicitation</h2>
              </button>
              {isOpen("nonsolicitation") && (
                <div style={bodyStyle}>
                  <p><strong>13.1</strong> During the term of this Agreement and for 12 months following its termination, You agree not to directly solicit or attempt to solicit any Client of the Agency with whom You had contact through a Project, for the purpose of providing services that compete with or are substantially similar to those offered by the Agency.</p>
                  <p><strong>13.2</strong> This restriction does not apply if the Client independently contacts You without solicitation, or if the Agency provides prior written consent.</p>
                  <p><strong>13.3</strong> The parties acknowledge that the duration, scope, and geographic reach of the restriction in Section 13.1 are reasonable and necessary to protect the Agency&rsquo;s legitimate business interests. However, if any court or tribunal of competent jurisdiction determines that the restriction is unreasonable, the parties agree that such court or tribunal may modify the restriction to the minimum extent necessary to render it enforceable.</p>
                </div>
              )}
            </div>

            {/* ---- §14 General Provisions ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("general")} aria-expanded={isOpen("general")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("general")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>14. General Provisions</h2>
              </button>
              {isOpen("general") && (
                <div style={bodyStyle}>
                  <p><strong>14.1 Entire Agreement.</strong> This Agreement, together with all Project Briefs and any NDAs executed pursuant hereto, constitutes the entire understanding between the parties with respect to its subject matter and supersedes all prior and contemporaneous agreements, negotiations, representations, and understandings, whether written or oral.</p>
                  <p><strong>14.2 Amendments.</strong> The Agency may amend this Agreement by providing You with 30 calendar days&rsquo; written notice of the proposed changes. If You do not agree to the amendments, You may terminate this Agreement within the notice period. Continued engagement after the effective date of the amendments constitutes Your acceptance.</p>
                  <p><strong>14.3 Assignment.</strong> You may not assign, transfer, or delegate this Agreement or any of Your rights or obligations hereunder without the Agency&rsquo;s prior written consent. The Agency may assign this Agreement in connection with a merger, acquisition, or sale of substantially all of its assets.</p>
                  <p><strong>14.4 Force Majeure.</strong> Neither party shall be liable for any failure or delay in performing its obligations under this Agreement (other than payment obligations) to the extent such failure or delay results from circumstances beyond the party&rsquo;s reasonable control, including but not limited to natural disasters, pandemics, war, terrorism, government actions, load shedding or prolonged power outages, internet outages, or infrastructure failures. The affected party must provide prompt written notice and use reasonable efforts to mitigate the impact.</p>
                  <p><strong>14.5 Severability.</strong> If any provision of this Agreement is found to be invalid, illegal, or unenforceable by a court of competent jurisdiction, such provision shall be modified to the minimum extent necessary to make it enforceable, or if modification is not possible, shall be severed from this Agreement. The remaining provisions shall continue in full force and effect.</p>
                  <p><strong>14.6 Waiver.</strong> The failure of either party to enforce any provision of this Agreement shall not constitute a waiver of that party&rsquo;s right to enforce that provision or any other provision in the future.</p>
                  <p><strong>14.7 Notices.</strong> All formal notices under this Agreement must be in writing and delivered via email (with read receipt or confirmation of delivery) or registered mail to the addresses specified below or as subsequently updated in writing.</p>
                  <p><strong>14.8 Relationship of the Parties.</strong> Nothing in this Agreement shall be construed to create a joint venture, partnership, franchise, or agency relationship between the parties. Neither party has the authority to bind or commit the other party in any way.</p>
                  <p><strong>14.9 Counterparts.</strong> This Agreement may be executed in counterparts, including electronic counterparts, each of which shall be deemed an original, and all of which together shall constitute one and the same instrument. Electronic signatures shall be deemed valid and binding to the extent permitted by the Electronic Communications and Transactions Act, 2002 (Act No. 25 of 2002).</p>
                  <p><strong>14.10 POPIA Compliance.</strong> To the extent that the Developer processes personal information (as defined in POPIA) in the course of performing services under this Agreement, the Developer shall do so solely as an operator (as defined in POPIA) on behalf of the Agency, and shall comply with all applicable provisions of POPIA. The Agency and the Developer shall enter into a separate data processing agreement if required by the scope of the personal information processed.</p>
                </div>
              )}
            </div>

            {/* ---- §15 Acceptance ---- */}
            <div style={sectionStyle}>
              <button type="button" style={headerStyle} onClick={() => toggle("acceptance")} aria-expanded={isOpen("acceptance")}>
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("acceptance")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>15. Acceptance</h2>
              </button>
              {isOpen("acceptance") && (
                <div style={bodyStyle}>
                  <p>By signing below or clicking &ldquo;Accept&rdquo; in the Agency&rsquo;s onboarding portal, You acknowledge that You have read this Agreement in its entirety, have had the opportunity to seek independent legal advice, and agree to be bound by its terms.</p>
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
                Register as Developer
              </Link>
              <Link
                to="/developers"
                className="btn btn--ghost"
                style={{ textAlign: "center" }}
              >
                Developer Information
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
              only and does not constitute legal advice. The Agency should have the final version
              reviewed by a qualified South African attorney to ensure full compliance with all
              applicable laws, including but not limited to POPIA, the Copyright Act, the Labour
              Relations Act, the Basic Conditions of Employment Act, and SARS requirements. This
              Agreement governs the independent contractor relationship between the Agency and
              Developer. It does not create an employment relationship. Developers are encouraged to
              seek independent legal and tax advice before accepting these terms.
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
                <li><Link to="/developers">Developer Info</Link></li>
                <li><Link to="/developer-terms">Developer T&amp;Cs</Link></li>
                <li><Link to="/terms-and-conditions">Customer T&amp;Cs</Link></li>
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

export default DeveloperTermsPage;

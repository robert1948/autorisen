import React, { useState } from "react";
import { Link } from "react-router-dom";
import TopNav from "../../components/nav/TopNav";
import logoUrl from "../../assets/capecontrol-logo.png";
import BuildBadge from "../../components/version/BuildBadge";

type SectionKey =
  | "overview"
  | "collection"
  | "use"
  | "sharing"
  | "security"
  | "retention"
  | "cookies"
  | "rights"
  | "children"
  | "international"
  | "changes"
  | "contact";

const PrivacyPolicyPage: React.FC = () => {
  const [openSections, setOpenSections] = useState<Set<SectionKey>>(
    new Set<SectionKey>(["overview"])
  );

  const allKeys: SectionKey[] = [
    "overview",
    "collection",
    "use",
    "sharing",
    "security",
    "retention",
    "cookies",
    "rights",
    "children",
    "international",
    "changes",
    "contact",
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

      <main style={{ maxWidth: 900, margin: "0 auto", padding: "6rem 1.5rem 4rem" }}>
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: "3rem" }}>
          <img src={logoUrl} alt="CapeControl" width={56} height={56} style={{ marginBottom: "1rem" }} />
          <h1 style={{ fontSize: "2.25rem", fontWeight: 700, marginBottom: "0.5rem" }}>Privacy Policy</h1>
          <p style={{ opacity: 0.6, fontSize: "0.95rem" }}>
            Effective date: 1 March 2026 &nbsp;|&nbsp; Last updated: 4 March 2026
          </p>
          <p style={{ opacity: 0.5, fontSize: "0.85rem", marginTop: "0.5rem" }}>
            Cape Craft Projects CC (trading as CapeControl) &bull; VAT 4270105119 &bull; South Africa
          </p>
        </div>

        {/* Controls */}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem", marginBottom: "1.5rem" }}>
          <button
            type="button"
            onClick={expandAll}
            style={{ background: "none", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 8, padding: "0.4rem 0.8rem", cursor: "pointer", color: "inherit", fontSize: "0.85rem" }}
          >
            Expand all
          </button>
          <button
            type="button"
            onClick={collapseAll}
            style={{ background: "none", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 8, padding: "0.4rem 0.8rem", cursor: "pointer", color: "inherit", fontSize: "0.85rem" }}
          >
            Collapse all
          </button>
        </div>

        {/* Sections */}
        <div>
          {/* ---- §1 Overview ---- */}
          <div style={sectionStyle}>
            <button type="button" style={headerStyle} onClick={() => toggle("overview")} aria-expanded={isOpen("overview")}>
              <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("overview")}</span>
              <h2 style={{ margin: 0, fontSize: "1.25rem" }}>1. Overview</h2>
            </button>
            {isOpen("overview") && (
              <div style={bodyStyle}>
                <p>Cape Craft Projects CC, trading as <strong>CapeControl</strong> (&ldquo;we&rdquo;, &ldquo;us&rdquo;, &ldquo;our&rdquo;), operates the CapeControl platform at <a href="https://cape-control.com" style={{ color: "#93c5fd" }}>cape-control.com</a>. This Privacy Policy explains how we collect, use, store, and protect your personal information when you use our platform, website, and related services (collectively, the &ldquo;Services&rdquo;).</p>
                <p>We are committed to complying with the Protection of Personal Information Act, 2013 (POPIA), and where applicable, the EU General Data Protection Regulation (GDPR), UK GDPR, and the California Consumer Privacy Act (CCPA).</p>
                <p>By using the Services, you consent to the collection and processing of your personal information as described in this policy. If you do not agree with these practices, please do not use the Services.</p>
              </div>
            )}
          </div>

          {/* ---- §2 Information We Collect ---- */}
          <div style={sectionStyle}>
            <button type="button" style={headerStyle} onClick={() => toggle("collection")} aria-expanded={isOpen("collection")}>
              <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("collection")}</span>
              <h2 style={{ margin: 0, fontSize: "1.25rem" }}>2. Information We Collect</h2>
            </button>
            {isOpen("collection") && (
              <div style={bodyStyle}>
                <p><strong>2.1. Information you provide directly:</strong></p>
                <div style={subStyle}>
                  <p>(a) Account registration details: name, email address, organisation name, and password.</p>
                  <p>(b) Profile information: job title, phone number, and communication preferences.</p>
                  <p>(c) Payment information: billing address and payment method details (processed by PayFast; we do not store full card numbers).</p>
                  <p>(d) Communications: messages you send to us via support channels, chat, or email.</p>
                  <p>(e) Content you upload: documents, agent configurations, and other materials submitted to the platform.</p>
                </div>
                <p><strong>2.2. Information collected automatically:</strong></p>
                <div style={subStyle}>
                  <p>(a) Usage data: pages visited, features used, timestamps, and interaction patterns.</p>
                  <p>(b) Device information: browser type, operating system, screen resolution, and device identifiers.</p>
                  <p>(c) Network data: IP address, approximate geolocation (city/country level), and referring URLs.</p>
                  <p>(d) Cookies and similar technologies: session identifiers, authentication tokens, and preference cookies (see Section 7).</p>
                </div>
                <p><strong>2.3. Information from third parties:</strong></p>
                <div style={subStyle}>
                  <p>(a) OAuth providers (Google, LinkedIn): name, email, and profile picture when you choose social login.</p>
                  <p>(b) Payment provider (PayFast): transaction status and payment confirmation details.</p>
                </div>
              </div>
            )}
          </div>

          {/* ---- §3 How We Use Your Information ---- */}
          <div style={sectionStyle}>
            <button type="button" style={headerStyle} onClick={() => toggle("use")} aria-expanded={isOpen("use")}>
              <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("use")}</span>
              <h2 style={{ margin: 0, fontSize: "1.25rem" }}>3. How We Use Your Information</h2>
            </button>
            {isOpen("use") && (
              <div style={bodyStyle}>
                <p>We process your personal information for the following purposes:</p>
                <div style={subStyle}>
                  <p>(a) <strong>Service delivery:</strong> To create and manage your account, provide access to the platform, process transactions, and deliver the Services you have requested.</p>
                  <p>(b) <strong>Platform improvement:</strong> To analyse usage patterns, diagnose technical issues, and improve the functionality, performance, and security of the platform.</p>
                  <p>(c) <strong>Communication:</strong> To send you service-related notifications, security alerts, billing updates, and respond to your enquiries.</p>
                  <p>(d) <strong>Legal compliance:</strong> To comply with applicable laws, regulations, legal processes, or enforceable governmental requests.</p>
                  <p>(e) <strong>Security:</strong> To detect, prevent, and address fraud, abuse, security risks, and technical issues.</p>
                  <p>(f) <strong>Marketing:</strong> With your opt-in consent only, to send product updates and promotional communications. You may opt out at any time.</p>
                </div>
              </div>
            )}
          </div>

          {/* ---- §4 Sharing and Disclosure ---- */}
          <div style={sectionStyle}>
            <button type="button" style={headerStyle} onClick={() => toggle("sharing")} aria-expanded={isOpen("sharing")}>
              <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("sharing")}</span>
              <h2 style={{ margin: 0, fontSize: "1.25rem" }}>4. Sharing and Disclosure</h2>
            </button>
            {isOpen("sharing") && (
              <div style={bodyStyle}>
                <p><strong>We do not sell your personal information to third parties.</strong></p>
                <p>We may share your information in the following limited circumstances:</p>
                <div style={subStyle}>
                  <p>(a) <strong>Service providers:</strong> With trusted third-party vendors who assist us in operating the platform (e.g., cloud hosting on Heroku/AWS, payment processing via PayFast, email delivery). These providers are contractually bound to protect your data and may only process it for the purposes we specify.</p>
                  <p>(b) <strong>AI model providers:</strong> Query content may be sent to third-party AI providers (e.g., Anthropic, OpenAI) for processing. We do not send personal identification data to AI providers unless you include it in your queries. AI providers are bound by data processing agreements.</p>
                  <p>(c) <strong>Legal requirements:</strong> When required by law, regulation, court order, or to protect the rights, property, or safety of CapeControl, our users, or the public.</p>
                  <p>(d) <strong>Business transfers:</strong> In connection with a merger, acquisition, or sale of assets, your information may be transferred as part of the transaction. We will notify you of any such change.</p>
                </div>
              </div>
            )}
          </div>

          {/* ---- §5 Data Security ---- */}
          <div style={sectionStyle}>
            <button type="button" style={headerStyle} onClick={() => toggle("security")} aria-expanded={isOpen("security")}>
              <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("security")}</span>
              <h2 style={{ margin: 0, fontSize: "1.25rem" }}>5. Data Security</h2>
            </button>
            {isOpen("security") && (
              <div style={bodyStyle}>
                <p>We implement reasonable technical and organisational measures to protect your personal information, including:</p>
                <div style={subStyle}>
                  <p>(a) <strong>Encryption:</strong> All data is encrypted in transit (TLS 1.2+) and at rest.</p>
                  <p>(b) <strong>Tenant isolation:</strong> Customer data is logically segregated per tenant. No customer can access another customer&rsquo;s data.</p>
                  <p>(c) <strong>Access controls:</strong> Role-based access with multi-factor authentication available. Administrative access is logged and audited.</p>
                  <p>(d) <strong>Audit trails:</strong> All significant actions are logged via our audit system for traceability and compliance.</p>
                  <p>(e) <strong>Regular review:</strong> We conduct periodic security reviews and vulnerability assessments.</p>
                </div>
                <p>No method of electronic transmission or storage is 100% secure. While we strive to protect your information, we cannot guarantee absolute security.</p>
              </div>
            )}
          </div>

          {/* ---- §6 Data Retention ---- */}
          <div style={sectionStyle}>
            <button type="button" style={headerStyle} onClick={() => toggle("retention")} aria-expanded={isOpen("retention")}>
              <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("retention")}</span>
              <h2 style={{ margin: 0, fontSize: "1.25rem" }}>6. Data Retention</h2>
            </button>
            {isOpen("retention") && (
              <div style={bodyStyle}>
                <p>We retain your personal information only for as long as necessary to fulfil the purposes described in this policy, or as required by law.</p>
                <div style={subStyle}>
                  <p>(a) <strong>Active accounts:</strong> Data is retained for the duration of your account and active subscription.</p>
                  <p>(b) <strong>After account deletion:</strong> Personal data is deleted or anonymised within 30 days of account deletion, except where retention is required for legal, tax, or audit obligations.</p>
                  <p>(c) <strong>Audit logs:</strong> Security and audit logs may be retained for up to 12 months for compliance and incident investigation purposes.</p>
                  <p>(d) <strong>Backups:</strong> Data may persist in encrypted backups for up to 90 days after deletion, after which it is permanently purged.</p>
                </div>
              </div>
            )}
          </div>

          {/* ---- §7 Cookies and Tracking ---- */}
          <div style={sectionStyle}>
            <button type="button" style={headerStyle} onClick={() => toggle("cookies")} aria-expanded={isOpen("cookies")}>
              <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("cookies")}</span>
              <h2 style={{ margin: 0, fontSize: "1.25rem" }}>7. Cookies and Tracking Technologies</h2>
            </button>
            {isOpen("cookies") && (
              <div style={bodyStyle}>
                <p>We use cookies and similar technologies for the following purposes:</p>
                <div style={subStyle}>
                  <p>(a) <strong>Essential cookies:</strong> Required for authentication, session management, and CSRF protection. These cannot be disabled.</p>
                  <p>(b) <strong>Functional cookies:</strong> Remember your preferences and settings (e.g., theme, language).</p>
                  <p>(c) <strong>Analytics cookies:</strong> Help us understand how you use the platform so we can improve it. Currently we do not use third-party analytics trackers.</p>
                </div>
                <p>You can control cookie settings through your browser. Disabling essential cookies may prevent the platform from functioning correctly.</p>
              </div>
            )}
          </div>

          {/* ---- §8 Your Rights ---- */}
          <div style={sectionStyle}>
            <button type="button" style={headerStyle} onClick={() => toggle("rights")} aria-expanded={isOpen("rights")}>
              <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("rights")}</span>
              <h2 style={{ margin: 0, fontSize: "1.25rem" }}>8. Your Rights</h2>
            </button>
            {isOpen("rights") && (
              <div style={bodyStyle}>
                <p>Depending on your jurisdiction, you may have the following rights regarding your personal information:</p>
                <div style={subStyle}>
                  <p>(a) <strong>Access:</strong> Request a copy of the personal information we hold about you.</p>
                  <p>(b) <strong>Correction:</strong> Request correction of inaccurate or incomplete personal information.</p>
                  <p>(c) <strong>Deletion:</strong> Request deletion of your personal information, subject to legal retention requirements.</p>
                  <p>(d) <strong>Portability:</strong> Request your data in a structured, machine-readable format.</p>
                  <p>(e) <strong>Objection:</strong> Object to certain processing of your personal information.</p>
                  <p>(f) <strong>Withdraw consent:</strong> Where processing is based on consent, withdraw your consent at any time.</p>
                </div>
                <p><strong>POPIA (South Africa):</strong> You have the right to lodge a complaint with the Information Regulator at <a href="https://inforegulator.org.za" style={{ color: "#93c5fd" }} target="_blank" rel="noopener noreferrer">inforegulator.org.za</a>.</p>
                <p><strong>GDPR (EU/UK):</strong> You have the right to lodge a complaint with your local data protection authority.</p>
                <p><strong>CCPA (California):</strong> You have the right to know what personal information is collected, request its deletion, and opt out of any sale of personal information (we do not sell personal information).</p>
                <p>To exercise any of these rights, contact us at <a href="mailto:privacy@capecontrol.ai" style={{ color: "#93c5fd" }}>privacy@capecontrol.ai</a>. We will respond within 30 days (or sooner as required by applicable law).</p>
              </div>
            )}
          </div>

          {/* ---- §9 Children's Privacy ---- */}
          <div style={sectionStyle}>
            <button type="button" style={headerStyle} onClick={() => toggle("children")} aria-expanded={isOpen("children")}>
              <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("children")}</span>
              <h2 style={{ margin: 0, fontSize: "1.25rem" }}>9. Children&rsquo;s Privacy</h2>
            </button>
            {isOpen("children") && (
              <div style={bodyStyle}>
                <p>The Services are not directed at individuals under the age of 18. We do not knowingly collect personal information from children. If we discover that we have collected personal information from a child, we will delete it promptly.</p>
              </div>
            )}
          </div>

          {/* ---- §10 International Data Transfers ---- */}
          <div style={sectionStyle}>
            <button type="button" style={headerStyle} onClick={() => toggle("international")} aria-expanded={isOpen("international")}>
              <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("international")}</span>
              <h2 style={{ margin: 0, fontSize: "1.25rem" }}>10. International Data Transfers</h2>
            </button>
            {isOpen("international") && (
              <div style={bodyStyle}>
                <p>Your personal information may be transferred to and processed in countries other than your own, including the United States (for cloud hosting and AI processing). We ensure appropriate safeguards are in place, including:</p>
                <div style={subStyle}>
                  <p>(a) Standard contractual clauses approved by the European Commission (for GDPR transfers).</p>
                  <p>(b) Data processing agreements with all sub-processors.</p>
                  <p>(c) Compliance with POPIA&rsquo;s requirements for trans-border information flows (Section 72).</p>
                </div>
              </div>
            )}
          </div>

          {/* ---- §11 Changes to This Policy ---- */}
          <div style={sectionStyle}>
            <button type="button" style={headerStyle} onClick={() => toggle("changes")} aria-expanded={isOpen("changes")}>
              <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("changes")}</span>
              <h2 style={{ margin: 0, fontSize: "1.25rem" }}>11. Changes to This Policy</h2>
            </button>
            {isOpen("changes") && (
              <div style={bodyStyle}>
                <p>We may update this Privacy Policy from time to time. When we make material changes, we will:</p>
                <div style={subStyle}>
                  <p>(a) Update the &ldquo;Last updated&rdquo; date at the top of this page.</p>
                  <p>(b) Notify you via email or an in-app notification for significant changes.</p>
                  <p>(c) Where required by law, obtain your renewed consent before processing your information under the updated policy.</p>
                </div>
                <p>We encourage you to review this policy periodically.</p>
              </div>
            )}
          </div>

          {/* ---- §12 Contact Us ---- */}
          <div style={sectionStyle}>
            <button type="button" style={headerStyle} onClick={() => toggle("contact")} aria-expanded={isOpen("contact")}>
              <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("contact")}</span>
              <h2 style={{ margin: 0, fontSize: "1.25rem" }}>12. Contact Us</h2>
            </button>
            {isOpen("contact") && (
              <div style={bodyStyle}>
                <p>If you have any questions, concerns, or requests regarding this Privacy Policy or our data practices, please contact us:</p>
                <div style={subStyle}>
                  <p><strong>Email:</strong> <a href="mailto:privacy@capecontrol.ai" style={{ color: "#93c5fd" }}>privacy@capecontrol.ai</a></p>
                  <p><strong>General support:</strong> <a href="mailto:support@capecontrol.ai" style={{ color: "#93c5fd" }}>support@capecontrol.ai</a></p>
                  <p><strong>Website:</strong> <a href="https://cape-control.com" style={{ color: "#93c5fd" }}>cape-control.com</a></p>
                </div>
                <p><strong>Information Officer:</strong> Robert Kleyn, Cape Craft Projects CC</p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* FOOTER */}
      <footer className="footer" data-analytics-section="footer">
        <div className="footer__content">
          <div className="footer__main">
            <div className="footer__brand">
              <img className="footer__logo" src={logoUrl} alt="CapeControl logo" width={44} height={44} loading="lazy" />
              <div>
                <h3>CapeControl</h3>
                <p className="footer__brand-meta">Operated by Cape Craft Projects CC (VAT: 4270105119)</p>
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
              <h4>Legal</h4>
              <ul className="footer__links-list">
                <li><Link to="/privacy-policy">Privacy Policy</Link></li>
                <li><Link to="/terms-and-conditions">Customer T&amp;Cs</Link></li>
                <li><Link to="/developer-terms">Developer T&amp;Cs</Link></li>
                <li><Link to="/customer-terms">Proposal Terms</Link></li>
              </ul>
            </div>
            <div className="footer__column">
              <h4>Company</h4>
              <ul className="footer__links-list">
                <li><a href="/#about">About</a></li>
                <li><a href="mailto:support@capecontrol.ai">Contact</a></li>
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

export default PrivacyPolicyPage;

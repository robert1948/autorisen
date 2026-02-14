import React, { useState } from "react";
import { Link } from "react-router-dom";
import TopNav from "../../components/nav/TopNav";
import logoUrl from "../../assets/capecontrol-logo.png";
import BuildBadge from "../../components/version/BuildBadge";

type SectionKey =
  | "signup"
  | "payment"
  | "timelines"
  | "ip"
  | "confidentiality"
  | "termination"
  | "warranties"
  | "other"
  | "commitment";

const CustomerInfoPage: React.FC = () => {
  const [openSections, setOpenSections] = useState<Set<SectionKey>>(
    new Set<SectionKey>(["signup"])
  );

  const toggle = (key: SectionKey) => {
    setOpenSections((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

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

  return (
    <div className="landing">
      <TopNav onOpenSupport={() => {}} />
      <main className="landing__main">
        <section className="section" style={{ paddingTop: "6rem" }}>
          <div style={{ maxWidth: 860, margin: "0 auto" }}>
            <span className="badge badge--accent">Customer Information</span>
            <h1 style={{ fontSize: "2.4rem", lineHeight: 1.2, marginBottom: "1rem" }}>
              Customer Information: Committing to a Proposal
            </h1>
            <p style={{ opacity: 0.7, marginBottom: "1.5rem" }}>
              Last Updated: February 14, 2026
            </p>

            <p>
              Welcome to Cape Control! By committing to a Proposal, you agree to the following key
              terms and conditions outlined in our Customer Terms and Conditions. Please review the
              summary below to understand your rights, obligations, and what to expect.
            </p>
            <p style={{ opacity: 0.7, fontStyle: "italic", marginBottom: "2.5rem" }}>
              For full details, refer to the complete{" "}
              <Link to="/terms-and-conditions" style={{ color: "#93c5fd" }}>
                Terms and Conditions
              </Link>
              .
            </p>

            {/* ---- 1. What You're Signing Up For ---- */}
            <div style={sectionStyle}>
              <button
                type="button"
                style={headerStyle}
                onClick={() => toggle("signup")}
                aria-expanded={isOpen("signup")}
              >
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("signup")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>
                  1. What You're Signing Up For
                </h2>
              </button>
              {isOpen("signup") && (
                <div style={bodyStyle}>
                  <ul style={{ paddingLeft: "1.5rem" }}>
                    <li>
                      <strong>Custom Services:</strong> Your Proposal outlines bespoke services,
                      such as AI agent customisation or integrations, tailored to your needs{" "}
                      <span style={{ opacity: 0.6 }}>(Section 2.2)</span>.
                    </li>
                    <li>
                      <strong>Scope of Work:</strong> The Proposal defines the specific Deliverables
                      (e.g., software, workflows, or agent interactions) and timelines for your
                      project <span style={{ opacity: 0.6 }}>(Section 4.1)</span>.
                    </li>
                    <li>
                      <strong>Subcontracting:</strong> Cape Control may engage subcontractors to
                      deliver parts of the services but remains fully responsible for quality and
                      delivery <span style={{ opacity: 0.6 }}>(Section 2.3)</span>.
                    </li>
                  </ul>
                </div>
              )}
            </div>

            {/* ---- 2. Payment Terms ---- */}
            <div style={sectionStyle}>
              <button
                type="button"
                style={headerStyle}
                onClick={() => toggle("payment")}
                aria-expanded={isOpen("payment")}
              >
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("payment")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>2. Payment Terms</h2>
              </button>
              {isOpen("payment") && (
                <div style={bodyStyle}>
                  <ul style={{ paddingLeft: "1.5rem" }}>
                    <li>
                      <strong>Pricing:</strong> Payments follow the terms in your Proposal,
                      typically 50% upfront and 50% upon delivery, unless otherwise specified{" "}
                      <span style={{ opacity: 0.6 }}>(Section 3.2)</span>.
                    </li>
                    <li>
                      <strong>Invoicing:</strong> Invoices are sent electronically and are due
                      within 14 days of issue, unless stated otherwise in your Proposal{" "}
                      <span style={{ opacity: 0.6 }}>(Section 3.4)</span>.
                    </li>
                    <li>
                      <strong>Revenue-Sharing Modules:</strong> Some services may include
                      revenue-sharing or delayed-access terms, which will be clearly disclosed in
                      your Proposal <span style={{ opacity: 0.6 }}>(Section 3.3)</span>.
                    </li>
                    <li>
                      <strong>Refunds:</strong> Refunds for custom work are only available under
                      specific termination conditions outlined in Section 7 below{" "}
                      <span style={{ opacity: 0.6 }}>(Section 3.5)</span>.
                    </li>
                    <li>
                      <strong>Non-Payment:</strong> Failure to pay outstanding invoices may result
                      in restricted or suspended platform access until the balance is resolved{" "}
                      <span style={{ opacity: 0.6 }}>(Section 3.6)</span>.
                    </li>
                  </ul>
                </div>
              )}
            </div>

            {/* ---- 3. Timelines and Delivery ---- */}
            <div style={sectionStyle}>
              <button
                type="button"
                style={headerStyle}
                onClick={() => toggle("timelines")}
                aria-expanded={isOpen("timelines")}
              >
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("timelines")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>3. Timelines and Delivery</h2>
              </button>
              {isOpen("timelines") && (
                <div style={bodyStyle}>
                  <ul style={{ paddingLeft: "1.5rem" }}>
                    <li>
                      <strong>Schedule:</strong> Custom project timelines are detailed in your
                      Proposal. Standard platform services are available immediately unless
                      otherwise specified{" "}
                      <span style={{ opacity: 0.6 }}>(Section 4.1)</span>.
                    </li>
                    <li>
                      <strong>Your Responsibilities:</strong> Delays caused by unavailable
                      materials, data, or access from your side may extend delivery deadlines
                      accordingly <span style={{ opacity: 0.6 }}>(Section 4.2)</span>.
                    </li>
                    <li>
                      <strong>Acceptance:</strong> Deliverables are deemed accepted unless you
                      report issues in writing within 7 days of delivery{" "}
                      <span style={{ opacity: 0.6 }}>(Section 4.3)</span>.
                    </li>
                  </ul>
                </div>
              )}
            </div>

            {/* ---- 4. Intellectual Property ---- */}
            <div style={sectionStyle}>
              <button
                type="button"
                style={headerStyle}
                onClick={() => toggle("ip")}
                aria-expanded={isOpen("ip")}
              >
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("ip")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>
                  4. Intellectual Property (IP)
                </h2>
              </button>
              {isOpen("ip") && (
                <div style={bodyStyle}>
                  <ul style={{ paddingLeft: "1.5rem" }}>
                    <li>
                      <strong>Platform IP:</strong> Cape Control owns all pre-existing AI agents,
                      modules, and platform components. You receive a non-exclusive,
                      non-transferable licence to use them as specified in your Proposal{" "}
                      <span style={{ opacity: 0.6 }}>(Section 5.1)</span>.
                    </li>
                    <li>
                      <strong>Custom Work IP:</strong> IP rights for custom Deliverables are either
                      licensed to you or transferred to you, as specified in your Proposal terms{" "}
                      <span style={{ opacity: 0.6 }}>(Section 5.2)</span>.
                    </li>
                    <li>
                      <strong>Your Materials:</strong> You grant Cape Control a royalty-free licence
                      to use your uploaded content solely for the purpose of delivering the agreed
                      services <span style={{ opacity: 0.6 }}>(Section 5.3)</span>.
                    </li>
                    <li>
                      <strong>Third-Party Materials:</strong> You are responsible for ensuring that
                      any materials you provide do not infringe on third-party intellectual property
                      rights <span style={{ opacity: 0.6 }}>(Section 5.4)</span>.
                    </li>
                  </ul>
                </div>
              )}
            </div>

            {/* ---- 5. Confidentiality ---- */}
            <div style={sectionStyle}>
              <button
                type="button"
                style={headerStyle}
                onClick={() => toggle("confidentiality")}
                aria-expanded={isOpen("confidentiality")}
              >
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>
                  {chevron("confidentiality")}
                </span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>5. Confidentiality</h2>
              </button>
              {isOpen("confidentiality") && (
                <div style={bodyStyle}>
                  <ul style={{ paddingLeft: "1.5rem" }}>
                    <li>
                      <strong>Protection of Information:</strong> Both parties agree to keep all
                      confidential information private and will not disclose it to any third party
                      without prior written consent{" "}
                      <span style={{ opacity: 0.6 }}>(Section 6.1)</span>.
                    </li>
                    <li>
                      <strong>Marketing Use:</strong> Cape Control may reference your name and a
                      general project description for marketing purposes, unless you notify us in
                      writing that you wish to opt out{" "}
                      <span style={{ opacity: 0.6 }}>(Section 6.2)</span>.
                    </li>
                  </ul>
                </div>
              )}
            </div>

            {/* ---- 6. Termination ---- */}
            <div style={sectionStyle}>
              <button
                type="button"
                style={headerStyle}
                onClick={() => toggle("termination")}
                aria-expanded={isOpen("termination")}
              >
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>
                  {chevron("termination")}
                </span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>6. Termination</h2>
              </button>
              {isOpen("termination") && (
                <div style={bodyStyle}>
                  <ul style={{ paddingLeft: "1.5rem" }}>
                    <li>
                      <strong>General Termination:</strong> Either party may terminate the agreement
                      for a material breach by providing 30 days' written notice, provided the
                      breach remains unresolved after a 14-day cure period{" "}
                      <span style={{ opacity: 0.6 }}>(Section 7.1)</span>.
                    </li>
                    <li>
                      <strong>Cancellation by You:</strong> You may cancel the Proposal before work
                      begins; however, a cancellation fee (typically 20% of the Proposal value)
                      may apply <span style={{ opacity: 0.6 }}>(Section 7.2)</span>.
                    </li>
                    <li>
                      <strong>Termination by Cape Control:</strong> Cape Control may terminate or
                      suspend your access for non-payment, misuse, or abuse of the platform or AI
                      agents <span style={{ opacity: 0.6 }}>(Section 7.3)</span>.
                    </li>
                    <li>
                      <strong>Post-Termination:</strong> You retain access to all Deliverables that
                      have been fully paid for and delivered prior to termination. No refunds will
                      be provided for services already rendered{" "}
                      <span style={{ opacity: 0.6 }}>(Section 7.4)</span>.
                    </li>
                  </ul>
                </div>
              )}
            </div>

            {/* ---- 7. Warranties and Liability ---- */}
            <div style={sectionStyle}>
              <button
                type="button"
                style={headerStyle}
                onClick={() => toggle("warranties")}
                aria-expanded={isOpen("warranties")}
              >
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>
                  {chevron("warranties")}
                </span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>
                  7. Warranties and Liability
                </h2>
              </button>
              {isOpen("warranties") && (
                <div style={bodyStyle}>
                  <ul style={{ paddingLeft: "1.5rem" }}>
                    <li>
                      <strong>Custom Work Warranty:</strong> Cape Control warrants that Deliverables
                      will conform to the specifications outlined in your Proposal for a period of
                      30 days following delivery{" "}
                      <span style={{ opacity: 0.6 }}>(Section 8.2)</span>.
                    </li>
                    <li>
                      <strong>Liability Cap:</strong> Cape Control's total aggregate liability is
                      capped at the total fees paid by you in the 3-month period immediately
                      preceding the claim{" "}
                      <span style={{ opacity: 0.6 }}>(Section 8.3)</span>.
                    </li>
                    <li>
                      <strong>No Outcome Guarantees:</strong> Cape Control does not guarantee
                      specific business outcomes, revenue generation, or profitability beyond the
                      described features and functionality of the Deliverables{" "}
                      <span style={{ opacity: 0.6 }}>(Section 8.4)</span>.
                    </li>
                  </ul>
                </div>
              )}
            </div>

            {/* ---- 8. Other Important Information ---- */}
            <div style={sectionStyle}>
              <button
                type="button"
                style={headerStyle}
                onClick={() => toggle("other")}
                aria-expanded={isOpen("other")}
              >
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>{chevron("other")}</span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>
                  8. Other Important Information
                </h2>
              </button>
              {isOpen("other") && (
                <div style={bodyStyle}>
                  <ul style={{ paddingLeft: "1.5rem" }}>
                    <li>
                      <strong>Force Majeure:</strong> Neither party shall be held liable for delays
                      or failures in performance caused by events beyond reasonable control,
                      including but not limited to system outages, natural disasters, or government
                      actions <span style={{ opacity: 0.6 }}>(Section 9)</span>.
                    </li>
                    <li>
                      <strong>Governing Law:</strong> These terms are governed by the laws of the
                      Republic of South Africa. Disputes will be resolved through good-faith
                      negotiation in the first instance, followed by arbitration in Cape Town, or
                      through the courts of Cape Town if arbitration is not pursued{" "}
                      <span style={{ opacity: 0.6 }}>(Section 10)</span>.
                    </li>
                    <li>
                      <strong>Amendments to Terms:</strong> Cape Control may update these general
                      terms with 30 days' prior written notice. Your continued use of the platform
                      after this notice period constitutes acceptance of the updated terms{" "}
                      <span style={{ opacity: 0.6 }}>(Section 11.1)</span>.
                    </li>
                    <li>
                      <strong>Amendments to Proposals:</strong> Any changes to an active Proposal
                      require the written agreement of both parties{" "}
                      <span style={{ opacity: 0.6 }}>(Section 11.2)</span>.
                    </li>
                    <li>
                      <strong>Assignment:</strong> You may not assign or transfer this agreement,
                      or any rights or obligations under it, without Cape Control's prior written
                      consent <span style={{ opacity: 0.6 }}>(Section 12.2)</span>.
                    </li>
                  </ul>
                </div>
              )}
            </div>

            {/* ---- 9. Your Commitment ---- */}
            <div style={sectionStyle}>
              <button
                type="button"
                style={headerStyle}
                onClick={() => toggle("commitment")}
                aria-expanded={isOpen("commitment")}
              >
                <span style={{ fontSize: "1.1rem", opacity: 0.5 }}>
                  {chevron("commitment")}
                </span>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>9. Your Commitment</h2>
              </button>
              {isOpen("commitment") && (
                <div style={bodyStyle}>
                  <p>
                    By signing the Proposal, you acknowledge that you have read, understood, and
                    agree to be bound by these Terms and Conditions in their entirety{" "}
                    <span style={{ opacity: 0.6 }}>(Section 13)</span>.
                  </p>
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
              <a
                href="https://autorisen-dac8e65796e7.herokuapp.com/auth/register"
                className="btn btn--primary"
                style={{ textAlign: "center" }}
              >
                Register Now
              </a>
              <Link to="/terms-and-conditions" className="btn btn--ghost" style={{ textAlign: "center" }}>
                Read Full Terms &amp; Conditions
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
            <h2 style={{ marginTop: "3rem" }}>Contact Us</h2>
            <p>
              For questions, clarifications, or support, please reach out to us through any of the
              following channels:
            </p>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                gap: "1rem",
                marginTop: "1rem",
              }}
            >
              {[
                {
                  label: "Website",
                  value: "cape-control.com",
                  href: "https://cape-control.com",
                },
                {
                  label: "Email",
                  value: "support@cape-control.com",
                  href: "mailto:support@cape-control.com",
                },
                {
                  label: "Location",
                  value: "Cape Town, South Africa",
                  href: undefined,
                },
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
              <strong>Disclaimer:</strong> This page provides a summary of key terms for
              informational purposes only. It does not replace or override the full Customer Terms
              and Conditions. In the event of any conflict, the full Terms and Conditions shall
              prevail. Cape Control reserves the right to update this summary in line with any
              amendments to the underlying terms.
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
                <li>
                  <Link to="/">Home</Link>
                </li>
                <li>
                  <Link to="/subscribe">Pricing</Link>
                </li>
              </ul>
            </div>
            <div className="footer__column">
              <h4>Information</h4>
              <ul className="footer__links-list">
                <li>
                  <Link to="/customer-terms">Proposal Terms</Link>
                </li>
                <li>
                  <Link to="/developers">Developer Info</Link>
                </li>
              </ul>
            </div>
            <div className="footer__column">
              <h4>Company</h4>
              <ul className="footer__links-list">
                <li>
                  <a href="/#about">About</a>
                </li>
                <li>
                  <a href="/#privacy">Privacy Policy</a>
                </li>
                <li>
                  <Link to="/terms-and-conditions">Terms of Service</Link>
                </li>
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

export default CustomerInfoPage;

import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import ChatModal, { type ChatPlacement } from "../components/chat/ChatModal";
import TopNav from "../components/nav/TopNav";
import OnboardingChat from "../features/chat/OnboardingChat";
import OnboardingHistory from "../features/chat/OnboardingHistory";
import AgentWorkbench from "../features/dev/AgentWorkbench";
import AgentRegistryPanel from "../features/dev/AgentRegistryPanel";
import MarketplaceShowcase from "../features/marketplace/MarketplaceShowcase";
import AuthGate from "../features/auth/AuthGate";
import logoUrl from "../assets/capecontrol-logo.png";

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "/api";

type HealthResponse = {
  status: string;
  version?: string;
  env?: string;
};

type HealthState = {
  data?: HealthResponse;
  loading: boolean;
  error?: string;
};

type ActiveChat = "support" | "onboarding" | "energy" | "developer" | null;

type ChatView = {
  placement: ChatPlacement;
  title: string;
  description: string;
};

const chatConfig: Record<Exclude<ActiveChat, null>, ChatView> = {
  support: {
    placement: "support",
    title: "Talk with CapeControl Support",
    description:
      "Need a hand? Connect with a specialist for billing, onboarding, or troubleshooting in seconds.",
  },
  onboarding: {
    placement: "onboarding",
    title: "Meet CapeAI — Your Launch Guide",
    description:
      "A guided tour through customer onboarding, tenant setup, and your first automations.",
  },
  energy: {
    placement: "energy",
    title: "Explain My Usage",
    description:
      "Ask why energy spiked last night or get proactive suggestions for savings.",
  },
  developer: {
    placement: "developer",
    title: "Agent Workbench",
    description:
      "Inspect tool calls, prompts, and evaluations in real time before you publish an agent.",
  },
};

const Home = () => {
  const [state, setState] = useState<HealthState>({ loading: true });
  const [activeChat, setActiveChat] = useState<ActiveChat>(null);

  const fetchHealth = async () => {
    setState({ loading: true });
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const json: HealthResponse = await res.json();
      setState({ loading: false, data: json });
    } catch (err) {
      const message = err instanceof Error ? err.message : "unknown error";
      setState({ loading: false, error: message });
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const { data, loading, error } = state;
  const statusBadge = useMemo(() => {
    if (loading) return { label: "Checking…", tone: "neutral" };
    if (error) return { label: "Degraded", tone: "warn" };
    if (!data) return { label: "Unknown", tone: "neutral" };
    return {
      label: data.status === "ok" ? "Operational" : data.status,
      tone: data.status === "ok" ? "ok" : "warn",
    };
  }, [data, error, loading]);

  const chatModalConfig = activeChat ? chatConfig[activeChat] : null;

  const launchChat = (placement: Exclude<ActiveChat, null>) => {
    setActiveChat(placement);
  };

  return (
    <div className="landing">
      <TopNav onOpenSupport={() => launchChat("support")} />
      <main className="landing__main">
        <section className="hero" id="home">
          <div className="hero__content">
            <span className="badge badge--accent">CapeControl Platform</span>
            <h1>
              Where Intelligence Meets Impact—<br /> AI Accessible to Everyone.
            </h1>
            <p>
              Democratize AI across your organization with CapeControl. Launch guided onboarding,
              query energy and finance data, and empower developers with compliant agent workflows.
            </p>
            <div className="hero__actions">
              <button
                type="button"
                className="btn btn--primary"
                onClick={() => launchChat("onboarding")}
              >
                Launch CapeAI Guide
              </button>
              <button
                type="button"
                className="btn btn--ghost"
                onClick={() => launchChat("support")}
              >
                Talk to Support
              </button>
              <a className="btn btn--link" href="#demo">
                See how it works →
              </a>
            </div>
            <div className="hero__status">
              <span className={`status status--${statusBadge.tone}`}>
                {statusBadge.label}
              </span>
              {data?.version && <span className="status__meta">API {data.version}</span>}
              {data?.env && <span className="status__meta">{data.env}</span>}
            </div>
          </div>

          <div className="hero__visual" aria-hidden="true">
            <div className="hero__pane">
              <header>
                <div>
                  <p className="hero__pane-eyebrow">CapeAI Assistant</p>
                  <h3>Customer onboarding checklist</h3>
                </div>
                <span className="hero__badge">Live</span>
              </header>
              <ul>
                <li>
                  <span>✓</span>Create tenant and invite teammates
                </li>
                <li>
                  <span>✓</span>Connect data sources &amp; tools
                </li>
                <li>
                  <span>•</span>Automate weekly usage digest
                </li>
              </ul>
              <footer>
                <button
                  type="button"
                  className="btn btn--mini"
                  onClick={() => launchChat("energy")}
                >
                  Explain last night’s spike
                </button>
                <p>AI responses verified with safety guardrails.</p>
              </footer>
            </div>
          </div>
        </section>

        <section className="section highlights" id="features">
          <h2>Built for teams shipping AI-driven experiences.</h2>
          <div className="highlights__grid">
            <article>
              <h3>Guided Onboarding</h3>
              <p>
                CapeAI walks every new customer through account creation, environment setup, and the
                first automations—no playbooks required.
              </p>
            </article>
            <article>
              <h3>Operational Insights</h3>
              <p>
                Ask natural-language questions about tenant energy usage or transaction data and get
                clean, auditable answers.
              </p>
            </article>
            <article>
              <h3>Developers Welcome</h3>
              <p>
                Build on top of our agent platform with role-based access, quota enforcement, and
                observability baked in.
              </p>
            </article>
          </div>
        </section>

        <section className="section showcase" id="demo">
          <div className="showcase__content">
            <h2>CapeAI Automates Every Step.</h2>
            <p>
              Trigger a guided chat from marketing, keep it running inside the app, and hand off to
              support seamlessly—the same conversation, all in one thread.
            </p>
            <ul>
              <li>Multi-placement ChatKit sessions with per-tool guardrails.</li>
              <li>Thread persistence backed by Postgres for return visits.</li>
              <li>Ops visibility with audit-grade event logging.</li>
            </ul>
          </div>
          <div className="showcase__panel" aria-hidden="true">
            <div className="chart">
              <p>Weekly Engagement</p>
              <div className="chart__bars">
                <div style={{ height: "35%" }} />
                <div style={{ height: "55%" }} />
                <div style={{ height: "78%" }} />
                <div style={{ height: "90%" }} />
              </div>
            </div>
            <div className="showcase__stats">
              <div>
                <span>92%</span>
                Assisted onboarding completion
              </div>
              <div>
                <span>38%</span>
                Faster support resolution
              </div>
            </div>
          </div>
        </section>

        <section className="section pricing" id="pricing">
          <h2>Plans that scale with your impact.</h2>
          <div className="pricing__tiers">
            <article>
              <p className="pricing__badge">Starter</p>
              <h3>$0</h3>
              <ul>
                <li>CapeAI onboarding guide</li>
                <li>Energy &amp; finance read access</li>
                <li>Developer sandbox tools</li>
              </ul>
              <Link to="/register" className="btn btn--ghost">
                Get Started Free
              </Link>
            </article>
            <article className="pricing__featured">
              <p className="pricing__badge">Growth</p>
              <h3>$249<span>/mo</span></h3>
              <ul>
                <li>Unlimited ChatKit seats</li>
                <li>Tenant analytics dashboards</li>
                <li>Ops Copilot &amp; runbooks</li>
              </ul>
              <a href="#contact" className="btn btn--primary">
                Talk to Sales
              </a>
            </article>
            <article>
              <p className="pricing__badge">Enterprise</p>
              <h3>Let’s talk</h3>
              <ul>
                <li>Dedicated environment</li>
                <li>Custom tool adapters</li>
                <li>24/7 support &amp; SLAs</li>
              </ul>
              <a href="#contact" className="btn btn--ghost">
                Contact Us
              </a>
            </article>
          </div>
        </section>

        <section className="section faq" id="faq">
          <h2>Frequently asked questions</h2>
          <div className="faq__grid">
            <article>
              <h3>Does ChatKit require my developers to change code?</h3>
              <p>
                No—CapeControl mints secure tokens server-side. You can embed ChatKit widgets
                anywhere without exposing secrets.
              </p>
            </article>
            <article>
              <h3>How do you keep conversations safe?</h3>
              <p>
                Threads are persisted with audit logs and tool usage tracking. You decide which tools
                are available per placement.
              </p>
            </article>
            <article>
              <h3>Can I monitor system health?</h3>
              <p>
                Yes, the platform exposes structured logs, web vitals, and API smoke checks—plus Ops
                Copilot right in the admin console.
              </p>
            </article>
          </div>
        </section>
        <AuthGate
          fallback={
            <section className="section experiences" id="experiences">
              <h2>Experience CapeControl right now</h2>
              <p>Please log in to access onboarding and developer tools.</p>
            </section>
          }
        >
          <section className="section experiences" id="experiences">
            <h2>Experience CapeControl right now</h2>
            <div className="experiences__grid">
              <OnboardingChat onLaunchChat={() => launchChat("onboarding")} />
              <AgentWorkbench onLaunchChat={() => launchChat("developer")} />
              <OnboardingHistory />
            </div>
          </section>
          <section className="section developer" id="developers">
            <AgentRegistryPanel />
          </section>
          <MarketplaceShowcase />
        </AuthGate>

        <section className="section about" id="about">
          <h2>About CapeControl</h2>
          <div className="about__content">
            <p>
              CapeControl is built by Cape Craft Projects CC with a single goal: make enterprise AI
              approachable, compliant, and genuinely useful for every team. Our platform blends
              guided onboarding, transparent automation, and developer tooling so you can move from
              idea to production insight in days—not quarters.
            </p>
            <ul className="about__list">
              <li>Headquarters: Cape Town, South Africa (VAT: 4270105119)</li>
              <li>Focus: Secure AI agents, operational intelligence, and automation</li>
              <li>Mission: Empower organizations worldwide to innovate responsibly with AI</li>
            </ul>
          </div>
        </section>

        <section className="section legal" id="privacy">
          <h2>Privacy Policy</h2>
          <div className="legal__card">
            <p>
              We collect only the information required to operate CapeControl, provide support, and
              improve the platform. Customer data is segregated per tenant, encrypted in transit and
              at rest, and never sold to third parties.
            </p>
            <ul>
              <li>Data retention follows the shorter of contract term or 30 days after deletion.</li>
              <li>Access logs, audit trails, and export tooling are available to administrators.</li>
              <li>
                Request data removal or portability any time by contacting support@capecontrol.ai.
              </li>
            </ul>
          </div>
        </section>

        <section className="section legal" id="terms">
          <h2>Terms of Service</h2>
          <div className="legal__card">
            <p>
              By using CapeControl you agree to operate within applicable laws, respect platform
              rate limits, and protect credentials issued to your organization. CapeControl provides
              the service “as is” with commercially reasonable availability targets.
            </p>
            <ul>
              <li>
                Customers remain responsible for content produced by their agents and downstream
                automations.
              </li>
              <li>Enterprise SLAs, DPAs, and regional hosting addendums are available on request.</li>
              <li>
                Disputes are governed by South African law; venue is Cape Town, Western Cape.
              </li>
            </ul>
          </div>
        </section>
      </main>

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
                <p>
                  Enterprise AI platform democratizing AI development with seamless integration,
                  developer-first experience, and enterprise-grade security.
                </p>
                <p className="footer__brand-meta">Cape Craft Projects CC (VAT: 4270105119)</p>
                <p className="footer__brand-meta">Trading as Cape Control</p>
                <p className="footer__brand-meta">Empowering AI innovation worldwide</p>
              </div>
            </div>

            <div className="footer__column">
              <h4>Platform</h4>
              <ul className="footer__links-list">
                <li>
                  <a href="#home">Overview</a>
                </li>
                <li>
                  <a href="#experiences">How It Works</a>
                </li>
                <li>
                  <a href="#features">Our Vision</a>
                </li>
                <li>
                  <a href="#pricing">Pricing</a>
                </li>
              </ul>
            </div>

            <div className="footer__column">
              <h4>Developers</h4>
              <ul className="footer__links-list">
                <li>
                  <a href="#developers">Developer Hub</a>
                </li>
                <li>
                  <a href="#experiences">Join as Developer</a>
                </li>
                <li>
                  <a href="#developers">API Documentation</a>
                </li>
              </ul>
            </div>

            <div className="footer__column">
              <h4>Company</h4>
              <ul className="footer__links-list">
                <li>
                  <a href="#about">About Us</a>
                </li>
                <li>
                  <button
                    type="button"
                    className="footer__link-button"
                    onClick={() => launchChat("support")}
                  >
                    Contact
                  </button>
                </li>
                <li>
                  <a href="#privacy">Privacy Policy</a>
                </li>
                <li>
                  <a href="#terms">Terms of Service</a>
                </li>
              </ul>
            </div>
          </div>

          <div className="footer__bottom">
            <p>© {new Date().getFullYear()} CapeControl. All rights reserved.</p>
            <div className="footer__bottom-meta">
              <span>Built with ❤️ for the AI community.</span>
              <span>v{__APP_VERSION__}</span>
              <span className="footer__status">
                <span className="footer__status-dot" aria-hidden="true" />
                All systems operational
              </span>
            </div>
          </div>
        </div>
      </footer>
      {chatModalConfig && (
        <ChatModal
          open={!!activeChat}
          onClose={() => setActiveChat(null)}
          placement={chatModalConfig.placement}
          title={chatModalConfig.title}
          description={chatModalConfig.description}
        />
      )}
    </div>
  );
};

export default Home;

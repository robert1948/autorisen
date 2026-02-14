import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import ChatModal, { type ChatPlacement } from "../components/chat/ChatModal";
import TopNav from "../components/nav/TopNav";
import OnboardingChat from "../features/chat/OnboardingChat";
import OnboardingHistory from "../features/chat/OnboardingHistory";
import AgentWorkbench from "../features/dev/AgentWorkbench";
import AgentRegistryPanel from "../features/dev/AgentRegistryPanel";
import MarketplaceShowcase from "../features/marketplace/MarketplaceShowcase";
import AuthGate from "../features/auth/AuthGate";
import { useAuth } from "../features/auth/AuthContext";
import logoUrl from "../assets/capecontrol-logo.png";
import BuildBadge from "../components/version/BuildBadge";

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
      "Need a hand? Connect with a specialist for setup, workflows, or troubleshooting in seconds.",
  },
  onboarding: {
    placement: "onboarding",
    title: "Meet CapeAI — Your Launch Guide",
    description:
      "Walk through your first workflow map and see where AI can safely take work off your plate.",
  },
  energy: {
    placement: "energy",
    title: "Explain My Operations",
    description:
      "Ask where time or cost spiked this week and get a clear, business-friendly explanation.",
  },
  developer: {
    placement: "developer",
    title: "Agent Workbench",
    description:
      "Inspect tool calls, prompts, and evaluations in real time before you publish an agent.",
  },
};

const Home = () => {
  const { search } = useLocation();
  const navigate = useNavigate();
  const { state: authState } = useAuth();
  const isAuthenticated = Boolean(authState.accessToken);
  const registerHref = `/auth/register${search}`;
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
    if (!isAuthenticated) {
      // Redirect unauthenticated users to register (onboarding) or login (support)
      navigate(placement === "support" ? "/auth/login" : registerHref);
      return;
    }
    setActiveChat(placement);
  };

  return (
    <div className="landing">
      <TopNav onOpenSupport={() => launchChat("support")} />
      <main className="landing__main">
        {/* HERO */}
        <section className="hero" id="home">
          <div className="hero__content">
            <span className="badge badge--accent">Built for small business ops</span>
            <h1>
              AI that learns how your business runs—
              <br />
              then quietly removes the busywork.
            </h1>
            <p>
              If you&apos;re the founder or operations lead, you&apos;re probably the one holding
              everything together: spreadsheets, emails, follow-ups, and approvals. CapeControl
              listens first, maps how your day really works, then deploys AI-powered workflows that
              reduce manual tasks without forcing you into a rigid new system.
            </p>
            <div className="hero__actions">
              <button
                type="button"
                className="btn btn--primary"
                onClick={() => launchChat("onboarding")}
              >
                Start a workflow-mapping session
              </button>
              <button
                type="button"
                className="btn btn--ghost"
                onClick={() => launchChat("support")}
              >
                Talk to our team
              </button>
              <a className="btn btn--link" href="#demo">
                See a real workflow →
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

          {/* HERO VISUAL */}
          <div className="hero__visual" aria-hidden="true">
            <div className="hero__pane">
              <header>
                <div>
                  <p className="hero__pane-eyebrow">CapeAI Assistant</p>
                  <h3>Daily operations checklist</h3>
                </div>
                <span className="hero__badge">Live</span>
              </header>
              <ul>
                <li>
                  <span>✓</span>Capture today&apos;s incoming requests and tasks
                </li>
                <li>
                  <span>✓</span>Route work to the right person with clear next steps
                </li>
                <li>
                  <span>•</span>Summarise what&apos;s blocking progress before the day ends
                </li>
              </ul>
              <footer>
                <button
                  type="button"
                  className="btn btn--mini"
                  onClick={() => launchChat("energy")}
                >
                  Show me where time was lost
                </button>
                <p>AI responses are logged with audit trails and safety guardrails.</p>
              </footer>
            </div>
          </div>
        </section>

        {/* HIGHLIGHTS */}
        <section className="section highlights" id="features">
          <h2>Built for founders and ops teams who need their day back.</h2>
          <div className="highlights__grid">
            <article>
              <h3>Workflow Mapping &amp; Onboarding</h3>
              <p>
                Start with one live workflow, like client onboarding or job intake. CapeControl
                turns it into step-by-step progress you can track, with clear "next step" guidance.
                Capture blockers as they happen and improve the flow over time.
              </p>
            </article>
            <article>
              <h3>Operations Command Center</h3>
              <p>
                Get decision-ready answers, not raw tables. Use guided, plain-language questions to
                see current status, recurring blockers, and trends. Each response is backed by your
                live system data and a clear summary.
              </p>
            </article>
            <article>
              <h3>Developers When You&apos;re Ready</h3>
              <p>
                Start simple with a no-code setup. When you&apos;re ready, enable published agents and
                integrations with reviewed manifests, permissions, and audit logs, so every
                extension stays governed and traceable.
              </p>
            </article>
          </div>
        </section>

        {/* SHOWCASE */}
        <section className="section showcase" id="demo">
          <div className="showcase__content">
            <h2>From messy process to clear, assisted workflow.</h2>
            <p>
              Pick one process—like quoting, onboarding, or job handover. CapeControl turns the
              existing emails and spreadsheets into a guided flow, with AI agents nudging the next
              step and surfacing what needs your attention.
            </p>
            <ul>
              <li>Keep the tools you use today; add structure and automation on top.</li>
              <li>One conversation that follows your customer from first contact to follow-up.</li>
              <li>Ops visibility with audit-grade event logging and clear owners for each step.</li>
            </ul>
          </div>
          <div className="showcase__panel" aria-hidden="true">
            <div className="chart">
              <p>Manual hours per week</p>
              <div className="chart__bars">
                <div style={{ height: "85%" }} />
                <div style={{ height: "70%" }} />
                <div style={{ height: "45%" }} />
                <div style={{ height: "30%" }} />
              </div>
            </div>
            <div className="showcase__stats">
              <div>
                <span>40%</span>
                Less time spent on repetitive admin
              </div>
              <div>
                <span>2×</span>
                Faster from request to completed workflow
              </div>
            </div>
          </div>
        </section>

        {/* PRICING */}
        <section className="section pricing" id="pricing">
          <h2>Start small, grow as your workflows mature.</h2>
          <div className="pricing__tiers">
            <article>
              <p className="pricing__badge">Starter</p>
              <h3>$0</h3>
              <ul>
                <li>One guided workflow-mapping session</li>
                <li>CapeAI assistant for a single process</li>
                <li>Basic reporting and history</li>
              </ul>
              <Link to={registerHref} className="btn btn--ghost">
                Get Started Free
              </Link>
            </article>
            <article className="pricing__featured">
              <p className="pricing__badge">Growth</p>
              <h3>
                $249<span>/mo</span>
              </h3>
              <ul>
                <li>Multiple workflows across your business</li>
                <li>Team access with roles and permissions</li>
                <li>Ops insights and automation tuning</li>
              </ul>
              <a href="#contact" className="btn btn--primary">
                Talk to Sales
              </a>
            </article>
            <article>
              <p className="pricing__badge">Enterprise</p>
              <h3>Let&apos;s talk</h3>
              <ul>
                <li>Dedicated environment &amp; governance</li>
                <li>Custom tool adapters and integrations</li>
                <li>24/7 support &amp; SLAs</li>
              </ul>
              <a href="#contact" className="btn btn--ghost">
                Contact Us
              </a>
            </article>
          </div>
        </section>

        {/* FAQ */}
        <section className="section faq" id="faq">
          <h2>Frequently asked questions</h2>
          <div className="faq__grid">
            <article>
              <h3>Do I need technical skills to get value?</h3>
              <p>
                No. We start with a conversation about how your business runs today and help you map
                one workflow. You don&apos;t need to design prompts, write code, or rebuild your
                stack to see results.
              </p>
            </article>
            <article>
              <h3>Will I have to change all my tools?</h3>
              <p>
                Not at all. CapeControl layers on top of your existing tools wherever possible,
                using AI agents and workflows to connect the dots and reduce manual steps.
              </p>
            </article>
            <article>
              <h3>Is our data secure and auditable?</h3>
              <p>
                Yes. Workflows run with audit logs, role-based access, and environment separation.
                You can see who did what, when—and which agents were involved in each action.
              </p>
            </article>
          </div>
        </section>

        {/* AUTH-GATED EXPERIENCE SECTIONS */}
        <AuthGate
          fallback={
            <section className="section experiences" id="experiences">
              <h2>Experience CapeControl right now</h2>
              <p>Please log in to access guided workflows and developer tools.</p>
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

        {/* ABOUT */}
        <section className="section about" id="about">
          <h2>About CapeControl</h2>
          <div className="about__content">
            <p>
              CapeControl is built by Cape Craft Projects CC with a single goal: give small
              businesses and lean teams enterprise-grade AI workflows without enterprise complexity.
              We blend guided onboarding, transparent automation, and developer tooling so you can
              move from messy processes to reliable flows in days—not quarters.
            </p>
            <ul className="about__list">
              <li>Headquarters: Cape Town, South Africa (VAT: 4270105119)</li>
              <li>Focus: Secure AI agents, operational intelligence, and workflow automation</li>
              <li>Mission: Help operators reclaim their day and scale responsibly with AI</li>
            </ul>
          </div>
        </section>

        {/* LEGAL SECTIONS (unchanged structure) */}
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

      {/* FOOTER (unchanged layout, copy slightly tuned above) */}
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
                <div className="footer__legal-desktop">
                  <p>
                    Workflow-first AI platform that helps small businesses and growing teams run more
                    smoothly, with enterprise-grade security behind the scenes.
                  </p>
                  <p className="footer__brand-meta">Operated by Cape Craft Projects CC (VAT: 4270105119)</p>
                  <p className="footer__brand-meta">Trading as CapeControl</p>
                  <p className="footer__brand-meta">Empowering AI-driven operations worldwide</p>
                </div>
                <p className="footer__legal-mobile">
                  CapeControl • Operated by Cape Craft Projects CC (VAT: 4270105119)
                </p>
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
                  <a href="#features">Workflows</a>
                </li>
                <li>
                  <a href="#pricing">Pricing</a>
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
                <li>
                  <a href="#developers">Developer Hub</a>
                </li>
                <li>
                  <a href="#experiences">Join as Developer</a>
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
              <span>Built with ❤️ for operators and their teams.</span>
              <span className="footer__status">
                <span className="footer__status-dot" aria-hidden="true" />
                All systems operational
              </span>
              <BuildBadge />
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

import { useEffect, useMemo, useState } from "react";

import ChatModal, { type ChatPlacement } from "../components/chat/ChatModal";
import TopNav from "../components/nav/TopNav";
import OnboardingChat from "../features/chat/OnboardingChat";
import OnboardingHistory from "../features/chat/OnboardingHistory";
import AgentWorkbench from "../features/dev/AgentWorkbench";
import AgentRegistryPanel from "../features/dev/AgentRegistryPanel";
import MarketplaceShowcase from "../features/marketplace/MarketplaceShowcase";
import AuthForms from "../features/auth/AuthForms";
import AuthGate from "../features/auth/AuthGate";

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
              <a href="#register" className="btn btn--ghost">
                Get Started Free
              </a>
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
      </main>

      <footer className="footer">
        <div className="footer__content">
          <p>© {new Date().getFullYear()} CapeControl • AI that works for every team.</p>
          <div className="footer__links">
            <a href="#privacy">Privacy</a>
            <a href="#terms">Terms</a>
            <button type="button" onClick={() => launchChat("support")}>
              Need help?
            </button>
          </div>
        </div>
      </footer>
      <AuthForms />

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

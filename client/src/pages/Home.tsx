import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import ChatModal, { type ChatPlacement } from "../components/chat/ChatModal";
import TopNav from "../components/nav/TopNav";
import { useAuth } from "../features/auth/AuthContext";
import logoUrl from "../assets/capecontrol-logo.png";
import BuildBadge from "../components/version/BuildBadge";
import { useLandingAnalytics } from "../hooks/useLandingAnalytics";

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

/* ── SVG Icon Components for "AI Magic" Feature Illustrations ── */

const IconShield = () => (
  <svg className="magic-icon" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <defs>
      <linearGradient id="shield-grad" x1="0" y1="0" x2="64" y2="64">
        <stop offset="0%" stopColor="#667eea" />
        <stop offset="100%" stopColor="#60a5fa" />
      </linearGradient>
    </defs>
    <path d="M32 4L6 16v16c0 14.4 11.1 27.8 26 32 14.9-4.2 26-17.6 26-32V16L32 4z" stroke="url(#shield-grad)" strokeWidth="2.5" fill="url(#shield-grad)" fillOpacity="0.15" />
    <path d="M22 32l6 6 14-14" stroke="url(#shield-grad)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
    <circle cx="48" cy="12" r="2" fill="#fbbf24" opacity="0.9" />
    <circle cx="52" cy="20" r="1.2" fill="#fbbf24" opacity="0.7" />
    <circle cx="14" cy="10" r="1.5" fill="#a78bfa" opacity="0.8" />
  </svg>
);

const IconSparkle = () => (
  <svg className="magic-icon" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <defs>
      <linearGradient id="sparkle-grad" x1="0" y1="0" x2="64" y2="64">
        <stop offset="0%" stopColor="#764ba2" />
        <stop offset="100%" stopColor="#a78bfa" />
      </linearGradient>
    </defs>
    <path d="M32 4l4 12 12 4-12 4-4 12-4-12-12-4 12-4 4-12z" fill="url(#sparkle-grad)" fillOpacity="0.2" stroke="url(#sparkle-grad)" strokeWidth="2" />
    <path d="M48 36l2 6 6 2-6 2-2 6-2-6-6-2 6-2 2-6z" fill="#fbbf24" fillOpacity="0.8" />
    <path d="M14 40l1.5 4.5 4.5 1.5-4.5 1.5L14 52l-1.5-4.5L8 46l4.5-1.5L14 40z" fill="#60a5fa" fillOpacity="0.7" />
    <circle cx="32" cy="20" r="6" fill="url(#sparkle-grad)" fillOpacity="0.35" />
  </svg>
);

const IconRocket = () => (
  <svg className="magic-icon" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <defs>
      <linearGradient id="rocket-grad" x1="0" y1="0" x2="64" y2="64">
        <stop offset="0%" stopColor="#ff6b6b" />
        <stop offset="100%" stopColor="#fbbf24" />
      </linearGradient>
    </defs>
    <path d="M36 8c-8 4-14 12-16 22l8 8c10-2 18-8 22-16l-2-2c2-6 2-10 2-10s-4 0-10 2l-4-4z" stroke="url(#rocket-grad)" strokeWidth="2.5" fill="url(#rocket-grad)" fillOpacity="0.15" />
    <circle cx="38" cy="26" r="4" stroke="url(#rocket-grad)" strokeWidth="2" fill="none" />
    <path d="M20 30c-4 4-6 12-6 12s8-2 12-6" stroke="url(#rocket-grad)" strokeWidth="2" strokeLinecap="round" />
    <circle cx="16" cy="48" r="2" fill="#fbbf24" opacity="0.9" />
    <circle cx="12" cy="52" r="1.5" fill="#ff6b6b" opacity="0.7" />
    <circle cx="20" cy="54" r="1" fill="#a78bfa" opacity="0.6" />
  </svg>
);

const IconWand = () => (
  <svg className="magic-icon magic-icon--lg" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <defs>
      <linearGradient id="wand-grad" x1="0" y1="0" x2="80" y2="80">
        <stop offset="0%" stopColor="#667eea" />
        <stop offset="50%" stopColor="#764ba2" />
        <stop offset="100%" stopColor="#ff6b6b" />
      </linearGradient>
    </defs>
    <line x1="16" y1="64" x2="56" y2="24" stroke="url(#wand-grad)" strokeWidth="3.5" strokeLinecap="round" />
    <circle cx="56" cy="24" r="6" fill="url(#wand-grad)" fillOpacity="0.35" stroke="url(#wand-grad)" strokeWidth="2" />
    <path d="M60 12l2 5 5 2-5 2-2 5-2-5-5-2 5-2 2-5z" fill="#fbbf24" />
    <path d="M70 30l1.5 3.5 3.5 1.5-3.5 1.5L70 40l-1.5-3.5L65 35l3.5-1.5L70 30z" fill="#60a5fa" opacity="0.8" />
    <path d="M44 10l1 3 3 1-3 1-1 3-1-3-3-1 3-1 1-3z" fill="#a78bfa" opacity="0.7" />
    <circle cx="24" cy="52" r="1.5" fill="#fbbf24" opacity="0.6" />
    <circle cx="36" cy="44" r="1" fill="#ff6b6b" opacity="0.5" />
  </svg>
);

const Home = () => {
  const { search } = useLocation();
  const navigate = useNavigate();
  const { state: authState } = useAuth();
  const isAuthenticated = Boolean(authState.accessToken);
  const registerHref = `/auth/register${search}`;
  const [state, setState] = useState<HealthState>({ loading: true });
  const [activeChat, setActiveChat] = useState<ActiveChat>(null);

  /* Analytics: auto-track CTA clicks + section visibility */
  useLandingAnalytics();

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
      navigate(placement === "support" ? "/auth/login" : registerHref);
      return;
    }
    setActiveChat(placement);
  };

  return (
    <div className="landing">
      <TopNav onOpenSupport={() => launchChat("support")} />
      <main className="landing__main">

        {/* ═══════════════════════════════════════════════════════════
            SECTION 1 — HERO (Above the Fold)
            ═══════════════════════════════════════════════════════════ */}
        <section
          className="hero magic-hero"
          id="home"
          data-analytics-section="hero"
        >
          <div className="hero__content">
            <div className="magic-hero__wand" aria-hidden="true">
              <IconWand />
            </div>
            <h1>
              Reframe Your AI Journey:
              <br />
              <span className="magic-gradient-text">From Overwhelm to Effortless Magic.</span>
            </h1>
            <p className="hero__sub">
              In a landscape of complex integrations and compliance risks, CapeControl transforms AI
              into your intuitive, secure ally. Say goodbye to &ldquo;range anxiety&rdquo;&mdash;embrace
              seamless onboarding, secure data querying, and compliant agents that operate like a
              genius whisper in your ear.
            </p>

            <div className="hero__actions">
              <Link
                to="/app/dashboard"
                className="btn btn--primary btn--magic"
                data-analytics-cta="hero-primary"
              >
                Go to Dashboard
              </Link>
              <button
                type="button"
                className="btn btn--ghost"
                onClick={() => launchChat("support")}
                data-analytics-cta="hero-secondary"
              >
                Talk to our team
              </button>
            </div>

            <div className="hero__status">
              <span className={`status status--${statusBadge.tone}`}>
                {statusBadge.label}
              </span>
              {data?.version && <span className="status__meta">API {data.version}</span>}
              {data?.env && <span className="status__meta">{data.env}</span>}
            </div>
          </div>

          {/* HERO VISUAL — Animated magic illustration */}
          <div className="hero__visual" aria-hidden="true">
            <div className="magic-hero__illustration">
              <div className="magic-orb magic-orb--1" />
              <div className="magic-orb magic-orb--2" />
              <div className="magic-orb magic-orb--3" />
              <div className="magic-hero__card">
                <header>
                  <p className="hero__pane-eyebrow">CapeAI</p>
                  <span className="hero__badge">Magic</span>
                </header>
                <p className="magic-hero__tagline">
                  &ldquo;Compliance paths illuminated. Setup dread reduced by 70%.&rdquo;
                </p>
                <div className="magic-hero__sparkles">
                  <span>✦</span><span>✧</span><span>✦</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════
            SECTION 2 — CORE PHILOSOPHY / THE "WHY US?"
            ═══════════════════════════════════════════════════════════ */}
        <section
          className="section magic-philosophy"
          id="philosophy"
          data-analytics-section="philosophy"
        >
          <div className="magic-section__header">
            <h2>The Alchemy of AI: Why Rationality Falls Short</h2>
            <p className="magic-section__subhead">
              Rationality Gets You Bronze. <span className="magic-gradient-text">Magic Gets You Gold.</span>
            </p>
          </div>
          <div className="magic-philosophy__body">
            <p>
              Inspired by Rory Sutherland&apos;s <em>Alchemy</em>, we recognize that engineering
              alone is insufficient for business transformation. The real driver of adoption is the
              psychological spark&mdash;the reframing, the element of surprise. CapeControl offers
              more than just faster AI; it delivers an AI experience that feels truly{" "}
              <strong>liberating</strong>.
            </p>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════
            SECTION 3 — KEY FEATURES / SOLUTIONS
            ═══════════════════════════════════════════════════════════ */}
        <section
          className="section magic-features"
          id="features"
          data-analytics-section="features"
        >
          <div className="magic-section__header">
            <h2>What We Do</h2>
          </div>
          <div className="magic-features__grid">
            <article
              className="magic-feature-card"
              data-analytics-block="feature-tame"
            >
              <div className="magic-feature-card__icon">
                <IconShield />
              </div>
              <h3>Tame AI Anxiety</h3>
              <p>
                Our guided onboarding illuminates compliance paths, dramatically reducing setup dread
                (by 70%), much like neon-lit charging stations guide EV owners.
              </p>
            </article>

            <article
              className="magic-feature-card"
              data-analytics-block="feature-query"
            >
              <div className="magic-feature-card__icon">
                <IconSparkle />
              </div>
              <h3>Query with Magic</h3>
              <p>
                Intuitive data chats designed for energy and finance professionals, transforming
                complex spreadsheets into instant &ldquo;aha!&rdquo; moments&mdash;no PhD required.
              </p>
            </article>

            <article
              className="magic-feature-card"
              data-analytics-block="feature-agents"
            >
              <div className="magic-feature-card__icon">
                <IconRocket />
              </div>
              <h3>Agents That Delight</h3>
              <p>
                Secure, modular AI agents for developers. Build compliant bots that surprise with
                their efficiency, not their errors.
              </p>
            </article>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════
            SECTION 4 — USP / REVERSE BENCHMARK
            ═══════════════════════════════════════════════════════════ */}
        <section
          className="section magic-usp"
          id="usp"
          data-analytics-section="usp"
        >
          <div className="magic-section__header">
            <h2>
              Reverse Benchmark: We Fix the Worst, We Don&apos;t Copy the Best
            </h2>
            <p className="magic-section__subhead">
              We Don&apos;t Copy the Best. <span className="magic-gradient-text">We Fix the Worst.</span>
            </p>
          </div>

          <div className="magic-usp__grid">
            <article
              className="magic-usp-card"
              data-analytics-block="usp-onboarding"
            >
              <span className="magic-usp-card__badge">Solved</span>
              <h3>Clunky Onboarding?</h3>
              <p>
                Our &ldquo;Guided Onboarding Theater&rdquo; offers a personalized, witty concierge
                experience, accelerating adoption by <strong>4x</strong>.
              </p>
            </article>

            <article
              className="magic-usp-card"
              data-analytics-block="usp-compliance"
            >
              <span className="magic-usp-card__badge">Think Again</span>
              <h3>Boring Compliance?</h3>
              <p>
                Experience &ldquo;Compliance as Comedy&rdquo;: tools and videos that make red tape
                feel like an engaging spy thriller. It&apos;s secure, but surprisingly fun.
              </p>
            </article>

            <article
              className="magic-usp-card"
              data-analytics-block="usp-playground"
            >
              <span className="magic-usp-card__badge">Playtime Awaits</span>
              <h3>Rigid Tools?</h3>
              <p>
                The &ldquo;Agent Playground&rdquo; is a free sandbox for wild, compliant creation.
                Devs are empowered to unlock innovation, even by building memes from finance data.
              </p>
            </article>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════
            SECTION 5 — VISION / 80-20 STRATEGY
            ═══════════════════════════════════════════════════════════ */}
        <section
          className="section magic-vision"
          id="vision"
          data-analytics-section="vision"
        >
          <div className="magic-section__header">
            <h2>Explore the Magic: 20% Wild, 80% Wise</h2>
            <p className="magic-section__subhead">
              Balance the Hive: Exploit Efficiency, Explore Surprises.
            </p>
          </div>

          <div className="magic-vision__content">
            <p>
              Like bees scouting new fields, we balance proven ROI (80% Exploit Efficiency) with
              necessary lucky bets (20% Explore Magic). Your AI will thrive on fat-tailed
              wins, rather than starving in local maxima.
            </p>

            <div className="magic-vision__orbs">
              <div className="magic-vision__orb magic-vision__orb--exploit">
                <span className="magic-vision__orb-pct">80%</span>
                <span className="magic-vision__orb-label">Exploit</span>
                <span className="magic-vision__orb-sub">Efficiency</span>
              </div>
              <div className="magic-vision__orb magic-vision__orb--explore">
                <span className="magic-vision__orb-pct">20%</span>
                <span className="magic-vision__orb-label">Explore</span>
                <span className="magic-vision__orb-sub">Magic</span>
              </div>
            </div>

            <div className="magic-vision__community">
              <h3>Join our AI Alchemist Circles</h3>
              <p>
                Share &ldquo;magic moments&rdquo; with peers in finance and energy. A single
                surprising insight can <strong>4x</strong> your processes.
              </p>
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════
            SECTION 6 — SECONDARY CTA / HUMAN SPARK
            ═══════════════════════════════════════════════════════════ */}
        <section
          className="section magic-spark"
          id="spark"
          data-analytics-section="secondary-cta"
        >
          <div className="magic-spark__inner">
            <h2>The Human Spark in an AI World</h2>
            <p>
              Even as algorithms dominate, a genuine &ldquo;posty&rdquo; moment&mdash;a trusted chat
              with our AI Whisperer&mdash;can create brand quakes that last.
            </p>
            <button
              type="button"
              className="btn btn--secondary btn--magic"
              onClick={() => launchChat("support")}
              data-analytics-cta="secondary-discovery"
            >
              Book a Surprise Discovery Chat
            </button>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════
            SECTION 7 — FINAL CTA
            ═══════════════════════════════════════════════════════════ */}
        <section
          className="section magic-final-cta"
          id="get-started"
          data-analytics-section="final-cta"
        >
          <h2>Ready to Ignite Your Alchemy?</h2>
          <p className="magic-final-cta__sub">
            Perceptions shift. Behaviors follow. Worlds transform.
          </p>
          <Link
            to="/app/dashboard"
            className="btn btn--primary btn--magic btn--lg"
            data-analytics-cta="final-primary"
          >
            Go to Dashboard
          </Link>
        </section>

        {/* MOTTO BANNER */}
        <div className="magic-motto" data-analytics-block="motto-banner">
          <p>&ldquo;Ideas that don&apos;t make sense&hellip; until they do.&rdquo;</p>
          <span>— Inspired by Rory Sutherland</span>
        </div>

        {/* LEGAL */}
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
              the service &ldquo;as is&rdquo; with commercially reasonable availability targets.
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

      {/* FOOTER */}
      <footer className="footer" data-analytics-section="footer">
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
                    AI Alchemy platform that transforms enterprises in finance &amp; energy with
                    secure, intuitive, and surprisingly delightful AI workflows.
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
                <li><a href="#home">Overview</a></li>
                <li><a href="#features">Features</a></li>
                <li><a href="#usp">Why CapeControl</a></li>
                <li><a href="#vision">Our Vision</a></li>
              </ul>
            </div>

            <div className="footer__column">
              <h4>Information</h4>
              <ul className="footer__links-list">
                <li><Link to="/customer-terms">Proposal Terms</Link></li>
                <li><Link to="/developers">Developer Info</Link></li>
                <li><Link to="/developer-terms">Developer T&amp;Cs</Link></li>
              </ul>
            </div>

            <div className="footer__column">
              <h4>Company</h4>
              <ul className="footer__links-list">
                <li>
                  <button
                    type="button"
                    className="footer__link-button"
                    onClick={() => launchChat("support")}
                  >
                    Contact
                  </button>
                </li>
                <li><a href="#privacy">Privacy Policy</a></li>
                <li><Link to="/terms-and-conditions">Customer T&amp;Cs</Link></li>
              </ul>
            </div>
          </div>

          <div className="footer__bottom">
            <p>
              © {new Date().getFullYear()} CapeControl. All rights reserved.
            </p>
            <div className="footer__bottom-meta">
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

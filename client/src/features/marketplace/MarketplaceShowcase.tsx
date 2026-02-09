import { useEffect, useState } from "react";

import {
  fetchMarketplaceAgentDetail,
  fetchMarketplaceAgents,
  launchMarketplaceAgent,
  runMarketplaceAgentAction,
  type AgentRun,
  type MarketplaceAgent,
  type MarketplaceAgentDetail,
} from "../../lib/api";

const MarketplaceShowcase = () => {
  const [agents, setAgents] = useState<MarketplaceAgent[]>([]);
  const [filtered, setFiltered] = useState<MarketplaceAgent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeSlug, setActiveSlug] = useState<string | null>(null);
  const [detail, setDetail] = useState<MarketplaceAgentDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [runLoading, setRunLoading] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);
  const [activeRun, setActiveRun] = useState<AgentRun | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionResult, setActionResult] = useState<Record<string, unknown> | null>(null);
  const [nextStepKey, setNextStepKey] = useState<string>("");
  const [blockedReason, setBlockedReason] = useState<string>("");
  const [blockedNotes, setBlockedNotes] = useState<string>("");
  const [faqQuery, setFaqQuery] = useState<string>("");
  const [ticketSubject, setTicketSubject] = useState<string>("");
  const [ticketBody, setTicketBody] = useState<string>("");
  const [search, setSearch] = useState("");
  const [placementFilter, setPlacementFilter] = useState("all");

  useEffect(() => {
    let mounted = true;
    const fetchAgents = async () => {
      try {
        setLoading(true);
        const data = await fetchMarketplaceAgents();
        if (mounted) {
          setAgents(data);
          setFiltered(data);
          setError(null);
        }
      } catch (err) {
        if (mounted) {
          const message = err instanceof Error ? err.message : "Failed to load marketplace";
          setError(message);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };
    fetchAgents();
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    const next = agents.filter((agent) => {
      const matchesSearch = agent.name.toLowerCase().includes(search.toLowerCase());
      const matchesPlacement = placementFilter === "all" || agent.category === placementFilter;
      return matchesSearch && matchesPlacement;
    });
    setFiltered(next);
  }, [agents, search, placementFilter]);

  useEffect(() => {
    if (!activeSlug) {
      setDetail(null);
      setActiveRun(null);
      setActionResult(null);
      setActionError(null);
      setRunError(null);
      setNextStepKey("");
      setBlockedReason("");
      setBlockedNotes("");
      setFaqQuery("");
      setTicketSubject("");
      setTicketBody("");
      return;
    }
    let mounted = true;
    const fetchDetail = async () => {
      try {
        setDetailLoading(true);
        const data = await fetchMarketplaceAgentDetail(activeSlug);
        if (mounted) {
          setDetail(data);
        }
      } catch (err) {
        if (mounted) {
          const message = err instanceof Error ? err.message : "Failed to load agent detail";
          setError(message);
        }
      } finally {
        if (mounted) {
          setDetailLoading(false);
        }
      }
    };
    fetchDetail();
    return () => {
      mounted = false;
    };
  }, [activeSlug]);

  const ensureRun = async () => {
    if (!detail) return null;
    if (activeRun) return activeRun;
    try {
      setRunLoading(true);
      const run = await launchMarketplaceAgent(detail.slug, { source: "marketplace" });
      setActiveRun(run);
      setRunError(null);
      return run;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unable to launch agent";
      setRunError(message);
      return null;
    } finally {
      setRunLoading(false);
    }
  };

  const handleAgentAction = async (action: string, payload: Record<string, unknown>) => {
    if (!detail) return;
    const run = await ensureRun();
    if (!run) return;
    try {
      setActionLoading(true);
      const result = await runMarketplaceAgentAction(detail.slug, run.id, action, payload);
      setActionResult(result.result);
      setActionError(null);
      if (detail.slug === "onboarding-guide") {
        const step = (result.result as { step?: { step_key?: string } }).step;
        if (step?.step_key) {
          setNextStepKey(step.step_key);
        }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unable to run action";
      setActionError(message);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <section className="marketplace" id="marketplace">
      <header className="marketplace__header">
        <span className="badge">Marketplace</span>
        <h3>Discover published CapeControl agents</h3>
        <p>
          Browse curated agents from the community. Launch them in your workspace or review their
          manifests before integrating.
        </p>
        <div className="marketplace__filters">
          <input
            type="search"
            placeholder="Search agents..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <select value={placementFilter} onChange={(event) => setPlacementFilter(event.target.value)}>
            <option value="all">All Categories</option>
            <option value="communication">Communication</option>
            <option value="productivity">Productivity</option>
            <option value="analytics">Analytics</option>
          </select>
        </div>
      </header>

      {error && <p className="marketplace__error">{error}</p>}
      {loading && !error && <p className="marketplace__loading">Loading marketplace…</p>}

      {!loading && agents.length === 0 && !error && (
        <p className="marketplace__empty">No public agents yet. Be the first to publish one!</p>
      )}

      <div className="marketplace__grid">
        {filtered.map((agent) => (
          <article key={agent.id} className="marketplace__card">
            <header>
              <h4>{agent.name}</h4>
              <span className="marketplace__slug">{agent.slug}</span>
            </header>
            <p>{agent.description || "No description provided."}</p>
            <ul className="marketplace__meta">
              <li>
                Version <strong>{agent.version}</strong>
              </li>
              {agent.published_at && (
                <li>
                  Published {new Date(agent.published_at).toLocaleDateString()}
                </li>
              )}
              <li>
                Category: <strong>{agent.category}</strong>
              </li>
            </ul>
            <footer>
              <button
                type="button"
                className="btn btn--ghost btn--small"
                onClick={() => setActiveSlug(agent.slug)}
              >
                View details
              </button>
              <button type="button" className="btn btn--primary btn--small">
                Launch agent
              </button>
            </footer>
          </article>
        ))}
      </div>

      {activeSlug && detail && (
        <div className="marketplace-modal-overlay" role="dialog" aria-modal="true">
          <div className="marketplace-modal">
            <header className="marketplace-modal__header">
              <div>
                <p className="marketplace-modal__eyebrow">Published agent</p>
                <h4>{detail.name}</h4>
                <span className="marketplace__slug">{detail.slug}</span>
              </div>
              <button
                type="button"
                className="marketplace-modal__close"
                onClick={() => setActiveSlug(null)}
              >
                ×
              </button>
            </header>
            <p>{detail.description || "No description provided."}</p>
            {detailLoading && <p>Refreshing details…</p>}
            
            <section className="marketplace-modal__versions">
              <h5>Details</h5>
              <p><strong>Author:</strong> {detail.author}</p>
              <p><strong>License:</strong> {detail.license}</p>
              <p><strong>Rating:</strong> {detail.rating} ({detail.downloads} downloads)</p>
              <p><strong>Permissions:</strong> {detail.permissions?.join(", ") || "None listed"}</p>
              <p><strong>Capabilities:</strong> {detail.tags?.join(", ") || "Not specified"}</p>
              
              {detail.readme && (
                <div className="marketplace-modal__readme">
                  <h5>Readme</h5>
                  <pre>{detail.readme}</pre>
                </div>
              )}
              
              {detail.configuration && (
                 <div className="marketplace-modal__config">
                   <h5>Configuration</h5>
                   <pre>{JSON.stringify(detail.configuration, null, 2)}</pre>
                 </div>
              )}
            </section>

            <section className="marketplace-modal__runner">
              <h5>Agent Runner</h5>
              {runError && <p className="marketplace__error">{runError}</p>}
              {actionError && <p className="marketplace__error">{actionError}</p>}

              {detail.slug === "onboarding-guide" && (
                <div className="marketplace-runner">
                  <div className="marketplace-runner__row">
                    <button
                      type="button"
                      className="btn btn--ghost btn--small"
                      onClick={() => handleAgentAction("next_step", {})}
                      disabled={actionLoading}
                    >
                      Show next step
                    </button>
                    <input
                      type="text"
                      placeholder="Step key"
                      value={nextStepKey}
                      onChange={(event) => setNextStepKey(event.target.value)}
                    />
                    <button
                      type="button"
                      className="btn btn--primary btn--small"
                      onClick={() => handleAgentAction("complete_step", { step_key: nextStepKey })}
                      disabled={actionLoading || !nextStepKey}
                    >
                      Mark complete
                    </button>
                  </div>
                  <div className="marketplace-runner__row">
                    <input
                      type="text"
                      placeholder="Blocked reason"
                      value={blockedReason}
                      onChange={(event) => setBlockedReason(event.target.value)}
                    />
                    <input
                      type="text"
                      placeholder="Notes (optional)"
                      value={blockedNotes}
                      onChange={(event) => setBlockedNotes(event.target.value)}
                    />
                    <button
                      type="button"
                      className="btn btn--ghost btn--small"
                      onClick={() =>
                        handleAgentAction("blocked", {
                          step_key: nextStepKey,
                          reason: blockedReason,
                          notes: blockedNotes || undefined,
                        })
                      }
                      disabled={actionLoading || !nextStepKey || !blockedReason}
                    >
                      I&apos;m blocked
                    </button>
                  </div>
                </div>
              )}

              {detail.slug === "cape-support-bot" && (
                <div className="marketplace-runner">
                  <div className="marketplace-runner__row">
                    <input
                      type="text"
                      placeholder="Search FAQs"
                      value={faqQuery}
                      onChange={(event) => setFaqQuery(event.target.value)}
                    />
                    <button
                      type="button"
                      className="btn btn--ghost btn--small"
                      onClick={() => handleAgentAction("faq_search", { query: faqQuery })}
                      disabled={actionLoading}
                    >
                      Search
                    </button>
                    <button
                      type="button"
                      className="btn btn--ghost btn--small"
                      onClick={() => handleAgentAction("list_tickets", {})}
                      disabled={actionLoading}
                    >
                      My tickets
                    </button>
                  </div>
                  <div className="marketplace-runner__row">
                    <input
                      type="text"
                      placeholder="Ticket subject"
                      value={ticketSubject}
                      onChange={(event) => setTicketSubject(event.target.value)}
                    />
                    <input
                      type="text"
                      placeholder="Ticket details"
                      value={ticketBody}
                      onChange={(event) => setTicketBody(event.target.value)}
                    />
                    <button
                      type="button"
                      className="btn btn--primary btn--small"
                      onClick={() => handleAgentAction("create_ticket", { subject: ticketSubject, body: ticketBody })}
                      disabled={actionLoading || !ticketSubject || !ticketBody}
                    >
                      Create ticket
                    </button>
                  </div>
                </div>
              )}

              {detail.slug === "data-analyst" && (
                <div className="marketplace-runner">
                  <div className="marketplace-runner__row">
                    {[
                      "project_status",
                      "top_blockers",
                      "onboarding_completion_rate",
                      "agent_usage_last_7d",
                      "open_support_tickets",
                    ].map((intent) => (
                      <button
                        key={intent}
                        type="button"
                        className="btn btn--ghost btn--small"
                        onClick={() => handleAgentAction("insight", { intent })}
                        disabled={actionLoading}
                      >
                        {intent.replace(/_/g, " ")}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {actionResult && (
                <pre className="marketplace-modal__config">
                  {JSON.stringify(actionResult, null, 2)}
                </pre>
              )}
            </section>

            <div className="marketplace-modal__actions">
              <button type="button" className="btn btn--ghost btn--small" onClick={() => setActiveSlug(null)}>
                Close
              </button>
              <button
                type="button"
                className="btn btn--primary btn--small"
                onClick={() => ensureRun()}
                disabled={runLoading}
              >
                {runLoading ? "Launching…" : "Launch agent"}
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};

export default MarketplaceShowcase;

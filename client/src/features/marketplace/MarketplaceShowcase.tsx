import { useEffect, useState, useCallback } from "react";

import {
  searchMarketplace,
  fetchMarketplaceCategories,
  fetchMarketplaceAgentDetail,
  launchMarketplaceAgent,
  runMarketplaceAgentAction,
  installMarketplaceAgent,
  type AgentRun,
  type MarketplaceAgent,
  type MarketplaceAgentDetail,
} from "../../lib/api";

/** Human-friendly category labels. */
const CATEGORY_LABELS: Record<string, string> = {
  automation: "Automation",
  analytics: "Analytics",
  integration: "Integration",
  security: "Security",
  productivity: "Productivity",
  ai_assistant: "AI Assistant",
  workflow: "Workflow",
  monitoring: "Monitoring",
  communication: "Communication",
  development: "Development",
};

interface MarketplaceShowcaseProps {
  /** Pre-selected category from the parent page. */
  categoryFilter?: string | null;
}

const MarketplaceShowcase = ({ categoryFilter }: MarketplaceShowcaseProps) => {
  const [agents, setAgents] = useState<MarketplaceAgent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [categories, setCategories] = useState<string[]>([]);
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
  const [localCategory, setLocalCategory] = useState("all");
  const [installMsg, setInstallMsg] = useState<string | null>(null);

  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const PAGE_SIZE = 20;

  // Resolve effective category: prop overrides local dropdown
  const effectiveCategory = categoryFilter ?? (localCategory === "all" ? undefined : localCategory);

  // Fetch categories for filter dropdown
  useEffect(() => {
    fetchMarketplaceCategories()
      .then(setCategories)
      .catch(() => setCategories(Object.keys(CATEGORY_LABELS)));
  }, []);

  // Fetch agents via marketplace search API
  const loadAgents = useCallback(async () => {
    try {
      setLoading(true);
      const result = await searchMarketplace({
        query: search || undefined,
        category: effectiveCategory || undefined,
        page,
        limit: PAGE_SIZE,
        sort_by: "updated",
      });
      setAgents(result.agents);
      setTotal(result.total);
      setTotalPages(result.pages);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load marketplace";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [search, effectiveCategory, page]);

  useEffect(() => {
    loadAgents();
  }, [loadAgents]);

  // Reset to page 1 when filters change
  useEffect(() => {
    setPage(1);
  }, [search, effectiveCategory]);

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
          {/* Only show local dropdown when parent hasn't pre-selected a category */}
          {!categoryFilter && (
            <select value={localCategory} onChange={(event) => setLocalCategory(event.target.value)}>
              <option value="all">All Categories</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {CATEGORY_LABELS[cat] ?? cat}
                </option>
              ))}
            </select>
          )}
        </div>
      </header>

      {error && <p className="marketplace__error">{error}</p>}
      {installMsg && <p className="marketplace__success" style={{ color: "green" }}>{installMsg}</p>}
      {loading && !error && <p className="marketplace__loading">Loading marketplace…</p>}

      {!loading && agents.length === 0 && !error && (
        <p className="marketplace__empty">No public agents yet. Be the first to publish one!</p>
      )}

      <div className="marketplace__grid">
        {agents.map((agent) => (
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
                Category: <strong>{CATEGORY_LABELS[agent.category] ?? agent.category}</strong>
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
              <button
                type="button"
                className="btn btn--primary btn--small"
                onClick={async () => {
                  try {
                    const res = await installMarketplaceAgent(agent.id, agent.version);
                    setInstallMsg(res.message);
                    setTimeout(() => setInstallMsg(null), 4000);
                  } catch (err) {
                    const message = err instanceof Error ? err.message : "Install failed";
                    setInstallMsg(message);
                    setTimeout(() => setInstallMsg(null), 4000);
                  }
                }}
              >
                Install
              </button>
            </footer>
          </article>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <nav className="marketplace__pagination" style={{ display: "flex", gap: "0.5rem", justifyContent: "center", padding: "1rem 0" }}>
          <button
            type="button"
            className="btn btn--ghost btn--small"
            disabled={page <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          >
            ← Previous
          </button>
          <span style={{ lineHeight: "2rem" }}>
            Page {page} of {totalPages} ({total} agent{total !== 1 ? "s" : ""})
          </span>
          <button
            type="button"
            className="btn btn--ghost btn--small"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          >
            Next →
          </button>
        </nav>
      )}

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

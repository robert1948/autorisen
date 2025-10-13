import { useEffect, useState } from "react";

import {
  fetchMarketplaceAgentDetail,
  fetchMarketplaceAgents,
  runFlow,
  type FlowRunResponse,
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
  const [runResult, setRunResult] = useState<FlowRunResponse | null>(null);
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
      const placement = agent.version.manifest?.placement as string | undefined;
      const matchesPlacement = placementFilter === "all" || placement === placementFilter;
      return matchesSearch && matchesPlacement;
    });
    setFiltered(next);
  }, [agents, search, placementFilter]);

  useEffect(() => {
    if (!activeSlug) {
      setDetail(null);
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

  const handleRunAgent = async () => {
    if (!detail) return;
    const published = detail.published_version
      ? detail.versions.find((version) => version.id === detail.published_version)
      : detail.versions[0];
    const manifest = published?.manifest ?? {};
    const tools = Array.isArray(manifest.tools)
      ? (manifest.tools as string[])
      : [];
    const firstTool = tools[0];
    if (!firstTool) {
      setRunError("Agent manifest does not declare tools");
      return;
    }

    setRunLoading(true);
    setRunError(null);
    setRunResult(null);
    try {
      const idempotencyKey =
        typeof crypto !== "undefined" && "randomUUID" in crypto
          ? crypto.randomUUID()
          : `marketplace-${Date.now()}`;
      const response = await runFlow({
        agent_slug: detail.slug,
        agent_version: published?.version,
        tool_calls: [
          {
            name: firstTool,
            payload: {},
          },
        ],
        idempotency_key: idempotencyKey,
        max_attempts: 3,
      });
      setRunResult(response);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to run agent";
      setRunError(message);
    } finally {
      setRunLoading(false);
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
            <option value="all">All placements</option>
            <option value="support">Support</option>
            <option value="onboarding">Onboarding</option>
            <option value="energy">Energy</option>
            <option value="money">Money</option>
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
                Version <strong>{agent.version.version}</strong>
              </li>
              {agent.version.published_at && (
                <li>
                  Published {new Date(agent.version.published_at).toLocaleDateString()}
                </li>
              )}
              <li>
                Placement: <strong>{agent.version.manifest?.placement as string}</strong>
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
              <h5>Versions</h5>
              <ul>
                {detail.versions.map((version) => (
                  <li key={version.id}>
                    <div className="marketplace-modal__version-row">
                      <strong>{version.version}</strong>
                      <span className="marketplace-modal__status">{version.status}</span>
                    </div>
                    <p className="marketplace-modal__meta">
                      Created {new Date(version.created_at).toLocaleDateString()}
                      {version.published_at && (
                        <>
                          {" · "}
                          Published {new Date(version.published_at).toLocaleDateString()}
                        </>
                      )}
                    </p>
                    <pre className="marketplace-modal__manifest">
                      {JSON.stringify(version.manifest, null, 2)}
                    </pre>
                  </li>
                ))}
              </ul>
            </section>
            <div className="marketplace-modal__actions">
              <button type="button" className="btn btn--ghost btn--small" onClick={() => setActiveSlug(null)}>
                Close
              </button>
              <button
                type="button"
                className="btn btn--primary btn--small"
                onClick={handleRunAgent}
                disabled={runLoading}
              >
                {runLoading ? "Running…" : "Run with CapeControl"}
              </button>
            </div>
            {runError && <p className="marketplace-modal__error">{runError}</p>}
            {runResult && (
              <section className="marketplace-modal__run">
                <h5>Last run preview</h5>
                <p className="marketplace-modal__run-meta">
                  Status: <strong>{runResult.status}</strong> · Attempt{" "}
                  {runResult.attempt}/{runResult.max_attempts}
                  {runResult.error_message && (
                    <>
                      {" · "}
                      <span className="marketplace-modal__error-inline">
                        {runResult.error_message}
                      </span>
                    </>
                  )}
                </p>
                <ul>
                  {runResult.steps.map((step) => (
                    <li key={step.event_id}>
                      <div className="marketplace-modal__version-row">
                        <strong>{step.tool}</strong>
                        <span className="marketplace-modal__status">event {step.event_id}</span>
                      </div>
                      <pre className="marketplace-modal__manifest">
                        {JSON.stringify(step.result, null, 2)}
                      </pre>
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </div>
        </div>
      )}
    </section>
  );
};

export default MarketplaceShowcase;

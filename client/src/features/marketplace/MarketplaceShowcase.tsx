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
      const matchesPlacement = placementFilter === "all" || agent.category === placementFilter;
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
    // TODO: Implement run logic with new API structure
    // For now, we just show an alert or log
    console.log("Run agent not implemented for new structure yet");
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
          </div>
        </div>
      )}
    </section>
  );
};

export default MarketplaceShowcase;

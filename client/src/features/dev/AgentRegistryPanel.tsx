import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";

import {
  Agent,
  createAgent,
  createAgentVersion,
  fetchAgentDetail,
  listAgents,
  publishAgentVersion,
  type CreateAgentPayload,
} from "../../lib/api";
import AgentManifestEditor from "./AgentManifestEditor";

type FormState = {
  name: string;
  slug: string;
  description: string;
  visibility: "private" | "public";
};

type VersionFormState = {
  version: string;
  changelog: string;
};

type ManifestValidation =
  | { ok: true; value: Record<string, unknown> }
  | { ok: false; error: string };

const initialForm: FormState = {
  name: "",
  slug: "",
  description: "",
  visibility: "private",
};

const initialVersionForm: VersionFormState = {
  version: "",
  changelog: "",
};

const pretty = (data: unknown) => JSON.stringify(data, null, 2);

function buildManifestTemplate(agent: Agent) {
  return {
    name: agent.name,
    description: agent.description ?? "",
    placement: "support",
    tools: ["support.ticket"],
  };
}

function validateManifest(raw: unknown): ManifestValidation {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    return { ok: false, error: "Manifest must be a JSON object." };
  }

  const manifest = raw as Record<string, unknown>;
  const missing: string[] = [];
  for (const key of ["name", "description", "placement", "tools"]) {
    if (!(key in manifest)) missing.push(key);
  }
  if (missing.length > 0) {
    return { ok: false, error: `Manifest missing keys: ${missing.join(", ")}.` };
  }

  const name = manifest.name;
  const placement = manifest.placement;
  const tools = manifest.tools;

  if (typeof name !== "string" || name.trim().length === 0) {
    return { ok: false, error: "Manifest requires a non-empty 'name' string." };
  }

  if (typeof placement !== "string" || placement.trim().length === 0) {
    return { ok: false, error: "Manifest requires a non-empty 'placement' string." };
  }

  if (!Array.isArray(tools) || tools.length === 0) {
    return { ok: false, error: "Manifest.tools must be a non-empty array." };
  }

  if (tools.some((tool) => typeof tool !== "string" || tool.trim().length === 0)) {
    return { ok: false, error: "Manifest.tools entries must be non-empty strings." };
  }

  return { ok: true, value: manifest };
}

const AgentRegistryPanel = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<FormState>(initialForm);
  const [saving, setSaving] = useState(false);
  const [versionTarget, setVersionTarget] = useState<Agent | null>(null);
  const [versionForm, setVersionForm] = useState<VersionFormState>(initialVersionForm);
  const [versionSaving, setVersionSaving] = useState(false);
  const [publishing, setPublishing] = useState<Record<string, boolean>>({});
  const [manifestAgent, setManifestAgent] = useState<Agent | null>(null);
  const [versionManifestText, setVersionManifestText] = useState("");
  const [versionError, setVersionError] = useState<string | null>(null);
  const [publishedMarketplaceSlug, setPublishedMarketplaceSlug] = useState<string | null>(null);

  const isMountedRef = useRef(true);

  useEffect(() => {
    isMountedRef.current = true;
    let mounted = true;
    const fetchAgents = async () => {
      try {
        setLoading(true);
        const data = await listAgents();
        if (mounted) {
          setAgents(data);
          setError(null);
        }
      } catch (err) {
        if (mounted) {
          const message = err instanceof Error ? err.message : "Failed to load agents";
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
      isMountedRef.current = false;
    };
  }, []);

  const resetForm = () => setForm(initialForm);
  const resetVersionForm = () => setVersionForm(initialVersionForm);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    try {
      const payload: CreateAgentPayload = {
        name: form.name.trim(),
        slug: form.slug.trim(),
        description: form.description.trim() || undefined,
        visibility: form.visibility,
      };
      const created = await createAgent(payload);
      if (isMountedRef.current) {
        setAgents((prev) => [created, ...prev]);
        resetForm();
        setError(null);
      }
    } catch (err) {
      if (isMountedRef.current) {
        const message = err instanceof Error ? err.message : "Unable to create agent";
        setError(message);
      }
    } finally {
      if (isMountedRef.current) {
        setSaving(false);
      }
    }
  };

  const handleVersionSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!versionTarget) return;
    setVersionError(null);

    let parsed: unknown;
    try {
      parsed = JSON.parse(versionManifestText);
    } catch (jsonErr) {
      const message = jsonErr instanceof Error ? jsonErr.message : "Invalid JSON";
      setVersionError(`Invalid JSON: ${message}`);
      return;
    }

    const validated = validateManifest(parsed);
    if (!validated.ok) {
      setVersionError(validated.error);
      return;
    }

    setVersionSaving(true);
    try {
      const payload = {
        version: versionForm.version.trim(),
        manifest: validated.value,
        changelog: versionForm.changelog.trim() || undefined,
        status: "draft" as const,
      };
      const created = await createAgentVersion(versionTarget.id, payload);
      if (isMountedRef.current) {
        setAgents((prev) =>
          prev.map((agent) =>
            agent.id === versionTarget.id
              ? { ...agent, versions: [created, ...agent.versions] }
              : agent,
          ),
        );
        setError(null);
        setVersionSaving(false);
        resetVersionForm();
        setVersionManifestText("");
        setVersionTarget(null);
      }
    } catch (err) {
      if (isMountedRef.current) {
        const message = err instanceof Error ? err.message : "Unable to create agent version";
        setVersionError(message);
        setVersionSaving(false);
      }
    } finally {
      if (isMountedRef.current) {
        setVersionSaving(false);
      }
    }
  };

  const agentCountLabel = useMemo(() => {
    if (loading) return "Fetching agents…";
    if (agents.length === 0) return "No agents created yet";
    return `${agents.length} agent${agents.length === 1 ? "" : "s"}`;
  }, [agents.length, loading]);

  return (
    <div className="registry">
      <header className="registry__header">
        <div>
          <span className="badge">Developer Portal</span>
          <h3>Agent Registry</h3>
          <p>Manage your private CapeControl agents and publish new versions.</p>
        </div>
        <p className="registry__meta">{agentCountLabel}</p>
      </header>

      <section className="registry__form">
        <h4>Create a new agent</h4>
        <form onSubmit={handleSubmit} className="registry__fields">
          <label>
            Name
            <input
              required
              minLength={3}
              value={form.name}
              onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
              placeholder="CapeAI Demo"
            />
          </label>
          <label>
            Slug
            <input
              required
              pattern="[a-z0-9-]+"
              title="lowercase letters, numbers, and hyphens"
              value={form.slug}
              onChange={(event) => setForm((prev) => ({ ...prev, slug: event.target.value }))}
              placeholder="capeai-demo"
            />
          </label>
          <label>
            Visibility
            <select
              value={form.visibility}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, visibility: event.target.value as FormState["visibility"] }))
              }
            >
              <option value="private">Private</option>
              <option value="public">Public</option>
            </select>
          </label>
          <label className="registry__fullwidth">
            Description
            <textarea
              rows={3}
              value={form.description}
              onChange={(event) => setForm((prev) => ({ ...prev, description: event.target.value }))}
              placeholder="Short summary of what this agent does."
            />
          </label>
          <button className="btn btn--primary" type="submit" disabled={saving}>
            {saving ? "Creating…" : "Create Agent"}
          </button>
        </form>
      </section>

      <section className="registry__list">
        <h4>Your agents</h4>
        {error && <p className="registry__error">{error}</p>}
        {loading && !error && <p>Loading agents…</p>}
        {!loading && agents.length === 0 && !error && (
          <p className="registry__empty">No agents yet. Create one to get started.</p>
        )}
        <ul>
          {agents.map((agent) => (
            <li key={agent.id} className="registry__item">
              <div>
                <strong>{agent.name}</strong>
                <span className="registry__slug">{agent.slug}</span>
              </div>
              <p>{agent.description || "No description provided."}</p>
              <p className="registry__versions">
                {agent.versions.length} version{agent.versions.length === 1 ? "" : "s"}
              </p>
              <div className="registry__item-actions">
                <button
                  type="button"
                  className="btn btn--ghost btn--small"
                  onClick={() => {
                    setVersionTarget(agent);
                    resetVersionForm();
                    setVersionError(null);
                    setPublishedMarketplaceSlug(null);
                    setVersionManifestText(pretty(buildManifestTemplate(agent)));
                  }}
                >
                  New version
                </button>
                <button
                  type="button"
                  className="btn btn--ghost btn--small"
                  onClick={async () => {
                    try {
                      const detail = await fetchAgentDetail(agent.id);
                      if (isMountedRef.current) {
                        setManifestAgent(detail);
                      }
                    } catch (err) {
                      if (isMountedRef.current) {
                        const message =
                          err instanceof Error ? err.message : "Unable to load agent manifest";
                        setError(message);
                      }
                    }
                  }}
                >
                  Edit manifest
                </button>
              </div>
              {agent.versions.length > 0 && (
                <ul className="registry__version-list">
                  {agent.versions.map((version) => (
                    <li key={version.id}>
                      <strong>{version.version}</strong> — {version.status}
                      {version.published_at && (
                        <span className="registry__version-meta">
                          · published {new Date(version.published_at).toLocaleDateString()}
                        </span>
                      )}
                      {version.status !== "published" && (
                        <button
                          type="button"
                          className="btn btn--ghost btn--tiny"
                          disabled={publishing[version.id]}
                          onClick={async () => {
                            setPublishing((prev) => ({ ...prev, [version.id]: true }));
                            try {
                              const updated = await publishAgentVersion(agent.id, version.id);
                              if (isMountedRef.current) {
                                setAgents((prev) =>
                                  prev.map((current) => {
                                    if (current.id !== agent.id) return current;
                                    const updatedVersions = current.versions.map((existing) => {
                                      if (existing.id === updated.id) {
                                        return updated;
                                      }
                                      if (existing.status === "published") {
                                        return { ...existing, status: "archived" };
                                      }
                                      return existing;
                                    });
                                    return { ...current, versions: updatedVersions };
                                  }),
                                );
                                setPublishedMarketplaceSlug(agent.slug);
                              }
                            } catch (err) {
                              if (isMountedRef.current) {
                                const message =
                                  err instanceof Error ? err.message : "Unable to publish version";
                                setError(message);
                              }
                            } finally {
                              if (isMountedRef.current) {
                                setPublishing((prev) => ({ ...prev, [version.id]: false }));
                              }
                            }
                          }}
                        >
                          {publishing[version.id] ? "Publishing…" : "Publish"}
                        </button>
                      )}
                      {version.status === "published" && publishedMarketplaceSlug === agent.slug && (
                        <Link
                          to="/app/marketplace"
                          className="btn btn--ghost btn--tiny"
                          style={{ marginLeft: "0.5rem" }}
                        >
                          View in Marketplace
                        </Link>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ul>
      </section>

      {versionTarget && (
        <div className="registry-modal-overlay" role="dialog" aria-modal="true">
          <div className="registry-modal">
            <header className="registry-modal__header">
              <div>
                <p className="registry-modal__eyebrow">Agent version</p>
                <h4>{versionTarget.name}</h4>
              </div>
              <button
                type="button"
                className="registry-modal__close"
                onClick={() => {
                  setVersionTarget(null);
                  resetVersionForm();
                }}
              >
                ×
              </button>
            </header>
            <form onSubmit={handleVersionSubmit} className="registry-modal__form">
              <label>
                Version tag
                <input
                  required
                  minLength={1}
                  value={versionForm.version}
                  onChange={(event) =>
                    setVersionForm((prev) => ({ ...prev, version: event.target.value }))
                  }
                  placeholder="v1.0.0"
                />
              </label>
              <label className="registry-modal__fullwidth">
                Manifest (JSON)
                <textarea
                  rows={12}
                  value={versionManifestText}
                  onChange={(event) => setVersionManifestText(event.target.value)}
                  placeholder='{"name":"My agent","description":"","placement":"support","tools":["support.ticket"]}'
                />
              </label>
              <label className="registry-modal__fullwidth">
                Changelog (optional)
                <textarea
                  rows={3}
                  value={versionForm.changelog}
                  onChange={(event) =>
                    setVersionForm((prev) => ({ ...prev, changelog: event.target.value }))
                  }
                  placeholder="Describe what changed in this version."
                />
              </label>
              {versionError && <p className="registry__error">{versionError}</p>}
              <div className="registry-modal__actions">
                <button
                  type="button"
                  className="btn btn--ghost btn--small"
                  onClick={() => {
                    setVersionTarget(null);
                    resetVersionForm();
                    setVersionManifestText("");
                    setVersionError(null);
                  }}
                >
                  Cancel
                </button>
                <button className="btn btn--primary" type="submit" disabled={versionSaving}>
                  {versionSaving ? "Saving…" : "Create version"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      {manifestAgent && (
        <div className="registry-modal-overlay" role="dialog" aria-modal="true">
          <div className="registry-modal registry-modal--wide">
            <header className="registry-modal__header">
              <div>
                <p className="registry-modal__eyebrow">Manifest editor</p>
                <h4>{manifestAgent.name}</h4>
              </div>
              <button
                type="button"
                className="registry-modal__close"
                onClick={() => setManifestAgent(null)}
              >
                ×
              </button>
            </header>
            <AgentManifestEditor agent={manifestAgent} />
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentRegistryPanel;

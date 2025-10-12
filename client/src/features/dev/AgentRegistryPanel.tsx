import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  Agent,
  AgentVersion,
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
  placement: string;
  tools: string;
  changelog: string;
  status: "draft" | "published";
};

const initialForm: FormState = {
  name: "",
  slug: "",
  description: "",
  visibility: "private",
};

const initialVersionForm: VersionFormState = {
  version: "",
  placement: "",
  tools: "",
  changelog: "",
  status: "draft",
};

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

  useEffect(() => {
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
      setAgents((prev) => [created, ...prev]);
      resetForm();
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unable to create agent";
      setError(message);
    } finally {
      setSaving(false);
    }
  };

  const handleVersionSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!versionTarget) return;
    const placement = versionForm.placement.trim();
    const tools = versionForm.tools
      .split(",")
      .map((tool) => tool.trim())
      .filter(Boolean);
    if (!placement || tools.length === 0) {
      setError("Placement and at least one tool are required.");
      return;
    }

    setVersionSaving(true);
    try {
      const payload = {
        version: versionForm.version.trim(),
        manifest: {
          name: versionTarget.name,
          description: versionTarget.description ?? "",
          placement,
          tools,
        },
        changelog: versionForm.changelog.trim() || undefined,
        status: versionForm.status,
      };
      const created = await createAgentVersion(versionTarget.id, payload);
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
      setVersionTarget(null);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Unable to create agent version";
      setError(message);
      setVersionSaving(false);
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
                      setManifestAgent(detail);
                    } catch (err) {
                      const message =
                        err instanceof Error ? err.message : "Unable to load agent manifest";
                      setError(message);
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
                            } catch (err) {
                              const message =
                                err instanceof Error ? err.message : "Unable to publish version";
                              setError(message);
                            } finally {
                              setPublishing((prev) => ({ ...prev, [version.id]: false }));
                            }
                          }}
                        >
                          {publishing[version.id] ? "Publishing…" : "Publish"}
                        </button>
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
              <label>
                Placement
                <input
                  required
                  value={versionForm.placement}
                  onChange={(event) =>
                    setVersionForm((prev) => ({ ...prev, placement: event.target.value }))
                  }
                  placeholder="support"
                />
              </label>
              <label>
                Tools (comma separated)
                <input
                  required
                  value={versionForm.tools}
                  onChange={(event) =>
                    setVersionForm((prev) => ({ ...prev, tools: event.target.value }))
                  }
                  placeholder="support.ticket,support.notify"
                />
              </label>
              <label>
                Status
                <select
                  value={versionForm.status}
                  onChange={(event) =>
                    setVersionForm((prev) => ({
                      ...prev,
                      status: event.target.value as VersionFormState["status"],
                    }))
                  }
                >
                  <option value="draft">Draft</option>
                  <option value="published">Published</option>
                </select>
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
              <div className="registry-modal__actions">
                <button
                  type="button"
                  className="btn btn--ghost btn--small"
                  onClick={() => {
                    setVersionTarget(null);
                    resetVersionForm();
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

import { FormEvent, useMemo, useState } from "react";

import {
  createAgentVersion,
  fetchAgentDetail,
  type Agent,
} from "../../lib/api";

const pretty = (data: unknown) => JSON.stringify(data, null, 2);

const initialManifest = {
  name: "Agent name",
  description: "Describe what this agent does",
  placement: "support",
  tools: ["support.ticket"],
};

type ManifestValidation = { ok: true; value: Record<string, unknown> } | { ok: false; error: string };

function validateManifest(raw: unknown): ManifestValidation {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    return { ok: false, error: "Manifest must be a JSON object." };
  }

  const manifest = raw as Record<string, unknown>;
  const name = manifest.name;
  const placement = manifest.placement;
  const tools = manifest.tools;

  if (typeof name !== "string" || name.trim().length === 0) {
    return { ok: false, error: "Manifest requires a non-empty 'name' string." };
  }

  if (typeof placement !== "string" || placement.trim().length === 0) {
    return { ok: false, error: "Manifest requires a non-empty 'placement' string." };
  }

  if (!Array.isArray(tools) || tools.length === 0 || tools.some((tool) => typeof tool !== "string" || tool.trim().length === 0)) {
    return { ok: false, error: "Manifest requires a non-empty 'tools' array of strings." };
  }

  return { ok: true, value: manifest };
}

const AgentManifestEditor = ({ agent }: { agent: Agent }) => {
  const [version, setVersion] = useState("v1.0.0");
  const [manifestText, setManifestText] = useState(
    pretty(agent.versions[0]?.manifest ?? initialManifest),
  );
  const [changelog, setChangelog] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState(agent.versions[0]?.manifest ?? initialManifest);

  const handlePreview = () => {
    try {
      const parsed = JSON.parse(manifestText);
      const validated = validateManifest(parsed);
      if (!validated.ok) {
        setError(validated.error);
        return;
      }
      setPreview(validated.value);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Invalid JSON";
      setError(message);
    }
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const parsed = JSON.parse(manifestText);
      const validated = validateManifest(parsed);
      if (!validated.ok) {
        setError(validated.error);
        return;
      }
      await createAgentVersion(agent.id, {
        version,
        manifest: validated.value,
        changelog,
        status: "draft",
      });
      await fetchAgentDetail(agent.id); // refresh cached data server-side (optional)
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to save version";
      setError(message);
    } finally {
      setSaving(false);
    }
  };

  const manifestValid = useMemo(() => {
    try {
      const parsed = JSON.parse(manifestText);
      return validateManifest(parsed).ok;
    } catch {
      return false;
    }
  }, [manifestText]);

  return (
    <section className="manifest-editor">
      <header>
        <h4>Manifest editor</h4>
        <p>Define placement and tools used by this agent. JSON must match your tool adapters.</p>
      </header>
      <form className="manifest-form" onSubmit={handleSubmit}>
        <label>
          Version tag
          <input
            required
            value={version}
            onChange={(event) => setVersion(event.target.value)}
            placeholder="v1.0.1"
          />
        </label>
        <label className="manifest-form__full">
          Manifest JSON
          <textarea
            value={manifestText}
            onChange={(event) => setManifestText(event.target.value)}
            rows={16}
          />
        </label>
        <label className="manifest-form__full">
          Changelog (optional)
          <textarea
            value={changelog}
            onChange={(event) => setChangelog(event.target.value)}
            rows={4}
          />
        </label>
        {error && <p className="manifest-error">{error}</p>}
        <div className="manifest-actions">
          <button type="button" className="btn btn--ghost" onClick={handlePreview}>
            Preview
          </button>
          <button
            className="btn btn--primary"
            type="submit"
            disabled={saving || !manifestValid}
          >
            {saving ? "Saving…" : "Save version"}
          </button>
        </div>
      </form>
      <section className="manifest-preview">
        <h5>Preview</h5>
        <pre>{pretty(preview)}</pre>
      </section>
    </section>
  );
};

export default AgentManifestEditor;

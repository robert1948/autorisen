/**
 * DeveloperHubSection — developer-specific dashboard modules.
 *
 * Per spec §3.6: rendered only when user.role === 'developer' || 'admin'.
 * Loaded lazily via React.lazy() in the parent Dashboard component.
 *
 * Sub-sections:
 *   §3.6.1 API Key Management
 *   §3.6.2 Workflow Management
 *   §3.6.3 Developer Quick Links
 */

import { useCallback, useEffect, useState } from "react";
import type { UserProfile } from "../../types/user";

interface DeveloperHubSectionProps {
  user: UserProfile;
}

/* ── Types ────────────────────────────────────────── */

interface ApiKey {
  id: string;
  name: string;
  createdAt: string;
  lastUsed: string | null;
  status: "active" | "revoked" | "expired";
  maskedKey: string; // last 4 chars only
}

interface Workflow {
  id: string;
  name: string;
  type: "approved" | "custom";
  status: "active" | "paused" | "draft";
  lastRun: string | null;
}

/* ── Main component ───────────────────────────────── */

export default function DeveloperHubSection({ user }: DeveloperHubSectionProps) {
  const devProfile = user.developerProfile;

  return (
    <div className="col-span-full space-y-6">
      <h2 className="text-lg font-bold text-slate-900">Developer Hub</h2>

      {/* §3.6.1 API Key Management */}
      <ApiKeyManagement maxKeys={5} />

      {/* §3.6.2 Workflow Management */}
      <WorkflowManagement />

      {/* §3.6.3 Developer Quick Links */}
      <DeveloperQuickLinks hasApiKeys={(devProfile?.apiKeysCount ?? 0) > 0} />
    </div>
  );
}

/* ── §3.6.1 API Key Management ────────────────────── */

function ApiKeyManagement({ maxKeys }: { maxKeys: number }) {
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadKeys = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Connect to real endpoint: GET /api/v1/developer/api-keys
      setKeys([]);
    } catch {
      setError("Failed to load API keys.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadKeys();
  }, [loadKeys]);

  const activeCount = keys.filter((k) => k.status === "active").length;
  const canCreate = activeCount < maxKeys;

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-slate-900">API Keys</h3>
        <span className="text-xs text-slate-500">
          {activeCount} / {maxKeys} active
        </span>
      </div>

      {loading && <p className="mt-3 text-sm text-slate-500">Loading API keys…</p>}
      {error && (
        <div className="mt-3">
          <p className="text-sm text-red-600">{error}</p>
          <button
            onClick={loadKeys}
            className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-700"
          >
            Retry
          </button>
        </div>
      )}

      {!loading && !error && keys.length === 0 && (
        <div className="mt-4 rounded-md border border-dashed border-slate-200 p-4 text-center">
          <p className="text-sm text-slate-500">No API keys yet.</p>
          <button
            disabled={!canCreate}
            className="mt-3 inline-flex items-center rounded-md bg-blue-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
          >
            Create API Key
          </button>
        </div>
      )}

      {!loading && keys.length > 0 && (
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left text-sm" role="table">
            <thead>
              <tr className="border-b border-slate-100 text-xs uppercase text-slate-500">
                <th className="py-2 pr-4" scope="col">Name</th>
                <th className="py-2 pr-4" scope="col">Key</th>
                <th className="py-2 pr-4" scope="col">Status</th>
                <th className="py-2 pr-4" scope="col">Last Used</th>
                <th className="py-2" scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              {keys.map((key) => (
                <tr key={key.id} className="border-b border-slate-50">
                  <td className="py-3 pr-4 font-medium text-slate-900">{key.name}</td>
                  <td className="py-3 pr-4 font-mono text-slate-500">****{key.maskedKey}</td>
                  <td className="py-3 pr-4">
                    <StatusBadge status={key.status} />
                  </td>
                  <td className="py-3 pr-4 text-slate-500">
                    {key.lastUsed ? new Date(key.lastUsed).toLocaleDateString() : "Never"}
                  </td>
                  <td className="py-3">
                    {key.status === "active" && (
                      <button className="text-sm font-medium text-red-600 hover:text-red-700">
                        Revoke
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

/* ── §3.6.2 Workflow Management ───────────────────── */

function WorkflowManagement() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadWorkflows = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Connect to real endpoint: GET /api/v1/developer/workflows
      setWorkflows([]);
    } catch {
      setError("Failed to load workflows.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadWorkflows();
  }, [loadWorkflows]);

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-slate-900">Workflows</h3>
        <button className="inline-flex items-center rounded-md border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50">
          Create Workflow
        </button>
      </div>

      {loading && <p className="mt-3 text-sm text-slate-500">Loading workflows…</p>}
      {error && (
        <div className="mt-3">
          <p className="text-sm text-red-600">{error}</p>
          <button onClick={loadWorkflows} className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-700">
            Retry
          </button>
        </div>
      )}

      {!loading && !error && workflows.length === 0 && (
        <div className="mt-4 rounded-md border border-dashed border-slate-200 p-4 text-center">
          <p className="text-sm text-slate-500">No workflows yet.</p>
          <p className="mt-1 text-xs text-slate-400">
            Create your first workflow to automate tasks.
          </p>
        </div>
      )}

      {!loading && workflows.length > 0 && (
        <ul className="mt-4 space-y-3">
          {workflows.map((wf) => (
            <li key={wf.id} className="flex items-center justify-between rounded-md border border-slate-100 p-3">
              <div>
                <p className="text-sm font-medium text-slate-900">{wf.name}</p>
                <p className="text-xs text-slate-500">
                  {wf.type === "approved" ? "Approved template" : "Custom"} ·{" "}
                  {wf.lastRun ? `Last run ${new Date(wf.lastRun).toLocaleDateString()}` : "Never run"}
                </p>
              </div>
              <StatusBadge status={wf.status} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

/* ── §3.6.3 Developer Quick Links ─────────────────── */

function DeveloperQuickLinks({ hasApiKeys }: { hasApiKeys: boolean }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-base font-semibold text-slate-900">Quick Links</h3>
      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <QuickLinkCard
          title="Documentation"
          description="API reference and guides"
          href="https://docs.capecontrol.io"
          external
        />
        {!hasApiKeys && (
          <QuickLinkCard
            title="Quick-Start Guide"
            description="Create your first API key"
            href="/app/developer/quickstart"
          />
        )}
        <QuickLinkCard
          title="Support & Community"
          description="Get help from the team"
          href="https://community.capecontrol.io"
          external
        />
      </div>
    </div>
  );
}

/* ── Shared sub-components ────────────────────────── */

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    active: "bg-green-50 text-green-700 border-green-200",
    revoked: "bg-red-50 text-red-700 border-red-200",
    expired: "bg-slate-100 text-slate-600 border-slate-200",
    paused: "bg-amber-50 text-amber-700 border-amber-200",
    draft: "bg-slate-50 text-slate-600 border-slate-200",
  };

  return (
    <span className={`inline-flex rounded-full border px-2 py-0.5 text-xs font-medium ${styles[status] ?? styles.draft}`}>
      {status}
    </span>
  );
}

function QuickLinkCard({
  title,
  description,
  href,
  external,
}: {
  title: string;
  description: string;
  href: string;
  external?: boolean;
}) {
  return (
    <a
      href={href}
      target={external ? "_blank" : undefined}
      rel={external ? "noopener noreferrer" : undefined}
      className="block rounded-md border border-slate-200 p-4 transition-colors hover:border-blue-200 hover:bg-blue-50"
    >
      <p className="text-sm font-medium text-slate-900">{title}</p>
      <p className="mt-1 text-xs text-slate-500">{description}</p>
    </a>
  );
}

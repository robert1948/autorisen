/**
 * DeveloperHubSection — developer-specific dashboard modules.
 *
 * Per dashboard-flow.mm §8 [PARTIAL]:
 *   Wired to real /api/dev/* endpoints.
 *   - §3.6.1 API Key Management (GET/POST/DELETE /api/dev/api-keys)
 *   - §3.6.2 Developer Usage Stats (GET /api/dev/usage)
 *   - §3.6.3 Developer Quick Links
 *
 * Loaded lazily via React.lazy() in the parent Dashboard component.
 * Only visible when hasPermission(user, "apikeys:manage").
 */

import { useCallback, useEffect, useState } from "react";
import type { UserProfile } from "../../types/user";
import {
  dashboardModulesApi,
  type ApiCredential,
  type ApiCredentialCreated,
  type DeveloperUsage,
} from "../../services/dashboardModulesApi";

interface DeveloperHubSectionProps {
  user: UserProfile;
}

/* ── Main component ───────────────────────────────── */

export default function DeveloperHubSection({ user }: DeveloperHubSectionProps) {
  return (
    <div className="col-span-full space-y-6">
      <h2 className="text-lg font-bold text-slate-900 dark:text-white">Developer Hub</h2>

      {/* §3.6.1 API Key Management */}
      <ApiKeyManagement maxKeys={5} emailVerified={user.emailVerified} />

      {/* §3.6.2 Usage Stats */}
      <UsageStats />

      {/* §3.6.3 Developer Quick Links */}
      <DeveloperQuickLinks />
    </div>
  );
}

/* ── §3.6.1 API Key Management ────────────────────── */

function ApiKeyManagement({
  maxKeys,
  emailVerified,
}: {
  maxKeys: number;
  emailVerified: boolean;
}) {
  const [keys, setKeys] = useState<ApiCredential[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [newLabel, setNewLabel] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [createdKey, setCreatedKey] = useState<ApiCredentialCreated | null>(null);
  const [revoking, setRevoking] = useState<string | null>(null);

  const loadKeys = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await dashboardModulesApi.getDevApiKeys();
      setKeys(data);
    } catch {
      setError("Failed to load API keys.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadKeys();
  }, [loadKeys]);

  const handleCreate = async () => {
    if (!newLabel.trim()) return;
    try {
      setCreating(true);
      const result = await dashboardModulesApi.createDevApiKey(newLabel.trim());
      setCreatedKey(result);
      setNewLabel("");
      setShowCreate(false);
      await loadKeys();
    } catch (err) {
      setError((err as Error).message || "Failed to create API key.");
    } finally {
      setCreating(false);
    }
  };

  const handleRevoke = async (id: string) => {
    try {
      setRevoking(id);
      await dashboardModulesApi.revokeDevApiKey(id);
      await loadKeys();
    } catch (err) {
      setError((err as Error).message || "Failed to revoke API key.");
    } finally {
      setRevoking(null);
    }
  };

  const activeCount = keys.filter((k) => k.is_active).length;
  const canCreate = activeCount < maxKeys && emailVerified;

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-slate-900 dark:text-white">API Keys</h3>
        <span className="text-xs text-slate-500 dark:text-slate-400">
          {activeCount} / {maxKeys} active
        </span>
      </div>

      {/* Show-once secret banner */}
      {createdKey && (
        <div className="mt-3 rounded-md border border-green-200 bg-green-50 p-4 dark:border-green-800 dark:bg-green-900/30">
          <p className="text-sm font-medium text-green-800 dark:text-green-300">
            API key created! Copy your secret now — it won't be shown again.
          </p>
          <div className="mt-2 space-y-1">
            <p className="text-xs text-green-700 dark:text-green-400">
              Client ID: <code className="rounded bg-green-100 px-1 font-mono dark:bg-green-800/50">{createdKey.client_id}</code>
            </p>
            <p className="text-xs text-green-700 dark:text-green-400">
              Client Secret: <code className="rounded bg-green-100 px-1 font-mono dark:bg-green-800/50">{createdKey.client_secret}</code>
            </p>
          </div>
          <button
            onClick={() => setCreatedKey(null)}
            className="mt-2 text-xs font-medium text-green-700 underline hover:text-green-800 dark:text-green-400 dark:hover:text-green-300"
          >
            Dismiss
          </button>
        </div>
      )}

      {loading && (
        <div className="mt-3 animate-pulse space-y-2">
          <div className="h-4 w-2/3 rounded bg-slate-200 dark:bg-slate-700" />
          <div className="h-4 w-1/2 rounded bg-slate-200 dark:bg-slate-700" />
        </div>
      )}

      {error && (
        <div className="mt-3">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          <button
            onClick={() => { setError(null); loadKeys(); }}
            className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
          >
            Retry
          </button>
        </div>
      )}

      {!loading && !error && keys.length === 0 && (
        <div className="mt-4 rounded-md border border-dashed border-slate-200 p-4 text-center dark:border-slate-600">
          <p className="text-sm text-slate-500 dark:text-slate-400">No API keys yet.</p>
          {!emailVerified && (
            <p className="mt-1 text-xs text-amber-600 dark:text-amber-400">
              Verify your email before creating API keys.
            </p>
          )}
          <button
            onClick={() => setShowCreate(true)}
            disabled={!canCreate}
            className="mt-3 inline-flex items-center rounded-md bg-blue-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50 dark:bg-blue-500 dark:hover:bg-blue-600"
          >
            Create API Key
          </button>
        </div>
      )}

      {!loading && keys.length > 0 && (
        <>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-sm" role="table">
              <thead>
                <tr className="border-b border-slate-100 text-xs uppercase text-slate-500 dark:border-slate-700 dark:text-slate-400">
                  <th className="py-2 pr-4" scope="col">Label</th>
                  <th className="py-2 pr-4" scope="col">Client ID</th>
                  <th className="py-2 pr-4" scope="col">Status</th>
                  <th className="py-2 pr-4" scope="col">Created</th>
                  <th className="py-2" scope="col">Actions</th>
                </tr>
              </thead>
              <tbody>
                {keys.map((key) => (
                  <tr key={key.id} className="border-b border-slate-50 dark:border-slate-700/50">
                    <td className="py-3 pr-4 font-medium text-slate-900 dark:text-white">{key.label || "—"}</td>
                    <td className="py-3 pr-4 font-mono text-xs text-slate-500 dark:text-slate-400">
                      {key.client_id.slice(0, 12)}…
                    </td>
                    <td className="py-3 pr-4">
                      <StatusBadge active={key.is_active} />
                    </td>
                    <td className="py-3 pr-4 text-slate-500 dark:text-slate-400">
                      {new Date(key.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3">
                      {key.is_active && (
                        <button
                          onClick={() => handleRevoke(key.id)}
                          disabled={revoking === key.id}
                          className="text-sm font-medium text-red-600 hover:text-red-700 disabled:opacity-50 dark:text-red-400 dark:hover:text-red-300"
                        >
                          {revoking === key.id ? "Revoking…" : "Revoke"}
                        </button>
                      )}
                      {!key.is_active && key.revoked_at && (
                        <span className="text-xs text-slate-400 dark:text-slate-500">
                          Revoked {new Date(key.revoked_at).toLocaleDateString()}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {canCreate && (
            <button
              onClick={() => setShowCreate(true)}
              className="mt-3 text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
            >
              + Create another key
            </button>
          )}
        </>
      )}

      {/* Create dialog */}
      {showCreate && (
        <div className="mt-4 rounded-md border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-900/20">
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
            Key label
          </label>
          <div className="mt-1 flex gap-2">
            <input
              type="text"
              value={newLabel}
              onChange={(e) => setNewLabel(e.target.value)}
              placeholder="e.g. Production App"
              maxLength={100}
              className="w-full rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-700 dark:text-white dark:placeholder-slate-500"
            />
            <button
              onClick={handleCreate}
              disabled={creating || !newLabel.trim()}
              className="rounded-md bg-blue-600 px-4 py-1.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50 dark:bg-blue-500 dark:hover:bg-blue-600"
            >
              {creating ? "Creating…" : "Create"}
            </button>
            <button
              onClick={() => { setShowCreate(false); setNewLabel(""); }}
              className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-700"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

/* ── §3.6.2 Usage Stats ──────────────────────────── */

function UsageStats() {
  const [usage, setUsage] = useState<DeveloperUsage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadUsage = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await dashboardModulesApi.getDevUsage();
      setUsage(data);
    } catch {
      setError("Failed to load usage stats.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUsage();
  }, [loadUsage]);

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <h3 className="text-base font-semibold text-slate-900 dark:text-white">Developer Usage</h3>

      {loading && (
        <div className="mt-3 animate-pulse">
          <div className="grid grid-cols-3 gap-4">
            <div className="h-16 rounded bg-slate-200 dark:bg-slate-700" />
            <div className="h-16 rounded bg-slate-200 dark:bg-slate-700" />
            <div className="h-16 rounded bg-slate-200 dark:bg-slate-700" />
          </div>
        </div>
      )}

      {error && (
        <div className="mt-3">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          <button
            onClick={loadUsage}
            className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
          >
            Retry
          </button>
        </div>
      )}

      {!loading && !error && usage && (
        <div className="mt-4 grid grid-cols-3 gap-4">
          <div className="rounded-md bg-slate-50 p-4 dark:bg-slate-700/50">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Total Keys
            </p>
            <p className="mt-1 text-lg font-semibold text-slate-900 dark:text-white">
              {usage.total_api_keys}
            </p>
          </div>
          <div className="rounded-md bg-emerald-50 p-4 dark:bg-emerald-900/20">
            <p className="text-xs font-medium uppercase tracking-wide text-emerald-600 dark:text-emerald-400">
              Active
            </p>
            <p className="mt-1 text-lg font-semibold text-emerald-700 dark:text-emerald-300">
              {usage.active_api_keys}
            </p>
          </div>
          <div className="rounded-md bg-red-50 p-4 dark:bg-red-900/20">
            <p className="text-xs font-medium uppercase tracking-wide text-red-600 dark:text-red-400">
              Revoked
            </p>
            <p className="mt-1 text-lg font-semibold text-red-700 dark:text-red-300">
              {usage.revoked_api_keys}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

/* ── §3.6.3 Developer Quick Links ─────────────────── */

function DeveloperQuickLinks() {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <h3 className="text-base font-semibold text-slate-900 dark:text-white">Quick Links</h3>
      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <QuickLinkCard
          title="API Documentation"
          description="Endpoints, schemas & guides"
          href="/app/developer"
        />
        <QuickLinkCard
          title="Marketplace"
          description="Browse & publish agents"
          href="/app/marketplace"
        />
        <QuickLinkCard
          title="Support"
          description="Get help from the team"
          href="mailto:support@capecontrol.io"
          external
        />
      </div>
    </div>
  );
}

/* ── Shared sub-components ────────────────────────── */

function StatusBadge({ active }: { active: boolean }) {
  return (
    <span
      className={`inline-flex rounded-full border px-2 py-0.5 text-xs font-medium ${
        active
          ? "border-green-200 bg-green-50 text-green-700 dark:border-green-800 dark:bg-green-900/30 dark:text-green-400"
          : "border-red-200 bg-red-50 text-red-700 dark:border-red-800 dark:bg-red-900/30 dark:text-red-400"
      }`}
    >
      {active ? "active" : "revoked"}
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
      className="block rounded-md border border-slate-200 p-4 transition-colors hover:border-blue-200 hover:bg-blue-50 dark:border-slate-600 dark:hover:border-blue-700 dark:hover:bg-blue-900/20"
    >
      <p className="text-sm font-medium text-slate-900 dark:text-white">{title}</p>
      <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{description}</p>
    </a>
  );
}

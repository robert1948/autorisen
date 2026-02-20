/**
 * AdminPanel — admin-only dashboard section.
 *
 * Per dashboard-flow.mm §8 [PARTIAL]:
 *   - Invite management: GET/POST/DELETE /api/admin/invites
 *   - System health: GET /api/health
 *   - User management: [PLANNED]
 *   - Feature flags: [PLANNED]
 *
 * Only visible when hasPermission(user, "admin:users").
 */

import { useCallback, useEffect, useState } from "react";
import type { UserProfile } from "../../types/user";
import {
  dashboardModulesApi,
  type AdminInvite,
} from "../../services/dashboardModulesApi";

interface AdminPanelProps {
  user: UserProfile;
}

export default function AdminPanel({ user }: AdminPanelProps) {
  return (
    <div className="col-span-full space-y-6">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-100 dark:bg-purple-900/40">
          <svg className="h-5 w-5 text-purple-600 dark:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">Admin Panel</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">System administration and user management</p>
        </div>
      </div>

      {/* System Health */}
      <SystemHealthCard />

      {/* Invite Management */}
      <InviteManagement />

      {/* Planned sections */}
      <div className="grid gap-4 sm:grid-cols-2">
        <PlannedCard title="User Management" description="View, suspend, and modify user roles" />
        <PlannedCard title="Feature Flags" description="Toggle features across the platform" />
      </div>
    </div>
  );
}

/* ── System Health ────────────────────────────────── */

function SystemHealthCard() {
  const [health, setHealth] = useState<{ status: string; database?: string } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = await dashboardModulesApi.getHealthStatus();
        setHealth(data);
      } catch {
        setHealth({ status: "error" });
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const isHealthy = health?.status === "ok" || health?.status === "healthy";

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <h3 className="text-base font-semibold text-slate-900 dark:text-white">System Health</h3>
      {loading ? (
        <div className="mt-3 h-10 w-1/3 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
      ) : (
        <div className="mt-4 grid gap-4 sm:grid-cols-3">
          <div className={`rounded-md p-4 ${isHealthy ? "bg-green-50 dark:bg-green-900/20" : "bg-red-50 dark:bg-red-900/20"}`}>
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">API</p>
            <p className={`mt-1 text-lg font-semibold ${isHealthy ? "text-green-700 dark:text-green-400" : "text-red-700 dark:text-red-400"}`}>
              {isHealthy ? "Operational" : "Degraded"}
            </p>
          </div>
          <div className={`rounded-md p-4 ${health?.database === "connected" ? "bg-green-50 dark:bg-green-900/20" : "bg-amber-50 dark:bg-amber-900/20"}`}>
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">Database</p>
            <p className={`mt-1 text-lg font-semibold ${health?.database === "connected" ? "text-green-700 dark:text-green-400" : "text-amber-700 dark:text-amber-400"}`}>
              {health?.database === "connected" ? "Connected" : health?.database || "Unknown"}
            </p>
          </div>
          <div className="rounded-md bg-slate-50 p-4 dark:bg-slate-700/50">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">Version</p>
            <p className="mt-1 text-lg font-semibold text-slate-900 dark:text-white">
              {(health as Record<string, string>)?.version || "—"}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

/* ── Invite Management ────────────────────────────── */

function InviteManagement() {
  const [invites, setInvites] = useState<AdminInvite[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [email, setEmail] = useState("");
  const [creating, setCreating] = useState(false);
  const [revoking, setRevoking] = useState<string | null>(null);

  const loadInvites = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await dashboardModulesApi.getAdminInvites();
      setInvites(data);
    } catch {
      setError("Failed to load invites.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadInvites();
  }, [loadInvites]);

  const handleCreate = async () => {
    if (!email.trim()) return;
    try {
      setCreating(true);
      await dashboardModulesApi.createAdminInvite(email.trim());
      setEmail("");
      setShowCreate(false);
      await loadInvites();
    } catch (err) {
      setError((err as Error).message || "Failed to create invite.");
    } finally {
      setCreating(false);
    }
  };

  const handleRevoke = async (id: string) => {
    try {
      setRevoking(id);
      await dashboardModulesApi.revokeAdminInvite(id);
      await loadInvites();
    } catch (err) {
      setError((err as Error).message || "Failed to revoke invite.");
    } finally {
      setRevoking(null);
    }
  };

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-slate-900 dark:text-white">Invite Management</h3>
        <button
          onClick={() => setShowCreate(true)}
          className="inline-flex items-center rounded-md bg-purple-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-purple-700 dark:bg-purple-500 dark:hover:bg-purple-600"
        >
          + Invite User
        </button>
      </div>

      {/* Create form */}
      {showCreate && (
        <div className="mt-4 rounded-md border border-purple-200 bg-purple-50 p-4 dark:border-purple-800 dark:bg-purple-900/20">
          <div className="flex flex-wrap gap-2">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="user@example.com"
              className="flex-1 rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-900 placeholder-slate-400 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500 dark:border-slate-600 dark:bg-slate-700 dark:text-white dark:placeholder-slate-500"
            />
            <button
              onClick={handleCreate}
              disabled={creating || !email.trim()}
              className="rounded-md bg-purple-600 px-4 py-1.5 text-sm font-semibold text-white hover:bg-purple-700 disabled:opacity-50 dark:bg-purple-500 dark:hover:bg-purple-600"
            >
              {creating ? "Sending…" : "Send"}
            </button>
            <button
              onClick={() => { setShowCreate(false); setEmail(""); }}
              className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-700"
            >
              Cancel
            </button>
          </div>
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
            onClick={() => { setError(null); loadInvites(); }}
            className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
          >
            Retry
          </button>
        </div>
      )}

      {!loading && !error && invites.length === 0 && (
        <div className="mt-4 rounded-md border border-dashed border-slate-200 p-4 text-center dark:border-slate-600">
          <p className="text-sm text-slate-500 dark:text-slate-400">No pending invites.</p>
        </div>
      )}

      {!loading && invites.length > 0 && (
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left text-sm" role="table">
            <thead>
              <tr className="border-b border-slate-100 text-xs uppercase text-slate-500 dark:border-slate-700 dark:text-slate-400">
                <th className="py-2 pr-4" scope="col">Email</th>
                <th className="py-2 pr-4" scope="col">Status</th>
                <th className="py-2 pr-4" scope="col">Created</th>
                <th className="py-2 pr-4" scope="col">Expires</th>
                <th className="py-2" scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              {invites.map((inv) => {
                const status = inv.revoked_at ? "revoked" : inv.used_at ? "accepted" : "pending";
                return (
                  <tr key={inv.id} className="border-b border-slate-50 dark:border-slate-700/50">
                    <td className="py-3 pr-4 font-medium text-slate-900 dark:text-white">{inv.target_email}</td>
                    <td className="py-3 pr-4">
                      <span className={`inline-flex rounded-full border px-2 py-0.5 text-xs font-medium ${
                        status === "pending"
                          ? "border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-800 dark:bg-amber-900/30 dark:text-amber-400"
                          : status === "accepted"
                          ? "border-green-200 bg-green-50 text-green-700 dark:border-green-800 dark:bg-green-900/30 dark:text-green-400"
                          : "border-red-200 bg-red-50 text-red-700 dark:border-red-800 dark:bg-red-900/30 dark:text-red-400"
                      }`}>
                        {status}
                      </span>
                    </td>
                    <td className="py-3 pr-4 text-slate-500 dark:text-slate-400">
                      {new Date(inv.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3 pr-4 text-slate-500 dark:text-slate-400">
                      {new Date(inv.expires_at).toLocaleDateString()}
                    </td>
                    <td className="py-3">
                      {status === "pending" && (
                        <button
                          onClick={() => handleRevoke(inv.id)}
                          disabled={revoking === inv.id}
                          className="text-sm font-medium text-red-600 hover:text-red-700 disabled:opacity-50 dark:text-red-400 dark:hover:text-red-300"
                        >
                          {revoking === inv.id ? "Revoking…" : "Revoke"}
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

/* ── Planned section placeholder ──────────────────── */

function PlannedCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="rounded-lg border border-dashed border-slate-200 bg-slate-50 p-6 dark:border-slate-600 dark:bg-slate-800/50">
      <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300">{title}</h4>
      <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{description}</p>
      <span className="mt-3 inline-block rounded-full border border-slate-200 bg-white px-2 py-0.5 text-xs font-medium text-slate-500 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-400">
        PLANNED
      </span>
    </div>
  );
}

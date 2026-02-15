/**
 * WelcomeHeader — top-of-dashboard greeting and quick stats.
 *
 * Per spec §3.1:
 *   - Always visible regardless of role
 *   - Greeting with displayName fallback chain
 *   - Role-aware quick stat cards
 *   - System status badge
 *   - Empty state CTA for new users
 */

import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { UserProfile } from "../../types/user";
import { ROLE_LABELS } from "../../constants/roles";
import { hasPermission } from "../../utils/permissions";

interface WelcomeHeaderProps {
  user: UserProfile;
}

type SystemStatus = "operational" | "partial" | "disruption";

const STATUS_BADGES: Record<SystemStatus, { label: string; icon: string; className: string }> = {
  operational: { label: "All systems operational", icon: "🟢", className: "text-green-700 bg-green-50 border-green-200" },
  partial: { label: "Partial disruption", icon: "🟡", className: "text-yellow-700 bg-yellow-50 border-yellow-200" },
  disruption: { label: "Service disruption", icon: "🔴", className: "text-red-700 bg-red-50 border-red-200" },
};

function mapStatus(raw: string): SystemStatus {
  if (raw === "ok" || raw === "operational") return "operational";
  if (raw === "partial" || raw === "degraded") return "partial";
  return "disruption";
}

export function WelcomeHeader({ user }: WelcomeHeaderProps) {
  const navigate = useNavigate();
  const [systemStatus, setSystemStatus] = useState<SystemStatus>("operational");

  // TODO: fetch from /api/health or status endpoint
  useEffect(() => {
    // Placeholder — will connect to real status endpoint
    setSystemStatus("operational");
  }, []);

  const greeting = user.displayName || user.name || user.email.split("@")[0];
  const roleLabel = ROLE_LABELS[user.role] ?? "User";
  const badge = STATUS_BADGES[systemStatus];
  const isNewUser = user.account.balance === 0 && !user.developerProfile;

  return (
    <div className="col-span-full">
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        {/* Greeting row */}
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-slate-900 sm:text-2xl">
              Welcome back, {greeting}
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              {roleLabel} · Last login{" "}
              {new Date(user.lastLogin).toLocaleDateString(undefined, {
                year: "numeric",
                month: "short",
                day: "numeric",
              })}
            </p>
          </div>

          {/* System status badge */}
          <span
            className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium ${badge.className}`}
            role="status"
            aria-label={`System status: ${badge.label}`}
          >
            <span aria-hidden="true">{badge.icon}</span>
            {badge.label}
          </span>
        </div>

        {/* Quick stat cards */}
        <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {/* Active projects — all roles */}
          <StatCard label="Active projects" value="0" />

          {/* Account status — all roles */}
          <StatCard
            label="Account status"
            value={user.status === "active" ? "Active" : user.status}
            accent={user.status === "active" ? "green" : "amber"}
          />

          {/* Balance — all roles where applicable */}
          {hasPermission(user, "account:billing") && (
            <StatCard
              label="Balance"
              value={`${user.account.currency} ${user.account.balance.toFixed(2)}`}
            />
          )}

          {/* API calls — developer + admin */}
          {hasPermission(user, "apikeys:manage") && user.developerProfile && (
            <StatCard
              label="API calls this period"
              value={`${user.developerProfile.usageQuota.apiCallsUsed.toLocaleString()} / ${user.developerProfile.usageQuota.apiCallsLimit.toLocaleString()}`}
            />
          )}
        </div>

        {/* Empty state for new users */}
        {isNewUser && (
          <div className="mt-6 rounded-md border border-blue-100 bg-blue-50 p-4 text-center">
            <p className="text-sm font-medium text-blue-800">
              Welcome to CapeControl! Let's get started.
            </p>
            <button
              onClick={() => navigate("/app/projects/new")}
              className="mt-3 inline-flex items-center rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Create your first project
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

/* ── Stat card sub-component ─────────────────────────────── */

interface StatCardProps {
  label: string;
  value: string | number;
  accent?: "green" | "amber" | "blue" | "slate";
}

function StatCard({ label, value, accent = "slate" }: StatCardProps) {
  const accentStyles: Record<string, string> = {
    green: "text-green-700",
    amber: "text-amber-700",
    blue: "text-blue-700",
    slate: "text-slate-900",
  };

  return (
    <div className="rounded-md bg-slate-50 p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className={`mt-1 text-lg font-semibold ${accentStyles[accent]}`}>{value}</p>
    </div>
  );
}

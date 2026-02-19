/**
 * WelcomeHeader — top-of-dashboard greeting and quick stats.
 *
 * Per spec §3.1:
 *   - Always visible regardless of role
 *   - Greeting with displayName fallback chain
 *   - Role-aware quick stat cards with gradient accents
 *   - System status badge
 *   - Empty state CTA for new users
 *   - Responsive: stacked on mobile, 4-col cards on desktop
 */

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { UserProfile } from "../../types/user";
import { ROLE_LABELS } from "../../constants/roles";
import { hasPermission } from "../../utils/permissions";

interface WelcomeHeaderProps {
  user: UserProfile;
}

type SystemStatus = "operational" | "partial" | "disruption";

const STATUS_BADGES: Record<SystemStatus, { label: string; dot: string; className: string }> = {
  operational: { label: "All systems operational", dot: "bg-green-500", className: "text-green-700 bg-green-50 border-green-200 dark:text-green-400 dark:bg-green-900/20 dark:border-green-800" },
  partial: { label: "Partial disruption", dot: "bg-yellow-500", className: "text-yellow-700 bg-yellow-50 border-yellow-200 dark:text-yellow-400 dark:bg-yellow-900/20 dark:border-yellow-800" },
  disruption: { label: "Service disruption", dot: "bg-red-500", className: "text-red-700 bg-red-50 border-red-200 dark:text-red-400 dark:bg-red-900/20 dark:border-red-800" },
};

function mapStatus(raw: string): SystemStatus {
  if (raw === "ok" || raw === "operational" || raw === "healthy") return "operational";
  if (raw === "partial" || raw === "degraded") return "partial";
  return "disruption";
}

export function WelcomeHeader({ user }: WelcomeHeaderProps) {
  const navigate = useNavigate();
  const [systemStatus, setSystemStatus] = useState<SystemStatus>("operational");
  const [projectCount, setProjectCount] = useState<number | null>(null);

  // Fetch system status from /api/health
  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/health", { signal: controller.signal })
      .then((res) => {
        if (res.ok) return res.json();
        throw new Error(`HTTP ${res.status}`);
      })
      .then((data: { status?: string }) => {
        setSystemStatus(mapStatus(data.status ?? "operational"));
      })
      .catch((err) => {
        if (err instanceof DOMException && err.name === "AbortError") return;
        setSystemStatus("partial");
      });
    return () => controller.abort();
  }, []);

  // Fetch active project count from /api/projects/status
  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/projects/status", {
      signal: controller.signal,
      credentials: "include",
      headers: { Accept: "application/json" },
    })
      .then((res) => {
        if (res.ok) return res.json();
        throw new Error(`HTTP ${res.status}`);
      })
      .then((data: { total?: number }) => {
        setProjectCount(data.total ?? 0);
      })
      .catch((err) => {
        if (err instanceof DOMException && err.name === "AbortError") return;
        setProjectCount(0);
      });
    return () => controller.abort();
  }, []);

  const greeting = user.displayName || user.name || user.email.split("@")[0];
  const roleLabel = ROLE_LABELS[user.role] ?? "User";
  const badge = STATUS_BADGES[systemStatus];
  const isNewUser = user.account.balance === 0 && !user.developerProfile;

  // Time-based greeting
  const hour = new Date().getHours();
  const timeGreeting = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";

  return (
    <div className="col-span-full">
      {/* Hero greeting card with subtle gradient */}
      <div className="relative overflow-hidden rounded-xl border border-slate-200 bg-gradient-to-br from-white via-white to-blue-50 p-5 shadow-sm sm:p-6 dark:border-slate-700 dark:from-slate-800 dark:via-slate-800 dark:to-blue-950/30">
        {/* Decorative background circle */}
        <div className="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full bg-blue-500/5 dark:bg-blue-400/5" />
        <div className="pointer-events-none absolute -right-8 top-8 h-32 w-32 rounded-full bg-indigo-500/5 dark:bg-indigo-400/5" />

        {/* Greeting row */}
        <div className="relative flex flex-wrap items-start justify-between gap-3">
          <div className="flex items-center gap-4">
            {/* Avatar */}
            <div className="hidden h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 text-lg font-bold text-white shadow-md sm:flex">
              {(greeting[0] ?? "U").toUpperCase()}
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900 sm:text-xl dark:text-white">
                {timeGreeting}, {greeting}
              </h2>
              <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
                {roleLabel} · Last login{" "}
                {new Date(user.lastLogin).toLocaleDateString(undefined, {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                })}
              </p>
            </div>
          </div>

          {/* System status badge */}
          <span
            className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium ${badge.className}`}
            role="status"
            aria-label={`System status: ${badge.label}`}
          >
            <span className={`h-2 w-2 rounded-full ${badge.dot}`} aria-hidden="true" />
            <span className="hidden sm:inline">{badge.label}</span>
            <span className="sm:hidden">{systemStatus === "operational" ? "OK" : "!"}</span>
          </span>
        </div>

        {/* Stat cards — gradient accented */}
        <div className="relative mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          <GradientStatCard
            label="Active projects"
            value={projectCount !== null ? String(projectCount) : "…"}
            gradient="from-blue-500 to-blue-600"
            icon={
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
            }
          />

          <GradientStatCard
            label="Account status"
            value={user.status === "active" ? "Active" : user.status}
            gradient={user.status === "active" ? "from-emerald-500 to-emerald-600" : "from-amber-500 to-amber-600"}
            icon={
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            }
          />

          {hasPermission(user, "account:billing") && (
            <GradientStatCard
              label="Balance"
              value={`${user.account.currency} ${user.account.balance.toFixed(2)}`}
              gradient="from-violet-500 to-violet-600"
              icon={
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              }
            />
          )}

          {hasPermission(user, "apikeys:manage") && user.developerProfile && (
            <GradientStatCard
              label="API calls"
              value={`${user.developerProfile.usageQuota.apiCallsUsed.toLocaleString()} / ${user.developerProfile.usageQuota.apiCallsLimit.toLocaleString()}`}
              gradient="from-amber-500 to-orange-500"
              icon={
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              }
            />
          )}
        </div>

        {/* Empty state for new users */}
        {isNewUser && (
          <div className="relative mt-5 rounded-lg border border-blue-200 bg-blue-50/50 p-4 text-center dark:border-blue-800 dark:bg-blue-900/20">
            <p className="text-sm font-medium text-blue-800 dark:text-blue-300">
              Welcome to CapeControl! Let's get you started.
            </p>
            <button
              onClick={() => navigate("/app/projects/new")}
              className="mt-3 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 active:scale-[0.98]"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Create your first project
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

/* ── Gradient stat card sub-component ──────────────────── */

interface GradientStatCardProps {
  label: string;
  value: string | number;
  gradient: string;
  icon: React.ReactNode;
}

function GradientStatCard({ label, value, gradient, icon }: GradientStatCardProps) {
  return (
    <div className="group flex items-center gap-3 rounded-lg border border-slate-100 bg-white/80 p-3 shadow-sm backdrop-blur-sm transition-all hover:shadow-md sm:p-4 dark:border-slate-700 dark:bg-slate-800/80">
      <div className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br ${gradient} text-white shadow-sm`}>
        {icon}
      </div>
      <div className="min-w-0">
        <p className="truncate text-[11px] font-medium uppercase tracking-wider text-slate-400 dark:text-slate-500">{label}</p>
        <p className="mt-0.5 truncate text-base font-bold text-slate-900 sm:text-lg dark:text-white">{value}</p>
      </div>
    </div>
  );
}

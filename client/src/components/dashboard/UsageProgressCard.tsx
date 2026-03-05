/**
 * UsageProgressCard — usage meters with progress bars.
 *
 * Shows API calls, project count, and storage usage
 * with circular/linear progress indicators inspired by
 * the reference dashboard designs.
 */

import type { UserProfile } from "../../types/user";
import { hasPermission } from "../../utils/permissions";
import { useUsageSummary } from "../../hooks/useUsageSummary";

interface UsageProgressCardProps {
  user: UserProfile;
}

interface ProgressItem {
  label: string;
  current: number;
  max: number;
  color: string;
  bgColor: string;
}

function ProgressBar({ item }: { item: ProgressItem }) {
  const pct = item.max > 0 ? Math.min((item.current / item.max) * 100, 100) : 0;
  const isWarning = pct >= 80;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-slate-700 dark:text-slate-300">{item.label}</span>
        <span className={`text-xs font-semibold ${isWarning ? "text-amber-600" : "text-slate-500"}`}>
          {item.current.toLocaleString()} / {item.max.toLocaleString()}
        </span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
        <div
          className={`h-full rounded-full transition-all duration-500 ${isWarning ? "bg-amber-500" : item.color}`}
          style={{ width: `${pct}%` }}
          role="progressbar"
          aria-valuenow={item.current}
          aria-valuemin={0}
          aria-valuemax={item.max}
          aria-label={`${item.label}: ${item.current} of ${item.max}`}
        />
      </div>
    </div>
  );
}

function CircularProgress({ value, max, size = 80, strokeWidth = 6, color = "#3b82f6" }: {
  value: number;
  max: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
}) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const pct = max > 0 ? Math.min(value / max, 1) : 0;
  const dashOffset = circumference * (1 - pct);

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-slate-100 dark:text-slate-700"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          strokeLinecap="round"
          className="transition-all duration-700"
        />
      </svg>
      <span className="absolute text-lg font-bold text-slate-900 dark:text-slate-100">
        {Math.round(pct * 100)}%
      </span>
    </div>
  );
}

export function UsageProgressCard({ user }: UsageProgressCardProps) {
  const isDeveloper = hasPermission(user, "apikeys:manage");
  const { data: usage, isLoading } = useUsageSummary();

  const apiUsed = usage.apiCallsUsed;
  const apiLimit = usage.apiCallsLimit;

  // Primary gauge metric: executions used / limit
  const execPct = apiLimit > 0 ? apiUsed / apiLimit : 0;
  const showUpgrade = execPct >= 0.8 || (usage.maxAgents > 0 && usage.agentCount / usage.maxAgents >= 0.8);

  const items: ProgressItem[] = [];

  // Always show Executions (the core billable metric)
  items.push({
    label: "Executions",
    current: apiUsed,
    max: apiLimit,
    color: "bg-blue-500",
    bgColor: "bg-blue-100",
  });

  // Always show Agents
  items.push({
    label: "Agents",
    current: usage.agentCount,
    max: usage.maxAgents,
    color: "bg-indigo-500",
    bgColor: "bg-indigo-100",
  });

  items.push({
    label: "Documents",
    current: usage.documentsCount,
    max: 100, // soft display cap
    color: "bg-emerald-500",
    bgColor: "bg-emerald-100",
  });

  items.push({
    label: "RAG Queries",
    current: usage.ragQueries,
    max: apiLimit, // same quota pool
    color: "bg-violet-500",
    bgColor: "bg-violet-100",
  });

  if (isDeveloper) {
    items.push({
      label: "Storage Used",
      current: usage.storageUsedMb,
      max: usage.storageLimitMb,
      color: "bg-cyan-500",
      bgColor: "bg-cyan-100",
    });
  }

  return (
    <section
      className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800"
      aria-labelledby="usage-heading"
    >
      <h3 id="usage-heading" className="mb-4 text-base font-semibold text-slate-900 dark:text-white">
        Usage Overview
      </h3>

      <div className="flex flex-col gap-6 sm:flex-row sm:items-center">
        {/* Circular gauge */}
        <div className="flex flex-col items-center gap-2">
          <CircularProgress
            value={apiUsed}
            max={apiLimit}
            size={90}
            strokeWidth={7}
            color={execPct > 0.8 ? "#f59e0b" : "#3b82f6"}
          />
          <span className="text-xs font-medium text-slate-500">
            {usage.planId === "free" ? "Free" : usage.planId === "pro" ? "Pro" : "Enterprise"} Plan
          </span>
        </div>

        {/* Linear progress bars */}
        <div className="flex-1 space-y-4">
          {items.map((item) => (
            <ProgressBar key={item.label} item={item} />
          ))}
        </div>
      </div>

      {showUpgrade && usage.planId !== "enterprise" && (
        <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 dark:border-amber-700 dark:bg-amber-900/30">
          <p className="text-sm text-amber-800 dark:text-amber-200">
            You&apos;re approaching your plan limits.{" "}
            <a href="/app/pricing" className="font-semibold underline hover:text-amber-900 dark:hover:text-amber-100">
              Upgrade your plan
            </a>{" "}
            for more capacity.
          </p>
        </div>
      )}
    </section>
  );
}

/**
 * UsageProgressCard — usage meters with progress bars.
 *
 * Shows API calls, project count, and storage usage
 * with circular/linear progress indicators inspired by
 * the reference dashboard designs.
 */

import type { UserProfile } from "../../types/user";
import { hasPermission } from "../../utils/permissions";

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

  const apiUsed = user.developerProfile?.usageQuota.apiCallsUsed ?? 0;
  const apiLimit = user.developerProfile?.usageQuota.apiCallsLimit ?? 1000;

  const items: ProgressItem[] = [];

  if (isDeveloper && user.developerProfile) {
    items.push({
      label: "API Calls",
      current: apiUsed,
      max: apiLimit,
      color: "bg-blue-500",
      bgColor: "bg-blue-100",
    });
  }

  // Storage (placeholder — to be wired to real endpoint)
  items.push({
    label: "Storage Used",
    current: 0,
    max: 1024,
    color: "bg-emerald-500",
    bgColor: "bg-emerald-100",
  });

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
            color={apiUsed / apiLimit > 0.8 ? "#f59e0b" : "#3b82f6"}
          />
          <span className="text-xs font-medium text-slate-500">API Quota</span>
        </div>

        {/* Linear progress bars */}
        <div className="flex-1 space-y-4">
          {items.map((item) => (
            <ProgressBar key={item.label} item={item} />
          ))}
        </div>
      </div>
    </section>
  );
}

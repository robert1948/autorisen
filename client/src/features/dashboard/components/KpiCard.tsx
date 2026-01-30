// Figma: DashboardPage/KpiCard

import { StatusPill, type StatusTone } from "./StatusPill";

export type KpiCardProps = {
  label: string;
  value: string;
  delta?: string;
  tone?: StatusTone;
};

export function KpiCard({ label, value, delta, tone }: KpiCardProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm text-slate-600">{label}</p>
          <p className="mt-1 text-xl font-semibold text-slate-900">{value}</p>
        </div>
        {tone ? <StatusPill label={tone} tone={tone} /> : null}
      </div>
      {delta ? <p className="mt-2 text-xs text-slate-500">{delta}</p> : null}
    </div>
  );
}

// Figma: DashboardPage/ActivityItem

import { StatusPill, type StatusTone } from "./StatusPill";

export type ActivityItemProps = {
  message: string;
  timestamp: string;
  tone?: StatusTone;
};

export function ActivityItem({ message, timestamp, tone }: ActivityItemProps) {
  return (
    <div className="flex items-start justify-between gap-3 py-2">
      <div className="min-w-0">
        <p className="text-sm text-slate-800">{message}</p>
        <p className="mt-1 text-xs text-slate-500">{timestamp}</p>
      </div>
      {tone ? <StatusPill label={tone} tone={tone} /> : null}
    </div>
  );
}

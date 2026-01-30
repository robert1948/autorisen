// Figma: DashboardPage/TrendChart

import type { DashboardTrendPointDTO } from "../types";

export type TrendChartProps = {
  points?: DashboardTrendPointDTO[];
};

export function TrendChart({ points }: TrendChartProps) {
  const safePoints = points ?? [];

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-3">
      <p className="text-xs font-medium text-slate-600">Trend (stub)</p>
      {safePoints.length === 0 ? (
        <p className="mt-2 text-sm text-slate-500">No data.</p>
      ) : (
        <div className="mt-2 flex flex-wrap gap-2">
          {safePoints.map((point) => (
            <span
              key={`${point.x}-${point.y}`}
              className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-700"
            >
              {point.x}: {point.y}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

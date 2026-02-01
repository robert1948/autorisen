import React, { useEffect, useMemo, useState } from "react";

/**
 * Dashboard v1 (thin vertical slice)
 * - UI: KPI cards + trend + recent activity + audit preview
 * - Data source: GET /api/dashboard/summary (same-origin)
 */

type KPI = {
  id: string;
  label: string;
  value: number;
  unit?: string;
  deltaPct?: number;
};

type TrendPoint = {
  date: string;
  value: number;
};

type ActivityItem = {
  id: string;
  ts: string;
  type: string;
  summary: string;
  status: "ok" | "warn" | "error";
};

type DashboardSummary = {
  kpis: KPI[];
  trend: TrendPoint[];
  recent: ActivityItem[];
};

const DEFAULT_API_URL = ""; // same-origin
const ENDPOINT = "/api/dashboard/summary";

const normalizeOrigin = (u: string) => u.replace(/\/+$/, "");
const isAbsoluteHttpUrl = (u: string) => /^https?:\/\//i.test(u);

function shouldFetchSummaryInDev(apiUrlRaw: string | undefined): boolean {
  if (!import.meta.env.DEV) return true;

  const apiUrl = (apiUrlRaw ?? "").trim();
  if (!isAbsoluteHttpUrl(apiUrl)) return false;

  try {
    const apiOrigin = normalizeOrigin(new URL(apiUrl).origin);
    const curOrigin = normalizeOrigin(window.location.origin);
    return apiOrigin !== curOrigin;
  } catch {
    return false;
  }
}

const mockData: DashboardSummary = {
  kpis: [
    { id: "requests_7d", label: "Requests (7d)", value: 1240, deltaPct: 10.2 },
    { id: "evidence_7d", label: "Evidence Packs (7d)", value: 86, deltaPct: 4.4 },
    { id: "blocks_7d", label: "Policy Blocks (7d)", value: 7, deltaPct: -12.5 },
    { id: "latency_ms", label: "Avg Latency", value: 420, unit: "ms", deltaPct: -3.1 },
  ],
  trend: [
    { date: "2026-01-20", value: 120 },
    { date: "2026-01-21", value: 180 },
    { date: "2026-01-22", value: 140 },
    { date: "2026-01-23", value: 220 },
    { date: "2026-01-24", value: 200 },
    { date: "2026-01-25", value: 260 },
    { date: "2026-01-26", value: 240 },
  ],
  recent: [
    {
      id: "evt_1",
      ts: "2026-01-26T10:32:00Z",
      type: "agent.run",
      summary: "CapeAI created an evidence-grade output for WO validation",
      status: "ok",
    },
    {
      id: "evt_2",
      ts: "2026-01-26T09:58:00Z",
      type: "auth.login",
      summary: "Developer login succeeded",
      status: "ok",
    },
    {
      id: "evt_3",
      ts: "2026-01-26T09:42:00Z",
      type: "policy.block",
      summary: "Content moderation blocked a request (policy)",
      status: "warn",
    },
  ],
};

function formatNumber(n: number): string {
  try {
    return new Intl.NumberFormat().format(n);
  } catch {
    return String(n);
  }
}

function formatDelta(deltaPct?: number): { text: string; tone: "up" | "down" | "flat" } {
  if (deltaPct === undefined || Number.isNaN(deltaPct)) return { text: "—", tone: "flat" };
  if (Math.abs(deltaPct) < 0.05) return { text: "0.0%", tone: "flat" };
  const sign = deltaPct > 0 ? "+" : "";
  return { text: `${sign}${deltaPct.toFixed(1)}%`, tone: deltaPct > 0 ? "up" : "down" };
}

function formatTs(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString();
}

function classNames(...xs: Array<string | false | undefined | null>) {
  return xs.filter(Boolean).join(" ");
}

function Sparkline({ points }: { points: TrendPoint[] }) {
  const { w, h, pad } = { w: 520, h: 160, pad: 16 };

  const values = points.map((p) => p.value);
  const min = Math.min(...values, 0);
  const max = Math.max(...values, 1);

  const scaleX = (i: number) => {
    if (points.length <= 1) return pad;
    const innerW = w - pad * 2;
    return pad + (innerW * i) / (points.length - 1);
  };

  const scaleY = (v: number) => {
    const innerH = h - pad * 2;
    const t = (v - min) / (max - min || 1);
    return pad + (1 - t) * innerH;
  };

  const d = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${scaleX(i).toFixed(2)} ${scaleY(p.value).toFixed(2)}`)
    .join(" ");

  const last = points[points.length - 1];

  return (
    <div className="w-full">
      <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-auto">
        <line x1={pad} y1={h - pad} x2={w - pad} y2={h - pad} stroke="rgba(255,255,255,0.12)" />
        <path d={d} fill="none" stroke="rgba(120,200,255,0.9)" strokeWidth="2.5" />
        {last ? (
          <circle
            cx={scaleX(points.length - 1)}
            cy={scaleY(last.value)}
            r="4"
            fill="rgba(120,200,255,0.95)"
          />
        ) : null}
      </svg>

      <div className="mt-2 flex items-center justify-between text-xs text-white/60">
        <span>{points[0]?.date ?? ""}</span>
        <span>{points[points.length - 1]?.date ?? ""}</span>
      </div>
    </div>
  );
}

function Panel({
  title,
  subtitle,
  children,
  right,
}: {
  title: string;
  subtitle?: string;
  right?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur p-5 shadow-sm">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-white/90">{title}</h2>
          {subtitle ? <p className="mt-1 text-sm text-white/60">{subtitle}</p> : null}
        </div>
        {right ? <div className="shrink-0">{right}</div> : null}
      </div>
      {children}
    </div>
  );
}

function KpiCard({ kpi }: { kpi: KPI }) {
  const delta = formatDelta(kpi.deltaPct);
  const deltaClass =
    delta.tone === "up" ? "text-emerald-300" : delta.tone === "down" ? "text-rose-300" : "text-white/60";

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur p-4 shadow-sm">
      <div className="text-xs text-white/60">{kpi.label}</div>
      <div className="mt-2 flex items-baseline gap-2">
        <div className="text-2xl font-semibold text-white/90">{formatNumber(kpi.value)}</div>
        {kpi.unit ? <div className="text-sm text-white/60">{kpi.unit}</div> : null}
      </div>
      <div className={classNames("mt-2 text-xs", deltaClass)}>{delta.text}</div>
    </div>
  );
}

function StatusPill({ status }: { status: ActivityItem["status"] }) {
  const cls =
    status === "ok"
      ? "bg-emerald-500/15 text-emerald-200 border-emerald-500/20"
      : status === "warn"
      ? "bg-amber-500/15 text-amber-200 border-amber-500/20"
      : "bg-rose-500/15 text-rose-200 border-rose-500/20";

  return (
    <span className={classNames("inline-flex items-center rounded-full px-2 py-0.5 text-xs border", cls)}>
      {status}
    </span>
  );
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const apiBaseRaw = import.meta.env.VITE_API_URL;
  const apiBase = (apiBaseRaw ?? DEFAULT_API_URL).trim();

  useEffect(() => {
    let alive = true;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        if (import.meta.env.DEV && !shouldFetchSummaryInDev(apiBaseRaw)) {
          if (alive) {
            setError("Backend not configured; using fallback data");
            setData(mockData);
          }
          return;
        }

        const url = import.meta.env.DEV
          ? new URL(ENDPOINT, apiBase).toString()
          : `${apiBase}${ENDPOINT}`;

        const res = await fetch(url, {
          method: "GET",
          headers: { Accept: "application/json" },
          credentials: "include",
        });

        if (!res.ok) {
          throw new Error(`HTTP ${res.status} ${res.statusText}`);
        }

        const json = (await res.json()) as DashboardSummary;
        if (!json || !Array.isArray(json.kpis) || !Array.isArray(json.trend) || !Array.isArray(json.recent)) {
          throw new Error("Invalid dashboard payload shape");
        }

        if (alive) setData(json);
      } catch (e: any) {
        if (alive) {
          setError(e?.message ?? "Failed to load dashboard");
          setData(mockData);
        }
      } finally {
        if (alive) setLoading(false);
      }
    }

    load();
    return () => {
      alive = false;
    };
  }, [apiBase]);

  const kpis = data?.kpis ?? [];
  const trend = data?.trend ?? [];
  const recent = data?.recent ?? [];

  const hasReal = useMemo(() => !error, [error]);

  return (
    <div className="min-h-[calc(100vh-0px)] px-4 py-6 md:px-8">
      <div className="mx-auto w-full max-w-6xl">
        <div className="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-white/90">Dashboard</h1>
            <p className="mt-1 text-sm text-white/60">
              Evidence-first overview of activity, outcomes, and operational health.
            </p>
          </div>

          <div className="flex w-full flex-wrap items-center gap-2 md:w-auto md:justify-end">
            <span
              className={classNames(
                "inline-flex items-center rounded-full border px-3 py-1 text-xs",
                hasReal
                  ? "border-emerald-500/25 bg-emerald-500/10 text-emerald-200"
                  : "border-amber-500/25 bg-amber-500/10 text-amber-200"
              )}
              title={hasReal ? "Live data" : "Fallback (mock) data"}
            >
              {hasReal ? "Live" : "Mock"}
            </span>

            <button
              onClick={() => window.location.reload()}
              className="rounded-xl border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white/80 hover:bg-white/10"
            >
              Refresh
            </button>
          </div>
        </div>

        {loading ? (
          <div className="grid gap-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="h-24 rounded-2xl border border-white/10 bg-white/5 animate-pulse" />
              ))}
            </div>
            <div className="h-56 rounded-2xl border border-white/10 bg-white/5 animate-pulse" />
            <div className="h-56 rounded-2xl border border-white/10 bg-white/5 animate-pulse" />
          </div>
        ) : (
          <>
            {error ? (
              <div className="mb-4 rounded-2xl border border-amber-500/20 bg-amber-500/10 p-4 text-sm text-amber-200">
                <div className="font-medium">Using fallback data</div>
                <div className="mt-2 text-xs text-amber-200/70">
                  Live dashboard data is temporarily unavailable. Details: {error}
                </div>
              </div>
            ) : null}

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {kpis.map((k) => (
                <KpiCard key={k.id} kpi={k} />
              ))}
            </div>

            <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <Panel title="Trend" subtitle="Simple sparkline (v1)">
                  {trend.length ? (
                    <Sparkline points={trend} />
                  ) : (
                    <div className="rounded-xl border border-white/10 bg-white/5 p-4 text-sm text-white/60">
                      No trend data.
                    </div>
                  )}
                </Panel>
              </div>

              <div>
                <Panel title="Recent activity" subtitle="Last events (v1)">
                  {recent.length ? (
                    <div className="space-y-3">
                      {recent.slice(0, 6).map((a) => (
                        <div key={a.id} className="flex items-start justify-between gap-3">
                          <div className="min-w-0">
                            <div className="flex items-center gap-2">
                              <div className="text-sm font-medium text-white/90 truncate">{a.type}</div>
                              <StatusPill status={a.status} />
                            </div>
                            <div className="mt-1 text-sm text-white/70">{a.summary}</div>
                            <div className="mt-1 text-xs text-white/50">{formatTs(a.ts)}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="rounded-xl border border-white/10 bg-white/5 p-4 text-sm text-white/60">
                      No recent activity.
                    </div>
                  )}
                </Panel>
              </div>
            </div>

            <div className="mt-4">
              <Panel title="Audit preview" subtitle="Minimal table view of recent events (v1)">
                {recent.length ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="text-xs text-white/60">
                        <tr className="border-b border-white/10">
                          <th className="py-2 pr-4">Time</th>
                          <th className="py-2 pr-4">Type</th>
                          <th className="py-2 pr-4">Summary</th>
                          <th className="py-2 pr-2">Status</th>
                        </tr>
                      </thead>
                      <tbody className="text-white/80">
                        {recent.slice(0, 8).map((a) => (
                          <tr key={a.id} className="border-b border-white/10 last:border-0">
                            <td className="py-2 pr-4 whitespace-nowrap text-white/60">{formatTs(a.ts)}</td>
                            <td className="py-2 pr-4 whitespace-nowrap">{a.type}</td>
                            <td className="py-2 pr-4">{a.summary}</td>
                            <td className="py-2 pr-2">
                              <StatusPill status={a.status} />
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="rounded-xl border border-white/10 bg-white/5 p-4 text-sm text-white/60">
                    No audit events available.
                  </div>
                )}
              </Panel>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

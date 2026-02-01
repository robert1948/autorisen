/**
 * ARCHIVED: Legacy dashboard scaffold-only stub.
 * Do not import or route to this page.
 */

// Canonical sync strings (do not edit):
// Route: /dashboard
// API: GET /api/dashboard/summary
// DTO: DashboardSummaryDTO
// DB anchor: audit_log
// PageComponent: DashboardPage

import { useEffect, useState } from "react";

import { getDashboardSummary } from "../features/dashboard/api";
import type { DashboardSummaryDTO } from "../features/dashboard/types";
import { PageHeader } from "../features/dashboard/components/PageHeader";
import { KpiCard } from "../features/dashboard/components/KpiCard";
import { Panel } from "../features/dashboard/components/Panel";
import { ActivityItem } from "../features/dashboard/components/ActivityItem";
import { TrendChart } from "../features/dashboard/components/TrendChart";
import { EmptyState } from "../features/dashboard/components/EmptyState";
import { ErrorState } from "../features/dashboard/components/ErrorState";
import { SkeletonBlock } from "../features/dashboard/components/SkeletonBlock";

type LoadState = {
  loading: boolean;
  data?: DashboardSummaryDTO;
  error?: string;
};

export function DashboardPage() {
  const [state, setState] = useState<LoadState>({ loading: true });

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setState({ loading: true });
      try {
        const data = await getDashboardSummary();
        if (cancelled) return;
        setState({ loading: false, data });
      } catch (err) {
        const message = err instanceof Error ? err.message : "unknown error";
        if (cancelled) return;
        setState({ loading: false, error: message });
      }
    };

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-4 py-6">
      <PageHeader
        title="Dashboard"
        subtitle="Scaffold-only UI stub (no route wiring)"
      />

      {state.loading ? (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <div className="rounded-lg border border-slate-200 bg-white p-4">
            <SkeletonBlock height={14} width={120} />
            <div className="mt-3">
              <SkeletonBlock height={22} width={80} />
            </div>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-4">
            <SkeletonBlock height={14} width={120} />
            <div className="mt-3">
              <SkeletonBlock height={22} width={80} />
            </div>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-4">
            <SkeletonBlock height={14} width={120} />
            <div className="mt-3">
              <SkeletonBlock height={22} width={80} />
            </div>
          </div>
        </div>
      ) : state.error ? (
        <ErrorState title="Dashboard unavailable" message={state.error} />
      ) : null}

      {!state.loading && !state.error ? (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          {(state.data?.kpis ?? []).length === 0 ? (
            <div className="sm:col-span-3">
              <EmptyState title="No KPIs yet" />
            </div>
          ) : (
            (state.data?.kpis ?? []).map((kpi) => (
              <KpiCard
                key={kpi.id}
                label={kpi.label}
                value={kpi.value}
                delta={kpi.delta}
                tone={kpi.tone}
              />
            ))
          )}
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
        <div className="lg:col-span-3">
          <Panel title="Activity">
            {(state.data?.activity ?? []).length === 0 ? (
              <EmptyState title="No activity" />
            ) : (
              <div className="divide-y divide-slate-100">
                {(state.data?.activity ?? []).map((item) => (
                  <ActivityItem
                    key={item.id}
                    message={item.message}
                    timestamp={item.timestamp}
                    tone={item.tone}
                  />
                ))}
              </div>
            )}
          </Panel>
        </div>
        <div className="lg:col-span-2">
          <Panel title="Trend">
            <TrendChart points={state.data?.trend} />
          </Panel>
        </div>
      </div>
    </div>
  );
}

/**
 * useUsageSummary — fetches real usage data from GET /api/usage/summary.
 *
 * Replaces the hardcoded zeros in useProfile for API quota,
 * storage, and cost tracking.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { apiFetch } from "../lib/apiFetch";

export interface UsageSummary {
  apiCallsUsed: number;
  apiCallsLimit: number;
  totalTokensIn: number;
  totalTokensOut: number;
  totalCostUsd: number;
  storageUsedMb: number;
  storageLimitMb: number;
  periodStart: string;
  periodEnd: string;
  planId: string;
  /* PROD-007: real usage metrics */
  agentRuns: number;
  documentsCount: number;
  ragQueries: number;
  evidenceExports: number;
}

const EMPTY: UsageSummary = {
  apiCallsUsed: 0,
  apiCallsLimit: 50,
  totalTokensIn: 0,
  totalTokensOut: 0,
  totalCostUsd: 0,
  storageUsedMb: 0,
  storageLimitMb: 512,
  periodStart: new Date().toISOString(),
  periodEnd: new Date(Date.now() + 30 * 86_400_000).toISOString(),
  planId: "free",
  agentRuns: 0,
  documentsCount: 0,
  ragQueries: 0,
  evidenceExports: 0,
};

interface UsageSummaryState {
  data: UsageSummary;
  isLoading: boolean;
  error: string | null;
}

/**
 * Map the snake_case backend response to our camelCase interface.
 */
function mapResponse(raw: Record<string, unknown>): UsageSummary {
  return {
    apiCallsUsed: (raw.api_calls_used as number) ?? 0,
    apiCallsLimit: (raw.api_calls_limit as number) ?? 50,
    totalTokensIn: (raw.total_tokens_in as number) ?? 0,
    totalTokensOut: (raw.total_tokens_out as number) ?? 0,
    totalCostUsd: (raw.total_cost_usd as number) ?? 0,
    storageUsedMb: (raw.storage_used_mb as number) ?? 0,
    storageLimitMb: (raw.storage_limit_mb as number) ?? 512,
    periodStart: (raw.period_start as string) ?? EMPTY.periodStart,
    periodEnd: (raw.period_end as string) ?? EMPTY.periodEnd,
    planId: (raw.plan_id as string) ?? "free",
    agentRuns: (raw.agent_runs as number) ?? 0,
    documentsCount: (raw.documents_count as number) ?? 0,
    ragQueries: (raw.rag_queries as number) ?? 0,
    evidenceExports: (raw.evidence_exports as number) ?? 0,
  };
}

export function useUsageSummary() {
  const [state, setState] = useState<UsageSummaryState>({
    data: EMPTY,
    isLoading: true,
    error: null,
  });
  const isMounted = useRef(true);

  const refresh = useCallback(async () => {
    try {
      const raw = await apiFetch("/usage/summary", { auth: true });
      if (isMounted.current) {
        setState({ data: mapResponse(raw as Record<string, unknown>), isLoading: false, error: null });
      }
    } catch (err) {
      if (isMounted.current) {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: (err as Error).message ?? "Failed to fetch usage",
        }));
      }
    }
  }, []);

  useEffect(() => {
    isMounted.current = true;
    refresh();
    return () => {
      isMounted.current = false;
    };
  }, [refresh]);

  return { ...state, refresh };
}

import type {
  DashboardActivityDTO,
  DashboardKpiDTO,
  DashboardSummaryDTO,
  DashboardTrendPointDTO,
} from "./types";

type RecordLike = Record<string, unknown>;

const isRecord = (value: unknown): value is RecordLike =>
  typeof value === "object" && value !== null;

const asString = (value: unknown): string | undefined =>
  typeof value === "string" ? value : undefined;

const asNumber = (value: unknown): number | undefined =>
  typeof value === "number" ? value : undefined;

const mapKpi = (value: unknown): DashboardKpiDTO | undefined => {
  if (!isRecord(value)) return undefined;

  const id = asString(value.id) ?? asString(value.key) ?? "kpi";
  const label = asString(value.label) ?? "KPI";
  const rawValue = asString(value.value) ?? asString(value.display) ?? "—";

  return {
    id,
    label,
    value: rawValue,
    delta: asString(value.delta),
    tone:
      value.tone === "neutral" ||
      value.tone === "good" ||
      value.tone === "warning" ||
      value.tone === "bad"
        ? value.tone
        : undefined,
  };
};

const mapActivity = (value: unknown): DashboardActivityDTO | undefined => {
  if (!isRecord(value)) return undefined;

  const id = asString(value.id) ?? "activity";
  const message = asString(value.message) ?? "Activity";
  const timestamp = asString(value.timestamp) ?? new Date().toISOString();

  return {
    id,
    message,
    timestamp,
    tone:
      value.tone === "neutral" ||
      value.tone === "good" ||
      value.tone === "warning" ||
      value.tone === "bad"
        ? value.tone
        : undefined,
  };
};

const mapTrendPoint = (value: unknown): DashboardTrendPointDTO | undefined => {
  if (!isRecord(value)) return undefined;

  const x = asString(value.x) ?? asString(value.label) ?? "";
  const y = asNumber(value.y) ?? asNumber(value.value) ?? 0;

  return { x, y };
};

export function mapDashboardSummaryResponse(input: unknown): DashboardSummaryDTO {
  if (!isRecord(input)) {
    return {};
  }

  const kpis = Array.isArray(input.kpis)
    ? input.kpis.map(mapKpi).filter(Boolean)
    : undefined;

  const activity = Array.isArray(input.activity)
    ? input.activity.map(mapActivity).filter(Boolean)
    : undefined;

  const trend = Array.isArray(input.trend)
    ? input.trend.map(mapTrendPoint).filter(Boolean)
    : undefined;

  return {
    kpis: kpis as DashboardKpiDTO[] | undefined,
    activity: activity as DashboardActivityDTO[] | undefined,
    trend: trend as DashboardTrendPointDTO[] | undefined,
  };
}

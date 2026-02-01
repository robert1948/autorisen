/**
 * API service for user profile and onboarding operations
 */

import { getConfig } from "../config";

const AUTH_STORAGE_KEY = "autorisen-auth";
const REFRESH_TOKEN_KEY = "autorisen-refresh-token";
const EMAIL_NOT_VERIFIED_MESSAGE = "Email not verified";

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

const DASHBOARD_STATS_DEV_FIXTURE: DashboardStats = {
  active_agents: 3,
  tasks_complete: 42,
  system_status: "operational",
  agents_deployed: 5,
  total_runs: 127,
  success_rate: 94.2,
};

const DASHBOARD_ACTIVITY_DEV_FIXTURE: ActivityItem[] = [
  {
    id: "1",
    type: "agent_deploy",
    title: "Agent Deployed",
    description: "Email automation agent deployed successfully",
    timestamp: new Date().toISOString(),
    status: "success",
  },
  {
    id: "2",
    type: "task_complete",
    title: "Task Completed",
    description: "Data analysis workflow completed",
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    status: "success",
  },
];

function handleEmailNotVerified(): void {
  if (typeof window === "undefined") return;

  try {
    window.localStorage.removeItem(AUTH_STORAGE_KEY);
    window.localStorage.removeItem(REFRESH_TOKEN_KEY);
  } catch {
    // ignore storage issues
  }

  const path = window.location?.pathname || "";
  if (!path.startsWith("/auth/verify-email")) {
    window.location.assign("/auth/verify-email");
  }
}

function getApiBaseUrl(): string {
  const config = getConfig();
  return config.API_BASE_URL || "/api";
}

// Types
export interface UserProfile {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  company: string;
  role: string;
  experience_level?: string;
  is_email_verified: boolean;
  created_at: string;
  updated_at: string;
  interests: string[];
  notifications_email: boolean;
  notifications_push: boolean;
  notifications_sms: boolean;
}

export interface UserProfileUpdate {
  first_name: string;
  last_name: string;
  company?: string;
  role: string;
  experience_level?: string;
  interests?: string[];
  notifications_email: boolean;
  notifications_push: boolean;
  notifications_sms: boolean;
}

export interface OnboardingChecklistItem {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  required: boolean;
  order: number;
}

export interface OnboardingChecklist {
  items: OnboardingChecklistItem[];
  completion_percentage: number;
  required_completed: number;
  required_total: number;
  optional_completed: number;
  optional_total: number;
}

export interface DashboardStats {
  active_agents: number;
  tasks_complete: number;
  system_status: string;
  agents_deployed: number;
  total_runs: number;
  success_rate: number;
}

export interface DashboardKpi {
  id: string;
  label: string;
  value: number;
  unit?: string;
  deltaPct?: number;
}

export interface DashboardTrendPoint {
  date: string;
  value: number;
}

export interface DashboardSummaryActivityItem {
  id: string;
  ts: string;
  type: string;
  summary: string;
  status: "ok" | "warn" | "error";
}

export interface DashboardSummary {
  kpis: DashboardKpi[];
  trend: DashboardTrendPoint[];
  recent: DashboardSummaryActivityItem[];
}

export interface DashboardSummaryMeta {
  isFallback: boolean;
  message?: string;
}

export interface DashboardSummaryResponse {
  data: DashboardSummary;
  meta: DashboardSummaryMeta;
}

export interface ActivityItem {
  id: string;
  type: string;
  title: string;
  description: string;
  timestamp: string;
  status: string;
  metadata?: Record<string, any>;
}

// API error handling
export class APIError extends Error {
  constructor(public status: number, public message: string) {
    super(message);
    this.name = 'APIError';
  }
}

// Helper function for API calls
function getAccessToken(): string | null {
  if (typeof window === "undefined" || !("localStorage" in window)) {
    return null;
  }

  try {
    const raw = window.localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as { accessToken?: string | null };
    return parsed.accessToken ?? null;
  } catch (err) {
    console.warn("Failed to read auth state", err);
    return null;
  }
}

function normalizeHeaders(headers?: HeadersInit): Record<string, string> {
  if (!headers) return {};

  const out: Record<string, string> = {};
  if (headers instanceof Headers) {
    headers.forEach((value, key) => {
      out[key] = value;
    });
    return out;
  }

  if (Array.isArray(headers)) {
    headers.forEach(([key, value]) => {
      out[key] = value;
    });
    return out;
  }

  return { ...headers };
}

function buildApiUrl(endpoint: string, baseOverride?: string): string {
  const normalizedEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;

  if (import.meta.env.DEV && baseOverride) {
    const apiBase = baseOverride.trim();
    if (shouldFetchSummaryInDev(apiBase)) {
      return new URL(`/api${normalizedEndpoint}`, apiBase).toString();
    }
  }

  return `${getApiBaseUrl()}${normalizedEndpoint}`;
}

async function apiCall<T>(
  endpoint: string,
  options: RequestInit = {},
  baseOverride?: string,
): Promise<T> {
  const url = buildApiUrl(endpoint, baseOverride);
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  const requestHeaders: Record<string, string> = {
    ...defaultHeaders,
    ...normalizeHeaders(options.headers),
  };

  const hasAuthorization = Object.keys(requestHeaders).some(
    (key) => key.toLowerCase() === "authorization",
  );

  if (!hasAuthorization) {
    const token = getAccessToken();
    if (token) {
      requestHeaders.Authorization = `Bearer ${token}`;
    }
  }

  const response = await fetch(url, {
    ...options,
    headers: requestHeaders,
    credentials: 'include', // Include cookies for authentication
  });

  if (!response.ok) {
    const errorText = await response.text();

    if (
      response.status === 403 &&
      typeof errorText === "string" &&
      errorText.toLowerCase().includes(EMAIL_NOT_VERIFIED_MESSAGE.toLowerCase())
    ) {
      handleEmailNotVerified();
    }

    throw new APIError(response.status, errorText || `HTTP ${response.status}`);
  }

  return response.json();
}

// User Profile API
export const userProfileAPI = {
  /**
   * Get current user's profile
   */
  async getProfile(): Promise<UserProfile> {
    return apiCall<UserProfile>('/user/profile');
  },

  /**
   * Update current user's profile
   */
  async updateProfile(profileData: UserProfileUpdate): Promise<UserProfile> {
    return apiCall<UserProfile>('/user/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  },
};

// Onboarding API
export const onboardingAPI = {
  /**
   * Get onboarding checklist for current user
   */
  async getChecklist(): Promise<OnboardingChecklist> {
    return apiCall<OnboardingChecklist>('/user/onboarding/checklist');
  },

  /**
   * Mark an onboarding item as complete
   */
  async completeItem(itemId: string): Promise<{ status: string; item_id: string }> {
    return apiCall<{ status: string; item_id: string }>(
      `/user/onboarding/checklist/item/${itemId}/complete`,
      {
        method: 'POST',
      }
    );
  },
};

// Dashboard API
export const dashboardAPI = {
  /**
   * Get dashboard statistics
   */
  async getStats(): Promise<DashboardStats> {
    const apiBase = (import.meta.env.VITE_API_URL as string | undefined)?.trim();
    if (import.meta.env.DEV && !shouldFetchSummaryInDev(apiBase)) {
      return DASHBOARD_STATS_DEV_FIXTURE;
    }

    return apiCall<DashboardStats>("/user/dashboard/stats", {}, apiBase);
  },

  /**
   * Get recent activity
   */
  async getRecentActivity(limit: number = 10): Promise<ActivityItem[]> {
    const apiBase = (import.meta.env.VITE_API_URL as string | undefined)?.trim();
    if (import.meta.env.DEV && !shouldFetchSummaryInDev(apiBase)) {
      return DASHBOARD_ACTIVITY_DEV_FIXTURE.slice(0, Math.max(0, limit));
    }

    return apiCall<ActivityItem[]>(
      `/user/dashboard/recent-activity?limit=${limit}`,
      {},
      apiBase,
    );
  },

  /**
   * Canonical dashboard payload used by the deployable UI.
   * - If the endpoint is missing (404/501), return fixture data with a clean message.
   * - Never surface raw "HTTP 404 Not Found" text to the user.
   */
  async getSummary(): Promise<DashboardSummaryResponse> {
    const apiBase = (import.meta.env.VITE_API_URL as string | undefined)?.trim();

    const fixture: DashboardSummary = {
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

    if (import.meta.env.DEV && !shouldFetchSummaryInDev(apiBase)) {
      return {
        data: fixture,
        meta: {
          isFallback: true,
          message: "Using fallback data — live dashboard feed isn’t enabled yet.",
        },
      };
    }

    try {
      const data = await apiCall<DashboardSummary>("/dashboard/summary", {}, apiBase);
      return { data, meta: { isFallback: false } };
    } catch (err) {
      const status = err instanceof APIError ? err.status : undefined;
      const message =
        status === 404 || status === 501
          ? "Using fallback data — live dashboard feed isn’t enabled yet."
          : "Using fallback data — temporary service issue.";

      return {
        data: fixture,
        meta: { isFallback: true, message },
      };
    }
  },
};

// Combined API export
export const api = {
  userProfile: userProfileAPI,
  onboarding: onboardingAPI,
  dashboard: dashboardAPI,
};
import { getConfig } from "../config";
import { getCsrfToken } from "../lib/authApi";

function getApiBase(): string {
  const config = getConfig();
  return config.API_BASE_URL || "/api";
}

const AUTH_STORAGE_KEY = "autorisen-auth";

const defaultHeaders: Record<string, string> = {
  "Content-Type": "application/json",
};

const defaultFetchOptions: RequestInit = {
  credentials: "include",
};

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

type RequestOptions = {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
  auth?: boolean;
  csrf?: boolean;
};

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, headers = {}, auth = true, csrf = false } = options;
  const requestHeaders: Record<string, string> = {
    ...defaultHeaders,
    ...headers,
  };

  if (auth) {
    const token = getAccessToken();
    if (token) {
      requestHeaders.Authorization = `Bearer ${token}`;
    }
  }

  if (csrf && method !== "GET") {
    const csrfToken = await getCsrfToken();
    requestHeaders["X-CSRF-Token"] = csrfToken;
  }

  const response = await fetch(`${getApiBase()}${endpoint}`, {
    method,
    headers: requestHeaders,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    ...defaultFetchOptions,
  });

  if (response.ok) {
    if (response.status === 204) {
      return undefined as T;
    }
    const text = await response.text();
    if (!text) {
      return undefined as T;
    }
    return JSON.parse(text) as T;
  }

  let message = `Request failed with status ${response.status}`;
  try {
    const data = await response.json();
    if (typeof data?.detail === "string") {
      message = data.detail;
    } else if (data?.detail) {
      message = JSON.stringify(data.detail);
    }
  } catch (err) {
    console.warn("Failed to parse error response", err);
  }

  const error = new Error(message) as Error & { status?: number };
  error.status = response.status;
  throw error;
}

export type OnboardingSession = {
  id: string;
  status: string;
  onboarding_completed: boolean;
  last_step_key?: string | null;
  started_at: string;
  completed_at?: string | null;
};

export type OnboardingStepState = {
  status: string;
  completed_at?: string | null;
  skipped_at?: string | null;
};

export type OnboardingStep = {
  step_key: string;
  title: string;
  order_index: number;
  required: boolean;
  role_scope_json?: Record<string, unknown> | null;
  state?: OnboardingStepState | null;
};

export type OnboardingStatus = {
  session: OnboardingSession | null;
  steps: OnboardingStep[];
  progress: number;
};

export async function getOnboardingStatus(): Promise<OnboardingStatus> {
  return request<OnboardingStatus>("/onboarding/status");
}

export async function startOnboarding(): Promise<OnboardingStatus> {
  return request<OnboardingStatus>("/onboarding/start", { method: "POST", csrf: true });
}

export async function updateOnboardingProfile(payload: Record<string, unknown>) {
  return request<{ profile: Record<string, unknown> }>("/onboarding/profile", {
    method: "PATCH",
    body: payload,
    csrf: true,
  });
}

export async function listOnboardingSteps(): Promise<OnboardingStep[]> {
  return request<OnboardingStep[]>("/onboarding/steps");
}

export async function completeOnboardingStep(stepKey: string) {
  return request<{ step: OnboardingStep; progress: number }>(
    `/onboarding/steps/${stepKey}/complete`,
    {
      method: "POST",
      csrf: true,
    },
  );
}

export async function skipOnboardingStep(stepKey: string) {
  return request<{ step: OnboardingStep; progress: number }>(
    `/onboarding/steps/${stepKey}/skip`,
    {
      method: "POST",
      csrf: true,
    },
  );
}

export async function acknowledgeTrust(key: string, metadata?: Record<string, unknown>) {
  return request<{ key: string; acknowledged_at: string }>(`/onboarding/trust/${key}/ack`, {
    method: "POST",
    body: metadata ? { metadata } : undefined,
    csrf: true,
  });
}

export async function completeOnboarding() {
  return request<{ session: OnboardingSession; progress: number }>("/onboarding/complete", {
    method: "POST",
    csrf: true,
  });
}

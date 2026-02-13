import { getConfig } from "../config";

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

let unauthorizedHandler: (() => void) | null = null;
let unauthorizedFired = false;
let unauthorizedTimer: ReturnType<typeof setTimeout> | null = null;

export function setApiUnauthorizedHandler(handler: (() => void) | null): void {
  unauthorizedHandler = handler;
  // Reset the dedup flag when handler is (re)set
  unauthorizedFired = false;
  if (unauthorizedTimer) {
    clearTimeout(unauthorizedTimer);
    unauthorizedTimer = null;
  }
}

type RequestOptions = {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
  auth?: boolean;
  signal?: AbortSignal;
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

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, headers = {}, auth = true, signal } = options;
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

  const response = await fetch(`${getApiBase()}${endpoint}`, {
    method,
    headers: requestHeaders,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    signal,
    ...defaultFetchOptions,
  });

  if (response.status === 401 && unauthorizedHandler && !unauthorizedFired) {
    unauthorizedFired = true;
    // Debounce: only fire once per 2 s window to prevent redirect storms
    unauthorizedTimer = setTimeout(() => { unauthorizedFired = false; }, 2000);
    unauthorizedHandler();
  }

  if (response.ok) {
    if (response.status === 204) {
      return undefined as T;
    }
    const text = await response.text();
    if (!text) {
      return undefined as T;
    }
    try {
      return JSON.parse(text) as T;
    } catch (err) {
      console.warn("Failed to parse JSON response", err);
      return undefined as T;
    }
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

export type ChecklistTask = {
  label: string;
  done: boolean;
};

export type ChecklistSummary = {
  tasks: Record<string, ChecklistTask>;
  summary: {
    completed: number;
    total: number;
  };
};

export async function fetchOnboardingChecklist(): Promise<ChecklistSummary> {
  return request<ChecklistSummary>("/flows/onboarding/checklist");
}

export async function updateOnboardingChecklist(
  taskId: string,
  done: boolean,
  label?: string,
): Promise<ChecklistSummary> {
  return request<ChecklistSummary>("/flows/onboarding/checklist", {
    method: "POST",
    body: {
      task_id: taskId,
      done,
      label,
    },
  });
}

export type FlowRunRecord = {
  id: string;
  placement: string;
  thread_id: string;
  agent_id: string | null;
  agent_version_id: string | null;
  steps: Array<Record<string, unknown>>;
  created_at: string;
  status: string;
  attempt: number;
  max_attempts: number;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
};

export async function fetchFlowRuns(
  placement?: string,
  limit: number = 10,
): Promise<FlowRunRecord[]> {
  const params = new URLSearchParams();
  if (placement) {
    params.set("placement", placement);
  }
  params.set("limit", String(limit));
  const query = params.toString();
  const path = `/flows/runs${query ? `?${query}` : ""}`;
  return request<FlowRunRecord[]>(path);
}

export type FlowRunStep = {
  tool: string;
  payload: Record<string, unknown>;
  result: Record<string, unknown>;
  event_id: string;
};

export type FlowRunResponse = {
  run_id: string;
  thread_id: string;
  placement: string;
  steps: FlowRunStep[];
  agent_id: string | null;
  agent_version_id: string | null;
  status: string;
  attempt: number;
  max_attempts: number;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
};

export type RunFlowPayload = {
  placement?: string;
  agent_slug?: string;
  agent_version?: string;
  thread_id?: string;
  tool_calls: Array<{ name: string; payload: Record<string, unknown> }>;
  idempotency_key?: string;
  max_attempts?: number;
};

export async function runFlow(payload: RunFlowPayload): Promise<FlowRunResponse> {
  return request<FlowRunResponse>("/flows/run", {
    method: "POST",
    body: payload,
  });
}

export type AgentVersion = {
  id: string;
  version: string;
  manifest: Record<string, unknown>;
  changelog?: string | null;
  status: "draft" | "published" | string;
  created_at: string;
  published_at: string | null;
};

export type Agent = {
  id: string;
  owner_id: string | null;
  name: string;
  slug: string;
  description?: string | null;
  visibility: "private" | "public" | string;
  created_at: string;
  updated_at: string;
  versions: AgentVersion[];
};

export type CreateAgentPayload = {
  name: string;
  slug: string;
  description?: string;
  visibility: "private" | "public";
};

export async function listAgents(): Promise<Agent[]> {
  return request<Agent[]>("/agents");
}

export async function createAgent(payload: CreateAgentPayload): Promise<Agent> {
  return request<Agent>("/agents", {
    method: "POST",
    body: payload,
  });
}

export async function fetchAgentDetail(agentId: string): Promise<Agent> {
  return request<Agent>(`/agents/${agentId}`);
}

export type CreateAgentVersionPayload = {
  version: string;
  manifest: Record<string, unknown>;
  changelog?: string;
  status: "draft" | "published";
};

export async function createAgentVersion(
  agentId: string,
  payload: CreateAgentVersionPayload,
): Promise<AgentVersion> {
  return request<AgentVersion>(`/agents/${agentId}/versions`, {
    method: "POST",
    body: payload,
  });
}

export async function publishAgentVersion(
  agentId: string,
  versionId: string,
): Promise<AgentVersion> {
  return request<AgentVersion>(`/agents/${agentId}/versions/${versionId}/publish`, {
    method: "POST",
  });
}

export type MarketplaceAgent = {
  id: string;
  slug: string;
  name: string;
  description: string;
  category: string;
  author: string;
  version: string;
  rating: number;
  downloads: number;
  tags: string[];
  published_at: string;
  updated_at: string;
  thumbnail_url?: string | null;
};

export type AgentRun = {
  id: string;
  agent_id: string;
  user_id: string;
  status: string;
  input_json?: Record<string, unknown> | null;
  output_json?: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
};

export type AgentActionResult = {
  run_id: string;
  event_id: string;
  status: string;
  result: Record<string, unknown>;
};

export type OpsInsight = {
  title: string;
  summary: string;
  key_metrics: Array<Record<string, unknown>>;
  sources: Array<Record<string, unknown>>;
};

export async function fetchMarketplaceAgents(): Promise<MarketplaceAgent[]> {
  return request<MarketplaceAgent[]>("/agents?published=true");
}

export type MarketplaceAgentDetail = MarketplaceAgent & {
  readme: string;
  changelog: string;
  requirements: string[];
  configuration: Record<string, unknown>;
  permissions: string[];
  license: string;
  repository_url?: string | null;
  documentation_url?: string | null;
  support_url?: string | null;
};

export async function fetchMarketplaceAgentDetail(
  slug: string,
): Promise<MarketplaceAgentDetail> {
  return request<MarketplaceAgentDetail>(`/agents/${slug}?published=true`);
}

export async function launchMarketplaceAgent(
  slug: string,
  input?: Record<string, unknown>,
): Promise<AgentRun> {
  return request<AgentRun>(`/agents/${slug}/launch`, {
    method: "POST",
    body: { input },
  });
}

export async function runMarketplaceAgentAction(
  slug: string,
  runId: string,
  action: string,
  payload: Record<string, unknown> = {},
): Promise<AgentActionResult> {
  return request<AgentActionResult>(`/agents/${slug}/action`, {
    method: "POST",
    body: {
      run_id: runId,
      action,
      payload,
    },
  });
}

export { request as apiRequest };

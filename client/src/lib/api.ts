const API_BASE =
  ((import.meta as unknown as { env?: Record<string, string | undefined> }).env?.VITE_API_BASE as
    | string
    | undefined) ?? "/api";

const AUTH_STORAGE_KEY = "autorisen-auth";

const defaultHeaders: Record<string, string> = {
  "Content-Type": "application/json",
};

const defaultFetchOptions: RequestInit = {
  credentials: "include",
};

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

  const response = await fetch(`${API_BASE}${endpoint}`, {
    method,
    headers: requestHeaders,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    signal,
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

  throw new Error(message);
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
  description?: string | null;
  owner_id: string | null;
  updated_at: string;
  version: {
    id: string;
    version: string;
    published_at: string | null;
    manifest?: Record<string, unknown>;
  };
};

export async function fetchMarketplaceAgents(): Promise<MarketplaceAgent[]> {
  return request<MarketplaceAgent[]>("/marketplace/agents", { auth: false });
}

export type MarketplaceAgentDetail = {
  id: string;
  slug: string;
  name: string;
  description?: string | null;
  owner_id: string | null;
  created_at: string;
  updated_at: string;
  published_version: string | null;
  versions: Array<{
    id: string;
    version: string;
    status: string;
    created_at: string;
    published_at: string | null;
    manifest: Record<string, unknown>;
  }>;
};

export async function fetchMarketplaceAgentDetail(
  slug: string,
): Promise<MarketplaceAgentDetail> {
  return request<MarketplaceAgentDetail>(`/marketplace/agents/${slug}`, { auth: false });
}

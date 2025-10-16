export type AgentVersion = {
  id: string;
  version: string;
  status: string;
  created_at: string;
  published_at?: string | null;
  manifest: Record<string, unknown>;
  changelog?: string | null;
};

export type Agent = {
  id: string;
  name: string;
  slug: string;
  description?: string | null;
  visibility: string;
  owner_id?: string | null;
  created_at: string;
  updated_at: string;
  versions: AgentVersion[];
};

const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined) ?? "/api";

const AUTH_STORAGE_KEY = "autorisen-auth";

const getAccessToken = (): string | null => {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as { accessToken?: string | null };
    return parsed.accessToken ?? null;
  } catch (err) {
    console.warn("Failed to parse auth token", err);
    return null;
  }
};

const jsonHeaders = () => {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  const token = getAccessToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
};

const authHeaders = () => {
  const headers: Record<string, string> = {};
  const token = getAccessToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
};

const handleResponse = async <T>(res: Response): Promise<T> => {
  if (!res.ok) {
    const message = await res
      .json()
      .catch(() => ({ detail: res.statusText }));
    throw new Error(message?.detail ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
};

export const listAgents = async (): Promise<Agent[]> => {
  const response = await fetch(`${API_BASE}/agents`, {
    method: "GET",
    headers: authHeaders(),
    credentials: "include",
  });
  return handleResponse<Agent[]>(response);
};

export type CreateAgentPayload = {
  name: string;
  slug: string;
  description?: string;
  visibility?: string;
};

export const createAgent = async (
  payload: CreateAgentPayload,
): Promise<Agent> => {
  const response = await fetch(`${API_BASE}/agents`, {
    method: "POST",
    headers: jsonHeaders(),
    credentials: "include",
    body: JSON.stringify(payload),
  });
  return handleResponse<Agent>(response);
};

export type CreateAgentVersionPayload = {
  version: string;
  manifest: Record<string, unknown>;
  changelog?: string;
  status?: string;
};

export const createAgentVersion = async (
  agentId: string,
  payload: CreateAgentVersionPayload,
): Promise<AgentVersion> => {
  const response = await fetch(`${API_BASE}/agents/${agentId}/versions`, {
    method: "POST",
    headers: jsonHeaders(),
    credentials: "include",
    body: JSON.stringify(payload),
  });
  return handleResponse<AgentVersion>(response);
};

export const publishAgentVersion = async (
  agentId: string,
  versionId: string,
): Promise<AgentVersion> => {
  const response = await fetch(
    `${API_BASE}/agents/${agentId}/versions/${versionId}/publish`,
    {
      method: "POST",
      headers: jsonHeaders(),
      credentials: "include",
    },
  );
  return handleResponse<AgentVersion>(response);
};

export type MarketplaceAgent = {
  id: string;
  slug: string;
  name: string;
  description?: string;
  owner_id?: string;
  updated_at: string;
  version: {
    id: string;
    version: string;
    published_at?: string;
    manifest: Record<string, unknown>;
  };
};

export type MarketplaceAgentDetail = {
  id: string;
  slug: string;
  name: string;
  description?: string;
  owner_id?: string;
  created_at: string;
  updated_at: string;
  published_version?: string | null;
  versions: AgentVersion[];
};

export const fetchMarketplaceAgents = async (): Promise<MarketplaceAgent[]> => {
  const response = await fetch(`${API_BASE}/marketplace/agents`, {
    headers: authHeaders(),
  });
  return handleResponse<MarketplaceAgent[]>(response);
};

export const fetchMarketplaceAgentDetail = async (
  slug: string,
): Promise<MarketplaceAgentDetail> => {
  const response = await fetch(`${API_BASE}/marketplace/agents/${slug}`, {
    headers: authHeaders(),
  });
  return handleResponse<MarketplaceAgentDetail>(response);
};

export type FlowRunResponse = {
  run_id: string;
  thread_id: string;
  placement: string;
  steps: Array<{
    tool: string;
    payload: Record<string, unknown>;
    result: Record<string, unknown>;
    event_id: string;
  }>;
  agent_id?: string;
  agent_version_id?: string;
  status: string;
  attempt: number;
  max_attempts: number;
  error_message?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
};

export type FlowRunRecord = {
  id: string;
  placement: string;
  thread_id: string;
  agent_id?: string | null;
  agent_version_id?: string | null;
  steps: Array<Record<string, unknown>>;
  created_at: string;
  status: string;
  attempt: number;
  max_attempts: number;
  error_message?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
};

export type FlowRunRequest = {
  placement?: string;
  agent_slug?: string;
  agent_version?: string;
  thread_id?: string;
  tool_calls: Array<{
    name: string;
    payload: Record<string, unknown>;
  }>;
  idempotency_key?: string;
  max_attempts?: number;
};

export const runFlow = async (payload: FlowRunRequest): Promise<FlowRunResponse> => {
  const response = await fetch(`${API_BASE}/flows/run`, {
    method: "POST",
    headers: jsonHeaders(),
    credentials: "include",
    body: JSON.stringify(payload),
  });
  return handleResponse<FlowRunResponse>(response);
};

export const fetchFlowRuns = async (
  placement?: string,
  limit = 10,
): Promise<FlowRunRecord[]> => {
  const params = new URLSearchParams();
  params.set("limit", String(limit));
  if (placement) {
    params.set("placement", placement);
  }
  const response = await fetch(`${API_BASE}/flows/runs?${params.toString()}`, {
    headers: authHeaders(),
    credentials: "include",
  });
  return handleResponse<FlowRunRecord[]>(response);
};

export type ChecklistSummary = {
  tasks: Record<string, { label: string; done: boolean }>;
  summary: {
    completed: number;
    total: number;
  };
};

export const fetchOnboardingChecklist = async (): Promise<ChecklistSummary> => {
  const response = await fetch(`${API_BASE}/flows/onboarding/checklist`, {
    headers: authHeaders(),
    credentials: "include",
  });
  return handleResponse<ChecklistSummary>(response);
};

export const updateOnboardingChecklist = async (
  taskId: string,
  done: boolean,
  label?: string,
): Promise<ChecklistSummary> => {
  const response = await fetch(`${API_BASE}/flows/onboarding/checklist`, {
    method: "POST",
    headers: jsonHeaders(),
    credentials: "include",
    body: JSON.stringify({ task_id: taskId, done, label }),
  });
  return handleResponse<ChecklistSummary>(response);
};

export const fetchAgentDetail = async (agentId: string): Promise<Agent> => {
  const response = await fetch(`${API_BASE}/agents/${agentId}`, {
    headers: authHeaders(),
    credentials: "include",
  });
  return handleResponse<Agent>(response);
};

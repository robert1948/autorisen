import { getConfig } from "../config";

function getApiBase(): string {
  const config = getConfig();
  return config.API_BASE_URL || "/api";
}

type RequestOptions = {
  method?: string;
  body?: unknown;
};

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body } = options;
  const response = await fetch(`${getApiBase()}${endpoint}`, {
    method,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const error = new Error(`Request failed with status ${response.status}`) as Error & {
      status?: number;
    };
    error.status = response.status;
    try {
      const data = await response.json();
      if (typeof data?.detail === "string") {
        error.message = data.detail;
      }
    } catch (err) {
      // ignore parse errors
    }
    throw error;
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export type AccountDetails = {
  id: string;
  email: string;
  display_name: string;
  status: string;
  role: string;
  created_at: string;
  last_login?: string | null;
  company_name?: string | null;
};

export type AccountUpdate = {
  display_name?: string | null;
  first_name?: string | null;
  last_name?: string | null;
  company_name?: string | null;
};

export type PersonalInfo = {
  phone?: string | null;
  location?: string | null;
  timezone?: string | null;
  bio?: string | null;
  avatar_url?: string | null;
  updated_at?: string | null;
};

export type PersonalInfoUpdate = {
  phone?: string | null;
  location?: string | null;
  timezone?: string | null;
  bio?: string | null;
  avatar_url?: string | null;
};

export type ProjectStatusItem = {
  id: string;
  title: string;
  status: string;
  created_at: string;
};

export type AccountBalance = {
  total_paid: number;
  total_pending: number;
  currency: string;
};

export const dashboardModulesApi = {
  getAccountDetails(): Promise<AccountDetails> {
    return request<AccountDetails>("/account/me");
  },
  updateAccountDetails(payload: AccountUpdate): Promise<AccountDetails> {
    return request<AccountDetails>("/account/me", { method: "PATCH", body: payload });
  },
  getPersonalInfo(): Promise<PersonalInfo> {
    return request<PersonalInfo>("/profile/me");
  },
  updatePersonalInfo(payload: PersonalInfoUpdate): Promise<PersonalInfo> {
    return request<PersonalInfo>("/profile/me", { method: "PATCH", body: payload });
  },
  getProjects(): Promise<ProjectStatusItem[]> {
    return request<ProjectStatusItem[]>("/projects/mine");
  },
  getBalance(): Promise<AccountBalance> {
    return request<AccountBalance>("/billing/balance");
  },
  deleteAccount(): Promise<{ status: string; message: string }> {
    return request<{ status: string; message: string }>("/account/me", { method: "DELETE" });
  },
};

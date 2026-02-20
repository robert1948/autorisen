import { apiFetch } from "../lib/apiFetch";

type RequestOptions = {
  method?: string;
  body?: unknown;
};

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
  currency?: string | null;
  updated_at?: string | null;
};

export type PersonalInfoUpdate = {
  phone?: string | null;
  location?: string | null;
  timezone?: string | null;
  bio?: string | null;
  avatar_url?: string | null;
  currency?: string | null;
};

export type ProjectStatusItem = {
  id: string;
  title: string;
  status: string;
  created_at: string;
};

export type ProjectStatusSummary = {
  value: string;
  total: number;
  projects: ProjectStatusItem[];
};

export type ProjectDetail = {
  id: string;
  title: string;
  description?: string | null;
  status: string;
  created_at: string;
  updated_at?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
};

export type AccountBalance = {
  total_paid: number;
  total_pending: number;
  currency: string;
};

/* ── Developer API types ──────────────────────────── */

export type ApiCredential = {
  id: string;
  client_id: string;
  label: string | null;
  is_active: boolean;
  created_at: string;
  revoked_at: string | null;
};

export type ApiCredentialCreated = {
  id: string;
  client_id: string;
  client_secret: string;
  label: string;
  created_at: string;
  message: string;
};

export type DeveloperUsage = {
  total_api_keys: number;
  active_api_keys: number;
  revoked_api_keys: number;
  account_created_at: string | null;
  email_verified: boolean;
};

export type DeveloperProfile = {
  user_id: string;
  email: string;
  first_name: string;
  last_name: string;
  organization: string | null;
  use_case: string | null;
  website_url: string | null;
  github_url: string | null;
  developer_terms_accepted_at: string | null;
  developer_terms_version: string | null;
  created_at: string;
  email_verified: boolean;
};

/* ── Admin API types ──────────────────────────────── */

export type AdminInvite = {
  id: string;
  target_email: string;
  invited_by: string;
  created_at: string;
  expires_at: string;
  used_at: string | null;
  revoked_at: string | null;
};

export type AdminInviteCreated = {
  invite_id: string;
  target_email: string;
  expires_at: string;
};

export const dashboardModulesApi = {
  getAccountDetails(): Promise<AccountDetails> {
    return apiFetch<AccountDetails>("/account/me");
  },
  updateAccountDetails(payload: AccountUpdate): Promise<AccountDetails> {
    return apiFetch<AccountDetails>("/account/me", { method: "PATCH", body: payload });
  },
  getPersonalInfo(): Promise<PersonalInfo> {
    return apiFetch<PersonalInfo>("/profile/me");
  },
  updatePersonalInfo(payload: PersonalInfoUpdate): Promise<PersonalInfo> {
    return apiFetch<PersonalInfo>("/profile/me", { method: "PATCH", body: payload });
  },
  getProjects(): Promise<ProjectStatusItem[]> {
    return apiFetch<ProjectStatusItem[]>("/projects/mine");
  },
  createProject(payload: { title: string; description?: string }): Promise<ProjectStatusItem> {
    return apiFetch<ProjectStatusItem>("/projects", { method: "POST", body: payload });
  },
  getProject(id: string): Promise<ProjectDetail> {
    return apiFetch<ProjectDetail>(`/projects/${id}`);
  },
  updateProject(id: string, payload: { title?: string; description?: string; status?: string }): Promise<ProjectDetail> {
    return apiFetch<ProjectDetail>(`/projects/${id}`, { method: "PATCH", body: payload });
  },
  deleteProject(id: string): Promise<void> {
    return apiFetch<void>(`/projects/${id}`, { method: "DELETE" });
  },
  getProjectStatus(): Promise<ProjectStatusSummary> {
    return apiFetch<ProjectStatusSummary>("/projects/status");
  },
  getBalance(): Promise<AccountBalance> {
    return apiFetch<AccountBalance>("/billing/balance");
  },
  deleteAccount(): Promise<{ status: string; message: string }> {
    return apiFetch<{ status: string; message: string }>("/account/me", { method: "DELETE" });
  },

  /* ── Developer endpoints (/api/dev/*) ── */

  getDevApiKeys(): Promise<ApiCredential[]> {
    return apiFetch<ApiCredential[]>("/dev/api-keys");
  },
  createDevApiKey(label: string): Promise<ApiCredentialCreated> {
    return apiFetch<ApiCredentialCreated>("/dev/api-keys", { method: "POST", body: { label } });
  },
  revokeDevApiKey(id: string): Promise<{ message: string }> {
    return apiFetch<{ message: string }>(`/dev/api-keys/${id}`, { method: "DELETE" });
  },
  getDevUsage(): Promise<DeveloperUsage> {
    return apiFetch<DeveloperUsage>("/dev/usage");
  },
  getDevProfile(): Promise<DeveloperProfile> {
    return apiFetch<DeveloperProfile>("/dev/profile");
  },

  /* ── Admin endpoints (/api/admin/*) ── */

  getAdminInvites(): Promise<AdminInvite[]> {
    return apiFetch<AdminInvite[]>("/admin/invites");
  },
  createAdminInvite(target_email: string, expiry_hours?: number): Promise<AdminInviteCreated> {
    return apiFetch<AdminInviteCreated>("/admin/invite", {
      method: "POST",
      body: { target_email, expiry_hours: expiry_hours ?? 72 },
    });
  },
  revokeAdminInvite(id: string): Promise<{ message: string }> {
    return apiFetch<{ message: string }>(`/admin/invite/${id}`, { method: "DELETE" });
  },

  /* ── Health ── */

  getHealthStatus(): Promise<{ status: string; database?: string }> {
    return apiFetch<{ status: string; database?: string }>("/health", { auth: false });
  },
};

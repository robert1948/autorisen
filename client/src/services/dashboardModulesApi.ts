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
  getBalance(): Promise<AccountBalance> {
    return apiFetch<AccountBalance>("/billing/balance");
  },
  deleteAccount(): Promise<{ status: string; message: string }> {
    return apiFetch<{ status: string; message: string }>("/account/me", { method: "DELETE" });
  },
};

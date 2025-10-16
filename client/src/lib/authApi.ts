const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "/api";
const defaultHeaders = {
  "Content-Type": "application/json",
};

type ErrorPayload = { detail?: string };

const handleResponse = async <T>(resp: Response): Promise<T> => {
  if (!resp.ok) {
    const message = (await resp.json().catch(() => ({ detail: resp.statusText }))) as ErrorPayload;
    throw new Error(message.detail ?? `HTTP ${resp.status}`);
  }
  return (await resp.json()) as T;
};

export type UserRole = "Customer" | "Developer";

export type TokenResponse = {
  access_token: string;
  refresh_token: string | null;
  expires_at: string | null;
};

export type RegisterStep1Payload = {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  confirm_password: string;
  role: UserRole;
  recaptcha_token: string;
};

export type RegisterStep1Response = {
  temp_token: string;
};

export type RegisterStep2Payload = {
  company_name: string;
  profile: Record<string, unknown>;
};

export type RegisteredUser = {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  company_name: string;
  is_email_verified: boolean;
  created_at: string;
  profile: Record<string, unknown>;
};

export type RegisterStep2Response = {
  access_token: string;
  refresh_token: string | null;
  expires_at: string | null;
  user: RegisteredUser;
};

export type AnalyticsEventPayload = {
  event_type: string;
  step?: string | null;
  role?: UserRole | null;
  details?: Record<string, unknown>;
};

export const registerStep1 = async (
  payload: RegisterStep1Payload,
): Promise<RegisterStep1Response> => {
  const resp = await fetch(`${API_BASE}/auth/register/step1`, {
    method: "POST",
    headers: defaultHeaders,
    credentials: "include",
    body: JSON.stringify(payload),
  });
  return handleResponse<RegisterStep1Response>(resp);
};

export const registerStep2 = async (
  payload: RegisterStep2Payload,
  tempToken: string,
): Promise<RegisterStep2Response> => {
  const resp = await fetch(`${API_BASE}/auth/register/step2`, {
    method: "POST",
    headers: {
      ...defaultHeaders,
      Authorization: `Bearer ${tempToken}`,
    },
    credentials: "include",
    body: JSON.stringify(payload),
  });
  return handleResponse<RegisterStep2Response>(resp);
};

export const resendWelcomeEmail = async (): Promise<void> => {
  const resp = await fetch(`${API_BASE}/auth/resend-welcome`, {
    method: "POST",
    headers: defaultHeaders,
    credentials: "include",
  });
  if (!resp.ok) {
    const message = (await resp.json().catch(() => ({ detail: resp.statusText }))) as ErrorPayload;
    throw new Error(message.detail ?? `HTTP ${resp.status}`);
  }
};

export const trackAnalyticsEvent = async (payload: AnalyticsEventPayload): Promise<void> => {
  const resp = await fetch(`${API_BASE}/auth/analytics/track`, {
    method: "POST",
    headers: defaultHeaders,
    credentials: "include",
    body: JSON.stringify(payload),
  });
  if (!resp.ok && resp.status !== 204) {
    const message = (await resp.json().catch(() => ({ detail: resp.statusText }))) as ErrorPayload;
    throw new Error(message.detail ?? `HTTP ${resp.status}`);
  }
};

export const login = async (email: string, password: string): Promise<TokenResponse> => {
  const resp = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: defaultHeaders,
    credentials: "include",
    body: JSON.stringify({ email, password }),
  });
  return handleResponse<TokenResponse>(resp);
};

export const refreshSession = async (refreshToken: string): Promise<TokenResponse> => {
  const resp = await fetch(`${API_BASE}/auth/refresh`, {
    method: "POST",
    headers: defaultHeaders,
    credentials: "include",
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  return handleResponse<TokenResponse>(resp);
};

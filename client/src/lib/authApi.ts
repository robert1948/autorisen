const API_BASE =
  ((import.meta as unknown as { env?: Record<string, string | undefined> }).env?.VITE_API_BASE as
    | string
    | undefined) ?? "/api";
const AUTH_BASE = `${API_BASE}/auth`;
const CSRF_HEADER = "X-CSRF-Token";

export type UserRole = "Customer" | "Developer";

let csrfTokenCache: string | null = null;
let unauthorizedHandler: (() => void) | null = null;

export function setUnauthorizedHandler(handler: (() => void) | null): void {
  unauthorizedHandler = handler;
}

const defaultHeaders: Record<string, string> = {
  "Content-Type": "application/json",
};

const defaultFetchOptions: RequestInit = {
  credentials: "include",
};

function getStoredAccessToken(): string | null {
  if (typeof window === "undefined" || !("localStorage" in window)) {
    return null;
  }
  try {
    const raw = window.localStorage.getItem("autorisen-auth");
    if (!raw) return null;
    const parsed = JSON.parse(raw) as { accessToken?: string | null };
    return parsed.accessToken ?? null;
  } catch (err) {
    console.warn("Failed to read auth state", err);
    return null;
  }
}

async function fetchCsrfToken(): Promise<string> {
  if (csrfTokenCache) {
    return csrfTokenCache;
  }

  const response = await fetch(`${AUTH_BASE}/csrf`, {
    method: "GET",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Unable to fetch CSRF token");
  }

  const data = (await response.json()) as { csrf_token: string };
  csrfTokenCache = data.csrf_token;
  return csrfTokenCache;
}

function invalidateCsrfToken(): void {
  csrfTokenCache = null;
}

async function parseError(response: Response): Promise<never> {
  let message = `Request failed with status ${response.status}`;

  try {
    const data = await response.json();
    if (typeof data?.error?.message === "string") {
      message = data.error.message;
    } else if (typeof data?.detail === "string") {
      message = data.detail;
    } else if (data?.detail) {
      message = JSON.stringify(data.detail);
    }
  } catch (err) {
    console.warn("Failed to parse error response", err);
  }

  if (response.status === 401 && unauthorizedHandler) {
    unauthorizedHandler();
  }

  invalidateCsrfToken();
  const error = new Error(message) as Error & { status?: number };
  error.status = response.status;
  throw error;
}

type FieldErrorMap = Record<string, string>;

export type RegisterApiError = Error & {
  status?: number;
  fieldErrors?: FieldErrorMap;
};

function extractFieldErrors(detail: unknown): FieldErrorMap | undefined {
  if (detail && typeof detail === "object" && !Array.isArray(detail)) {
    const entries = Object.entries(detail as Record<string, unknown>);
    if (entries.length > 0 && entries.every(([, value]) => typeof value === "string")) {
      return entries.reduce<FieldErrorMap>((acc, [key, value]) => {
        acc[key] = String(value);
        return acc;
      }, {});
    }
  }
  if (Array.isArray(detail)) {
    return detail.reduce<FieldErrorMap>((acc, item) => {
      if (!item || typeof item !== "object") return acc;
      const loc = (item as { loc?: unknown }).loc;
      const msg = (item as { msg?: string }).msg;
      if (Array.isArray(loc) && loc.length > 0 && typeof msg === "string") {
        const locParts = loc.filter((part) => typeof part === "string") as string[];
        const field = locParts[locParts.length - 1];
        if (field) {
          acc[field] = msg;
        }
      }
      return acc;
    }, {});
  }

  if (typeof detail === "string") {
    if (detail.toLowerCase().includes("passwords do not match")) {
      return { confirm_password: detail };
    }
    if (detail.toLowerCase().includes("terms") && detail.toLowerCase().includes("accept")) {
      return { terms_accepted: detail };
    }
    if (detail.toLowerCase().includes("company name")) {
      return { company_name: detail };
    }
  }

  return undefined;
}

async function parseRegisterError(response: Response): Promise<never> {
  let data: { detail?: unknown; error?: { message?: string; fields?: unknown } } | undefined;
  try {
    data = (await response.json()) as { detail?: unknown; error?: { message?: string; fields?: unknown } };
  } catch (err) {
    console.warn("Failed to parse register error response", err);
  }

  const status = response.status;
  const detail = data?.detail ?? data?.error?.message;
  let message = `Request failed with status ${status}`;
  if (status === 409) {
    message = "An account with this email already exists.";
  } else if (status === 429) {
    message = "Too many registration attempts. Please try again later.";
  } else if (status === 400 || status === 422) {
    message = "Please correct the highlighted fields.";
  } else if (typeof detail === "string") {
    message = detail;
  }

  const error = new Error(message) as RegisterApiError;
  error.status = status;
  error.fieldErrors =
    extractFieldErrors(data?.error?.fields) ??
    extractFieldErrors(detail);
  invalidateCsrfToken();
  throw error;
}

async function handleJson<T>(response: Response): Promise<T> {
  if (response.ok) {
    if (response.status === 204) {
      return undefined as T;
    }
    return (await response.json()) as T;
  }

  return parseError(response);
}

export type RegisterStep1Payload = {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  confirm_password: string;
  terms_accepted: boolean;
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

export type RegisterStep2Response = {
  access_token: string;
  refresh_token: string | null;
  expires_at: string | null;
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    role: UserRole;
    is_active: boolean;
    email_verified: boolean;
    company_name?: string | null;
    profile?: Record<string, unknown> | null;
  };
};

export type TokenResponse = {
  access_token: string;
  refresh_token?: string | null;
  expires_at?: string | null;
  token_type?: string;
  email_verified?: boolean;
};

export type SocialLoginResponse = TokenResponse & {
  email: string;
};

export type MeResponse = {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  is_active: boolean;
  email_verified: boolean;
};

export type GoogleLoginPayload = {
  id_token?: string;
  code?: string;
  redirect_uri?: string;
  recaptcha_token?: string | null;
};

export type LinkedInLoginPayload = {
  access_token?: string;
  code?: string;
  redirect_uri?: string;
  recaptcha_token?: string | null;
};

export type AnalyticsEventPayload = {
  event_type: string;
  step?: string | null;
  role?: UserRole | null;
  details?: Record<string, unknown>;
};

export type PasswordResetRequestPayload = {
  email: string;
};

export type PasswordResetResponse = {
  message: string;
};

export type CompletePasswordResetPayload = {
  token: string;
  password: string;
  confirm_password: string;
};

export async function registerStep1(
  payload: RegisterStep1Payload,
): Promise<RegisterStep1Response> {
  const csrfToken = await fetchCsrfToken();
  const response = await fetch(`${AUTH_BASE}/register/step1`, {
    method: "POST",
    headers: {
      ...defaultHeaders,
      [CSRF_HEADER]: csrfToken,
    },
    ...defaultFetchOptions,
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    return parseRegisterError(response);
  }

  return handleJson<RegisterStep1Response>(response);
}

export async function registerStep2(
  payload: RegisterStep2Payload,
  token: string,
): Promise<RegisterStep2Response> {
  const csrfToken = await fetchCsrfToken();
  const response = await fetch(`${AUTH_BASE}/register/step2`, {
    method: "POST",
    headers: {
      ...defaultHeaders,
      Authorization: `Bearer ${token}`,
      [CSRF_HEADER]: csrfToken,
    },
    ...defaultFetchOptions,
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    return parseRegisterError(response);
  }

  return handleJson<RegisterStep2Response>(response);
}

export async function login(
  email: string,
  password: string,
  recaptchaToken: string | null,
): Promise<TokenResponse> {
  const csrfToken = await fetchCsrfToken();
  const body: Record<string, unknown> = { email, password };
  if (recaptchaToken) {
    body.recaptcha_token = recaptchaToken;
  }
  const response = await fetch(`${AUTH_BASE}/login`, {
    method: "POST",
    headers: {
      ...defaultHeaders,
      [CSRF_HEADER]: csrfToken,
    },
    ...defaultFetchOptions,
    body: JSON.stringify(body),
  });

  return handleJson<TokenResponse>(response);
}

export async function loginWithGoogle(
  payload: GoogleLoginPayload,
): Promise<SocialLoginResponse> {
  const csrfToken = await fetchCsrfToken();
  const body: Record<string, unknown> = {};
  if (payload.id_token) body.id_token = payload.id_token;
  if (payload.code) body.code = payload.code;
  if (payload.redirect_uri) body.redirect_uri = payload.redirect_uri;
  if (payload.recaptcha_token) body.recaptcha_token = payload.recaptcha_token;

  const response = await fetch(`${AUTH_BASE}/login/google`, {
    method: "POST",
    headers: {
      ...defaultHeaders,
      [CSRF_HEADER]: csrfToken,
    },
    ...defaultFetchOptions,
    body: JSON.stringify(body),
  });

  return handleJson<SocialLoginResponse>(response);
}

export async function loginWithLinkedIn(
  payload: LinkedInLoginPayload,
): Promise<SocialLoginResponse> {
  const csrfToken = await fetchCsrfToken();
  const body: Record<string, unknown> = {};
  if (payload.access_token) body.access_token = payload.access_token;
  if (payload.code) body.code = payload.code;
  if (payload.redirect_uri) body.redirect_uri = payload.redirect_uri;
  if (payload.recaptcha_token) body.recaptcha_token = payload.recaptcha_token;

  const response = await fetch(`${AUTH_BASE}/login/linkedin`, {
    method: "POST",
    headers: {
      ...defaultHeaders,
      [CSRF_HEADER]: csrfToken,
    },
    ...defaultFetchOptions,
    body: JSON.stringify(body),
  });

  return handleJson<SocialLoginResponse>(response);
}

export async function getMe(): Promise<MeResponse> {
  const token = getStoredAccessToken();
  const response = await fetch(`${AUTH_BASE}/me`, {
    method: "GET",
    headers: {
      ...defaultHeaders,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...defaultFetchOptions,
  });
  if (response.ok) {
    return handleJson<MeResponse>(response);
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
    console.warn("Failed to parse /me error response", err);
  }
  const error = new Error(message) as Error & { status?: number };
  error.status = response.status;
  throw error;
}

export async function refreshSession(refreshToken: string): Promise<TokenResponse> {
  const response = await fetch(`${AUTH_BASE}/refresh`, {
    method: "POST",
    ...defaultFetchOptions,
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  return handleJson<TokenResponse>(response);
}

export async function trackAnalyticsEvent(payload: AnalyticsEventPayload): Promise<void> {
  try {
    const csrfToken = await fetchCsrfToken();
    const response = await fetch(`${AUTH_BASE}/analytics/track`, {
      method: "POST",
      headers: {
        ...defaultHeaders,
        [CSRF_HEADER]: csrfToken,
      },
      ...defaultFetchOptions,
      body: JSON.stringify(payload),
    });

    if (!response.ok && response.status !== 404) {
      await parseError(response);
    }
  } catch (err) {
    console.warn("Failed to track analytics event", err);
  }
}

export async function logout(): Promise<void> {
  const csrfToken = await fetchCsrfToken();
  const response = await fetch(`${AUTH_BASE}/logout`, {
    method: "POST",
    headers: {
      ...defaultHeaders,
      [CSRF_HEADER]: csrfToken,
    },
    ...defaultFetchOptions,
  });

  if (!response.ok && response.status !== 204) {
    await parseError(response);
  }
  invalidateCsrfToken();
}

export async function verifyEmail(token: string): Promise<void> {
  const url = `${AUTH_BASE}/verify?token=${encodeURIComponent(token)}`;
  const response = await fetch(url, {
    method: "GET",
    redirect: "manual" as RequestRedirect,
    credentials: "include",
  });

  if (response.status >= 200 && response.status < 300) {
    return;
  }
  if (response.status >= 300 && response.status < 400) {
    return;
  }
  await parseError(response);
}

export async function resendVerification(email: string): Promise<void> {
  const csrfToken = await fetchCsrfToken();
  const response = await fetch(`${AUTH_BASE}/verify/resend`, {
    method: "POST",
    headers: {
      ...defaultHeaders,
      [CSRF_HEADER]: csrfToken,
    },
    ...defaultFetchOptions,
    body: JSON.stringify({ email }),
  });

  if (!response.ok) {
    await parseError(response);
  }
}

export async function requestPasswordReset(email: string): Promise<PasswordResetResponse> {
  const csrfToken = await fetchCsrfToken();
  const response = await fetch(`${AUTH_BASE}/password/forgot`, {
    method: "POST",
    headers: {
      ...defaultHeaders,
      [CSRF_HEADER]: csrfToken,
    },
    ...defaultFetchOptions,
    body: JSON.stringify({ email }),
  });

  const data = await handleJson<PasswordResetResponse>(response);
  return data;
}

export async function completePasswordReset(
  payload: CompletePasswordResetPayload,
): Promise<PasswordResetResponse> {
  const csrfToken = await fetchCsrfToken();
  const response = await fetch(`${AUTH_BASE}/password/reset`, {
    method: "POST",
    headers: {
      ...defaultHeaders,
      [CSRF_HEADER]: csrfToken,
    },
    ...defaultFetchOptions,
    body: JSON.stringify(payload),
  });

  const data = await handleJson<PasswordResetResponse>(response);
  return data;
}

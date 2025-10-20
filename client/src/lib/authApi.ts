const API_BASE =
  ((import.meta as unknown as { env?: Record<string, string | undefined> }).env?.VITE_API_BASE as
    | string
    | undefined) ?? "/api";
const AUTH_BASE = `${API_BASE}/auth`;
const CSRF_HEADER = "X-CSRF-Token";

export type UserRole = "Customer" | "Developer";

let csrfTokenCache: string | null = null;

const defaultHeaders: Record<string, string> = {
  "Content-Type": "application/json",
};

const defaultFetchOptions: RequestInit = {
  credentials: "include",
};

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
    if (typeof data?.detail === "string") {
      message = data.detail;
    } else if (data?.detail) {
      message = JSON.stringify(data.detail);
    }
  } catch (err) {
    console.warn("Failed to parse error response", err);
  }

  invalidateCsrfToken();
  throw new Error(message);
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
};

export type SocialLoginResponse = TokenResponse & {
  email: string;
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

  const data = await handleJson<RegisterStep1Response>(response);
  return data;
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

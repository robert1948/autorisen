import { getConfig } from "../config";

type ApiFetchOptions = {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
  auth?: boolean;
  signal?: AbortSignal;
};

type ApiFetchError = Error & { status?: number };

const AUTH_STORAGE_KEY = "autorisen-auth";

function getApiBase(): string {
  const envBase = (import.meta as unknown as { env?: Record<string, string | undefined> }).env
    ?.VITE_API_BASE;
  if (envBase) {
    return envBase;
  }
  const config = getConfig();
  return config.API_BASE_URL || "/api";
}

function getStoredAccessToken(): string | null {
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
  const error = new Error(message) as ApiFetchError;
  error.status = response.status;
  throw error;
}

export async function apiFetch<T>(endpoint: string, options: ApiFetchOptions = {}): Promise<T> {
  const { method = "GET", body, headers = {}, auth = true, signal } = options;
  const requestHeaders: Record<string, string> = {
    ...headers,
  };

  if (body !== undefined) {
    requestHeaders["Content-Type"] = "application/json";
  }

  if (auth) {
    const token = getStoredAccessToken();
    if (token) {
      requestHeaders.Authorization = `Bearer ${token}`;
    }
  }

  const response = await fetch(`${getApiBase()}${endpoint}`, {
    method,
    headers: requestHeaders,
    credentials: "include",
    body: body !== undefined ? JSON.stringify(body) : undefined,
    signal,
  });

  if (!response.ok) {
    return parseError(response);
  }

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

import { createContext, ReactNode, useCallback, useContext, useEffect, useRef, useState } from "react";

import {
  getMe,
  login,
  loginWithGoogle as loginWithGoogleApi,
  loginWithLinkedIn as loginWithLinkedInApi,
  logout as logoutApi,
  refreshSession,
  setUnauthorizedHandler,
  type GoogleLoginPayload,
  type LinkedInLoginPayload,
  type MeResponse,
  type TokenResponse,
} from "../../lib/authApi";
import { setApiUnauthorizedHandler } from "../../lib/api";

export type AuthStatus = "unknown" | "authenticated" | "unauthenticated";

export type AuthUser = {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  profile: Record<string, unknown>;
  summary: Record<string, unknown>;
  developer?: Record<string, unknown>;
};

export type AuthState = {
  status: AuthStatus;
  accessToken: string | null;
  refreshToken: string | null;
  expiresAt: string | null;
  userEmail: string | null;
  isEmailVerified: boolean;
  user: AuthUser | null;
};

const AuthContext = createContext<{
  state: AuthState;
  loading: boolean;
  error: string | null;
  loginUser: (email: string, password: string, recaptchaToken: string | null) => Promise<void>;
  loginWithGoogle: (payload: GoogleLoginPayload) => Promise<void>;
  loginWithLinkedIn: (payload: LinkedInLoginPayload) => Promise<void>;
  setAuthFromTokens: (email: string, token: TokenResponse, emailVerified?: boolean) => void;
  markEmailVerified: () => void;
  logout: () => Promise<void>;
}>({
  state: {
    status: "unknown",
    accessToken: null,
    refreshToken: null,
    expiresAt: null,
    userEmail: null,
    isEmailVerified: false,
    user: null,
  },
  loading: false,
  error: null,
  loginUser: async () => undefined,
  loginWithGoogle: async () => undefined,
  loginWithLinkedIn: async () => undefined,
  setAuthFromTokens: () => undefined,
  markEmailVerified: () => undefined,
  logout: async () => undefined,
});

const STORAGE_KEY = "autorisen-auth";

const loadState = (): AuthState => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw)
      return {
        status: "unknown",
        accessToken: null,
        refreshToken: null,
        expiresAt: null,
        userEmail: null,
        isEmailVerified: false,
        user: null,
      };
    const parsed = JSON.parse(raw) as Partial<AuthState>;
    return {
      status: "unknown",
      accessToken: parsed.accessToken ?? null,
      refreshToken: parsed.refreshToken ?? null,
      expiresAt: parsed.expiresAt ?? null,
      userEmail: parsed.userEmail ?? null,
      isEmailVerified: parsed.isEmailVerified ?? false,
      user: null,
    };
  } catch (err) {
    console.warn("Failed to parse auth state", err);
    return {
      status: "unknown",
      accessToken: null,
      refreshToken: null,
      expiresAt: null,
      userEmail: null,
      isEmailVerified: false,
      user: null,
    };
  }
};

const saveState = (state: AuthState) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
};

const clearState = () => {
  localStorage.removeItem(STORAGE_KEY);
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [state, setState] = useState<AuthState>(loadState);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bootstrapped = useRef(false);

  const normalizeMe = useCallback((me: MeResponse): AuthUser => {
    const role = me.role ?? "";
    const roleNormalized = role.toLowerCase();
    return {
      id: me.id,
      email: me.email,
      first_name: me.first_name,
      last_name: me.last_name,
      role,
      profile: {},
      summary: {
        email: me.email,
        first_name: me.first_name,
        last_name: me.last_name,
        role,
      },
      developer: roleNormalized === "developer" ? {} : undefined,
    };
  }, []);

  const redirectToLogin = useCallback(() => {
    if (window.location.pathname !== "/auth/login") {
      window.location.assign("/auth/login");
    }
  }, []);

  const clearAuthState = useCallback(() => {
    setState({
      status: "unauthenticated",
      accessToken: null,
      refreshToken: null,
      expiresAt: null,
      userEmail: null,
      isEmailVerified: false,
      user: null,
    });
    clearState();
    localStorage.removeItem("autorisen-refresh-token");
  }, []);

  const fetchMeOnce = useCallback(async () => {
    if (bootstrapped.current) return;
    bootstrapped.current = true;
    setState((prev) => ({ ...prev, status: "unknown" }));
    try {
      const me = await getMe();
      setState((prev) => ({
        ...prev,
        status: "authenticated",
        userEmail: me.email ?? prev.userEmail,
        isEmailVerified: Boolean(me.email_verified),
        user: normalizeMe(me),
      }));
    } catch (err) {
      const status = (err as { status?: number }).status ?? 0;
      if (status === 401 || status === 403) {
        clearAuthState();
      } else {
        setState((prev) => ({ ...prev, status: "unauthenticated", user: null }));
      }
    }
  }, [clearAuthState, normalizeMe]);

  useEffect(() => {
    fetchMeOnce();
  }, [fetchMeOnce]);
  const setAuthFromTokens = (email: string, token: TokenResponse, emailVerified?: boolean) => {
    const resolvedVerified =
      typeof emailVerified === "boolean"
        ? emailVerified
        : typeof token.email_verified === "boolean"
        ? token.email_verified
        : state.isEmailVerified;
    const newState: AuthState = {
      status: "authenticated",
      accessToken: token.access_token,
      refreshToken: token.refresh_token ?? null,
      expiresAt: token.expires_at ?? null,
      userEmail: email,
      isEmailVerified: Boolean(resolvedVerified),
      user: state.user,
    };
    setState(newState);
    saveState(newState);
    if (token.refresh_token) {
      localStorage.setItem("autorisen-refresh-token", token.refresh_token);
    }
  };

  const loginUser = async (email: string, password: string, recaptchaToken: string | null) => {
    setLoading(true);
    setError(null);
    try {
      const resp = await login(email, password, recaptchaToken);
      setAuthFromTokens(email, resp, resp.email_verified ?? false);
      bootstrapped.current = false;
      await fetchMeOnce();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Login failed";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const loginWithGoogle = async (payload: GoogleLoginPayload) => {
    setLoading(true);
    setError(null);
    try {
      const resp = await loginWithGoogleApi(payload);
      setAuthFromTokens(resp.email, resp, resp.email_verified ?? true);
      bootstrapped.current = false;
      await fetchMeOnce();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Google login failed";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const loginWithLinkedIn = async (payload: LinkedInLoginPayload) => {
    setLoading(true);
    setError(null);
    try {
      const resp = await loginWithLinkedInApi(payload);
      setAuthFromTokens(resp.email, resp, resp.email_verified ?? true);
      bootstrapped.current = false;
      await fetchMeOnce();
    } catch (err) {
      const message = err instanceof Error ? err.message : "LinkedIn login failed";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const markEmailVerified = () => {
    setState((prev) => {
      const next: AuthState = {
        status: prev.status,
        accessToken: prev.accessToken,
        refreshToken: prev.refreshToken,
        expiresAt: prev.expiresAt,
        userEmail: prev.userEmail,
        isEmailVerified: true,
        user: prev.user,
      };
      saveState(next);
      return next;
    });
  };

  const refreshToken = async () => {
    const refreshValue =
      state.refreshToken || localStorage.getItem("autorisen-refresh-token");
    if (!refreshValue) {
      clearAuthState();
      redirectToLogin();
      return;
    }
    try {
      const resp = await refreshSession(refreshValue);
      setAuthFromTokens(state.userEmail ?? "", resp, state.isEmailVerified);
      bootstrapped.current = false;
      await fetchMeOnce();
    } catch (err) {
      console.warn("Failed to refresh token", err);
      clearAuthState();
      redirectToLogin();
    }
  };

  const logout = async () => {
    try {
      await logoutApi();
    } catch (err) {
      console.warn("Failed to call logout endpoint", err);
    } finally {
      clearAuthState();
      redirectToLogin();
    }
  };

  useEffect(() => {
    setUnauthorizedHandler(() => {
      clearAuthState();
      redirectToLogin();
    });
    setApiUnauthorizedHandler(() => {
      clearAuthState();
      redirectToLogin();
    });
    return () => {
      setUnauthorizedHandler(null);
      setApiUnauthorizedHandler(null);
    };
  }, [clearAuthState, redirectToLogin]);

  useEffect(() => {
    if (!state.accessToken || !state.expiresAt) return;
    const expireTime = new Date(state.expiresAt).getTime();
    const now = Date.now();
    const timeout = expireTime - now - 60 * 1000;
    if (timeout <= 0) {
      refreshToken();
      return;
    }
    const id = window.setTimeout(() => refreshToken(), timeout);
    return () => window.clearTimeout(id);
  }, [state.accessToken, state.expiresAt, state.refreshToken]);

  const value = {
    state,
    loading,
    error,
    loginUser,
    loginWithGoogle,
    loginWithLinkedIn,
    setAuthFromTokens,
    markEmailVerified,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
};

import { createContext, ReactNode, useContext, useEffect, useState } from "react";

import {
  login,
  loginWithGoogle as loginWithGoogleApi,
  loginWithLinkedIn as loginWithLinkedInApi,
  refreshSession,
  logout as logoutApi,
  type GoogleLoginPayload,
  type LinkedInLoginPayload,
  type TokenResponse,
} from "../../lib/authApi";

export type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  expiresAt: string | null;
  userEmail: string | null;
  isEmailVerified: boolean;
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
    accessToken: null,
    refreshToken: null,
    expiresAt: null,
    userEmail: null,
    isEmailVerified: false,
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
        accessToken: null,
        refreshToken: null,
        expiresAt: null,
        userEmail: null,
        isEmailVerified: false,
      };
    const parsed = JSON.parse(raw) as Partial<AuthState>;
    return {
      accessToken: parsed.accessToken ?? null,
      refreshToken: parsed.refreshToken ?? null,
      expiresAt: parsed.expiresAt ?? null,
      userEmail: parsed.userEmail ?? null,
      isEmailVerified: parsed.isEmailVerified ?? false,
    };
  } catch (err) {
    console.warn("Failed to parse auth state", err);
    return {
      accessToken: null,
      refreshToken: null,
      expiresAt: null,
      userEmail: null,
      isEmailVerified: false,
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

  useEffect(() => {
    if (!state.accessToken || !state.expiresAt) return;
    const expireDate = new Date(state.expiresAt);
    const now = new Date();
    if (expireDate <= now) {
      refreshToken().catch(() => logout());
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps
  const setAuthFromTokens = (email: string, token: TokenResponse, emailVerified?: boolean) => {
    const resolvedVerified =
      typeof emailVerified === "boolean"
        ? emailVerified
        : typeof token.email_verified === "boolean"
        ? token.email_verified
        : state.isEmailVerified;
    const newState: AuthState = {
      accessToken: token.access_token,
      refreshToken: token.refresh_token ?? null,
      expiresAt: token.expires_at ?? null,
      userEmail: email,
      isEmailVerified: Boolean(resolvedVerified),
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
    } catch (err) {
      const message = err instanceof Error ? err.message : "LinkedIn login failed";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const clearAuthState = () => {
    setState({
      accessToken: null,
      refreshToken: null,
      expiresAt: null,
      userEmail: null,
      isEmailVerified: false,
    });
    clearState();
    localStorage.removeItem("autorisen-refresh-token");
  };

  const markEmailVerified = () => {
    setState((prev) => {
      const next: AuthState = {
        accessToken: prev.accessToken,
        refreshToken: prev.refreshToken,
        expiresAt: prev.expiresAt,
        userEmail: prev.userEmail,
        isEmailVerified: true,
      };
      saveState(next);
      return next;
    });
  };

const redirectToLogin = () => {
  if (window.location.pathname !== "/auth/login") {
    window.location.assign("/auth/login");
  }
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

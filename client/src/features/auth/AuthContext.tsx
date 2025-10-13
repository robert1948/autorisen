import { createContext, ReactNode, useContext, useEffect, useState } from "react";

import { login, refreshSession, type TokenResponse } from "../../lib/authApi";

export type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  expiresAt: string | null;
  userEmail: string | null;
};

const AuthContext = createContext<{
  state: AuthState;
  loading: boolean;
  error: string | null;
  loginUser: (email: string, password: string) => Promise<void>;
  setAuthFromTokens: (email: string, token: TokenResponse) => void;
  logout: () => void;
}>({
  state: { accessToken: null, refreshToken: null, expiresAt: null, userEmail: null },
  loading: false,
  error: null,
  loginUser: async () => undefined,
  setAuthFromTokens: () => undefined,
  logout: () => undefined,
});

const STORAGE_KEY = "autorisen-auth";

const loadState = (): AuthState => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { accessToken: null, refreshToken: null, expiresAt: null, userEmail: null };
    const parsed = JSON.parse(raw) as AuthState;
    return parsed;
  } catch (err) {
    console.warn("Failed to parse auth state", err);
    return { accessToken: null, refreshToken: null, expiresAt: null, userEmail: null };
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
  const setAuthFromTokens = (email: string, token: TokenResponse) => {
    const newState: AuthState = {
      accessToken: token.access_token,
      refreshToken: token.refresh_token ?? null,
      expiresAt: token.expires_at ?? null,
      userEmail: email,
    };
    setState(newState);
    saveState(newState);
    if (token.refresh_token) {
      localStorage.setItem("autorisen-refresh-token", token.refresh_token);
    }
  };

  const loginUser = async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const resp = await login(email, password);
      setAuthFromTokens(email, resp);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Login failed";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const refreshToken = async () => {
    const refreshValue =
      state.refreshToken || localStorage.getItem("autorisen-refresh-token");
    if (!refreshValue) {
      logout();
      return;
    }
    try {
      const resp = await refreshSession(refreshValue);
      setAuthFromTokens(state.userEmail ?? "", resp);
    } catch (err) {
      console.warn("Failed to refresh token", err);
      logout();
    }
  };

  const logout = () => {
    setState({ accessToken: null, refreshToken: null, expiresAt: null, userEmail: null });
    clearState();
    localStorage.removeItem("autorisen-refresh-token");
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
    setAuthFromTokens,
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

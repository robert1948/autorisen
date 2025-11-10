import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { useChatKit, type ChatToken } from "../components/chat/ChatKitProvider";

type TokenMode = "initial" | "refresh";

type TokenState =
  | { loading: boolean; refreshing: boolean; token?: undefined; error?: string }
  | { loading: boolean; refreshing: boolean; token: ChatToken; error?: string };

export type UseChatSessionOptions = {
  placement: string;
  threadId?: string | null;
  enabled?: boolean;
  autoRefresh?: boolean;
};

export type StartSessionOptions = {
  threadId?: string | null;
  mode?: TokenMode;
};

const INITIAL_STATE: TokenState = { loading: false, refreshing: false, token: undefined };

export const useChatSession = ({
  placement,
  threadId,
  enabled = true,
  autoRefresh = true,
}: UseChatSessionOptions) => {
  const { requestToken } = useChatKit();
  const [state, setState] = useState<TokenState>(() =>
    enabled ? { loading: true, refreshing: false } : INITIAL_STATE,
  );
  const [expiryCountdown, setExpiryCountdown] = useState<number | null>(null);

  const activeThreadRef = useRef<string | undefined>(threadId ?? undefined);
  const countdownTimerRef = useRef<number | null>(null);
  const refreshTimerRef = useRef<number | null>(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      if (countdownTimerRef.current) {
        window.clearInterval(countdownTimerRef.current);
      }
      if (refreshTimerRef.current) {
        window.clearTimeout(refreshTimerRef.current);
      }
    };
  }, []);

  useEffect(() => {
    activeThreadRef.current = threadId ?? undefined;
  }, [threadId]);

  const runRequest = useCallback(
    async (mode: TokenMode = "initial", overrideThreadId?: string | null) => {
      if (!enabled) {
        return;
      }
      setState((prev) => ({
        token: mode === "refresh" ? prev.token : undefined,
        loading: mode === "initial",
        refreshing: mode === "refresh",
        error: undefined,
      }));
      try {
        const token = await requestToken(
          placement,
          overrideThreadId ?? activeThreadRef.current ?? undefined,
        );
        activeThreadRef.current = token.threadId;
        if (!mountedRef.current) {
          return;
        }
        setState({ loading: false, refreshing: false, token });
      } catch (err) {
        if (!mountedRef.current) {
          return;
        }
        const message =
          err instanceof Error ? err.message : "Unable to establish chat session.";
        setState((prev) => ({
          ...prev,
          loading: false,
          refreshing: false,
          error: message,
        }));
      }
    },
    [enabled, placement, requestToken],
  );

  const startSession = useCallback(
    (options?: StartSessionOptions) => {
      const mode = options?.mode ?? (options?.threadId ? "initial" : "refresh");
      return runRequest(mode, options?.threadId ?? null);
    },
    [runRequest],
  );

  useEffect(() => {
    if (!enabled) {
      setState(INITIAL_STATE);
      setExpiryCountdown(null);
      if (countdownTimerRef.current) {
        window.clearInterval(countdownTimerRef.current);
      }
      if (refreshTimerRef.current) {
        window.clearTimeout(refreshTimerRef.current);
      }
      return;
    }
    runRequest("initial", threadId ?? undefined);
  }, [enabled, placement, threadId, runRequest]);

  useEffect(() => {
    if (!state.token || !enabled) {
      setExpiryCountdown(null);
      if (countdownTimerRef.current) {
        window.clearInterval(countdownTimerRef.current);
        countdownTimerRef.current = null;
      }
      return;
    }
    if (countdownTimerRef.current) {
      window.clearInterval(countdownTimerRef.current);
    }
    const updateCountdown = () => {
      const expiresAt = new Date(state.token!.expiresAt).getTime();
      if (Number.isNaN(expiresAt)) {
        setExpiryCountdown(null);
        return;
      }
      const remaining = Math.max(0, Math.round((expiresAt - Date.now()) / 1000));
      setExpiryCountdown(remaining);
    };
    updateCountdown();
    countdownTimerRef.current = window.setInterval(updateCountdown, 1000);
    return () => {
      if (countdownTimerRef.current) {
        window.clearInterval(countdownTimerRef.current);
        countdownTimerRef.current = null;
      }
    };
  }, [state.token, enabled]);

  useEffect(() => {
    if (!autoRefresh || !enabled || !state.token) {
      if (refreshTimerRef.current) {
        window.clearTimeout(refreshTimerRef.current);
        refreshTimerRef.current = null;
      }
      return;
    }
    if (refreshTimerRef.current) {
      window.clearTimeout(refreshTimerRef.current);
    }
    const expiresAt = new Date(state.token.expiresAt).getTime();
    if (Number.isNaN(expiresAt)) {
      return undefined;
    }
    const bufferMs = 45_000;
    const delay = Math.max(5_000, expiresAt - Date.now() - bufferMs);
    refreshTimerRef.current = window.setTimeout(() => {
      void runRequest("refresh");
    }, delay);
    return () => {
      if (refreshTimerRef.current) {
        window.clearTimeout(refreshTimerRef.current);
        refreshTimerRef.current = null;
      }
    };
  }, [autoRefresh, enabled, state.token, runRequest]);

  const value = useMemo(
    () => ({
      token: state.token,
      loading: state.loading,
      refreshing: state.refreshing,
      error: state.error,
      expiryCountdown,
      startSession,
    }),
    [state, expiryCountdown, startSession],
  );

  return value;
};

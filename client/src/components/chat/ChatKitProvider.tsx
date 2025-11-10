import React, { createContext, useContext, useMemo } from "react";

/** === Feature flag ===
 * Set VITE_ENABLE_CHATKIT=false to park ChatKit without touching the rest of the app.
 */
const CHATKIT_ENABLED = import.meta.env.VITE_ENABLE_CHATKIT === "true";
const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

/** Token shape returned by the backend token endpoint */
export type ChatToken = {
  token: string;
  placement: string;
  threadId: string;
  expiresAt: string;
  allowedTools: string[];
};

/** Context contract used by Chat UI pieces */
type ChatKitContextValue = {
  /** Requests a short-lived ChatKit token bundle from the backend */
  requestToken: (placement: string, threadId?: string | null) => Promise<ChatToken>;
};

const ChatKitContext = createContext<ChatKitContextValue | undefined>(
  undefined
);

type Props = { children: React.ReactNode };

/**
 * Provider that exposes requestToken(). When ChatKit is disabled, it becomes a no-op
 * pass-through so the rest of the app renders without network calls or errors.
 */
export const ChatKitProvider = ({ children }: Props) => {
  // Disabled → return a stubbed provider (no network calls)
  if (!CHATKIT_ENABLED) {
    const value = useMemo<ChatKitContextValue>(() => {
      return {
        requestToken: async () =>
          ({
            token: "",
            placement: "disabled",
            threadId: "",
            expiresAt: new Date().toISOString(),
            allowedTools: [],
          }) as ChatToken,
      };
    }, []);
    return (
      <ChatKitContext.Provider value={value}>
        {children}
      </ChatKitContext.Provider>
    );
  }

  // Enabled → real implementation
  const value = useMemo<ChatKitContextValue>(
    () => {
      const buildUrl = (placement: string, threadId?: string | null) => {
        if (!placement) {
          throw new Error("ChatKit placement is required.");
        }
        const params = new URLSearchParams({ placement });
        if (threadId) {
          params.set("thread_id", threadId);
        }
        return `${API_BASE}/chatkit/token?${params.toString()}`;
      };

      return {
        requestToken: async (placement: string, threadId?: string | null) => {
          const res = await fetch(buildUrl(placement, threadId), {
            method: "GET",
            credentials: "include",
          });

          if (!res.ok) {
            const detail = await res.text().catch(() => "");
            throw new Error(
              `Failed to fetch ChatKit token (HTTP ${res.status})${
                detail ? `: ${detail}` : ""
              }`
            );
          }
          const data = (await res.json()) as {
            token: string;
            placement: string;
            thread_id: string;
            expires_at: string;
            allowed_tools?: string[];
          };
          if (!data?.token || !data.thread_id) {
            throw new Error("ChatKit token response missing fields.");
          }
          return {
            token: data.token,
            placement: data.placement,
            threadId: data.thread_id,
            expiresAt: data.expires_at,
            allowedTools: data.allowed_tools ?? [],
          };
        },
      };
    },
    []
  );

  return (
    <ChatKitContext.Provider value={value}>{children}</ChatKitContext.Provider>
  );
};

/**
 * Hook to access ChatKit. When disabled, returns a stub with a no-op requestToken()
 * so callers can still call it safely.
 */
export const useChatKit = () => {
  const ctx = useContext(ChatKitContext);

  // If the provider wasn't mounted (shouldn't happen with our export), make a safe fallback:
  if (!ctx) {
    return {
      requestToken: async () =>
        ({
          token: "",
          placement: "no-provider",
          threadId: "",
          expiresAt: new Date().toISOString(),
          allowedTools: [],
        }) as ChatToken,
    } as ChatKitContextValue;
  }
  return ctx;
};

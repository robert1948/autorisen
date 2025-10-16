import React, { createContext, useContext, useMemo } from "react";

/** === Feature flag ===
 * Set VITE_ENABLE_CHATKIT=false to park ChatKit without touching the rest of the app.
 */
const CHATKIT_ENABLED = import.meta.env.VITE_ENABLE_CHATKIT === "true";
const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

/** Token shape returned by the backend token endpoint */
export type ChatToken = {
  client_secret: string;
  placement?: string;
};

/** Context contract used by Chat UI pieces */
type ChatKitContextValue = {
  /** Requests a short-lived client_secret from the backend */
  requestToken: (placement?: string) => Promise<ChatToken>;
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
    const value = useMemo<ChatKitContextValue>(
      () => ({
        requestToken: async () => {
          // Return an empty token so any optional callers don't explode.
          return { client_secret: "", placement: "disabled" };
        },
      }),
      []
    );
    return (
      <ChatKitContext.Provider value={value}>
        {children}
      </ChatKitContext.Provider>
    );
  }

  // Enabled → real implementation
  const value = useMemo<ChatKitContextValue>(
    () => ({
      requestToken: async (placement?: string) => {
        // If your app requires auth before getting a token, you can check for it here.
        const res = await fetch(`${API_BASE}/chatkit/token`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ placement }),
          credentials: "include",
        });

        if (!res.ok) {
          // Surface a concise error to the UI/console but don't crash the whole app.
          const detail = await res.text().catch(() => "");
          throw new Error(
            `Failed to fetch ChatKit token (HTTP ${res.status})${
              detail ? `: ${detail}` : ""
            }`
          );
        }
        const data = (await res.json()) as ChatToken;
        if (!data?.client_secret) {
          throw new Error("ChatKit token response missing client_secret.");
        }
        return data;
      },
    }),
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
        ({ client_secret: "", placement: "no-provider" } as ChatToken),
    } as ChatKitContextValue;
  }
  return ctx;
};

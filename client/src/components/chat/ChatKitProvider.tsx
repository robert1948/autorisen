import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useMemo,
} from "react";

const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined) ?? "/api";

export type ChatToken = {
  token: string;
  expiresAt: string;
  threadId: string;
  placement: string;
  allowedTools: string[];
};

type ChatKitContextValue = {
  requestToken: (placement: string, threadId?: string) => Promise<ChatToken>;
};

const ChatKitContext = createContext<ChatKitContextValue | undefined>(
  undefined,
);

type Props = {
  children: ReactNode;
};

export const ChatKitProvider = ({ children }: Props) => {
  const requestToken = useCallback(
    async (placement: string, threadId?: string) => {
      const response = await fetch(`${API_BASE}/chatkit/token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ placement, thread_id: threadId }),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch ChatKit token (HTTP ${response.status})`);
      }

      const data = await response.json();

      return {
        token: data.token as string,
        expiresAt: data.expires_at as string,
        threadId: data.thread_id as string,
        placement: data.placement as string,
        allowedTools: (data.allowed_tools as string[]) ?? [],
      };
    },
    [],
  );

  const value = useMemo<ChatKitContextValue>(
    () => ({
      requestToken,
    }),
    [requestToken],
  );

  return (
    <ChatKitContext.Provider value={value}>{children}</ChatKitContext.Provider>
  );
};

export const useChatKit = () => {
  const ctx = useContext(ChatKitContext);
  if (!ctx) {
    throw new Error("useChatKit must be used within a ChatKitProvider");
  }
  return ctx;
};

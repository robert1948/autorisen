export type ChatRole = "user" | "assistant" | "system" | "tool";

export type ChatThreadContext = Record<string, unknown> | null;

export type ChatThreadStatus = "active" | "archived" | "closed" | string;

export type ChatThread = {
  id: string;
  placement: string;
  title?: string | null;
  status?: ChatThreadStatus;
  context?: ChatThreadContext;
  createdAt: string;
  updatedAt: string;
  lastEventAt?: string | null;
  metadata?: Record<string, unknown> | null;
};

export type ChatMessage = {
  id: string;
  threadId: string;
  role: ChatRole;
  content: string;
  createdAt: string;
  toolName?: string | null;
  eventMetadata?: Record<string, unknown> | null;
};

export type MessageStatus = "sending" | "sent" | "error";

export type ClientMessage = ChatMessage & {
  /** Unique client-side identifier used for optimistic updates */
  clientId?: string;
  status?: MessageStatus;
  error?: string | null;
};

export type CreateThreadPayload = {
  placement: string;
  title?: string;
  context?: ChatThreadContext;
};

export type SendMessagePayload = {
  content: string;
  role?: Exclude<ChatRole, "assistant">;
  metadata?: Record<string, unknown>;
  toolName?: string | null;
};

export type ChatSocketEnvelope =
  | {
      type: "chat.event";
      event: ChatMessage;
    }
  | {
      type: "thread.updated";
      thread: ChatThread;
    }
  | {
      type: "pong" | "ping";
      timestamp?: string;
    }
  | {
      type: "error";
      message: string;
    }
  | Record<string, unknown>;

export type SocketStatus = "idle" | "connecting" | "open" | "closed" | "error";

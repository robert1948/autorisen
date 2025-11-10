import type { ChatThreadResponse, ChatEventResponse } from "./chatApi";
import { chatApi } from "./chatApi";
import type { ChatMessage, ChatSocketEnvelope, ChatThread, SocketStatus } from "../types/chat";

export type WebSocketClientOptions = {
  threadId: string;
  token?: string;
  urlOverride?: string;
  reconnect?: boolean;
  maxRetries?: number;
  onMessage?: (payload: ChatSocketEnvelope) => void;
  onEvent?: (message: ChatMessage) => void;
  onThreadUpdate?: (thread: ChatThread) => void;
  onStatusChange?: (status: SocketStatus) => void;
};

export type WebSocketClient = {
  connect: () => void;
  close: () => void;
  send: (payload: unknown) => void;
};

const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined) ??
  ((import.meta as unknown as { env?: Record<string, string | undefined> }).env?.VITE_API_BASE ??
    "/api");

const CHAT_WS_URL = import.meta.env.VITE_CHAT_WS_URL as string | undefined;

const toAbsoluteHttpBase = (base: string): string => {
  if (base.startsWith("http://") || base.startsWith("https://") || base.startsWith("ws")) {
    return base.replace(/\/$/, "");
  }
  if (typeof window !== "undefined" && window.location) {
    const prefix = base.startsWith("/") ? "" : "/";
    return `${window.location.origin}${prefix}${base.replace(/^\//, "")}`.replace(/\/$/, "");
  }
  return `http://localhost${base.startsWith("/") ? "" : "/"}${base.replace(/^\//, "")}`.replace(
    /\/$/,
    "",
  );
};

const httpToWs = (base: string): string => {
  if (base.startsWith("ws://") || base.startsWith("wss://")) {
    return base;
  }
  if (base.startsWith("https://")) {
    return `wss://${base.slice("https://".length)}`;
  }
  if (base.startsWith("http://")) {
    return `ws://${base.slice("http://".length)}`;
  }
  return base;
};

export const buildWebSocketUrl = (threadId: string, token?: string, override?: string) => {
  const root = override ?? CHAT_WS_URL ?? toAbsoluteHttpBase(API_BASE);
  const wsBase = httpToWs(root).replace(/\/$/, "");
  const url = `${wsBase}/chat/ws`;
  const search = new URLSearchParams({ thread_id: threadId });
  if (token) {
    search.set("token", token);
  }
  return `${url}?${search.toString()}`;
};

const parseEnvelope = (raw: string): ChatSocketEnvelope | null => {
  try {
    return JSON.parse(raw) as ChatSocketEnvelope;
  } catch (err) {
    console.warn("Failed to parse chat WebSocket payload", err);
    return null;
  }
};

const mapThread = (thread: ChatThreadResponse | ChatThread): ChatThread => {
  if ("createdAt" in thread) {
    return thread as ChatThread;
  }
  return chatApi.toThread(thread as ChatThreadResponse);
};

const mapEvent = (event: ChatEventResponse | ChatMessage): ChatMessage => {
  if ("createdAt" in event) {
    return event as ChatMessage;
  }
  return chatApi.toMessage(event as ChatEventResponse);
};

export const createWebSocketClient = (options: WebSocketClientOptions): WebSocketClient => {
  let socket: WebSocket | null = null;
  let retries = 0;
  let closedManually = false;

  const maxRetries = options.maxRetries ?? 3;
  const shouldReconnect = options.reconnect !== false;

  const notifyStatus = (status: SocketStatus) => {
    options.onStatusChange?.(status);
  };

  const connect = () => {
    if (closedManually) {
      return;
    }
    notifyStatus("connecting");
    const url = buildWebSocketUrl(options.threadId, options.token, options.urlOverride);
    socket = new WebSocket(url);
    socket.onopen = () => {
      retries = 0;
      notifyStatus("open");
    };
    socket.onerror = () => {
      notifyStatus("error");
    };
    socket.onmessage = (event) => {
      const envelope = parseEnvelope(event.data as string);
      if (!envelope) return;
      options.onMessage?.(envelope);
      if (envelope.type === "chat.event" && envelope.event) {
        options.onEvent?.(mapEvent(envelope.event));
      } else if (envelope.type === "thread.updated" && envelope.thread) {
        options.onThreadUpdate?.(mapThread(envelope.thread));
      }
    };
    socket.onclose = () => {
      notifyStatus("closed");
      if (!closedManually && shouldReconnect && retries < maxRetries) {
        retries += 1;
        const backoff = Math.min(10_000, 500 * 2 ** retries);
        window.setTimeout(connect, backoff);
      } else if (!closedManually && retries >= maxRetries) {
        notifyStatus("error");
      }
    };
  };

  const close = () => {
    closedManually = true;
    if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
      socket.close();
    }
    notifyStatus("closed");
  };

  const send = (payload: unknown) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      throw new Error("Chat WebSocket is not connected.");
    }
    socket.send(JSON.stringify(payload));
  };

  return {
    connect,
    close,
    send,
  };
};

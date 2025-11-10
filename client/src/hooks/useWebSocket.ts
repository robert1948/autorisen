import { useCallback, useEffect, useRef, useState } from "react";

import type { ChatMessage, ChatThread, SocketStatus } from "../types/chat";
import {
  createWebSocketClient,
  type WebSocketClient,
  type WebSocketClientOptions,
} from "../services/websocket";
import { useEnhancedWebSocket } from "./useEnhancedWebSocket";

export type UseChatWebSocketOptions = Omit<
  WebSocketClientOptions,
  "onMessage" | "onEvent" | "onThreadUpdate" | "onStatusChange" | "threadId" | "token"
> & {
  threadId?: string | null;
  token?: string | null;
  enabled?: boolean;
  onEvent?: (event: ChatMessage) => void;
  onThreadUpdate?: (thread: ChatThread) => void;
  useEnhanced?: boolean; // New option to enable enhanced features
};

export const useChatWebSocket = ({
  threadId,
  token,
  enabled = true,
  onEvent,
  onThreadUpdate,
  reconnect,
  maxRetries,
  urlOverride,
  useEnhanced = true, // Default to enhanced version
}: UseChatWebSocketOptions) => {
  // Use enhanced WebSocket if enabled
  if (useEnhanced) {
    const enhancedResult = useEnhancedWebSocket({
      threadId,
      token,
      enabled,
      onEvent,
      onThreadUpdate,
      autoReconnect: reconnect !== false,
      maxReconnectAttempts: maxRetries || 3,
    });

    return {
      status: enhancedResult.connectionHealth.status,
      send: enhancedResult.send,
      disconnect: async () => {
        // Enhanced client handles disconnect via destroy
      },
      isConnected: enhancedResult.isConnected,
      // Additional enhanced features
      connectionHealth: enhancedResult.connectionHealth,
      loadingState: enhancedResult.loadingState,
      errors: enhancedResult.errors,
      metrics: enhancedResult.metrics,
      reconnect: enhancedResult.reconnect,
      clearErrors: enhancedResult.clearErrors,
    };
  }

  // Legacy WebSocket implementation (fallback)
  const [status, setStatus] = useState<SocketStatus>("idle");
  const clientRef = useRef<WebSocketClient | null>(null);
  const eventHandlerRef = useRef<typeof onEvent>();
  const threadHandlerRef = useRef<typeof onThreadUpdate>();

  useEffect(() => {
    eventHandlerRef.current = onEvent;
  }, [onEvent]);

  useEffect(() => {
    threadHandlerRef.current = onThreadUpdate;
  }, [onThreadUpdate]);

  useEffect(() => {
    if (!enabled || !threadId) {
      if (clientRef.current) {
        clientRef.current.close();
        clientRef.current = null;
      }
      setStatus("idle");
      return;
    }
    const client = createWebSocketClient({
      threadId,
      token: token ?? undefined,
      reconnect,
      maxRetries,
      urlOverride,
      onStatusChange: (nextStatus) => setStatus(nextStatus),
      onEvent: (event) => {
        eventHandlerRef.current?.(event);
      },
      onThreadUpdate: (thread) => {
        threadHandlerRef.current?.(thread);
      },
    });
    clientRef.current = client;
    client.connect();
    return () => {
      client.close();
      clientRef.current = null;
    };
  }, [enabled, threadId, token, reconnect, maxRetries, urlOverride]);

  const send = useCallback((payload: unknown) => {
    if (!clientRef.current) {
      throw new Error("Chat WebSocket is not connected.");
    }
    clientRef.current.send(payload);
  }, []);

  const disconnect = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.close();
      clientRef.current = null;
    }
  }, []);

  return {
    status,
    send,
    disconnect,
    isConnected: status === "open",
  };
};

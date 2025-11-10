/**
 * Enhanced WebSocket hook with comprehensive connection management,
 * health monitoring, error handling, and message queuing
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import type {
  ConnectionHealth,
  ErrorState,
  LoadingState,
  ConnectionMetrics,
  EnhancedWebSocketClient,
  MessageSendOptions,
  WebSocketHookResult
} from '../types/websocket';
import type { ChatMessage, ChatThread, ChatSocketEnvelope } from '../types/chat';
import { createEnhancedWebSocketClient } from '../services/enhancedWebSocket';
import { buildWebSocketUrl } from '../services/websocket';

export interface UseEnhancedWebSocketOptions {
  threadId?: string | null;
  token?: string | null;
  enabled?: boolean;
  onEvent?: (event: ChatMessage) => void;
  onThreadUpdate?: (thread: ChatThread) => void;
  onConnectionChange?: (health: ConnectionHealth) => void;
  onError?: (error: ErrorState) => void;
  autoReconnect?: boolean;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
  messageTimeout?: number;
}

export const useEnhancedWebSocket = (options: UseEnhancedWebSocketOptions): WebSocketHookResult => {
  const {
    threadId,
    token,
    enabled = true,
    onEvent,
    onThreadUpdate,
    onConnectionChange,
    onError,
    autoReconnect = true,
    maxReconnectAttempts = 5,
    heartbeatInterval = 30000,
    messageTimeout = 10000
  } = options;

  // State
  const [connectionHealth, setConnectionHealth] = useState<ConnectionHealth>({
    status: 'idle',
    lastPing: 0,
    lastPong: 0,
    reconnectAttempts: 0,
    latency: 0,
    isHealthy: false,
    connectionQuality: 'critical'
  });

  const [loadingState, setLoadingState] = useState<LoadingState>({
    connecting: false,
    sendingMessage: false,
    loadingHistory: false,
    reconnecting: false,
    authenticating: false
  });

  const [errors, setErrors] = useState<ErrorState[]>([]);
  const [metrics, setMetrics] = useState<ConnectionMetrics>({
    totalConnections: 0,
    totalReconnections: 0,
    totalMessagesSent: 0,
    totalMessagesReceived: 0,
    totalErrors: 0,
    averageLatency: 0,
    uptime: 0
  });
  const [queueLength, setQueueLength] = useState(0);

  // Refs
  const clientRef = useRef<EnhancedWebSocketClient | null>(null);
  const eventHandlerRef = useRef(onEvent);
  const threadHandlerRef = useRef(onThreadUpdate);
  const connectionHandlerRef = useRef(onConnectionChange);
  const errorHandlerRef = useRef(onError);

  // Update handler refs when props change
  useEffect(() => {
    eventHandlerRef.current = onEvent;
  }, [onEvent]);

  useEffect(() => {
    threadHandlerRef.current = onThreadUpdate;
  }, [onThreadUpdate]);

  useEffect(() => {
    connectionHandlerRef.current = onConnectionChange;
  }, [onConnectionChange]);

  useEffect(() => {
    errorHandlerRef.current = onError;
  }, [onError]);

  // Message handler
  const handleMessage = useCallback((envelope: ChatSocketEnvelope) => {
    if (envelope.type === 'chat.event' && 'event' in envelope && envelope.event) {
      eventHandlerRef.current?.(envelope.event as ChatMessage);
    } else if (envelope.type === 'thread.updated' && 'thread' in envelope && envelope.thread) {
      threadHandlerRef.current?.(envelope.thread as ChatThread);
    }
  }, []);

  // Connection effect
  useEffect(() => {
    if (!enabled || !threadId) {
      if (clientRef.current) {
        clientRef.current.destroy();
        clientRef.current = null;
      }
      setConnectionHealth(prev => ({ ...prev, status: 'idle' }));
      return;
    }

    // Create enhanced WebSocket client
    const client = createEnhancedWebSocketClient(
      {
        url: buildWebSocketUrl(threadId, token || undefined),
        reconnectInterval: 1000,
        maxReconnectAttempts,
        heartbeatInterval,
        messageTimeout,
        connectionTimeout: 5000,
        maxQueueSize: 100,
        enableHeartbeat: true,
        enableMessageQueue: true,
        retryBackoffStrategy: 'exponential',
        maxRetryDelay: 30000
      },
      handleMessage
    );

    // Set up event listeners
    client.on('onConnectionChange', (health) => {
      setConnectionHealth(health);
      connectionHandlerRef.current?.(health);
    });

    client.on('onError', (error) => {
      setErrors(prev => [...prev, error]);
      errorHandlerRef.current?.(error);
    });

    client.on('onLoadingChange', setLoadingState);
    client.on('onMetricsUpdate', setMetrics);
    client.on('onQueueChange', setQueueLength);

    clientRef.current = client;

    // Connect
    client.connect().catch((error) => {
      console.error('Failed to connect WebSocket:', error);
    });

    // Cleanup
    return () => {
      client.destroy();
    };
  }, [enabled, threadId, token, maxReconnectAttempts, heartbeatInterval, messageTimeout, handleMessage]);

  // Actions
  const send = useCallback(async (payload: unknown, options?: MessageSendOptions): Promise<void> => {
    if (!clientRef.current) {
      throw new Error('WebSocket client not initialized');
    }
    
    return clientRef.current.send(payload, options);
  }, []);

  const reconnect = useCallback(async (): Promise<void> => {
    if (!clientRef.current) {
      throw new Error('WebSocket client not initialized');
    }
    
    return clientRef.current.reconnect();
  }, []);

  const clearErrors = useCallback(() => {
    setErrors([]);
    clientRef.current?.clearErrors();
  }, []);

  // Convenience state
  const isConnected = connectionHealth.status === 'open';
  const isConnecting = loadingState.connecting;
  const isReconnecting = loadingState.reconnecting;
  const hasErrors = errors.length > 0;

  return {
    // State
    connectionHealth,
    loadingState,
    errors,
    metrics,
    
    // Actions
    send,
    reconnect,
    clearErrors,
    
    // Convenience state
    isConnected,
    isConnecting,
    isReconnecting,
    hasErrors,
    queueLength
  };
};

// Legacy hook compatibility
export const useChatWebSocket = useEnhancedWebSocket;
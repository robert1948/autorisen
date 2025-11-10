/**
 * Enhanced WebSocket connection management types
 * Provides comprehensive connection health monitoring, error handling, and message queuing
 */

import type { SocketStatus } from './chat';

export interface ConnectionHealth {
  status: SocketStatus;
  lastPing: number;
  lastPong: number;
  reconnectAttempts: number;
  latency: number;
  isHealthy: boolean;
  connectionQuality: 'excellent' | 'good' | 'poor' | 'critical';
}

export interface ErrorState {
  type: 'connection' | 'message' | 'auth' | 'rate_limit' | 'timeout' | 'network';
  message: string;
  timestamp: number;
  recoverable: boolean;
  retryable: boolean;
  errorCode?: string | number;
  details?: Record<string, unknown>;
}

export interface LoadingState {
  connecting: boolean;
  sendingMessage: boolean;
  loadingHistory: boolean;
  reconnecting: boolean;
  authenticating: boolean;
}

export interface QueuedMessage {
  id: string;
  payload: unknown;
  timestamp: number;
  attempts: number;
  maxAttempts: number;
  priority: 'high' | 'normal' | 'low';
  onSuccess?: () => void;
  onError?: (error: ErrorState) => void;
}

export interface WebSocketConfig {
  url: string;
  protocols?: string[];
  reconnectInterval: number;
  maxReconnectAttempts: number;
  heartbeatInterval: number;
  messageTimeout: number;
  connectionTimeout: number;
  maxQueueSize: number;
  enableHeartbeat: boolean;
  enableMessageQueue: boolean;
  retryBackoffStrategy: 'linear' | 'exponential' | 'fibonacci';
  maxRetryDelay: number;
}

export interface ConnectionMetrics {
  totalConnections: number;
  totalReconnections: number;
  totalMessagesSent: number;
  totalMessagesReceived: number;
  totalErrors: number;
  averageLatency: number;
  uptime: number;
  lastConnected?: Date;
  lastDisconnected?: Date;
}

export interface WebSocketClientEvents {
  onConnectionChange: (health: ConnectionHealth) => void;
  onError: (error: ErrorState) => void;
  onLoadingChange: (loading: LoadingState) => void;
  onMetricsUpdate: (metrics: ConnectionMetrics) => void;
  onQueueChange: (queueLength: number) => void;
}

export interface EnhancedWebSocketClient {
  // Connection management
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  reconnect(): Promise<void>;
  
  // Message handling
  send(payload: unknown, options?: MessageSendOptions): Promise<void>;
  sendWithRetry(payload: unknown, maxAttempts?: number): Promise<void>;
  
  // Health monitoring
  getConnectionHealth(): ConnectionHealth;
  getMetrics(): ConnectionMetrics;
  getQueueStatus(): { length: number; messages: QueuedMessage[] };
  
  // Error recovery
  clearErrors(): void;
  retryFailedMessages(): Promise<void>;
  clearMessageQueue(): void;
  
  // State queries
  isConnected(): boolean;
  isConnecting(): boolean;
  hasErrors(): boolean;
  
  // Event handling
  on<K extends keyof WebSocketClientEvents>(event: K, listener: WebSocketClientEvents[K]): void;
  off<K extends keyof WebSocketClientEvents>(event: K, listener: WebSocketClientEvents[K]): void;
  
  // Cleanup
  destroy(): void;
}

export interface MessageSendOptions {
  priority?: QueuedMessage['priority'];
  timeout?: number;
  maxRetries?: number;
  onSuccess?: () => void;
  onError?: (error: ErrorState) => void;
}

export interface WebSocketHookResult {
  // Connection state
  connectionHealth: ConnectionHealth;
  loadingState: LoadingState;
  errors: ErrorState[];
  metrics: ConnectionMetrics;
  
  // Actions
  send: (payload: unknown, options?: MessageSendOptions) => Promise<void>;
  reconnect: () => Promise<void>;
  clearErrors: () => void;
  
  // Convenience state
  isConnected: boolean;
  isConnecting: boolean;
  isReconnecting: boolean;
  hasErrors: boolean;
  queueLength: number;
}

// Constants
export const DEFAULT_WEBSOCKET_CONFIG: WebSocketConfig = {
  url: '',
  reconnectInterval: 1000,
  maxReconnectAttempts: 5,
  heartbeatInterval: 30000,
  messageTimeout: 10000,
  connectionTimeout: 5000,
  maxQueueSize: 100,
  enableHeartbeat: true,
  enableMessageQueue: true,
  retryBackoffStrategy: 'exponential',
  maxRetryDelay: 30000,
};

export const CONNECTION_QUALITY_THRESHOLDS = {
  excellent: { latency: 100, uptime: 0.99 },
  good: { latency: 300, uptime: 0.95 },
  poor: { latency: 1000, uptime: 0.90 },
  critical: { latency: Infinity, uptime: 0 },
} as const;
/**
 * Enhanced WebSocket service with connection health monitoring,
 * automatic reconnection, message queuing, and comprehensive error handling
 */

import type {
  ConnectionHealth,
  ErrorState,
  LoadingState,
  QueuedMessage,
  WebSocketConfig,
  ConnectionMetrics,
  EnhancedWebSocketClient,
  WebSocketClientEvents,
  MessageSendOptions,
  CONNECTION_QUALITY_THRESHOLDS
} from '../types/websocket';
import { DEFAULT_WEBSOCKET_CONFIG } from '../types/websocket';
import type { ChatSocketEnvelope, SocketStatus } from '../types/chat';

export class EnhancedWebSocketService implements EnhancedWebSocketClient {
  private config: WebSocketConfig;
  private socket: WebSocket | null = null;
  private eventListeners: Partial<WebSocketClientEvents> = {};
  
  // State management
  private connectionHealth: ConnectionHealth;
  private loadingState: LoadingState;
  private errors: ErrorState[] = [];
  private metrics: ConnectionMetrics;
  private messageQueue: QueuedMessage[] = [];
  
  // Timers and intervals
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private pingTimer: NodeJS.Timeout | null = null;
  
  // Internal state
  private isDestroyed = false;
  private manualDisconnect = false;
  private lastPingTime = 0;
  private connectionStartTime = 0;

  constructor(
    config: Partial<WebSocketConfig>,
    private onMessage?: (envelope: ChatSocketEnvelope) => void
  ) {
    this.config = { ...DEFAULT_WEBSOCKET_CONFIG, ...config };
    
    this.connectionHealth = {
      status: 'idle',
      lastPing: 0,
      lastPong: 0,
      reconnectAttempts: 0,
      latency: 0,
      isHealthy: false,
      connectionQuality: 'critical'
    };
    
    this.loadingState = {
      connecting: false,
      sendingMessage: false,
      loadingHistory: false,
      reconnecting: false,
      authenticating: false
    };
    
    this.metrics = {
      totalConnections: 0,
      totalReconnections: 0,
      totalMessagesSent: 0,
      totalMessagesReceived: 0,
      totalErrors: 0,
      averageLatency: 0,
      uptime: 0
    };
  }

  // Public API Implementation
  async connect(): Promise<void> {
    if (this.isDestroyed) {
      throw new Error('WebSocket client has been destroyed');
    }

    if (this.socket?.readyState === WebSocket.OPEN) {
      return;
    }

    this.manualDisconnect = false;
    this.updateLoadingState({ connecting: true });
    
    try {
      await this.establishConnection();
    } catch (error) {
      this.handleConnectionError(error);
      throw error;
    }
  }

  async disconnect(): Promise<void> {
    this.manualDisconnect = true;
    this.updateLoadingState({ connecting: false, reconnecting: false });
    this.clearTimers();
    
    if (this.socket) {
      this.socket.close(1000, 'Manual disconnect');
      this.socket = null;
    }
    
    this.updateConnectionHealth({ status: 'closed' });
  }

  async reconnect(): Promise<void> {
    if (this.isDestroyed) {
      throw new Error('WebSocket client has been destroyed');
    }

    this.updateLoadingState({ reconnecting: true });
    
    try {
      await this.disconnect();
      await new Promise(resolve => setTimeout(resolve, this.config.reconnectInterval));
      await this.connect();
    } finally {
      this.updateLoadingState({ reconnecting: false });
    }
  }

  async send(payload: unknown, options: MessageSendOptions = {}): Promise<void> {
    if (this.isDestroyed) {
      throw new Error('WebSocket client has been destroyed');
    }

    const message: QueuedMessage = {
      id: this.generateMessageId(),
      payload,
      timestamp: Date.now(),
      attempts: 0,
      maxAttempts: options.maxRetries ?? 3,
      priority: options.priority ?? 'normal',
      onSuccess: options.onSuccess,
      onError: options.onError
    };

    if (this.socket?.readyState === WebSocket.OPEN) {
      await this.sendMessage(message);
    } else if (this.config.enableMessageQueue) {
      this.queueMessage(message);
    } else {
      throw new Error('WebSocket not connected and message queuing disabled');
    }
  }

  async sendWithRetry(payload: unknown, maxAttempts = 3): Promise<void> {
    return this.send(payload, { maxRetries: maxAttempts });
  }

  // State accessors
  getConnectionHealth(): ConnectionHealth {
    return { ...this.connectionHealth };
  }

  getMetrics(): ConnectionMetrics {
    return { ...this.metrics };
  }

  getQueueStatus() {
    return {
      length: this.messageQueue.length,
      messages: [...this.messageQueue]
    };
  }

  clearErrors(): void {
    this.errors = [];
  }

  async retryFailedMessages(): Promise<void> {
    if (this.socket?.readyState !== WebSocket.OPEN) {
      throw new Error('Cannot retry messages: WebSocket not connected');
    }

    const failedMessages = this.messageQueue.filter(msg => msg.attempts > 0);
    for (const message of failedMessages) {
      try {
        await this.sendMessage(message);
        this.removeFromQueue(message.id);
      } catch (error) {
        // Error handling is done in sendMessage
      }
    }
  }

  clearMessageQueue(): void {
    this.messageQueue = [];
    this.notifyQueueChange();
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN;
  }

  isConnecting(): boolean {
    return this.loadingState.connecting;
  }

  hasErrors(): boolean {
    return this.errors.length > 0;
  }

  // Event handling
  on<K extends keyof WebSocketClientEvents>(event: K, listener: WebSocketClientEvents[K]): void {
    this.eventListeners[event] = listener;
  }

  off<K extends keyof WebSocketClientEvents>(event: K, listener: WebSocketClientEvents[K]): void {
    if (this.eventListeners[event] === listener) {
      delete this.eventListeners[event];
    }
  }

  destroy(): void {
    this.isDestroyed = true;
    this.disconnect();
    this.clearTimers();
    this.eventListeners = {};
    this.messageQueue = [];
  }

  // Private implementation methods
  private async establishConnection(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.connectionStartTime = Date.now();
      this.socket = new WebSocket(this.config.url, this.config.protocols);
      
      const connectionTimeout = setTimeout(() => {
        this.socket?.close();
        reject(new Error('Connection timeout'));
      }, this.config.connectionTimeout);

      this.socket.onopen = () => {
        clearTimeout(connectionTimeout);
        this.handleConnectionOpen();
        resolve();
      };

      this.socket.onerror = (event) => {
        clearTimeout(connectionTimeout);
        this.handleSocketError(event);
        reject(new Error('WebSocket connection failed'));
      };

      this.socket.onmessage = (event) => {
        this.handleMessage(event);
      };

      this.socket.onclose = (event) => {
        this.handleConnectionClose(event);
      };
    });
  }

  private handleConnectionOpen(): void {
    this.metrics.totalConnections++;
    if (this.connectionHealth.reconnectAttempts > 0) {
      this.metrics.totalReconnections++;
    }
    
    this.updateConnectionHealth({
      status: 'open',
      reconnectAttempts: 0,
      isHealthy: true
    });
    
    this.updateLoadingState({
      connecting: false,
      reconnecting: false
    });

    this.startHeartbeat();
    this.processQueuedMessages();
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data);
      this.metrics.totalMessagesReceived++;
      
      // Handle pong responses for latency calculation
      if (data.type === 'pong' && data.timestamp) {
        const latency = Date.now() - parseInt(data.timestamp);
        this.updateConnectionHealth({
          lastPong: Date.now(),
          latency
        });
        this.calculateConnectionQuality();
      }
      
      // Forward to message handler
      if (this.onMessage) {
        this.onMessage(data);
      }
      
    } catch (error) {
      this.addError({
        type: 'message',
        message: 'Failed to parse WebSocket message',
        timestamp: Date.now(),
        recoverable: true,
        retryable: false,
        details: { error: error.message, data: event.data }
      });
    }
  }

  private handleConnectionClose(event: CloseEvent): void {
    this.updateConnectionHealth({
      status: 'closed',
      isHealthy: false
    });
    
    this.clearTimers();
    
    if (!this.manualDisconnect && !this.isDestroyed) {
      this.scheduleReconnect();
    }
    
    if (this.metrics.lastConnected) {
      this.metrics.uptime += Date.now() - this.connectionStartTime;
    }
  }

  private handleSocketError(event: Event): void {
    this.addError({
      type: 'connection',
      message: 'WebSocket connection error',
      timestamp: Date.now(),
      recoverable: true,
      retryable: true,
      details: { event }
    });
    
    this.updateConnectionHealth({
      status: 'error',
      isHealthy: false
    });
  }

  private handleConnectionError(error: unknown): void {
    this.addError({
      type: 'connection',
      message: error instanceof Error ? error.message : 'Unknown connection error',
      timestamp: Date.now(),
      recoverable: true,
      retryable: true,
      details: { error }
    });
    
    this.updateLoadingState({ connecting: false });
  }

  private scheduleReconnect(): void {
    if (this.connectionHealth.reconnectAttempts >= this.config.maxReconnectAttempts) {
      this.addError({
        type: 'connection',
        message: 'Maximum reconnection attempts exceeded',
        timestamp: Date.now(),
        recoverable: false,
        retryable: false
      });
      return;
    }

    const delay = this.calculateReconnectDelay();
    this.updateLoadingState({ reconnecting: true });
    
    this.reconnectTimer = setTimeout(() => {
      this.updateConnectionHealth({
        reconnectAttempts: this.connectionHealth.reconnectAttempts + 1
      });
      this.connect().catch(() => {
        // Error already handled in connect method
      });
    }, delay);
  }

  private calculateReconnectDelay(): number {
    const { reconnectAttempts } = this.connectionHealth;
    const { reconnectInterval, retryBackoffStrategy, maxRetryDelay } = this.config;
    
    let delay: number;
    
    switch (retryBackoffStrategy) {
      case 'linear':
        delay = reconnectInterval * (reconnectAttempts + 1);
        break;
      case 'exponential':
        delay = reconnectInterval * Math.pow(2, reconnectAttempts);
        break;
      case 'fibonacci':
        delay = reconnectInterval * this.fibonacci(reconnectAttempts + 1);
        break;
      default:
        delay = reconnectInterval;
    }
    
    return Math.min(delay, maxRetryDelay);
  }

  private fibonacci(n: number): number {
    if (n <= 1) return 1;
    return this.fibonacci(n - 1) + this.fibonacci(n - 2);
  }

  private startHeartbeat(): void {
    if (!this.config.enableHeartbeat) return;
    
    this.heartbeatTimer = setInterval(() => {
      if (this.socket?.readyState === WebSocket.OPEN) {
        this.lastPingTime = Date.now();
        this.socket.send(JSON.stringify({
          type: 'ping',
          timestamp: this.lastPingTime.toString()
        }));
        
        this.updateConnectionHealth({ lastPing: this.lastPingTime });
      }
    }, this.config.heartbeatInterval);
  }

  private clearTimers(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.pingTimer) {
      clearTimeout(this.pingTimer);
      this.pingTimer = null;
    }
  }

  private async sendMessage(message: QueuedMessage): Promise<void> {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket not connected');
    }

    try {
      this.updateLoadingState({ sendingMessage: true });
      
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Message send timeout')), this.config.messageTimeout);
      });
      
      const sendPromise = new Promise<void>((resolve, reject) => {
        try {
          this.socket!.send(JSON.stringify(message.payload));
          this.metrics.totalMessagesSent++;
          message.onSuccess?.();
          resolve();
        } catch (error) {
          reject(error);
        }
      });
      
      await Promise.race([sendPromise, timeoutPromise]);
      
    } catch (error) {
      message.attempts++;
      
      const errorState: ErrorState = {
        type: 'message',
        message: error instanceof Error ? error.message : 'Failed to send message',
        timestamp: Date.now(),
        recoverable: message.attempts < message.maxAttempts,
        retryable: true,
        details: { messageId: message.id, attempts: message.attempts }
      };
      
      this.addError(errorState);
      message.onError?.(errorState);
      
      if (message.attempts < message.maxAttempts) {
        // Re-queue for retry
        this.queueMessage(message);
      }
      
      throw error;
    } finally {
      this.updateLoadingState({ sendingMessage: false });
    }
  }

  private queueMessage(message: QueuedMessage): void {
    if (this.messageQueue.length >= this.config.maxQueueSize) {
      // Remove oldest low-priority message to make room
      const lowPriorityIndex = this.messageQueue.findIndex(msg => msg.priority === 'low');
      if (lowPriorityIndex >= 0) {
        this.messageQueue.splice(lowPriorityIndex, 1);
      } else {
        this.messageQueue.shift(); // Remove oldest message
      }
    }
    
    // Insert message based on priority
    const insertIndex = this.messageQueue.findIndex(msg => 
      this.getPriorityWeight(message.priority) > this.getPriorityWeight(msg.priority)
    );
    
    if (insertIndex >= 0) {
      this.messageQueue.splice(insertIndex, 0, message);
    } else {
      this.messageQueue.push(message);
    }
    
    this.notifyQueueChange();
  }

  private getPriorityWeight(priority: QueuedMessage['priority']): number {
    switch (priority) {
      case 'high': return 3;
      case 'normal': return 2;
      case 'low': return 1;
      default: return 2;
    }
  }

  private removeFromQueue(messageId: string): void {
    const index = this.messageQueue.findIndex(msg => msg.id === messageId);
    if (index >= 0) {
      this.messageQueue.splice(index, 1);
      this.notifyQueueChange();
    }
  }

  private async processQueuedMessages(): Promise<void> {
    const messagesToProcess = [...this.messageQueue];
    this.messageQueue = [];
    
    for (const message of messagesToProcess) {
      try {
        await this.sendMessage(message);
      } catch (error) {
        // Error handling is done in sendMessage
      }
    }
  }

  private calculateConnectionQuality(): void {
    const { latency } = this.connectionHealth;
    const uptime = this.metrics.uptime / (Date.now() - this.connectionStartTime);
    
    let quality: ConnectionHealth['connectionQuality'] = 'critical';
    
    for (const [level, thresholds] of Object.entries(CONNECTION_QUALITY_THRESHOLDS)) {
      if (latency <= thresholds.latency && uptime >= thresholds.uptime) {
        quality = level as ConnectionHealth['connectionQuality'];
        break;
      }
    }
    
    this.updateConnectionHealth({ connectionQuality: quality });
  }

  private updateConnectionHealth(updates: Partial<ConnectionHealth>): void {
    this.connectionHealth = { ...this.connectionHealth, ...updates };
    this.eventListeners.onConnectionChange?.(this.connectionHealth);
  }

  private updateLoadingState(updates: Partial<LoadingState>): void {
    this.loadingState = { ...this.loadingState, ...updates };
    this.eventListeners.onLoadingChange?.(this.loadingState);
  }

  private addError(error: ErrorState): void {
    this.errors.push(error);
    this.metrics.totalErrors++;
    this.eventListeners.onError?.(error);
    
    // Limit error history to prevent memory leaks
    if (this.errors.length > 50) {
      this.errors = this.errors.slice(-25);
    }
  }

  private notifyQueueChange(): void {
    this.eventListeners.onQueueChange?.(this.messageQueue.length);
  }

  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Factory function for creating enhanced WebSocket clients
export function createEnhancedWebSocketClient(
  config: Partial<WebSocketConfig>,
  onMessage?: (envelope: ChatSocketEnvelope) => void
): EnhancedWebSocketClient {
  return new EnhancedWebSocketService(config, onMessage);
}
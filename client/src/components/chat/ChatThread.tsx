import { useCallback, useEffect, useMemo, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import type { ChatToken } from "./ChatKitProvider";
import ChatInput from "./ChatInput";
import MessageList from "./MessageList";
import { chatApi } from "../../services/chatApi";
import type { ChatThread as ThreadModel, ClientMessage } from "../../types/chat";
import { useEnhancedWebSocket } from "../../hooks/useEnhancedWebSocket";
import type { ConnectionHealth, ErrorState } from "../../types/websocket";

type Props = {
  placement: string;
  token: ChatToken;
  onThreadChange: (threadId: string) => Promise<void> | void;
};

const createClientMessage = (content: string, threadId: string): ClientMessage => ({
  id: `optimistic-${threadId}-${Date.now()}`,
  clientId:
    typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
      ? crypto.randomUUID()
      : `local-${Date.now()}-${Math.random().toString(16).slice(2)}`,
  threadId,
  role: "user",
  content,
  createdAt: new Date().toISOString(),
  status: "sending",
});

const ConnectionIndicator = ({ health }: { health: ConnectionHealth }) => {
  const getStatusColor = () => {
    switch (health.status) {
      case 'open': return 'bg-green-500';
      case 'connecting': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      case 'closed': return 'bg-gray-500';
      default: return 'bg-gray-400';
    }
  };

  const getQualityIndicator = () => {
    switch (health.connectionQuality) {
      case 'excellent': return '🟢';
      case 'good': return '🟡';
      case 'poor': return '🟠';
      case 'critical': return '🔴';
      default: return '⚪';
    }
  };

  return (
    <div className="flex items-center gap-2 text-sm">
      <div className={`w-3 h-3 rounded-full ${getStatusColor()}`} />
      <span className="capitalize">{health.status}</span>
      {health.status === 'open' && (
        <>
          <span>{getQualityIndicator()}</span>
          <span className="text-xs text-gray-500">
            {health.latency}ms
          </span>
        </>
      )}
      {health.reconnectAttempts > 0 && (
        <span className="text-xs text-orange-600">
          Retry {health.reconnectAttempts}
        </span>
      )}
    </div>
  );
};

const ErrorBanner = ({ errors, onClearErrors }: { 
  errors: ErrorState[]; 
  onClearErrors: () => void; 
}) => {
  const latestError = errors[errors.length - 1];
  
  if (!latestError) return null;

  return (
    <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h4 className="text-sm font-medium text-red-800 capitalize">
            {latestError.type} Error
          </h4>
          <p className="text-sm text-red-700 mt-1">
            {latestError.message}
          </p>
          {latestError.recoverable && (
            <p className="text-xs text-red-600 mt-1">
              This error is recoverable. The system will retry automatically.
            </p>
          )}
        </div>
        <button
          onClick={onClearErrors}
          className="text-red-600 hover:text-red-800 text-xs"
        >
          Dismiss
        </button>
      </div>
    </div>
  );
};

const ChatThread = ({ placement, token, onThreadChange }: Props) => {
  const queryClient = useQueryClient();
  const [optimisticMessages, setOptimisticMessages] = useState<ClientMessage[]>([]);
  const [liveMessages, setLiveMessages] = useState<ClientMessage[]>([]);
  const [threadSwitching, setThreadSwitching] = useState<string | null>(null);
  const [threadActionError, setThreadActionError] = useState<string | null>(null);
  const [creatingThread, setCreatingThread] = useState(false);

  const [selectedThreadId, setSelectedThreadId] = useState(token.threadId);

  useEffect(() => {
    setSelectedThreadId(token.threadId);
    setOptimisticMessages([]);
    setLiveMessages([]);
    setThreadSwitching(null);
  }, [token.threadId]);

  const threadsQuery = useQuery({
    queryKey: ["chat", "threads", placement],
    queryFn: () => chatApi.listThreads({ placement, limit: 20 }),
    staleTime: 60_000,
  });

  const eventsQuery = useQuery({
    queryKey: ["chat", "threads", selectedThreadId, "events"],
    queryFn: () => chatApi.listEvents(selectedThreadId!, { limit: 200 }),
    enabled: Boolean(selectedThreadId),
    refetchOnWindowFocus: false,
  });

  const activeThread = useMemo(() => {
    return threadsQuery.data?.find((thread) => thread.id === selectedThreadId);
  }, [threadsQuery.data, selectedThreadId]);

  const mergedMessages = useMemo(() => {
    const base = [...(eventsQuery.data ?? [])];
    const seen = new Map<string, ClientMessage>();
    base.forEach((msg) => {
      seen.set(msg.id, msg);
    });
    liveMessages.forEach((msg) => {
      if (!seen.has(msg.id)) {
        seen.set(msg.id, msg);
      }
    });
    const merged = Array.from(seen.values()).sort((a, b) => {
      return new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
    });
    return [...merged, ...optimisticMessages];
  }, [eventsQuery.data, liveMessages, optimisticMessages]);

  // Enhanced WebSocket with comprehensive monitoring
  const websocketResult = useEnhancedWebSocket({
    threadId: selectedThreadId,
    token: token.token,
    enabled: Boolean(selectedThreadId),
    onEvent: (event) => {
      if (event.threadId !== selectedThreadId) {
        return;
      }
      setLiveMessages((prev) => {
        if (prev.some((item) => item.id === event.id)) {
          return prev;
        }
        return [...prev, event];
      });
    },
    onThreadUpdate: (thread) => {
      if (thread.placement !== placement) {
        return;
      }
      queryClient.setQueryData<ThreadModel[]>(["chat", "threads", placement], (prev) => {
        if (!prev) return prev;
        const idx = prev.findIndex((item) => item.id === thread.id);
        if (idx === -1) return prev;
        const next = [...prev];
        next[idx] = thread;
        return next;
      });
    },
    onError: (error) => {
      console.error('WebSocket error:', error);
      // Errors are automatically tracked in the hook
    },
  });

  const {
    connectionHealth,
    loadingState,
    errors,
    metrics,
    send: sendWebSocket,
    reconnect,
    clearErrors,
    isConnected,
    isConnecting,
    isReconnecting,
    queueLength
  } = websocketResult;

  const handleCreateThread = useCallback(async () => {
    setThreadActionError(null);
    setCreatingThread(true);
    try {
      const thread = await chatApi.createThread({
        placement,
        context: { source: "modal" },
      });
      await threadsQuery.refetch();
      await onThreadChange(thread.id);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unable to create thread.";
      setThreadActionError(message);
    } finally {
      setCreatingThread(false);
    }
  }, [placement, onThreadChange, threadsQuery]);

  const handleSelectThread = useCallback(
    async (threadId: string) => {
      if (threadId === selectedThreadId) {
        return;
      }
      setThreadActionError(null);
      setThreadSwitching(threadId);
      try {
        await onThreadChange(threadId);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Unable to switch threads.";
        setThreadActionError(message);
        setThreadSwitching(null);
      }
    },
    [selectedThreadId, onThreadChange],
  );

  const handleSend = useCallback(
    async (content: string, retryMessage?: ClientMessage) => {
      if (!selectedThreadId) {
        throw new Error("No active thread selected.");
      }
      const optimistic = retryMessage ?? createClientMessage(content, selectedThreadId);
      if (!retryMessage) {
        setOptimisticMessages((prev) => [...prev, optimistic]);
      } else {
        setOptimisticMessages((prev) =>
          prev.map((msg) =>
            msg.clientId === retryMessage.clientId
              ? { ...msg, status: "sending", error: null }
              : msg,
          ),
        );
      }
      try {
        const saved = await chatApi.sendMessage(selectedThreadId, {
          content,
          role: "user",
        });
        setOptimisticMessages((prev) =>
          prev.filter((msg) => msg.clientId !== optimistic.clientId),
        );
        setLiveMessages((prev) => [...prev, saved]);
        await eventsQuery.refetch();
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to send message.";
        setOptimisticMessages((prev) =>
          prev.map((msg) =>
            msg.clientId === optimistic.clientId
              ? { ...msg, status: "error", error: message }
              : msg,
          ),
        );
        throw err;
      }
    },
    [selectedThreadId, eventsQuery],
  );

  const handleRetry = useCallback(
    (message: ClientMessage) => {
      void handleSend(message.content, message);
    },
    [handleSend],
  );

  const handleReconnect = useCallback(async () => {
    try {
      await reconnect();
    } catch (error) {
      console.error('Manual reconnection failed:', error);
    }
  }, [reconnect]);

  return (
    <div className="chat-shell">
      <aside className="chat-sidebar">
        <div className="chat-sidebar__header">
          <div>
            <p className="chat-sidebar__label">Threads</p>
            <strong>{placement}</strong>
          </div>
          <button
            type="button"
            className="btn btn--tiny"
            onClick={() => void handleCreateThread()}
            disabled={creatingThread}
          >
            {creatingThread ? "Creating…" : "New thread"}
          </button>
        </div>
        {threadActionError && <p className="chat-sidebar__error">{threadActionError}</p>}
        <div className="chat-sidebar__list" role="list">
          {threadsQuery.isLoading && <p>Loading threads…</p>}
          {!threadsQuery.isLoading &&
            (threadsQuery.data?.length ?? 0) === 0 && <p>No threads yet.</p>}
          {threadsQuery.data?.map((thread) => (
            <button
              type="button"
              key={thread.id}
              className={`chat-sidebar__item ${
                thread.id === selectedThreadId ? "chat-sidebar__item--active" : ""
              }`}
              onClick={() => void handleSelectThread(thread.id)}
              disabled={threadSwitching === thread.id}
            >
              <div>
                <p className="chat-sidebar__title">{thread.title ?? "Untitled thread"}</p>
                <p className="chat-sidebar__meta">
                  {new Date(thread.updatedAt).toLocaleString([], {
                    month: "short",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
              </div>
              {thread.id === selectedThreadId && <span className="chat-sidebar__pill">Active</span>}
            </button>
          ))}
        </div>
      </aside>

      <section className="chat-main">
        <header className="chat-main__header">
          <div>
            <p className="chat-main__label">Thread</p>
            <strong>{selectedThreadId}</strong>
          </div>
          <div className="chat-main__status">
            <ConnectionIndicator health={connectionHealth} />
            {(loadingState.connecting || loadingState.reconnecting) && (
              <div className="flex items-center gap-1 text-xs text-blue-600">
                <span className="animate-spin">⚡</span>
                {loadingState.connecting && "Connecting..."}
                {loadingState.reconnecting && "Reconnecting..."}
              </div>
            )}
            {queueLength > 0 && (
              <div className="text-xs text-orange-600">
                Queue: {queueLength}
              </div>
            )}
            {!isConnected && connectionHealth.status !== 'connecting' && (
              <button
                onClick={handleReconnect}
                className="text-xs text-blue-600 hover:text-blue-800"
                disabled={isReconnecting}
              >
                {isReconnecting ? 'Reconnecting...' : 'Reconnect'}
              </button>
            )}
          </div>
        </header>

        {/* Error handling */}
        <ErrorBanner errors={errors} onClearErrors={clearErrors} />

        {/* Connection metrics for debugging (dev mode only) */}
        {process.env.NODE_ENV === 'development' && metrics.totalConnections > 0 && (
          <details className="mb-4">
            <summary className="text-xs text-gray-500 cursor-pointer">
              Connection Debug Info
            </summary>
            <div className="text-xs text-gray-600 mt-2 bg-gray-50 p-2 rounded">
              <div>Connections: {metrics.totalConnections}</div>
              <div>Messages Sent: {metrics.totalMessagesSent}</div>
              <div>Messages Received: {metrics.totalMessagesReceived}</div>
              <div>Average Latency: {metrics.averageLatency.toFixed(0)}ms</div>
              <div>Total Errors: {metrics.totalErrors}</div>
              <div>Uptime: {Math.round(metrics.uptime / 1000)}s</div>
            </div>
          </details>
        )}

        {activeThread?.context && (
          <pre className="chat-context">{JSON.stringify(activeThread.context, null, 2)}</pre>
        )}

        <MessageList
          messages={mergedMessages}
          isLoading={eventsQuery.isLoading}
          socketStatus={connectionHealth.status}
          onRetryMessage={handleRetry}
        />

        <ChatInput
          placeholder="Ask CapeAI anything about this placement…"
          onSend={handleSend}
          isSending={optimisticMessages.some((msg) => msg.status === "sending") || loadingState.sendingMessage}
          disabled={!selectedThreadId || threadSwitching !== null || (!isConnected && queueLength >= 10)}
          connectionHealth={connectionHealth}
          queueLength={queueLength}
        />
      </section>
    </div>
  );
};

export default ChatThread;

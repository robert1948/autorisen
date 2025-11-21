import { useEffect, useMemo, useState } from "react";

import ChatThread from "./ChatThread";
import ConnectionIndicator from "./ConnectionIndicator";
import {
  fetchOnboardingChecklist,
  updateOnboardingChecklist,
  type ChecklistSummary,
} from "../../lib/api";
import { useChatSession } from "../../hooks/useChatSession";
import type { ConnectionHealth } from "../../types/websocket";

export type ChatPlacement =
  | "support"
  | "onboarding"
  | "energy"
  | "money"
  | "admin"
  | "developer";

type Props = {
  open: boolean;
  onClose: () => void;
  placement: ChatPlacement;
  title: string;
  description?: string;
};

const PLACEMENT_LABELS: Record<ChatPlacement, string> = {
  support: "Support",
  onboarding: "CapeAI Onboarding",
  energy: "Energy Insights",
  money: "Money Copilot",
  admin: "Ops Copilot",
  developer: "Agent Workbench",
};

const ChatModal = ({ open, onClose, placement, title, description }: Props) => {
  const [threadMap, setThreadMap] = useState<Record<string, string>>({});
  const activeThreadId = threadMap[placement];
  const [checklist, setChecklist] = useState<ChecklistSummary | null>(null);
  const [checklistError, setChecklistError] = useState<string | null>(null);
  const [updatingTask, setUpdatingTask] = useState<string | null>(null);
  const [connectionHealth, setConnectionHealth] = useState<ConnectionHealth | null>(null);
  const {
    token,
    loading,
    refreshing,
    error,
    expiryCountdown,
    startSession,
  } = useChatSession({
    placement,
    threadId: activeThreadId,
    enabled: open,
  });

  useEffect(() => {
    if (!token) {
      return;
    }
    setThreadMap((prev) => {
      if (prev[placement] === token.threadId) {
        return prev;
      }
      return { ...prev, [placement]: token.threadId };
    });
  }, [token, placement]);

  if (!open) {
    return null;
  }

  const placementLabel = useMemo(
    () => PLACEMENT_LABELS[placement] ?? "Chat",
    [placement],
  );

  useEffect(() => {
    if (placement !== "onboarding" || !token) {
      setChecklist(null);
      return;
    }
    let mounted = true;
    const loadChecklist = async () => {
      try {
        const data = await fetchOnboardingChecklist();
        if (mounted) {
          setChecklist(data);
          setChecklistError(null);
        }
      } catch (err) {
        if (mounted) {
          const message = err instanceof Error ? err.message : "Failed to load checklist";
          setChecklistError(message);
        }
      }
    };
    loadChecklist();
    return () => {
      mounted = false;
    };
  }, [placement, token]);

  return (
    <div className="chat-modal-overlay" role="dialog" aria-modal="true">
      <div className="chat-modal">
        <header className="chat-modal__header">
          <div>
            <p className="chat-modal__eyebrow">{placementLabel}</p>
            <h2>{title}</h2>
          </div>
          <div className="chat-modal__header-actions">
            {connectionHealth && (
              <ConnectionIndicator health={connectionHealth} variant="compact" />
            )}
            <button type="button" className="chat-modal__close" onClick={onClose}>
              ×
            </button>
          </div>
        </header>
        {description && <p className="chat-modal__description">{description}</p>}

        {loading && (
          <div className="chat-modal__state">
            <div className="chat-modal__spinner" aria-hidden="true" />
            <p>Preparing your assistant…</p>
          </div>
        )}

        {error && !loading && (
          <div className="chat-modal__state chat-modal__state--error">
            <p>{error}</p>
          </div>
        )}

        {token && !loading && !error && (
          <ChatThread
            placement={placement}
            token={token}
            onThreadChange={(threadId) =>
              startSession({ threadId, mode: "initial" })
            }
            onConnectionHealthChange={setConnectionHealth}
          />
        )}
        {token && !loading && !error && (
          <section className="chat-modal__session-meta">
            <div className="chat-modal__session-meta-header">
              <div>
                <p className="chat-modal__session-label">Thread</p>
                <strong>{token.threadId}</strong>
              </div>
              <button
                type="button"
                className="btn btn--tiny"
                onClick={() => startSession({ mode: "refresh" })}
                disabled={refreshing}
              >
                {refreshing ? "Refreshing…" : "Refresh session"}
              </button>
            </div>
            <p className="chat-modal__session-expiry">
              Expires in {expiryCountdown ?? "—"}s · Placement {token.placement}
            </p>
            <div className="chat-modal__tool-list">
              {token.allowedTools.length > 0 ? (
                token.allowedTools.map((tool) => (
                  <span key={tool} className="chat-modal__tool-badge">
                    {tool}
                  </span>
                ))
              ) : (
                <span className="chat-modal__tool-empty">No tools provisioned yet.</span>
              )}
            </div>
          </section>
        )}

        {placement === "onboarding" && checklist && (
          <section className="chat-modal__checklist">
            <header>
              <h4>Checklist progress</h4>
              <span>
                {checklist.summary.completed}/{checklist.summary.total} complete
              </span>
            </header>
            {checklistError && <p className="chat-modal__error">{checklistError}</p>}
            <ul>
              {Object.entries(checklist.tasks)
                .sort((a, b) => a[0].localeCompare(b[0]))
                .map(([taskId, task]) => (
                  <li key={taskId}>
                    <span className={task.done ? "onboarding-checklist__done" : ""}>{task.label}</span>
                    <button
                      type="button"
                      className="btn btn--tiny"
                      disabled={updatingTask === taskId}
                      onClick={async () => {
                        setUpdatingTask(taskId);
                        try {
                          const data = await updateOnboardingChecklist(taskId, !task.done, task.label);
                          setChecklist(data);
                          setChecklistError(null);
                        } catch (err) {
                          const message =
                            err instanceof Error ? err.message : "Failed to update checklist";
                          setChecklistError(message);
                        } finally {
                          setUpdatingTask(null);
                        }
                      }}
                    >
                      {updatingTask === taskId
                        ? "Saving…"
                        : task.done
                        ? "Mark undone"
                        : "Mark done"}
                    </button>
                  </li>
                ))}
            </ul>
          </section>
        )}
      </div>
    </div>
  );
};

export default ChatModal;

import { useEffect, useMemo, useState } from "react";

import { ChatToken, useChatKit } from "./ChatKitProvider";
import ChatKitWidget from "./ChatKitWidget";
import {
  fetchOnboardingChecklist,
  updateOnboardingChecklist,
  type ChecklistSummary,
} from "../../lib/api";

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

type TokenState =
  | { loading: true; error?: string; token?: undefined }
  | { loading: false; error?: string; token?: ChatToken };

const PLACEMENT_LABELS: Record<ChatPlacement, string> = {
  support: "Support",
  onboarding: "CapeAI Onboarding",
  energy: "Energy Insights",
  money: "Money Copilot",
  admin: "Ops Copilot",
  developer: "Agent Workbench",
};

const ChatModal = ({ open, onClose, placement, title, description }: Props) => {
  const { requestToken } = useChatKit();
  const [state, setState] = useState<TokenState>({ loading: false });
  const [threadMap, setThreadMap] = useState<Record<string, string>>({});
  const activeThreadId = threadMap[placement];
  const [checklist, setChecklist] = useState<ChecklistSummary | null>(null);
  const [checklistError, setChecklistError] = useState<string | null>(null);
  const [updatingTask, setUpdatingTask] = useState<string | null>(null);

  useEffect(() => {
    if (!open) {
      setState({ loading: false, token: undefined, error: undefined });
      return;
    }

    let cancelled = false;
    setState({ loading: true });
    requestToken(placement, activeThreadId)
      .then((token) => {
        if (!cancelled) {
          setThreadMap((prev) => ({ ...prev, [placement]: token.threadId }));
          setState({ loading: false, token, error: undefined });
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          const message =
            err instanceof Error ? err.message : "Failed to load chat session.";
          setState({ loading: false, error: message });
        }
      });

    return () => {
      cancelled = true;
    };
  }, [open, placement, requestToken, activeThreadId]);

  if (!open) {
    return null;
  }

  const { loading, error } = state;
  const token = !loading ? state.token : undefined;
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
          <button type="button" className="chat-modal__close" onClick={onClose}>
            ×
          </button>
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
          <ChatKitWidget token={token} placement={placement} />
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

import { useEffect, useState } from "react";

import {
  fetchFlowRuns,
  fetchOnboardingChecklist,
  updateOnboardingChecklist,
  type ChecklistSummary,
  type FlowRunRecord,
} from "../../lib/api";

const DEFAULT_TASK_ORDER = [
  "invite_team",
  "connect_data_sources",
  "configure_notifications",
  "launch_first_run",
];

const OnboardingHistory = () => {
  const [runs, setRuns] = useState<FlowRunRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [checklist, setChecklist] = useState<ChecklistSummary | null>(null);
  const [updatingTask, setUpdatingTask] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const loadRuns = async () => {
      try {
        setLoading(true);
        const [runData, checklistData] = await Promise.all([
          fetchFlowRuns("onboarding", 5),
          fetchOnboardingChecklist(),
        ]);
        if (mounted) {
          setRuns(runData);
          setChecklist(checklistData);
          setError(null);
        }
      } catch (err) {
        if (mounted) {
          // Silently handle auth errors — the global unauthorized handler
          // already takes care of redirect / state cleanup.
          const status = (err as { status?: number }).status;
          if (status === 401 || status === 403 || status === 429) {
            setLoading(false);
            return;
          }
          const message = err instanceof Error ? err.message : "Unable to load onboarding runs";
          setError(message);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };
    loadRuns();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <article className="experience-card">
      <div className="experience-card__header">
        <span className="badge">Recent progress</span>
        <h3>Onboarding run history</h3>
      </div>
      {checklist && (
        <div className="onboarding-checklist">
          <p>
            Checklist progress: {checklist.summary.completed}/{checklist.summary.total}
          </p>
          <ul>
            {Object.entries(checklist.tasks).map(([taskId, task]) => (
              <li key={taskId} className={task.done ? "onboarding-checklist__done" : ""}>
                {task.label}
              </li>
            ))}
          </ul>
        </div>
      )}
      {loading && <p>Loading recent runs…</p>}
      {error && <p className="registry__error">{error}</p>}
      {!loading && !error && runs.length === 0 && (
        <p className="registry__empty">No onboarding runs yet. Start the CapeAI Guide to begin.</p>
      )}
      {!loading && !error && runs.length > 0 && (
        <ul className="onboarding-runs">
          {runs.map((run) => (
            <li key={run.id}>
              <header>
                <strong>{new Date(run.created_at).toLocaleString()}</strong>
                <span className={`status-badge status-badge--${run.status}`}>
                  {run.status.toUpperCase()}
                </span>
              </header>
              <p className="onboarding-runs__meta">
                Thread {run.thread_id} · Attempt {run.attempt}/{run.max_attempts}
              </p>
              {run.error_message && (
                <p className="onboarding-runs__error">Error: {run.error_message}</p>
              )}
              <pre className="onboarding-runs__steps">
                {JSON.stringify(run.steps, null, 2)}
              </pre>
            </li>
          ))}
        </ul>
      )}
      {checklist && Object.keys(checklist.tasks).length > 0 && (
        <div className="onboarding-checklist-actions">
          <h4>Checklist tasks</h4>
          <ul className="onboarding-checklist-list">
            {Object.entries(checklist.tasks)
              .sort((a, b) =>
                DEFAULT_TASK_ORDER.indexOf(a[0]) - DEFAULT_TASK_ORDER.indexOf(b[0]),
              )
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
                        const updated = await updateOnboardingChecklist(taskId, !task.done, task.label);
                        setChecklist(updated);
                      } catch (err) {
                        const message =
                          err instanceof Error ? err.message : "Failed to update checklist";
                        setError(message);
                      } finally {
                        setUpdatingTask(null);
                      }
                    }}
                  >
                    {updatingTask === taskId ? "Saving…" : task.done ? "Mark undone" : "Mark done"}
                  </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </article>
  );
};

export default OnboardingHistory;

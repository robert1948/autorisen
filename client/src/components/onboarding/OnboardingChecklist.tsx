import React, { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import {
  fetchOnboardingChecklist,
  updateOnboardingChecklist,
  type ChecklistSummary,
  type ChecklistTask,
} from "../../lib/api";

type TaskRow = {
  id: string;
  label: string;
  done: boolean;
};

function toRows(tasks: Record<string, ChecklistTask>): TaskRow[] {
  return Object.entries(tasks).map(([id, task]) => ({
    id,
    label: task.label,
    done: Boolean(task.done),
  }));
}

function setOnboardingComplete(complete: boolean) {
  try {
    window.localStorage.setItem("onboarding_complete", complete ? "true" : "false");
  } catch {
    // ignore storage failures
  }
}

const OnboardingChecklist: React.FC = () => {
  const navigate = useNavigate();
  const [data, setData] = useState<ChecklistSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updating, setUpdating] = useState<Record<string, boolean>>({});

  const rows = useMemo(() => (data ? toRows(data.tasks) : []), [data]);
  const percent = useMemo(() => {
    if (!data || data.summary.total === 0) return 0;
    return Math.round((data.summary.completed / data.summary.total) * 100);
  }, [data]);

  const complete = Boolean(data && data.summary.total > 0 && data.summary.completed === data.summary.total);

  useEffect(() => {
    let mounted = true;
    const controller = new AbortController();

    const load = async () => {
      try {
        setLoading(true);
        const checklist = await fetchOnboardingChecklist();
        if (!mounted) return;
        setData(checklist);
        setError(null);
        setOnboardingComplete(
          checklist.summary.total > 0 && checklist.summary.completed === checklist.summary.total,
        );
      } catch (err) {
        if (!mounted) return;
        // Silently handle auth/rate-limit errors — global handler manages redirect
        const status = (err as { status?: number }).status;
        if (status === 401 || status === 403 || status === 429) {
          return;
        }
        const message = err instanceof Error ? err.message : "Failed to load onboarding checklist";
        setError(message);
      } finally {
        if (mounted) setLoading(false);
      }
    };

    load();

    return () => {
      mounted = false;
      controller.abort();
    };
  }, []);

  const toggle = async (task: TaskRow) => {
    if (updating[task.id]) return;
    setUpdating((prev) => ({ ...prev, [task.id]: true }));
    try {
      const updated = await updateOnboardingChecklist(task.id, !task.done, task.label);
      setData(updated);
      setError(null);
      setOnboardingComplete(
        updated.summary.total > 0 && updated.summary.completed === updated.summary.total,
      );
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to update onboarding step";
      setError(message);
    } finally {
      setUpdating((prev) => ({ ...prev, [task.id]: false }));
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-700 font-medium">Unable to load checklist</p>
          <p className="text-gray-500 text-sm mt-1">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-3 text-blue-600 hover:text-blue-700"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500">No checklist data available.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-2xl font-bold text-gray-900">Getting Started Checklist</h1>
          <p className="mt-2 text-gray-600">Complete these steps to finish onboarding.</p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Your Progress</h2>
            <span className="text-2xl font-bold text-blue-600">{percent}%</span>
          </div>

          <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
            <div
              className="bg-blue-600 h-3 rounded-full transition-all duration-300"
              style={{ width: `${percent}%` }}
            />
          </div>

          <div className="flex justify-between text-sm text-gray-600">
            <span>
              {data.summary.completed}/{data.summary.total} complete
            </span>
            {complete ? <span className="text-green-700">Onboarding complete</span> : <span />}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow mb-8">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Steps</h3>
            <div className="space-y-3">
              {rows.map((task) => (
                <button
                  key={task.id}
                  type="button"
                  onClick={() => toggle(task)}
                  disabled={Boolean(updating[task.id])}
                  className={`w-full text-left p-4 border rounded-lg transition-colors ${
                    task.done
                      ? "border-green-200 bg-green-50"
                      : "border-gray-200 bg-white hover:border-gray-300"
                  } ${updating[task.id] ? "opacity-60 cursor-not-allowed" : ""}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start">
                      <div
                        className={`mt-1 h-5 w-5 rounded border flex items-center justify-center ${
                          task.done ? "bg-green-600 border-green-600" : "bg-white border-gray-300"
                        }`}
                      >
                        {task.done && (
                          <svg
                            className="h-4 w-4 text-white"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                            strokeWidth={3}
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                          </svg>
                        )}
                      </div>
                      <div className="ml-3">
                        <p className="font-medium text-gray-900">{task.label}</p>
                        <p className="text-sm text-gray-500">{task.id}</p>
                      </div>
                    </div>
                    <span className="text-sm text-gray-500">{task.done ? "Done" : "Mark done"}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="flex justify-between">
          <Link
            to="/onboarding/guide"
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            ← Back
          </Link>

          {complete ? (
            <button
              onClick={() => navigate("/app/dashboard")}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
            >
              Continue to Dashboard
            </button>
          ) : (
            <Link
              to="/app/dashboard"
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-500 hover:text-gray-700"
            >
              Skip for now
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};

export default OnboardingChecklist;

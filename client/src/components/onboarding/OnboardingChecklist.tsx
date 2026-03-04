import React, { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import {
  getOnboardingStatus,
  listOnboardingSteps,
  completeOnboardingStep,
  skipOnboardingStep,
  type OnboardingStep,
} from "../../api/onboarding";

type StepRow = {
  step_key: string;
  title: string;
  order_index: number;
  required: boolean;
  status: string; // "pending" | "completed" | "skipped" | "blocked"
};

function toRows(steps: OnboardingStep[]): StepRow[] {
  return steps
    .sort((a, b) => a.order_index - b.order_index)
    .map((s) => ({
      step_key: s.step_key,
      title: s.title,
      order_index: s.order_index,
      required: s.required,
      status: s.state?.status ?? "pending",
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
  const [rows, setRows] = useState<StepRow[]>([]);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updating, setUpdating] = useState<Record<string, boolean>>({});

  const totalSteps = rows.length;
  const completedSteps = rows.filter((r) => r.status === "completed" || r.status === "skipped").length;
  const percent = totalSteps > 0 ? Math.round((completedSteps / totalSteps) * 100) : 0;
  const complete = totalSteps > 0 && completedSteps === totalSteps;

  const loadData = async () => {
    try {
      setLoading(true);
      const status = await getOnboardingStatus();
      setRows(toRows(status.steps));
      setProgress(status.progress);
      setOnboardingComplete(status.session?.onboarding_completed ?? false);
      setError(null);
    } catch (err) {
      const statusCode = (err as { status?: number }).status;
      if (statusCode === 401 || statusCode === 403 || statusCode === 429) return;
      const message = err instanceof Error ? err.message : "Failed to load onboarding checklist";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const markComplete = async (step: StepRow) => {
    if (updating[step.step_key]) return;
    setUpdating((prev) => ({ ...prev, [step.step_key]: true }));
    try {
      const result = await completeOnboardingStep(step.step_key);
      setProgress(result.progress);
      // Refresh full list to get updated states
      const status = await getOnboardingStatus();
      setRows(toRows(status.steps));
      setOnboardingComplete(status.session?.onboarding_completed ?? false);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to complete step";
      setError(message);
    } finally {
      setUpdating((prev) => ({ ...prev, [step.step_key]: false }));
    }
  };

  const markSkipped = async (step: StepRow) => {
    if (updating[step.step_key] || step.required) return;
    setUpdating((prev) => ({ ...prev, [step.step_key]: true }));
    try {
      const result = await skipOnboardingStep(step.step_key);
      setProgress(result.progress);
      const status = await getOnboardingStatus();
      setRows(toRows(status.steps));
      setOnboardingComplete(status.session?.onboarding_completed ?? false);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to skip step";
      setError(message);
    } finally {
      setUpdating((prev) => ({ ...prev, [step.step_key]: false }));
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

  if (!rows.length && !loading) {
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
              {completedSteps}/{totalSteps} complete
            </span>
            {complete ? <span className="text-green-700">Onboarding complete</span> : <span />}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow mb-8">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Steps</h3>
            <div className="space-y-3">
              {rows.map((step) => {
                const isDone = step.status === "completed" || step.status === "skipped";
                return (
                <button
                  key={step.step_key}
                  type="button"
                  onClick={() => isDone ? undefined : markComplete(step)}
                  disabled={Boolean(updating[step.step_key]) || isDone}
                  className={`w-full text-left p-4 border rounded-lg transition-colors ${
                    isDone
                      ? "border-green-200 bg-green-50"
                      : "border-gray-200 bg-white hover:border-gray-300"
                  } ${updating[step.step_key] ? "opacity-60 cursor-not-allowed" : ""}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start">
                      <div
                        className={`mt-1 h-5 w-5 rounded border flex items-center justify-center ${
                          isDone ? "bg-green-600 border-green-600" : "bg-white border-gray-300"
                        }`}
                      >
                        {isDone && (
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
                        <p className="font-medium text-gray-900">{step.title}</p>
                        <p className="text-sm text-gray-500">
                          {step.required ? "Required" : "Optional"} · {step.step_key}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {isDone ? (
                        <span className="text-sm text-green-600">
                          {step.status === "skipped" ? "Skipped" : "Done"}
                        </span>
                      ) : (
                        <>
                          <span className="text-sm text-gray-500">Mark done</span>
                          {!step.required && (
                            <button
                              type="button"
                              onClick={(e) => { e.stopPropagation(); markSkipped(step); }}
                              className="text-xs text-gray-400 hover:text-gray-600 underline"
                            >
                              Skip
                            </button>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                </button>
                );
              })}
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

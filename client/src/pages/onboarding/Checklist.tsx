import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  completeOnboardingStep,
  listOnboardingSteps,
  type OnboardingStep,
} from "../../api/onboarding";

export default function OnboardingChecklist() {
  const navigate = useNavigate();
  const [steps, setSteps] = useState<OnboardingStep[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const checklistSteps = useMemo(
    () => steps.filter((step) => step.step_key.startsWith("checklist_")),
    [steps],
  );

  useEffect(() => {
    let mounted = true;
    listOnboardingSteps()
      .then((data) => {
        if (mounted) setSteps(data);
      })
      .catch((err) => {
        if (mounted) setError(err instanceof Error ? err.message : "Failed to load steps");
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  const markComplete = async (stepKey: string) => {
    try {
      const result = await completeOnboardingStep(stepKey);
      setSteps((prev) =>
        prev.map((step) => (step.step_key === stepKey ? result.step : step)),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update step");
    }
  };

  if (loading) {
    return <div className="app-loading">Loading checklist…</div>;
  }

  return (
    <div className="mx-auto flex min-h-[70vh] w-full max-w-3xl items-center px-6 py-10">
      <div className="w-full rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-semibold text-slate-900">Quick checklist</h1>
        <p className="mt-2 text-sm text-slate-600">
          Optional steps you can complete now or later.
        </p>

        <div className="mt-6 grid gap-3">
          {checklistSteps.map((step) => {
            const done = step.state?.status === "completed";
            return (
              <button
                key={step.step_key}
                type="button"
                className={`flex items-center justify-between rounded-lg border px-4 py-3 text-left text-sm transition ${
                  done ? "border-emerald-200 bg-emerald-50" : "border-slate-200 bg-white"
                }`}
                onClick={() => markComplete(step.step_key)}
                disabled={done}
              >
                <span className="text-slate-700">{step.title}</span>
                <span className="text-xs font-semibold text-slate-500">
                  {done ? "Done" : "Mark done"}
                </span>
              </button>
            );
          })}
        </div>

        {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <button
            type="button"
            className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700"
            onClick={() => navigate("/onboarding/trust")}
          >
            Continue
          </button>
          <button
            type="button"
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50"
            onClick={() => navigate("/app/dashboard")}
          >
            Skip for now
          </button>
        </div>
      </div>
    </div>
  );
}

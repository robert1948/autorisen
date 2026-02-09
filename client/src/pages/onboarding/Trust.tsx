import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  acknowledgeTrust,
  completeOnboarding,
  completeOnboardingStep,
} from "../../api/onboarding";

export default function OnboardingTrust() {
  const navigate = useNavigate();
  const [privacyChecked, setPrivacyChecked] = useState(false);
  const [securityChecked, setSecurityChecked] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAck = async (key: "trust_privacy" | "trust_security") => {
    try {
      await acknowledgeTrust(key, { acknowledged_from: "ui" });
      await completeOnboardingStep(key);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save acknowledgement");
    }
  };

  const onComplete = async () => {
    setLoading(true);
    setError(null);
    try {
      await completeOnboarding();
      localStorage.removeItem("onboarding_explore_quietly");
      localStorage.setItem("onboarding_complete", "true");
      navigate("/app/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to complete onboarding");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-[70vh] w-full max-w-3xl items-center px-6 py-10">
      <div className="w-full rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-semibold text-slate-900">Trust & transparency</h1>
        <p className="mt-2 text-sm text-slate-600">
          Review the commitments we make around privacy and security.
        </p>

        <div className="mt-6 grid gap-4 text-sm text-slate-700">
          <label className="flex items-start gap-3 rounded-lg border border-slate-200 px-4 py-3">
            <input
              type="checkbox"
              className="mt-1 h-4 w-4 text-indigo-600"
              checked={privacyChecked}
              onChange={(event) => {
                const checked = event.target.checked;
                setPrivacyChecked(checked);
                if (checked) void handleAck("trust_privacy");
              }}
            />
            <span>
              I acknowledge the CapeControl privacy commitments and data handling guidelines.
            </span>
          </label>
          <label className="flex items-start gap-3 rounded-lg border border-slate-200 px-4 py-3">
            <input
              type="checkbox"
              className="mt-1 h-4 w-4 text-indigo-600"
              checked={securityChecked}
              onChange={(event) => {
                const checked = event.target.checked;
                setSecurityChecked(checked);
                if (checked) void handleAck("trust_security");
              }}
            />
            <span>
              I acknowledge the CapeControl security posture and agree to follow best practices.
            </span>
          </label>
        </div>

        {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <button
            type="button"
            className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700"
            onClick={onComplete}
            disabled={loading || !privacyChecked || !securityChecked}
          >
            {loading ? "Completing…" : "Complete onboarding"}
          </button>
          <button
            type="button"
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50"
            onClick={() => navigate("/onboarding/checklist")}
          >
            Back
          </button>
        </div>
      </div>
    </div>
  );
}

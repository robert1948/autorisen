import React, { useEffect, useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";

import { startOnboarding } from "../../api/onboarding";
import { useAuth } from "../../features/auth/AuthContext";

const steps = [
  "Confirm your profile",
  "Choose your starting goal",
  "Activate your first dashboard",
];

export default function OnboardingWelcome() {
  const navigate = useNavigate();
  const location = useLocation();
  const { state } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [guideEnabled, setGuideEnabled] = useState(
    localStorage.getItem("onboarding_guide_enabled") !== "false",
  );

  const nextParam = new URLSearchParams(location.search).get("next");
  const safeNext = nextParam && nextParam.startsWith("/") ? nextParam : null;

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    startOnboarding()
      .catch((err) => {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : "Unable to start onboarding");
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  const onContinue = () => {
    localStorage.removeItem("onboarding_explore_quietly");
    navigate("/onboarding/profile");
  };

  const onExplore = () => {
    localStorage.setItem("onboarding_explore_quietly", "true");
    navigate(safeNext ?? "/app/dashboard");
  };

  const toggleGuide = () => {
    const nextValue = !guideEnabled;
    setGuideEnabled(nextValue);
    localStorage.setItem("onboarding_guide_enabled", nextValue ? "true" : "false");
  };

  return (
    <div className="mx-auto flex min-h-[70vh] w-full max-w-3xl items-center px-6 py-10">
      <div className="w-full rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <div className="mb-6">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-indigo-500">
            Onboarding
          </p>
          <h1 className="mt-2 text-3xl font-semibold text-slate-900">
            Welcome to CapeControl
          </h1>
          <p className="mt-2 text-base text-slate-600">
            A calm start—then we’ll guide you to your first control panel.
          </p>
        </div>

        <ul className="mb-6 grid gap-3 text-sm text-slate-700">
          {steps.map((step) => (
            <li key={step} className="flex items-start gap-3 rounded-lg bg-slate-50 px-4 py-3">
              <span className="mt-0.5 inline-flex h-5 w-5 items-center justify-center rounded-full bg-indigo-500 text-xs font-semibold text-white">
                ✓
              </span>
              <span>{step}</span>
            </li>
          ))}
        </ul>

        <div className="flex flex-wrap items-center gap-4">
          <button
            type="button"
            className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700"
            onClick={onContinue}
            disabled={loading}
          >
            Continue
          </button>
          <button
            type="button"
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
            onClick={onExplore}
          >
            Explore quietly (read-only)
          </button>
          <Link
            to="/auth/login"
            className="text-sm font-medium text-slate-500 hover:text-slate-700"
          >
            Back to login
          </Link>
        </div>

        <div className="mt-6 flex items-center gap-3 text-sm text-slate-600">
          <input
            id="guide-enabled"
            type="checkbox"
            className="h-4 w-4 rounded border-slate-300 text-indigo-600"
            checked={guideEnabled}
            onChange={toggleGuide}
          />
          <label htmlFor="guide-enabled">Enable guided onboarding tips</label>
        </div>

        {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

        {import.meta.env.MODE !== "production" && (
          <p className="mt-6 text-xs text-slate-500">
            Signed in as: {state.userEmail ?? "unknown"}
          </p>
        )}
      </div>
    </div>
  );
}

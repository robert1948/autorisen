import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

import { completeOnboardingStep, updateOnboardingProfile } from "../../api/onboarding";

export default function OnboardingProfile() {
  const navigate = useNavigate();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [role, setRole] = useState("Customer");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await updateOnboardingProfile({
        first_name: firstName,
        last_name: lastName,
        company_name: companyName,
        role,
      });
      await completeOnboardingStep("profile");
      navigate("/onboarding/checklist");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update profile");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-[70vh] w-full max-w-3xl items-center px-6 py-10">
      <div className="w-full rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-semibold text-slate-900">Confirm your profile</h1>
        <p className="mt-2 text-sm text-slate-600">
          Tell us a little about you so we can tailor your onboarding experience.
        </p>

        <form onSubmit={onSubmit} className="mt-6 grid gap-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium text-slate-700" htmlFor="first-name">
              First name
            </label>
            <input
              id="first-name"
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 caret-slate-900 placeholder:text-slate-400 dark:text-slate-900 dark:caret-slate-900 dark:placeholder:text-slate-400"
              value={firstName}
              onChange={(event) => setFirstName(event.target.value)}
              required
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium text-slate-700" htmlFor="last-name">
              Last name
            </label>
            <input
              id="last-name"
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 caret-slate-900 placeholder:text-slate-400 dark:text-slate-900 dark:caret-slate-900 dark:placeholder:text-slate-400"
              value={lastName}
              onChange={(event) => setLastName(event.target.value)}
              required
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium text-slate-700" htmlFor="company-name">
              Company
            </label>
            <input
              id="company-name"
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 caret-slate-900 placeholder:text-slate-400 dark:text-slate-900 dark:caret-slate-900 dark:placeholder:text-slate-400"
              value={companyName}
              onChange={(event) => setCompanyName(event.target.value)}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium text-slate-700" htmlFor="role">
              Role
            </label>
            <select
              id="role"
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 caret-slate-900 placeholder:text-slate-400 dark:text-slate-900 dark:caret-slate-900 dark:placeholder:text-slate-400"
              value={role}
              onChange={(event) => setRole(event.target.value)}
            >
              <option value="Customer">Customer</option>
              <option value="Developer">Developer</option>
              <option value="Operator">Operator</option>
            </select>
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button
            type="submit"
            className="mt-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700"
            disabled={loading}
          >
            {loading ? "Saving…" : "Continue"}
          </button>
        </form>
      </div>
    </div>
  );
}

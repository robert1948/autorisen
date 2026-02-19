import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { completeOnboardingStep, updateOnboardingProfile } from "../../api/onboarding";
import { useAuth } from "../../features/auth/AuthContext";

export default function OnboardingProfile() {
  const navigate = useNavigate();
  const { state: authState } = useAuth();
  const user = authState.user;

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [role, setRole] = useState("Customer");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Pre-fill from authenticated user profile (e.g. Google OAuth data)
  useEffect(() => {
    if (!user) return;
    if (user.first_name) setFirstName(user.first_name);
    if (user.last_name) setLastName(user.last_name);
    if (user.role && user.role !== "user") setRole(user.role);
  }, [user]);

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

  const inputCls =
    "w-full rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white caret-white placeholder:text-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500";
  const labelCls = "text-sm font-medium text-white";

  return (
    <div className="mx-auto flex min-h-[70vh] w-full max-w-3xl items-center px-6 py-10">
      <div className="w-full rounded-2xl border border-slate-700 bg-slate-900 p-8 shadow-lg">
        <h1 className="text-2xl font-semibold text-white">Confirm your profile</h1>
        <p className="mt-2 text-sm text-slate-300">
          Review and update your details below. Press <strong>Continue</strong> at any time to accept the current values.
        </p>

        <form onSubmit={onSubmit} className="mt-6 grid gap-4">
          {/* Email (read-only, from auth) */}
          {user?.email && (
            <div className="grid gap-2">
              <label className={labelCls} htmlFor="email">
                Email
              </label>
              <input
                id="email"
                className={`${inputCls} cursor-not-allowed opacity-70`}
                value={user.email}
                readOnly
                tabIndex={-1}
              />
            </div>
          )}
          <div className="grid gap-2">
            <label className={labelCls} htmlFor="first-name">
              First name
            </label>
            <input
              id="first-name"
              className={inputCls}
              value={firstName}
              onChange={(event) => setFirstName(event.target.value)}
              placeholder="Your first name"
            />
          </div>
          <div className="grid gap-2">
            <label className={labelCls} htmlFor="last-name">
              Last name
            </label>
            <input
              id="last-name"
              className={inputCls}
              value={lastName}
              onChange={(event) => setLastName(event.target.value)}
              placeholder="Your last name"
            />
          </div>
          <div className="grid gap-2">
            <label className={labelCls} htmlFor="company-name">
              Company
            </label>
            <input
              id="company-name"
              className={inputCls}
              value={companyName}
              onChange={(event) => setCompanyName(event.target.value)}
              placeholder="Optional"
            />
          </div>
          <div className="grid gap-2">
            <label className={labelCls} htmlFor="role">
              Role
            </label>
            <select
              id="role"
              className={inputCls}
              value={role}
              onChange={(event) => setRole(event.target.value)}
            >
              <option value="Customer">Customer</option>
              <option value="Developer">Developer</option>
              <option value="Operator">Operator</option>
            </select>
          </div>
          {error && <p className="text-sm text-red-400">{error}</p>}
          <button
            type="submit"
            className="mt-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? "Saving…" : "Continue"}
          </button>
        </form>
      </div>
    </div>
  );
}

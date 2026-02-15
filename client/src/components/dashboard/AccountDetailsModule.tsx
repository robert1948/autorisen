/**
 * AccountDetailsModule — view and edit core account information.
 *
 * Per spec §3.2: editable fields with optimistic UI,
 * proper ARIA labels, and skeleton loading states.
 */

import { useCallback, useEffect, useState } from "react";

import { dashboardModulesApi, type AccountDetails } from "../../services/dashboardModulesApi";
import { useAuth } from "../../features/auth/AuthContext";
import type { UserProfile } from "../../types/user";

interface AccountDetailsModuleProps {
  user?: UserProfile;
}

const emptyDetails: AccountDetails = {
  id: "",
  email: "",
  display_name: "",
  status: "",
  role: "",
  created_at: "",
  last_login: null,
  company_name: "",
};

export const AccountDetailsModule = ({ user }: AccountDetailsModuleProps) => {
  const { state } = useAuth();
  const [details, setDetails] = useState<AccountDetails>(emptyDetails);
  const [loading, setLoading] = useState(true);
  const [loaded, setLoaded] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDetails = useCallback(async () => {
    try {
      setError(null);
      setLoading(true);
      const data = await dashboardModulesApi.getAccountDetails();
      setDetails(data);
      setLoaded(true);
    } catch (err) {
      const message =
        state.status === "authenticated"
          ? "Couldn't load this section. Try again."
          : "Please sign in to view this section.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [state.status]);

  useEffect(() => {
    loadDetails();
  }, [loadDetails]);

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      const updated = await dashboardModulesApi.updateAccountDetails({
        display_name: details.display_name,
        company_name: details.company_name,
      });
      setDetails(updated);
    } catch (err) {
      setError("Couldn't save changes. Try again.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm" role="status" aria-label="Loading account details" aria-busy="true">
        <div className="animate-pulse">
          <div className="mb-4 h-5 w-1/3 rounded bg-slate-200" />
          <div className="grid gap-4 md:grid-cols-2">
            <div className="h-10 rounded bg-slate-200" />
            <div className="h-10 rounded bg-slate-200" />
            <div className="h-10 rounded bg-slate-200" />
            <div className="h-10 rounded bg-slate-200" />
          </div>
        </div>
      </div>
    );
  }

  if (!loading && error && !loaded) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900">Account details</h3>
        <p className="mt-2 text-sm text-slate-600">{error}</p>
        <button
          onClick={loadDetails}
          className="mt-4 rounded-md border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm" aria-labelledby="account-details-heading">
      <div className="flex items-center justify-between">
        <h3 id="account-details-heading" className="text-lg font-semibold text-slate-900">Account details</h3>
        <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs uppercase text-slate-500">{details.status}</span>
      </div>
      {error && <p className="mt-2 text-sm text-slate-600">{error}</p>}
      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <div>
          <label className="text-xs font-semibold text-slate-500">Display name</label>
          <input
            value={details.display_name}
            onChange={(event) =>
              setDetails((prev) => ({ ...prev, display_name: event.target.value }))
            }
            className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
            placeholder="Display name"
          />
        </div>
        <div>
          <label className="text-xs font-semibold text-slate-500">Company</label>
          <input
            value={details.company_name ?? ""}
            onChange={(event) =>
              setDetails((prev) => ({ ...prev, company_name: event.target.value }))
            }
            className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
            placeholder="Company name"
          />
        </div>
        <div>
          <label className="text-xs font-semibold text-slate-500">Email</label>
          <p className="mt-1 text-sm text-slate-700">{details.email}</p>
        </div>
        <div>
          <label className="text-xs font-semibold text-slate-500">Role</label>
          <p className="mt-1 text-sm text-slate-700 capitalize">{details.role}</p>
        </div>
      </div>
      <div className="mt-4 flex items-center justify-between text-xs text-slate-500">
        <span>Created {details.created_at ? new Date(details.created_at).toLocaleDateString() : ""}</span>
        <span>
          Last login {details.last_login ? new Date(details.last_login).toLocaleDateString() : "—"}
        </span>
      </div>
      <div className="mt-4">
        <button
          onClick={handleSave}
          disabled={saving}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
          aria-busy={saving}
        >
          {saving ? "Saving…" : "Save changes"}
        </button>
      </div>
    </section>
  );
};

import { useCallback, useEffect, useState } from "react";

import { dashboardModulesApi, type AccountDetails } from "../../services/dashboardModulesApi";
import { useAuth } from "../../features/auth/AuthContext";

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

export const AccountDetailsModule = () => {
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
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm text-slate-500">Loading account details…</p>
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
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-900">Account details</h3>
        <span className="text-xs uppercase text-slate-500">{details.status}</span>
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
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
        >
          {saving ? "Saving…" : "Save changes"}
        </button>
      </div>
    </div>
  );
};

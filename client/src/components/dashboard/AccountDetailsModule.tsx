import { useEffect, useState } from "react";

import { dashboardModulesApi, type AccountDetails } from "../../services/dashboardModulesApi";

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
  const [details, setDetails] = useState<AccountDetails>(emptyDetails);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const data = await dashboardModulesApi.getAccountDetails();
        setDetails(data);
      } catch (err) {
        setError((err as Error).message || "Failed to load account details");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

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
      setError((err as Error).message || "Failed to save account details");
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

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-900">Account details</h3>
        <span className="text-xs uppercase text-slate-500">{details.status}</span>
      </div>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
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

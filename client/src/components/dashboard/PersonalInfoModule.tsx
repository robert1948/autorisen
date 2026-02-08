import { useCallback, useEffect, useState } from "react";

import { dashboardModulesApi, type PersonalInfo } from "../../services/dashboardModulesApi";
import { useAuth } from "../../features/auth/AuthContext";

const emptyInfo: PersonalInfo = {
  phone: "",
  location: "",
  timezone: "",
  bio: "",
  avatar_url: "",
};

export const PersonalInfoModule = () => {
  const { state } = useAuth();
  const [info, setInfo] = useState<PersonalInfo>(emptyInfo);
  const [loading, setLoading] = useState(true);
  const [loaded, setLoaded] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadInfo = useCallback(async () => {
    try {
      setError(null);
      setLoading(true);
      const data = await dashboardModulesApi.getPersonalInfo();
      setInfo({ ...emptyInfo, ...data });
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
    loadInfo();
  }, [loadInfo]);

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      const updated = await dashboardModulesApi.updatePersonalInfo(info);
      setInfo({ ...emptyInfo, ...updated });
    } catch (err) {
      setError("Couldn't save changes. Try again.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm text-slate-500">Loading personal info…</p>
      </div>
    );
  }

  if (!loading && error && !loaded) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900">Personal information</h3>
        <p className="mt-2 text-sm text-slate-600">{error}</p>
        <button
          onClick={loadInfo}
          className="mt-4 rounded-md border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-slate-900">Personal information</h3>
      {error && <p className="mt-2 text-sm text-slate-600">{error}</p>}
      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <div>
          <label className="text-xs font-semibold text-slate-500">Phone</label>
          <input
            value={info.phone ?? ""}
            onChange={(event) => setInfo((prev) => ({ ...prev, phone: event.target.value }))}
            className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
            placeholder="+27 00 000 0000"
          />
        </div>
        <div>
          <label className="text-xs font-semibold text-slate-500">Location</label>
          <input
            value={info.location ?? ""}
            onChange={(event) => setInfo((prev) => ({ ...prev, location: event.target.value }))}
            className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
            placeholder="Cape Town"
          />
        </div>
        <div>
          <label className="text-xs font-semibold text-slate-500">Timezone</label>
          <input
            value={info.timezone ?? ""}
            onChange={(event) => setInfo((prev) => ({ ...prev, timezone: event.target.value }))}
            className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
            placeholder="Africa/Johannesburg"
          />
        </div>
        <div>
          <label className="text-xs font-semibold text-slate-500">Avatar URL</label>
          <input
            value={info.avatar_url ?? ""}
            onChange={(event) => setInfo((prev) => ({ ...prev, avatar_url: event.target.value }))}
            className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
            placeholder="https://"
          />
        </div>
      </div>
      <div className="mt-4">
        <label className="text-xs font-semibold text-slate-500">Bio</label>
        <textarea
          value={info.bio ?? ""}
          onChange={(event) => setInfo((prev) => ({ ...prev, bio: event.target.value }))}
          className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
          rows={3}
          placeholder="Tell us about yourself"
        />
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

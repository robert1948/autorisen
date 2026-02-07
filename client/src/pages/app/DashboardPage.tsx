import { useEffect, useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { AccountBalanceModule } from "../../components/dashboard/AccountBalanceModule";
import { AccountDetailsModule } from "../../components/dashboard/AccountDetailsModule";
import { DeleteAccountModule } from "../../components/dashboard/DeleteAccountModule";
import { PersonalInfoModule } from "../../components/dashboard/PersonalInfoModule";
import { ProjectStatusModule } from "../../components/dashboard/ProjectStatusModule";
import { useMe } from "../../hooks/useMe";

const Dashboard = () => {
  const { loading, error, status, data, reload } = useMe();
  const navigate = useNavigate();
  const location = useLocation();
  const isPreview = useMemo(() => {
    const search = new URLSearchParams(location.search);
    return search.get("preview") === "1" || localStorage.getItem("cc_preview_mode") === "true";
  }, [location.search]);

  useEffect(() => {
    if ((status === 401 || status === 403) && !isPreview) {
      navigate("/auth/login", { replace: true });
    }
  }, [navigate, status, isPreview]);

  if (isPreview) {
    return (
      <div className="min-h-screen bg-slate-50 p-8">
        <div className="mb-6 rounded-md border border-slate-200 bg-white p-4">
          <p className="text-sm text-slate-700">
            Read-only preview. Sign in to load account data.
          </p>
        </div>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="h-40 rounded-lg border border-dashed border-slate-200 bg-white" />
          <div className="h-40 rounded-lg border border-dashed border-slate-200 bg-white" />
          <div className="h-40 rounded-lg border border-dashed border-slate-200 bg-white" />
          <div className="h-40 rounded-lg border border-dashed border-slate-200 bg-white" />
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 p-8">
        <div className="flex h-64 items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-blue-600" />
        </div>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="min-h-screen bg-slate-50 p-8">
        <div className="rounded-lg border border-red-200 bg-white p-6 text-sm text-red-600">
          <p>{error}</p>
          <button
            onClick={reload}
            className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const role = data?.role ?? "user";
  const displayName = data?.profile?.display_name ?? "";
  const roleLabel = role === "developer" ? "Developer" : "User";

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
            <p className="text-sm text-slate-500">
              Welcome back{displayName ? `, ${displayName}` : ""} · {roleLabel}
            </p>
          </div>
        </div>
      </header>

      <main className="p-8">
        {error && !isPreview && (
          <div className="mb-6 rounded-md border border-yellow-200 bg-yellow-50 p-4">
            <p className="text-sm text-yellow-800">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <AccountDetailsModule />
          <PersonalInfoModule />
          <ProjectStatusModule title={role === "developer" ? "Developer projects" : "Project status"} />
          <AccountBalanceModule />
          <DeleteAccountModule />
        </div>
      </main>
    </div>
  );
};

export default Dashboard;